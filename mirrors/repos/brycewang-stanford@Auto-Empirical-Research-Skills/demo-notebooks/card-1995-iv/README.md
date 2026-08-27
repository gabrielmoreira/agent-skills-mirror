# Card (1995) 端到端复现 / End-to-End Replication

**一条命令、零依赖，从 vendored NLSYM 样本复现最著名的教育回报 IV，并对照发表值自动打分。**
One command, zero dependencies: reproduce the best-known returns-to-schooling IV
from the vendored NLSYM extract, auto-scored against the published values.

```bash
python3 demo-notebooks/card-1995-iv/replicate_card1995.py
```

## 结果 / Results

| 量 / Quantity | 论文 / Published | 本复现 / This run | 判定 |
|---|---:|---:|---|
| 估计样本量 / estimation sample | 3,010 | 3,010 | ✅ 精确 |
| OLS 教育回报 / OLS return | 0.075 | 0.0747 | ✅ |
| OLS 标准误 / OLS s.e. | 0.003 | 0.0035 | ✅ |
| 第一阶段 `nearc4` 系数 | 0.32 | 0.3199 | ✅ |
| 第一阶段标准误 / s.e. | 0.088 | 0.0879 | ✅ |
| **2SLS 教育回报 / IV return** | **0.132** | **0.1315** | ✅ |
| **2SLS 标准误 / IV s.e.** | **0.055** | **0.0550** | ✅ |

外加两项论证级检查（不是数字，而是论文的**主张**）：

- `iv_exceeds_ols` — IV 0.1315 > OLS 0.0747（+0.0568）。这正是论文的要点：
  用"是否在四年制大学附近长大"做工具变量，教育回报**上升**近一倍，与
  简单的能力偏误故事预测的方向相反。只复现出 0.075 什么也没证明。
- `instrument_relevant` — 第一阶段 F = 13.26。

## 为什么不只是"跑一遍回归" / What a replication owes that a point estimate does not

1. **标准误，不只是系数。** 0.132 (s.e. 0.055) 和 0.132 (s.e. 0.005) 是两篇不同的论文。
   2SLS 的方差必须用**结构残差**（`y − Xβ̂`，其中 X 是**真实**教育年限），
   而不是第二阶段那个"对拟合值回归"的残差。
   把手工两阶段的第二步当普通 OLS、直接读它输出的标准误，是最经典的手工 2SLS 错误。
   脚本把这个错误的数值一并算出来（`iv_se_naive_second_stage`）：**0.0565 vs 正确的 0.0550**，
   让错误的大小可见，而不是只写一句警告。

2. **工具变量强度。** F = 13.26 过了 10 的经验阈值，但远没到
   Anderson–Rubin 等价标准想要的 ~23。Card 本人对此就很谨慎。
   一份省掉第一阶段的"复现"没有复现这篇论文的论证。

3. **论文真正要讲的那个对比。** `iv_exceeds_ols` 被单独检查——
   一条流水线完全可能两个点估计都命中，却把结论埋掉。

## 数据来源 / Data provenance

复用仓库已 vendor 的 [`demo-StatsPAI-skill/data/card.csv`](../../demo-StatsPAI-skill/data/card.csv)
（3,010 × 34 的标准 NLSYM extract，来自 `wooldridge` R 包）。
样本限制为 1976 年报告了工资的男性（`lwage` 非缺失）——这正是 3,613 行的 extract
缩到 3,010 的原因。

工资方程控制变量：`exper`、`expersq`、`black`、`south`、`smsa`、`smsa66`，
以及 1966 年地区虚拟变量 `reg662`–`reg669`（`reg661` 为省略组）。

## 与仓库其它部分的关系 / How this relates to the rest of the repo

| | 做什么 | 数据 | 真值来自 |
|---|---|---|---|
| `benchmark/tasks/card-iv-recovery.toml` | 给**任意 agent** 的评分题：能否拿到 IV>OLS 并报告第一阶段 | 同一份 `card.csv` | 部分从数据重算 + 文献常数 |
| **本目录** | 证明**这条自动化流水线**能从数据走到发表值 | 同一份 `card.csv` | 论文报告值 |
| [`../card-krueger-1994/`](../card-krueger-1994/) | 同样的事，换成最低工资 DiD | 官方 `public.dat` | 论文原表逐格转录 |
| [`../../demo-StatsPAI-skill/`](../../demo-StatsPAI-skill/) | 完整 StatsPAI 八步流水线（表/图/复现包） | 同一份 `card.csv` | — |

前两者的区别值得说清楚：benchmark 问的是"**你**能不能做对"，
本目录答的是"**我们**确实做到了"。

复现数字由 [`tests/test_card1995_replication.py`](../../tests/test_card1995_replication.py)
守护，进 `make test`；脚本本身在错过任一发表锚点时以非零码退出。

## 引用 / Citation

Card, David (1995). "Using Geographic Variation in College Proximity to Estimate
the Return to Schooling." In L.N. Christofides, E.K. Grant and R. Swidinsky
(eds.), *Aspects of Labour Market Behaviour: Essays in Honour of John
Vanderkamp*. University of Toronto Press.
