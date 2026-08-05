"""
电力设备运维可靠性分析

功能：
1. MTBF计算
2. MTTR计算
3. 设备可用率计算
4. 不同维度可靠性对比
5. Top10风险设备识别

"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# ==============================
# 中文字体配置
# ==============================

import matplotlib

matplotlib.rcParams['font.sans-serif'] = [
    'SimHei'
]

matplotlib.rcParams['axes.unicode_minus'] = False



from pathlib import Path


# ======================
# 路径配置
# ======================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT /
    "data" /
    "raw" /
    "电力设备运维数据_2023-2026.xlsx"
)


RESULT_PATH = (
    PROJECT_ROOT /
    "results" /
    "week2"

)

STAT_PATH = RESULT_PATH / "statistics" / "reliability"

FIG_PATH = RESULT_PATH / "figures" / "reliability"


STAT_PATH.mkdir(
    parents=True,
    exist_ok=True
)

FIG_PATH.mkdir(
    parents=True,
    exist_ok=True
)



# ======================
# 数据读取
# ======================

def load_data():

    fault = pd.read_excel(
        DATA_PATH,
        sheet_name="故障工单"
    )


    device = pd.read_excel(
        DATA_PATH,
        sheet_name="设备台账"
    )


    return fault, device



# ======================
# 数据融合
# ======================

def merge_data(fault, device):

    df = fault.merge(
        device,
        on="设备编号",
        how="left"
    )

    return df



# ======================
# 可靠性指标计算
# ======================

def calculate_reliability(df):


    # 故障次数

    fault_count = (
        df
        .groupby("设备编号")
        .size()
        .rename("故障次数")
    )


    # 总修复时间

    repair_time = (
        df
        .groupby("设备编号")
        ["修复耗时（小时）"]
        .sum()
        .rename("累计修复时间")
    )


    result = pd.concat(
        [
            fault_count,
            repair_time
        ],
        axis=1
    )


    # 默认统计周期
    # 2023.1 - 2026.5
    # 约41个月

    total_hours = (
        41 * 30 * 24
    )


    # MTTR

    result["MTTR(h)"] = (
        result["累计修复时间"]
        /
        result["故障次数"]
    )


    # MTBF

    result["MTBF(h)"] = (

        (
            total_hours -
            result["累计修复时间"]
        )
        /
        result["故障次数"]

    )


    # 可用率

    result["设备可用率"] = (

        (
            total_hours -
            result["累计修复时间"]
        )
        /
        total_hours

    )


    result = result.reset_index()


    return result



# ======================
# 关联设备信息
# ======================

def add_device_info(result,device):


    result = result.merge(

        device,

        on="设备编号",

        how="left"

    )


    return result

# ======================
# 按设备年龄分层分析
# ======================

def analyze_by_age(df):


    # ----------------------
    # 设备年龄分组
    # ----------------------

    def age_group(age):

        if age <= 5:
            return "0-5年"

        elif age <= 10:
            return "5-10年"

        elif age <= 20:
            return "10-20年"

        else:
            return "20年以上"



    df["设备年龄分组"] = (

        df["已运行年限"]
        .apply(age_group)

    )


    # ----------------------
    # 分组可靠性指标
    # ----------------------

    result = (

        df
        .groupby("设备年龄分组")
        [
            [
                "MTBF(h)",
                "MTTR(h)",
                "设备可用率"
            ]
        ]
        .mean()

    )


    result.to_csv(

        STAT_PATH /
        "reliability_by_age.csv",

        encoding="utf-8-sig"

    )


    print(
        "\n设备年龄可靠性分析:"
    )

    print(result)


    return result

# ======================
# 按设备类型分析
# ======================

def analyze_by_type(df):


    result = (

        df
        .groupby("设备类型")
        [
            [
                "MTBF(h)",
                "MTTR(h)",
                "设备可用率"
            ]
        ]
        .mean()

    )


    result.to_csv(

        STAT_PATH /
        "reliability_by_type.csv",

        encoding="utf-8-sig"

    )


    return result



# ======================
# 按电压等级分析
# ======================

def analyze_by_voltage(df):


    result = (

        df
        .groupby("电压等级")
        [
            [
                "MTBF(h)",
                "MTTR(h)",
                "设备可用率"
            ]
        ]
        .mean()

    )


    result.to_csv(

        STAT_PATH /
        "reliability_by_voltage.csv",

        encoding="utf-8-sig"

    )


    return result



# ======================
# Top10风险设备
# ======================

def top10_risk(df):


    result = (

        df
        .sort_values(
            "MTBF(h)"
        )
        .head(10)

    )


    result.to_csv(

        STAT_PATH /
        "reliability_top10_risk_devices.csv",

        index=False,

        encoding="utf-8-sig"

    )


    return result



# ======================
# 设备类型可靠性指标柱状图
# ======================

def plot_type_reliability_bar(df):


    data = df.reset_index()


    # MTBF

    plt.figure(
        figsize=(10,6)
    )


    sns.barplot(
        data=data,
        x="设备类型",
        y="MTBF(h)"
    )


    plt.title(
        "不同设备类型MTBF对比"
    )

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "reliability_MTBF_device_type_bar.png",

        dpi=300

    )

    plt.close()



    # MTTR

    plt.figure(
        figsize=(10,6)
    )


    sns.barplot(
        data=data,
        x="设备类型",
        y="MTTR(h)"
    )


    plt.title(
        "不同设备类型MTTR对比"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "reliability_MTTR_device_type_bar.png",

        dpi=300

    )


    plt.close()



    # 可用率

    plt.figure(
        figsize=(10,6)
    )


    sns.barplot(

        data=data,

        x="设备类型",

        y="设备可用率"

    )


    plt.title(

        "不同设备类型设备可用率对比"

    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "reliability_availability_device_type_bar.png",

        dpi=300

    )


    plt.close()

# ======================
# 年龄分组可靠性对比图
# ======================

def plot_age_reliability(result):


    data = result.reset_index()


    # MTBF

    plt.figure(
        figsize=(8,5)
    )


    sns.barplot(

        data=data,

        x="设备年龄分组",

        y="MTBF(h)"

    )


    plt.title(
        "不同服役年限设备MTBF对比"
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "reliability_MTBF_by_age_group.png",

        dpi=300

    )


    plt.close()



    # 可用率

    plt.figure(
        figsize=(8,5)
    )


    sns.barplot(

        data=data,

        x="设备年龄分组",

        y="设备可用率"

    )


    plt.title(
        "不同服役年限设备可用率对比"
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "reliability_availability_by_age_group.png",

        dpi=300

    )


    plt.close()

# ======================
# 月度可靠性趋势分析
# ======================

def reliability_trend(df):


    df["故障月份"] = (

        pd.to_datetime(
            df["故障时间"]
        )
        .dt
        .to_period("M")
        .astype(str)

    )


    trend = (

        df
        .groupby("故障月份")
        .agg(

            故障次数=
            ("故障工单号","count"),

            平均修复时间=
            ("修复耗时（小时）","mean")

        )

    )


    trend.to_csv(

        STAT_PATH /
        "reliability_monthly_trend.csv",

        encoding="utf-8-sig"

    )


    # 折线图


    plt.figure(

        figsize=(12,5)

    )


    plt.plot(

        trend.index,

        trend["故障次数"],

        marker="o"

    )


    plt.xticks(

        rotation=45

    )


    plt.title(

        "月度故障次数变化趋势"

    )


    plt.xlabel(
        "月份"
    )


    plt.ylabel(
        "故障次数"
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "monthly_fault_trend.png",

        dpi=300

    )


    plt.close()



    # MTTR趋势


    plt.figure(

        figsize=(12,5)

    )


    plt.plot(

        trend.index,

        trend["平均修复时间"],

        marker="o"

    )


    plt.xticks(

        rotation=45

    )


    plt.title(

        "月度平均MTTR变化趋势"

    )


    plt.xlabel(
        "月份"
    )


    plt.ylabel(
        "MTTR(h)"
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "reliability_monthly_MTTR_trend.png",

        dpi=300

    )


    plt.close()

# ======================
# 主程序
# ======================


def main():


    fault,device = load_data()


    df = merge_data(
        fault,
        device
    )


    reliability = calculate_reliability(df)


    reliability = add_device_info(
        reliability,
        device
    )


    reliability.to_csv(

        STAT_PATH /
        "reliability_device_index.csv",

        index=False,

        encoding="utf-8-sig"

    )

    type_result = analyze_by_type(
        reliability
    )

    # 年龄分组分析

    age_result = analyze_by_age(
        reliability
    )

    plot_age_reliability(
        age_result
    )

    voltage_result = analyze_by_voltage(
        reliability
    )

    top10_risk(
        reliability
    )

    # 新增

    plot_type_reliability_bar(
        type_result
    )

    reliability_trend(
        df
    )


    print(
        "可靠性分析完成"
    )



if __name__=="__main__":

    main()