
<!-- PACENOTE-CONFIG-START -->
# PaceNote 开发指南

<!-- 🤖 配置说明:
     推荐使用 setup_project.py 自动部署，占位符会自动替换。
     
     如果手动复制此文件，需要替换以下占位符:
     - PLATFORM_PREFIX: 你的平台前缀（如 myplatform），无平台层则删除相关段落
     - PLATFORM_REPO: 你的平台代码仓库名
     - DOCS_CONFIG_SECTION（在"项目文档配置"段落中）: 替换为文档路径表格
     
     部署后用 @ProjectSetup 引导填充领域知识。
-->

> 🚀 专家目录: `.github/skills/`

---

## 🔑 专家路由机制（扫描 SKILL.md）

**专家发现方式**: 扫描 `.github/skills/*/SKILL.md` 的 YAML frontmatter

**执行方式**:
```python
# 扫描所有 skill 目录
for skill_dir in list_dir(".github/skills/"):
    skill_md = read_file(f".github/skills/{skill_dir}/SKILL.md")
    # 解析 frontmatter 中的 name 和 description
    # description 包含触发关键词，用于匹配用户问题
```

**匹配规则**: 
- 读取每个 SKILL.md 的 `description` 字段
- description 中包含"触发关键词: xxx、yyy、zzz"
- 用户问题与触发关键词进行正则匹配（忽略大小写）

**Skill 分类优先级**:
1. **工作流 Skill** - pbi-reviewer、roundtable-debate、coding-agent
2. **应用专家** - {app-prefix}-*-expert（应用特定业务）
3. **平台专家** - {{PLATFORM_PREFIX}}-*-expert（通用平台能力）
4. **工具专家** - git-blame 等

---

## ⚡ 执行声明规范

**每次使用 Skill 时，必须向用户明确告知：**

### 开始执行时
```
🔧 **正在执行: [Skill名称]** (`#skill-name`)

✅ 已加载 Skill 指引
⭕ 当前步骤: [步骤描述]
```

### 调用其他专家时
```
🔗 **调用领域专家**: `#expert-name`
   原因: [为什么需要调用]
```

### 遇到问题时
```
⚠️ **问题提示**:
   - [问题描述]
   - [建议操作]
```

### 执行完成时
```
✅ **执行完成**: [Skill名称]

参考来源:
- Skill: `#skill-name`
- 领域专家: [调用的专家列表]
- 其他: [配置文件/文档等]

产出物: [描述产出]
```

---

## � 用户交互规范（全局强制）

### ask_questions 对话框（强制）

**所有需要用户确认、选择、输入的交互点，必须使用 `ask_questions` 工具**，禁止使用纯文本询问。

| 规则 | 说明 |
|------|------|
| 🔴 **必须使用 ask_questions** | 任何需要用户做决定的场景（选择、确认、输入）都必须弹出对话框 |
| 🔴 **禁止纯文本询问** | 不得在回复中用"请选择 1/2/3"或"是否继续？[Y/N]"等文字形式向用户提问 |
| ✅ **设置推荐选项** | 如有明确的最优选项，标记为 `recommended` |
| ✅ **允许自由输入** | 需要用户补充信息时设置 `allowFreeformInput: true` |

### ask_questions 标准用法示例

```
ask_questions 参数格式：
- header: 简短标签（≤12字符），如 "确认操作"、"选择方案"
- question: 完整的问题描述
- options: 2-6 个选项，每个包含 label 和可选的 description
- recommended: 标记推荐选项（仅用于有明确最优选项时）
- allowFreeformInput: true（当用户可能需要输入自定义内容时）
```

### 🎯 主动澄清规范（全局强制）

> 📖 详细判断标准和场景示例见 `.github/skills/shared-operational-rules/references/proactive-clarification.md`

**核心原则**：对不确定的信息**禁止推断和猜测**，必须主动向用户澄清；但要把控颗粒度，避免过度询问。

**三级不确定性分级**：

| 级别 | 判断标准 | 行为 |
|------|---------|------|
| 🔴 **必须澄清** | 影响方向/范围/正确性；无法从上下文推断；猜错代价高 | 立即 `ask_questions` 阻断，等用户回答后再继续 |
| 🟡 **假设+声明** | 有高置信度默认值；猜错可低成本修正 | 选择最合理默认值，回复中**显式声明假设**，用户可随时纠正 |
| 🟢 **自主决策** | 纯技术实现细节；业界有明确最佳实践；不影响用户意图 | 直接执行，无需提及 |

**颗粒度守则（防止过度询问）**：

| 规则 | 说明 |
|------|------|
| 🔴 **先搜后问** | 能通过代码搜索、文件读取确认的信息，必须先搜索再决定，不得直接询问用户 |
| 🔴 **遵循惯例** | 项目已有明确模式/约定时，遵循现有模式，不再询问 |
| ✅ **合并关联问题** | 同一主题的多个不确定点合并为 1 个 `ask_questions`（上限 4 题） |
| ✅ **提供推荐选项** | 即使需要澄清，也应给出推荐选项（`recommended`），让用户能快速确认 |

### 🚫 文件保护（全局强制）

- **禁止主动删除用户文件**：AI 不得主动删除任何用户的工作产物、中间文件、工作目录
- **禁止询问删除**：AI 不得以任何形式（纯文本、对话框）向用户发起"是否删除/清理"的询问
- 仅当用户**主动明确要求**删除时才可执行

---


## 🔄 对话生命周期管理（全局强制）

> 📖 详见 `.github/skills/shared-operational-rules/references/conversation-lifecycle.md`

**核心原则**：长对话是质量下降的首要原因。重型 Skill（`#pbi-reviewer` / `#roundtable-debate` / `#coding-agent`）执行前必须读取上述规则，遵循对话健康度检测、跨对话续接、多轮修正处理等机制。

---

## �📁 项目文档配置
<!-- 🤖 AI 填充指南
复制以下提示词发送给 Copilot 来自动生成此段落：

---
请帮我配置 copilot-instructions.md 中的项目文档部分。

我的项目文档位于:
- 检查清单: [路径，如 .github/copilot-resources/docs/checklist.md]
- 模块清单: [路径，如 .github/copilot-resources/docs/modules.md]
- 依赖关系: [路径，如 .github/copilot-resources/docs/dependencies.md]

请生成如下格式的配置表格，替换下方的 {{DOCS_CONFIG_SECTION}}:
| 文档 | 路径 |
|------|------|
| 检查清单 | ... |
---
-->
{{DOCS_CONFIG_SECTION}}

### 🔴 文档读取优先级（强制）

> 📁 以上文档已复制到项目 `.github/copilot-resources/` 目录。
> **必须优先从 `.github/copilot-resources/` 读取，避免触发工作区外文件授权确认。**

**读取流程**：
1. 检查 `.github/copilot-resources/` 目录是否存在
2. 如果存在 → 从该目录下读取对应文件（`docs/` 子目录存放文档，`data/` 子目录存放 PBI 索引/详情）
3. 如果不存在 → 降级使用上表中的绝对路径

### 🔴 PBI 知识库分层读取（强制）

PBI 数据已拆分为**索引文件**（轻量）和**详情文件**（完整），减少 token 消耗：

1. **先读索引** — 用 `read_file` 读取 `*-index.md`（~400行），按标题/关键词匹配目标 PBI
2. **再搜详情** — 用 `grep_search` 在 `*-detail.md` 中搜索关键词，补充索引未覆盖的结果
3. **按需精读** — 对匹配到的 PBI ID，用 `read_file` 读取详情文件中对应 `## PBI-{id}` section

> ⚠️ **禁止**一次性 `read_file` 读取整个详情文件（>10000行），必须按 section 按需读取。

### 🔴 强制规则

在执行 `#pbi-reviewer` 或 `#coding-agent` 时，必须：
1. 检查上表中是否配置了文档路径
2. 如果有值，使用 `read_file` 读取对应文档
3. 在回复中声明参考了哪些文档

```
📚 **参考来源**:
- 检查清单: [文件路径]
- 功能模块: [文件路径]
- 功能依赖: [文件路径]
- 历史PBI: [索引文件名] + [详情文件名] (找到 X 条相关记录)
```

---


---

## 🔧 MCP 工具 & 平台架构 & PBI 解析（按需加载）

> 📖 调用 MCP 工具前，读取 `.github/skills/shared-operational-rules/references/mcp-tools-status.md`
> 📖 搜索代码前，读取 `.github/skills/shared-operational-rules/references/platform-identification.md`
> 📖 检测到需求输入时，读取 `.github/skills/shared-operational-rules/references/pbi-parsing.md`

---

## 📋 工作流程

```
用户提问
    ↓
1. 【意图检测】根据关键词自动匹配 Skill（通过 SKILL.md 的 description 字段）
    ↓
2. 【自动调用】无需用户手动指定，直接执行对应 Skill
    ↓
3. 【领域路由】如需领域知识，调用 #expert-index 获取专家推荐
    ↓
4. 【综合输出】金字塔原则（结论先行），告知参考来源
```

> 🔴 **平台代码搜索**：`#roundtable-debate` 和 `#coding-agent` 在检测到 PBI 涉及平台组件时，
> 必须参考 `#platform-architecture` 搜索策略，主动搜索 {{PLATFORM_REPO}} 的**完整源码**（头文件+实现）。
> 本地工作区有 {{PLATFORM_REPO}} 时直接 `read_file`，没有时通过 MCP `get_file_content` 读取。
> 不能仅依赖 expert skill 文档描述或本地 grep 调用处签名。

---


---

## ⚙️ Skill 变更兼容性规则（强制）

> 触发词是 Skill 路由的唯一依据，任何变更必须保证不影响现有路由。

| 规则 | 说明 |
|------|------|
| 触发词唯一性 | 新增/修改触发词后，运行 `python scripts/lint_skills.py` 检查是否与现有 Skill 冲突 |
| 重命名兼容 | 重命名 Skill 目录时，必须同步更新 `copilot-instructions.md` 中的所有引用 |
| 子串拦截防护 | 触发词不得是其他 Skill 触发词的子串，避免意外拦截（如 "Tissue" vs "TissueROI"） |
| 🔴 修改后自动验证 | AI 修改任何 SKILL.md 后，**必须**在终端运行 `python scripts/lint_skills.py --skill {name}` 并检查结果通过 |

---

## 🔍 输出质量 & 阶段过渡 & 代码规范（按需加载）

> 📖 工作流 Skill 执行完毕后，读取 `.github/skills/shared-operational-rules/references/quality-selfcheck.md`
> 📖 阶段切换时（需求→设计→编码），读取 `.github/skills/shared-operational-rules/references/workflow-transitions.md`
> 📖 编码或代码审查时，读取 `.github/skills/shared-operational-rules/references/coding-standards.md`
> 📖 对用户意图/需求范围不确定时，读取 `.github/skills/shared-operational-rules/references/proactive-clarification.md`

---

## 📦 知识库版本检查

> 📖 会话首次调用 Skill 时，检查 Skill 版本是否为最新

---

## �💡 使用技巧

1. **不确定用哪个专家？** → `#expert-index` + 描述问题
2. **需要分析/返讲需求？** → `#pbi-reviewer`
3. **需要设计方案？** → `#roundtable-debate`
4. **需要根据设计编码？** → `#coding-agent`
5. **涉及平台组件？** → 先 `#platform-architecture` 识别层级

---


## ➕ 添加新 Skill

1. 在 `.github/skills/` 目录下创建文件夹
2. 添加 `SKILL.md` 文件（参考 `_templates/` 中的模板）
3. 确保有正确的 YAML frontmatter（name, description, 触发词）
4. AI 会自动发现新 Skill，无需其他配置


<!-- PACENOTE-CONFIG-END -->
