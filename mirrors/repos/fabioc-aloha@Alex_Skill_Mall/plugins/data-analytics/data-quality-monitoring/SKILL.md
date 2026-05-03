---
type: skill
lifecycle: stable
inheritance: inheritable
name: data-quality-monitoring
description: Data pipeline quality assurance — anomaly detection, schema drift, null ratio monitoring, freshness checks, and safe-write protection for reliable data engineering
tier: standard
applyTo: '**/*data*,**/*quality*,**/*monitoring*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Data Quality Monitoring


> Trust your data, or fix it before anyone else sees it.

## Quality Dimensions

| Dimension | Definition | Measurement |
|-----------|------------|-------------|
| **Completeness** | All expected data present | Row count, null ratio |
| **Consistency** | Data follows expected patterns | Schema match, value ranges |
| **Timeliness** | Data arrives on schedule | Freshness, latency |
| **Accuracy** | Data reflects reality | Comparison to source |
| **Uniqueness** | No unexpected duplicates | Distinct key ratio |

## Anomaly Detection

### Row Count Monitoring (Z-Score)

```python
def check_row_count(source: str, current_count: int,
                    expected: float, stddev: float,
                    threshold_pct: float = 0.25) -> dict:
    """Detect row count anomalies using rolling baseline."""
    z_score = abs(current_count - expected) / max(stddev, 1)
    deviation_pct = abs(current_count - expected) / max(expected, 1)

    return {
        "source": source,
        "current": current_count,
        "expected": round(expected),
        "deviation_pct": round(deviation_pct, 4),
        "z_score": round(z_score, 2),
        "is_anomaly": deviation_pct > threshold_pct,
        "severity": _severity(deviation_pct),
    }

def _severity(deviation: float) -> str:
    if deviation > 0.5: return "CRITICAL"
    if deviation > 0.25: return "HIGH"
    if deviation > 0.1: return "MEDIUM"
    return "LOW"
```

### Severity Actions

| Severity | Deviation | Action |
|----------|-----------|--------|
| CRITICAL | > 50% | **BLOCK** — Manual review required |
| HIGH | > 25% | **WARN** — Review before proceeding |
| MEDIUM | > 10% | **LOG** — Monitor trend |
| LOW | ≤ 10% | **PASS** — Within normal range |

### Schema Drift Detection

```python
def detect_schema_drift(actual_cols: dict, expected_cols: dict,
                        strict: bool = False) -> dict:
    """Compare actual vs expected schema."""
    missing = set(expected_cols) - set(actual_cols)
    added = set(actual_cols) - set(expected_cols)
    type_changes = {
        col: (expected_cols[col], actual_cols[col])
        for col in set(actual_cols) & set(expected_cols)
        if expected_cols[col] != actual_cols[col]
    }

    return {
        "has_drift": bool(missing or (strict and added) or type_changes),
        "missing_columns": list(missing),
        "added_columns": list(added),
        "type_changes": type_changes,
        "severity": "HIGH" if missing or type_changes else "LOW",
    }
```

### Null Ratio Monitoring

```python
def check_null_ratios(columns: dict, total_rows: int,
                      thresholds: dict = None) -> list:
    """Flag columns exceeding null thresholds."""
    default_threshold = 0.1
    thresholds = thresholds or {}
    issues = []

    for col, null_count in columns.items():
        ratio = null_count / max(total_rows, 1)
        threshold = thresholds.get(col, default_threshold)
        if ratio > threshold:
            issues.append({
                "column": col,
                "null_count": null_count,
                "null_ratio": round(ratio, 4),
                "threshold": threshold,
                "severity": "HIGH" if ratio > threshold * 2 else "MEDIUM",
            })

    return issues
```

### Freshness Check

```python
from datetime import datetime

def check_freshness(latest_timestamp: datetime,
                    max_age_hours: int = 24) -> dict:
    """Check data freshness against maximum allowed age."""
    age_hours = (datetime.now() - latest_timestamp).total_seconds() / 3600

    return {
        "fresh": age_hours <= max_age_hours,
        "latest_record": latest_timestamp.isoformat(),
        "age_hours": round(age_hours, 2),
        "max_age_hours": max_age_hours,
        "status": "FRESH" if age_hours <= max_age_hours else "STALE",
    }
```

## Data Protection Patterns

### Safe Write (Prevent Empty Overwrites)

```python
def safe_write(current_count: int, existing_count: int,
               min_rows: int = 100, max_drop_pct: float = 0.5) -> list:
    """Validate before overwriting production data."""
    failures = []

    if current_count == 0 and existing_count > 0:
        failures.append(f"NO_EMPTY_OVERWRITE: cannot replace {existing_count} rows with 0")

    if existing_count > 0 and current_count < existing_count * (1 - max_drop_pct):
        drop = (1 - current_count / existing_count) * 100
        failures.append(f"MAX_DROP: {drop:.1f}% exceeds {max_drop_pct * 100}% threshold")

    if current_count < min_rows:
        failures.append(f"MIN_ROWS: {current_count} below minimum {min_rows}")

    return failures  # Empty list = safe to write
```

### Protection Decision Matrix

| Scenario | Action |
|----------|--------|
| New data = 0 rows, existing > 0 | **BLOCK** — empty overwrite |
| Drop > 50% | **BLOCK** — dramatic data loss |
| Drop > 25% | **WARN** — review before proceeding |
| Below minimum row count | **BLOCK** — incomplete pipeline |
| All checks pass | **WRITE** |

## Quality Report

```python
def generate_quality_report(source: str, row_count: int,
                            checks: dict) -> dict:
    """Combine all checks into a single report."""
    report = {
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "row_count": row_count,
        "checks": checks,
        "overall_status": "PASS" if all(
            not c.get("is_anomaly") and c.get("severity", "LOW") != "HIGH"
            for c in checks.values() if isinstance(c, dict)
        ) else "FAIL",
    }
    return report
```

## Baseline Management

### Rolling Baseline Update

```python
def update_baseline(history: list, new_value: int,
                    window_size: int = 30) -> dict:
    """Update rolling baseline with new observation."""
    history = history[-window_size:] + [new_value]
    avg = sum(history) / len(history)
    variance = sum((x - avg) ** 2 for x in history) / len(history)

    return {
        "avg": round(avg, 2),
        "stddev": round(variance ** 0.5, 2),
        "samples": len(history),
        "last_value": new_value,
        "history": history,
    }
```

## Implementation Checklist

- [ ] Row count anomaly detection on every pipeline run
- [ ] Schema drift check against registered schema
- [ ] Null ratio thresholds per column documented
- [ ] Freshness alerts for time-sensitive data
- [ ] Safe-write guards on production tables
- [ ] Rolling baselines updated after successful runs
- [ ] Quality reports stored for trend analysis
- [ ] Alerting integrated (email, Slack, PagerDuty)
