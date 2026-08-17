"""
Task4:
重复故障与慢性病设备分析

功能:
1. 识别90天内重复故障设备
2. 计算重复故障率
3. 分析重复故障设备共性特征
4. 构建设备慢性病风险评分
5. 输出故障规律分析报告

"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings


warnings.filterwarnings("ignore")


# ==============================
# 路径配置
# ==============================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


DATA_PATH = (
    PROJECT_ROOT
    /
    "data"
    /
    "raw"
    /
    "电力设备运维数据_2023-2026.xlsx"
)


RESULT_PATH = (
    PROJECT_ROOT
    /
    "results"
    /
    "week2"
)


STAT_PATH = RESULT_PATH / "statistics" / "recurring_fault"
FIG_PATH = RESULT_PATH / "figures" / "recurring_fault"
REPORT_PATH = RESULT_PATH / "reports"


for path in [
    STAT_PATH,
    FIG_PATH,
    REPORT_PATH
]:
    path.mkdir(
        parents=True,
        exist_ok=True
    )


# ==============================
# 中文显示
# ==============================

plt.rcParams["font.sans-serif"] = [
    "SimHei"
]

plt.rcParams["axes.unicode_minus"] = False



# ==============================
# 数据读取
# ==============================

def load_data():

    print("读取数据...")


    fault = pd.read_excel(
        DATA_PATH,
        sheet_name="故障工单"
    )


    device = pd.read_excel(
        DATA_PATH,
        sheet_name="设备台账"
    )


    parameter = pd.read_excel(
        DATA_PATH,
        sheet_name="运行参数"
    )


    fault["故障时间"] = pd.to_datetime(
        fault["故障时间"]
    )


    return fault, device, parameter




# ==============================
# 1. 识别90天重复故障
# ==============================


def identify_repeat_fault(
        fault
):


    print(
        "识别90天重复故障..."
    )


    records=[]


    fault_sort = (
        fault
        .sort_values(
            [
                "设备编号",
                "故障时间"
            ]
        )
    )


    for device_id, group in fault_sort.groupby(
            "设备编号"
    ):


        times = (
            group["故障时间"]
            .tolist()
        )


        repeat_count=0


        intervals=[]


        for i in range(
            1,
            len(times)
        ):

            days = (
                times[i]
                -
                times[i-1]
            ).days


            intervals.append(days)


            if days <=90:

                repeat_count +=1



        if repeat_count>0:


            records.append({

                "设备编号":
                device_id,

                "故障总次数":
                len(times),

                "90天重复故障次数":
                repeat_count,

                "首次故障时间":
                min(times),

                "最近故障时间":
                max(times),

                "平均故障间隔天数":
                np.mean(intervals)

            })



    result=pd.DataFrame(records)


    result["重复故障率"]=(
        result["90天重复故障次数"]
        /
        result["故障总次数"]
        *
        100
    )


    result.to_csv(

        STAT_PATH
        /
        "repeated_fault_devices.csv",

        index=False,

        encoding="utf-8-sig"

    )


    return result




# ==============================
# 2. 设备特征分析
# ==============================


def analyze_device_feature(
        repeat,
        device,
        fault
):


    print(
        "分析设备特征..."
    )

    # 获取设备故障严重等级统计

    fault_level = (

        fault

        .groupby("设备编号")

        ["严重等级"]

        .agg(
            lambda x:
            x.mode()[0]
            if len(x.mode()) > 0
            else "未知"
        )

        .reset_index()

    )

    data = pd.merge(

        repeat,

        device,

        on="设备编号",

        how="left"

    )

    data = pd.merge(

        data,

        fault_level,

        on="设备编号",

        how="left"

    )


    data.to_csv(

        STAT_PATH
        /
        "repeated_fault_device_feature.csv",

        index=False,

        encoding="utf-8-sig"

    )



    # 类型分布

    type_count=(

        data
        ["设备类型"]
        .value_counts()

    )


    plt.figure(
        figsize=(8,5)
    )


    type_count.plot(
        kind="bar"
    )


    plt.title(
        "重复故障设备类型分布"
    )


    plt.ylabel(
        "设备数量"
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH
        /
        "repeated_fault_equipment_type.png",

        dpi=300

    )


    plt.close()



    return data




# ==============================
# 3. 年限分析
# ==============================


def age_analysis(
        data
):


    print(
        "分析运行年限..."
    )


    bins=[0,5,10,20,100]

    labels=[

        "0-5年",

        "5-10年",

        "10-20年",

        "20年以上"

    ]


    data["年龄分组"]=pd.cut(

        data["已运行年限"],

        bins=bins,

        labels=labels

    )


    age_count=(

        data["年龄分组"]

        .value_counts()

        .sort_index()

    )


    plt.figure(
        figsize=(8,5)
    )


    age_count.plot(
        kind="bar"
    )


    plt.title(
        "重复故障设备运行年限分布"
    )


    plt.ylabel(
        "设备数量"
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH
        /
        "repeated_fault_device_age.png",

        dpi=300

    )


    plt.close()



    return data




# ==============================
# 4. 运行工况分析
# ==============================


def operating_condition(
        chronic,
        parameter
):


    print(
        "分析运行工况..."
    )


    param = (

        parameter

        .groupby(
            "设备编号"
        )

        [

        [
        "月平均负荷率",
        "油温（℃）",
        "绝缘电阻（MΩ）"
        ]

        ]

        .mean()

    )


    result=pd.merge(

        chronic,

        param,

        on="设备编号",

        how="left"

    )


    result.to_csv(

        STAT_PATH
        /
        "chronic_device_operating_condition.csv",

        index=False,

        encoding="utf-8-sig"

    )


    return result




# ==============================
# 5. 慢性病风险评分
# ==============================


def build_chronic_score(
        data
):


    print(
        "计算风险评分..."
    )


    score = pd.DataFrame()


    score["设备编号"]=data["设备编号"]


    # 重复故障

    score["重复故障得分"]=(
        data["90天重复故障次数"]
        /
        data["90天重复故障次数"]
        .max()
        *
        40
    )



    # 年龄


    score["年龄风险"]=np.where(

        data["已运行年限"]>20,

        20,

        data["已运行年限"]/20*20

    )


    # 严重等级

    level_score = {

        "紧急": 20,

        "严重": 15,

        "一般": 10,

        "轻微": 5

    }

    score["故障严重度"] = (

        data["严重等级"]

        .map(level_score)

        .fillna(0)

    )



    # 综合

    score["风险评分"]=(
        score[
            [
            "重复故障得分",
            "年龄风险",
            "故障严重度"
            ]
        ]

        .sum(axis=1)

    )


    score["风险等级"]=pd.cut(

        score["风险评分"],

        bins=[-1,30,45,60,100],

        labels=[

            "正常",

            "关注",

            "预警",

            "高风险"

        ]

    )



    result=pd.merge(

        data,

        score,

        on="设备编号",

        how="left"

    )


    result=(

        result

        .sort_values(

            "风险评分",

            ascending=False

        )

    )


    result.to_csv(

        STAT_PATH
        /
        "chronic_device_list.csv",

        index=False,

        encoding="utf-8-sig"

    )


    return result




# ==============================
# 6. 风险TOP10绘图
# ==============================


def plot_risk_top10(
        data
):


    top=data.head(10)


    plt.figure(
        figsize=(10,6)
    )


    plt.bar(

        top["设备编号"],

        top["风险评分"]

    )


    plt.xticks(
        rotation=45
    )


    plt.title(
        "慢性病设备风险TOP10"
    )


    plt.ylabel(
        "风险评分"
    )


    plt.tight_layout()


    plt.savefig(

        FIG_PATH
        /
        "chronic_device_risk.png",

        dpi=300

    )


    plt.close()




# ==============================
# 7. 自动生成报告
# ==============================


def generate_report(
        data
):


    report=f"""

# 故障规律分析报告


## 1. 故障重复性分析


重复故障设备数量：
{len(data)} 台


高风险设备数量：
{len(
data[data["风险等级"]=="高风险"]
)}
台



## 2. 慢性病设备特征


主要集中设备类型：

{data["设备类型"].value_counts().head(5).to_string()}



运行年限分布：

{data["年龄分组"].value_counts().to_string()}



## 3. 风险设备清单


Top10风险设备：

{data.head(10)[
[
"设备编号",
"设备类型",
"风险评分",
"风险等级"
]
].to_string(index=False)}



## 4. 运维建议


1. 高风险设备：
安排专项检修，必要时进行设备更换。


2. 重复故障设备：
开展故障根因分析，避免同类问题重复发生。


3. 老旧设备：
加强状态监测，提高巡检频率。


"""


    with open(

        REPORT_PATH
        /
        "故障规律分析报告.md",

        "w",

        encoding="utf-8"

    ) as f:

        f.write(report)




# ==============================
# 主程序
# ==============================


def main():


    fault, device, parameter = load_data()


    repeat = identify_repeat_fault(
        fault
    )


    if len(repeat)==0:

        print(
            "未发现90天重复故障设备"
        )

        return



    feature = analyze_device_feature(

        repeat,

        device,

        fault

    )


    feature = age_analysis(
        feature
    )


    chronic = operating_condition(

        feature,

        parameter

    )


    risk = build_chronic_score(

        chronic

    )


    plot_risk_top10(

        risk

    )


    generate_report(

        risk

    )


    print(
        "\nTask4完成"
    )



if __name__=="__main__":

    main()