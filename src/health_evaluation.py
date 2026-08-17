# -*- coding: utf-8 -*-
"""Week4 Task1：设备健康综合评价。"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "电力设备运维数据_2023-2026.xlsx"
OUT = ROOT / "results" / "week4" / "health"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

WEIGHTS = {"故障风险": .25, "可靠性": .20, "运行状态": .20, "巡检状态": .15, "检修状态": .10, "基础风险": .10}

def scale_high(s):
    s = pd.to_numeric(s, errors="coerce"); lo, hi = s.min(), s.max()
    return pd.Series(50.0, index=s.index) if pd.isna(lo) or hi == lo else (s - lo) / (hi - lo) * 100

def scale_low(s):
    return 100 - scale_high(s)

def main():
    device = pd.read_excel(DATA, sheet_name="设备台账")
    fault = pd.read_excel(DATA, sheet_name="故障工单")
    inspection = pd.read_excel(DATA, sheet_name="巡检记录")
    maintenance = pd.read_excel(DATA, sheet_name="检修计划")
    parameter = pd.read_excel(DATA, sheet_name="运行参数")
    for frame, col in [(fault, "故障时间"), (inspection, "巡检日期"), (maintenance, "实际日期"), (parameter, "记录年月")]:
        frame[col] = pd.to_datetime(frame[col], errors="coerce")

    base = device.drop_duplicates("设备编号").copy()
    # 故障风险：故障次数、严重故障占比、重复故障率
    f = fault.groupby("设备编号").agg(故障次数=("设备编号", "size"), 累计修复时间=("修复耗时（小时）", "sum"), 严重故障次数=("严重等级", lambda x: x.astype(str).isin(["严重", "重大", "高"]).sum())).reset_index()
    f["严重故障占比"] = f["严重故障次数"] / f["故障次数"]
    f["故障风险原始"] = f["故障次数"] + f["严重故障次数"] * 2
    # 可靠性：直接复用 Week2 口径计算设备级指标
    total_hours = 41 * 30 * 24
    f["MTTR(h)"] = f["累计修复时间"] / f["故障次数"]
    f["MTBF(h)"] = (total_hours - f["累计修复时间"]) / f["故障次数"]
    f["设备可用率"] = (total_hours - f["累计修复时间"]) / total_hours
    # 巡检状态：评分、缺陷率、评分下降
    i = inspection.groupby("设备编号").agg(平均巡检评分=("巡检评分", "mean"), 巡检次数=("设备编号", "size"), 缺陷次数=("是否发现缺陷", lambda x: (x.astype(str).isin(["是", "1", "True"])).sum())).reset_index()
    i["缺陷率"] = i["缺陷次数"] / i["巡检次数"]
    # 检修状态：延期率
    m = maintenance.groupby("设备编号").agg(检修次数=("设备编号", "size"), 平均延期天数=("延期天数", "mean"), 延期次数=("延期天数", lambda x: (pd.to_numeric(x, errors="coerce").fillna(0) > 0).sum())).reset_index()
    m["延期率"] = m["延期次数"] / m["检修次数"]
    # 运行状态：负荷率和参数趋势的可用数据
    p = parameter.groupby("设备编号").agg(平均负荷率=("月平均负荷率", "mean"), 最大负荷率=("月最大负荷率", "mean"), 平均油温=("油温（℃）", "mean"), 绝缘电阻=("绝缘电阻（MΩ）", "mean")).reset_index()
    # 设备年龄风险
    base["年龄风险原始"] = pd.to_numeric(base.get("已运行年限"), errors="coerce") / pd.to_numeric(base.get("设计寿命（年）"), errors="coerce")
    result = base.merge(f, on="设备编号", how="left").merge(i, on="设备编号", how="left").merge(m, on="设备编号", how="left").merge(p, on="设备编号", how="left")
    for c in ["故障次数", "累计修复时间", "严重故障次数", "故障风险原始", "平均巡检评分", "缺陷率", "平均延期天数", "延期率", "平均负荷率", "最大负荷率", "平均油温", "绝缘电阻", "MTTR(h)", "MTBF(h)", "设备可用率"]:
        if c not in result: result[c] = 0.0
        result[c] = pd.to_numeric(result[c], errors="coerce").fillna(result[c].median() if result[c].notna().any() else 0)
    result["故障风险得分"] = scale_low(result["故障风险原始"])
    result["可靠性得分"] = (scale_high(result["MTBF(h)"]) + scale_low(result["MTTR(h)"]) + result["设备可用率"] * 100) / 3
    result["运行状态得分"] = (scale_low(result["平均负荷率"]) + scale_low(result["最大负荷率"]) + scale_low(result["平均油温"]) + scale_high(result["绝缘电阻"])) / 4
    result["巡检状态得分"] = (result["平均巡检评分"] + scale_low(result["缺陷率"])) / 2
    result["检修状态得分"] = scale_low(result["延期率"])
    result["基础风险得分"] = scale_low(result["年龄风险原始"])
    result["健康评分"] = sum(result[f"{k}得分"] * w for k, w in WEIGHTS.items()).clip(0, 100)
    result["健康等级"] = pd.cut(result["健康评分"], bins=[-np.inf, 40, 60, 70, 85, np.inf], labels=["高风险", "预警", "注意", "良", "优"], right=False)
    result = result.sort_values("健康评分", ascending=False)
    result.to_csv(OUT / "设备健康评分排名.csv", index=False, encoding="utf-8-sig")
    result[result["健康等级"].isin(["高风险", "预警"])].to_csv(OUT / "高风险设备清单.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"维度": list(WEIGHTS), "权重": list(WEIGHTS.values())}).to_csv(OUT / "健康评价权重.csv", index=False, encoding="utf-8-sig")
    counts = result["健康等级"].value_counts().reindex(["优", "良", "注意", "预警", "高风险"], fill_value=0)
    counts.rename_axis("健康等级").reset_index(name="设备数量").to_csv(OUT / "健康等级分布.csv", index=False, encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(8, 5)); counts.plot(kind="bar", ax=ax, color=["#2e8b57", "#5b9bd5", "#f4b183", "#ed7d31", "#c00000"]); ax.set_title("设备健康等级分布"); ax.set_ylabel("设备数量"); fig.tight_layout(); fig.savefig(OUT / "健康等级分布.png", dpi=160); plt.close(fig)
    top = result.nsmallest(10, "健康评分"); fig, ax = plt.subplots(figsize=(8, 5)); ax.barh(top["设备编号"], top["健康评分"], color="#c00000"); ax.invert_yaxis(); ax.set_xlabel("健康评分"); ax.set_title("高风险设备Top10"); fig.tight_layout(); fig.savefig(OUT / "高风险设备Top10.png", dpi=160); plt.close(fig)
    print(f"健康评价完成：{len(result)}台设备，重点设备{len(result[result['健康等级'].isin(['高风险','预警'])])}台")

if __name__ == "__main__":
    main()
