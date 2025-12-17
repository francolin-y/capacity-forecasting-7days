# Day 02 – Time Series Exploration

## Goal
Understand normal patterns in service metrics.

## What I Did
- Plotted QPS, CPU, and p95 latency time series
- Observed daily traffic pattern

## Key Findings
- QPS shows strong diurnal seasonality
- CPU usage closely follows QPS
- p95 latency increases non-linearly under high load

## Insight
Latency is the most SLO-sensitive metric; small increases in load
cause disproportionate latency degradation.

## Next
Build a short-term forecast on QPS.
