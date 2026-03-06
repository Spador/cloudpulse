# CloudPulse — Specification Document
> Single source of truth for the entire build. Update as decisions change.

---

## 1. Project Overview and Goals

CloudPulse is a production-grade, self-hosted AWS cost and resource monitoring dashboard. It solves the pain point of AWS cost observability without paying for commercial tools like CloudHealth or Spot.io.

**Goals:**
- Give engineers a real-time view of AWS spend broken down by service
- Surface cost anomalies (>20% day-over-day spikes) as actionable alerts
- Provide a resource inventory (EC2, S3, Lambda) at a glance
- Be fully deployable from a fresh clone in under 30 minutes
- Work in "mock mode" without any AWS credentials (for demos and reviewers)
- Serve as a portfolio-quality DevOps/SRE reference project

**Non-Goals:**
- Multi-account AWS organizations support (v1 scope: single account)
- Cost allocation tags editor
- Automated cost remediation / right-sizing

---

## 2. Tech Stack (Version Pins)

| Layer | Technology | Version |
|-------|-----------|---------|
| Python runtime | CPython | 3.11 |
| Backend framework | Flask | 3.x |
| AWS SDK | boto3 | 1.34+ |
| Frontend framework | React | 18.x |
| Frontend language | TypeScript | 5.x |
| Charting | Recharts | 2.x |
| CSS framework | Tailwind CSS | 3.x |
| Build tool | Vite | 5.x |
| IaC | Terraform | 1.7+ |
| AWS provider | hashicorp/aws | ~> 5.0 |
| CI/CD | GitHub Actions | - |
| Database | AWS DynamoDB | - |
| Linter (Python) | flake8 | 7.x |
| Linter (JS/TS) | ESLint | 8.x |
| Test (Python) | pytest | 8.x |
| Test (JS/TS) | Jest + React Testing Library | 29.x / 14.x |
| Formatter (Python) | black | 24.x |
| Node.js | Node.js | 20 LTS |
| Package manager (JS) | npm | 10.x |

---

## 3. Full Folder / File Structure

```
cloudpulse/                         # project root
├── spec.md                         # THIS FILE — single source of truth
├── brand-guidelines.md             # Color palette and typography
├── README.md                       # Setup guide, architecture diagram, screenshots
├── .env.example                    # All environment variables documented
├── .gitignore
│
├── directives/
│   ├── 01-terraform-infra.md       # SOP: provision AWS infra
│   ├── 02-flask-api.md             # SOP: backend API + boto3
│   ├── 03-anomaly-detection.md     # SOP: spike detection logic
│   ├── 04-react-dashboard.md       # SOP: frontend build
│   ├── 05-cicd-pipeline.md         # SOP: GitHub Actions
│   └── 06-readme-docs.md           # SOP: documentation
│
├── execution/
│   ├── snapshot_costs.py           # Polls Cost Explorer → DynamoDB
│   ├── detect_anomalies.py         # Runs spike detection logic
│   ├── seed_mock_data.py           # Seeds local DynamoDB with mock data
│   └── validate_terraform.py       # Runs terraform validate + plan
│
├── backend/
│   ├── app.py                      # Flask application factory
│   ├── config.py                   # Config class, reads from env
│   ├── requirements.txt
│   ├── requirements-dev.txt        # pytest, flake8, black, moto
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── costs.py                # GET /api/costs
│   │   ├── resources.py            # GET /api/resources
│   │   ├── anomalies.py            # GET /api/anomalies
│   │   └── health.py               # GET /api/health
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cost_service.py         # boto3 Cost Explorer calls
│   │   ├── resource_service.py     # boto3 EC2/S3/Lambda calls
│   │   ├── anomaly_service.py      # spike detection logic
│   │   ├── dynamo_service.py       # DynamoDB read/write
│   │   └── mock_service.py         # Returns mock JSON when no creds
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # pytest fixtures, moto setup
│       ├── test_costs.py
│       ├── test_resources.py
│       ├── test_anomalies.py
│       └── test_health.py
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── .eslintrc.json
│   ├── jest.config.ts
│   ├── public/
│   │   └── favicon.ico
│   └── src/
│       ├── main.tsx                # Entry point
│       ├── App.tsx                 # Root component, routing
│       ├── index.css               # Tailwind directives
│       ├── vite-env.d.ts
│       ├── api/
│       │   ├── client.ts           # axios/fetch wrapper, base URL config
│       │   ├── costs.ts            # /api/costs calls
│       │   ├── resources.ts        # /api/resources calls
│       │   ├── anomalies.ts        # /api/anomalies calls
│       │   └── health.ts           # /api/health calls
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Header.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── Layout.tsx
│       │   ├── charts/
│       │   │   ├── DailyCostBarChart.tsx
│       │   │   └── CostTrendLineChart.tsx
│       │   ├── tables/
│       │   │   └── ResourceInventoryTable.tsx
│       │   ├── panels/
│       │   │   └── AnomalyAlertPanel.tsx
│       │   ├── controls/
│       │   │   ├── DateRangePicker.tsx
│       │   │   └── MockToggle.tsx
│       │   └── ui/
│       │       ├── SkeletonLoader.tsx
│       │       ├── EmptyState.tsx
│       │       ├── Badge.tsx
│       │       └── StatusIndicator.tsx
│       ├── hooks/
│       │   ├── useCosts.ts
│       │   ├── useResources.ts
│       │   ├── useAnomalies.ts
│       │   └── useMockMode.ts
│       ├── mock/
│       │   ├── costs.json
│       │   ├── resources.json
│       │   └── anomalies.json
│       ├── types/
│       │   └── index.ts            # All TypeScript interfaces
│       ├── utils/
│       │   └── formatters.ts       # Currency, date, percent formatters
│       └── __tests__/
│           ├── DailyCostBarChart.test.tsx
│           ├── AnomalyAlertPanel.test.tsx
│           └── ResourceInventoryTable.test.tsx
│
├── infra/
│   ├── main.tf                     # Root module: calls child modules
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf                 # terraform + provider version pins
│   ├── backend.tf                  # S3 remote state config
│   ├── terraform.tfvars.example
│   └── modules/
│       ├── compute/
│       │   ├── main.tf             # Lambda function + CloudWatch Event rule
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── storage/
│       │   ├── main.tf             # DynamoDB table + S3 state bucket
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── iam/
│           ├── main.tf             # IAM role + least-privilege policy
│           ├── variables.tf
│           └── outputs.tf
│
├── .github/
│   └── workflows/
│       ├── pr-checks.yml           # lint + test on every PR
│       └── deploy.yml              # build + terraform plan/apply on main
│
└── .tmp/                           # Ignored — intermediate files only
```

---

## 4. API Endpoints

### `GET /api/costs`
Returns daily and monthly cost breakdown by AWS service.

**Query params:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `days` | integer | No | 30 | Number of days to look back (7, 30, 90) |
| `mock` | boolean | No | false | Return mock data instead of live AWS |

**Response shape:**
```json
{
  "period": {
    "start": "2024-02-04",
    "end": "2024-03-05"
  },
  "daily": [
    {
      "date": "2024-02-04",
      "services": [
        { "service": "Amazon EC2", "cost": 12.34, "currency": "USD" },
        { "service": "Amazon S3", "cost": 1.02, "currency": "USD" }
      ],
      "total": 13.36
    }
  ],
  "monthly_summary": [
    { "service": "Amazon EC2", "total_cost": 320.45, "currency": "USD" },
    { "service": "Amazon S3", "total_cost": 28.10, "currency": "USD" }
  ],
  "grand_total": 348.55,
  "currency": "USD",
  "source": "live"
}
```

---

### `GET /api/resources`
Returns EC2 instance counts/states, S3 bucket count, Lambda function count.

**Query params:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `mock` | boolean | No | false | Return mock data |

**Response shape:**
```json
{
  "ec2": {
    "total": 12,
    "by_state": {
      "running": 8,
      "stopped": 3,
      "terminated": 1
    },
    "instances": [
      {
        "id": "i-0abc123",
        "type": "t3.medium",
        "state": "running",
        "region": "us-east-1",
        "name": "web-server-01"
      }
    ]
  },
  "s3": {
    "total_buckets": 7,
    "buckets": [
      { "name": "my-app-assets", "region": "us-east-1", "creation_date": "2023-01-15" }
    ]
  },
  "lambda": {
    "total_functions": 23,
    "functions": [
      { "name": "cloudpulse-poller", "runtime": "python3.11", "region": "us-east-1", "last_modified": "2024-03-01" }
    ]
  },
  "source": "live",
  "fetched_at": "2024-03-05T12:00:00Z"
}
```

---

### `GET /api/anomalies`
Returns services with >20% day-over-day spend increase, ranked by spike magnitude.

**Query params:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `threshold` | float | No | 0.20 | Minimum fractional increase to flag (0.20 = 20%) |
| `days` | integer | No | 7 | Window of days to scan |
| `mock` | boolean | No | false | Return mock data |

**Response shape:**
```json
{
  "anomalies": [
    {
      "service": "Amazon EC2",
      "date": "2024-03-04",
      "previous_cost": 10.00,
      "current_cost": 18.50,
      "pct_change": 85.0,
      "severity": "critical",
      "currency": "USD"
    }
  ],
  "threshold_used": 0.20,
  "period_scanned": { "start": "2024-02-27", "end": "2024-03-05" },
  "total_anomalies": 1,
  "source": "live"
}
```

Severity levels: `critical` (>100%), `high` (50–100%), `medium` (20–50%).

---

### `GET /api/health`
Returns app version, uptime, and AWS connectivity status.

**Response shape:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "aws": {
    "connected": true,
    "region": "us-east-1",
    "account_id": "123456789012"
  },
  "dynamodb": {
    "connected": true,
    "table": "cloudpulse-costs"
  },
  "timestamp": "2024-03-05T12:00:00Z"
}
```

---

## 5. DynamoDB Table Schema

**Table name:** `cloudpulse-costs`

| Attribute | Type | Role | Notes |
|-----------|------|------|-------|
| `pk` | String | Partition key | `SERVICE#<service_name>` e.g. `SERVICE#Amazon EC2` |
| `sk` | String | Sort key | `DATE#<YYYY-MM-DD>` e.g. `DATE#2024-03-05` |
| `service` | String | Attribute | Human-readable service name |
| `date` | String | Attribute | ISO date string |
| `cost` | Number | Attribute | Daily cost in USD |
| `currency` | String | Attribute | Always `"USD"` |
| `source` | String | Attribute | `"cost_explorer"` or `"mock"` |
| `ttl` | Number | TTL attribute | Unix epoch; items expire after 90 days |
| `snapshot_at` | String | Attribute | ISO 8601 timestamp of when row was written |

**GSI: `DateIndex`**
- Partition key: `date`
- Sort key: `cost` (Number, for range queries sorted by cost)
- Use case: "give me all services for a given date, sorted by cost"

**Capacity:** On-demand (PAY_PER_REQUEST) — no provisioned throughput needed at this scale.

**TTL:** Enabled on `ttl` attribute. Items older than 90 days auto-expire.

---

## 6. IAM Role and Policy Spec

**Role name:** `cloudpulse-app-role`

**Trust policy:** EC2 instances and Lambda functions can assume this role (for deployed use). For local dev, use AWS credentials from environment.

**Allowed actions (nothing more):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CostExplorerReadOnly",
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ce:GetDimensionValues"
      ],
      "Resource": "*"
    },
    {
      "Sid": "EC2ReadOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3ListOnly",
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation"
      ],
      "Resource": "*"
    },
    {
      "Sid": "LambdaReadOnly",
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DynamoDBReadWrite",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/cloudpulse-costs*"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/cloudpulse/*"
    }
  ]
}
```

---

## 7. Terraform Module Breakdown

### `/modules/iam`
**Owns:** IAM role (`cloudpulse-app-role`), IAM policy, role-policy attachment, Lambda execution role.
**Inputs:** `app_name`, `aws_account_id`, `dynamodb_table_arn`
**Outputs:** `role_arn`, `role_name`, `policy_arn`

### `/modules/storage`
**Owns:** DynamoDB table (`cloudpulse-costs`) with TTL and GSI, S3 bucket for Terraform remote state (created separately/bootstrapped), S3 bucket for Lambda deployment package.
**Inputs:** `app_name`, `environment`, `dynamodb_ttl_days`
**Outputs:** `dynamodb_table_name`, `dynamodb_table_arn`, `state_bucket_name`, `lambda_bucket_name`

### `/modules/compute`
**Owns:** Lambda function (Python 3.11, runs `snapshot_costs.py`), CloudWatch Events rule (cron every 60 min), CloudWatch log group with 30-day retention.
**Inputs:** `app_name`, `environment`, `lambda_role_arn`, `lambda_bucket`, `lambda_zip_key`, `dynamodb_table_name`
**Outputs:** `lambda_arn`, `lambda_function_name`, `cloudwatch_rule_arn`, `log_group_name`

---

## 8. React Component Tree

```
App
├── Layout
│   ├── Header (app title, mock toggle, AWS connection badge)
│   └── Sidebar (navigation links)
└── Dashboard (main page)
    ├── DateRangePicker (7d / 30d / 90d selector)
    ├── MockToggle (live vs mock data switch)
    ├── DailyCostBarChart
    │   └── SkeletonLoader (loading state)
    ├── CostTrendLineChart
    │   └── SkeletonLoader (loading state)
    ├── ResourceInventoryTable
    │   ├── StatusIndicator (per EC2 instance state)
    │   └── EmptyState (no resources)
    └── AnomalyAlertPanel
        ├── Badge (severity: critical/high/medium)
        └── EmptyState (no anomalies — good news state)
```

**Data flow per component:**

| Component | Hook | API endpoint |
|-----------|------|-------------|
| `DailyCostBarChart` | `useCosts(days, mock)` | `GET /api/costs?days=N` |
| `CostTrendLineChart` | `useCosts(days, mock)` | `GET /api/costs?days=7` |
| `ResourceInventoryTable` | `useResources(mock)` | `GET /api/resources` |
| `AnomalyAlertPanel` | `useAnomalies(days, mock)` | `GET /api/anomalies` |
| `Header` | `useHealthCheck()` | `GET /api/health` |

---

## 9. CI/CD Pipeline Stages

### Workflow: `pr-checks.yml` (triggers on: `pull_request`)
1. **Checkout** — actions/checkout@v4
2. **Setup Python 3.11** — actions/setup-python@v5
3. **Cache pip** — actions/cache@v4 (key: requirements hash)
4. **Install Python deps** — `pip install -r backend/requirements-dev.txt`
5. **Lint Python** — `flake8 backend/ execution/ --max-line-length=100`
6. **Run pytest** — `pytest backend/tests/ -v --tb=short` (boto3 mocked via moto)
7. **Setup Node 20** — actions/setup-node@v4
8. **Cache npm** — actions/cache@v4 (key: package-lock hash)
9. **Install JS deps** — `npm ci` in `frontend/`
10. **Lint TypeScript** — `npm run lint` in `frontend/`
11. **Run Jest** — `npm test -- --watchAll=false` in `frontend/`
12. **Gate:** All steps must pass. Fail fast: lint before tests.

### Workflow: `deploy.yml` (triggers on: `push to main` + `workflow_dispatch`)
1. **Checkout**
2. **Setup Python + Node** (parallel)
3. **Build React app** — `npm run build` → `frontend/dist/`
4. **Setup Terraform 1.7+** — hashicorp/setup-terraform@v3
5. **Terraform init** — `terraform init` (reads S3 backend)
6. **Terraform validate** — `terraform validate`
7. **Terraform plan** — `terraform plan -out=tfplan` (posts plan summary as PR comment)
8. **Manual approval gate** — `workflow_dispatch` input or environment protection rule
9. **Terraform apply** — `terraform apply tfplan` (only after approval)
10. **Deploy Lambda** — upload zip to S3, update Lambda function code
11. **Notify** — post deployment summary to PR/Slack (optional)

---

## 10. Milestone Checklist

- [ ] **Milestone 1: Terraform Infrastructure**
  - [ ] Bootstrap S3 backend bucket (manual, one-time)
  - [ ] `/modules/iam`: role + least-privilege policy
  - [ ] `/modules/storage`: DynamoDB table + TTL + GSI
  - [ ] `/modules/compute`: Lambda + CloudWatch Events + log group
  - [ ] Root `main.tf` wires modules together
  - [ ] `terraform validate` passes
  - [ ] `terraform plan` produces expected resource count
  - [ ] `terraform.tfvars.example` documents all vars

- [ ] **Milestone 2: Flask API**
  - [ ] Flask app factory in `app.py`
  - [ ] `GET /api/health` working
  - [ ] `GET /api/costs` with boto3 + mock fallback
  - [ ] `GET /api/resources` with boto3 + mock fallback
  - [ ] `GET /api/anomalies` wired to anomaly service
  - [ ] DynamoDB read/write in `dynamo_service.py`
  - [ ] Structured JSON logging on all routes
  - [ ] Input validation on all query params
  - [ ] All routes return correct HTTP status codes on errors
  - [ ] `execution/snapshot_costs.py` runs end-to-end
  - [ ] `execution/seed_mock_data.py` seeds local DynamoDB

- [ ] **Milestone 3: Anomaly Detection**
  - [ ] Spike detection: day-over-day % change calculation
  - [ ] Severity classification (critical/high/medium)
  - [ ] `execution/detect_anomalies.py` runs standalone
  - [ ] pytest unit tests for anomaly logic (edge cases: zero previous cost, new service)
  - [ ] Tests pass with mocked data

- [ ] **Milestone 4: React Dashboard**
  - [ ] Vite + React + TypeScript + Tailwind project bootstrapped
  - [ ] All TypeScript types defined in `types/index.ts`
  - [ ] Mock JSON files match API response shapes
  - [ ] `MockToggle` switches data source
  - [ ] `DateRangePicker` filters cost views
  - [ ] `DailyCostBarChart` renders with Recharts
  - [ ] `CostTrendLineChart` renders with Recharts
  - [ ] `ResourceInventoryTable` with status indicators
  - [ ] `AnomalyAlertPanel` with severity badges
  - [ ] Loading skeletons on all panels
  - [ ] Empty states on all panels
  - [ ] Jest tests for all components
  - [ ] ESLint passes

- [ ] **Milestone 5: GitHub Actions CI/CD**
  - [ ] `pr-checks.yml`: lint + test on PR
  - [ ] `deploy.yml`: build + plan + apply on main
  - [ ] pip and npm caching working
  - [ ] Manual approval gate configured
  - [ ] `execution/validate_terraform.py` integrated

- [ ] **Milestone 6: README and Docs**
  - [ ] Mermaid architecture diagram
  - [ ] Prerequisites section
  - [ ] Step-by-step setup guide
  - [ ] Mock mode instructions
  - [ ] Screenshots section (with placeholder labels)
  - [ ] Cost estimate section
  - [ ] All six directive files updated with lessons learned

---

## 11. Mock Data Contract

Mock data must mirror real boto3/API Gateway response shapes exactly. Stored in `frontend/src/mock/` (frontend) and `backend/tests/fixtures/` (pytest).

### `costs.json` (mirrors `GET /api/costs` response)
```json
{
  "period": { "start": "2024-02-04", "end": "2024-03-05" },
  "daily": [
    {
      "date": "2024-02-04",
      "services": [
        { "service": "Amazon EC2", "cost": 12.34, "currency": "USD" },
        { "service": "Amazon S3", "cost": 1.02, "currency": "USD" },
        { "service": "AWS Lambda", "cost": 0.12, "currency": "USD" },
        { "service": "Amazon RDS", "cost": 8.50, "currency": "USD" },
        { "service": "Amazon CloudFront", "cost": 0.45, "currency": "USD" }
      ],
      "total": 22.43
    }
  ],
  "monthly_summary": [
    { "service": "Amazon EC2", "total_cost": 320.45, "currency": "USD" },
    { "service": "Amazon S3", "total_cost": 28.10, "currency": "USD" },
    { "service": "AWS Lambda", "total_cost": 3.60, "currency": "USD" },
    { "service": "Amazon RDS", "total_cost": 255.00, "currency": "USD" },
    { "service": "Amazon CloudFront", "total_cost": 13.50, "currency": "USD" }
  ],
  "grand_total": 620.65,
  "currency": "USD",
  "source": "mock"
}
```

### `resources.json` (mirrors `GET /api/resources` response)
```json
{
  "ec2": {
    "total": 5,
    "by_state": { "running": 3, "stopped": 2, "terminated": 0 },
    "instances": [
      { "id": "i-0abc123def456", "type": "t3.medium", "state": "running", "region": "us-east-1", "name": "web-01" },
      { "id": "i-0def456abc789", "type": "t3.large", "state": "running", "region": "us-east-1", "name": "api-01" },
      { "id": "i-0ghi789jkl012", "type": "t2.micro", "state": "stopped", "region": "us-west-2", "name": "dev-bastion" }
    ]
  },
  "s3": {
    "total_buckets": 4,
    "buckets": [
      { "name": "my-app-assets-prod", "region": "us-east-1", "creation_date": "2023-06-01" },
      { "name": "cloudpulse-tf-state", "region": "us-east-1", "creation_date": "2024-01-10" }
    ]
  },
  "lambda": {
    "total_functions": 8,
    "functions": [
      { "name": "cloudpulse-poller", "runtime": "python3.11", "region": "us-east-1", "last_modified": "2024-03-01" },
      { "name": "image-resizer", "runtime": "nodejs20.x", "region": "us-east-1", "last_modified": "2024-02-15" }
    ]
  },
  "source": "mock",
  "fetched_at": "2024-03-05T12:00:00Z"
}
```

### `anomalies.json` (mirrors `GET /api/anomalies` response)
```json
{
  "anomalies": [
    { "service": "Amazon EC2", "date": "2024-03-04", "previous_cost": 10.00, "current_cost": 23.00, "pct_change": 130.0, "severity": "critical", "currency": "USD" },
    { "service": "Amazon RDS", "date": "2024-03-03", "previous_cost": 8.00, "current_cost": 13.20, "pct_change": 65.0, "severity": "high", "currency": "USD" },
    { "service": "Amazon S3", "date": "2024-03-02", "previous_cost": 1.00, "current_cost": 1.30, "pct_change": 30.0, "severity": "medium", "currency": "USD" }
  ],
  "threshold_used": 0.20,
  "period_scanned": { "start": "2024-02-27", "end": "2024-03-05" },
  "total_anomalies": 3,
  "source": "mock"
}
```

---

## 12. Environment Variables

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `AWS_REGION` | AWS region for all boto3 calls | Yes (or falls back to mock) | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | No (uses IAM role if deployed) | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | No (uses IAM role if deployed) | `wJalr...` |
| `DYNAMODB_TABLE_NAME` | DynamoDB table for cost snapshots | Yes | `cloudpulse-costs` |
| `FLASK_ENV` | Flask environment | No | `development` |
| `FLASK_SECRET_KEY` | Flask session secret | Yes | `change-me-in-prod` |
| `MOCK_MODE` | Force mock data regardless of creds | No | `true` |
| `LOG_LEVEL` | Python log level | No | `INFO` |
| `COST_SNAPSHOT_DAYS` | How many days back to snapshot | No | `90` |
| `ANOMALY_THRESHOLD` | Fractional spike threshold | No | `0.20` |
| `VITE_API_BASE_URL` | Frontend API base URL | No | `http://localhost:5000` |
| `TF_STATE_BUCKET` | S3 bucket for Terraform state | Yes (Terraform) | `cloudpulse-tf-state-abc123` |
| `TF_STATE_KEY` | S3 key for Terraform state | No | `cloudpulse/terraform.tfstate` |
| `TF_STATE_REGION` | Region for S3 state bucket | Yes (Terraform) | `us-east-1` |

---

## 13. Known Constraints and Decisions

### Why DynamoDB over RDS?
- Zero operational overhead (no instance to manage, patch, or right-size)
- Pay-per-request fits bursty polling workload
- TTL is a first-class feature — no cron jobs to purge old data
- Sufficient for time-series cost snapshots; no relational joins needed

### Why Flask over FastAPI?
- Simpler mental model for a portfolio project
- Broader familiarity in DevOps/SRE community
- Lower dependency footprint
- FastAPI is the right choice if async IO or OpenAPI generation becomes critical

### Why Vite over Create React App?
- CRA is deprecated; Vite is the community standard
- Dramatically faster HMR and build times
- Better TypeScript support out of the box

### Why Recharts over D3?
- React-native integration (no imperative DOM manipulation)
- Sufficient for bar and line charts
- Much smaller learning curve for contributors

### AWS Cost Explorer API constraints:
- Minimum granularity: DAILY
- Data available from ~48 hours ago (not real-time)
- Rate limit: 10 requests/second per account
- Each GetCostAndUsage call costs $0.01 (budget: ~$3/month at hourly polling)

### Terraform remote state bootstrap:
- S3 backend bucket must be created before `terraform init`
- `execution/validate_terraform.py` handles this check and prints instructions if bucket missing

### Mock mode auto-detection:
- If `AWS_ACCESS_KEY_ID` or `AWS_PROFILE` is not set AND no IAM role metadata is available, Flask backend auto-enables mock mode
- Frontend has an explicit toggle; state persisted in localStorage

### Cost Explorer billing data lag:
- Up to 24 hours for data to appear
- `snapshot_costs.py` fetches last 3 days on each run to catch delayed records
