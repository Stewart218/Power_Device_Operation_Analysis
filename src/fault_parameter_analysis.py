"""
故障-运行参数关联分析

Task3:
1. 提取故障前3个月及故障月份运行参数
2. 基于设备自身历史状态计算参数相对变化率
3. 绘制故障前参数异常趋势图
4. 分析高负荷率与故障发生相关性


"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")


# ==============================
# 路径配置
# ==============================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "电力设备运维数据_2023-2026.xlsx"
)


RESULT_PATH = (
    PROJECT_ROOT
    / "results"
    / "week2"
)

STAT_PATH = RESULT_PATH / "statistics" / "fault_parameter_analysis"
FIG_PATH = RESULT_PATH / "figures" / "fault_parameter_analysis"


STAT_PATH.mkdir(
    parents=True,
    exist_ok=True
)

FIG_PATH.mkdir(
    parents=True,
    exist_ok=True
)



# ==============================
# 中文显示
# ==============================

plt.rcParams["font.sans-serif"] = [
    "SimHei"
]

plt.rcParams[
    "axes.unicode_minus"
] = False



# ==============================
# 参数配置
# ==============================

PARAM_COLUMNS = [

    "月平均负荷率",

    "月最大负荷率",

    "环境温度（℃）",

    "油温（℃）",

    "绕组温度（℃）",

    "绝缘电阻（MΩ）",

    "介质损耗角tanδ",

    "局部放电量（pC）",

    "SF6气体压力（MPa）"

]


# 正向异常:
# 数值升高表示风险增加

POSITIVE_PARAMS = [

    "月平均负荷率",

    "月最大负荷率",

    "环境温度（℃）",

    "油温（℃）",

    "绕组温度（℃）",

    "介质损耗角tanδ",

    "局部放电量（pC）"

]


# 反向异常:
# 数值下降表示风险增加

NEGATIVE_PARAMS = [

    "绝缘电阻（MΩ）",

    "SF6气体压力（MPa）"

]



# ==============================
# 数据读取
# ==============================

def load_data():

    print("读取数据...")


    fault = pd.read_excel(
        DATA_PATH,
        sheet_name="故障工单"
    )


    parameter = pd.read_excel(
        DATA_PATH,
        sheet_name="运行参数"
    )


    fault["故障时间"] = pd.to_datetime(
        fault["故障时间"]
    )


    parameter["记录年月"] = pd.to_datetime(
        parameter["记录年月"]
    )


    return fault, parameter




# ==============================
# 构造故障窗口
# ==============================

def build_fault_window(
        fault,
        parameter
):


    print(
        "构造故障前3个月窗口..."
    )


    records = []


    for _, row in fault.iterrows():

        device = row["设备编号"]

        fault_time = row["故障时间"]


        temp = parameter[
            parameter["设备编号"]
            ==
            device
        ].copy()


        if len(temp)==0:
            continue


        temp["距离故障月份"] = (

            (

            temp["记录年月"].dt.year
            -
            fault_time.year

            )
            *
            12

            +

            (
            temp["记录年月"].dt.month
            -
            fault_time.month
            )

        )


        temp = temp[
            temp["距离故障月份"]
            .isin(
                [-3,-2,-1,0]
            )
        ]


        temp["故障时间"] = fault_time


        temp["故障类型"] = row["故障类型"]


        records.append(temp)



    if len(records)==0:

        raise ValueError(
            "没有匹配到故障运行参数"
        )


    result = pd.concat(
        records,
        ignore_index=True
    )


    result.to_csv(

        STAT_PATH
        /
        "fault_parameter_window.csv",

        index=False,

        encoding="utf-8-sig"

    )


    return result




# ==============================
# 计算相对变化率
# ==============================


def calculate_relative_change(
        data
):


    print(
        "计算参数相对变化率..."
    )


    result=[]


    for device, group in data.groupby(
            "设备编号"
    ):


        baseline_data = group[
            group["距离故障月份"]
            .isin(
                [-3,-2,-1]
            )
        ]


        fault_data = group[
            group["距离故障月份"]
            ==
            0
        ]


        if len(baseline_data)==0:
            continue


        if len(fault_data)==0:
            continue



        baseline = (
            baseline_data[
                PARAM_COLUMNS
            ]
            .mean()
        )


        fault_value = (
            fault_data[
                PARAM_COLUMNS
            ]
            .mean()
        )


        item={

            "设备编号":
            device

        }


        for p in PARAM_COLUMNS:


            if p in POSITIVE_PARAMS:


                change = (

                    fault_value[p]
                    -
                    baseline[p]

                ) / baseline[p]


            else:


                change = (

                    baseline[p]
                    -
                    fault_value[p]

                ) / baseline[p]


            item[
                p+"异常变化率"
            ] = change



        result.append(item)



    df = pd.DataFrame(
        result
    )


    df.to_csv(

        STAT_PATH
        /
        "fault_parameter_change_rate.csv",

        index=False,

        encoding="utf-8-sig"

    )


    return df




# ==============================
# 绘制异常趋势
# ==============================

def plot_relative_trend(
        data
):


    print(
        "绘制故障前参数异常趋势..."
    )


    trend=[]


    for device, group in data.groupby(
            "设备编号"
    ):


        base = (

            group[
                group["距离故障月份"]
                .isin([-3,-2,-1])
            ]

            [PARAM_COLUMNS]

            .mean()

        )


        for _, row in group.iterrows():

            item={

                "距离故障月份":
                row["距离故障月份"]

            }


            for p in PARAM_COLUMNS:


                if p in POSITIVE_PARAMS:

                    value=(

                        row[p]-base[p]

                    )/base[p]


                else:

                    value=(

                        base[p]-row[p]

                    )/base[p]


                item[p]=value


            trend.append(item)



    trend=pd.DataFrame(
        trend
    )


    trend_mean=(

        trend

        .groupby(
            "距离故障月份"
        )

        [PARAM_COLUMNS]

        .mean()

        .reindex(
            [-3,-2,-1,0]
        )

    )


    trend_mean.to_csv(

        STAT_PATH
        /
        "fault_relative_trend.csv",

        encoding="utf-8-sig"

    )


    for p in PARAM_COLUMNS:


        plt.figure(
            figsize=(8,5)
        )


        plt.plot(

            trend_mean.index,

            trend_mean[p],

            marker="o"

        )


        plt.xlabel(
            "距离故障月份"
        )


        plt.ylabel(
            "相对异常变化率"
        )


        plt.title(

            f"{p}故障前异常趋势"

        )


        plt.xticks(
            [-3,-2,-1,0]
        )


        plt.grid(
            alpha=0.3
        )


        plt.tight_layout()


        plt.savefig(

            FIG_PATH
            /
            f"{p}_fault_trend.png",

            dpi=300

        )


        plt.close()




# ==============================
# 高负荷相关性分析
# ==============================

def load_fault_correlation(
        change
):


    print(
        "分析负荷率相关性..."
    )


    result=(

        change

        [
            [
            "设备编号",
            "月平均负荷率异常变化率",
            "月最大负荷率异常变化率"
            ]

        ]

    )


    result.to_csv(

        STAT_PATH
        /
        "load_fault_correlation.csv",

        index=False,

        encoding="utf-8-sig"

    )




# ==============================
# 主程序
# ==============================


def main():


    fault, parameter = load_data()


    window = build_fault_window(

        fault,

        parameter

    )


    change = calculate_relative_change(

        window

    )


    plot_relative_trend(

        window

    )


    load_fault_correlation(

        change

    )


    print(
        "\nTask3分析完成"
    )



if __name__ == "__main__":

    main()