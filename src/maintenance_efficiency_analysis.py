# -*- coding: utf-8 -*-

"""
检修执行效能评估分析

功能：
1. 检修计划完成率分析
2. 检修及时率分析
3. 检修类型工时/费用分析
4. 延期情况分析
5. 检修前后运行参数改善分析

输入：
data/raw/电力设备运维数据_2023-2026.xlsx

输出：
results/week3/
    ├── maintenance_csv
    └── maintenance_figures

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
    "maintenance"
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
# 中文显示配置
# ==========================================================

plt.rcParams["font.sans-serif"] = [
    "SimHei"
]

plt.rcParams[
    "axes.unicode_minus"
] = False



# ==========================================================
# 数据分析类
# ==========================================================

class MaintenanceEfficiencyAnalyzer:


    def __init__(self):

        self.maintenance = None

        self.parameter = None



    # ------------------------------------------------------
    # 数据读取
    # ------------------------------------------------------

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


        self.maintenance = pd.read_excel(
            DATA_PATH,
            sheet_name="检修计划"
        )


        self.parameter = pd.read_excel(
            DATA_PATH,
            sheet_name="运行参数"
        )


        print(
            "检修计划:",
            self.maintenance.shape
        )


        print(
            "运行参数:",
            self.parameter.shape
        )



    # ------------------------------------------------------
    # 数据预处理
    # ------------------------------------------------------

    def preprocess(self):

        print(
            "数据预处理..."
        )


        # ----------------------------
        # 日期格式转换
        # ----------------------------

        self.maintenance[
            "计划日期"
        ] = pd.to_datetime(
            self.maintenance[
                "计划日期"
            ],
            errors="coerce"
        )


        self.maintenance[
            "实际日期"
        ] = pd.to_datetime(
            self.maintenance[
                "实际日期"
            ],
            errors="coerce"
        )



        self.parameter[
            "记录年月"
        ] = pd.to_datetime(
            self.parameter[
                "记录年月"
            ],
            errors="coerce"
        )



        # ----------------------------
        # 删除关键字段缺失
        # ----------------------------

        self.maintenance.dropna(
            subset=[
                "设备编号",
                "计划日期"
            ],
            inplace=True
        )


        self.parameter.dropna(
            subset=[
                "设备编号",
                "记录年月"
            ],
            inplace=True
        )


        # ----------------------------
        # 延期天数转换
        # ----------------------------

        if "延期天数" in self.maintenance.columns:


            self.maintenance[
                "延期天数"
            ] = pd.to_numeric(
                self.maintenance[
                    "延期天数"
                ],
                errors="coerce"
            ).fillna(0)



        # ----------------------------
        # 是否按时标准化
        # ----------------------------

        if "是否按时" in self.maintenance.columns:


            self.maintenance[
                "是否按时"
            ] = (
                self.maintenance[
                    "是否按时"
                ]
                .astype(str)
                .str.strip()
            )


        print(
            "预处理完成"
        )



    # ------------------------------------------------------
    # 基础检查
    # ------------------------------------------------------

    def check_columns(self):


        print(
            "\n检修字段:"
        )

        print(
            list(
                self.maintenance.columns
            )
        )


        print(
            "\n运行参数字段:"
        )

        print(
            list(
                self.parameter.columns
            )
        )


    # ======================================================
    # 任务1：计划检修完成率分析
    # ======================================================

    def completion_rate_analysis(self):

        print(
            "分析计划检修完成率..."
        )


        data = self.maintenance.copy()



        # 实际日期存在表示完成

        total_count = len(
            data
        )


        completed_count = (
            data[
                "实际日期"
            ]
            .notna()
            .sum()
        )


        completion_rate = (
            completed_count
            /
            total_count
            *
            100
        )



        result = pd.DataFrame(
            {
                "指标":
                [
                    "计划检修总数",
                    "已完成检修数",
                    "计划检修完成率"
                ],

                "数值":
                [
                    total_count,
                    completed_count,
                    round(
                        completion_rate,
                        2
                    )
                ]
            }
        )



        result.to_csv(
            CSV_PATH
            /
            "completion_rate.csv",

            index=False,

            encoding="utf-8-sig"
        )


        return result



    # ======================================================
    # 任务1：检修及时率分析
    # ======================================================

    def timeliness_rate_analysis(self):

        print(
            "分析检修及时率..."
        )


        data = self.maintenance.copy()



        # --------------------------
        # 总体及时率
        # --------------------------

        total = len(
            data
        )


        on_time = (
            data[
                "是否按时"
            ]
            .astype(str)
            .isin(
                [
                    "是",
                    "按时",
                    "1",
                    "True"
                ]
            )
            .sum()
        )


        rate = (
            on_time
            /
            total
            *
            100
        )


        overall = pd.DataFrame(
            {
                "统计维度":
                [
                    "总体"
                ],

                "计划数量":
                [
                    total
                ],

                "按时完成数量":
                [
                    on_time
                ],

                "及时率(%)":
                [
                    round(
                        rate,
                        2
                    )
                ]
            }
        )



        # --------------------------
        # 按检修类型统计
        # --------------------------

        type_result = (

            data

            .groupby(
                "检修类型"
            )

            .apply(
                lambda x:
                pd.Series(
                    {

                        "计划数量":
                        len(x),


                        "按时完成数量":
                        (
                            x[
                                "是否按时"
                            ]
                            .astype(str)
                            .isin(
                                [
                                    "是",
                                    "按时",
                                    "1",
                                    "True"
                                ]
                            )
                            .sum()
                        )

                    }
                )

            )

            .reset_index()

        )


        type_result[
            "及时率(%)"
        ] = (

            type_result[
                "按时完成数量"
            ]

            /

            type_result[
                "计划数量"
            ]

            *

            100

        ).round(2)



        type_result.to_csv(
            CSV_PATH
            /
            "timeliness_rate.csv",

            index=False,

            encoding="utf-8-sig"
        )



        return type_result




    # ======================================================
    # 任务2：检修类型工时、费用分析
    # ======================================================

    def maintenance_type_analysis(self):

        print(
            "分析检修类型工时费用..."
        )


        data = self.maintenance.copy()



        result = (

            data

            .groupby(
                "检修类型"
            )

            .agg(

                检修次数=
                (
                    "检修工单号",
                    "count"
                ),


                总工时=
                (
                    "检修工时（天）",
                    "sum"
                ),


                平均工时=
                (
                    "检修工时（天）",
                    "mean"
                ),


                总费用=
                (
                    "检修费用（万元）",
                    "sum"
                ),


                平均费用=
                (
                    "检修费用（万元）",
                    "mean"
                )

            )

            .reset_index()

        )



        result[
            [
                "平均工时",
                "平均费用"
            ]
        ] = (

            result[
                [
                    "平均工时",
                    "平均费用"
                ]
            ]

            .round(2)

        )



        result.to_csv(

            CSV_PATH
            /
            "maintenance_type_statistics.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return result




    # ======================================================
    # 任务4：延期等级分析
    # ======================================================

    def delay_analysis(self):

        print(
            "分析检修延期情况..."
        )



        data = self.maintenance.copy()



        def classify_delay(days):


            if days <= 0:

                return "按时完成"


            elif days <= 7:

                return "轻微延期"


            elif days <= 30:

                return "中度延期"


            else:

                return "严重延期"



        data[
            "延期等级"
        ] = (

            data[
                "延期天数"
            ]

            .apply(
                classify_delay
            )

        )



        result = (

            data

            .groupby(
                "延期等级"
            )

            .size()

            .reset_index(
                name="数量"
            )

        )



        result[
            "比例(%)"
        ] = (

            result[
                "数量"
            ]

            /

            result[
                "数量"
            ]
            .sum()

            *

            100

        ).round(2)



        result.to_csv(

            CSV_PATH
            /
            "delay_analysis.csv",

            index=False,

            encoding="utf-8-sig"

        )


        return result

    # ======================================================
    # 任务3：检修后设备运行参数改善效果分析
    # ======================================================

    def parameter_improvement_analysis(self):

        print(
            "分析检修前后运行参数改善效果..."
        )


        maintenance = self.maintenance.copy()

        parameter = self.parameter.copy()



        # ==================================================
        # 参数字段
        # ==================================================

        parameter_columns = [

            "月平均负荷率",

            "月最大负荷率",

            "油温（℃）",

            "绕组温度（℃）",

            "绝缘电阻（MΩ）",

            "介质损耗角tanδ",

            "局部放电量（pC）",

            "SF6气体压力（MPa）"

        ]



        results = []



        # ==================================================
        # 遍历每一次检修
        # ==================================================

        for _, row in maintenance.iterrows():


            device_id = row[
                "设备编号"
            ]


            repair_date = row[
                "实际日期"
            ]


            # 没有实际检修日期跳过

            if pd.isna(
                repair_date
            ):

                continue



            device_parameter = parameter[
                parameter[
                    "设备编号"
                ]
                ==
                device_id
            ].copy()



            if len(device_parameter) == 0:

                continue



            # ==================================================
            # 检修前3个月
            # ==================================================

            before_data = device_parameter[

                (
                    device_parameter[
                        "记录年月"
                    ]

                    >=

                    repair_date
                    -
                    pd.DateOffset(
                        months=3
                    )
                )

                &

                (

                    device_parameter[
                        "记录年月"
                    ]

                    <

                    repair_date

                )

            ]



            # ==================================================
            # 检修后3个月
            # ==================================================

            after_data = device_parameter[

                (

                    device_parameter[
                        "记录年月"
                    ]

                    >

                    repair_date

                )

                &

                (

                    device_parameter[
                        "记录年月"
                    ]

                    <=

                    repair_date
                    +
                    pd.DateOffset(
                        months=3
                    )

                )

            ]



            # 前后数据不足不计算

            if (

                len(before_data)==0

                or

                len(after_data)==0

            ):

                continue



            result = {

                "设备编号":
                device_id,


                "检修日期":
                repair_date,


                "设备类型":
                row[
                    "设备类型"
                ],


                "所属变电站":
                row[
                    "所属变电站"
                ]

            }



            # ==================================================
            # 计算前后平均值
            # ==================================================

            for col in parameter_columns:


                before_mean = (

                    before_data[
                        col
                    ]

                    .mean()

                )


                after_mean = (

                    after_data[
                        col
                    ]

                    .mean()

                )



                result[
                    f"检修前_{col}"
                ] = round(
                    before_mean,
                    3
                )


                result[
                    f"检修后_{col}"
                ] = round(
                    after_mean,
                    3
                )



                # 变化率

                if before_mean != 0:


                    change = (

                        (
                            after_mean
                            -
                            before_mean
                        )

                        /

                        abs(
                            before_mean
                        )

                        *

                        100

                    )


                else:

                    change = np.nan



                result[
                    f"{col}_变化率(%)"
                ] = round(
                    change,
                    2
                )



            results.append(
                result
            )



        result_df = pd.DataFrame(
            results
        )



        result_df.to_csv(

            CSV_PATH
            /
            "parameter_improvement.csv",

            index=False,

            encoding="utf-8-sig"

        )


        print(
            "参数改善分析完成:",
            result_df.shape
        )


        return result_df


    # ======================================================
    # 绘图1：检修及时率
    # ======================================================

    def plot_timeliness_rate(
            self,
            data
    ):

        print(
            "绘制及时率图..."
        )


        plt.figure(
            figsize=(8,5)
        )


        plt.bar(

            data[
                "检修类型"
            ],

            data[
                "及时率(%)"
            ]

        )


        plt.title(
            "不同检修类型及时率"
        )


        plt.ylabel(
            "及时率(%)"
        )


        plt.xticks(
            rotation=30
        )


        plt.ylim(
            0,
            100
        )


        plt.tight_layout()


        plt.savefig(

            FIGURE_PATH
            /
            "timeliness_rate.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 绘图2：检修费用分析
    # ======================================================

    def plot_cost_analysis(
            self,
            data
    ):

        print(
            "绘制检修费用图..."
        )


        plt.figure(
            figsize=(8,5)
        )


        plt.bar(

            data[
                "检修类型"
            ],

            data[
                "总费用"
            ]

        )


        plt.title(
            "不同检修类型费用分布"
        )


        plt.ylabel(
            "费用（万元）"
        )


        plt.xticks(
            rotation=30
        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH
            /
            "maintenance_cost.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 绘图3：检修工时分析
    # ======================================================

    def plot_hours_analysis(
            self,
            data
    ):

        print(
            "绘制检修工时图..."
        )


        plt.figure(
            figsize=(8,5)
        )


        plt.bar(

            data[
                "检修类型"
            ],

            data[
                "总工时"
            ]

        )


        plt.title(
            "不同检修类型工时分布"
        )


        plt.ylabel(
            "工时（天）"
        )


        plt.xticks(
            rotation=30
        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH
            /
            "maintenance_hours.png",

            dpi=300

        )


        plt.close()




    # ======================================================
    # 绘图4：延期等级分布
    # ======================================================

    def plot_delay_analysis(
            self,
            data
    ):

        print(
            "绘制延期分析图..."
        )


        plt.figure(
            figsize=(7,5)
        )


        plt.bar(

            data[
                "延期等级"
            ],

            data[
                "比例(%)"
            ]

        )


        plt.title(
            "检修延期等级分布"
        )


        plt.ylabel(
            "比例(%)"
        )


        plt.xticks(
            rotation=30
        )


        plt.tight_layout()



        plt.savefig(

            FIGURE_PATH
            /
            "delay_distribution.png",

            dpi=300

        )


        plt.close()



# ==========================================================
# 主程序
# ==========================================================


def main():


    analyzer = MaintenanceEfficiencyAnalyzer()



    # --------------------------
    # 数据读取
    # --------------------------

    analyzer.load_data()



    # --------------------------
    # 数据处理
    # --------------------------

    analyzer.preprocess()



    analyzer.check_columns()



    # --------------------------
    # 核心分析
    # --------------------------

    completion = (

        analyzer
        .completion_rate_analysis()

    )



    timeliness = (

        analyzer
        .timeliness_rate_analysis()

    )



    type_statistics = (

        analyzer
        .maintenance_type_analysis()

    )



    delay = (

        analyzer
        .delay_analysis()

    )



    parameter = (

        analyzer
        .parameter_improvement_analysis()

    )



    # --------------------------
    # 图表
    # --------------------------


    analyzer.plot_timeliness_rate(
        timeliness
    )


    analyzer.plot_cost_analysis(
        type_statistics
    )


    analyzer.plot_hours_analysis(
        type_statistics
    )


    analyzer.plot_delay_analysis(
        delay
    )






    print(
        "\n检修执行效能评估完成！"
    )


    print(
        "结果目录：",
        RESULT_PATH
    )



if __name__ == "__main__":

    main()