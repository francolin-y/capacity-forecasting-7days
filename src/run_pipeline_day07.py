"""
Day 07 Pipeline Orchestrator
Runs the full chain:
- Day 03: Forecast (Prophet)
- Day 04: Anomaly Detection (STL + EWMA)
- Day 05: SLO Report (Markdown)
- Day 06: Decision Engine (Rule-based)
"""

import subprocess
import sys

STEPS = [
    ("Forecast QPS (Day 03)", ["python", "src/forecast_day03.py"]),
    ("Detect Anomalies (Day 04)", ["python", "src/anomaly_day04.py"]),
    ("Generate SLO Report (Day 05)", ["python", "src/report_day05.py"]),
    ("Decision Engine (Day 06)", ["python", "src/decision_day06.py"]),
]

def run_step(name, cmd):
    print(f"\n=== {name} ===")
    try:
        subprocess.check_call(cmd)
        print(f"[OK] {name}")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {name}")
        sys.exit(e.returncode)

def main():
    for name, cmd in STEPS:
        run_step(name, cmd)
    print("\n[PIPELINE DONE] All steps completed successfully.")

if __name__ == "__main__":
    main()
