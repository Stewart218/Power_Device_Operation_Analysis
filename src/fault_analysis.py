"""
电力设备运维与故障分析项目

Week2 Task1:
故障多维统计分析

功能：
1. 故障工单与设备台账关联
2. 设备类型/电压等级/变电站交叉统计
3. 故障时间趋势分析
4. 故障类型Pareto分析
5. 故障原因分布分析

Author:
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


# ==============================
# 路径配置
# ==============================

ROOT = Path(__file__).resolve().parent.parent


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


FIG_PATH = RESULT_PATH / "figures" / "fault"

CSV_PATH = RESULT_PATH / "statistics" / "fault"


FIG_PATH.mkdir(
    parents=True,
    exist_ok=True
)

CSV_PATH.mkdir(
    parents=True,
    exist_ok=True
)



# ==============================
# 数据分析类
# ==============================


class FaultAnalyzer:


    def __init__(self):

        self.fault_df = None

        self.device_df = None

        self.data = None

    # ==============================
    # 故障原因大类映射
    # ==============================

    FAULT_REASON_MAPPING = {

        # 设备缺陷
        "绝缘老化": "设备缺陷",
        "机械故障": "设备缺陷",

        # 外力破坏
        "人为误操作": "外力破坏",
        "鸟害": "外力破坏",

        # 自然灾害
        "雷击": "自然灾害",

        # 过负荷
        "过载运行": "过负荷"

    }

    # --------------------------
    # 数据读取
    # --------------------------

    def load_data(self):

        print("正在读取数据...")


        self.fault_df = pd.read_excel(
            DATA_PATH,
            sheet_name="故障工单"
        )


        self.device_df = pd.read_excel(
            DATA_PATH,
            sheet_name="设备台账"
        )


        print(
            "故障记录:",
            len(self.fault_df)
        )


        print(
            "设备记录:",
            len(self.device_df)
        )



    # --------------------------
    # 数据关联
    # --------------------------

    def merge_data(self):


        print(
            "正在关联设备信息..."
        )


        self.data = self.fault_df.merge(
            self.device_df[
                [
                    "设备编号",
                    "电压等级",
                    "所属区域",
                    "制造商",
                    "已运行年限"
                ]
            ],
            on="设备编号",
            how="left"
        )


        match_rate = (
            self.data["电压等级"]
            .notna()
            .mean()
        )


        print(
            f"设备关联成功率:{match_rate:.2%}"
        )



    # --------------------------
    # 1.设备维度统计
    # --------------------------

    def device_statistics(self):


        print(
            "设备维度统计..."
        )


        # 设备类型

        device_type = (
            self.data
            .groupby("设备类型")
            .size()
            .sort_values(
                ascending=False
            )
        )


        device_type.to_csv(
            CSV_PATH /
            "fault_by_device_type.csv",
            encoding="utf-8-sig"
        )


        plt.figure(
            figsize=(8,5)
        )


        sns.barplot(
            x=device_type.index,
            y=device_type.values
        )


        plt.xticks(
            rotation=45
        )


        plt.title(
            "Fault Distribution by Device Type"
        )


        plt.ylabel(
            "Fault Count"
        )


        plt.tight_layout()


        plt.savefig(
            FIG_PATH /
            "fault_device_type.png",
            dpi=300
        )


        plt.close()



    # --------------------------
    # 电压等级分析
    # --------------------------

    def voltage_statistics(self):


        voltage = (
            self.data
            .groupby("电压等级")
            .size()
            .sort_values(
                ascending=False
            )
        )


        voltage.to_csv(
            CSV_PATH /
            "fault_by_voltage.csv",
            encoding="utf-8-sig"
        )


        plt.figure(
            figsize=(7,5)
        )


        sns.barplot(
            x=voltage.index,
            y=voltage.values
        )


        plt.title(
            "Fault Distribution by Voltage Level"
        )


        plt.tight_layout()


        plt.savefig(
            FIG_PATH /
            "fault_voltage_level.png",
            dpi=300
        )


        plt.close()



    # --------------------------
    # 变电站Top10
    # --------------------------

    def station_statistics(self):


        station = (
            self.data
            .groupby("所属变电站")
            .size()
            .sort_values(
                ascending=False
            )
            .head(10)
        )


        station.to_csv(
            CSV_PATH /
            "fault_by_station.csv",
            encoding="utf-8-sig"
        )


        plt.figure(
            figsize=(10,5)
        )


        sns.barplot(
            y=station.index,
            x=station.values
        )


        plt.title(
            "Top10 Fault Stations"
        )


        plt.xlabel(
            "Fault Count"
        )


        plt.tight_layout()


        plt.savefig(
            FIG_PATH /
            "fault_station_top10.png",
            dpi=300
        )


        plt.close()



    # --------------------------
    # 时间趋势
    # --------------------------

    def time_analysis(self):


        self.data["故障时间"] = pd.to_datetime(
            self.data["故障时间"]
        )


        self.data["月份"] = (
            self.data["故障时间"]
            .dt.to_period("M")
            .astype(str)
        )


        monthly = (
            self.data
            .groupby("月份")
            .size()
        )


        monthly.to_csv(
            CSV_PATH /
            "fault_monthly.csv",
            encoding="utf-8-sig"
        )


        plt.figure(
            figsize=(12,5)
        )


        monthly.plot()


        plt.title(
            "Monthly Fault Trend"
        )


        plt.ylabel(
            "Fault Count"
        )


        plt.grid()


        plt.tight_layout()


        plt.savefig(
            FIG_PATH /
            "fault_monthly_trend.png",
            dpi=300
        )


        plt.close()



        # 季度

        self.data["季度"] = (
            self.data["故障时间"]
            .dt.to_period("Q")
            .astype(str)
        )


        quarterly = (
            self.data
            .groupby("季度")
            .size()
        )


        quarterly.to_csv(
            CSV_PATH /
            "fault_quarterly.csv",
            encoding="utf-8-sig"
        )



    # --------------------------
    # Pareto分析
    # --------------------------

    def pareto_analysis(self):


        fault_type = (
            self.data
            .groupby("故障类型")
            .size()
            .sort_values(
                ascending=False
            )
        )


        percent = (
            fault_type /
            fault_type.sum()
        )


        cumulative = (
            percent.cumsum()
        )



        fig, ax1 = plt.subplots(
            figsize=(10,6)
        )


        ax1.bar(
            fault_type.index,
            fault_type.values
        )


        ax1.set_ylabel(
            "Fault Count"
        )


        ax1.tick_params(
            axis="x",
            rotation=45
        )


        ax2 = ax1.twinx()


        ax2.plot(
            cumulative.index,
            cumulative.values,
            marker="o"
        )


        ax2.axhline(
            0.8,
            linestyle="--"
        )


        ax2.set_ylabel(
            "Cumulative Percentage"
        )


        plt.title(
            "Fault Type Pareto Analysis"
        )


        plt.tight_layout()


        plt.savefig(
            FIG_PATH /
            "fault_type_pareto.png",
            dpi=300
        )


        plt.close()



    # --------------------------
    # 故障原因
    # --------------------------

    def reason_analysis(self):
        print("故障原因成因分析...")

        # ==============================
        # 故障原因大类映射
        # ==============================

        # ==============================
        # 故障原因大类映射
        # ==============================

        reason_mapping = {

            # ======================
            # 设备老化与绝缘缺陷
            # ======================

            "绝缘击穿": "设备老化与绝缘缺陷",
            "绝缘故障": "设备老化与绝缘缺陷",
            "绝缘老化": "设备老化与绝缘缺陷",
            "局部放电": "设备老化与绝缘缺陷",

            # ======================
            # 机械结构与部件故障
            # ======================

            "机械故障": "机械结构与部件故障",
            "密封失效": "机械结构与部件故障",
            "鼓肚渗油": "机械结构与部件故障",
            "阀片劣化": "机械结构与部件故障",
            "瓷套破裂": "机械结构与部件故障",

            # ======================
            # 运行异常与热故障
            # ======================

            "过热故障": "运行异常与热故障",
            "油系统故障": "运行异常与热故障",

            # ======================
            # 保护与控制异常
            # ======================

            "保护动作": "保护与控制异常",
            "拒动/误动": "保护与控制异常",
            "接线故障": "保护与控制异常",

            # ======================
            # 外部环境与人为因素
            # ======================

            "外力因素": "外部环境与人为因素",
            "接触不良": "外部环境与人为因素",

            # ======================
            # 系统运行工况异常
            # ======================

            "接地故障": "系统运行工况异常",

        }

        # 创建故障原因大类字段

        self.data["故障原因大类"] = (
            self.data["故障类型"]
            .map(reason_mapping)
            .fillna("其他原因")
        )

        # ==============================
        # 按大类统计
        # ==============================

        reason_category = (

            self.data
            .groupby("故障原因大类")
            .size()
            .sort_values(
                ascending=False
            )

        )

        print(reason_category)

        # 保存统计结果

        reason_category.to_csv(

            CSV_PATH /
            "fault_reason_category_statistics.csv",

            encoding="utf-8-sig"

        )

        # ==============================
        # 绘制故障原因分类柱状图
        # ==============================

        plt.figure(
            figsize=(8, 5)
        )

        sns.barplot(

            x=reason_category.values,

            y=reason_category.index

        )

        plt.title(
            "故障原因成因分类分布"
        )

        plt.xlabel(
            "故障次数"
        )

        plt.ylabel(
            "故障原因类别"
        )

        # 添加数值标签

        for i, value in enumerate(reason_category.values):
            plt.text(

                value + 1,

                i,

                str(value),

                va="center"

            )

        plt.tight_layout()

        plt.savefig(

            FIG_PATH /
            "fault_reason_category_distribution.png",

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()



    # --------------------------
    # 总运行
    # --------------------------

    def run(self):


        self.load_data()

        self.merge_data()

        self.device_statistics()

        self.voltage_statistics()

        self.station_statistics()

        self.time_analysis()

        self.pareto_analysis()

        self.reason_analysis()


        print(
            "Week2 Task1完成!"
        )



if __name__ == "__main__":


    analyzer = FaultAnalyzer()

    analyzer.run()