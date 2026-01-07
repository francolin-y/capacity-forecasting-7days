# Day 06 – Decision Engine for Capacity & SLO Risk

## Goal
Convert analytical signals into deterministic operational decisions.

## What I Did
- Defined a minimal decision space: SCALE_UP / INVESTIGATE / NO_OP
- Formalized decision rules combining:
  - SLO risk (WARN / BREACH)
  - Peak latency severity
  - Traffic anomaly presence
- Implemented a rule-based decision engine in code
- Validated decisions against Day 05 report results

## Key Insight
- SLO breaches do not require traffic anomalies to justify action.
- The absence of anomalies increases confidence that scaling is the correct response.
- Decision logic must be explicit to avoid inconsistent human judgment.

## Outcome
- Current dataset deterministically resolves to SCALE_UP
- Decision is reproducible and explainable

## Next
- Wire decision outputs to automation (cron/Airflow or ITSM)
- Add decision confidence scoring
