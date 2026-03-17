# WILL A. SOTO
**AWS Cloud Engineer | US Navy Veteran**

Providence, RI | sotowilmeralberto@gmail.com | 857-544-6474 | linkedin.com/in/iamwillsoto | github.com/iamwillsoto

---

## PROFESSIONAL SUMMARY

AWS Cloud Engineer specializing in enterprise AWS platforms, Terraform-driven infrastructure, and production-grade CI/CD automation. Experienced in designing and supporting secure, highly available cloud environments with a focus on scalable networking, infrastructure as code, governance, and operational reliability. Hands-on experience integrating Amazon Bedrock into cloud-native automation workflows.

---

## SKILLS

**AWS Infrastructure:** VPC, Transit Gateway, Route 53, ALB, Auto Scaling, EC2, RDS, S3, Lambda, API Gateway, DynamoDB  
**Infrastructure as Code & Automation:** Terraform, CloudFormation, GitHub Actions, Jenkins, Python, Boto3, Bash, PowerShell, Linux  
**Security & Operations:** IAM, RBAC, KMS, GuardDuty, Security Hub, AWS Config, CloudWatch, EventBridge, VPC Flow Logs  
**Containers:** Docker, Docker Swarm, ECS, Kubernetes  
**AI Services:** Amazon Bedrock, Rekognition, Transcribe, Translate, Polly

---

## EXPERIENCE

### HD SUPPLY | Cloud Infrastructure Engineer (Contract)
**Jun 2024 – Present**

- Architected segmented multi-VPC AWS environment with Transit Gateway centralized routing, enforcing deterministic east-west traffic control and isolating production workloads to reduce cross-environment risk.
- Automated compliance evidence generation using AWS Lambda and PowerShell, converting Security Hub and Inspector findings into structured audit artifacts and reducing manual evidence collection by 60%.
- Standardized Route 53 DNS governance with public/private hosted zone separation and routing policies, improving service resolution reliability and eliminating ad-hoc DNS sprawl across environments.
- Implemented enterprise security baselines using KMS encryption, scoped IAM role hierarchies, and RBAC boundary controls to minimize standing privilege and reduce infrastructure blast radius.
- Established Terraform-driven infrastructure convergence with AWS Config rule validation to detect and remediate configuration drift across beta and production environments.

### LEVELUPINTECH | Cloud Engineer
**Feb 2024 – Oct 2024**

- Architected multi-tier AWS infrastructure using Terraform Cloud across ALB, Auto Scaling, and RDS with private subnet isolation and high-availability deployment across multiple Availability Zones.
- Developed reusable VPC Terraform modules implementing segmented subnets, controlled route propagation, and standardized NAT gateway egress patterns to enforce predictable network traffic flows.
- Strengthened platform security posture by integrating GuardDuty threat detection, AWS Config compliance validation, and KMS encryption standards across compute and storage layers.
- Provisioned Amazon Bedrock AI pipelines with DynamoDB-backed persistence and throttling-aware fallback logic to support reliable AI service integration across isolated environments.

### VERIZON | Cloud Support Engineer
**Jan 2021 – Mar 2024**

- Operated enterprise AWS production environments sustaining 99.9%+ SLA adherence through CloudWatch alarm strategy, scaling policy optimization, and proactive degradation detection.
- Diagnosed complex routing, DNS resolution, and load balancer health failures using VPC Flow Logs and CloudWatch Insights to restore service integrity.

### UNITED STATES NAVY | Boatswain's Mate
**Jan 2010 – Mar 2014 | USS Lake Champlain (CG-57), San Diego, CA**

- Served aboard the guided missile cruiser USS Lake Champlain supporting maritime operations requiring rapid decision-making, operational discipline, and mission execution in high-pressure environments.

---

## PROJECTS

### AI Resume Platform — Serverless AI Delivery Pipeline
**Amazon Bedrock · CloudFormation · GitHub Actions · Lambda · API Gateway · DynamoDB · S3**  
**Live Demo:** [Resume Platform](https://ai-resume-iamwillsoto.s3.amazonaws.com/prod/index.html) | **GitHub:** [Repo](https://github.com/iamwillsoto/ai-resume-platform)

- Built a serverless AI-powered resume scoring platform using Amazon Bedrock and Lambda, processing resume submissions through API Gateway and returning structured ATS evaluations.
- Provisioned all infrastructure using AWS CloudFormation, enabling repeatable, version-controlled deployments across isolated beta and production environments.
- Automated delivery through GitHub Actions CI/CD with review-first promotion from beta to production.

### Automated EC2 Governance — Serverless Shutdown & Audit Pipeline
**Lambda · EventBridge · DynamoDB · API Gateway · CloudFormation · GitHub Actions**  
**GitHub:** [Repo](https://github.com/iamwillsoto/lambda-ec2-shutdown)

- Built a tag-governed Lambda workflow that automatically stops Dev EC2 instances nightly via EventBridge, targeting only approved non-production resources.
- Implemented DynamoDB audit logging for every shutdown event, capturing instance ID, tags, timestamp, and request metadata for governance traceability.
- Exposed on-demand shutdown capability through API Gateway, enabling controlled cleanup without console access.

---

## CERTIFICATIONS & RECOGNITION

**AWS Certified Solutions Architect – Associate** | Dec 2025  
**AWS Certified SysOps Administrator – Associate** | Jul 2025  
**AWS Certified AI Practitioner** | Jan 2026  
**CompTIA Security+** | Apr 2025  
**CompTIA Network+** | Feb 2026  
**AWS Community Builder** | 2026 – Present

---

## EDUCATION

**Western Governors University** | Bachelor of Science, Cloud & Network Engineering
