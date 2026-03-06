# Directive 06 — README and Documentation

## Objective
Write a README that enables any engineer to clone the repo and have CloudPulse fully running in under 30 minutes. It must be polished enough to attract GitHub stars from the DevOps/platform engineering community.

---

## Inputs
- Completed Milestones 1–5
- Architecture decisions documented in `spec.md`
- Screenshots of the running app (capture after Milestone 4)

---

## README Structure

### 1. Header
- Project name: **CloudPulse**
- Tagline: "Open-source AWS cost and resource monitoring — self-hosted, no SaaS fees."
- Badges: CI status, Python version, License (MIT), Terraform version
- Screenshot of the dashboard (hero image)

### 2. Mermaid Architecture Diagram
```mermaid
graph TB
    subgraph Browser
        UI[React SPA<br/>Recharts + Tailwind]
    end

    subgraph Backend
        API[Flask REST API<br/>Python 3.11]
        SVC[boto3 Services<br/>Cost Explorer, EC2, S3, Lambda]
    end

    subgraph AWS
        CE[Cost Explorer API]
        EC2[EC2 API]
        S3API[S3 API]
        LAPI[Lambda API]
        DDB[DynamoDB<br/>cloudpulse-costs]
        CWE[CloudWatch Events<br/>rate(1 hour)]
        LFN[Lambda Function<br/>cloudpulse-poller]
    end

    subgraph Terraform
        TF[Terraform 1.7+<br/>S3 Remote State]
    end

    UI -->|GET /api/*| API
    API --> SVC
    SVC -->|GetCostAndUsage| CE
    SVC -->|DescribeInstances| EC2
    SVC -->|ListAllMyBuckets| S3API
    SVC -->|ListFunctions| LAPI
    SVC -->|Query/PutItem| DDB
    CWE -->|Invoke| LFN
    LFN -->|GetCostAndUsage| CE
    LFN -->|PutItem| DDB
    TF -.->|provisions| DDB
    TF -.->|provisions| LFN
    TF -.->|provisions| CWE
```

### 3. Features
- Bullet list of all features (with emoji if desired):
  - Daily and monthly cost breakdown by AWS service
  - 7-day cost trend charts
  - EC2 / S3 / Lambda resource inventory
  - Anomaly detection (>20% day-over-day spikes)
  - Mock mode — runs without AWS credentials
  - Infrastructure as Code (Terraform)
  - Automated CI/CD pipeline (GitHub Actions)

### 4. Prerequisites
```
- AWS Account (optional — mock mode works without it)
- AWS CLI configured (aws configure)
- Terraform >= 1.7
- Python 3.11
- Node.js 20 LTS
- npm 10+
```

### 5. Quick Start (Mock Mode — No AWS Required)
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/cloudpulse.git
cd cloudpulse

# 2. Backend (mock mode auto-enabled when no AWS creds)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
MOCK_MODE=true flask run --port 5000

# 3. Frontend (in a new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### 6. Full Setup (With AWS Account)
```bash
# Step 1: Configure AWS credentials
aws configure

# Step 2: Bootstrap Terraform state bucket (one-time)
aws s3 mb s3://cloudpulse-tf-state-$(aws sts get-caller-identity --query Account --output text) \
  --region us-east-1

# Step 3: Provision infrastructure
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init \
  -backend-config="bucket=YOUR_STATE_BUCKET" \
  -backend-config="key=cloudpulse/terraform.tfstate" \
  -backend-config="region=us-east-1"
terraform plan
terraform apply

# Step 4: Configure environment
cp .env.example .env
# Edit .env with your DynamoDB table name and region

# Step 5: Seed initial cost data
cd ..
source backend/.venv/bin/activate
python execution/snapshot_costs.py

# Step 6: Start backend
cd backend && flask run --port 5000

# Step 7: Start frontend (new terminal)
cd frontend && npm run dev
```

### 7. Environment Configuration
Table of all env vars (from spec.md Section 12) with descriptions and example values.

### 8. Mock Mode Instructions
- Explain auto-detection: if no AWS creds found, backend serves mock data
- Explain frontend toggle: switch in the header bar
- Note: mock data is realistic but static
- How to customize mock data: edit `frontend/src/mock/*.json`

### 9. Development

#### Running tests
```bash
# Backend
cd backend && pytest -v

# Frontend
cd frontend && npm test
```

#### Linting
```bash
# Python
flake8 backend/ execution/

# TypeScript
cd frontend && npm run lint
```

#### Local DynamoDB (optional)
```bash
docker run -p 8000:8000 amazon/dynamodb-local
AWS_ENDPOINT_URL=http://localhost:8000 python execution/seed_mock_data.py
```

### 10. Screenshots
```
[Screenshot: Main dashboard with cost charts]
[Screenshot: Anomaly alert panel showing critical spike]
[Screenshot: Resource inventory table]
[Screenshot: Mock mode toggle]
```
_(Replace with actual screenshots after Milestone 4)_

### 11. Cost Estimate
Monthly AWS infrastructure cost estimate:
| Resource | Monthly Cost |
|----------|-------------|
| DynamoDB (on-demand, <1M reads/writes) | ~$0.00 (free tier) |
| Lambda (1 invocation/hour, <1s runtime) | ~$0.00 (free tier) |
| CloudWatch Logs (minimal) | ~$0.02 |
| S3 state bucket | ~$0.01 |
| Cost Explorer API ($0.01/request) | ~$0.72/month |
| **Total** | **~$0.75/month** |

_Free tier covers DynamoDB and Lambda entirely for most accounts._

### 12. Contributing
- Fork the repo
- Create a feature branch
- Run tests: `pytest` + `npm test`
- Run lint: `flake8` + `npm run lint`
- Open a PR — CI will run automatically

### 13. License
MIT License — see `LICENSE` file.

---

## Files to Create

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `LICENSE` | MIT license text |
| `brand-guidelines.md` | Color palette and fonts |
| `.env.example` | All env vars with example values |
| `infra/terraform.tfvars.example` | All Terraform vars with descriptions |

---

## Quality Bar
Before marking Milestone 6 done, verify:
- [ ] A stranger can follow README from clone to running app without asking any questions
- [ ] All commands in README are copy-pasteable and correct
- [ ] Architecture diagram renders correctly in GitHub markdown preview
- [ ] All screenshots are present (not placeholder labels)
- [ ] Badges in header all pass/display correctly
- [ ] `MOCK_MODE=true flask run` actually works as documented

---

## Updates Log
_Update this section as you learn new constraints during implementation._

- (Add entries here as they're discovered)
