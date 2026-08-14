# AWS Deployment Guide — Hodgkin Lymphoma Risk Prediction Platform

This document describes the recommended AWS architecture and the steps to
deploy this project yourself. Nothing here has been deployed — these are
instructions and configuration for you to execute.

## Architecture Overview
┌─────────────────┐
│   Route 53 (DNS) │  (optional)
└────────┬─────────┘
│
┌────────▼─────────┐
│   CloudFront CDN │  → S3 (frontend static files)
└────────┬─────────┘
│ HTTPS
┌────────▼─────────┐
│  ALB / API GW    │  (HTTPS termination)
└────────┬─────────┘
│
┌────────▼─────────┐
│  ECS Fargate     │  (backend container)
│  or EC2 instance │
└────────┬─────────┘
│
┌────────▼─────────┐
│  RDS PostgreSQL  │  (managed database)
└──────────────────┘
## Component choices

| Component | Service | Why |
|---|---|---|
| Frontend hosting | S3 + CloudFront | Static files, cheap, fast, HTTPS via ACM |
| Backend hosting | ECS Fargate (recommended) or EC2 | Fargate = no server management; EC2 = simpler mental model, more manual |
| Database | RDS PostgreSQL | Managed backups, patching, monitoring |
| Secrets | AWS Secrets Manager or SSM Parameter Store | Never put JWT_SECRET/DB password in code |
| ML model storage | S3 (optional) | If you want the model artifact outside the container image |
| Container registry | ECR | Stores your Docker images |

---

## Part 1 — RDS PostgreSQL

1. AWS Console → RDS → Create database
2. Engine: PostgreSQL 16
3. Templates: Free tier (for a college project) or Dev/Test
4. DB instance identifier: `hodgkin-db`
5. Master username: `hodgkin_admin` (don't reuse local dev credentials)
6. Master password: generate a strong one, store it in Secrets Manager
7. Instance: `db.t3.micro` (free tier eligible)
8. Storage: 20 GB gp3
9. **Connectivity**:
    - VPC: default or a custom one
    - Public access: **No** (backend will reach it via VPC, not the internet)
    - VPC security group: create new, name it `hodgkin-db-sg`
10. Create database
11. Once available, note the **endpoint** (e.g. `hodgkin-db.xxxxx.us-east-1.rds.amazonaws.com`)

### Security Group for RDS
- Inbound rule: PostgreSQL (5432) from the **backend's security group only** (not `0.0.0.0/0`)
- No inbound from the public internet

### Run migrations against RDS
From your local machine (temporarily allow your IP in the RDS security group, or use a bastion/SSM tunnel), set:
Then run:
Afterward, remove your IP from the security group again.

---

## Part 2 — ECR (container registry)

1. AWS Console → ECR → Create repository
2. Name: `hodgkin-backend`
3. Push your image:
```bash
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com

docker build -t hodgkin-backend ./backend
docker tag hodgkin-backend:latest <account-id>.dkr.ecr.<your-region>.amazonaws.com/hodgkin-backend:latest
docker push <account-id>.dkr.ecr.<your-region>.amazonaws.com/hodgkin-backend:latest
```

---

## Part 3 — ECS Fargate (backend)

1. AWS Console → ECS → Create cluster (Fargate)
2. Cluster name: `hodgkin-cluster`
3. Create a **Task Definition**:
    - Launch type: Fargate
    - Task size: 0.5 vCPU / 1GB memory (adjust if ML inference needs more)
    - Container image: your ECR image URI
    - Port mapping: 8000
    - Environment variables (or better, reference Secrets Manager):
    - DATABASE_URL       -> from Secrets Manager
      JWT_SECRET          -> from Secrets Manager
      JWT_ALGORITHM        = HS256
      ENVIRONMENT           = production
      CORS_ORIGINS          = https://your-cloudfront-domain.cloudfront.net
      API_PREFIX             = /api
      MODEL_VERSION          = 1.0.0
- 4. Create a **Service**:
    - Cluster: `hodgkin-cluster`
    - Launch type: Fargate
    - Desired tasks: 1 (scale up later if needed)
    - VPC: same as RDS
    - Security group: `hodgkin-backend-sg` — allow inbound 8000 from the ALB only
    - Load balancer: Application Load Balancer (new)
        - Listener: HTTPS (443) — requires an ACM certificate
        - Target group: forwards to port 8000

### ML model artifact
Your `ml/models/hodgkin_model.pth` needs to be available inside the container. Options:
- **Simplest**: bake it into the Docker image (`COPY ml/models ./ml_models` in the Dockerfile) — fine for a college project, just means rebuilding the image if you retrain
- **More flexible**: upload to S3, have the container download it at startup using an IAM role scoped to that bucket

---

## Part 4 — S3 + CloudFront (frontend)

1. AWS Console → S3 → Create bucket
2. Name: `hodgkin-frontend-<your-unique-suffix>`
3. Block all public access: **keep this ON** (CloudFront will access it via Origin Access Control, not public bucket policy)
4. Upload your `frontend/` contents (or automate with `aws s3 sync`):
```bash
aws s3 sync ./frontend s3://hodgkin-frontend-<suffix>/ --delete
```
5. AWS Console → CloudFront → Create distribution
    - Origin: the S3 bucket (select "Origin Access Control" when prompted)
    - Default root object: `pages/register.html`
    - Viewer protocol policy: Redirect HTTP to HTTPS
6. Request an ACM certificate (in `us-east-1`, required for CloudFront) if using a custom domain

### Update the frontend's API URL
Before uploading, change `frontend/js/api.js`:
```javascript
const API_BASE = "https://your-backend-domain.com/api";
```
(Currently hardcoded to `http://localhost:8000/api` for local dev — this must point to your ALB/API Gateway HTTPS endpoint in production.)

---

## Part 5 — IAM

Create a dedicated IAM role for the ECS task (not your personal AWS credentials):
- **Task execution role**: `AmazonECSTaskExecutionRolePolicy` (lets ECS pull from ECR, write logs)
- **Task role** (used by your app code, if it needs AWS API access — e.g. reading the model from S3):
    - Custom policy scoped to only the specific S3 bucket/prefix needed, e.g.:
```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": ["s3:GetObject"],
          "Resource": "arn:aws:s3:::hodgkin-ml-models/*"
        }
      ]
    }
```

Never attach `AdministratorAccess` to a task role.

---

## Part 6 — Security Groups Summary

| Security Group | Inbound | Outbound |
|---|---|---|
| `hodgkin-alb-sg` | 443 from `0.0.0.0/0` | to `hodgkin-backend-sg` on 8000 |
| `hodgkin-backend-sg` | 8000 from `hodgkin-alb-sg` only | to `hodgkin-db-sg` on 5432, to internet for package updates |
| `hodgkin-db-sg` | 5432 from `hodgkin-backend-sg` only | — |

---

## Part 7 — HTTPS

- CloudFront: use ACM certificate (free) for your custom domain, or the default `*.cloudfront.net` domain works out of the box with HTTPS
- ALB: request/import an ACM certificate for your backend domain, attach to the HTTPS listener
- Never expose the backend over plain HTTP in production

---

## Part 8 — Environment Variables / Secrets

Use **AWS Secrets Manager** for `DATABASE_URL` and `JWT_SECRET`:
```bash
aws secretsmanager create-secret --name hodgkin/jwt-secret --secret-string "<generate-a-real-random-value>"
aws secretsmanager create-secret --name hodgkin/database-url --secret-string "postgresql+psycopg://hodgkin_admin:<password>@<rds-endpoint>:5432/hodgkin_db"
```
Reference these in your ECS Task Definition's `secrets` block instead of `environment`, so they're never visible in plaintext in the console or logs.

---

## Part 9 — Logging & Monitoring

- ECS tasks automatically send stdout/stderr to **CloudWatch Logs** if configured in the task definition (log driver: `awslogs`)
- Set up a CloudWatch Alarm on ECS service health / ALB 5xx error rate for basic monitoring
- RDS has built-in CloudWatch metrics (CPU, connections, storage) — check these periodically

---

## Cost note (for a college project)

Free tier covers: RDS `db.t3.micro` (750 hrs/month for 12 months), S3 (5GB), some CloudFront usage. **ECS Fargate is NOT free tier** — it bills per vCPU/memory-second. For a demo, consider running the backend on a free-tier EC2 instance with Docker Compose instead of Fargate, and shutting it down when not actively demoing.

---

## What has and hasn't been done

- ✅ This document describes the architecture and steps
- ❌ Nothing has been deployed — no AWS resources have been created
- ❌ No claims of "production readiness" are made — this is a college project;
  security review, load testing, and cost optimization would be needed before
  any real-world use