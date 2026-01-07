import os
import pandas as pd
import numpy as np

# ===== 复用：按你上一版“整行字符串 CSV”方式读数据 =====
def load_metrics_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])

    raw_col = df.columns[0]  # e.g. 'timestamp,qps,cpu,p95_latency'
    df[["timestamp", "qps", "cpu", "p95_latency"]] = (
        df[raw_col].astype(str).str.strip().str.split(",", expand=True)
    )
    df = df.drop(columns=[raw_col])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["qps"] = df["qps"].astype(float)
    df["cpu"] = df["cpu"].astype(float)
    df["p95_latency"] = df["p95_latency"].astype(float)

    df = df.set_index("timestamp").sort_index()
    return df


def pct_change(a: float, b: float) -> float:
    """从 a 到 b 的百分比变化（避免除 0）"""
    if a == 0:
        return np.nan
    return (b - a) / a * 100.0


def risk_level(p95_latency: float, slo_ms: float) -> str:
    """
    简化 SLO 风险分级：
    - OK: < 80% SLO
    - WARN: 80%~100% SLO
    - BREACH: >= SLO
    """
    if p95_latency >= slo_ms:
        return "BREACH"
    if p95_latency >= 0.8 * slo_ms:
        return "WARN"
    return "OK"


def main():
    # ===== 你可以改的参数（本质就是“口径”）=====
    SLO_P95_MS = 400.0  # 例：p95 latency SLO 400ms（你可按真实服务改）
    LOOKBACK_HOURS = 24  # 本报告覆盖最近 24 小时（你数据是 1 天，刚好）

    # ===== 1) 读取数据 =====
    df = load_metrics_csv("data/raw/metrics.csv")

    # 最近窗口（如果数据不足 24h，会自动取全部）
    end_ts = df.index.max()
    start_ts = end_ts - pd.Timedelta(hours=LOOKBACK_HOURS)
    win = df[df.index >= start_ts].copy()

    # ===== 2) 计算关键摘要指标 =====
    qps_max = float(win["qps"].max())
    qps_avg = float(win["qps"].mean())
    cpu_max = float(win["cpu"].max())
    cpu_avg = float(win["cpu"].mean())
    p95_max = float(win["p95_latency"].max())
    p95_avg = float(win["p95_latency"].mean())

    # 峰值时刻（对决策最有用）
    peak_row = win.loc[win["qps"].idxmax()]
    peak_time = win["qps"].idxmax()
    peak_qps = float(peak_row["qps"])
    peak_cpu = float(peak_row["cpu"])
    peak_p95 = float(peak_row["p95_latency"])
    peak_risk = risk_level(peak_p95, SLO_P95_MS)

    # 风险统计
    win["risk"] = win["p95_latency"].apply(lambda x: risk_level(float(x), SLO_P95_MS))
    risk_counts = win["risk"].value_counts().to_dict()
    warn_hours = int(risk_counts.get("WARN", 0))
    breach_hours = int(risk_counts.get("BREACH", 0))

    # ===== 3) 读取 Day 4 异常清单（如果存在）=====
    anomalies_path = "data/processed/day04_anomalies_qps.csv"
    anomalies = None
    anomaly_count = 0
    if os.path.exists(anomalies_path):
        anomalies = pd.read_csv(anomalies_path, encoding="utf-8-sig")
        anomaly_count = len(anomalies)
    else:
        anomaly_count = 0

    # ===== 4) 生成决策建议（最小可解释规则）=====
    # 规则（你后面可逐步工程化）：
    # - 如果出现 BREACH：建议立刻扩容/排查
    # - 如果出现 WARN 且峰值接近 SLO：建议提前扩容（或检查限流/缓存/下游）
    # - 如果无 WARN/BREACH 且无异常：无需行动
    actions = []
    if breach_hours > 0:
        actions.append(f"- **Immediate action**: p95 latency breached SLO (≥ {SLO_P95_MS:.0f}ms) for {breach_hours} time points. Consider scaling up and incident triage.")
    elif warn_hours > 0:
        actions.append(f"- **Proactive action**: p95 latency entered WARN zone (≥ {0.8*SLO_P95_MS:.0f}ms) for {warn_hours} time points. Consider pre-scaling before peak hours.")
    else:
        actions.append("- **No action required**: latency stayed within OK zone for the entire window.")

    if anomaly_count > 0:
        actions.append(f"- **Traffic anomaly**: detected {anomaly_count} QPS residual anomalies (see anomalies table). Validate whether these correlate with latency risk.")
    else:
        actions.append("- **Traffic anomaly**: none detected in QPS residuals (seasonality-driven pattern).")

    # ===== 5) 输出 Markdown 报告 =====
    os.makedirs("reports/daily", exist_ok=True)
    report_path = "reports/daily/report_day05.md"

    # anomalies 预览表（最多 10 行）
    anomalies_md = ""
    if anomalies is not None and len(anomalies) > 0:
        preview = anomalies.head(10).copy()
        # 尽量保证 timestamp 字段存在（你 Day4 脚本里已输出 timestamp）
        cols = [c for c in ["timestamp", "value", "ewma", "upper", "lower", "score"] if c in preview.columns]
        anomalies_md = preview[cols].to_markdown(index=False)
    else:
        anomalies_md = "_No anomalies detected (table empty)._"

    md = f"""# Daily Service Health Report (Day 05)

**Window:** {start_ts} → {end_ts}  
**SLO (p95 latency):** {SLO_P95_MS:.0f} ms

## Executive Summary
- **Peak QPS:** {peak_qps:.0f} at {peak_time}
- **Peak CPU:** {peak_cpu:.2f}
- **Peak p95 latency:** {peak_p95:.0f} ms → **Risk: {peak_risk}**
- **Risk counts (time points):** OK={int(risk_counts.get("OK", 0))}, WARN={warn_hours}, BREACH={breach_hours}
- **QPS residual anomalies:** {anomaly_count}

## Key Metrics (last {LOOKBACK_HOURS}h)
- QPS: avg={qps_avg:.0f}, max={qps_max:.0f}
- CPU: avg={cpu_avg:.2f}, max={cpu_max:.2f}
- p95 latency: avg={p95_avg:.0f} ms, max={p95_max:.0f} ms

## Recommended Actions
{chr(10).join(actions)}

## Evidence
### QPS Residual Anomalies (Top 10)
{anomalies_md}

### Notes
- Anomaly detection is performed on **STL residuals** with **EWMA banding** (Day 04).
- “No anomalies” is treated as a positive signal when traffic is strongly seasonal.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"[OK] report generated: {report_path}")


if __name__ == "__main__":
    main()
