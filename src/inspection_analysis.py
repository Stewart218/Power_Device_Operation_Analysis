# -*- coding: utf-8 -*-

"""
电力设备运维分析项目
Week3 Task1：巡检管理分析

功能：
1. 月度巡检频次分析
2. 变电站巡检覆盖率分析
3. 巡检评分趋势分析
4. 缺陷发现率分析
5. 缺陷消除率分析
6. 缺陷类型分析
7. 缺陷-故障关联分析

输入：
data/raw/电力设备运维数据_2023-2026.xlsx

输出：
results/week3/inspection/
    ├── csv/
    ├── images/
    └── inspection_analysis_report.txt

"""


import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from datetime import timedelta



# ==============================
# 中文显示设置
# ==============================

plt.rcParams["font.sans-serif"] = [
    "SimHei"
]

plt.rcParams["axes.unicode_minus"] = False



# ==============================
# 路径配置
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent


DATA_PATH = (
    BASE_DIR
    /
    "data"
    /
    "raw"
    /
    "电力设备运维数据_2023-2026.xlsx"
)



RESULT_PATH = (
    BASE_DIR
    /
    "results"
    /
    "week3"
    /
    "inspection"
)


CSV_PATH = RESULT_PATH / "csv"

IMAGE_PATH = RESULT_PATH / "images"



# 创建目录

CSV_PATH.mkdir(
    parents=True,
    exist_ok=True
)


IMAGE_PATH.mkdir(
    parents=True,
    exist_ok=True
)




# ==============================
# 巡检分析类
# ==============================


class InspectionAnalyzer:


    def __init__(self):

        self.inspection = None

        self.device = None

        self.fault = None



    # ==========================
    # 数据读取
    # ==========================

    def load_data(self):

        print("读取数据...")


        excel = pd.ExcelFile(
            DATA_PATH
        )


        print(
            excel.sheet_names
        )


        self.inspection = pd.read_excel(
            DATA_PATH,
            sheet_name="巡检记录"
        )


        self.device = pd.read_excel(
            DATA_PATH,
            sheet_name="设备台账"
        )


        self.fault = pd.read_excel(
            DATA_PATH,
            sheet_name="故障工单"
        )


        print(
            "巡检记录:",
            self.inspection.shape
        )

        print(
            "设备台账:",
            self.device.shape
        )

        print(
            "故障工单:",
            self.fault.shape
        )



    # ==========================
    # 数据预处理
    # ==========================


    def preprocess(self):

        print("数据预处理...")


        # 日期转换

        self.inspection[
            "巡检日期"
        ] = pd.to_datetime(
            self.inspection[
                "巡检日期"
            ],
            errors="coerce"
        )


        self.fault[
            "故障时间"
        ] = pd.to_datetime(
            self.fault[
                "故障时间"
            ],
            errors="coerce"
        )



        # 去除无效设备编号


        self.inspection = (
            self.inspection
            [
                self.inspection[
                    "设备编号"
                ].notna()
            ]
        )


        self.device = (
            self.device
            [
                self.device[
                    "设备编号"
                ].notna()
            ]
        )


        self.fault = (
            self.fault
            [
                self.fault[
                    "设备编号"
                ].notna()
            ]
        )



        # 巡检月份

        self.inspection[
            "月份"
        ] = (
            self.inspection[
                "巡检日期"
            ]
            .dt
            .to_period("M")
            .astype(str)
        )



        print(
            "预处理完成"
        )



    # ==========================
    # 数据关联
    # ==========================


    def merge_device_info(self):

        self.inspection = self.inspection.merge(
            self.device[
                [
                    "设备编号",
                    "已运行年限",
                    "设计寿命（年）"
                ]
            ],
            on="设备编号",
            how="left"
        )



        print(
            "设备信息关联完成"
        )


    # ==========================
    # 1. 月度巡检频次分析
    # ==========================

    def monthly_inspection_analysis(self):

        print(
            "分析月度巡检频次..."
        )


        monthly = (
            self.inspection
            .groupby("月份")
            .size()
            .reset_index(
                name="巡检次数"
            )
        )


        monthly.to_csv(
            CSV_PATH /
            "monthly_inspection_statistics.csv",
            index=False,
            encoding="utf-8-sig"
        )


        return monthly



    # ==========================
    # 2. 变电站巡检覆盖率
    # ==========================


    def station_coverage_analysis(self):

        print(
            "分析变电站巡检覆盖率..."
        )


        # 每个变电站设备总数

        station_device = (
            self.device
            .groupby(
                "所属变电站"
            )
            [
                "设备编号"
            ]
            .nunique()
            .reset_index(
                name="设备总数"
            )
        )



        # 已巡检设备数量

        station_inspection = (
            self.inspection
            .groupby(
                "所属变电站"
            )
            [
                "设备编号"
            ]
            .nunique()
            .reset_index(
                name="已巡检设备数"
            )
        )


        result = (
            station_device
            .merge(
                station_inspection,
                on="所属变电站",
                how="left"
            )
        )


        result[
            "已巡检设备数"
        ] = (
            result[
                "已巡检设备数"
            ]
            .fillna(0)
        )



        result[
            "巡检覆盖率(%)"
        ] = (
            result[
                "已巡检设备数"
            ]
            /
            result[
                "设备总数"
            ]
            *
            100
        )



        result.to_csv(
            CSV_PATH /
            "station_inspection_coverage.csv",
            index=False,
            encoding="utf-8-sig"
        )


        return result



    # ==========================
    # 3. 巡检评分分析
    # ==========================


    def score_analysis(self):

        print(
            "分析巡检评分..."
        )


        score = (
            self.inspection
            .groupby(
                "设备编号"
            )
            [
                "巡检评分"
            ]
            .agg(
                [
                    "mean",
                    "min",
                    "max",
                    "count"
                ]
            )
            .reset_index()
        )


        score.columns = [
            "设备编号",
            "平均评分",
            "最低评分",
            "最高评分",
            "巡检次数"
        ]



        score = (
            score
            .merge(
                self.device[
                    [
                        "设备编号",
                        "设备类型",
                        "所属变电站"
                    ]
                ],
                on="设备编号",
                how="left"
            )
        )



        score.to_csv(
            CSV_PATH /
            "inspection_score_statistics.csv",
            index=False,
            encoding="utf-8-sig"
        )


        return score




    # ==========================
    # 4. 持续下降设备识别
    # ==========================


    def declining_device_analysis(self):

        print(
            "识别评分下降设备..."
        )


        decline_list = []


        temp = (
            self.inspection
            .sort_values(
                [
                    "设备编号",
                    "巡检日期"
                ]
            )
        )


        for device_id, group in temp.groupby(
            "设备编号"
        ):


            scores = (
                group[
                    "巡检评分"
                ]
                .dropna()
                .values
            )


            if len(scores) >= 3:


                # 连续下降

                if (
                    scores[-1]
                    <
                    scores[-2]
                    <
                    scores[-3]
                ):


                    decline_list.append(
                        [
                            device_id,
                            scores[-3],
                            scores[-2],
                            scores[-1]
                        ]
                    )



        result = pd.DataFrame(
            decline_list,
            columns=[
                "设备编号",
                "三次前评分",
                "两次前评分",
                "最近评分"
            ]
        )


        result.to_csv(
            CSV_PATH /
            "declining_score_devices.csv",
            index=False,
            encoding="utf-8-sig"
        )


        return result



    # ==========================
    # 5. 缺陷分析
    # ==========================


    def defect_analysis(self):

        print(
            "分析设备缺陷..."
        )


        # 发现缺陷记录

        defect = self.inspection[
            self.inspection["是否发现缺陷"] == "是"
            ].copy()



        # 缺陷类型统计


        defect_type = (
            defect
            .groupby(
                "缺陷类型"
            )
            .size()
            .reset_index(
                name="缺陷数量"
            )
            .sort_values(
                "缺陷数量",
                ascending=False
            )
        )



        defect_type.to_csv(
            CSV_PATH /
            "defect_statistics.csv",
            index=False,
            encoding="utf-8-sig"
        )



        # 缺陷发现率


        discovery_rate = {

            "巡检总次数":
                len(self.inspection),


            "发现缺陷次数":
                len(defect),


            "缺陷发现率(%)":
                len(defect)
                /
                len(self.inspection)
                *
                100

        }


        pd.DataFrame(
            [discovery_rate]
        ).to_csv(
            CSV_PATH /
            "defect_discovery_rate.csv",
            index=False,
            encoding="utf-8-sig"
        )



        return defect_type, defect



    # ==========================
    # 6. 缺陷消除分析
    # ==========================

    def defect_resolution_analysis(
            self,
            defect
    ):

        print(
            "分析缺陷消除情况..."
        )

        total = len(defect)

        # 已消除缺陷数量

        resolved = (
            defect[
                defect["缺陷处理状态"]
                ==
                "已消除"
                ]
            .shape[0]
        )

        # 处理中数量

        processing = (
            defect[
                defect["缺陷处理状态"]
                ==
                "处理中"
                ]
            .shape[0]
        )

        # 待处理数量

        pending = (
            defect[
                defect["缺陷处理状态"]
                ==
                "待处理"
                ]
            .shape[0]
        )

        result = pd.DataFrame(
            [
                {
                    "缺陷总数":
                        total,

                    "已消除数量":
                        resolved,

                    "处理中数量":
                        processing,

                    "待处理数量":
                        pending,

                    "缺陷消除率(%)":
                        resolved /
                        total *
                        100
                        if total > 0
                        else 0
                }
            ]
        )

        result.to_csv(
            CSV_PATH /
            "defect_resolution_statistics.csv",
            index=False,
            encoding="utf-8-sig"
        )

        return result




    # ==========================
    # 7. 缺陷-故障关联分析
    # ==========================


    def defect_fault_relation_analysis(
            self
    ):


        print(
            "分析缺陷转故障关系..."
        )


        defect_devices = (
            self.inspection
            [
                self.inspection[
                    "是否发现缺陷"
                ].notna()
            ]
            [
                [
                    "设备编号",
                    "巡检日期"
                ]
            ]
            .drop_duplicates()
        )



        results = []



        for _, row in defect_devices.iterrows():

            device_id = row[
                "设备编号"
            ]

            defect_date = row[
                "巡检日期"
            ]



            future_fault = self.fault[
                (
                    self.fault[
                        "设备编号"
                    ]
                    ==
                    device_id
                )
                &
                (
                    self.fault[
                        "故障时间"
                    ]
                    >
                    defect_date
                )
                &
                (
                    self.fault[
                        "故障时间"
                    ]
                    <=
                    defect_date
                    +
                    timedelta(days=90)
                )
            ]



            results.append(
                [
                    device_id,
                    defect_date,
                    1
                    if len(future_fault)>0
                    else 0
                ]
            )



        relation = pd.DataFrame(
            results,
            columns=[
                "设备编号",
                "缺陷发现日期",
                "90天内是否故障"
            ]
        )



        relation.to_csv(
            CSV_PATH /
            "defect_fault_relation.csv",
            index=False,
            encoding="utf-8-sig"
        )


        return relation

        # ==========================
        # 图1 月度巡检频次
        # ==========================

    def plot_monthly_frequency(
            self,
            monthly
    ):
        plt.figure(
            figsize=(10, 5)
        )

        plt.plot(
            monthly["月份"],
            monthly["巡检次数"],
            marker="o"
        )

        plt.xticks(
            rotation=45
        )

        plt.title(
            "月度巡检频次趋势"
        )

        plt.xlabel(
            "月份"
        )

        plt.ylabel(
            "巡检次数"
        )

        plt.tight_layout()

        plt.savefig(
            IMAGE_PATH /
            "monthly_inspection_frequency.png",
            dpi=300
        )

        plt.close()

    # ==========================
    # 图2 变电站覆盖率
    # ==========================

    def plot_station_coverage(
            self,
            coverage
    ):
        plt.figure(
            figsize=(10, 6)
        )

        temp = (
            coverage
            .sort_values(
                "巡检覆盖率(%)",
                ascending=False
            )
        )

        sns.barplot(
            data=temp,
            x="所属变电站",
            y="巡检覆盖率(%)"
        )

        plt.xticks(
            rotation=45
        )

        plt.title(
            "各变电站巡检覆盖率"
        )

        plt.tight_layout()

        plt.savefig(
            IMAGE_PATH /
            "station_inspection_coverage.png",
            dpi=300
        )

        plt.close()

    # ==========================
    # 图3 巡检评分分布
    # ==========================

    def plot_score_distribution(
            self,
            score
    ):
        plt.figure(
            figsize=(8, 5)
        )

        sns.histplot(
            score["平均评分"],
            bins=20,
            kde=True
        )

        plt.title(
            "设备巡检平均评分分布"
        )

        plt.xlabel(
            "平均巡检评分"
        )

        plt.ylabel(
            "设备数量"
        )

        plt.tight_layout()

        plt.savefig(
            IMAGE_PATH /
            "inspection_score_distribution.png",
            dpi=300
        )

        plt.close()

    # ==========================
    # 图4 巡检评分趋势
    # ==========================

    def plot_score_trend(
            self
    ):
        trend = (
            self.inspection
            .groupby(
                "月份"
            )
            [
                "巡检评分"
            ]
            .mean()
            .reset_index()
        )

        plt.figure(
            figsize=(10, 5)
        )

        plt.plot(
            trend["月份"],
            trend["巡检评分"],
            marker="o"
        )

        plt.xticks(
            rotation=45
        )

        plt.title(
            "月度平均巡检评分趋势"
        )

        plt.xlabel(
            "月份"
        )

        plt.ylabel(
            "平均评分"
        )

        plt.tight_layout()

        plt.savefig(
            IMAGE_PATH /
            "inspection_score_trend.png",
            dpi=300
        )

        plt.close()

    # ==========================
    # 图5 缺陷类型分布
    # ==========================

    def plot_defect_type(
            self,
            defect_type
    ):
        plt.figure(
            figsize=(8, 5)
        )

        sns.barplot(
            data=defect_type,
            x="缺陷类型",
            y="缺陷数量"
        )

        plt.xticks(
            rotation=45
        )

        plt.title(
            "设备缺陷类型分布"
        )

        plt.tight_layout()

        plt.savefig(
            IMAGE_PATH /
            "defect_type_distribution.png",
            dpi=300
        )

        plt.close()

    # ==========================
    # 图6 缺陷消除率
    # ==========================

    def plot_resolution_rate(
            self,
            resolution
    ):

        value = resolution.iloc[0]

        data = pd.DataFrame(
            {
                "状态":
                    [
                        "已消除",
                        "处理中",
                        "待处理"
                    ],

                "数量":
                    [
                        value["已消除数量"],
                        value["处理中数量"],
                        value["待处理数量"]
                    ]
            }
        )

        plt.figure(
            figsize=(7, 5)
        )

        sns.barplot(
            data=data,
            x="状态",
            y="数量"
        )

        plt.title(
            "设备缺陷处理状态分布"
        )

        plt.xlabel(
            "处理状态"
        )

        plt.ylabel(
            "缺陷数量"
        )

        plt.tight_layout()

        plt.savefig(
            IMAGE_PATH /
            "defect_resolution_status.png",
            dpi=300
        )

        plt.close()

    # ==========================
    # 图7 缺陷转故障
    # ==========================

    def plot_defect_fault_conversion(
            self,
            relation
    ):
        result = (
            relation
            [
                "90天内是否故障"
            ]
            .value_counts()
            .rename(
                {
                    0: "未转化",
                    1: "转化故障"
                }
            )
        )

        plt.figure(
            figsize=(6, 5)
        )

        sns.barplot(
            x=result.index,
            y=result.values
        )

        plt.ylabel(
            "设备数量"
        )

        plt.title(
            "巡检缺陷90天故障转化分析"
        )

        plt.tight_layout()

        plt.savefig(
            IMAGE_PATH /
            "defect_fault_conversion.png",
            dpi=300
        )

        plt.close()

    # ==========================
    # 自动生成分析报告
    # ==========================

    def generate_report(
            self,
            monthly,
            coverage,
            resolution,
            relation
    ):
        report_path = (
                RESULT_PATH /
                "inspection_analysis_report.txt"
        )

        with open(
                report_path,
                "w",
                encoding="utf-8"
        ) as f:
            f.write(
                "电力设备运维分析 Week3 Task1\n"
            )

            f.write(
                "巡检管理分析报告\n\n"
            )

            f.write(
                "1. 巡检频次分析\n"
            )

            f.write(
                f"累计巡检次数：{len(self.inspection)}\n"
            )

            f.write(
                f"覆盖月份数量：{monthly.shape[0]}\n\n"
            )

            f.write(
                "2. 巡检覆盖率分析\n"
            )

            f.write(
                f"平均覆盖率："
                f"{coverage['巡检覆盖率(%)'].mean():.2f}%\n\n"
            )

            f.write(
                "3. 缺陷管理分析\n"
            )

            f.write(
                f"缺陷总数："
                f"{resolution.iloc[0]['缺陷总数']}\n"
            )

            f.write(
                f"缺陷消除率："
                f"{resolution.iloc[0]['缺陷消除率(%)']:.2f}%\n\n"
            )

            conversion = (
                    relation[
                        "90天内是否故障"
                    ]
                    .mean()
                    *
                    100
            )

            f.write(
                "4. 缺陷转故障分析\n"
            )

            f.write(
                f"90天缺陷故障转化率："
                f"{conversion:.2f}%\n"
            )

        print(
            "报告生成完成:"
        )

        print(
            report_path
        )

# ==============================
# 主函数
# ==============================


def main():

    analyzer = InspectionAnalyzer()

    analyzer.load_data()

    analyzer.preprocess()

    analyzer.merge_device_info()

    # 数据分析

    monthly = (
        analyzer
        .monthly_inspection_analysis()
    )

    coverage = (
        analyzer
        .station_coverage_analysis()
    )

    score = (
        analyzer
        .score_analysis()
    )

    analyzer.declining_device_analysis()

    defect_type, defect = (
        analyzer
        .defect_analysis()
    )

    resolution = (
        analyzer
        .defect_resolution_analysis(
            defect
        )
    )

    relation = (
        analyzer
        .defect_fault_relation_analysis()
    )

    # 绘图

    analyzer.plot_monthly_frequency(
        monthly
    )

    analyzer.plot_station_coverage(
        coverage
    )

    analyzer.plot_score_distribution(
        score
    )

    analyzer.plot_score_trend()

    analyzer.plot_defect_type(
        defect_type
    )

    analyzer.plot_resolution_rate(
        resolution
    )

    analyzer.plot_defect_fault_conversion(
        relation
    )

    analyzer.generate_report(
        monthly,
        coverage,
        resolution,
        relation
    )

    print(
        "\nWeek3 Task1 巡检管理分析完成!"
    )

if __name__ == "__main__":
    main()