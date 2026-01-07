# Day 05 – SLO Risk Summary & Automated Daily Report

## Goal
Turn forecasting/anomaly outputs into an operationally actionable daily report.

## What I Did
- Loaded QPS/CPU/p95 latency metrics for the last 24h window
- Derived SLO risk levels from p95 latency (OK/WARN/BREACH)
- Pulled Day04 QPS residual anomaly results (if available)
- Generated a Markdown daily report with executive summary and recommended actions

## Key Findings
- Peak traffic window and peak p95 latency were identified and labeled with risk level
- Current dataset shows strong seasonality; QPS residual anomalies are empty (expected)
- SLO risk rules provide clear operational guidance even without anomalies

## Next
- Add plots to the report (trend + risk timeline)
- Orchestrate the pipeline (cron/Airflow) to run daily without manual steps
