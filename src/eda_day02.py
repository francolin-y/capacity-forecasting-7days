import pandas as pd
import matplotlib.pyplot as plt

# 1. 先按“整行字符串”读进来
df = pd.read_csv(
    "data/raw/metrics.csv",
    encoding="utf-8-sig"
)

print("RAW COLUMNS:", df.columns.tolist())
print(df.head())

# 2. 删除无用的空列
df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])

# 3. 把“整行字符串列”拆成真正的 4 列
raw_col = df.columns[0]  # 'timestamp,qps,cpu,p95_latency'

df[["timestamp", "qps", "cpu", "p95_latency"]] = (
    df[raw_col]
    .str.strip()
    .str.split(",", expand=True)
)

# 4. 删除原始拼在一起的列
df = df.drop(columns=[raw_col])

# 5. 类型转换
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["qps"] = df["qps"].astype(float)
df["cpu"] = df["cpu"].astype(float)
df["p95_latency"] = df["p95_latency"].astype(float)

# 6. 设置时间索引
df.set_index("timestamp", inplace=True)

# 7. 画图
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

df["qps"].plot(ax=axes[0], title="QPS")
df["cpu"].plot(ax=axes[1], title="CPU Usage")
df["p95_latency"].plot(ax=axes[2], title="P95 Latency (ms)")

plt.tight_layout()
plt.show()
