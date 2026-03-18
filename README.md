# AI Resume Platform — Serverless AI Delivery Pipeline

A production-grade CI/CD pipeline that converts a Markdown resume into a 
live, versioned website with AI-powered ATS scoring, environment isolation, 
and full deployment auditability.

Resume delivery is treated as an engineering workflow:
- Source of truth in GitHub (`resume.md`)
- Automated rendering + ATS analysis via Amazon Bedrock
- Review-first promotion: beta → production
- Deployment history + analytics persisted in DynamoDB
- Infrastructure defined as code (CloudFormation)
- Served over HTTPS from a global CDN via CloudFront + ACM + custom domain

---

## Live Production Site

🔗 https://willsoto.tech

---

## Outcome

- **Beta site (PR / beta branch):** `s3://ai-resume-iamwillsoto/beta/index.html`
- **Production site:** https://willsoto.tech
- **Auditability:** Each run writes:
  - Deployment metadata to **DeploymentTracking**
  - ATS/quality analytics to **ResumeAnalytics**
- **View Tracking:** Every resume page visit is captured in **ResumeViews** 
  via Lambda + API Gateway, persisting visitor metadata for engagement analytics
- **Reliability:** Bedrock invocation includes **deterministic fallback** 
  when throttled or unavailable.

---

## Architecture

### Components
- **GitHub Actions** — CI/CD orchestration
- **AWS CloudFormation** — IaC for S3 + DynamoDB + IAM
- **Amazon S3** — static hosting with versioning and environment prefixes
- **Amazon CloudFront** — global CDN with HTTPS enforcement and edge caching
- **AWS Certificate Manager (ACM)** — SSL/TLS certificate for custom domain
- **AWS Lambda** — serverless view tracking handler
- **Amazon API Gateway** — HTTP endpoint for view tracking invocation
- **Amazon DynamoDB**
  - `DeploymentTracking`: commit SHA, environment, status, URL, model, timestamp
  - `ResumeAnalytics`: ATS score + structured metrics by analysis ID
  - `ResumeViews`: visitor metadata, timestamps, and engagement records per page visit
- **Amazon Bedrock** — resume rendering + ATS analysis with throttling-aware 
  fallback logic

---

## CI/CD Flow

### Beta (push to `beta`)
1. Deploy/Update CloudFormation stack
2. Run pipeline script:
   - Render resume (Bedrock-first, fallback-enabled)
   - Generate ATS analytics (Bedrock-first, fallback-enabled)
3. Upload output to `s3://ai-resume-iamwillsoto/beta/index.html`
4. Write DynamoDB records:
   - `DeploymentTracking` (beta deployment)
   - `ResumeAnalytics` (analysis record)

### Production (push to `main`)
1. Deploy/Update CloudFormation stack
2. Run pipeline in production mode
3. Upload output to `s3://ai-resume-iamwillsoto/prod/index.html`
4. Serve via CloudFront distribution at https://willsoto.tech
5. Write deployment metadata to `DeploymentTracking`

### View Tracking (runtime, per visit)
1. Resume page loads at https://willsoto.tech
2. JavaScript invokes API Gateway endpoint
3. Lambda handler processes the request
4. Visitor metadata and timestamp written to `ResumeViews` in DynamoDB

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
└── validation-screenshots/       # evidence screenshots
```

---

## Configuration

### GitHub Secrets

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### Runtime Environment Variables

- `BUCKET_NAME`
- `DEPLOYMENT_TABLE`
- `ANALYTICS_TABLE`
- `VIEWS_TABLE`
- `ENV` (beta | prod)
- `COMMIT_SHA`
- `MODEL_ID`

---

## Bedrock Throttling & Fallback Design

AI invocation may be throttled due to account or regional limits.
This pipeline remains fully functional under those conditions by:

- Falling back to deterministic resume rendering
- Falling back to deterministic ATS analysis
- Preserving deployment history and analytics integrity
- Keeping CI/CD pipelines green and auditable

This mirrors real production resilience patterns used in platform engineering.

---

## What This Project Demonstrates

- Production-grade CI/CD with environment isolation
- Infrastructure as Code using CloudFormation
- Automated artifact publishing to S3
- Global HTTPS delivery via CloudFront + ACM + custom domain
- Deployment and analytics persistence in DynamoDB
- Resume view tracking via Lambda + API Gateway + DynamoDB
- Resilient pipeline design under third-party service constraints
- Clear separation between application logic and infrastructure
