# src/anomaly_day04.py
# Day 4: STL + EWMA anomaly detection on residuals
# 目标：
# 1) 复用你 Day3 的“脏 CSV 处理逻辑”，稳定读入数据
# 2) 用 STL 分解得到 residual（残差 = 去掉趋势/季节后的“异常载体”）
# 3) 在 residual 上跑 EWMA，标记异常点
# 4) 输出：图 + 异常清单 CSV + 日志要点可直接写进 logs/day04.md

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.seasonal import STL


def load_metrics_csv(path: str) -> pd.DataFrame:
    """
    按你给的流程读 metrics.csv，并返回以 timestamp 为索引的 DataFrame。
    columns: qps, cpu, p95_latency (float)
    """
    # 1) 先按“整行字符串”读进来
    df = pd.read_csv(path, encoding="utf-8-sig")

    # 2) 删除无用空列（Excel 常见 Unnamed: 0 之类）
    df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])

    # 3) 把“整行字符串列”拆成真正的 4 列
    raw_col = df.columns[0]  # e.g. 'timestamp,qps,cpu,p95_latency'
    df[["timestamp", "qps", "cpu", "p95_latency"]] = (
        df[raw_col].astype(str).str.strip().str.split(",", expand=True)
    )

    # 4) 删除原始拼在一起的列
    df = df.drop(columns=[raw_col])

    # 5) 类型转换
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["qps"] = df["qps"].astype(float)
    df["cpu"] = df["cpu"].astype(float)
    df["p95_latency"] = df["p95_latency"].astype(float)

    # 6) 设置时间索引
    df = df.set_index("timestamp").sort_index()

    return df


def ewma_anomaly(
    series: pd.Series,
    alpha: float = 0.3,
    z: float = 3.0,
) -> pd.DataFrame:
    """
    在 residual 序列上做 EWMA 异常检测（最小可解释版本）。

    思路（为什么需要 EWMA）：
    - residual 本质上是“去掉周期/趋势后的偏差”
    - EWMA 像“带记忆的温度计”，持续跟踪 residual 的中心位置（均值）
    - 用滚动方差估计波动范围，再用 z-score 判定异常

    返回：
    - DataFrame: [value, ewma, sigma, upper, lower, is_anomaly, score]
    """
    x = series.astype(float)

    # EWMA 平滑后的中心线（均值的递推估计）
    ewma = x.ewm(alpha=alpha, adjust=False).mean()

    # 估计波动尺度：用 ewma 的残差再做 EWMA 方差（最小实现）
    # var_t = E[(x - mu)^2]
    resid = x - ewma
    var = (resid ** 2).ewm(alpha=alpha, adjust=False).mean()
    sigma = np.sqrt(var).replace(0, np.nan)

    # 置信带
    upper = ewma + z * sigma
    lower = ewma - z * sigma

    # 异常判定：超出带宽
    is_anomaly = (x > upper) | (x < lower)

    # 分数：偏离程度（|x-mu| / sigma）
    score = (resid.abs() / sigma).replace([np.inf, -np.inf], np.nan)

    out = pd.DataFrame(
        {
            "value": x,
            "ewma": ewma,
            "sigma": sigma,
            "upper": upper,
            "lower": lower,
            "is_anomaly": is_anomaly,
            "score": score,
        }
    )
    return out


def main():
    # ========== 0) 读取数据 ==========
    df = load_metrics_csv("data/raw/metrics.csv")

    # ========== 1) 选择检测对象：先用 QPS（最核心） ==========
    y = df["qps"]

    # ========== 2) STL 分解 ==========
    # period 选择：
    # - 你这份 mock 数据是小时粒度，一天 24 个点 -> period=24 最符合“日周期”
    # - 如果你未来换成 5min 粒度，就用 24*12=288
    stl = STL(y, period=24, robust=True)
    res = stl.fit()

    trend = res.trend
    seasonal = res.seasonal
    residual = res.resid  # 异常检测主要看它

    # ========== 3) 在 residual 上做 EWMA 异常检测 ==========
    # 参数建议：
    # - alpha 越大越敏感（0.2~0.4 常用）
    # - z 越小越容易报异常（2.5~3.5 常用）
    ew = ewma_anomaly(residual, alpha=0.3, z=3.0)

    # 异常清单
    anomalies = ew[ew["is_anomaly"]].copy()
    anomalies["timestamp"] = anomalies.index
    anomalies = anomalies[["timestamp", "value", "ewma", "upper", "lower", "score"]]
    anomalies = anomalies.sort_values("score", ascending=False)

    # ========== 4) 输出结果 ==========
    os.makedirs("reports/daily", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    anomalies_path = "data/processed/day04_anomalies_qps.csv"
    anomalies.to_csv(anomalies_path, index=False, encoding="utf-8-sig")
    print(f"[OK] anomalies saved: {anomalies_path}")
    print(anomalies.head(10))

    # ========== 5) 画图（1）：STL 分解 ==========
    plt.figure(figsize=(14, 8))
    plt.plot(y.index, y.values, label="QPS (raw)")
    plt.plot(trend.index, trend.values, label="Trend")
    plt.plot(seasonal.index, seasonal.values, label="Seasonal")
    plt.title("STL Decomposition (QPS)")
    plt.xlabel("Time")
    plt.ylabel("QPS")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # ========== 6) 画图（2）：Residual + EWMA band + anomalies ==========
    plt.figure(figsize=(14, 6))
    plt.plot(ew.index, ew["value"].values, label="Residual")
    plt.plot(ew.index, ew["ewma"].values, label="EWMA")
    plt.plot(ew.index, ew["upper"].values, label="Upper (EWMA + z*sigma)")
    plt.plot(ew.index, ew["lower"].values, label="Lower (EWMA - z*sigma)")

    # 异常点打散点
    anom_idx = ew.index[ew["is_anomaly"]]
    plt.scatter(anom_idx, ew.loc[anom_idx, "value"], marker="o", label="Anomalies")

    plt.title("Residual Anomaly Detection (STL residual + EWMA)")
    plt.xlabel("Time")
    plt.ylabel("Residual")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
