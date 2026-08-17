"""
电力设备运维数据质量评估报告生成

检查内容：
1. 缺失值统计
2. 重复记录统计
3. 异常值统计
4. 时间连续性检查
5. 设备编号一致性检查
6. 各表年月覆盖分析

输出：
reports/数据质量评估报告.xlsx
"""


import pandas as pd
import os


class DataQualityReport:


    def __init__(self, input_file, output_file):

        self.input_file = input_file
        self.output_file = output_file



    def load_data(self):

        return pd.read_excel(
            self.input_file,
            sheet_name=None
        )



    # -----------------------------
    # 缺失值检查
    # -----------------------------

    def missing_check(self, data):

        result = []

        for name, df in data.items():

            for col in df.columns:

                missing = df[col].isna().sum()

                rate = missing / len(df) * 100


                result.append({

                    "数据表": name,

                    "字段": col,

                    "缺失数量": missing,

                    "记录数量": len(df),

                    "缺失比例(%)": round(rate,2)

                })


        return pd.DataFrame(result)



    # -----------------------------
    # 重复记录
    # -----------------------------

    def duplicate_check(self,data):

        result=[]

        for name,df in data.items():

            result.append({

                "数据表":name,

                "总记录数":len(df),

                "重复记录数":
                    df.duplicated().sum()

            })


        return pd.DataFrame(result)



    # -----------------------------
    # 时间连续性
    # -----------------------------

    def time_check(self,data):

        result=[]


        for name,df in data.items():

            time_cols=[]


            for c in df.columns:

                if (
                    "时间" in str(c)
                    or "日期" in str(c)
                    or "年月" in str(c)
                ):

                    time_cols.append(c)



            for c in time_cols:


                temp=df[c].dropna()


                try:

                    temp=pd.to_datetime(temp)


                    start=temp.min()

                    end=temp.max()


                    months=pd.period_range(

                        start=start,

                        end=end,

                        freq="M"

                    )


                    exist_months=(

                        temp.dt.to_period("M")
                        .unique()

                    )


                    missing_months=set(months)-set(exist_months)


                    result.append({

                        "数据表":name,

                        "时间字段":c,

                        "开始时间":start,

                        "结束时间":end,

                        "覆盖月份数量":
                            len(exist_months),

                        "缺失月份":
                            ",".join(
                                map(
                                    str,
                                    missing_months
                                )
                            )

                    })


                except:

                    pass


        return pd.DataFrame(result)



    # -----------------------------
    # 设备编号一致性
    # -----------------------------

    def equipment_id_check(self,data):


        result=[]


        if "设备台账" not in data:

            return pd.DataFrame()


        master=set(

            data["设备台账"]
            ["设备编号"]
            .dropna()

        )


        for name,df in data.items():


            if (
                "设备编号"
                in df.columns
            ):

                ids=set(

                    df["设备编号"]
                    .dropna()

                )


                missing=ids-master


                result.append({

                    "数据表":name,

                    "设备编号数量":len(ids),

                    "匹配数量":
                        len(ids & master),

                    "无法匹配数量":
                        len(missing),

                    "匹配率(%)":
                        round(
                            len(ids & master)
                            /
                            len(ids)
                            *
                            100,
                            2
                        )

                })


        return pd.DataFrame(result)



    # -----------------------------
    # 月份分布
    # -----------------------------

    def month_distribution(self,data):


        result=[]


        for name,df in data.items():


            for col in df.columns:

                if (
                        "时间" in str(col)
                        or "年月" in str(col)
                        or (
                        "日期" in str(col)
                        and "投运" not in str(col)
                )
                ):


                    try:

                        temp=pd.to_datetime(
                            df[col]
                        )


                        count=(

                            temp.dt
                            .to_period("M")
                            .value_counts()
                            .reset_index()

                        )


                        count.columns=[

                            "年月",

                            "记录数量"

                        ]


                        count["数据表"]=name

                        count["时间字段"]=col


                        result.append(count)


                    except:

                        pass



        if result:

            return pd.concat(
                result
            )


        return pd.DataFrame()



    # -----------------------------
    # 输出报告
    # -----------------------------

    def generate(self):


        data=self.load_data()


        os.makedirs(

            os.path.dirname(
                self.output_file
            ),

            exist_ok=True

        )


        with pd.ExcelWriter(
            self.output_file

        ) as writer:


            self.missing_check(data)\
                .to_excel(
                    writer,
                    sheet_name="缺失值统计",
                    index=False
                )


            self.duplicate_check(data)\
                .to_excel(
                    writer,
                    sheet_name="重复记录",
                    index=False
                )

            self.abnormal_check(data)\
                .to_excel(
                    writer,
                    sheet_name="异常值统计",
                    index=False
                )

            self.time_check(data)\
                .to_excel(
                    writer,
                    sheet_name="时间连续性",
                    index=False
                )


            self.equipment_id_check(data)\
                .to_excel(
                    writer,
                    sheet_name="设备编号一致性",
                    index=False
                )


            self.month_distribution(data)\
                .to_excel(
                    writer,
                    sheet_name="年月分布",
                    index=False
                )


        print(
            "数据质量评估报告生成完成:"
        )

        print(
            self.output_file
        )

    # -----------------------------
    # 异常值检查
    # -----------------------------

    def abnormal_check(self, data):

        """
        根据电力设备运行规律检查异常值
        """

        result = []


        # 定义字段异常规则
        rules = {

            "温度": {
                "min": -40,
                "max": 150,
                "unit": "℃"
            },

            "负荷率": {
                "min": 0,
                "max": 100,
                "unit": "%"
            },

            "压力": {
                "min": 0,
                "max": 1,
                "unit": "MPa"
            },

            "电压": {
                "min": 0,
                "max": 1000,
                "unit": "kV"
            },

            "电流": {
                "min": 0,
                "max": 10000,
                "unit": "A"
            },

            "费用": {
                "min": 0,
                "max": None,
                "unit": "元"
            },

            "数量": {
                "min": 0,
                "max": None,
                "unit": ""
            },

            "库存": {
                "min": 0,
                "max": None,
                "unit": ""
            }

        }


        for table, df in data.items():


            for col in df.columns:


                col_name = str(col)


                rule = None


                # 判断字段是否需要检查

                for key in rules.keys():

                    if key in col_name:

                        rule = rules[key]

                        break



                if rule is None:

                    continue



                try:

                    series = pd.to_numeric(
                        df[col],
                        errors="coerce"
                    )


                    abnormal = pd.Series(
                        False,
                        index=series.index
                    )


                    if rule["min"] is not None:

                        abnormal |= (
                            series < rule["min"]
                        )


                    if rule["max"] is not None:

                        abnormal |= (
                            series > rule["max"]
                        )


                    abnormal_count = abnormal.sum()



                    result.append({

                        "数据表": table,

                        "字段": col,

                        "检测规则":
                            f'{rule["min"]}~{rule["max"]}',

                        "异常数量":
                            int(abnormal_count),

                        "总数量":
                            len(series),

                        "异常比例(%)":
                            round(
                                abnormal_count
                                /
                                len(series)
                                *
                                100,
                                2
                            )

                    })


                except Exception:

                    pass



        return pd.DataFrame(result)


if __name__=="__main__":


    report=DataQualityReport(

        "../data/raw/电力设备运维数据_2023-2026.xlsx",

        "../reports/数据质量评估报告.xlsx"

    )


    report.generate()