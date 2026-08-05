"""
故障-运行参数关联分析

Task3:
1. 提取故障发生前3个月运行参数
2. 对比故障设备与正常设备运行参数差异
3. 分析故障前参数变化趋势
4. 分析负荷率与故障发生相关性


输出：
results/week2

statistics / fault_parameter/
    fault_before_3months_parameter.csv
    fault_normal_parameter_compare.csv
    load_fault_correlation.csv

figures / fault_parameter/
    fault_before_load_trend.png
    fault_before_temperature_trend.png
    fault_before_insulation_trend.png
    fault_before_pd_trend.png

"""


from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# 中文字体配置
# ==============================

import matplotlib

matplotlib.rcParams['font.sans-serif'] = [
    'SimHei'
]

matplotlib.rcParams['axes.unicode_minus'] = False



# ==================================================
# 路径配置
# ==================================================

ROOT = Path(__file__).resolve().parents[1]


DATA_PATH = (
    ROOT /
    "data" /
    "raw" /
    "电力设备运维数据_2023-2026.xlsx"
)


RESULT_PATH = (
    ROOT /
    "results" /
    "week2"
)


STAT_PATH = RESULT_PATH / "statistics" / "fault_parameter"

FIG_PATH = RESULT_PATH / "figures" / "fault_parameter"



STAT_PATH.mkdir(
    parents=True,
    exist_ok=True
)


FIG_PATH.mkdir(
    parents=True,
    exist_ok=True
)



# ==================================================
# 运行参数分析指标
# ==================================================

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



# ==================================================
# 读取数据
# ==================================================

def load_data():

    print("正在读取数据...")


    fault = pd.read_excel(

        DATA_PATH,

        sheet_name="故障工单"

    )


    parameter = pd.read_excel(

        DATA_PATH,

        sheet_name="运行参数"

    )


    print(
        "故障工单数量:",
        len(fault)
    )

    print(
        "运行参数记录:",
        len(parameter)
    )


    return fault, parameter




# ==================================================
# 提取故障前三个月运行参数
# ==================================================

def extract_before_fault(
        fault,
        parameter
):


    print(
        "\n开始提取故障前三个月参数..."
    )


    fault["故障时间"] = pd.to_datetime(

        fault["故障时间"]

    )


    parameter["记录年月"] = pd.to_datetime(

        parameter["记录年月"]

    )



    records = []



    for _, row in fault.iterrows():


        device_id = row["设备编号"]


        fault_time = row["故障时间"]



        start_time = (

            fault_time -

            pd.DateOffset(
                months=3
            )

        )



        temp = parameter[

            (parameter["设备编号"] == device_id)

            &

            (parameter["记录年月"] >= start_time)

            &

            (parameter["记录年月"] < fault_time)

        ].copy()



        if len(temp) > 0:


            temp["故障时间"] = fault_time

            temp["故障设备"] = 1


            records.append(temp)



    if len(records) == 0:


        print(
            "未匹配到故障前三个月运行参数"
        )


        return pd.DataFrame()



    fault_parameter = pd.concat(

        records,

        ignore_index=True

    )



    fault_parameter.to_csv(

        STAT_PATH /
        "fault_before_3months_parameter.csv",

        index=False,

        encoding="utf-8-sig"

    )



    print(

        "故障前三个月参数记录:",

        len(fault_parameter)

    )



    return fault_parameter





# ==================================================
# 故障设备与正常设备参数比较
# ==================================================

def compare_parameter(
        parameter,
        fault_parameter
):


    print(
        "\n开始故障设备参数对比..."
    )



    fault_devices = (

        fault_parameter
        ["设备编号"]
        .unique()

    )



    parameter["是否故障设备"] = (

        parameter["设备编号"]
        .isin(fault_devices)

    )



    result = (

        parameter

        .groupby(
            "是否故障设备"
        )

        [PARAM_COLUMNS]

        .mean()

    )



    result.to_csv(

        STAT_PATH /
        "fault_normal_parameter_compare.csv",

        encoding="utf-8-sig"

    )



    print(result)




# ==================================================
# 故障前三个月趋势分析
# ==================================================

def plot_fault_trend(
        fault_parameter
):


    print(
        "\n生成趋势图..."
    )



    trend = (

        fault_parameter

        .groupby(
            "记录年月"
        )

        [PARAM_COLUMNS]

        .mean()

    )



    # --------------------------
    # 负荷趋势
    # --------------------------

    plt.figure(
        figsize=(10,5)
    )


    plt.plot(

        trend.index,

        trend["月平均负荷率"],

        marker="o"

    )


    plt.title(
        "故障前三个月平均负荷率趋势"
    )


    plt.xlabel(
        "时间"
    )


    plt.ylabel(
        "负荷率"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH /
        "fault_before_load_trend.png",

        dpi=300

    )


    plt.close()



    # --------------------------
    # 温升趋势
    # --------------------------

    plt.figure(
        figsize=(10,5)
    )


    plt.plot(

        trend.index,

        trend["油温（℃）"],

        marker="o",

        label="油温"

    )


    plt.plot(

        trend.index,

        trend["绕组温度（℃）"],

        marker="o",

        label="绕组温度"

    )


    plt.legend()


    plt.title(
        "故障前三个月温升趋势"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()



    plt.savefig(

        FIG_PATH /
        "fault_before_temperature_trend.png",

        dpi=300

    )


    plt.close()



    # --------------------------
    # 绝缘趋势
    # --------------------------

    plt.figure(
        figsize=(10,5)
    )


    plt.plot(

        trend.index,

        trend["绝缘电阻（MΩ）"],

        marker="o"

    )


    plt.title(
        "故障前三个月绝缘电阻趋势"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()



    plt.savefig(

        FIG_PATH /
        "fault_before_insulation_trend.png",

        dpi=300

    )


    plt.close()



    # --------------------------
    # 局放趋势
    # --------------------------

    plt.figure(
        figsize=(10,5)
    )


    plt.plot(

        trend.index,

        trend["局部放电量（pC）"],

        marker="o"

    )


    plt.title(
        "故障前三个月局部放电趋势"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()



    plt.savefig(

        FIG_PATH /
        "fault_before_pd_trend.png",

        dpi=300

    )


    plt.close()




# ==================================================
# 负荷率与故障相关性
# ==================================================

def load_fault_correlation(
        fault,
        parameter
):


    print(
        "\n分析负荷率与故障关系..."
    )



    fault_devices = (

        fault["设备编号"]
        .unique()

    )



    parameter["是否故障"] = (

        parameter["设备编号"]
        .isin(fault_devices)

    )



    correlation = (

        parameter

        [

        [

        "月平均负荷率",

        "月最大负荷率",

        "是否故障"

        ]

        ]

        .corr()

    )



    correlation.to_csv(

        STAT_PATH /
        "load_fault_correlation.csv",

        encoding="utf-8-sig"

    )



    print(correlation)




# ==================================================
# 主函数
# ==================================================

def main():


    fault, parameter = load_data()



    fault_parameter = extract_before_fault(

        fault,

        parameter

    )



    if fault_parameter.empty:


        return



    compare_parameter(

        parameter,

        fault_parameter

    )



    plot_fault_trend(

        fault_parameter

    )



    load_fault_correlation(

        fault,

        parameter

    )



    print(

        "\n===== 故障-参数关联分析完成 ====="

    )




if __name__ == "__main__":


    main()