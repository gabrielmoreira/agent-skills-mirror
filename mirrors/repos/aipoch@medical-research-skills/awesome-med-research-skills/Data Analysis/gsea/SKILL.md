---
name: gsea
description: 对按统计量排序的基因列表执行 GSEA 分析，输出富集结果表、运行分数表和绘图结果。
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## 何时读取外部文件

| 情况 | 读取文件 | 目的 |
|---|---|---|
| 需要了解算法细节 | `references/algorithm.md` | 统计方法与公式 |
| 需要执行分析 | `scripts/main.R` | 获取完整命令 |
| 遇到报错 | `references/troubleshooting.md` | 查找解决方案 |
| 需要 CLI 示例 | `references/cli-guide.md` | 参数用法示例 |

## 适用场景

适用于：
- 对按统计量排序的基因列表执行 GSEA 分析
- 基于已有 `enrichGSEA.csv` 和 `gsea_running_scores.csv` 生成富集曲线图
- 使用 `tests/data/sample_deg_results.csv` 做最小可运行验证

不适用于：
- 原始表达矩阵的差异分析
- 单样本 ssGSEA
- 网络分析或多组学整合分析

## 使用方法

分析模式：
`Rscript scripts/main.R --input tests/data/sample_deg_results.csv --outdir ./GSEA_analysis --type KEGG --species human --seed 42 --timeout 300`

绘图模式：
`Rscript scripts/main.R --running_file ./GSEA_analysis/Table/gsea_running_scores.csv --enrich_file ./GSEA_analysis/Table/enrichGSEA.csv --plot_output ./GSEA_analysis/plot/gsea_plot.pdf --top_n 5 --plot_format pdf --seed 42 --timeout 300`

说明：详见 `references/cli-guide.md`。

模式选择说明：
- 仅提供 `--input` 时进入分析模式
- 同时提供 `--running_file` 和 `--enrich_file` 时进入绘图模式
- 若同时提供分析参数与绘图参数，则绘图模式优先，分析模式会被跳过，并输出警告信息

## 参数说明

### 分析模式参数

| 短参数 | 长参数 | 类型 | 默认值 | 是否必填 | 说明 |
|---|---|---|---|---|---|
| `-i` | `--input` | character | `NULL` | 是 | 输入 CSV 文件 |
| `-o` | `--outdir` | character | `GSEA_analysis` | 否 | 输出目录 |
| `-g` | `--gene_col` | character | `name` | 否 | 基因列名 |
| `-f` | `--fc_col` | character | `logFC` | 否 | 排序统计量列名 |
| `-t` | `--type` | character | `KEGG` | 否 | 基因集类型：`KEGG`、`HALLMARKS`、`GO_BP`、`GO_MF`、`GO_CC`；预载 RDS 中会自动将 `HALLMARKS` 映射到资产键 `Hallmarks` |
| `-s` | `--species` | character | `human` | 否 | 物种：`human`、`mouse`、`rat` |
| `-p` | `--pvalue_cutoff` | numeric | `0.05` | 否 | 显著性阈值 |
| `-m` | `--method` | character | `fgsea` | 否 | GSEA 方法：`fgsea` 或 `DOSE` |
| `-c` | `--chunk_size` | numeric | `1000` | 否 | 大基因集转换时的分块大小 |
| `-r` | `--rds_path` | character | `NULL` | 否 | 预存基因集 RDS 路径 |
| `-v` | `--verbose` | logical | `FALSE` | 否 | 输出详细日志 |
|  | `--seed` | integer | `42` | 否 | 随机种子 |
|  | `--timeout` | integer | `300` | 否 | 超时秒数，`<=0` 表示不限制 |
| `-h` | `--help` | logical | `FALSE` | 否 | 显示帮助 |

### 绘图模式参数

| 短参数 | 长参数 | 类型 | 默认值 | 是否必填 | 说明 |
|---|---|---|---|---|---|
|  | `--running_file` | character | `NULL` | 是 | `gsea_running_scores.csv` 路径 |
|  | `--enrich_file` | character | `NULL` | 是 | `enrichGSEA.csv` 路径 |
|  | `--plot_output` | character | `gsea_plot.pdf` | 否 | 输出图文件路径 |
|  | `--plot_width` | numeric | `8` | 否 | 图宽 |
|  | `--plot_height` | numeric | `6` | 否 | 图高 |
|  | `--plot_format` | character | `pdf` | 否 | 输出格式：`pdf` 或 `png` |
|  | `--top_n` | numeric | `1` | 否 | 未指定 `geneSetID` 时绘制前 N 条通路 |
|  | `--rank_by` | character | `p.adjust` | 否 | 通路排序列 |
|  | `--geneSetID` | character | `""` | 否 | 逗号分隔的通路 ID |
|  | `--plot_title` | character | `""` | 否 | 图标题 |
|  | `--colors` | character | `#4DBBD5,#E64B35,#00A087,#F39B7F,#3C5488,#8491B4` | 否 | 颜色列表 |
|  | `--base_size` | numeric | `11` | 否 | 基础字号 |
|  | `--subplots` | character | `1,2,3` | 否 | 显示子图编号 |
|  | `--rel_heights` | character | `1.5,0.8,1` | 否 | 子图高度比例 |
|  | `--NES_table` | logical | `TRUE` | 否 | 显示 NES 注释 |
|  | `--no_NES_table` | logical | `FALSE` | 否 | 关闭 NES 注释 |
|  | `--NES_label_size` | numeric | `4` | 否 | NES 注释字号 |
|  | `--NES_label_x` | numeric | `0.75` | 否 | NES 注释横向位置 |
|  | `--NES_label_y` | numeric | `0.75` | 否 | NES 注释纵向位置 |
|  | `--NES_label_color` | character | `black` | 否 | NES 注释颜色 |
|  | `--NES_label_hjust` | numeric | `0` | 否 | NES 注释水平对齐 |
|  | `--NES_label_vjust` | numeric | `1` | 否 | NES 注释垂直对齐 |
|  | `--line_width` | numeric | `1` | 否 | ES 线宽 |
|  | `--dot_size` | numeric | `1.2` | 否 | ES 点大小 |
|  | `--legend_position` | character | `auto` | 否 | 图例位置 |
|  | `--legend_x` | numeric | `0.02` | 否 | 内嵌图例横坐标 |
|  | `--legend_y` | numeric | `0.02` | 否 | 内嵌图例纵坐标 |
|  | `--legend_just_x` | numeric | `0` | 否 | 图例横向对齐 |
|  | `--legend_just_y` | numeric | `0` | 否 | 图例纵向对齐 |
|  | `--legend_text_size` | numeric | `9` | 否 | 图例文字大小 |
|  | `--legend_key_size` | numeric | `0.6` | 否 | 图例键大小 |
|  | `--legend_bg_alpha` | numeric | `0` | 否 | 图例背景透明度 |
|  | `--grid_major_color` | character | `grey92` | 否 | 主网格颜色 |
|  | `--grid_minor_color` | character | `grey92` | 否 | 次网格颜色 |
|  | `--ylab_es` | character | `Enrichment Score` | 否 | ES 面板纵轴标题 |
|  | `--ylab_rank` | character | `Ranked List Metric` | 否 | 排名面板纵轴标题 |
|  | `--xlab_rank` | character | `Rank in Ordered Dataset` | 否 | 排名面板横轴标题 |
|  | `--hit_height` | numeric | `1` | 否 | 命中条高度 |
|  | `--hit_gap` | numeric | `0` | 否 | 命中条间距 |
|  | `--hit_linewidth` | numeric | `0.5` | 否 | 命中条线宽 |
|  | `--rank_bar_alpha` | numeric | `0.9` | 否 | 排名条透明度 |
|  | `--rank_bar_height_ratio` | numeric | `0.3` | 否 | 排名条高度比例 |
|  | `--rank_metric_segment_color` | character | `grey` | 否 | 排名线颜色 |
|  | `--rank_metric_segment_width` | numeric | `0.3` | 否 | 排名线宽 |
|  | `--rank_metric_segment_alpha` | numeric | `1` | 否 | 排名线透明度 |
|  | `--pvalue_table` | logical | `FALSE` | 否 | 显示 P 值表 |
|  | `--ES_geom` | character | `line` | 否 | ES 绘制方式：`line` 或 `dot` |
|  | `--verbose` | logical | `FALSE` | 否 | 输出详细日志 |
|  | `--seed` | integer | `42` | 否 | 随机种子 |
|  | `--timeout` | integer | `300` | 否 | 超时秒数，`<=0` 表示不限制 |
| `-h` | `--help` | logical | `FALSE` | 否 | 显示帮助 |

## 输入格式

分析模式输入为 CSV 文件，至少包含两列：
- 基因列，默认列名为 `name`
- 排序统计量列，默认列名为 `logFC`

示例：
```csv
name,logFC,pvalue,padj
TP53,2.5,0.001,0.01
BRCA1,1.8,0.005,0.02
EGFR,-1.2,0.01,0.05
```

取值约束：
- `type` 支持 `KEGG`、`HALLMARKS`、`GO_BP`、`GO_MF`、`GO_CC`
- 当使用预载 RDS 时，`HALLMARKS` 会自动匹配资产中的 `Hallmarks` 键名
- `species` 支持 `human`、`mouse`、`rat`

## 输出文件

| 文件名 | 格式 | 内容说明 |
|---|---|---|
| `data/GSEA_list.rda` | RDA | 完整 GSEA 结果对象 |
| `Table/enrichGSEA.csv` | CSV | 富集结果表 |
| `Table/gsea_running_scores.csv` | CSV | 运行分数表；若无富集结果则输出空表头文件 |
| `plot/` | directory | 绘图输出目录 |
| `session_info.txt` | TXT | R 版本与包版本信息 |

`enrichGSEA.csv` 主要包含：`ID`、`Description`、`NES`、`pvalue`、`p.adjust`、`core_enrichment`。

## 错误处理

常见错误码：
- `SKILL_FILE_NOT_FOUND`：输入文件不存在
- `SKILL_MISSING_COLUMNS`：缺少必要列
- `SKILL_EMPTY_DATA`：输入数据为空或过滤后为空
- `SKILL_INVALID_PARAMETER`：参数值不合法
- `SKILL_PACKAGE_NOT_FOUND`：依赖包未安装
- `SKILL_ANALYSIS_FAILED`：分析重试后仍失败

排查文档：`references/troubleshooting.md`

退出状态码：
- `0`：运行成功
- `1`：运行失败

## 测试方法

最小测试数据集：`tests/data/sample_deg_results.csv`

最小运行命令：
`Rscript scripts/main.R --input tests/data/sample_deg_results.csv --outdir ./test_output --type KEGG --species human --seed 42 --timeout 300 --verbose`

预期输出：
- `./test_output/data/GSEA_list.rda`
- `./test_output/Table/enrichGSEA.csv`
- `./test_output/Table/gsea_running_scores.csv`
- `./test_output/session_info.txt`
- 若无显著富集结果，`gsea_running_scores.csv` 仍会生成，但只包含表头
- 退出状态码为 `0`