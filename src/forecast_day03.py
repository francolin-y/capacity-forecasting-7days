import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

# ========== Step 1: 原始读取 ==========
df = pd.read_csv(
    "data/raw/metrics.csv",
    encoding="utf-8-sig"
)

print("RAW COLUMNS:", df.columns.tolist())
print(df.head())

# ========== Step 2: 删除无用空列 ==========
df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])

# ========== Step 3: 拆分整行字符串列 ==========
raw_col = df.columns[0]  # e.g. 'timestamp,qps,cpu,p95_latency'

df[["timestamp", "qps", "cpu", "p95_latency"]] = (
    df[raw_col]
    .str.strip()
    .str.split(",", expand=True)
)

# ========== Step 4: 删除原始拼接列 ==========
df = df.drop(columns=[raw_col])

# ========== Step 5: 类型转换 ==========
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["qps"] = df["qps"].astype(float)
df["cpu"] = df["cpu"].astype(float)
df["p95_latency"] = df["p95_latency"].astype(float)

# ========== Step 6: 设置时间索引 ==========
df.set_index("timestamp", inplace=True)

# ================== Prophet 需要的格式 ==================
# Prophet 要求列名为 ds / y，且 ds 不能是 index
prophet_df = (
    df.reset_index()
      .rename(columns={
          "timestamp": "ds",
          "qps": "y"
      })
      [["ds", "y"]]
)

# ================== 训练 Prophet ==================
model = Prophet(
    daily_seasonality=True,
    weekly_seasonality=False
)

model.fit(prophet_df)

# ================== 预测未来 6 小时 ==================
future = model.make_future_dataframe(periods=6, freq="H")
forecast = model.predict(future)

# ================== 可视化 ==================
fig = model.plot(forecast)
plt.title("QPS Forecast (Prophet)")
plt.xlabel("Time")
plt.ylabel("QPS")
plt.show()

