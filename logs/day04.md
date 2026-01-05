# Day 04 – Anomaly Detection with STL + EWMA (QPS)

## Goal
Detect non-seasonal anomalies in QPS by separating expected patterns
(trend and seasonality) from irregular deviations.

## What I Did
- Loaded and cleaned Prometheus-style QPS data
- Applied STL decomposition with period=24 to separate:
  - Trend
  - Daily seasonality
  - Residual (irregular component)
- Used the STL residual as the anomaly carrier signal
- Applied EWMA-based banding (alpha=0.3, z=3.0) on residuals
- Exported detected anomalies to CSV

## Observations
- STL decomposition cleanly explains almost all QPS variation:
  - Trend remains nearly flat over the day
  - Seasonality dominates the signal with a strong diurnal pattern
- The residual component is extremely small (near numerical precision),
  indicating minimal unexplained behavior after removing trend and seasonality.
- EWMA control bands tightly track the residual signal.
- No residual values exceed the EWMA upper or lower bounds.

## Result
- No anomalies were detected in the QPS residuals.
- The anomaly output table is empty, which is an expected and valid result
  given the highly regular and seasonality-driven traffic pattern.

## Interpretation
- The absence of detected anomalies indicates that observed QPS behavior
  fully conforms to historical expectations.
- This is treated as a positive operational signal:
  no unexpected traffic spikes or drops are present.
- Under this condition, no immediate SRE intervention or capacity adjustment
  is required.

## Limitations
- With limited historical data, residual variance estimates may be unstable
  at the beginning of the series.
- QPS is often less sensitive to anomalies than latency metrics in real systems.
- This method detects deviations from expected patterns, not all possible failures.

## Next
- Apply the same anomaly detection pipeline to p95 latency,
  which is more directly correlated with SLO violations.
- Link detected anomalies (if any) to SLO risk and reporting logic.
