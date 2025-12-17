# Day 03 – QPS Forecasting with Prophet

## Goal
Build a short-term QPS forecast to support near-term capacity planning.

## What I Did
- Cleaned and reshaped raw Prometheus-style QPS data
- Trained a Prophet model with daily seasonality
- Forecasted QPS for the next several hours
- Visualized forecast with confidence intervals

## Key Observations
- The forecast successfully captures the diurnal traffic pattern:
  - Early-morning low (~1100–1200 QPS)
  - Morning ramp-up
  - Afternoon peak (~1850–1900 QPS)
  - Gradual decline in the evening
- The predicted curve closely follows historical observations,
  indicating the dominant signal is seasonality rather than noise.
- The uncertainty band (confidence interval) widens slightly
  around peak hours, reflecting higher variance under high load.

## Interpretation
- QPS is highly predictable in the short term when traffic follows
  stable daily patterns.
- Peak periods are the most capacity-sensitive windows, where
  small forecasting errors could translate into SLO risk.
- This forecast is suitable for **proactive capacity adjustment**
  (e.g., scaling ahead of known peaks), but not for detecting
  sudden, non-seasonal traffic spikes.

## Limitation
- The model assumes future traffic follows historical seasonality.
- It cannot anticipate unexpected events (e.g., incidents,
  promotions, or external traffic bursts).
- Forecast accuracy degrades beyond short horizons.

## Decision Implication
- Capacity planning should primarily align with predicted peak QPS.
- Additional safeguards (anomaly detection, alerting) are required
  to handle non-seasonal traffic changes.

## Next
Analyze residuals and apply anomaly detection (STL + EWMA) to
identify deviations from expected patterns.
