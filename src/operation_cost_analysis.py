# -*- coding: utf-8 -*-

"""
运维成本分析

Task4:
1. 汇总故障抢修成本、计划检修成本、备件消耗成本
2. 按设备类型、变电站分析成本构成
3. 计算单台设备年均运维成本
4. 分析成本趋势和异常增长点


输入：
电力设备运维数据_2023-2026.xlsx


输出：

results/week3/

    operation_cost_csv/

    operation_cost_figures/

"""


import pandas as pd

import numpy as np

from pathlib import Path

import matplotlib.pyplot as plt



# ==========================================================
# 路径配置
# ==========================================================


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

    "week3"

    /

    "operation_cost"

)



CSV_PATH = (

    RESULT_PATH

    /

    "csv"

)



FIGURE_PATH = (

    RESULT_PATH

    /

    "figures"

)



CSV_PATH.mkdir(

    parents=True,

    exist_ok=True

)


FIGURE_PATH.mkdir(

    parents=True,

    exist_ok=True

)



# ==========================================================
# matplotlib设置
# ==========================================================


plt.rcParams[

    "font.sans-serif"

] = [

    "SimHei"

]


plt.rcParams[

    "axes.unicode_minus"

] = False





# ==========================================================
# 运维成本分析类
# ==========================================================


class OperationCostAnalyzer:


    def __init__(self):


        self.fault = None


        self.maintenance = None


        self.spare_parts = None


        self.device = None





    # ======================================================
    # 数据读取
    # ======================================================


    def load_data(self):


        print(

            "读取数据..."

        )



        excel = pd.ExcelFile(

            DATA_PATH

        )



        print(

            excel.sheet_names

        )



        self.fault = pd.read_excel(

            DATA_PATH,

            sheet_name="故障工单"

        )



        self.maintenance = pd.read_excel(

            DATA_PATH,

            sheet_name="检修计划"

        )



        self.spare_parts = pd.read_excel(

            DATA_PATH,

            sheet_name="备品备件"

        )



        self.device = pd.read_excel(

            DATA_PATH,

            sheet_name="设备台账"

        )



        print(

            "故障工单:",

            self.fault.shape

        )


        print(

            "检修计划:",

            self.maintenance.shape

        )


        print(

            "备品备件:",

            self.spare_parts.shape

        )


        print(

            "设备台账:",

            self.device.shape

        )






    # ======================================================
    # 数据预处理
    # ======================================================


    def preprocess(self):


        print(

            "数据预处理..."

        )



        # -------------------------
        # 日期处理
        # -------------------------


        if "故障时间" in self.fault.columns:


            self.fault[

                "故障时间"

            ] = pd.to_datetime(

                self.fault[

                    "故障时间"

                ],

                errors="coerce"

            )



        if "实际日期" in self.maintenance.columns:


            self.maintenance[

                "实际日期"

            ] = pd.to_datetime(

                self.maintenance[

                    "实际日期"

                ],

                errors="coerce"

            )



        if "记录年月" in self.spare_parts.columns:


            self.spare_parts[

                "记录年月"

            ] = pd.to_datetime(

                self.spare_parts[

                    "记录年月"

                ],

                format="%Y-%m",

                errors="coerce"

            )




        # -------------------------
        # 金额字段转换
        # -------------------------


        money_columns = [


            "修复费用（万元）"

        ]



        for col in money_columns:


            if col in self.fault.columns:


                self.fault[col] = pd.to_numeric(

                    self.fault[col],

                    errors="coerce"

                ).fillna(0)



        if "检修费用（万元）" in self.maintenance.columns:


            self.maintenance[

                "检修费用（万元）"

            ] = pd.to_numeric(

                self.maintenance[

                    "检修费用（万元）"

                ],

                errors="coerce"

            ).fillna(0)




        if "消耗金额（万元）" in self.spare_parts.columns:


            self.spare_parts[

                "消耗金额（万元）"

            ] = pd.to_numeric(

                self.spare_parts[

                    "消耗金额（万元）"

                ],

                errors="coerce"

            ).fillna(0)




        print(

            "预处理完成"

        )

    # ======================================================
    # 1. 故障抢修成本分析
    # ======================================================


    def fault_cost_analysis(self):


        print(
            "分析故障抢修成本..."
        )



        data = self.fault.copy()



        data["年份"] = (

            data["故障时间"]

            .dt.year

        )



        data["月份"] = (

            data["故障时间"]

            .dt.to_period("M")

            .dt.to_timestamp()

        )



        # 年度统计

        annual = (

            data

            .groupby("年份")

            [

                "修复费用（万元）"

            ]

            .sum()

            .reset_index()

        )


        annual.rename(

            columns={

                "修复费用（万元）":

                "故障抢修成本"

            },

            inplace=True

        )



        # 月度统计

        monthly = (

            data

            .groupby("月份")

            [

                "修复费用（万元）"

            ]

            .sum()

            .reset_index()

        )



        monthly.rename(

            columns={

                "修复费用（万元）":

                "故障抢修成本"

            },

            inplace=True

        )



        annual.to_csv(

            CSV_PATH /

            "fault_cost_annual.csv",

            index=False,

            encoding="utf-8-sig"

        )



        monthly.to_csv(

            CSV_PATH /

            "fault_cost_monthly.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return annual, monthly





    # ======================================================
    # 2. 计划检修成本分析
    # ======================================================


    def maintenance_cost_analysis(self):


        print(

            "分析计划检修成本..."

        )



        data = self.maintenance.copy()



        data["年份"] = (

            data["实际日期"]

            .dt.year

        )



        data["月份"] = (

            data["实际日期"]

            .dt.to_period("M")

            .dt.to_timestamp()

        )



        annual = (

            data

            .groupby("年份")

            [

                "检修费用（万元）"

            ]

            .sum()

            .reset_index()

        )


        annual.rename(

            columns={

                "检修费用（万元）":

                "计划检修成本"

            },

            inplace=True

        )



        monthly = (

            data

            .groupby("月份")

            [

                "检修费用（万元）"

            ]

            .sum()

            .reset_index()

        )


        monthly.rename(

            columns={

                "检修费用（万元）":

                "计划检修成本"

            },

            inplace=True

        )



        annual.to_csv(

            CSV_PATH /

            "maintenance_cost_annual.csv",

            index=False,

            encoding="utf-8-sig"

        )



        monthly.to_csv(

            CSV_PATH /

            "maintenance_cost_monthly.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return annual, monthly





    # ======================================================
    # 3. 备件消耗成本分析
    # ======================================================


    def spare_cost_analysis(self):


        print(

            "分析备件消耗成本..."

        )



        data = self.spare_parts.copy()



        data["年份"] = (

            data["记录年月"]

            .dt.year

        )



        annual = (

            data

            .groupby("年份")

            [

                "消耗金额（万元）"

            ]

            .sum()

            .reset_index()

        )



        annual.rename(

            columns={

                "消耗金额（万元）":

                "备件消耗成本"

            },

            inplace=True

        )



        monthly = (

            data

            .groupby("记录年月")

            [

                "消耗金额（万元）"

            ]

            .sum()

            .reset_index()

        )



        monthly.rename(

            columns={

                "记录年月":

                "月份",

                "消耗金额（万元）":

                "备件消耗成本"

            },

            inplace=True

        )



        annual.to_csv(

            CSV_PATH /

            "spare_cost_annual.csv",

            index=False,

            encoding="utf-8-sig"

        )



        monthly.to_csv(

            CSV_PATH /

            "spare_cost_monthly.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return annual, monthly





    # ======================================================
    # 4. 运维总成本汇总
    # ======================================================


    def total_cost_analysis(self):


        print(

            "汇总年度运维成本..."

        )


        fault, _ = (

            self.fault_cost_analysis()

        )


        maintenance, _ = (

            self.maintenance_cost_analysis()

        )


        spare, _ = (

            self.spare_cost_analysis()

        )



        total = (

            fault

            .merge(

                maintenance,

                on="年份",

                how="outer"

            )

            .merge(

                spare,

                on="年份",

                how="outer"

            )

        )



        total.fillna(

            0,

            inplace=True

        )



        total["年度总运维成本"] = (

            total["故障抢修成本"]

            +

            total["计划检修成本"]

            +

            total["备件消耗成本"]

        )



        total.to_csv(

            CSV_PATH /

            "annual_cost_summary.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return total





    # ======================================================
    # 5. 月度运维成本趋势
    # ======================================================


    def monthly_cost_trend_analysis(self):


        print(

            "分析月度成本趋势..."

        )



        fault_month = (

            self.fault

            .assign(

                月份=lambda x:

                x["故障时间"]

                .dt.to_period("M")

                .dt.to_timestamp()

            )

            .groupby("月份")

            [

                "修复费用（万元）"

            ]

            .sum()

            .rename(

                "故障抢修成本"

            )

        )



        maintenance_month = (

            self.maintenance

            .assign(

                月份=lambda x:

                x["实际日期"]

                .dt.to_period("M")

                .dt.to_timestamp()

            )

            .groupby("月份")

            [

                "检修费用（万元）"

            ]

            .sum()

            .rename(

                "计划检修成本"

            )

        )



        spare_month = (

            self.spare_parts

            .groupby(

                "记录年月"

            )

            [

                "消耗金额（万元）"

            ]

            .sum()

            .rename(

                "备件消耗成本"

            )

        )



        trend = pd.concat(

            [

                fault_month,

                maintenance_month,

                spare_month

            ],

            axis=1

        )



        trend.fillna(

            0,

            inplace=True

        )


        trend["总成本"] = (

            trend["故障抢修成本"]

            +

            trend["计划检修成本"]

            +

            trend["备件消耗成本"]

        )



        trend.reset_index(

            inplace=True

        )


        trend.rename(

            columns={

                "index":

                "月份"

            },

            inplace=True

        )



        trend.to_csv(

            CSV_PATH /

            "monthly_cost_trend.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return trend

    # ======================================================
    # 6. 设备类型成本分析
    # ======================================================


    def equipment_type_cost_analysis(self):


        print(

            "分析设备类型成本..."

        )



        # ============================
        # 故障成本
        # ============================


        fault_cost = (

            self.fault

            .groupby(

                "设备类型"

            )

            [

                "修复费用（万元）"

            ]

            .sum()

            .reset_index()

        )


        fault_cost.rename(

            columns={

                "修复费用（万元）":

                "故障抢修成本"

            },

            inplace=True

        )



        # ============================
        # 检修成本
        # ============================


        maintenance_cost = (

            self.maintenance

            .groupby(

                "设备类型"

            )

            [

                "检修费用（万元）"

            ]

            .sum()

            .reset_index()

        )



        maintenance_cost.rename(

            columns={

                "检修费用（万元）":

                "计划检修成本"

            },

            inplace=True

        )



        # ============================
        # 备件成本
        # ============================


        spare_cost = (

            self.spare_parts

            .groupby(

                "设备类型"

            )

            [

                "消耗金额（万元）"

            ]

            .sum()

            .reset_index()

        )


        spare_cost.rename(

            columns={

                "消耗金额（万元）":

                "备件消耗成本"

            },

            inplace=True

        )



        # ============================
        # 合并
        # ============================


        result = (

            fault_cost

            .merge(

                maintenance_cost,

                on="设备类型",

                how="outer"

            )

            .merge(

                spare_cost,

                on="设备类型",

                how="outer"

            )

        )


        result.fillna(

            0,

            inplace=True

        )



        result["总运维成本"] = (

            result["故障抢修成本"]

            +

            result["计划检修成本"]

            +

            result["备件消耗成本"]

        )



        result.sort_values(

            "总运维成本",

            ascending=False,

            inplace=True

        )



        result.to_csv(

            CSV_PATH /

            "equipment_type_cost.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return result

    # ======================================================
    # 7. 变电站成本分析
    # ======================================================


    def station_cost_analysis(self):


        print(

            "分析变电站成本..."

        )



        fault = (

            self.fault

            .groupby(

                "所属变电站"

            )

            [

                "修复费用（万元）"

            ]

            .sum()

            .reset_index()

        )



        fault.rename(

            columns={

                "修复费用（万元）":

                "故障抢修成本"

            },

            inplace=True

        )



        maintenance = (

            self.maintenance

            .groupby(

                "所属变电站"

            )

            [

                "检修费用（万元）"

            ]

            .sum()

            .reset_index()

        )


        maintenance.rename(

            columns={

                "检修费用（万元）":

                "计划检修成本"

            },

            inplace=True

        )



        result = (

            fault

            .merge(

                maintenance,

                on="所属变电站",

                how="outer"

            )

        )


        result.fillna(

            0,

            inplace=True

        )



        result["变电站运维成本"] = (

            result["故障抢修成本"]

            +

            result["计划检修成本"]

        )



        result.sort_values(

            "变电站运维成本",

            ascending=False,

            inplace=True

        )



        result.to_csv(

            CSV_PATH /

            "station_cost.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return result

    # ======================================================
    # 8. 单台设备年均成本
    # ======================================================


    def equipment_average_cost_analysis(self):


        print(

            "计算单台设备年均成本..."

        )



        total_cost = (

            self.total_cost_analysis()

        )



        # 总设备数量

        device_count = (

            self.device

            [

                "设备编号"

            ]

            .nunique()

        )



        result = total_cost.copy()



        result["设备数量"] = (

            device_count

        )



        result["单台设备年均运维成本"] = (

            result["年度总运维成本"]

            /

            device_count

        )



        result.to_csv(

            CSV_PATH /

            "equipment_average_cost.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return result

    # ======================================================
    # 9. 行业基准对比
    # ======================================================


    def benchmark_compare(
            self,
            benchmark=5
    ):


        print(

            "进行行业基准对比..."

        )



        data = (

            self.equipment_average_cost_analysis()

        )



        data["行业基准(万元/台年)"] = (

            benchmark

        )



        data["成本评价"] = np.where(

            data["单台设备年均运维成本"]

            >

            benchmark,

            "高于行业基准",

            "低于行业基准"

        )



        data.to_csv(

            CSV_PATH /

            "benchmark_compare.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return data


    # ======================================================
    # 10. 成本异常增长识别
    # ======================================================


    def abnormal_cost_growth_analysis(
            self
    ):


        print(

            "识别成本异常增长..."

        )



        data = (

            self.monthly_cost_trend_analysis()

        )



        data["成本环比增长率"] = (

            data["总成本"]

            .pct_change()

            *

            100

        )



        abnormal = (

            data

            [

                data["成本环比增长率"]

                >

                50

            ]

            .copy()

        )



        abnormal.to_csv(

            CSV_PATH /

            "abnormal_cost_growth.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return abnormal

    # ======================================================
    # 11. 成本构成饼图
    # ======================================================


    def plot_cost_structure(
            self,
            data
    ):


        print(
            "绘制成本构成图..."
        )



        values = [

            data["故障抢修成本"].sum(),

            data["计划检修成本"].sum(),

            data["备件消耗成本"].sum()

        ]



        labels = [

            "故障抢修成本",

            "计划检修成本",

            "备件消耗成本"

        ]



        plt.figure(

            figsize=(7,7)

        )


        plt.pie(

            values,

            labels=labels,

            autopct="%1.1f%%"

        )


        plt.title(

            "运维成本构成分析"

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH /

            "cost_structure_pie.png",

            dpi=300

        )


        plt.close()

    # ======================================================
    # 12. 月度成本趋势图
    # ======================================================


    def plot_monthly_cost_trend(
            self,
            data
    ):


        print(

            "绘制月度成本趋势..."

        )



        plt.figure(

            figsize=(12,5)

        )



        plt.plot(

            data["月份"],

            data["故障抢修成本"],

            marker="o",

            label="故障抢修"

        )


        plt.plot(

            data["月份"],

            data["计划检修成本"],

            marker="o",

            label="计划检修"

        )


        plt.plot(

            data["月份"],

            data["备件消耗成本"],

            marker="o",

            label="备件消耗"

        )


        plt.plot(

            data["月份"],

            data["总成本"],

            linewidth=2,

            label="总成本"

        )



        plt.title(

            "月度运维成本趋势"

        )


        plt.xlabel(

            "月份"

        )


        plt.ylabel(

            "成本（万元）"

        )


        plt.xticks(

            rotation=45

        )


        plt.legend()



        plt.grid(

            alpha=0.3

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH /

            "monthly_cost_trend.png",

            dpi=300

        )


        plt.close()

    # ======================================================
    # 13. 设备类型成本分析图
    # ======================================================


    def plot_equipment_type_cost(
            self,
            data
    ):


        print(

            "绘制设备类型成本..."

        )



        data = (

            data

            .head(10)

        )



        plt.figure(

            figsize=(10,6)

        )


        plt.bar(

            data["设备类型"],

            data["总运维成本"]

        )



        plt.title(

            "设备类型运维成本Top10"

        )


        plt.xlabel(

            "设备类型"

        )


        plt.ylabel(

            "成本（万元）"

        )


        plt.xticks(

            rotation=45

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH /

            "equipment_type_cost.png",

            dpi=300

        )


        plt.close()


    # ======================================================
    # 14. 变电站成本Top10
    # ======================================================


    def plot_station_cost(
            self,
            data
    ):


        print(

            "绘制变电站成本..."

        )



        top10 = (

            data

            .head(10)

        )



        plt.figure(

            figsize=(10,6)

        )


        plt.barh(

            top10["所属变电站"],

            top10["变电站运维成本"]

        )


        plt.title(

            "变电站运维成本Top10"

        )


        plt.xlabel(

            "成本（万元）"

        )


        plt.ylabel(

            "变电站"

        )


        plt.gca().invert_yaxis()



        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH /

            "station_cost_top10.png",

            dpi=300

        )


        plt.close()

    # ======================================================
    # 15. 异常增长分析图
    # ======================================================


    def plot_abnormal_growth(
            self,
            data
    ):


        print(

            "绘制异常增长点..."

        )


        if len(data) == 0:


            print(

                "无异常增长月份"

            )


            return




        plt.figure(

            figsize=(8,5)

        )


        plt.bar(

            data["月份"].astype(str),

            data["成本环比增长率"]

        )


        plt.axhline(

            50,

            linestyle="--"

        )


        plt.title(

            "运维成本异常增长点"

        )


        plt.xlabel(

            "月份"

        )


        plt.ylabel(

            "环比增长率(%)"

        )


        plt.xticks(

            rotation=45

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH /

            "abnormal_growth.png",

            dpi=300

        )


        plt.close()

def main():


    analyzer = OperationCostAnalyzer()



    # ===============================
    # 数据读取
    # ===============================


    analyzer.load_data()



    analyzer.preprocess()



    # ===============================
    # 成本分析
    # ===============================


    annual_cost = (

        analyzer

        .total_cost_analysis()

    )



    monthly_cost = (

        analyzer

        .monthly_cost_trend_analysis()

    )



    equipment_type = (

        analyzer

        .equipment_type_cost_analysis()

    )



    station_cost = (

        analyzer

        .station_cost_analysis()

    )



    average_cost = (

        analyzer

        .equipment_average_cost_analysis()

    )



    benchmark = (

        analyzer

        .benchmark_compare(

            benchmark=5

        )

    )



    abnormal = (

        analyzer

        .abnormal_cost_growth_analysis()

    )



    # ===============================
    # 绘图
    # ===============================


    analyzer.plot_cost_structure(

        annual_cost

    )



    analyzer.plot_monthly_cost_trend(

        monthly_cost

    )



    analyzer.plot_equipment_type_cost(

        equipment_type

    )



    analyzer.plot_station_cost(

        station_cost

    )



    analyzer.plot_abnormal_growth(

        abnormal

    )



    print(

        "\n运维成本分析完成!"

    )


    print(

        "结果保存：",

        RESULT_PATH

    )




if __name__ == "__main__":


    main()