# 电力设备运维与故障分析项目

## 项目简介

本项目基于 2023 年 1 月至 2026 年 5 月的电力设备运维数据，围绕设备台账、运行参数、故障工单、巡检记录、检修计划和备品备件六类业务数据，完成从数据质量评估、故障规律分析到设备健康评价和运维策略建议的全流程分析。

项目目标是通过多表关联和指标量化，识别设备故障风险、巡检与检修管理短板、备件保障问题及成本异常，为状态检修、重点巡检和备件储备提供数据支持。

### 核心分析内容

- 数据质量评估与探索性数据分析（EDA）
- 故障多维统计、故障原因分析和月度/季度趋势分析
- MTBF、MTTR、设备可用率及可靠性分层分析
- 故障前运行参数变化与高负荷关联分析
- 重复故障、慢性病设备和高风险设备识别
- 巡检覆盖率、评分趋势、缺陷发现与消除情况分析
- 检修完成率、及时率、延期、工时、费用和参数改善分析
- 备件消耗、库存周转、库存预警、ABC 分类和采购周期分析
- 运维成本构成、趋势、异常增长、设备类型和变电站成本分析
- 设备健康综合评分、风险分级、运维优化建议和综合可视化展示

## 环境配置教程

### 1. 创建环境

```bash
conda create -n power_device_env python=3.9 -y
conda activate power_device_env
```

### 2. 安装依赖

在项目根目录运行：

```bash
pip install -r requirements.txt
```

主要依赖包括 pandas、numpy、openpyxl、matplotlib、seaborn、plotly、scikit-learn、jupyter、notebook、tqdm 和 pyyaml。

### 3. 中文字体

静态图表优先使用 `Microsoft YaHei` 或 `SimHei`。如果中文显示为方框，请安装中文字体，或修改脚本中的 Matplotlib 字体配置。

### 4. 目录结构

```text
Power_Device_Operation_Analysis/
├── data/raw/       # 原始 Excel 数据
├── src/            # 分析脚本
├── results/        # Week1 至 Week4 结果
├── reports/        # 周报、报告、建议方案和复盘
├── dashboard/      # Plotly 综合大屏
├── notebooks/      # Notebook 过程文件
├── requirements.txt
└── README.md
```

## 数据集说明

原始文件为 `data/raw/电力设备运维数据_2023-2026.xlsx`，覆盖 2023 年 1 月至 2026 年 5 月，共 41 个月，包含六张工作表：

| 工作表 | 内容 | 关键字段 |
|---|---|---|
| 设备台账 | 设备基础档案 | 设备编号、类型、电压等级、变电站、投运日期、设计寿命 |
| 运行参数 | 月度运行状态 | 负荷率、油温、绕组温度、绝缘电阻、介质损耗角、局放量、SF6 气压 |
| 故障工单 | 故障和修复记录 | 故障时间、故障类型、原因、严重等级、修复耗时、修复费用 |
| 巡检记录 | 巡检、评分和缺陷 | 巡检日期、巡检评分、缺陷类型、缺陷等级、处理状态 |
| 检修计划 | 计划和实际检修 | 检修类型、计划/实际日期、是否按时、延期天数、工时、费用 |
| 备品备件 | 消耗、库存和采购 | 月消耗、期末库存、安全库存、消耗金额、采购周期 |

跨表分析主要以 `设备编号` 关联，时间字段按故障时间、巡检日期、检修日期和记录年月匹配。巡检数据没有缺陷实际消除日期，因此项目不推算缺陷平均消除耗时，而使用缺陷消除率和处理状态开展分析。

## 分析运行指南

以下命令均在项目根目录执行：

```bash
conda activate power_device_env
```

### Week1：数据质量与 EDA

```bash
python src/generate_data_dictionary.py
python src/data_quality_report.py
python src/eda_analysis.py
```

输出：`results/week1/`、`results/EDA/`。

### Week2：故障与可靠性

```bash
python src/fault_analysis.py
python src/reliability_analysis.py
python src/fault_parameter_analysis.py
python src/chronic_fault_analysis.py
python src/fault_dashboard.py
```

输出：`results/week2/`，包括故障统计、可靠性指标、故障参数关联、重复故障清单和 Dashboard。

### Week3：运维效能与备件

```bash
python src/inspection_analysis.py
python src/maintenance_efficiency_analysis.py
python src/spare_parts_analysis.py
python src/operation_cost_analysis.py
python src/comprehensive_operation_analysis.py
```

输出：`results/week3/`，包括巡检、检修、备件、成本和四维综合效能结果。

### Week4：健康评价与综合展示

```bash
python src/health_evaluation.py
python dashboard/app.py
```

输出：`results/week4/health/` 和 `dashboard/week4_dashboard.html`。后者是 Plotly 交互式 HTML，可直接用浏览器打开，无需启动额外服务。

## 核心成果展示

### 运维 KPI

| 指标 | 实际结果 |
|---|---:|
| 变电站巡检覆盖率 | 100.00% |
| 缺陷发现率 | 12.21% |
| 缺陷消除率 | 65.11% |
| 计划检修完成率 | 100.00% |
| 总体检修及时率 | 约 81.11% |
| 延期检修次数 | 857 次 |
| 库存不足备件 | 21 类 |
| 采购周期较长备件 | 9 类 |

Week3 综合评分：巡检 85.26 分、检修 87.39 分、备件 46.43 分、成本 100.00 分，总体 79.77 分。备件保障是当前优先改进方向。

### 设备健康评价

健康模型覆盖故障风险、可靠性、运行状态、巡检状态、检修状态和基础风险六个维度，权重为 25%、20%、20%、15%、10%、10%。共评价 439 台设备：优 13 台、良 327 台、注意 79 台、预警 20 台、高风险 0 台。

主要文件：

- `results/week4/health/设备健康评分排名.csv`
- `results/week4/health/高风险设备清单.csv`
- `results/week4/health/健康等级分布.png`
- `results/week4/health/高风险设备Top10.png`
- `dashboard/week4_dashboard.html`
- `reports/设备运维优化建议方案.md`
- `reports/项目复盘总结.md`

项目当前已生成 65 个 PNG/HTML 可视化成果，覆盖 EDA、故障、可靠性、巡检、检修、备件、成本、综合效能和设备健康评价主题。
