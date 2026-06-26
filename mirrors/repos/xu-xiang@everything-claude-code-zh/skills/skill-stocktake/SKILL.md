---
description: "用于对 Claude 技能（Skills）和命令进行质量审计。支持快速扫描（Quick Scan，仅针对变更的技能）和全面盘点（Full Stocktake）模式，并通过子智能体（subagent）进行顺序批处理评估。"
origin: ECC
---

# skill-stocktake

斜杠命令（`/skill-stocktake`），使用质量检查清单 + AI 综合判断来审计所有 Claude 技能（Skills）和命令。支持两种模式：针对最近变更技能的快速扫描（Quick Scan），以及用于完整审查的全面盘点（Full Stocktake）。

## 作用范围（Scope）

该命令的目标路径**相对于调用它的目录**：

| 路径 | 描述 |
|------|-------------|
| `~/.claude/skills/` | 全局技能（适用于所有项目） |
| `{cwd}/.claude/skills/` | 项目级技能（如果该目录存在） |

**在阶段 1（Phase 1）开始时，该命令会明确列出已发现并扫描的路径。**

### 针对特定项目

若要包含项目级技能，请在该项目的根目录下运行：

```bash
cd ~/path/to/my-project
/skill-stocktake
```

如果项目没有 `.claude/skills/` 目录，则仅评估全局技能和命令。

## 模式（Modes）

| 模式 | 触发条件 | 预计耗时 |
|------|---------|---------|
| 快速扫描（Quick Scan） | `results.json` 已存在（默认） | 5–10 分钟 |
| 全面盘点（Full Stocktake） | `results.json` 不存在，或执行 `/skill-stocktake full` | 20–30 分钟 |

**结果缓存路径：** `~/.claude/skills/skill-stocktake/results.json`

## 快速扫描流程（Quick Scan Flow）

仅重新评估自上次运行以来发生变更的技能（5–10 分钟）。

1. 读取 `~/.claude/skills/skill-stocktake/results.json`
2. 运行：`bash ~/.claude/skills/skill-stocktake/scripts/quick-diff.sh \
         ~/.claude/skills/skill-stocktake/results.json`
   （项目目录会自动从 `$PWD/.claude/skills` 检测；仅在需要时显式传递）
3. 如果输出为 `[]`：报告 "No changes since last run."（自上次运行以来无变更）并停止
4. 使用相同的“阶段 2（Phase 2）”标准仅重新评估那些变更的文件
5. 沿用之前结果中未变更的技能
6. 仅输出差异部分（diff）
7. 运行：`bash ~/.claude/skills/skill-stocktake/scripts/save-results.sh \
         ~/.claude/skills/skill-stocktake/results.json <<< "$EVAL_RESULTS"`

## 全面盘点流程（Full Stocktake Flow）

### 阶段 1 — 清单盘点（Inventory）

运行：`bash ~/.claude/skills/skill-stocktake/scripts/scan.sh`

该脚本会枚举技能文件，提取 Frontmatter，并收集 UTC 修改时间（mtimes）。
项目目录会自动从 `$PWD/.claude/skills` 检测；仅在需要时显式传递。
展示脚本输出的扫描摘要和清单表格：

```
Scanning:
  ✓ ~/.claude/skills/         (17 files)
  ✗ {cwd}/.claude/skills/    (not found — global skills only)
```

| 技能 | 7天使用率 | 30天使用率 | 描述 |
|-------|--------|---------|-------------|

### 阶段 2 — 质量评估（Quality Evaluation）

启动一个任务工具子智能体（Task tool subagent，**Explore agent, model: opus**），携带完整的清单和检查表。
子智能体读取每个技能，应用检查表，并返回每个技能的 JSON 结果：

`{ "verdict": "Keep"|"Improve"|"Update"|"Retire"|"Merge into [X]", "reason": "..." }`

**分块指南（Chunk guidance）：** 每次子智能体调用处理约 20 个技能，以保持上下文可控。在每个分块处理后，将中间结果保存到 `results.json`（`status: "in_progress"`）。

在所有技能评估完成后：设置 `status: "completed"`，进入阶段 3。

**断点续传检测：** 如果启动时发现 `status: "in_progress"`，则从第一个未评估的技能开始恢复。

每个技能都会对照以下检查清单进行评估：

```
- [ ] 已检查与其他技能的内容重叠情况
- [ ] 已检查与 MEMORY.md / CLAUDE.md 的重叠情况
- [ ] 已验证技术引用的时效性（如果存在工具名称 / CLI 标志 / API，请使用 WebSearch）
- [ ] 已考虑使用频率
```

判定（Verdict）标准：

| 判定（Verdict） | 含义 |
|---------|---------|
| 保留（Keep） | 有用且不过时 |
| 改进（Improve） | 值得保留，但需要特定的改进 |
| 更新（Update） | 引用的技术已过时（通过 WebSearch 验证） |
| 退役（Retire） | 质量低、陈旧或成本收益不对称 |
| 合并至 [X]（Merge into [X]） | 与另一个技能存在实质性重叠；需注明合并目标 |

评估基于 **AI 综合判断** —— 而非数字量化表。指导维度：
- **可操作性（Actionability）**：能够让你立即行动的代码示例、命令或步骤
- **范畴契合度（Scope fit）**：名称、触发条件和内容一致；既不太宽泛也不太狭隘
- **唯一性（Uniqueness）**：其价值无法被 MEMORY.md / CLAUDE.md / 其他技能替代
- **时效性（Currency）**：技术引用在当前环境下有效

**理由质量要求** —— `reason` 字段必须是自包含的且能够支持决策：
- 不要只写 "unchanged"（未变更） —— 务必重申核心证据
- 对于**退役（Retire）**：说明（1）发现了什么具体缺陷，（2）什么东西替代了该需求
  - 错误示例：`"Superseded"`（已被取代）
  - 正确示例：`"disable-model-invocation: true already set; superseded by continuous-learning-v2 which covers all the same patterns plus confidence scoring. No unique content remains."`
- 对于**合并（Merge）**：指明目标并描述要整合的内容
  - 错误示例：`"Overlaps with X"`（与 X 重叠）
  - 正确示例：`"42-line thin content; Step 4 of chatlog-to-article already covers the same workflow. Integrate the 'article angle' tip as a note in that skill."`
- 对于**改进（Improve）**：描述所需的具体变更（哪个章节，什么操作，如果相关则说明目标大小）
  - 错误示例：`"Too long"`（太长了）
  - 正确示例：`"276 lines; Section 'Framework Comparison' (L80–140) duplicates ai-era-architecture-principles; delete it to reach ~150 lines."`
- 对于**保留（Keep）**（快速扫描中仅修改时间变更的情况）：重申原始判定理由，不要写 "unchanged"
  - 错误示例：`"Unchanged"`
  - 正确示例：`"mtime updated but content unchanged. Unique Python reference explicitly imported by rules/python/; no overlap found."`

### 阶段 3 — 摘要表格（Summary Table）

| 技能 | 7天使用率 | 判定（Verdict） | 理由（Reason） |
|-------|--------|---------|--------|

### 阶段 4 — 整合（Consolidation）

1. **退役 / 合并（Retire / Merge）**：在用户确认前，针对每个文件提供详细的辩护理由：
   - 发现了什么具体问题（重叠、过时、引用失效等）
   - 哪种替代方案涵盖了相同的功能（对于退役：哪个现有技能/规则；对于合并：目标文件及要整合的内容）
   - 移除的影响（任何依赖该技能、MEMORY.md 引用或受影响的工作流）
2. **改进（Improve）**：提供具体的改进建议及理由：
   - 变更内容及原因（例如，“将 430 行修剪至 200 行，因为 X/Y 章节与 python-patterns 重复”）
   - 由用户决定是否执行
3. **更新（Update）**：提供已通过来源检查的更新内容
4. 检查 MEMORY.md 的行数；如果超过 100 行，建议进行压缩

## 结果文件 Schema

`~/.claude/skills/skill-stocktake/results.json`:

**`evaluated_at`**：必须设置为评估完成的实际 UTC 时间。
通过 Bash 获取：`date -u +%Y-%m-%dT%H:%M:%SZ`。切勿使用类似 `T00:00:00Z` 的仅日期近似值。

```json
{
  "evaluated_at": "2026-02-21T10:00:00Z",
  "mode": "full",
  "batch_progress": {
    "total": 80,
    "evaluated": 80,
    "status": "completed"
  },
  "skills": {
    "skill-name": {
      "path": "~/.claude/skills/skill-name/SKILL.md",
      "verdict": "Keep",
      "reason": "Concrete, actionable, unique value for X workflow",
      "mtime": "2026-01-15T08:30:00Z"
    }
  }
}
```

## 注意事项

- 评估是盲审：同样的检查清单适用于所有技能，无论其来源如何（ECC、自创、自动提取）
- 归档 / 删除操作始终需要明确的用户确认
- 判定结果不会因技能来源不同而产生分支
