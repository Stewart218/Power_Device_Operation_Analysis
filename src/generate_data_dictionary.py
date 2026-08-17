"""
数据字典自动生成脚本

功能：
1. 读取电力设备运维Excel数据
2. 自动分析6张数据表结构
3. 提取字段信息
4. 生成数据字典初稿Excel

输出：
results/week1/data_dictionary_draft.xlsx
"""


import pandas as pd
import os


class DataDictionaryGenerator:

    def __init__(self, excel_path, output_path):

        self.excel_path = excel_path
        self.output_path = output_path


    def load_data(self):
        """
        读取Excel所有Sheet
        """

        print("正在读取数据...")

        data = pd.read_excel(
            self.excel_path,
            sheet_name=None
        )

        print(f"共读取 {len(data)} 张数据表")

        return data



    def analyze_table(self, sheet_name, df):
        """
        分析单张表字段信息
        """

        dictionary = []


        total_rows = len(df)


        for column in df.columns:

            series = df[column]


            missing_count = series.isnull().sum()


            missing_rate = (
                missing_count / total_rows
                if total_rows > 0
                else 0
            )


            unique_count = series.nunique()


            # 获取非空示例值
            examples = (
                series.dropna()
                .astype(str)
                .head(3)
                .tolist()
            )


            dictionary.append({

                "数据表": sheet_name,

                "字段名称": column,

                "数据类型": str(series.dtype),

                "记录数量": total_rows,

                "缺失数量": missing_count,

                "缺失比例": round(
                    missing_rate * 100,
                    2
                ),

                "唯一值数量": unique_count,

                "示例值": "；".join(examples),

                "业务含义": "",

                "取值范围": "",

                "计量单位": "",

                "备注": ""

            })


        return dictionary



    def generate(self):

        data = self.load_data()


        all_dictionary = []


        for sheet_name, df in data.items():

            print(
                f"正在分析：{sheet_name}"
            )


            result = self.analyze_table(
                sheet_name,
                df
            )


            all_dictionary.extend(result)



        dictionary_df = pd.DataFrame(
            all_dictionary
        )


        # 创建输出目录

        os.makedirs(
            os.path.dirname(self.output_path),
            exist_ok=True
        )


        dictionary_df.to_excel(
            self.output_path,
            index=False
        )


        print("\n数据字典生成完成")

        print(
            f"保存位置：{self.output_path}"
        )



if __name__ == "__main__":


    # 原始数据路径

    excel_path = (
        "../data/raw/"
        "电力设备运维数据_2023-2026.xlsx"
    )


    # 输出路径

    output_path = (
        "../results/week1/"
        "data_dictionary_draft.xlsx"
    )



    generator = DataDictionaryGenerator(
        excel_path,
        output_path
    )


    generator.generate()