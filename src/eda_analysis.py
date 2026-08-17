"""
电力设备运维数据EDA分析

任务4：
1.设备台账分析
2.运行参数趋势分析
3.故障工单分析
4.巡检记录分析

输出：
results/EDA/*.png
"""


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


# 中文显示设置

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei"
]

plt.rcParams["axes.unicode_minus"] = False


sns.set_theme(
    style="whitegrid",
    font="Microsoft YaHei"
)


class EDAAnalyzer:


    def __init__(self):

        self.input_file = (
            "../data/raw/"
            "电力设备运维数据_2023-2026.xlsx"
        )


        self.output_dir = (
            "../results/EDA"
        )


        os.makedirs(
            self.output_dir,
            exist_ok=True
        )


        self.data = pd.read_excel(
            self.input_file,
            sheet_name=None
        )



    def save_plot(self,name):

        plt.savefig(
            f"{self.output_dir}/{name}",
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

    def device_type_analysis(self):

        df=self.data["设备台账"]


        plt.figure(figsize=(8,5))


        sns.countplot(
            data=df,
            x="设备类型"
        )


        plt.xticks(
            rotation=45
        )


        plt.title(
            "设备类型数量分布"
        )


        self.save_plot(
            "01_设备类型分布.png"
        )

    def voltage_analysis(self):

        df=self.data["设备台账"]


        plt.figure(figsize=(8,5))


        sns.countplot(
            data=df,
            x="电压等级"
        )


        plt.title(
            "设备电压等级分布"
        )


        self.save_plot(
            "02_电压等级分布.png"
        )

    def substation_analysis(self):


        df=self.data["设备台账"]


        count=(

            df["所属变电站"]
            .value_counts()
            .head(15)

        )


        plt.figure(
            figsize=(10,5)
        )


        count.plot(
            kind="bar"
        )


        plt.title(
            "各变电站设备数量"
        )


        plt.xticks(
            rotation=45
        )


        self.save_plot(
            "03_变电站设备数量.png"
        )

    def load_rate_trend(self):
        df = self.data["运行参数"].copy()

        df["记录年月"] = pd.to_datetime(
            df["记录年月"]
        )

        trend = (
            df.groupby("记录年月")
            ["月平均负荷率"]
            .mean()
        )

        plt.figure(figsize=(12, 5))

        trend.plot()

        plt.title(
            "月平均负荷率变化趋势"
        )

        plt.xlabel(
            "时间"
        )

        plt.ylabel(
            "负荷率/%"
        )

        self.save_plot(
            "04_月平均负荷率趋势.png"
        )

    def temperature_box(self):
        df = self.data["运行参数"]

        temp_cols = [
            "环境温度（℃）",
            "油温（℃）",
            "绕组温度（℃）"
        ]

        plt.figure(figsize=(10, 5))

        df[temp_cols].boxplot()

        plt.title(
            "运行温度分布箱线图"
        )

        self.save_plot(
            "05_油温箱线图.png"
        )

    def insulation_box(self):
        df = self.data["运行参数"]

        plt.figure(figsize=(8, 5))

        sns.boxplot(
            y=df["绝缘电阻（MΩ）"]
        )

        plt.title(
            "绝缘电阻分布"
        )

        self.save_plot(
            "06_绝缘电阻箱线图.png"
        )

    def fault_type(self):

        df=self.data["故障工单"]


        plt.figure(
            figsize=(8,5)
        )


        sns.countplot(
            data=df,
            x="故障类型"
        )


        plt.xticks(
            rotation=45
        )


        plt.title(
            "故障类型分布"
        )


        self.save_plot(
            "07_故障类型分布.png"
        )

    # ===============================
    # 故障等级分布
    # ===============================

    def fault_level(self):

        df = self.data["故障工单"].copy()


        plt.figure(
            figsize=(8,5)
        )


        sns.countplot(
            data=df,
            x="严重等级",
            order=df["严重等级"]
            .value_counts()
            .index
        )


        plt.title(
            "故障严重等级分布"
        )


        plt.xlabel(
            "严重等级"
        )


        plt.ylabel(
            "故障数量"
        )


        plt.xticks(
            rotation=45
        )


        self.save_plot(
            "08_故障等级分布.png"
        )

    def fault_heatmap(self):
        df = self.data["故障工单"].copy()

        df["月份"] = pd.to_datetime(
            df["故障时间"]
        ).dt.month

        table = pd.crosstab(
            df["故障类型"],
            df["月份"]
        )

        plt.figure(figsize=(10, 6))

        sns.heatmap(
            table,
            annot=True,
            fmt="d"
        )

        plt.title(
            "故障类型月度热力图"
        )

        self.save_plot(
            "09_故障月度热力图.png"
        )

    def inspection_score(self):

        df=self.data["巡检记录"]


        plt.figure(
            figsize=(8,5)
        )


        sns.histplot(
            df["巡检评分"],
            bins=10
        )


        plt.title(
            "巡检评分分布"
        )


        self.save_plot(
            "10_巡检评分分布.png"
        )

    def defect_rate(self):
        df = self.data["巡检记录"]

        rate = (

            df["是否发现缺陷"]
            .value_counts(normalize=True)
        )

        plt.figure(figsize=(6, 5))

        rate.plot(
            kind="bar"
        )

        plt.title(
            "巡检缺陷发现比例"
        )

        self.save_plot(
            "11_缺陷发现率.png"
        )

if __name__=="__main__":


    eda=EDAAnalyzer()

    # 设备台账

    eda.device_type_analysis()

    eda.voltage_analysis()

    eda.substation_analysis()


    # 运行参数
    eda.load_rate_trend()

    eda.temperature_box()

    eda.insulation_box()


    # 故障工单

    eda.fault_type()

    eda.fault_level()

    eda.fault_heatmap()

    # 巡检记录

    eda.inspection_score()

    eda.defect_rate()


    print(
        "EDA分析完成"
    )