from dataclasses import dataclass

@dataclass
class DecisionInput:
    peak_p95_latency: float
    slo_p95_ms: float
    warn_count: int
    breach_count: int
    anomaly_count: int


def decide_action(x: DecisionInput) -> str:
    """
    决策优先级：确定性 > 保守兜底
    """
    # 1) 明确 breach
    if x.breach_count > 0:
        if x.anomaly_count == 0:
            return "SCALE_UP"
        return "INVESTIGATE"

    # 2) 临界风险（WARN）
    if x.warn_count > 0:
        if x.peak_p95_latency >= 0.9 * x.slo_p95_ms:
            return "SCALE_UP"
        if x.anomaly_count > 0:
            return "INVESTIGATE"

    # 3) 稳定状态
    if x.warn_count == 0 and x.breach_count == 0 and x.anomaly_count == 0:
        return "NO_OP"

    # 4) 兜底
    return "INVESTIGATE"


if __name__ == "__main__":
    # 用你 Day 5 的真实结果做一次“回放测试”
    inp = DecisionInput(
        peak_p95_latency=410,
        slo_p95_ms=400,
        warn_count=5,
        breach_count=1,
        anomaly_count=0,
    )

    action = decide_action(inp)
    print(f"[DECISION] action={action}")
