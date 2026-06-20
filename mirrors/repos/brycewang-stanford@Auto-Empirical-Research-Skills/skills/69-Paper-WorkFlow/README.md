# 69 · Paper-WorkFlow — 经管 / 社科实证论文全流程总编排器

> 一个 **meta-orchestrator（总编排器）skill**：把「选题 → 设计 → 数据 → 计量识别与估计 →
> 表与图 → 写作初稿 → 全流程打磨 → 语言去 AI 味 → 模拟评审与修订 → 选刊与投稿 → 复盘交付」
> 这条端到端流水线**自动跑通**。它不重复实现任何子能力，而是**按阶段调用既有 skill / 派发
> 并行 subagent**，帮用户自动化完成一篇可投稿的实证论文。

本 skill 设计上**模仿并整合**了仓库里两套成熟范式（已获授权模仿
[`68-research-productivity-skills/do-agent`](../68-research-productivity-skills/do-agent/SKILL.md)）：

- **`do-agent` 的「多代理 + 上下文保护」执行范式** —— 子代理自己写盘、只回传状态摘要，主代理
  上下文极度节省；规划完即自动执行，无需逐步审批。
- **`67-econfin-workflow-toolkit/paper-pipeline` 的「固定顺序 + 断点续跑 + 交互档位」编排范式**
  —— 用 `workflow_state.json` 记录进度，可中断后从断点恢复，开跑前一次性问清交互档位。

---

## 它和隔壁 `Paper-WorkFlow/` 是什么关系？

| | 本目录 `69-Paper-WorkFlow/` | 隔壁 [`Paper-WorkFlow/`](../Paper-WorkFlow/) |
|---|---|---|
| 性质 | **可执行的 skill**（`SKILL.md`） | **演示物料**（PPTX + DiD 演示 Notebook） |
| 作用 | 真的把一篇论文从选题跑到投稿 | 给人讲清楚"实证论文工作流长什么样" |
| 何时用 | 想让 Claude 帮你**自动做论文** | 想**讲解 / 培训 / 汇报**这套流程 |

两者互补：先用隔壁的 PPTX 把流程讲清楚，再用本 skill 真正把流程跑起来。

---

## 这条流水线（Stage 0–9）

| Stage | 阶段 | 主要调用的 skill（均在 [`67-econfin-workflow-toolkit/`](../67-econfin-workflow-toolkit/)） |
|---|---|---|
| 0 | Intake & Setup | *(编排器本体：建工作区、定入口、问档位、写状态文件)* |
| 1 | 选题与设计 | `econfin-idea-finder` → `novelty-check` → `significance-search` → `journal-digest` → `econfin-proposal` |
| 2 | 数据 | `data-fetcher` → `data-cleaning` |
| 3 | 计量识别与估计 | 按设计择一：`did-analysis` / `iv-estimation` / `rdd-analysis` / `synthetic-control` / `panel-data` / `ols-regression` / `time-series` / `ml-causal`（+ StatsPAI MCP） |
| 4 | 表与图 | `table` + `figure` |
| 5 | 写作初稿 | `paper-writer` |
| 6 | 全流程打磨 | `paper-pipeline`（内部：polish → self-revise → style → polish → reference-verify） |
| 7 | 语言与去 AI 味 | `readability` / `fix-chinese` + 去 AIGC 集合（44/47/48/49） |
| 8 | 模拟评审与修订 | `referee-report` → `paper-referee-revise` |
| 9 | 选刊与投稿 | `paper-submission` + `reference-verify`（终审） |

完整每阶段操作手册见 [`references/stage-playbook.md`](references/stage-playbook.md)；
「任务 → 用哪个 skill」的全量路由（覆盖仓库 69 个集合）见
[`references/skill-map.md`](references/skill-map.md)。

---

## 怎么用

在 Claude Code 里直接说触发语，并把你**手头已有的东西**告诉它（决定从哪个阶段切入）：

```text
/paper-workflow 我想做"绿色信贷政策对企业创新的影响"，目标期刊《经济研究》
/paper-workflow 这是我的计划书 ./proposal.md，帮我一条龙做到投稿
/paper-workflow 数据在 ./panel.csv，设计是 DiD，先把基准和稳健性跑出来
/paper-workflow 初稿在 ./paper/main.tex，从打磨开始
```

**入口路由**：你带来一句话想法 → 从 Stage 1 开始；带来计划书 → 从 Stage 2；带来数据 →
Stage 3；带来初稿 → Stage 6；带来初稿 + 审稿意见 → Stage 8。不用每次都从头跑。

**交互档位**（开跑前问一次）：

- `全自动` —— 只在最终交付时汇报（贴近 `do-agent` 的无人值守）。
- `阶段确认`（**推荐**）—— 每阶段末给摘要卡、等放行再进下一阶段。
- `全程交互` —— 每个子 skill 跑自己原生的逐项审批，投稿前终版用。

---

## 产出（一个自包含工作区）

运行后在 `paper_workspace/<研究短名>_<时间戳>/` 下沉淀全部产物：计划书、清洗后数据 + codebook、
分析代码、出版级表图、`main.tex` + `ref.bib`、response letter、期刊清单 + cover letter，以及一份
`FINAL_REPORT.md` 复盘表。目录布局与 `workflow_state.json` 字段定义见
[`references/workspace-and-state.md`](references/workspace-and-state.md)。

```text
skills/69-Paper-WorkFlow/
├── SKILL.md                              # 总编排器（入口）
├── README.md                             # 本文件
├── references/
│   ├── stage-playbook.md                 # 10 阶段逐阶段操作手册
│   ├── skill-map.md                      # 任务 → skill 全量路由表
│   └── workspace-and-state.md            # 工作区布局 + 状态字段 + 子代理 I/O 约定
└── assets/
    ├── init_workspace.sh                 # 一键铺出工作区骨架（拒绝覆盖已存在路径）
    └── workflow_state.template.json      # 进度状态文件模板
```

---

## 设计纪律（为什么这样设计）

1. **能调用就不要重写**。仓库已有 47 个覆盖全流程的 skill，本编排器只负责"在对的时点把对的
   skill 喂对的输入"，绝不复制它们的逻辑。
2. **上下文保护优先**。任何会把大段文本灌回主代理的操作，一律改成"子代理写盘 + 回传摘要"。
3. **真实优先，绝不编造**。引用核验交给 `reference-verify`，数据来源交给 `data-fetcher`，计量结论
   以真实运行结果为准（可走 StatsPAI MCP 链路自检稳健性）。
4. **失败要回退而非硬写成功**。平行趋势不过 / 弱工具 / 不显著时自动切备选方案，并在阶段闸门标红
   告知（借鉴 `China-CF-study` 纪律）。
5. **人类决策点守在阶段闸门**。选题定标题、定目标期刊、识别策略拍板、投稿前终审——除非全自动档位
   且已显式授权，否则这些点必须经人放行。

---

## 致谢与许可

- 执行范式模仿自 `do-agent`（本仓库授权模仿），编排范式来自 `67-econfin-workflow-toolkit/paper-pipeline`。
- 本目录为编排器，本身不内置任何被编排 skill；运行时按需调用 `67/` 等集合里的 skill。混合来源
  集合的再分发请各自核对其上游许可（见 [`67/README.md`](../67-econfin-workflow-toolkit/README.md) 的许可注记）。

> 返回仓库技能总览：[`../`](../) ｜ 本演示流程配套讲义：[`../Paper-WorkFlow/`](../Paper-WorkFlow/)
