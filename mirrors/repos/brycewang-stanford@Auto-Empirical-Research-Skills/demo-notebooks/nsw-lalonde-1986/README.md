# NSW 实验基准 + LaLonde 问题 / The NSW benchmark, and LaLonde's problem

**同样的 185 名受训者，两个对照组，两个符号相反的答案。**
The same 185 trained men, two comparison groups, two answers of opposite sign.

```bash
python3 demo-notebooks/nsw-lalonde-1986/replicate_nsw.py
```

## 结果 / Results

| | 对照组 / Comparison group | n | 估计 / Estimate |
|---|---|---:|---:|
| **实验 / Experiment** | NSW 随机对照 / randomized controls | 260 | **+$1,794** |
| **观测 / Observational** | PSID-1 比较组 / comparison sample | 429 | **−$635** |

选择偏误 = **−$2,429**。这就是 LaLonde (1986)：
非实验比较组没能复现实验答案——**连符号都反了**。
匹配、加权、双重稳健那一整套文献，都是这个发现的后果。

| 锚点 / Anchor | 值 / Value | 判定 |
|---|---:|---|
| 受训组样本量 / treated n | 185 | ✅ |
| 实验对照样本量 / control n | 260 | ✅ |
| **实验 ATT（re78 简单均值差）** | **+1,794.34** | ✅ 对上文献的 1,794 |
| 随机化检验：处理前 re74 差 | −$11 | ✅ 平衡 |
| PSID 组：处理前 re74 差 | −$3,524 | ✅ 严重不平衡（且**在看结果之前就能发现**） |
| 两个估计用的是同一批受训者 | 逐变量核对 | ✅ |

## 为什么这个 demo 值得存在 / Why this one matters

在此之前，**+$1,794 这个数字在仓库里只是一个手抄的文献常数**——写在
[`benchmark/tasks/lalonde-recovery.toml`](../../benchmark/tasks/lalonde-recovery.toml)
的 `experimental_att` 里。手抄的常数是一个**声称**。

这个脚本把它**从随机化数据里算出来**：185 减 260，没有模型，没有协变量。
于是那道 benchmark 题所对照的基准值变成了**可复现的**，而不是被断言的。
[`tests/test_nsw_replication.py`](../../tests/test_nsw_replication.py) 把两者
钉在一起——改常数不改数据（或反过来）都会让测试挂掉。

Until now the +$1,794 experimental benchmark existed in this repo only as a
hand-transcribed literature constant. A transcribed constant is a claim. This
derives it from the randomized data, so the number the benchmark grades against
is reproducible rather than asserted, and a test pins the two together.

## 一个可以在看结果之前就发现的问题 / A symptom available before the outcome

脚本跑的随机化检验不是装饰：

- 实验组 vs 实验对照，处理前 1974 年收入差 **−$11**（基数约 $2,100）。随机化生效。
- 同一批受训者 vs PSID 比较组，同一个差 **−$3,524**。

第二个数字**不需要看 re78 就能算出来**。观测研究失败的症状在结果变量之前
就已经暴露了——这正是平衡表应该出现在结果表之前的原因。

## 与 `lalonde-recovery` benchmark 的关系 / How this relates to the benchmark task

| | 问什么 | 数据 |
|---|---|---|
| [`benchmark/tasks/lalonde-recovery.toml`](../../benchmark/tasks/lalonde-recovery.toml) | **你的**流水线能否发现不平衡、拒绝把 −$635 当因果效应、并在调整后回到实验基准附近 | `_lalonde_data.csv`（受训组 + PSID-1） |
| **本目录** | 那个实验基准**本身**从哪来 | Dehejia 的 NSW 实验两臂 |

Dehejia & Wahba (1999) 的贡献是：在这个 re74 子样本上，
以处理前收入为条件的倾向得分方法**可以**把观测估计拉回实验值附近。
那是 benchmark 题在考的事；本目录只负责把标尺本身做实。

## 数据来源 / Data provenance

见 [`data/PROVENANCE.md`](data/PROVENANCE.md)：下载日期、URL、SHA-256、列顺序，
未做任何修改。

## 引用 / Citation

- LaLonde, Robert J. (1986). "Evaluating the Econometric Evaluations of Training
  Programs with Experimental Data." *American Economic Review* 76(4), 604–620.
- Dehejia, Rajeev H. and Sadek Wahba (1999). "Causal Effects in Nonexperimental
  Studies: Reevaluating the Evaluation of Training Programs." *JASA* 94(448),
  1053–1062.
