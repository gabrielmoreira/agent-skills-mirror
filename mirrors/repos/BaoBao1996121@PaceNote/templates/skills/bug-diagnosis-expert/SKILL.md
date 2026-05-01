---
name: bug-diagnosis-expert
description: |
  Bug 辅助诊断专家 - 两种模式：批量分析历史 Bug 生成模式库，实时诊断定位嫌疑文件。
  模式A: 读取 data/bug_analysis/ 的 JSON 数据，分析并生成 bug-patterns.md 到模块 Skill。
  模式B: 接收 Bug ID 或描述，路由到对应模块专家，聚合诊断建议。
  触发关键词: Bug诊断, 缺陷分析, 问题排查, bug diagnosis, 更新Bug模式库,
  Bug模式, 嫌疑文件, regression, 崩溃分析, 黑图排查, bug-patterns
---

# Bug 辅助诊断专家

> **模式A** 分析历史 Bug 生成知识库 | **模式B** 实时诊断定位问题

---

## 🔴 执行声明（强制）

### 开始执行时
```
🔍 **正在执行: Bug Diagnosis Expert** (`#bug-diagnosis-expert`)

⭕ 工作模式: [模式A: 生成Bug模式库 / 模式B: 实时诊断]
⭕ 当前步骤: [步骤描述]
```

### 执行完成时
```
✅ **执行完成**: Bug Diagnosis Expert

参考来源:
- 数据: data/bug_analysis/{module}.json
- 模块专家: #{skill-name}

产出物: [生成/更新的文件列表 或 诊断结论]
```

---

## 模式判断

| 用户意图 | 模式 | 关键词 |
|---------|------|--------|
| 分析历史 Bug、生成/更新模式库 | **A** | 更新模式库、分析历史Bug、生成bug-patterns |
| 排查具体 Bug、定位问题 | **B** | Bug#12345、崩溃、黑图、排查、诊断 |

**不确定时** → 使用 ask_questions 询问用户。

---

## 模式 A：生成/更新 Bug 模式库

### 前置检测

检查 `data/bug_analysis/` 目录是否有数据：

```
list_dir("data/bug_analysis/")
```

**如果目录不存在或为空** → 引导用户：

```
⚠️ 暂无 Bug 分析数据。

🚀 **推荐使用交互式引导**（会帮你完成全部配置和数据采集）：
  在 Copilot Chat 中输入 `@GuidedDev` → 选择"🐛 Bug 修复/分析" → "🔍 分析历史 Bug"

📝 **或者手动运行**（需要先配置 data/user_preferences.json）：
  python scripts/analyze_bug_prs.py --app {{APP_NAME}} --days 180
```

**如果数据已就绪** → 直接进入分析流程（Step A1-A6）。

📖 **完整分析流程见 `references/diagnosis-workflow.md`**

### 执行流程（数据已就绪）

#### A1. 选择目标模块

使用 ask_questions 让用户从可用 JSON 中选择模块。

#### A2. 读取与分析

按以下顺序读取：
1. `data/bug_analysis/{module}.json` — Bug 元数据 + PR + 文件统计
2. `data/bug_analysis/diffs/{bugId}_PR{prId}.diff` — 高频文件和跨模块 Bug 的 diff
3. `templates/skills/{module}-expert/SKILL.md` — 模块知识（常见陷阱/上下游）
4. `references/analysis-prompt-template.md` — 分析维度框架

分析维度：
1. **高频嫌疑文件** — 哪些文件 Bug 最多（从 diff 看根因）
2. **Bug 类型聚类** — 黑图/崩溃/状态不同步/配置遗漏
3. **跨模块联动陷阱** — 改 A 漏了对 B 的影响
4. **修复模式归纳** — 常见修复手法
5. **隐含规则提取** — 非代码约束

数据量策略：

| Bug 数量 | 策略 |
|---------|------|
| ≤ 20 | 全量 Bug + 全部 Diff |
| 20-50 | 全量元数据 + 高频/跨模块 Diff |
| > 50 | 统计摘要 + Top-10 典型 Diff |

#### A3. 生成 bug-patterns.md

写入 `templates/skills/{module}-expert/references/bug-patterns.md`：

```markdown
# {模块名} Bug 模式库
> 🤖 由 #bug-diagnosis-expert 分析生成
> 📅 最后更新: {date} | 数据源: {N}个Bug / {M}个PR / {K}个diff

## 高频嫌疑文件
| 排名 | 文件路径 | Bug 次数 | 典型场景 |

## Bug 类型分布
| 类型 | 数量 | 占比 | 典型 Bug ID |

## 跨模块联动 Bug
| 触发模块 | 受影响操作 | Bug 数 | 典型模式 |

## 修复模式摘要
| 模式 | 频率 | 说明 |

## 隐含规则（从 Diff 提取）
- ✅ {规则} — 来源: Bug #{id}
```

#### A4. 追加 AI 建议到 experience-notes.md

仅追加到 `🤖 AI 建议` 区域。**禁止修改其他章节。**

---

## 模式 B：实时 Bug 诊断

### B1. 信息收集

接收 Bug ID 或问题描述。有 Bug ID 时：
```bash
python scripts/get_bug_prs.py {id} --show-changes
```

### B2. 模块识别

从 Bug 标题/复现步骤/描述中提取关键词，匹配模块：

| 关键词 | 模块 | 对应 Skill |
|--------|------|-----------|

<!-- 🤖 AI 填充指南
将以下提示词发送给你的 AI 助手：

---
我的应用有以下业务模块：
[列出模块名称和对应的 Skill 名]

请帮我生成 Bug 关键词 → 模块映射表，让 AI 能通过 Bug 描述中的关键词自动定位到对应模块。
格式：| Bug关键词 | 对应模块 | 域专家 Skill 名 |
---
-->

| [你的关键词] | [模块名] | `#app-[模块]-expert` |

**无法判断时** → 使用 ask_questions 让用户选择模块。

### B3. 加载模块知识

依次读取：
1. 对应模块 Skill 的 `references/bug-patterns.md` — 历史 Bug 模式
2. 对应模块 Skill 的 `references/experience-notes.md` — 团队经验
3. 对应模块 Skill 的主 SKILL.md — 代码入口和常见陷阱
4. `docs/功能依赖关系.md` — 下游影响矩阵（如已配置）

### B4. 输出诊断建议

```markdown
## 🔍 Bug 诊断报告

### 嫌疑文件（优先级排序）
| 优先级 | 文件 | 原因 |
|:------:|------|------|
| 🔴 P0 | `xxx.cs` | 历史 Bug 高频文件 + 团队经验标记 |
| 🟡 P1 | `xxx.cpp` | 从 Bug 描述匹配到的代码入口 |

### 历史相似 Bug
| Bug ID | 标题 | 解决方案 |
|--------|------|---------|

### 团队经验参考
- {来自 experience-notes.md 的相关条目}

### 影响范围
| 下游模块 | 可能影响 | 需要验证 |
|---------|---------|---------|

### 建议排查步骤
1. {具体操作}
2. {具体操作}
```

---

## ⚠️ 文件保护规则

| 文件 | 策略 |
|------|------|
| `references/bug-patterns.md` | 🤖 **可覆盖** — AI 重新生成时整体替换 |
| `references/experience-notes.md` | 🔒 **仅追加** — 只能向 `🤖 AI 建议` 区域追加内容 |
| `data/bug_analysis/*.json` | 🤖 **可覆盖** — 脚本重新采集时替换 |
| `data/bug_analysis/diffs/*.diff` | 🤖 **可覆盖** — 脚本重新采集时替换 |

---

## 参考文件

- **执行流程**: `read_file("references/diagnosis-workflow.md")`
- **分析模板**: `read_file("references/analysis-prompt-template.md")`
- **功能依赖**: `read_file("docs/功能依赖关系.md")`（如已配置）
- **功能清单**: `read_file("docs/功能模块清单.md")`（如已配置）
