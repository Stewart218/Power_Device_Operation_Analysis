# -*- coding: utf-8 -*-

"""
备品备件消耗与库存分析

功能：
1. 备件月度消耗趋势分析
2. 年度消耗统计
3. 库存周转率计算
4. 积压/短缺备件识别
5. ABC分类分析
6. 备件消耗与故障、检修关联分析
7. 采购周期合理性分析


输入：
data/raw/电力设备运维数据_2023-2026.xlsx


输出：

results/week3/

    ├── spare_parts_csv
    │
    └── spare_parts_figures


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

    "spare_parts"

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
# 中文显示
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
# 备件分析类
# ==========================================================


class SparePartsAnalyzer:



    def __init__(self):


        self.spare_parts = None


        self.fault = None


        self.maintenance = None




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



        # ----------------------------
        # 备品备件
        # ----------------------------


        self.spare_parts = pd.read_excel(

            DATA_PATH,

            sheet_name="备品备件"

        )



        # ----------------------------
        # 故障工单
        # ----------------------------


        self.fault = pd.read_excel(

            DATA_PATH,

            sheet_name="故障工单"

        )



        # ----------------------------
        # 检修计划
        # ----------------------------


        self.maintenance = pd.read_excel(

            DATA_PATH,

            sheet_name="检修计划"

        )



        print(

            "备品备件:",

            self.spare_parts.shape

        )


        print(

            "故障工单:",

            self.fault.shape

        )


        print(

            "检修计划:",

            self.maintenance.shape

        )





    # ======================================================
    # 数据预处理
    # ======================================================


    def preprocess(self):


        print(

            "数据预处理..."

        )



        # ==================================================
        # 记录年月
        # ==================================================


        self.spare_parts[

            "记录年月"

        ] = pd.to_datetime(

            self.spare_parts[

                "记录年月"

            ],

            format="%Y-%m",

            errors="coerce"

        )




        # ==================================================
        # 数值字段转换
        # ==================================================


        numeric_columns = [


            "期初库存",


            "本月消耗",


            "本月到货",


            "期末库存",


            "安全库存",


            "单价（元）",


            "消耗金额（万元）",


            "采购周期（天）"


        ]



        for col in numeric_columns:


            if col in self.spare_parts.columns:


                self.spare_parts[col] = pd.to_numeric(

                    self.spare_parts[col],

                    errors="coerce"

                ).fillna(0)





        # ==================================================
        # 故障日期
        # ==================================================


        if "故障时间" in self.fault.columns:


            self.fault[

                "故障时间"

            ] = pd.to_datetime(

                self.fault[

                    "故障时间"

                ],

                errors="coerce"

            )





        # ==================================================
        # 检修日期
        # ==================================================


        if "实际日期" in self.maintenance.columns:


            self.maintenance[

                "实际日期"

            ] = pd.to_datetime(

                self.maintenance[

                    "实际日期"

                ],

                errors="coerce"

            )




        print(

            "预处理完成"

        )





    # ======================================================
    # 字段检查
    # ======================================================


    def check_columns(self):


        print(

            "\n备品备件字段："

        )


        print(

            list(

                self.spare_parts.columns

            )

        )



        print(

            "\n故障字段："

        )


        print(

            list(

                self.fault.columns

            )

        )



        print(

            "\n检修字段："

        )


        print(

            list(

                self.maintenance.columns

            )

        )

    # ======================================================
    # 1. 月度消耗趋势分析
    # ======================================================


    def monthly_consumption_analysis(self):


        print(
            "分析月度备件消耗趋势..."
        )


        monthly = (

            self.spare_parts

            .groupby(
                "记录年月"
            )

            [

                "本月消耗"

            ]

            .sum()

            .reset_index()

        )


        monthly.columns = [

            "月份",

            "消耗数量"

        ]



        monthly.to_csv(

            CSV_PATH

            /

            "monthly_consumption.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return monthly




    # ======================================================
    # 2. 年度消耗统计
    # ======================================================


    def annual_consumption_analysis(self):


        print(

            "分析年度备件消耗..."

        )


        data = self.spare_parts.copy()



        data["年份"] = (

            data[

                "记录年月"

            ]

            .dt.year

        )



        annual = (

            data

            .groupby(

                "年份"

            )

            [

                "本月消耗"

            ]

            .sum()

            .reset_index()

        )



        annual.columns = [

            "年份",

            "年度消耗量"

        ]



        annual.to_csv(

            CSV_PATH

            /

            "annual_consumption.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return annual




    # ======================================================
    # 3. 库存周转率分析
    # ======================================================


    def inventory_turnover_analysis(self):


        print(

            "计算库存周转率..."

        )



        data = self.spare_parts.copy()



        data["平均库存"] = (

            data[

                "期初库存"

            ]

            +

            data[

                "期末库存"

            ]

        ) / 2



        turnover = (

            data

            .groupby(

                [

                    "备件名称",

                    "规格型号"

                ]

            )

            .agg(

                {

                    "本月消耗":

                    "sum",


                    "平均库存":

                    "mean",


                    "期末库存":

                    "last",


                    "安全库存":

                    "last",


                    "消耗金额（万元）":

                    "sum"

                }

            )

            .reset_index()

        )



        turnover.rename(

            columns={

                "本月消耗":

                "年度消耗量",

                "平均库存":

                "平均库存量",

                "期末库存":

                "当前库存"

            },

            inplace=True

        )



        # -----------------------------
        # 周转率
        # -----------------------------


        turnover[

            "库存周转率"

        ] = (

            turnover[

                "年度消耗量"

            ]

            /

            turnover[

                "平均库存量"

            ]

        ).replace(

            np.inf,

            0

        )



        turnover[

            "库存周转率"

        ] = turnover[

            "库存周转率"

        ].round(2)




        turnover.to_csv(

            CSV_PATH

            /

            "inventory_turnover.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return turnover





    # ======================================================
    # 4. 库存风险识别
    # ======================================================


    def inventory_warning_analysis(self):


        print(

            "识别积压与短缺备件..."

        )


        data = (

            self.inventory_turnover_analysis()

            .copy()

        )



        warning = []



        for _, row in data.iterrows():



            status = "正常"



            # -----------------------------
            # 短缺判断
            # -----------------------------


            if (

                row[

                    "当前库存"

                ]

                <

                row[

                    "安全库存"

                ]

            ):


                status = "库存不足"



            # -----------------------------
            # 积压判断
            # -----------------------------


            elif (

                row[

                    "库存周转率"

                ]

                <

                1

                and

                row[

                    "当前库存"

                ]

                >

                row[

                    "安全库存"

                ]

                *

                2

            ):


                status = "库存积压"



            warning.append(

                status

            )



        data[

            "库存状态"

        ] = warning



        data.to_csv(

            CSV_PATH

            /

            "inventory_warning.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return data

    # ======================================================
    # 5. ABC分类分析
    # ======================================================


    def abc_analysis(self):


        print(

            "进行ABC分类分析..."

        )



        # ----------------------------------
        # 按备件统计累计消耗金额
        # ----------------------------------


        abc = (

            self.spare_parts

            .groupby(

                [

                    "备件名称",

                    "规格型号"

                ]

            )

            [

                "消耗金额（万元）"

            ]

            .sum()

            .reset_index()

        )



        abc = abc.sort_values(

            by="消耗金额（万元）",

            ascending=False

        )



        # ----------------------------------
        # 累计金额
        # ----------------------------------


        total_cost = (

            abc[

                "消耗金额（万元）"

            ]

            .sum()

        )



        abc[

            "累计金额"

        ] = (

            abc[

                "消耗金额（万元）"

            ]

            .cumsum()

        )



        abc[

            "累计占比(%)"

        ] = (

            abc[

                "累计金额"

            ]

            /

            total_cost

            *

            100

        )



        # ----------------------------------
        # ABC分类
        # ----------------------------------


        def classify(x):


            if x <= 80:

                return "A类"


            elif x <= 95:

                return "B类"


            else:

                return "C类"




        abc[

            "ABC类别"

        ] = (

            abc[

                "累计占比(%)"

            ]

            .apply(classify)

        )



        abc.to_csv(

            CSV_PATH

            /

            "ABC_classification.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return abc

    # ======================================================
    # 6. 备件与故障检修关联分析
    # ======================================================


    def fault_maintenance_relation_analysis(self):


        print(

            "分析备件消耗与故障、检修关联..."

        )


        # ===============================
        # 备件月度消耗
        # ===============================


        spare_month = (

            self.spare_parts

            .groupby(

                "记录年月"

            )

            [

                "本月消耗"

            ]

            .sum()

            .reset_index()

        )


        spare_month.rename(

            columns={

                "记录年月":

                "月份",

                "本月消耗":

                "备件消耗量"

            },

            inplace=True

        )



        # ===============================
        # 故障月统计
        # ===============================


        fault = self.fault.copy()



        if "故障时间" in fault.columns:


            fault["月份"] = (

                fault[

                    "故障时间"

                ]

                .dt.to_period(

                    "M"

                )

                .dt.to_timestamp()

            )



            fault_month = (

                fault

                .groupby(

                    "月份"

                )

                .size()

                .reset_index(

                    name="故障次数"

                )

            )


        else:


            fault_month = pd.DataFrame(

                columns=[

                    "月份",

                    "故障次数"

                ]

            )




        # ===============================
        # 检修月统计
        # ===============================


        maintenance = self.maintenance.copy()



        if "实际日期" in maintenance.columns:


            maintenance["月份"] = (

                maintenance[

                    "实际日期"

                ]

                .dt.to_period(

                    "M"

                )

                .dt.to_timestamp()

            )



            maintenance_month = (

                maintenance

                .groupby(

                    "月份"

                )

                .size()

                .reset_index(

                    name="检修次数"

                )

            )


        else:


            maintenance_month = pd.DataFrame(

                columns=[

                    "月份",

                    "检修次数"

                ]

            )




        # ===============================
        # 合并
        # ===============================


        relation = (

            spare_month

            .merge(

                fault_month,

                on="月份",

                how="left"

            )

            .merge(

                maintenance_month,

                on="月份",

                how="left"

            )

        )



        relation.fillna(

            0,

            inplace=True

        )



        relation.to_csv(

            CSV_PATH

            /

            "spare_fault_maintenance_relation.csv",

            index=False,

            encoding="utf-8-sig"

        )



        return relation

    # ======================================================
    # 7. 采购周期合理性分析
    # ======================================================


    def procurement_cycle_analysis(self):


        print(

            "分析采购周期..."

        )



        data = (

            self.spare_parts

            .groupby(

                [

                    "备件名称",

                    "规格型号"

                ]

            )

            .agg(

                {

                    "采购周期（天）":

                    "mean",


                    "安全库存":

                    "mean",


                    "期末库存":

                    "mean"

                }

            )

            .reset_index()

        )



        def evaluate(day):


            if day <= 30:

                return "正常"



            elif day <= 60:

                return "采购周期较长"



            else:

                return "长周期备件"




        data[

            "采购周期评价"

        ] = (

            data[

                "采购周期（天）"

            ]

            .apply(evaluate)

        )



        data.to_csv(

            CSV_PATH

            /

            "procurement_cycle_analysis.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return data

    # ======================================================
    # 8. 月度消耗趋势图
    # ======================================================


    def plot_monthly_consumption(
            self,
            data
    ):


        print(
            "绘制月度消耗趋势..."
        )



        plt.figure(

            figsize=(10,5)

        )


        plt.plot(

            data["月份"],

            data["消耗数量"],

            marker="o"

        )


        plt.title(

            "备品备件月度消耗趋势"

        )


        plt.xlabel(

            "月份"

        )


        plt.ylabel(

            "消耗数量"

        )


        plt.xticks(

            rotation=45

        )


        plt.grid(

            alpha=0.3

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH

            /

            "monthly_consumption_trend.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 9. 年度消耗柱状图
    # ======================================================


    def plot_annual_consumption(
            self,
            data
    ):


        print(

            "绘制年度消耗趋势..."

        )



        plt.figure(

            figsize=(8,5)

        )


        plt.bar(

            data["年份"],

            data["年度消耗量"]

        )


        plt.title(

            "年度备件消耗总量"

        )


        plt.xlabel(

            "年份"

        )


        plt.ylabel(

            "消耗数量"

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH

            /

            "annual_consumption.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 10. 库存周转率Top20
    # ======================================================


    def plot_inventory_turnover(
            self,
            data
    ):


        print(

            "绘制库存周转率..."

        )



        top20 = (

            data

            .sort_values(

                "库存周转率",

                ascending=False

            )

            .head(20)

        )



        plt.figure(

            figsize=(10,6)

        )


        plt.barh(

            top20["备件名称"],

            top20["库存周转率"]

        )


        plt.title(

            "库存周转率Top20备件"

        )


        plt.xlabel(

            "库存周转率"

        )


        plt.ylabel(

            "备件名称"

        )


        plt.gca().invert_yaxis()



        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH

            /

            "inventory_turnover_top20.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 11. ABC帕累托图
    # ======================================================


    def plot_abc_pareto(
            self,
            data
    ):


        print(

            "绘制ABC帕累托图..."

        )



        plt.figure(

            figsize=(10,6)

        )


        x = range(

            len(data)

        )



        plt.bar(

            x,

            data["消耗金额（万元）"]

        )



        plt.plot(

            x,

            data["累计占比(%)"],

            color="red",

            marker="o"

        )


        plt.axhline(

            80,

            linestyle="--"

        )


        plt.axhline(

            95,

            linestyle="--"

        )


        plt.title(

            "备件ABC分类帕累托分析"

        )


        plt.xlabel(

            "备件排序"

        )


        plt.ylabel(

            "金额/累计比例"

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH

            /

            "ABC_pareto.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 12. 库存状态分布图
    # ======================================================


    def plot_inventory_warning(
            self,
            data
    ):


        print(

            "绘制库存预警图..."

        )



        status = (

            data["库存状态"]

            .value_counts()

            .reset_index()

        )



        status.columns = [

            "状态",

            "数量"

        ]



        plt.figure(

            figsize=(7,5)

        )


        plt.bar(

            status["状态"],

            status["数量"]

        )


        plt.title(

            "备件库存状态分布"

        )


        plt.ylabel(

            "备件数量"

        )


        plt.xticks(

            rotation=30

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH

            /

            "inventory_warning.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 13. 采购周期分析图
    # ======================================================


    def plot_procurement_cycle(
            self,
            data
    ):


        print(

            "绘制采购周期分析..."

        )



        result = (

            data

            [

                "采购周期评价"

            ]

            .value_counts()

            .reset_index()

        )



        result.columns=[

            "评价",

            "数量"

        ]



        plt.figure(

            figsize=(7,5)

        )


        plt.bar(

            result["评价"],

            result["数量"]

        )


        plt.title(

            "备件采购周期评价"

        )


        plt.ylabel(

            "备件数量"

        )


        plt.xticks(

            rotation=30

        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH

            /

            "procurement_cycle.png",

            dpi=300

        )


        plt.close()

def main():


    analyzer = SparePartsAnalyzer()



    # ==========================
    # 数据读取
    # ==========================


    analyzer.load_data()



    analyzer.preprocess()



    analyzer.check_columns()



    # ==========================
    # 核心分析
    # ==========================


    monthly = (

        analyzer

        .monthly_consumption_analysis()

    )



    annual = (

        analyzer

        .annual_consumption_analysis()

    )



    turnover = (

        analyzer

        .inventory_turnover_analysis()

    )



    warning = (

        analyzer

        .inventory_warning_analysis()

    )



    abc = (

        analyzer

        .abc_analysis()

    )



    relation = (

        analyzer

        .fault_maintenance_relation_analysis()

    )



    procurement = (

        analyzer

        .procurement_cycle_analysis()

    )



    # ==========================
    # 绘图
    # ==========================


    analyzer.plot_monthly_consumption(

        monthly

    )



    analyzer.plot_annual_consumption(

        annual

    )



    analyzer.plot_inventory_turnover(

        turnover

    )



    analyzer.plot_abc_pareto(

        abc

    )



    analyzer.plot_inventory_warning(

        warning

    )



    analyzer.plot_procurement_cycle(

        procurement

    )



    print(

        "\n备品备件分析完成!"

    )


    print(

        "结果路径:",

        RESULT_PATH

    )




if __name__ == "__main__":


    main()