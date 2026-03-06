# Directive 05 — CI/CD Pipeline

## Objective
Set up GitHub Actions workflows that enforce code quality on every PR and automate deployment to AWS on push to main, with a manual approval gate before `terraform apply`.

---

## Inputs
- GitHub repository with Actions enabled
- GitHub Secrets (see table below)
- AWS IAM user with deploy permissions (separate from app role)

---

## Required GitHub Secrets

| Secret | Purpose |
|--------|---------|
| `AWS_ACCESS_KEY_ID` | Deploy IAM user key |
| `AWS_SECRET_ACCESS_KEY` | Deploy IAM user secret |
| `AWS_REGION` | Target region |
| `TF_STATE_BUCKET` | S3 remote state bucket name |

---

## Workflow 1: `pr-checks.yml`

**Trigger:** `pull_request` to any branch

**Execution order (fail fast):**

```
Step 1: Checkout (actions/checkout@v4)
Step 2: Setup Python 3.11 (actions/setup-python@v5)
Step 3: Restore pip cache (key: requirements-dev hash)
Step 4: pip install -r backend/requirements-dev.txt
Step 5: flake8 backend/ execution/ --max-line-length=100 --exclude=__pycache__
Step 6: pytest backend/tests/ -v --tb=short --cov=backend
Step 7: Setup Node 20 (actions/setup-node@v4 with cache: npm)
Step 8: npm ci (in frontend/)
Step 9: npm run lint (ESLint — must exit 0)
Step 10: npm test -- --watchAll=false --passWithNoTests
```

**Gate:** All 10 steps must pass. If flake8 fails, steps 6–10 do not run.

---

## Workflow 2: `deploy.yml`

**Trigger:**
- `push` to `main` branch
- `workflow_dispatch` (manual trigger with optional inputs)

**Execution order:**

```
Step 1:  Checkout
Step 2a: Setup Python 3.11           } parallel
Step 2b: Setup Node 20               }
Step 3:  pip install -r backend/requirements.txt
Step 4:  npm ci (in frontend/)
Step 5:  npm run build (outputs to frontend/dist/)
Step 6:  Setup Terraform 1.7 (hashicorp/setup-terraform@v3)
Step 7:  terraform init (with S3 backend env vars)
Step 8:  terraform validate
Step 9:  terraform plan -out=tfplan -no-color (save plan artifact)
Step 10: Upload plan as workflow artifact (30-day retention)
Step 11: [GATE] Environment: production (requires manual approval in GitHub)
Step 12: terraform apply tfplan
Step 13: Package Lambda (zip execution/snapshot_costs.py + deps)
Step 14: Upload Lambda zip to S3
Step 15: aws lambda update-function-code (update poller Lambda)
Step 16: Post deployment summary as workflow run summary
```

**Manual approval gate (Step 11):**
- Uses GitHub Environment named `production`
- Environment must have required reviewers configured in repo settings
- Plan artifact is available for review before approval

---

## Caching Strategy

### pip cache
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ hashFiles('backend/requirements-dev.txt') }}
    restore-keys: pip-
```

### npm cache
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json
```

### Terraform plugin cache
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.terraform.d/plugin-cache
    key: terraform-${{ hashFiles('infra/.terraform.lock.hcl') }}
```

---

## Execution Scripts to Call

### Validate Terraform before plan
```bash
python execution/validate_terraform.py --check-state-bucket
```
If state bucket doesn't exist, fail with instructions.

---

## flake8 Configuration (`.flake8` in project root)
```ini
[flake8]
max-line-length = 100
exclude = .tmp, __pycache__, .venv, node_modules
ignore = E203, W503
per-file-ignores =
    backend/tests/*: S101
```

---

## ESLint Configuration (`frontend/.eslintrc.json`)
```json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended", "plugin:react-hooks/recommended"],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

---

## Edge Cases and Known Constraints

- **Terraform state lock**: If a previous apply crashed, the state may be locked. Unlock with `terraform force-unlock <lock-id>`. Never do this automatically in CI.
- **Lambda zip size**: If `snapshot_costs.py` dependencies exceed 50MB (direct upload limit), use S3. The deploy workflow always uses S3.
- **Concurrent workflow runs**: If two PRs merge simultaneously, Terraform state lock prevents corruption. The second apply will wait or fail gracefully.
- **AWS credentials in CI**: Never commit secrets. Use GitHub Secrets. The deploy IAM user needs: `lambda:UpdateFunctionCode`, `s3:PutObject`, and Terraform permissions.
- **`terraform plan` in PRs**: Do not auto-apply on PR. Only plan. Apply only on push to main after approval.
- **Node modules caching**: `actions/setup-node` with `cache: npm` handles this automatically when `cache-dependency-path` points to `package-lock.json`.
- **Branch protection**: Recommend requiring `pr-checks` status check to pass before merge. Configure in repo settings → Branches → Branch protection rules.

---

## Updates Log
_Update this section as you learn new constraints during implementation._

- (Add entries here as they're discovered)
