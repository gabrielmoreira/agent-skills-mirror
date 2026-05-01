---
name: prd-studio
description: 'PRD automation, PRD 全流程。Use when: "帮我写个 PRD 并审查通过"、"自动完成 PRD"、"PRD 全流程"。'
---

# PRD Studio - PRD 全自动工作室

## 定位

你是一个 **PRD 工作流编排器（Orchestrator）**。你的职责是：

1. 协调 Writer 和 Reviewer 两个角色
2. 通过隔离的 subagent 执行，确保上下文不污染
3. 自动完成"写 → 审 → 改 → 审"循环
4. 直到准出通过或达到最大迭代次数

## 核心原则

1. **隔离执行**：每次写作/审查都启动新的 subagent，上下文独立
2. **文件传递状态**：PRD 和审查报告通过文件共享，不通过对话上下文
3. **自动循环**：无需人工触发下一步，全自动流转
4. **有限迭代**：最多 3 轮修改，防止无限循环
5. **透明进度**：每个阶段都输出进度信息

## 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRD Studio 工作流                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户输入需求                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 1: 初始化                         │                   │
│  │  - 确认需求和 PRD 类型                   │                   │
│  │  - 创建 workflow/ 目录                   │                   │
│  │  - 初始化 workflow/status.md             │                   │
│  └─────────────────────────────────────────┘                   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 2: Writer Subagent (隔离)         │                   │
│  │  - 读取 references/writer/guide.md       │                   │
│  │  - 读取对应的 PRD 模板                   │                   │
│  │  - 生成 PRD → workflow/prd.md            │                   │
│  └─────────────────────────────────────────┘                   │
│       │ subagent 完成，上下文销毁                               │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 3: Reviewer Subagent (隔离)       │                   │
│  │  - 读取 references/reviewer/guide.md     │                   │
│  │  - 读取 workflow/prd.md                  │                   │
│  │  - 审查 → workflow/review-report.md      │                   │
│  └─────────────────────────────────────────┘                   │
│       │ subagent 完成，上下文销毁                               │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 4: 结果判断 (Orchestrator)        │                   │
│  │  - 解析 Reviewer 的 AGENT-RESULT 块      │                   │
│  │  - 基于 verdict/p0/p1 做流转判定         │                   │
│  └─────────────────────────────────────────┘                   │
│       │                                                         │
│       ├─── 准出通过 ───► Phase 5: 完成                          │
│       │                                                         │
│       └─── 有问题 且 迭代 < 3 ───┐                              │
│                                  │                              │
│       ┌──────────────────────────┘                              │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  回到 Phase 2: Writer(round+1) (隔离)    │                   │
│  │  - 读取 workflow/prd.md                  │                   │
│  │  - 读取 workflow/review-report.md        │                   │
│  │  - 修复问题 + 更新 PRD                   │                   │
│  │  - 保存 → workflow/prd.md                │                   │
│  └─────────────────────────────────────────┘                   │
│       │                                                         │
│       └──────► 回到 Phase 3 (Reviewer)                         │
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 5: 完成                           │                   │
│  │  - 输出最终 PRD 路径                     │                   │
│  │  - 输出准出证书或遗留问题                │                   │
│  │  - 更新 workflow/status.md               │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 初始化

### 1.1 确认输入类型和需求

**首先判断输入类型**：
- 如果用户提供了 BRD 文件路径 → 进入 **1:N 拆分评估流程**
- 如果用户直接描述需求 → 进入 **单 PRD 流程**

**使用 AskUserQuestion 确认**：

```yaml
questions:
  - question: "输入类型是什么？"
    header: "输入类型"
    multiSelect: false
    options:
      - label: "BRD 文件"
        description: "我有 BRD 文档，需要转换为 PRD"
      - label: "需求描述"
        description: "我直接描述需求，生成 PRD"
  - question: "这个 PRD 属于什么类型？"
    header: "PRD 类型"
    multiSelect: false
    options:
      - label: "新功能（有 UI）"
        description: "涉及用户界面的新功能"
      - label: "新功能（无 UI / 后端）"
        description: "后端服务、API、后台任务"
      - label: "第三方集成"
        description: "接入外部服务"
      - label: "功能重构"
        description: "不改变外部功能的内部重构"
```

### 1.2 BRD 拆分评估（当输入为 BRD 时）

如果用户提供了 BRD 文件，**必须先评估是否需要拆分**：

```yaml
Task:
  description: "BRD 拆分评估"
  subagent_type: "general-purpose"
  prompt: |
    你是 BRD 拆分评估专家。请按照以下步骤工作：

    ## 第一步：读取 BRD
    读取 BRD 文件：{brd_path}

    ## 第二步：检测拆分信号

    检查以下硬信号（出现任一即建议拆分）：
    - 独立业务价值：各部分有独立的 ROI 评估
    - 不同用户群体：面向完全不同的用户角色
    - 可独立验收与价值实现：各部分可独立交付并产生价值
    - 不同合规域：涉及不同法规/审批流程
    - 独立成功指标：KPI 完全不同
    - 独立 GTM 策略：需要不同的市场/销售方案

    检查反模式（不应拆分）：
    - 紧耦合用户旅程
    - 共享成功指标
    - 强依赖需协同发布

    ## 第三步：输出评估报告

    保存到 workflow/brd-split-assessment.md：

    ```markdown
    # BRD 拆分评估报告

    ## BRD 信息
    - **文件路径**：{brd_path}
    - **评估时间**：YYYY-MM-DD HH:MM

    ## 硬信号检测
    | 信号 | 是否存在 | 证据 |
    |------|----------|------|
    | 独立业务价值 | ✅/❌ | [说明] |
    | 不同用户群体 | ✅/❌ | [说明] |
    | ... | ... | ... |

    ## 反模式检测
    | 反模式 | 是否存在 | 说明 |
    |--------|----------|------|
    | 紧耦合用户旅程 | ✅/❌ | [说明] |
    | ... | ... | ... |

    ## 拆分建议
    - **建议**：拆分/不拆分
    - **拆分方案**（如建议拆分）：
      1. PRD-1: [范围]
      2. PRD-2: [范围]
      ...

    ## BRD 需求清单
    | # | 需求项 | 建议分配到 |
    |---|--------|-----------|
    | 1 | [需求] | PRD-1 |
    | 2 | [需求] | PRD-2 |
    ...
    ```

    完成后输出："[SPLIT-ASSESSMENT-COMPLETE]"
```

**评估完成后，使用 AskUserQuestion 让用户确认拆分方案**：

```yaml
questions:
  - question: "根据 BRD 分析，建议拆分为 N 个 PRD。是否同意此方案？"
    header: "拆分确认"
    multiSelect: false
    options:
      - label: "同意拆分方案"
        description: "按建议拆分为多个 PRD"
      - label: "调整拆分"
        description: "我想调整拆分方式"
      - label: "不拆分"
        description: "合并为单个 PRD"
```

### 1.3 创建工作目录

```bash
mkdir -p workflow/
```

### 1.4 初始化状态文件

创建 `workflow/status.md`：

```markdown
# PRD Studio 状态

## 基本信息
- **需求描述**：[用户输入]
- **PRD 类型**：[用户选择]
- **开始时间**：YYYY-MM-DD HH:MM
- **当前状态**：进行中

## 迭代记录

| 轮次 | 阶段 | 时间 | 结果 |
|------|------|------|------|
| 1 | Writer | - | - |
```

---

## 1:N 场景处理（当 BRD 需要拆分时）

当用户确认需要将 BRD 拆分为多个 PRD 时，工作流调整为：

### 1:N 工作流

```
┌─────────────────────────────────────────────────────────────────┐
│                   1:N PRD Studio 工作流                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BRD 拆分评估完成，确认拆分为 N 个 PRD                            │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 1.5: 创建 PRD 索引文档             │                   │
│  │  - 生成 workflow/PRD-INDEX-{brd}.md      │                   │
│  │  - 初始化 BRD 需求覆盖矩阵                │                   │
│  │  - 记录拆分决策                          │                   │
│  └─────────────────────────────────────────┘                   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 2-5: 循环处理每个 PRD              │                   │
│  │                                          │                   │
│  │  for PRD in [PRD-1, PRD-2, ..., PRD-N]:  │                   │
│  │    ├─ Writer(round=1) → prd-{n}.md      │                   │
│  │    ├─ Reviewer → AGENT-RESULT            │                   │
│  │    ├─ [循环] Writer(round+1) + Reviewer  │                   │
│  │    └─ 单个 PRD 准出                       │                   │
│  │                                          │                   │
│  └─────────────────────────────────────────┘                   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Phase 6: 覆盖率验证                      │                   │
│  │  - 检查 BRD 需求 100% 覆盖               │                   │
│  │  - 更新索引文档状态                      │                   │
│  │  - 输出整体准出证书                      │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1.5: 创建 PRD 索引文档

```yaml
Task:
  description: "创建 PRD 索引文档"
  subagent_type: "general-purpose"
  prompt: |
    根据拆分评估报告，创建 PRD 索引文档。

    ## 读取拆分评估
    读取 workflow/brd-split-assessment.md

    ## 创建索引文档
    保存到 workflow/PRD-INDEX-{brd_name}.md：

    ```markdown
    # PRD 索引：{BRD 名称}

    ## 基本信息
    | 项目 | 内容 |
    |------|------|
    | BRD 来源 | {brd_path} |
    | 拆分方式 | {split_method} |
    | PRD 数量 | N 个 |
    | 创建时间 | YYYY-MM-DD |

    ## PRD 清单
    | PRD | 名称 | 范围 | 状态 | 文件路径 |
    |-----|------|------|------|----------|
    | PRD-1 | [名称] | [范围] | 待编写 | workflow/prd-1.md |
    | PRD-2 | [名称] | [范围] | 待编写 | workflow/prd-2.md |
    | ... | ... | ... | ... | ... |

    ## BRD 需求覆盖矩阵
    | # | BRD 需求项 | 分配到 PRD | 覆盖状态 |
    |---|------------|-----------|----------|
    | 1 | [需求] | PRD-1 | ⏳ 待覆盖 |
    | 2 | [需求] | PRD-2 | ⏳ 待覆盖 |
    ...

    **覆盖率**：0 / {total} = 0%

    ## 拆分决策记录
    - **拆分原因**：[硬信号列表]
    - **拆分时间**：YYYY-MM-DD
    - **确认方式**：用户确认
    ```

    完成后输出："[INDEX-CREATED] 索引文档已创建"
```

### 循环处理每个 PRD

对于每个 PRD，执行标准的 Phase 2-5 流程，但需要：

1. **Writer Subagent 额外指令**：
   - 读取索引文档，明确本 PRD 的覆盖范围
   - 在 PRD 元信息中添加 BRD 映射
   - 保存到 `workflow/prd-{n}.md`

2. **Reviewer Subagent 额外检查**：
   - 验证本 PRD 是否正确引用索引文档
   - 验证覆盖范围是否清晰
   - 检查是否与其他 PRD 存在重叠/遗漏

3. **每个 PRD 准出后**：
   - 更新索引文档中该 PRD 的状态为"已完成"
   - 更新覆盖矩阵中对应需求的状态为"✅ 已覆盖"

### Phase 6: 覆盖率验证

所有 PRD 完成后，执行最终验证：

```yaml
Task:
  description: "PRD 覆盖率验证"
  subagent_type: "general-purpose"
  prompt: |
    验证 BRD 需求是否 100% 被覆盖。

    ## 读取索引文档
    读取 workflow/PRD-INDEX-{brd_name}.md

    ## 验证覆盖率
    - 检查每个 BRD 需求是否都有对应的 PRD 覆盖
    - 计算覆盖率 = 已覆盖需求 / 总需求

    ## 输出验证结果
    保存到 workflow/coverage-verification.md

    如果覆盖率 < 100%：
    - 列出未覆盖的需求
    - 标记为 P0 阻塞

    如果覆盖率 = 100%：
    - 更新索引文档覆盖率为 100%
    - 输出整体准出证书

    完成后输出："[COVERAGE-VERIFIED] 覆盖率验证完成"
```

### 1:N 场景目录结构

```
workflow/
├── status.md                    # 整体状态
├── brd-split-assessment.md      # BRD 拆分评估报告
├── PRD-INDEX-{brd}.md           # PRD 索引文档
├── prd-1.md                     # PRD-1
├── prd-1-review-report.md       # PRD-1 审查报告
├── prd-2.md                     # PRD-2
├── prd-2-review-report.md       # PRD-2 审查报告
├── ...
└── coverage-verification.md     # 覆盖率验证报告
```

---

## Phase 2: Writer Subagent

读取 `subagents/writer.md` 模板，将 `{requirement}`、`{prd_type}`、`{round}` 替换为实际值，通过 Task tool 启动隔离的 Writer subagent。

**首次写作（round=1）**：Writer 生成 PRD 初稿并保存到 `workflow/prd.md`。
**修订轮次（round>1）**：Writer 同时读取 `workflow/review-report.md`，按优先级修复问题后覆盖保存。

**结果解析**：从 subagent 输出中提取 `AGENT-RESULT` 块（详见 `references/orchestrator-rules.md`「结果解析」段）。

| AGENT-RESULT status | Orchestrator 行为 |
|---------------------|------------------|
| `success` | 进入 Phase 3 |
| `needs_input` | 暂停，通过 AskUserQuestion 转达 `blocking_issues` |
| `failed` + `needs_retry` | 重试一次 |
| `failed` + `!needs_retry` | 报告用户 |
| 块缺失 | 重试一次（强调输出要求），二次缺失 → 报告用户 |

---

## Phase 3: Reviewer Subagent

读取 `subagents/reviewer.md` 模板，将 `{round}` 替换为实际值，通过 Task tool 启动隔离的 Reviewer subagent。

**结果解析**：从 `AGENT-RESULT` 块提取 `verdict`、`p0_count`、`p1_count`。

---

## Phase 4: 结果判断

**基于 Reviewer 的 `AGENT-RESULT` 块判定**（不再从 review-report.md 自由文本中解析）：

### 4.1 准出通过条件

- `verdict: pass`（即 P0=0 且 P1<2）

→ 进入 Phase 5

### 4.2 需要修改条件

- `verdict: fail`（P0>0 或 P1>=2）

→ 检查迭代次数：
- 如果 < 3 次：回到 Phase 2 启动 Writer(round+1)，Writer 同时承担修复
- 如果 >= 3 次：进入 Phase 5（带遗留问题）

> 不再单独派发 Fixer subagent。Writer 在 round>1 时自动读取 review-report 并修复。

---

## Phase 5: 完成

### 5.1 准出通过

输出准出证书：

```markdown
# ✅ PRD 准出证书

## 基本信息
- **PRD 文件**：workflow/prd.md
- **准出时间**：YYYY-MM-DD HH:MM
- **总迭代轮次**：N 轮

## 审查历程
| 轮次 | 结果 | P0 | P1 | P2 |
|------|------|----|----|----|
| 1 | 需修改 | 2 | 3 | 5 |
| 2 | 需修改 | 0 | 2 | 3 |
| 3 | 通过 | 0 | 1 | 2 |

## 遗留建议（P2）
[列出未处理的 P2 建议]

---

**PRD 已准出，可进入 HLD 阶段。**
```

### 5.2 达到最大迭代次数

输出遗留问题报告：

```markdown
# ⚠️ PRD 迭代完成（有遗留问题）

## 基本信息
- **PRD 文件**：workflow/prd.md
- **完成时间**：YYYY-MM-DD HH:MM
- **总迭代轮次**：3 轮（已达上限）

## 遗留问题
### P0 阻塞问题
[如果有]

### P1 严重问题
[如果有]

## 建议
1. 人工介入处理遗留的 P0/P1 问题
2. 处理完成后可使用 /prd-reviewer 单独审查
```

### 5.3 更新状态文件

更新 `workflow/status.md` 为完成状态。

---

## 目录结构

工作流程中产生的文件：

```
workflow/
├── status.md           # 状态跟踪
├── prd.md              # PRD 文件（不断更新）
└── review-report.md    # 最新的审查报告
```

---

## 执行示例

### 用户触发

```
用户: /prd-studio 我想做一个用户积分系统，用户可以通过购买、签到获得积分，用积分兑换优惠券
```

### Orchestrator 执行

```
[Phase 1] 初始化
  → 确认 PRD 类型：新功能（有 UI）
  → 创建 workflow/ 目录
  → 初始化 status.md

[Phase 2] Writer Subagent (round=1)
  → 读取 subagents/writer.md 模板
  → 生成 PRD → workflow/prd.md
  → AGENT-RESULT: status=success

[Phase 3] Reviewer Subagent (round=1)
  → 读取 subagents/reviewer.md 模板
  → 审查 workflow/prd.md
  → AGENT-RESULT: verdict=fail, p0=1, p1=2

[Phase 4] 结果判断
  → verdict=fail，迭代=1 < 3，继续

[Phase 2] Writer Subagent (round=2，读取 review-report 修复)
  → 修复 P0 + P1 问题
  → 保存修改后的 PRD
  → AGENT-RESULT: status=success

[Phase 3] Reviewer Subagent (round=2)
  → 审查修改后的 PRD
  → AGENT-RESULT: verdict=pass, p0=0, p1=1

[Phase 4] 结果判断
  → verdict=pass，准出通过！

[Phase 5] 完成
  → 输出准出证书
  → 更新 status.md
```

---

## 注意事项

1. **不要跳过 subagent**：每个阶段必须通过 Task tool 启动隔离的 subagent，不能在主线程直接执行
2. **文件是唯一状态**：所有状态通过 workflow/ 目录下的文件传递
3. **AGENT-RESULT 契约**：每个 subagent 必须在输出末尾包含 `AGENT-RESULT` 块（详见 `subagents/*.md` 和 `references/orchestrator-rules.md`）。Orchestrator 只从该块做流转判定，不解析自由文本
4. **错误处理**：AGENT-RESULT 缺失 → 重试一次；`status=failed` → 按 `needs_retry` 决定重试或报告用户（详见 orchestrator-rules.md）
5. **进度可见**：每个阶段开始和结束都要输出进度信息
