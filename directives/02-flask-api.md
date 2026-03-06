# Directive 02 — Flask API

## Objective
Build a production-quality REST API using Flask 3.x that serves cost data, resource inventory, and anomaly alerts. All boto3 calls must gracefully fall back to mock data if AWS credentials are absent.

---

## Inputs
- `.env` file (or environment variables) — see `spec.md` Section 12
- Mock JSON fixtures in `backend/tests/fixtures/`
- DynamoDB table: `cloudpulse-costs`

---

## Endpoints to Implement

| Method | Path | Module | Service |
|--------|------|--------|---------|
| GET | `/api/health` | `routes/health.py` | Direct (no service layer) |
| GET | `/api/costs` | `routes/costs.py` | `services/cost_service.py` |
| GET | `/api/resources` | `routes/resources.py` | `services/resource_service.py` |
| GET | `/api/anomalies` | `routes/anomalies.py` | `services/anomaly_service.py` |

---

## Architecture

### Application Factory (`app.py`)
```python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)
    register_blueprints(app)
    setup_logging(app)
    return app
```

### Mock Detection Logic (`services/mock_service.py`)
Auto-enable mock mode if:
1. `MOCK_MODE=true` in environment, OR
2. No `AWS_ACCESS_KEY_ID` set AND no EC2 instance metadata available AND no `AWS_PROFILE` set

### boto3 Fallback Pattern
Every service function must follow:
```python
def get_costs(days=30):
    if is_mock_mode():
        return load_mock("costs.json")
    try:
        return _fetch_from_aws(days)
    except (NoCredentialsError, ClientError) as e:
        logger.warning(f"AWS call failed, falling back to mock: {e}")
        return load_mock("costs.json")
```

---

## Execution Scripts to Call

### Snapshot costs to DynamoDB
```bash
python execution/snapshot_costs.py
```
Calls `services/cost_service.py` directly and writes results to DynamoDB.

### Seed local DynamoDB with mock data
```bash
python execution/seed_mock_data.py
```
Requires `AWS_ENDPOINT_URL=http://localhost:8000` (local DynamoDB via Docker).

---

## Input Validation Rules

| Endpoint | Param | Type | Min | Max | Default |
|----------|-------|------|-----|-----|---------|
| `/api/costs` | `days` | int | 1 | 90 | 30 |
| `/api/costs` | `mock` | bool | - | - | false |
| `/api/resources` | `mock` | bool | - | - | false |
| `/api/anomalies` | `days` | int | 1 | 30 | 7 |
| `/api/anomalies` | `threshold` | float | 0.01 | 5.0 | 0.20 |
| `/api/anomalies` | `mock` | bool | - | - | false |

Return `400 Bad Request` with JSON error body on invalid params:
```json
{ "error": "invalid_param", "message": "'days' must be an integer between 1 and 90", "param": "days" }
```

---

## HTTP Status Code Contract

| Scenario | Status |
|----------|--------|
| Success | 200 |
| Invalid query param | 400 |
| AWS auth failure | 503 (with fallback to mock) |
| Unexpected server error | 500 |
| DynamoDB unavailable | 503 |

---

## Structured Logging
Use Python `logging` with a JSON formatter. Every request must log:
```json
{
  "timestamp": "2024-03-05T12:00:00Z",
  "level": "INFO",
  "method": "GET",
  "path": "/api/costs",
  "params": { "days": 30 },
  "status_code": 200,
  "duration_ms": 245,
  "source": "live"
}
```

---

## Testing Requirements
- All routes tested with pytest
- boto3 calls mocked using `moto` library
- Test files in `backend/tests/`
- Coverage target: >80% on `routes/` and `services/`
- Run: `pytest backend/tests/ -v --cov=backend --cov-report=term-missing`

### Test scenarios per endpoint:
- Happy path (live mode, mock mode)
- Invalid param returns 400
- AWS credentials missing → falls back to mock, returns 200
- DynamoDB unavailable → returns 503

---

## Edge Cases and Known Constraints

- **Cost Explorer only available in `us-east-1`**: Always create CE client with `region_name='us-east-1'` even if app runs in another region.
- **Cost data lag**: CE data can be 24-48h behind. Document this in health endpoint response.
- **`GetCostAndUsage` pagination**: Response may be paginated if >100 days requested. Implement pagination loop in `cost_service.py`.
- **Flask CORS**: Enable CORS for development (frontend on port 5173, backend on 5000). Use `flask-cors` and restrict origins in production.
- **DynamoDB local for dev**: Use `AWS_ENDPOINT_URL=http://localhost:8000` to point boto3 at local DynamoDB Docker container. `seed_mock_data.py` handles table creation if it doesn't exist.
- **Lambda package size**: `snapshot_costs.py` and its dependencies must fit in 250MB Lambda deployment limit. Use Lambda layers for large deps if needed.

---

## Updates Log
_Update this section as you learn new constraints during implementation._

- (Add entries here as they're discovered)
