"""
正式版数据字典生成脚本

输入:
results/week1/data_dictionary_draft.xlsx

输出:
docs/数据字典.xlsx

功能:
1. 按数据表拆分Sheet
2. 自动生成业务含义
3. 自动生成取值范围
4. 自动生成计量单位
"""


import pandas as pd
import os


class FinalDictionaryGenerator:


    def __init__(self, input_file, output_file):

        self.input_file = input_file
        self.output_file = output_file



    def load_draft(self):

        """
        读取数据字典初稿
        """

        df = pd.read_excel(
            self.input_file
        )

        return df



    def generate_description(self, field):

        """
        根据字段名称生成业务描述
        """

        field = str(field)


        # 编号类

        if "编号" in field:

            return (
                "设备或业务记录唯一标识编号",
                "按照系统编码规则",
                "无"
            )


        # 名称类

        elif "名称" in field:

            return (
                "设备或对象名称信息",
                "文本描述",
                "无"
            )


        # 日期时间

        elif (
            "日期" in field
            or "时间" in field
            or "年月" in field
        ):

            return (
                "业务事件发生或记录时间",
                "有效日期格式",
                "无"
            )


        # 温度

        elif "温度" in field:

            return (
                "设备运行温度监测参数",
                "根据设备运行规范确定",
                "℃"
            )


        # 电压

        elif "电压" in field:

            return (
                "设备运行电压参数",
                "大于等于0",
                "kV"
            )


        # 电流

        elif "电流" in field:

            return (
                "设备运行电流参数",
                "大于等于0",
                "A"
            )


        # 负荷

        elif "负荷率" in field:

            return (
                "设备负载水平指标",
                "0~100",
                "%"
            )


        # 压力

        elif "压力" in field:

            return (
                "设备运行压力监测参数",
                "大于等于0",
                "MPa"
            )


        # 数量

        elif (
            "数量" in field
            or "库存" in field
        ):

            return (
                "物资或设备数量指标",
                "大于等于0",
                "件"
            )


        # 金额费用

        elif (
            "费用" in field
            or "金额" in field
            or "单价" in field
        ):

            return (
                "运维经济指标",
                "大于等于0",
                "元"
            )


        # 等级

        elif "等级" in field:

            return (
                "业务分类等级信息",
                "按照业务规则划分",
                "无"
            )


        # 默认

        else:

            return (
                f"{field}对应业务记录信息",
                "根据业务规则确定",
                "无"
            )



    def generate(self):


        df = self.load_draft()


        os.makedirs(
            os.path.dirname(self.output_file),
            exist_ok=True
        )


        writer = pd.ExcelWriter(
            self.output_file,
            engine="openpyxl"
        )


        tables = df["数据表"].unique()


        for table in tables:


            table_df = df[
                df["数据表"] == table
            ]


            result = []


            for _, row in table_df.iterrows():


                meaning, scope, unit = (
                    self.generate_description(
                        row["字段名称"]
                    )
                )


                result.append({

                    "字段名称":
                        row["字段名称"],


                    "数据类型":
                        row["数据类型"],


                    "业务含义":
                        meaning,


                    "取值范围":
                        scope,


                    "计量单位":
                        unit,


                    "备注":
                        ""

                })


            result_df = pd.DataFrame(
                result
            )


            result_df.to_excel(
                writer,
                sheet_name=table,
                index=False
            )



        writer.close()


        print(
            "正式版数据字典生成完成!"
        )

        print(
            self.output_file
        )





if __name__ == "__main__":


    input_file = (
        "../results/week1/"
        "data_dictionary_draft.xlsx"
    )


    output_file = (
        "../docs/"
        "数据字典.xlsx"
    )


    generator = FinalDictionaryGenerator(
        input_file,
        output_file
    )


    generator.generate()