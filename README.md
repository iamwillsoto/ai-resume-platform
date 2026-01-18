# AI-Generated Resume Website (Beta → Prod) — CloudFormation + GitHub Actions + DynamoDB

A production-style CI/CD pipeline that converts a Markdown resume into a public, versioned HTML website and stores ATS-style analytics for auditability and iteration over time.

This project treats resume publishing as an engineering workflow:
- Source of truth in GitHub (`resume.md`)
- Automated rendering + analysis in CI
- Environment isolation (beta → prod)
- Deployment history + analytics persisted in DynamoDB
- Infrastructure defined as code (CloudFormation)

---

## Outcome

- **Beta site (PR / beta branch):** `s3://ai-resume-iamwillsoto/beta/index.html`
- **Production site (main branch):** `s3://ai-resume-iamwillsoto/prod/index.html`
- **Auditability:** Each run writes:
  - deployment metadata to **DeploymentTracking**
  - ATS/quality analytics to **ResumeAnalytics**
- **Reliability:** Bedrock invocation includes **deterministic fallback** when throttled or unavailable.

---

## Architecture

### Components
- **GitHub Actions** — CI/CD orchestration
- **AWS CloudFormation** — IaC for S3 + DynamoDB (+ IAM for pipeline access)
- **Amazon S3** — public static hosting with versioning and environment prefixes
- **Amazon DynamoDB**
  - `DeploymentTracking`: commit SHA, environment, status, URL, model, timestamp
  - `ResumeAnalytics`: ATS score + structured metrics by analysis id
- **Amazon Bedrock (optional / best-effort)** — resume rendering + ATS analysis
  - Pipeline falls back to deterministic rendering/analysis when Bedrock is throttled

---

## CI/CD Flow

### Beta (push to `beta`)
1. Deploy/Update CloudFormation stack
2. Run pipeline script:
   - Render resume (Bedrock-first, fallback-enabled)
   - Generate ATS analytics (Bedrock-first, fallback-enabled)
3. Upload output to:
   - `s3://ai-resume-iamwillsoto/beta/index.html`
4. Write DynamoDB records:
   - `DeploymentTracking` (beta deployment)
   - `ResumeAnalytics` (analysis record)

### Production (push to `main`)
1. Deploy/Update CloudFormation stack
2. Run pipeline in production mode:
   - Promote or generate prod artifact (depending on pipeline configuration)
3. Upload output to:
   - `s3://ai-resume-iamwillsoto/prod/index.html`
4. Write deployment metadata to `DeploymentTracking`

---

## Repo Structure

```text
.
├── app/
│   ├── resume_pipeline.py        # end-to-end pipeline (render, analyze, upload, record)
│   └── requirements.txt
├── infra/
│   └── template.yaml             # CloudFormation (S3 + DynamoDB + IAM)
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD workflow (beta + prod jobs)
├── resume.md                     # source-of-truth resume content
└── validation-screenshots/       # evidence screenshots (tracked)
```

## Configuration
### GitHub Secrets

Required repository secrets:

- AWS_ACCESS_KEY_ID

- AWS_SECRET_ACCESS_KEY

- AWS_REGION

### Runtime Environment Variables

Provided by the workflow:

- BUCKET_NAME

- DEPLOYMENT_TABLE

- ANALYTICS_TABLE

- ENV (beta | prod)

- COMMIT_SHA

- MODEL_ID

## Bedrock Throttling & Fallback Design

AI invocation may be throttled due to account or regional limits.
This pipeline remains fully functional under those conditions by:

- Falling back to deterministic resume rendering

- Falling back to deterministic ATS analysis

- Preserving deployment history and analytics integrity

- Keeping CI/CD pipelines green and auditable

This mirrors real production resilience patterns used in platform engineering.

## What This Project Demonstrates

- Production-grade CI/CD with environment isolation

- Infrastructure as Code using CloudFormation

- Automated artifact publishing to S3

- Deployment and analytics persistence in DynamoDB

- Resilient pipeline design under third-party service constraints

- Clear separation between application logic and infrastructure

## Optional Enhancements

- CloudFront + Route 53 + ACM for custom domain and HTTPS

- Origin Access Control (OAC) with private S3

- Automated PR comments with beta URL and ATS delta

- Cost metrics and trend analysis in DynamoDB
