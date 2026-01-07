# Capacity Forecasting & SLO Decision Pipeline (7-Day Build)

A minimal, end-to-end pipeline that turns service metrics into
**forecasting, anomaly detection, SLO risk assessment, and deterministic actions**.

## Problem
Static thresholds and manual analysis lead to:
- Over-provisioning
- Late reaction to peak traffic
- Inconsistent operational decisions

## What This Project Delivers
- **Forecasting:** Short-term QPS forecasting with Prophet
- **Anomaly Detection:** STL decomposition + EWMA on residuals
- **SLO Risk:** p95 latency risk classification (OK/WARN/BREACH)
- **Decision Engine:** Rule-based actions (SCALE_UP / INVESTIGATE / NO_OP)
- **Automation:** One-command pipeline execution

## Architecture
Metrics (Prometheus-style CSV)
→ Forecast (Day 03)
→ Anomaly Detection (Day 04)
→ SLO Report (Day 05)
→ Decision Engine (Day 06)

## How to Run
```bash
pip install pandas matplotlib prophet statsmodels
python src/run_pipeline_day07.py
