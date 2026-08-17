# -*- coding: utf-8 -*-
"""Week3 Task5：运维效能综合分析。"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
WEEK3 = ROOT / "results" / "week3"
OUT = WEEK3 / "comprehensive"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

def read(rel):
    return pd.read_csv(WEEK3 / rel, encoding="utf-8-sig")

def pct(v):
    return float(v) if pd.notna(v) else np.nan

def main():
    # 巡检：覆盖、缺陷闭环、缺陷后故障和评分下降
    cov = read("inspection/csv/station_inspection_coverage.csv")
    discovery = read("inspection/csv/defect_discovery_rate.csv").iloc[0]
    resolution = read("inspection/csv/defect_resolution_statistics.csv").iloc[0]
    relation = read("inspection/csv/defect_fault_relation.csv")
    declining = read("inspection/csv/declining_score_devices.csv")
    score = read("inspection/csv/inspection_score_statistics.csv")
    inspection_metrics = {
        "巡检覆盖率(%)": cov["巡检覆盖率(%)"].mean(),
        "缺陷发现率(%)": pct(discovery["缺陷发现率(%)"]),
        "缺陷消除率(%)": pct(resolution["缺陷消除率(%)"]),
        "缺陷后90天故障率(%)": relation["90天内是否故障"].mean() * 100,
        "评分持续下降设备占比(%)": len(declining) / len(score) * 100,
        "设备平均巡检评分": score["平均评分"].mean(),
    }
    inspection_score = np.mean([
        inspection_metrics["巡检覆盖率(%)"], inspection_metrics["缺陷消除率(%)"],
        100 - inspection_metrics["缺陷后90天故障率(%)"],
        100 - inspection_metrics["评分持续下降设备占比(%)"],
    ])

    # 检修：完成率、按时率、延期率
    completion = read("maintenance/csv/completion_rate.csv").set_index("指标")["数值"]
    timely = read("maintenance/csv/timeliness_rate.csv")
    delay = read("maintenance/csv/delay_analysis.csv")
    total_plans = timely["计划数量"].sum()
    overall_timely = timely["按时完成数量"].sum() / total_plans * 100
    delayed_rate = delay.loc[delay["延期等级"] != "按时完成", "数量"].sum() / total_plans * 100
    maintenance_metrics = {
        "计划检修完成率(%)": pct(completion["计划检修完成率"]),
        "检修及时率(%)": overall_timely,
        "延期率(%)": delayed_rate,
    }
    maintenance_score = np.mean([maintenance_metrics["计划检修完成率(%)"], overall_timely, 100 - delayed_rate])

    # 备件：库存状态和采购周期评价
    inventory = read("spare_parts/csv/inventory_warning.csv")
    procurement = read("spare_parts/csv/procurement_cycle_analysis.csv")
    normal_inventory = (inventory["库存状态"] == "正常").mean() * 100
    normal_procurement = (procurement["采购周期评价"] == "正常").mean() * 100
    spare_metrics = {"库存正常率(%)": normal_inventory, "采购周期正常率(%)": normal_procurement,
                     "库存不足备件数": int((inventory["库存状态"] == "库存不足").sum()),
                     "采购周期较长备件数": int((procurement["采购周期评价"] == "采购周期较长").sum())}
    spare_score = np.mean([normal_inventory, normal_procurement])

    # 成本：单台年均成本相对基准，年度趋势
    benchmark = read("operation_cost/csv/benchmark_compare.csv")
    latest = benchmark.iloc[-1]
    cost_ratio = latest["单台设备年均运维成本"] / latest["行业基准(万元/台年)"] * 100
    # 成本不高于行业基准时记为满分，高于基准按基准/实际值折算
    cost_score = min(100, latest["行业基准(万元/台年)"] / latest["单台设备年均运维成本"] * 100)
    cost_metrics = {"最新年度": int(latest["年份"]), "单台年均运维成本(万元/台年)": latest["单台设备年均运维成本"],
                    "行业基准(万元/台年)": latest["行业基准(万元/台年)"], "成本/行业基准(%)": cost_ratio}

    indicators = pd.DataFrame([
        ["巡检", "巡检覆盖率(%)", inspection_metrics["巡检覆盖率(%)"], "越高越好", "inspection/csv/station_inspection_coverage.csv"],
        ["巡检", "缺陷消除率(%)", inspection_metrics["缺陷消除率(%)"], "越高越好", "inspection/csv/defect_resolution_statistics.csv"],
        ["巡检", "缺陷后90天故障率(%)", inspection_metrics["缺陷后90天故障率(%)"], "越低越好", "inspection/csv/defect_fault_relation.csv"],
        ["检修", "计划检修完成率(%)", maintenance_metrics["计划检修完成率(%)"], "越高越好", "maintenance/csv/completion_rate.csv"],
        ["检修", "检修及时率(%)", maintenance_metrics["检修及时率(%)"], "越高越好", "maintenance/csv/timeliness_rate.csv"],
        ["检修", "延期率(%)", maintenance_metrics["延期率(%)"], "越低越好", "maintenance/csv/delay_analysis.csv"],
        ["备件", "库存正常率(%)", normal_inventory, "越高越好", "spare_parts/csv/inventory_warning.csv"],
        ["备件", "采购周期正常率(%)", normal_procurement, "越高越好", "spare_parts/csv/procurement_cycle_analysis.csv"],
        ["成本", "单台年均运维成本(万元/台年)", cost_metrics["单台年均运维成本(万元/台年)"], "越低越好", "operation_cost/csv/benchmark_compare.csv"],
        ["成本", "成本/行业基准(%)", cost_ratio, "越低越好", "operation_cost/csv/benchmark_compare.csv"],
    ], columns=["维度", "指标", "数值", "方向", "数据来源"])
    indicators.to_csv(OUT / "综合效能指标.csv", index=False, encoding="utf-8-sig")
    scores = pd.DataFrame({"维度": ["巡检", "检修", "备件", "成本"], "综合评分": [inspection_score, maintenance_score, spare_score, cost_score],
                          "评分说明": ["覆盖、闭环、缺陷后故障和评分下降反向指标等权平均", "完成、及时和延期反向指标等权平均", "库存正常率与采购周期正常率等权平均", "按最新年度单台成本相对行业基准反向计分"]})
    scores.loc[len(scores)] = ["总体", scores["综合评分"].mean(), "四维评分等权平均"]
    scores.to_csv(OUT / "综合效能评分.csv", index=False, encoding="utf-8-sig")

    # 问题优先级：使用实际异常量排序
    problems = pd.DataFrame([
        ["备件", "库存不足备件", spare_metrics["库存不足备件数"], "库存状态=库存不足"],
        ["巡检", "评分持续下降设备", len(declining), "declining_score_devices.csv记录数"],
        ["检修", "延期检修", int(delay.loc[delay["延期等级"] != "按时完成", "数量"].sum()), "延期等级不等于按时完成"],
        ["备件", "采购周期较长备件", spare_metrics["采购周期较长备件数"], "采购周期评价=采购周期较长"],
        ["成本", "异常成本增长月份", len(read("operation_cost/csv/abnormal_cost_growth.csv")), "成本环比增长率>50%（沿用现有逻辑）"],
        ["巡检", "缺陷后90天故障记录", int(relation["90天内是否故障"].sum()), "90天内是否故障=1"],
    ], columns=["维度", "问题", "数量", "判定依据"]).sort_values("数量", ascending=False)
    problems.to_csv(OUT / "运维问题优先级.csv", index=False, encoding="utf-8-sig")

    # 图表
    dims = scores.iloc[:4]
    fig, ax = plt.subplots(figsize=(8, 5)); ax.bar(dims["维度"], dims["综合评分"], color=["#2f6690", "#3d9970", "#d99024", "#a64b4b"]); ax.set_ylim(0, 100); ax.set_ylabel("评分"); ax.set_title("四维运维效能评分"); fig.tight_layout(); fig.savefig(OUT / "四维指标对比.png", dpi=160); plt.close(fig)
    vals = dims["综合评分"].tolist(); labels = dims["维度"].tolist(); angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist(); vals += vals[:1]; angles += angles[:1]
    fig = plt.figure(figsize=(6, 6)); ax = fig.add_subplot(111, polar=True); ax.plot(angles, vals, "o-", color="#2f6690"); ax.fill(angles, vals, alpha=.2, color="#2f6690"); ax.set_thetagrids(np.degrees(angles[:-1]), labels); ax.set_ylim(0, 100); ax.set_title("综合效能雷达图"); fig.tight_layout(); fig.savefig(OUT / "综合效能雷达图.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5)); ax.barh(problems["问题"], problems["数量"], color="#a64b4b"); ax.invert_yaxis(); ax.set_xlabel("记录数/数量"); ax.set_title("运维问题优先级"); fig.tight_layout(); fig.savefig(OUT / "运维问题优先级.png", dpi=160); plt.close(fig)
    annual = benchmark.copy(); fig, ax1 = plt.subplots(figsize=(8, 5)); ax1.plot(annual["年份"], annual["单台设备年均运维成本"], marker="o", label="单台年均成本"); ax1.axhline(float(annual["行业基准(万元/台年)"].iloc[-1]), color="#a64b4b", linestyle="--", label="行业基准"); ax1.set_ylabel("万元/台年"); ax1.set_title("成本与运维效能综合图"); ax1.legend(); fig.tight_layout(); fig.savefig(OUT / "成本与运维效能综合图.png", dpi=160); plt.close(fig)
    print("综合分析完成：", OUT)

if __name__ == "__main__":
    main()
