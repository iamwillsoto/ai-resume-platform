#!/usr/bin/env python3
"""
AI Resume Platform Pipeline (Bedrock-first with deterministic fallback)

Responsibilities (beta deploy):
- Read resume.md
- Attempt Bedrock AI Call #1: resume.md -> ATS-friendly HTML
- Attempt Bedrock AI Call #2: resume.md -> ATS analytics JSON (strict schema)
- If Bedrock throttles (tokens/day or throttling), fall back to:
    - deterministic markdown->html
    - deterministic ATS analytics
- Upload HTML to S3: s3://<bucket>/<env>/index.html
- Write DynamoDB records:
    - DeploymentTracking
    - ResumeAnalytics

Environment variables (set by GitHub Actions job env):
- AWS_REGION              (required)  : region for S3 + DynamoDB
- BEDROCK_REGION          (optional)  : region for Bedrock; defaults to AWS_REGION
- BUCKET_NAME             (required)
- DEPLOYMENT_TABLE        (required)  : DeploymentTracking
- ANALYTICS_TABLE         (required)  : ResumeAnalytics
- ENV                     (required)  : beta (or prod later)
- COMMIT_SHA              (required)
- MODEL_ID                (required)  : bedrock model ID
"""

import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


# ----------------------------
# Strict schema for analytics
# ----------------------------
REQUIRED_ANALYTICS_KEYS = {
    "word_count": int,
    "ats_score": int,
    "keywords": list,
    "readability": str,
    "missing_sections": list,
}


# ----------------------------
# Helpers
# ----------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v


def clamp_text(s: str, max_chars: int = 12000) -> str:
    s = (s or "").strip()
    return s[:max_chars]


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render_inline(text: str) -> str:
    """
    Convert inline markdown (bold, italic) to HTML after escaping raw text.
    Order matters: escape first, then apply inline tags.
    """
    text = (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
    )
    # Bold+italic: ***text*** or ___text___
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"___(.*?)___", r"<strong><em>\1</em></strong>", text)
    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.*?)__", r"<strong>\1</strong>", text)
    # Italic: *text* or _text_
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.*?)_", r"<em>\1</em>", text)
    # Inline code: `code`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def md_to_basic_html(md: str) -> str:
    """
    Deterministic HTML rendering (ATS-friendly, no dependencies).
    Handles: h1/h2/h3, ul/li, hr, bold, italic, inline code, paragraphs.
    """
    lines = [ln.rstrip() for ln in md.splitlines()]

    html_parts: List[str] = []
    in_ul = False

    def close_ul():
        nonlocal in_ul
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False

    for ln in lines:
        # Horizontal rule: --- or ***
        if re.match(r"^\s*[-*]{3,}\s*$", ln):
            close_ul()
            html_parts.append("<hr>")
            continue

        if not ln.strip():
            close_ul()
            continue

        if ln.startswith("# "):
            close_ul()
            html_parts.append(f"<h1>{render_inline(ln[2:].strip())}</h1>")
        elif ln.startswith("## "):
            close_ul()
            html_parts.append(f"<h2>{render_inline(ln[3:].strip())}</h2>")
        elif ln.startswith("### "):
            close_ul()
            html_parts.append(f"<h3>{render_inline(ln[4:].strip())}</h3>")
        elif ln.startswith("- ") or ln.startswith("* "):
            if not in_ul:
                html_parts.append("<ul>")
                in_ul = True
            html_parts.append(f"<li>{render_inline(ln[2:].strip())}</li>")
        else:
            close_ul()
            html_parts.append(f"<p>{render_inline(ln.strip())}</p>")

    close_ul()

    css = """
    body { font-family: Arial, sans-serif; margin: 40px auto; color: #111; max-width: 860px; padding: 0 20px; }
    h1 { font-size: 26px; margin: 0 0 4px; }
    h2 { font-size: 16px; margin: 20px 0 4px; border-bottom: 1px solid #ccc; padding-bottom: 2px; text-transform: uppercase; letter-spacing: 0.05em; }
    h3 { font-size: 14px; margin: 12px 0 2px; }
    p { font-size: 13px; line-height: 1.5; margin: 3px 0; }
    ul { margin: 4px 0 10px 20px; padding: 0; }
    li { font-size: 13px; line-height: 1.5; margin: 2px 0; }
    hr { border: none; border-top: 1px solid #ddd; margin: 14px 0; }
    code { background: #f4f4f4; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
    strong { font-weight: 600; }
    """
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>Will Soto | AWS Cloud Engineer</title><style>{css}</style></head>"
        f"<body>{''.join(html_parts)}</body></html>"
    )


def escape_html(s: str) -> str:
    # Kept for compatibility — use render_inline() for full markdown support
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def basic_ats_analysis(md: str) -> Dict[str, Any]:
    """
    Deterministic, rubric-aligned analytics payload for fallback.
    FIX: Summary detection now matches both 'PROFESSIONAL SUMMARY' and 'Summary'
         so it is not incorrectly flagged as missing.
    """
    words = re.findall(r"\b\w+\b", md)
    word_count = len(words)

    def has_section(name: str) -> bool:
        return bool(re.search(rf"(?im)^##\s+{re.escape(name)}\b", md))

    sections = {
        # FIX: match both '## Summary' and '## PROFESSIONAL SUMMARY'
        "Summary": bool(re.search(r"(?im)^##\s+(professional\s+)?summary\b", md)),
        "Skills": has_section("Skills"),
        "Projects": has_section("Projects"),
        "Experience": has_section("Experience"),
        "Education": has_section("Education"),
        "Certifications": bool(re.search(r"(?im)^##\s+Certifications?\b", md)),
    }
    missing_sections = [k for k, v in sections.items() if not v]

    # Simple ATS score heuristic (0-100). Good enough for fallback.
    score = 60
    if word_count >= 350:
        score += 10
    else:
        score -= 5

    score += 10 if sections["Skills"] else -10
    score += 10 if sections["Experience"] else -10
    score += 5 if sections["Projects"] else -5
    score -= min(15, 3 * len(missing_sections))
    score = max(0, min(100, score))

    # Keyword extraction (top unique words length>=4)
    freq: Dict[str, int] = {}
    for w in words:
        w2 = w.lower()
        if len(w2) < 4:
            continue
        freq[w2] = freq.get(w2, 0) + 1
    keywords = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)[:15]

    readability = "Good" if word_count >= 350 else "Fair"

    return {
        "word_count": int(word_count),
        "ats_score": int(score),
        "keywords": keywords,
        "readability": readability,
        "missing_sections": missing_sections,
    }


def validate_analytics(obj: Dict[str, Any]) -> Dict[str, Any]:
    for k, t in REQUIRED_ANALYTICS_KEYS.items():
        if k not in obj:
            raise ValueError(f"Analytics missing required key: {k}")
        if not isinstance(obj[k], t):
            raise ValueError(f"Analytics key '{k}' expected type {t.__name__}")
    # normalize keyword items
    obj["keywords"] = [str(x) for x in obj["keywords"]][:50]
    obj["missing_sections"] = [str(x) for x in obj["missing_sections"]][:50]
    obj["word_count"] = int(obj["word_count"])
    obj["ats_score"] = int(max(0, min(100, obj["ats_score"])))
    obj["readability"] = str(obj["readability"])[:40]
    return obj


# ----------------------------
# Bedrock invocation (Bedrock-first)
# ----------------------------
def bedrock_invoke_text(
    *,
    bedrock_region: str,
    model_id: str,
    prompt: str,
    max_tokens: int,
    temperature: float = 0.2,
    retries: int = 1,
    backoff_seconds: float = 2.0,
) -> str:
    """
    Calls bedrock-runtime InvokeModel. Includes minimal retry/backoff
    (we avoid aggressive retries to reduce throttling).
    """
    client = boto3.client("bedrock-runtime", region_name=bedrock_region)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }

    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            resp = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body).encode("utf-8"),
                accept="application/json",
                contentType="application/json",
            )
            raw = resp["body"].read().decode("utf-8")
            data = json.loads(raw)

            # Anthropic response shape:
            # { "content": [ { "type": "text", "text": "..." } ], ... }
            content = data.get("content", [])
            texts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    texts.append(item.get("text", ""))
            return "\n".join(texts).strip()

        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_seconds * (attempt + 1))
                continue
            break

    raise last_err if last_err else RuntimeError("Unknown Bedrock error")


def is_bedrock_fallback_error(e: Exception) -> bool:
    """
    FIX: Broadened from throttling-only to catch all Bedrock failures that
    should trigger graceful fallback instead of crashing the pipeline.
    Covers: throttling, token limits, access denied (model not enabled in
    region), and validation errors.
    """
    msg = str(e)

    # Throttling and token quota
    if "ThrottlingException" in msg:
        return True
    if "Too many tokens per day" in msg:
        return True

    # Model not enabled in this region (AccessDeniedException)
    if "AccessDeniedException" in msg:
        return True

    # Model ID not valid for region or malformed request
    if "ValidationException" in msg:
        return True

    # Model not found / not available in region
    if "ResourceNotFoundException" in msg:
        return True

    # Service unavailable / internal Bedrock errors
    if "ServiceUnavailableException" in msg:
        return True
    if "InternalServerException" in msg:
        return True
    if "ModelErrorException" in msg:
        return True
    if "ModelTimeoutException" in msg:
        return True

    # ClientError structured codes
    if isinstance(e, ClientError):
        code = e.response.get("Error", {}).get("Code", "")
        if code in {
            "ThrottlingException",
            "TooManyRequestsException",
            "AccessDeniedException",
            "ValidationException",
            "ResourceNotFoundException",
            "ServiceUnavailableException",
            "InternalServerException",
            "ModelErrorException",
            "ModelTimeoutException",
        }:
            return True

    return False


# ----------------------------
# Prompts
# ----------------------------
def build_html_prompt(resume_md: str) -> str:
    return (
        "Convert the following resume in Markdown into clean, ATS-friendly HTML.\n"
        "Requirements:\n"
        "- Use semantic HTML tags (h1/h2/h3, p, ul/li).\n"
        "- Do NOT include Markdown code fences.\n"
        "- Keep styling minimal (no external assets).\n"
        "- Output ONLY HTML.\n\n"
        f"RESUME_MARKDOWN:\n{resume_md}\n"
    )


def build_ats_json_prompt(resume_md: str) -> str:
    schema = {
        "word_count": 0,
        "ats_score": 0,
        "keywords": ["string"],
        "readability": "Good|Fair|Poor",
        "missing_sections": ["string"],
    }
    return (
        "Analyze the resume below for ATS readiness.\n"
        "Return STRICT JSON only (no markdown, no commentary).\n"
        "Schema keys must match exactly:\n"
        f"{json.dumps(schema)}\n\n"
        "Guidance:\n"
        "- ats_score must be 0-100 integer\n"
        "- keywords: 10-20 items\n"
        # FIX: explicitly tell Bedrock that PROFESSIONAL SUMMARY satisfies Summary
        "- missing_sections: list any missing standard sections. "
        "Note: 'PROFESSIONAL SUMMARY' fully satisfies the Summary section requirement. "
        "Do NOT flag Summary as missing if a PROFESSIONAL SUMMARY section is present.\n\n"
        f"RESUME_MARKDOWN:\n{resume_md}\n"
    )


def sanitize_html(html: str) -> str:
    html = html.strip()
    html = re.sub(r"^```(?:html)?\s*", "", html, flags=re.IGNORECASE)
    html = re.sub(r"\s*```$", "", html)
    return clamp_text(html, max_chars=120000)


def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract first JSON object from a string (AI sometimes wraps output).
    """
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in AI output")
    return json.loads(m.group(0))


# ----------------------------
# AWS writes: S3 + DynamoDB
# ----------------------------
def upload_html_to_s3(region: str, bucket: str, env: str, html: str) -> str:
    s3 = boto3.client("s3", region_name=region)
    key = f"{env}/index.html"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=html.encode("utf-8"),
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )
    return f"http://{bucket}.s3-website-{region}.amazonaws.com/{key}"


def put_deployment_tracking(
    region: str,
    table_name: str,
    deployment_id: str,
    commit_sha: str,
    env: str,
    status: str,
    s3_url: str,
    model_used: str,
) -> None:
    ddb = boto3.resource("dynamodb", region_name=region).Table(table_name)
    ddb.put_item(
        Item={
            "deployment_id": deployment_id,
            "commit_sha": commit_sha,
            "environment": env,
            "status": status,
            "s3_url": s3_url,
            "model_used": model_used,
            "timestamp": now_iso(),
        }
    )


def put_resume_analytics(
    region: str,
    table_name: str,
    analytics_id: str,
    commit_sha: str,
    env: str,
    model_used: str,
    analytics: Dict[str, Any],
) -> None:
    ddb = boto3.resource("dynamodb", region_name=region).Table(table_name)
    ddb.put_item(
        Item={
            "analysis_id": analytics_id,
            "commit_sha": commit_sha,
            "environment": env,
            "model_used": model_used,
            "timestamp": now_iso(),
            "word_count": analytics["word_count"],
            "ats_score": analytics["ats_score"],
            "keywords": analytics["keywords"],
            "readability": analytics["readability"],
            "missing_sections": analytics["missing_sections"],
        }
    )


# ----------------------------
# Main
# ----------------------------
def main() -> int:
    region = require_env("AWS_REGION")
    bedrock_region = os.getenv("BEDROCK_REGION", region)

    bucket = require_env("BUCKET_NAME")
    deployment_table = require_env("DEPLOYMENT_TABLE")
    analytics_table = require_env("ANALYTICS_TABLE")

    env = require_env("ENV")
    commit_sha = require_env("COMMIT_SHA")
    model_id = require_env("MODEL_ID")

    resume_md = clamp_text(read_text_file("resume.md"), max_chars=12000)

    deployment_id = str(uuid.uuid4())
    analytics_id = str(uuid.uuid4())

    used_model = model_id
    used_fallback = False
    fallback_reason = None

    # Bedrock-first
    try:
        html_prompt = build_html_prompt(resume_md)
        html_raw = bedrock_invoke_text(
            bedrock_region=bedrock_region,
            model_id=model_id,
            prompt=html_prompt,
            max_tokens=4000,
            temperature=0.2,
            retries=1,
            backoff_seconds=2.0,
        )
        html = sanitize_html(html_raw)

        json_prompt = build_ats_json_prompt(resume_md)
        ats_raw = bedrock_invoke_text(
            bedrock_region=bedrock_region,
            model_id=model_id,
            prompt=json_prompt,
            max_tokens=350,
            temperature=0.1,
            retries=1,
            backoff_seconds=2.0,
        )
        ats_obj = extract_json(ats_raw)
        ats = validate_analytics(ats_obj)

    except Exception as e:
        # FIX: broadened fallback — any Bedrock failure degrades gracefully
        # instead of crashing the pipeline mid-execution after deployment write
        if is_bedrock_fallback_error(e):
            fallback_reason = type(e).__name__
            print(
                f"WARN: Bedrock unavailable ({fallback_reason}: {e}). "
                "Falling back to deterministic rendering/analytics.",
                file=sys.stderr,
            )
            used_model = "fallback-deterministic"
            used_fallback = True
            html = md_to_basic_html(resume_md)
            ats = validate_analytics(basic_ats_analysis(resume_md))
        else:
            raise

    # Upload HTML to S3
    s3_url = upload_html_to_s3(region=region, bucket=bucket, env=env, html=html)

    # Write DynamoDB records
    put_deployment_tracking(
        region=region,
        table_name=deployment_table,
        deployment_id=deployment_id,
        commit_sha=commit_sha,
        env=env,
        status="success",
        s3_url=s3_url,
        model_used=used_model,
    )

    put_resume_analytics(
        region=region,
        table_name=analytics_table,
        analytics_id=analytics_id,
        commit_sha=commit_sha,
        env=env,
        model_used=used_model,
        analytics=ats,
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "environment": env,
                "commit_sha": commit_sha,
                "s3_url": s3_url,
                "deployment_id": deployment_id,
                "analysis_id": analytics_id,
                "model_used": used_model,
                "used_fallback": used_fallback,
                "fallback_reason": fallback_reason,
                "bedrock_region": bedrock_region,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
