#!/usr/bin/env python3
"""
app/resume_pipeline.py

Responsibilities (in order):
1) Read resume.md
2) AI Call #1 -> HTML (ATS optimized)
3) AI Call #2 -> ATS analysis JSON (strict schema)
4) Upload HTML to s3://<BUCKET_NAME>/<ENV>/index.html
5) Write DynamoDB records:
   - DeploymentTracking
   - ResumeAnalytics
"""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import boto3


# -----------------------------
# Config + Guardrails
# -----------------------------

REQUIRED_ENV_VARS = [
    "AWS_REGION",
    "BUCKET_NAME",
    "DEPLOYMENT_TABLE",
    "ANALYTICS_TABLE",
    "ENV",          # beta | prod
    "COMMIT_SHA",
    "MODEL_ID",     # Bedrock model id, e.g. anthropic.claude-3-5-sonnet-20240620-v1:0
]


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def require_env() -> Dict[str, str]:
    missing = [k for k in REQUIRED_ENV_VARS if not os.getenv(k)]
    if missing:
        fail(f"Missing required environment variables: {', '.join(missing)}")
    env = {k: os.environ[k] for k in REQUIRED_ENV_VARS}
    if env["ENV"] not in ("beta", "prod"):
        fail("ENV must be 'beta' or 'prod'")
    return env


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_resume_md(path: str = "resume.md") -> str:
    if not os.path.exists(path):
        fail(f"resume.md not found at path: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if len(content) < 50:
        fail("resume.md content is unexpectedly short; aborting.")
    return content


# -----------------------------
# Bedrock InvokeModel helpers
# -----------------------------

def bedrock_invoke_text(model_id: str, region: str, prompt: str, max_tokens: int = 2500) -> str:
    """
    Calls Bedrock Runtime InvokeModel. Payload format varies by model provider.
    This implementation supports Anthropic Claude models (recommended).
    """
    client = boto3.client("bedrock-runtime", region_name=region)

    # Anthropic Claude messages format
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    resp = client.invoke_model(
        modelId=model_id,
        accept="application/json",
        contentType="application/json",
        body=json.dumps(body).encode("utf-8"),
    )

    raw = resp["body"].read()
    data = json.loads(raw)

    # Claude returns content as a list of blocks: [{"type":"text","text":"..."}]
    blocks = data.get("content", [])
    if not blocks or "text" not in blocks[0]:
        fail(f"Unexpected Bedrock response shape: {data}")
    return blocks[0]["text"]


# -----------------------------
# Prompts
# -----------------------------

def build_html_prompt(resume_md: str) -> str:
    return f"""You are generating an ATS-optimized, professional resume website as a SINGLE HTML document.

Requirements:
- Output ONLY valid HTML (no markdown, no code fences, no commentary).
- Use semantic HTML: <header>, <main>, <section>, <h1>-<h3>, <ul>, <li>.
- Keep styling minimal and ATS-friendly: inline CSS only, simple fonts, high contrast.
- Do NOT include external JS/CSS, trackers, or images.
- Ensure sections map cleanly from the resume: Summary, Skills, Projects, Experience, Education, Certifications.
- If a section is missing in the input, omit it.
- Preserve all user-provided facts; do not invent new experience.

Input resume markdown:
{resume_md}
"""


def build_ats_json_prompt(resume_md: str) -> str:
    return f"""Analyze the resume markdown for ATS readiness and output STRICT JSON ONLY.

Return a JSON object with EXACTLY these keys:
- word_count: integer
- ats_score: integer (0-100)
- keywords: array of strings (most important ATS keywords found; 5-20 items)
- readability: string (one of: "Excellent", "Good", "Fair", "Poor")
- missing_sections: array of strings (any of: "Summary","Skills","Projects","Experience","Education","Certifications")

Rules:
- Output ONLY JSON (no markdown fences, no extra text).
- Do not include trailing commas.
- Do not include additional keys.

Resume markdown:
{resume_md}
"""


# -----------------------------
# Output validation
# -----------------------------

def sanitize_html(html: str) -> str:
    # Basic guardrail: ensure it's HTML-ish and not wrapped in code fences.
    html = html.strip()
    html = re.sub(r"^```html\s*", "", html, flags=re.IGNORECASE)
    html = re.sub(r"^```\s*", "", html)
    html = re.sub(r"\s*```$", "", html)
    if "<html" not in html.lower():
        # Accept if it’s a fragment but still HTML.
        if not any(tag in html.lower() for tag in ("<section", "<h1", "<main", "<header")):
            fail("HTML output does not appear to be valid HTML.")
        # Wrap fragment
        html = f"<!doctype html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"
    return html


def validate_ats_json(raw_text: str) -> Dict[str, Any]:
    text = raw_text.strip()
    # Remove accidental code fences
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        fail(f"ATS JSON output is not valid JSON: {e}\nRaw:\n{text[:500]}")

    required_keys = ["word_count", "ats_score", "keywords", "readability", "missing_sections"]
    if sorted(obj.keys()) != sorted(required_keys):
        fail(f"ATS JSON keys must be exactly {required_keys}. Got: {list(obj.keys())}")

    # Type checks
    if not isinstance(obj["word_count"], int):
        fail("ATS JSON word_count must be an integer.")
    if not isinstance(obj["ats_score"], int):
        fail("ATS JSON ats_score must be an integer.")
    if not (0 <= obj["ats_score"] <= 100):
        fail("ATS JSON ats_score must be between 0 and 100.")
    if not isinstance(obj["keywords"], list) or not all(isinstance(k, str) for k in obj["keywords"]):
        fail("ATS JSON keywords must be an array of strings.")
    if not isinstance(obj["missing_sections"], list) or not all(isinstance(s, str) for s in obj["missing_sections"]):
        fail("ATS JSON missing_sections must be an array of strings.")
    if obj["readability"] not in ("Excellent", "Good", "Fair", "Poor"):
        fail('ATS JSON readability must be one of: "Excellent","Good","Fair","Poor"')

    return obj


# -----------------------------
# AWS writes: S3 + DynamoDB
# -----------------------------

def upload_html_to_s3(bucket: str, env: str, html: str, region: str) -> str:
    s3 = boto3.client("s3", region_name=region)
    key = f"{env}/index.html"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=html.encode("utf-8"),
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )
    # Public bucket, so URL is predictable:
    return f"https://{bucket}.s3.amazonaws.com/{key}"


def write_deployment_tracking(
    table_name: str,
    region: str,
    commit_sha: str,
    env: str,
    status: str,
    s3_url: str,
    model_id: str,
) -> str:
    ddb = boto3.resource("dynamodb", region_name=region)
    table = ddb.Table(table_name)

    deployment_id = str(uuid.uuid4())
    item = {
        "deployment_id": deployment_id,
        "commit_sha": commit_sha,
        "environment": env,
        "status": status,
        "s3_url": s3_url,
        "model_used": model_id,
        "timestamp": utc_now_iso(),
    }
    table.put_item(Item=item)
    return deployment_id


def write_resume_analytics(
    table_name: str,
    region: str,
    commit_sha: str,
    env: str,
    analytics: Dict[str, Any],
    model_id: str,
) -> str:
    ddb = boto3.resource("dynamodb", region_name=region)
    table = ddb.Table(table_name)

    analysis_id = str(uuid.uuid4())
    item = {
        "analysis_id": analysis_id,
        "commit_sha": commit_sha,
        "environment": env,
        "model_used": model_id,
        "timestamp": utc_now_iso(),
        "word_count": analytics["word_count"],
        "ats_score": analytics["ats_score"],
        "readability": analytics["readability"],
        "keywords": analytics["keywords"],
        "missing_sections": analytics["missing_sections"],
    }
    table.put_item(Item=item)
    return analysis_id


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    cfg = require_env()

    region = cfg["AWS_REGION"]
    bucket = cfg["BUCKET_NAME"]
    deployment_table = cfg["DEPLOYMENT_TABLE"]
    analytics_table = cfg["ANALYTICS_TABLE"]
    env = cfg["ENV"]
    commit_sha = cfg["COMMIT_SHA"]
    model_id = cfg["MODEL_ID"]

    resume_md = read_resume_md("resume.md")

    # AI Call #1 -> HTML
    html_prompt = build_html_prompt(resume_md)
    html_raw = bedrock_invoke_text(model_id=model_id, region=region, prompt=html_prompt, max_tokens=3000)
    html = sanitize_html(html_raw)

    # AI Call #2 -> ATS JSON
    json_prompt = build_ats_json_prompt(resume_md)
    ats_raw = bedrock_invoke_text(model_id=model_id, region=region, prompt=json_prompt, max_tokens=1200)
    ats = validate_ats_json(ats_raw)

    # Upload to S3
    s3_url = upload_html_to_s3(bucket=bucket, env=env, html=html, region=region)

    # Write DynamoDB records
    deployment_id = write_deployment_tracking(
        table_name=deployment_table,
        region=region,
        commit_sha=commit_sha,
        env=env,
        status="success",
        s3_url=s3_url,
        model_id=model_id,
    )

    analysis_id = write_resume_analytics(
        table_name=analytics_table,
        region=region,
        commit_sha=commit_sha,
        env=env,
        analytics=ats,
        model_id=model_id,
    )

    # CI-friendly summary
    print(json.dumps({
        "status": "ok",
        "env": env,
        "commit_sha": commit_sha,
        "s3_url": s3_url,
        "deployment_id": deployment_id,
        "analysis_id": analysis_id,
        "ats_score": ats["ats_score"],
    }, indent=2))


if __name__ == "__main__":
    main()
