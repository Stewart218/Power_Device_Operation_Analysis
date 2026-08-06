"""
故障分析可视化仪表板
Task5

功能:
1. 故障趋势
2. 故障类型分布
3. 严重等级分布
4. TOP故障设备
5. MTBF/MTTR对比
6. 慢性病设备展示


输出:
results/week2/fault_dashboard.html

"""


from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ==========================
# 路径
# ==========================

ROOT = Path(__file__).resolve().parent.parent


DATA_PATH = (
    ROOT
    /
    "data"
    /
    "raw"
    /
    "电力设备运维数据_2023-2026.xlsx"
)


RESULT_PATH = (

    ROOT
    /
    "results"
    /
    "week2"

)


OUTPUT_HTML = (

    RESULT_PATH
    /
    "fault_dashboard.html"

)


STAT_PATH = (

    RESULT_PATH
    /
    "statistics"

)



# ==========================
# 数据读取
# ==========================


def load_data():

    fault = pd.read_excel(
        DATA_PATH,
        sheet_name="故障工单"
    )


    reliability = None


    file = (
        STAT_PATH
        /
        "reliability"
        /
        "reliability_device_index.csv"
    )


    if file.exists():

        reliability = pd.read_csv(
            file,
            encoding="utf-8-sig"
        )


    chronic_file = (

        STAT_PATH
        /
        "recurring_fault"
        /
        "chronic_device_list.csv"

    )


    if chronic_file.exists():

        chronic = pd.read_csv(
            chronic_file,
            encoding="utf-8-sig"
        )

    else:

        chronic = None



    fault["故障时间"] = pd.to_datetime(
        fault["故障时间"]
    )


    return fault,reliability,chronic



# ==========================
# 故障趋势
# ==========================


def fault_trend(fault):


    temp=(

        fault

        .set_index("故障时间")

        .resample("ME")

        .size()

        .reset_index(
            name="故障次数"
        )

    )


    fig=px.line(

        temp,

        x="故障时间",

        y="故障次数",

        markers=True,

        title="月度故障趋势"

    )


    return fig



# ==========================
# 类型分布
# ==========================


def fault_type(fault):


    data=(

        fault

        ["故障类型"]

        .value_counts()

        .reset_index()

    )


    data.columns=[

        "故障类型",

        "数量"

    ]


    fig=px.bar(

        data,

        x="故障类型",

        y="数量",

        title="故障类型分布"

    )


    return fig



# ==========================
# 等级分布
# ==========================


def fault_level(fault):


    data=(

        fault["严重等级"]

        .value_counts()

        .reset_index()

    )


    data.columns=[

        "严重等级",

        "数量"

    ]


    fig=px.pie(

        data,

        names="严重等级",

        values="数量",

        title="故障严重等级分布"

    )


    return fig



# ==========================
# TOP故障设备
# ==========================


def top_fault_device(fault):


    data=(

        fault

        ["设备编号"]

        .value_counts()

        .head(10)

        .reset_index()

    )


    data.columns=[

        "设备编号",

        "故障次数"

    ]


    fig=px.bar(

        data,

        x="设备编号",

        y="故障次数",

        title="TOP10故障设备"

    )


    return fig



# ==========================
# MTBF MTTR
# ==========================


def reliability_compare(data):

    if data is None:

        fig = go.Figure()

        fig.update_layout(
            title="暂无可靠性指标数据"
        )

        return fig


    # ==========================
    # 字段匹配
    # ==========================

    mtbf_col = None
    mttr_col = None


    for col in data.columns:

        if (
            "MTBF" in col
            or
            "平均故障间隔" in col
        ):
            mtbf_col = col


        if (
            "MTTR" in col
            or
            "平均修复" in col
        ):
            mttr_col = col



    if mtbf_col is None or mttr_col is None:

        fig = go.Figure()

        fig.update_layout(
            title="未找到MTBF/MTTR字段"
        )

        return fig



    # 排序

    data = data.sort_values(
        by=mtbf_col,
        ascending=False
    )


    fig = go.Figure()



    # ==========================
    # MTBF柱
    # 左轴
    # ==========================

    fig.add_trace(

        go.Bar(

            x=data["设备类型"],

            y=data[mtbf_col],

            name="MTBF",

            yaxis="y",

            offsetgroup="MTBF"

        )

    )



    # ==========================
    # MTTR柱
    # 右轴
    # ==========================

    fig.add_trace(

        go.Bar(

            x=data["设备类型"],

            y=data[mttr_col],

            name="MTTR",

            yaxis="y2",

            offsetgroup="MTTR"

        )

    )



    fig.update_layout(

        title=
        "不同设备类型可靠性指标 MTBF / MTTR 对比",


        barmode="group",


        xaxis=dict(

            title="设备类型"

        ),


        yaxis=dict(

            title="MTBF（小时）",

            side="left"

        ),


        yaxis2=dict(

            title="MTTR（小时）",

            side="right",

            overlaying="y"

        ),


        legend=dict(

            orientation="h",

            y=1.1

        ),


        template="plotly_white",

        height=600

    )


    return fig



# ==========================
# 慢性病设备表格
# ==========================


def build_chronic_table(data):

    table_html = """

    <style>

    /* 固定底部滚动条 */

    .bottom-scroll {

        position: fixed;

        bottom: 0;

        left: 0;

        width: 100%;

        height: 18px;

        overflow-x: auto;

        overflow-y: hidden;

        background: white;

        border-top:1px solid #ccc;

        z-index:9999;

    }


    .bottom-scroll div{

        height:1px;

    }


    /* 表格滚动区域 */

    .table-container{

        overflow-x:auto;

        width:100%;

        margin-bottom:30px;

    }


    table{

        border-collapse:collapse;

        width:max-content;

        min-width:100%;

    }


    th{

        background:#f2f2f2;

    }


    th,td{

        border:1px solid #ddd;

        padding:8px;

        white-space:nowrap;

    }


    </style>



    <div class="table-container"
         id="chronic-table">


    <table id="chronic-real-table">


    <thead>

    <tr>

    """



    # 表头

    for col in data.columns:

        table_html += f"""

        <th>
        {col}
        </th>

        """



    table_html += """

    </tr>

    </thead>


    <tbody>

    """



    # 数据

    for _,row in data.iterrows():

        table_html += "<tr>"


        for value in row:

            table_html += f"""

            <td>
            {value}
            </td>

            """


        table_html += "</tr>"


    table_html += """

    </tbody>

    </table>

    </div>


    <!-- 固定滚动条 -->

    <div class="bottom-scroll"
         id="bottom-scroll">


        <div id="scroll-width"></div>


    </div>



    <script>


    let table =
    document.getElementById(
        "chronic-table"
    );


    let bottom =
    document.getElementById(
        "bottom-scroll"
    );


    let scrollWidth =
    document.getElementById(
        "scroll-width"
    );



    // 设置底部滚动长度

    scrollWidth.style.width =
        table.scrollWidth + "px";



    // 双向同步

    bottom.addEventListener(
        "scroll",
        function(){

            table.scrollLeft =
                bottom.scrollLeft;

        }

    );


    table.addEventListener(
        "scroll",
        function(){

            bottom.scrollLeft =
                table.scrollLeft;

        }

    );


    </script>


    """


    return table_html



# ==========================
# 生成Dashboard
# ==========================


def build_dashboard():


    fault,reliability,chronic=load_data()


    figs=[

        fault_trend(fault),

        fault_type(fault),

        fault_level(fault),

        top_fault_device(fault),

        reliability_compare(reliability)

    ]



    html="""

<html>

<head>

<meta charset="utf-8">

<title>电力设备故障分析仪表板</title>

</head>


<body>


<h1>
电力设备运维故障分析仪表板
</h1>


"""


    for fig in figs:


        html += fig.to_html(

            full_html=False,

            include_plotlyjs="cdn"

        )



    html += """

<h2>
慢性病设备TOP10
</h2>

"""


    html += build_chronic_table(chronic)


    html+="""


</body>

</html>

"""


    RESULT_PATH.mkdir(

        parents=True,

        exist_ok=True

    )


    with open(

        OUTPUT_HTML,

        "w",

        encoding="utf-8"

    ) as f:


        f.write(html)



    print(
        "Dashboard生成完成:"
    )

    print(
        OUTPUT_HTML
    )



if __name__=="__main__":

    build_dashboard()
