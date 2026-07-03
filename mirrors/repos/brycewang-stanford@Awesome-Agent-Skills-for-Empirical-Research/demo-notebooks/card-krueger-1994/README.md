# Card & Krueger (1994) 端到端复现 / End-to-End Replication

**一条命令、零依赖，从官方原始数据复现最著名的最低工资 DiD，并对照发表值自动打分。**
One command, zero dependencies: reproduce the most famous minimum-wage DiD from the official raw data, auto-scored against the published values.

```bash
python3 demo-notebooks/card-krueger-1994/replicate_ck1994.py
```

## 结果 / Results

| 量 / Quantity | 论文 / Published | 本复现 / This run | 判定 |
|---|---:|---:|---|
| wave-1 mean FTE, PA（Table 3 r1） | 23.33 | 23.33 | ✅ 精确 |
| wave-1 mean FTE, NJ | 20.44 | 20.44 | ✅ 精确 |
| wave-2 mean FTE, PA（Table 3 r2） | 21.17 | 21.17 | ✅ 精确 |
| wave-2 mean FTE, NJ | 21.03 | 21.03 | ✅ 精确 |
| **DiD（NJ−PA），Table 3 r3 col (iii)** | **+2.76** | **+2.75** | ✅ 论文行 3 为未舍入行差的显示舍入 |
| Table 4 样本量 / sample size | 357 | 357 | ✅ 精确 |
| NJ dummy, 无控制（Table 4 model i） | +2.33 | +2.33 | ✅ 精确 |
| **NJ dummy, chain+ownership 控制（model ii）** | **+2.30** | **+2.30** | ✅ 精确 |

评分器（Paper-WorkFlow 复现基准）判定：**PERFECT** —— sign-correct / perfect / partial-or-better 三档均 100%：

```bash
python3 skills/69-Paper-WorkFlow/evals/check_replication_accuracy.py \
    --case skills/69-Paper-WorkFlow/evals/replication_cases/card_krueger_1994_minwage.json \
    --candidate demo-notebooks/card-krueger-1994/estimates.json
```

## 数据来源 / Data provenance

`data/` 目录 vendor 自 David Card 官网公开发布的 `njmin.zip`
（https://davidcard.berkeley.edu/data_sets.html ，*Myth and Measurement* 第 2 章
的 NJ–PA 调查数据）：410 家快餐门店、两波访谈的定宽 ASCII 文件 `public.dat`、
`codebook`、原始 `read.me` 与作者的 `check.sas`。下载日期 2026-07-02，未做任何修改。

## 方法说明 / Method notes

- **FTE 定义**（论文 p. 775）：全职员工 + 经理/副经理 + 0.5 × 兼职员工。
- **关店处理**（Table 3 注）：6 家永久关闭门店 wave-2 就业记 0；4 家临时关闭
  （装修/修路/商场火灾）与 1 家拒访记缺失。
- **Table 4 样本**：两波就业与起薪数据齐全的 357 家门店（永久关店保留，FTE2=0）。
- 全部计算为纯 Python 标准库（定宽解析 + 正规方程 OLS），任何 Python 3 可跑。
- 复现数字由 [`tests/test_ck_replication.py`](../../tests/test_ck_replication.py)
  守护，进 `make test`；脚本本身在错过任一发表锚点时以非零码退出。

## 为什么这件事重要 / Why this matters

复现套件里的 gold 值是从论文原表逐格转录的事实；这个演示证明**同一条自动化流水线
能从原始数据走到这些数字**。声称（"能复现已发表结果"）与证据（本目录）之间没有缝隙。
The golds are facts transcribed from the published tables; this demo shows the same
automated pipeline reaches those numbers from the raw data — no gap between claim
and evidence.
