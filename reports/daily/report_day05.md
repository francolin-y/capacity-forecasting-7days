# Daily Service Health Report (Day 05)

**Window:** 2023-12-31 23:00:00 → 2024-01-01 23:00:00  
**SLO (p95 latency):** 400 ms

## Executive Summary
- **Peak QPS:** 1900 at 2024-01-01 17:00:00
- **Peak CPU:** 0.72
- **Peak p95 latency:** 410 ms → **Risk: BREACH**
- **Risk counts (time points):** OK=18, WARN=5, BREACH=1
- **QPS residual anomalies:** 0

## Key Metrics (last 24h)
- QPS: avg=1485, max=1900
- CPU: avg=0.54, max=0.72
- p95 latency: avg=263 ms, max=410 ms

## Recommended Actions
- **Immediate action**: p95 latency breached SLO (≥ 400ms) for 1 time points. Consider scaling up and incident triage.
- **Traffic anomaly**: none detected in QPS residuals (seasonality-driven pattern).

## Evidence
### QPS Residual Anomalies (Top 10)
_No anomalies detected (table empty)._

### Notes
- Anomaly detection is performed on **STL residuals** with **EWMA banding** (Day 04).
- “No anomalies” is treated as a positive signal when traffic is strongly seasonal.
