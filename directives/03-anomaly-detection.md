# Directive 03 — Anomaly Detection

## Objective
Implement a spike detection system that identifies AWS services with >20% day-over-day cost increases. The logic must be deterministic, unit-tested, and accessible both as a Flask API service and as a standalone execution script.

---

## Inputs
- Cost snapshot data from DynamoDB (or mock JSON in `backend/tests/fixtures/costs.json`)
- `threshold` parameter (default: 0.20 = 20%)
- `days` parameter — window to scan (default: 7)

---

## Algorithm

### Step 1: Fetch cost data
Pull daily cost per service for the requested window from DynamoDB (or mock).
Shape: `{ date: { service: cost } }` keyed by date string.

### Step 2: Compute day-over-day change
For each service, for each pair of consecutive days:
```
pct_change = (current_cost - previous_cost) / previous_cost
```

### Step 3: Filter and classify
- Skip if `previous_cost == 0` (new service, no baseline) — mark as `"new_service"` not anomaly
- Flag if `pct_change >= threshold`
- Classify severity:
  - `critical`: pct_change >= 1.0 (100%+)
  - `high`: 0.50 <= pct_change < 1.0
  - `medium`: threshold <= pct_change < 0.50

### Step 4: Rank by pct_change descending
Return list sorted by `pct_change` descending (biggest spikes first).

---

## Implementation Location

| File | Responsibility |
|------|---------------|
| `backend/services/anomaly_service.py` | Core detection logic |
| `backend/routes/anomalies.py` | Flask route, calls anomaly service |
| `execution/detect_anomalies.py` | Standalone script, prints JSON report |

### `anomaly_service.py` interface:
```python
def detect_anomalies(
    cost_data: list[dict],   # list of daily cost records
    threshold: float = 0.20,
    days: int = 7
) -> list[dict]:
    """
    Returns list of anomaly dicts, sorted by pct_change descending.
    Each dict: { service, date, previous_cost, current_cost, pct_change, severity, currency }
    """
```

---

## Execution Script
```bash
python execution/detect_anomalies.py [--days 7] [--threshold 0.20] [--mock]
```

Output: JSON report to stdout + summary table to stderr.

---

## Unit Test Requirements

Test file: `backend/tests/test_anomalies.py`

### Required test cases:
| Test | Scenario | Expected |
|------|----------|---------|
| `test_spike_detected` | Cost goes from $10 → $18.50 | Returns 1 anomaly, pct_change=85.0 |
| `test_below_threshold` | Cost goes from $10 → $11.50 | Returns 0 anomalies |
| `test_zero_previous_cost` | Previous cost = $0, current = $5 | Skip (no anomaly, can't compute %) |
| `test_new_service` | Service only exists for 1 day | Skip (no previous day to compare) |
| `test_critical_severity` | Cost goes from $10 → $25 | Severity = "critical" |
| `test_high_severity` | Cost goes from $10 → $17 | Severity = "high" |
| `test_medium_severity` | Cost goes from $10 → $13 | Severity = "medium" |
| `test_ranking_order` | Multiple anomalies | Sorted by pct_change descending |
| `test_custom_threshold` | threshold=0.50, 30% spike | Not flagged |
| `test_multiple_services` | 5 services, 2 spike | Returns exactly 2 anomalies |

---

## Edge Cases and Known Constraints

- **Zero previous cost**: Division by zero risk. Always guard: `if previous_cost == 0: continue`
- **Missing days in data**: If a service has no record for a day, treat as $0. But $0 → $X is not a spike (new service), not an anomaly.
- **Negative costs (AWS credits)**: AWS can issue credits that appear as negative costs. Skip negative previous_cost values.
- **Floating-point precision**: Round `pct_change` to 2 decimal places for display. Use `round(x, 2)`.
- **Same-day comparison**: Only compare consecutive calendar days, not arbitrary pairs.
- **Weekend data gaps**: Some AWS services may not report costs on weekends. Fill missing days with the last known value or $0.
- **Cost Explorer lag**: The "today" record may be incomplete. Consider only analyzing data through yesterday (T-1).

---

## Updates Log
_Update this section as you learn new constraints during implementation._

- (Add entries here as they're discovered)
