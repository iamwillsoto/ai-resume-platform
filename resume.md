# WILL A. SOTO
**AWS Cloud Engineer | US Navy Veteran**

Providence, RI | sotowilmeralberto@gmail.com | 857-544-6474 | linkedin.com/in/iamwillsoto | github.com/iamwillsoto

---

## PROFESSIONAL SUMMARY

AWS Cloud Engineer specializing in enterprise AWS platforms, Terraform-driven infrastructure, and production-grade CI/CD automation. Experienced in designing and supporting secure, highly available cloud environments with a focus on scalable networking, infrastructure as code, governance, and operational reliability. Hands-on experience integrating Generative AI services such as Amazon Bedrock into cloud-native automation workflows.

---

## SKILLS

**AWS Infrastructure:** VPC, Transit Gateway, Route 53, ALB, Auto Scaling, EC2, RDS (Multi-AZ), S3, Lambda, API Gateway, DynamoDB
**Infrastructure as Code:** Terraform (Cloud & Remote State), CloudFormation, Ansible, Packer
**Security & Governance:** IAM, RBAC, KMS, GuardDuty, Security Hub, AWS Config, AWS WAF
**Containers & Compute:** Docker, Docker Swarm, Amazon ECS, Kubernetes
**Observability & Operations:** CloudWatch, EventBridge, VPC Flow Logs, Datadog, Prometheus, Grafana, Splunk
**Automation & Scripting:** Python, Boto3, Bash, PowerShell, Linux, GitHub Actions, Jenkins, Bitbucket
**AI Integration:** Amazon Bedrock, Rekognition, Transcribe, Translate, Polly

---

## EXPERIENCE

### HD SUPPLY | Cloud Infrastructure Engineer (Contract)
**Jun 2024 – Mar 2026**

- Architected segmented multi-VPC AWS environment with Transit Gateway centralized routing, enforcing deterministic east-west traffic control and isolating production workloads to reduce cross-environment risk.
- Automated compliance evidence generation using AWS Lambda and PowerShell, converting Security Hub and Inspector findings into structured audit artifacts and reducing manual evidence collection by 60%.
- Standardized Route 53 DNS governance with public/private hosted zone separation and routing policies, improving service resolution reliability and eliminating ad-hoc DNS sprawl across environments.
- Implemented enterprise security baselines using KMS encryption, scoped IAM role hierarchies, and RBAC boundary controls to minimize standing privilege and reduce infrastructure blast radius.
- Established Terraform-driven infrastructure convergence with AWS Config rule validation to detect and remediate configuration drift across beta and production environments.

---

### LEVELUPINTECH | Cloud Engineer
**Feb 2024 – Oct 2024**

- Architected multi-tier AWS infrastructure using Terraform Cloud across ALB, Auto Scaling, and RDS with private subnet isolation and high-availability deployment across multiple Availability Zones.
- Developed reusable VPC Terraform modules implementing segmented subnets, controlled route propagation, and standardized NAT gateway egress patterns to enforce predictable network traffic flows.
- Strengthened platform security posture by integrating GuardDuty threat detection, AWS Config compliance validation, and KMS encryption standards across compute and storage layers.
- Provisioned Amazon Bedrock AI pipelines with DynamoDB-backed persistence and throttling-aware fallback logic to support reliable AI service integration across isolated environments.

---

### VERIZON | Cloud Support Engineer
**Jan 2021 – Mar 2024**

- Operated enterprise AWS production environments sustaining 99.9%+ SLA adherence through CloudWatch alarm strategy, scaling policy optimization, and proactive degradation detection.
- Reduced MTTR by 25% through log correlation, metric threshold tuning, IAM policy evaluation, and structured incident response workflows.
- Executed controlled infrastructure modifications using Terraform and CloudFormation within governed IAM boundaries, ensuring policy-compliant change execution.
- Diagnosed complex routing, DNS resolution, and load balancer health failures using VPC Flow Logs and CloudWatch Insights to restore service integrity.

---

## PROJECTS

### AI Resume Platform — Serverless AI Delivery Pipeline
**Amazon Bedrock · CloudFormation · GitHub Actions · Lambda · API Gateway · DynamoDB · S3**
*Live: ai-resume-iamwillsoto.s3.amazonaws.com/prod/index.html | GitHub: github.com/iamwillsoto/ai-resume-platform*

- Built a serverless AI-powered resume scoring platform using Amazon Bedrock and Lambda, processing resume submissions through API Gateway and returning structured ATS evaluations with throttling-aware fallback logic.
- Provisioned all infrastructure using AWS CloudFormation, enabling repeatable, version-controlled deployments across isolated beta and production environments.
- Automated platform delivery via GitHub Actions CI/CD pipeline enforcing review-first promotion — PRs deploy to beta, merges promote validated artifacts to production.
- Persisted deployment metadata and ATS analytics to DynamoDB, enabling longitudinal scoring history and full audit traceability across pipeline executions.

---

### Prompt Deployment Pipeline — Event-Driven AI Content Delivery
**Terraform · Amazon Bedrock · GitHub Actions · Lambda · S3 · IAM · CloudWatch**
*GitHub: github.com/iamwillsoto/prompt-deployment-pipeline*

- Designed an event-driven prompt execution pipeline decoupling AI inference from CI workflows — S3 ObjectCreated events trigger Lambda, which renders prompts and invokes Bedrock on demand.
- Provisioned all infrastructure with Terraform including Lambda functions, IAM least-privilege roles, S3 event notifications, and environment-scoped storage paths across beta and production.
- Enforced structural environment isolation — pull requests deploy exclusively to beta resources, merges to main promote the same execution path to production with no code changes.
- Validated execution through durable CloudWatch logs and S3 output artifacts, providing full traceability of prompt rendering, inference, and content publication per run.

---

### Automated EC2 Governance — Serverless Shutdown & Audit Pipeline
**Lambda · EventBridge · DynamoDB · API Gateway · CloudFormation · GitHub Actions**
*GitHub: github.com/iamwillsoto/lambda-ec2-shutdown*

- Built a tag-governed Lambda workflow that automatically stops Dev EC2 instances nightly via EventBridge, targeting only instances tagged `Environment=Dev` and `AutoShutdown=True` to protect production workloads.
- Implemented DynamoDB audit logging for every shutdown event, capturing instance ID, tags, timestamp, and request metadata for governance traceability and cost reporting.
- Exposed on-demand shutdown capability via API Gateway HTTP API with tag-based query parameters, enabling release-driven cleanup without console access.
- Deployed across beta and production using GitHub Actions CI/CD pipelines with CloudFormation, enforcing review-gated promotion and consistent environment parity.

---

## UNITED STATES NAVY | Boatswain's Mate
**Jan 2010 – Mar 2014 | USS Lake Champlain (CG-57), San Diego, CA**

- Served aboard the guided missile cruiser USS Lake Champlain supporting maritime operations requiring rapid decision-making, operational discipline, and mission execution in high-pressure environments.

---

## CERTIFICATIONS

**AWS Certified Solutions Architect – Associate** | Dec 2025
**AWS Certified SysOps Administrator – Associate** | Jul 2025
**AWS Certified AI Practitioner** | Jan 2026
**AWS Certified Security – Specialty** | Expected
**CompTIA Security+** | Apr 2025
**CompTIA Network+** | Feb 2026
**Linux Essentials Certificate (LPI)** | Oct 2025
**AWS Community Builder** | 2026 – Present

---

## EDUCATION

**Western Governors University**
Bachelor of Science, Cloud & Network Engineering 
