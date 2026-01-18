# Will A. Soto

Providence, Rhode Island  
Email: willalbertosoto@gmail.com  
Phone: 857.544.6474  
LinkedIn: www.linkedin.com/in/wilmeralberto  
GitHub: iamwillsoto

---

## SUMMARY

Cloud DevOps Engineer with hands-on experience designing, automating, and operating secure, scalable AWS cloud environments. Delivers production-ready platforms using Infrastructure as Code, CI/CD automation, and AWS-native services to support reliable, observable, and well-governed workloads. Brings over 10 years of experience in high-accountability environments, including U.S. Navy service and client-facing, quota-driven roles, informing disciplined execution, clear technical communication, and alignment of engineering decisions with business and operational outcomes.

---

## SKILLS

### Cloud Platform Engineering
Amazon Web Services (VPC, EC2, S3, IAM, Lambda, EventBridge, CloudWatch), AWS CLI

### Infrastructure as Code
Terraform, AWS CloudFormation

### CI/CD & Automation
GitHub Actions, Git, YAML, automated promotion workflows with environment isolation (beta → prod)

### Observability & Operations
AWS CloudWatch (metrics and logs), Splunk (log ingestion and analysis for cloud workloads)

### Systems & Containers
Linux systems engineering, Docker, containerized workloads, Kubernetes (container orchestration for development workloads)

### Programming & Scripting
Python (boto3 for AWS automation), Bash, PowerShell

---

## PROJECTS

### Prompt Deployment Pipeline | Amazon Bedrock + S3 + GitHub Actions  
Use Case: Automate AI-powered content creation and publishing for static websites.
  
- Designed and implemented a GitHub-based CI/CD pipeline to process prompt templates and configuration files and automatically generate publishable content
- Developed a Python automation workflow (process_prompt.py) to render prompt templates with environment-specific variables and submit structured requests to Amazon Bedrock
- Generated AI-produced content as HTML and Markdown artifacts and uploaded outputs to Amazon S3 for static website hosting
- Implemented environment isolation using versioned S3 prefixes (beta/, prod/) to support controlled promotion from review to production
- Managed pipeline execution through pull requests and branch merges, with secrets and credentials securely handled via GitHub Actions

### Multilingual Audio Pipeline | Amazon Transcribe + Translate + Polly + S3 + GitHub Actions  
Use Case: Automate voice-to-voice translation for multilingual audio content.

- Built an end-to-end, automated audio processing pipeline using AWS managed AI services and Python
- Developed a Python workflow (process_audio.py) to upload audio files to Amazon S3, transcribe speech with Amazon Transcribe, translate text using Amazon Translate, and synthesize multilingual speech with Amazon Polly
- Structured outputs into organized S3 paths (transcripts/, translations/, audio_outputs/) to support traceability and reuse
- Automated execution using GitHub Actions workflows for pull request (beta) and main branch (production) deployments
- Secured AWS credentials and environment-specific configuration using GitHub Secrets 

### Two-Tier Web Architecture on AWS | EC2 + RDS + VPC  
Use Case: Deploy a secure and scalable content management website.

- Designed and deployed a custom Amazon VPC with public and private subnets, routing tables, and an Internet Gateway
- Provisioned an Ubuntu-based EC2 instance for the web tier and a MySQL-backed Amazon RDS instance for the database tier
- Implemented network isolation and security controls using security groups and subnet segmentation (EC2 in public, RDS in private)
- Validated application connectivity and documented the benefits of a two-tier architecture

### EC2 Shutdown Automation | AWS Lambda + GitHub Actions + CloudFormation  
Use Case: Reduce unnecessary EC2 runtime costs for non-production environments.

- Developed a Python-based AWS Lambda function using boto3 to identify and stop EC2 instances based on state and tags
- Scheduled automated shutdowns using Amazon EventBridge to enforce cost-control policies
- Packaged and deployed the solution using Amazon S3 and AWS CloudFormation, including IAM roles and permissions
- Automated deployments with GitHub Actions using separate beta and production workflows
- Managed environment-specific parameters and AWS credentials using GitHub Secrets

---

## EXPERIENCE

### Client Solutions Specialist / Enterprise Engagement  
Confidential Healthcare Technology Organization — Remote
December 2024 – Present

- Operate in a high-accountability, metrics-driven environment requiring disciplined execution, prioritization, and consistent delivery under pressure  
- Collaborate with cross-functional stakeholders to translate business requirements into structured workflows, operational processes, and measurable outcomes  
- Maintain rigorous documentation standards, process hygiene, and handoff practices to support reliability and continuity across teams  
- Communicate complex technical and operational concepts clearly to leadership, partners, and non-technical stakeholders

---

## EDUCATION

Bachelor of Science, Cloud Computing  
Western Governors University, Salt Lake City, UT - Expected Completion: June 2026

---

## CERTIFICATIONS

### Completed
CompTIA Security+ — April 2025  
AWS SysOps Administrator – Associate — July 2025  
AWS Solutions Architect – Associate — December 2025 
AWS Certified AI Practitioner — January 2026

### In Progress / Planned
HashiCorp Certified: Terraform Associate — Planned March 2026  
Splunk Core Certified Power User — Planned April 2026