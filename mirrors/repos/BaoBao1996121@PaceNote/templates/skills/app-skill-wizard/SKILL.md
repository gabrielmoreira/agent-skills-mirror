---
name: app-skill-wizard
description: |
  Skill 创建向导 - 交互式引导按模块生成 Copilot 专家 Skill。
  支持任意平台和应用层级，自动从 project-profile.json 读取技术栈配置。
  分批深度研究 + 分批生成，确保代码入口精确。
  触发关键词: 创建Skill, 新应用专家, 生成模块专家, app skill wizard,
  新增应用, 为应用创建专家, 添加应用Skill, create app skills,
  平台Skill, 再生专家, regenerate experts, 批量生成Skill,
  项目接入, project setup, 新项目专家
---

# Skill 创建向导

> 交互式引导：为目标项目按模块生成 Copilot 专家 Skill，注册到类别系统，通过 GUI 部署。
> 支持任意平台和应用层级。当存在 `project-profile.json` 时自动消费其中的技术栈/分层信息。
> AI 自动执行大部分操作，在 3 个检查点暂停等用户确认。

---

## 🔴 执行声明（强制）

你正在执行一个**交互式向导**，必须严格按照以下流程执行。
每个步骤完成后更新进度，在 🔴 检查点处**必须暂停等用户确认**后再继续。

### 启动时的开场引导（强制）

收到用户消息后，立即显示以下引导信息（在做任何操作之前）：

```markdown
👋 你好！我来帮你生成 Copilot Skill。

**整个过程我来跑，你只需要在 3 个关键节点确认一下：**

1️⃣ 确认模块清单 — 我分析完代码后，你看看模块划分对不对
2️⃣ 确认生成质量 — Skill 文件生成完，我会自动 lint 检查 + 评分
3️⃣ 确认交付清单 — 最终文件列表，可选自动提交 PR 并通知审阅人

⬇️ 现在开始收集信息...
```

然后进入 Step 0。

---

## 执行流程

```
Step 0  环境 + 信息收集
  │
  ├── 0-pre 运行模式选择
  ├── 0a   提取应用名 + 命名前缀
  ├── 0a'  确定 Skill 层级（应用/平台）
  ├── 0b   获取模块列表
  └── 0c   分析平台继承关系（应用层）
  │
  ▼
🔴 CP0  模块清单确认         ◀── 暂停：展示表格，等用户确认/修改
  │
  ▼
Step 1  分批研究 + 生成
  │
  ├── 1a   读取模版 + 参考
  ├── 1b   分批深度研究（runSubagent）
  ├── 1c   基于研究报告逐批生成 SKILL.md
  ├── 1d   [应用层] 读取 XML 配置自动填充
  └── 1e   自动 lint 验证
  │
  ▼
🔴 CP1  生成质量确认         ◀── 暂停：展示 lint 结果 + 评分卡，等用户确认
  │
  ▼
Step 2  注册类别 + 配置（AI自动）
  │
  ▼
🔴 CP2  交付确认             ◀── 暂停：展示文件清单，等用户确认
  │
  ▼
Step 3  [可选] 提交 PR + 飞书通知
  │
  ├── 3-local  [多根工作区] 本地脚本 create_skill_pr.ps1
  └── 3-remote [纯目标项目] MCP create_branch → create_commit → create_pull_request
  │
  ▼
🔴 CP3  最终交付确认         ◀── 暂停：展示 PR 链接 + 通知状态
```

---

## Step 0：环境 + 信息收集

### 0-pre-profile. 检查 project-profile.json

**优先检查** `.copilot-temp/project-setup/*/project-profile.json` 是否存在。

如存在：
- 读取 profile 中的 `techStack`、`layers`、`platform`、`configDiscovery`
- 跳过 Step 0a'(Skill层级)和 Step 0c(平台继承分析) 中的 平台特有逻辑
- 在 Step 1b 的研究指令中注入技术栈相关搜索项
- 在 Step 1d 的配置发现中使用 profile 的 `configDiscovery` 规则

如不存在：
- 回退到现有交互式收集流程（完全兼容现有用法）

### 0-pre. 运行模式选择

**自动检测**当前工作区结构，使用 ask_questions 确认运行模式：

1. **检查工作区根目录列表** — 确认是否包含工具项目（含 `templates/skills/` 和 `data/skill_categories.json`）
2. **检查 MCP 可用性** — 确认是否有 `azureDevOpsHSW` MCP server（可访问工具仓库）

**模式选择**（ask_questions）：
- header: "运行模式"
- question: "检测到当前环境支持以下模式，请选择："
- 选项A（推荐 — 如检测到工具项目）: "多根工作区模式 — 工具项目已在工作区，本地读写"
- 选项B（推荐 — 如未检测到工具项目但有 MCP）: "纯目标项目模式 — 通过 MCP 远程读写工具仓库"

| | 多根工作区模式 | 纯目标项目模式 |
|---|---|---|
| 前提 | 工具项目 + 目标项目同时打开 | MCP 已配置 azureDevOpsHSW |
| 模板读取 | `read_file` 本地读取 | MCP `get_file_content` 远程读取 |
| Skill 生成位置 | `templates/skills/`（工具项目内） | `.github/skills/`（目标项目本地预览） |
| 类别注册 | 本地编辑 `skill_categories.json` | MCP `create_commit` search/replace 远程编辑 |
| PR 创建 | `create_skill_pr.ps1` 本地脚本 | MCP `create_branch` → `create_commit` → `create_pull_request` |
| 部署到目标项目 | `python scripts/deploy_skills.py` 或 GUI | 已在本地，无需额外部署 |

**如果两种模式都不可用**（无工具项目 + 无 HSW MCP），使用 ask_questions 引导：
- header: "环境设置"
- question: "当前环境无法访问工具仓库。请选择以下方式之一设置环境："
- 选项A: "添加工具项目到工作区（File > Add Folder to Workspace...）"
- 选项B: "运行 GUI 工具配置 MCP（双击 点我启动.bat）"

### 0a. 提取应用名和命名前缀

从用户消息中提取应用名称（如 "YourApp"、"{{PLATFORM_REPO}}"），然后推导：

- **命名前缀**: 全小写 + 连字符，如 `cardiacct-` 或 `平台-`
- **Skill 命名格式**: `{前缀}{模块名}-expert`

如果用户未明确说应用名，使用 ask_questions 对话框询问：
- header: "应用名称"
- question: "请输入要创建 Skill 的应用/项目名称（如 YourApp、YourPlatform、{{PLATFORM_REPO}}）"
- allowFreeformInput: true，无预设选项

### 0a'. 确定 Skill 层级

> 如已从 `project-profile.json` 读取层级信息，可跳过此步。

使用 ask_questions 确认 Skill 层级：
- header: "Skill层级"
- question: "这批 Skill 属于哪个层级？不同层级的模版章节和行数限制不同。"
- 选项A: "应用层 — 有配置映射，≤120 行" (recommended)
- 选项B: "平台层 — 有搜索策略+核心概念，≤150 行"

**层级差异**：

| | 应用层 | 平台层 |
|---|---|---|
| 行数上限 | ≤ 120 行 | ≤ 150 行 |
| 运行时配置映岄 | ✅ 必填 | ⬜ 跳过 |
| 搜索策略 | ⬜ 跳过 | ✅ 必填 |
| 核心概念 | ⬜ 跳过 | ✅ 必填（5-8 行） |
| 与平台的关系 | ✅ 必填 | ⬜ 跳过 |

### 0b. 获取模块列表

**直接在多根工作区中访问目标项目**，按优先级获取模块列表：

1. **用户提到了模块清单文件** → 直接 `read_file` 读取
2. **搜索现有清单** → 在目标项目中 `file_search` 搜索 `*功能模块清单*`
3. **扫描目录结构推断** → `list_dir` 目标项目关键目录
   - 如有 `project-profile.json`: 使用 `layers[].dirPattern` 扫描对应目录
   - 平台默认: 扫描 `BE/`、`FE/`、`WebFE/` 目录
   - 其他项目: 扫描 `src/`、`packages/`、`modules/` 等通用目录
4. **均无法确定** → 使用 ask_questions 对话框询问用户提供模块列表

对每个模块确定：
- 模块中文名
- 模块英文标识（用于 Skill 命名）
- 一句话职责描述

### 0c. 分析平台继承关系

**仅应用层执行，平台层跳过。**

对每个模块判断与平台的关系：

- **如有 `project-profile.json`**: 读取 `platform.identifier` 构建平台专家前缀
  - 搜索关键词: `project-profile.platform.name` 相关的 import/using/include 语句
  - 平台专家关联: `#{platform_identifier}-{component}-expert`
- **平台默认**（无 profile 时）:
  - 依据 1: 模块名是否与已有 `{{PLATFORM_PREFIX}}-*-expert` 同名
  - 依据 2: 搜索 `using.*平台|import.*平台` 判断是否引用平台
  - 依据 3: 应用特有功能判定为 🆕 独立实现

输出两类：
- 🔄 **扩展继承**: 有对应平台模块 → 记录关联的平台专家
- 🆕 **独立实现**: 无对应平台模块

---

## 🔴 检查点 0：模块清单确认

**必须暂停**，向用户展示以下表格并等待确认：

```markdown
## 📋 模块清单确认

**Skill 层级**: {应用层/平台层}
**应用名**: {AppName}
**命名前缀**: `{app}-`
**模块总数**: {N} 个
**计划分批**: {ceil(N/6)} 批（每批 ≤6 个模块）

| # | 模块 | Skill 名称 | 继承类型 | 关联平台专家 |
|---|------|-----------|----------|-------------|
| 1 | ... | `{app}-{mod}-expert` | 🔄/🆕 | ... |

请确认是否正确，可以增删模块、修改命名、调整继承类型。
```

使用 ask_questions 让用户确认：
- header: "模块确认"
- question: "请看上面的模块列表，确认划分是否合理"
- 选项A（推荐）: "没问题，继续生成"
- 选项B: "需要修改" (allowFreeformInput: true)

---

## Step 1：分批研究 + 生成

### 1a. 读取模版和参考

**多根工作区模式**：
1. 读取 `templates/skills/_templates/module-expert-skill.md` — 获取标准模版结构
2. 读取一个已有的同层级 Skill 作为格式参考：
   - 应用层: `templates/skills/app-*-expert/SKILL.md`
   - 平台层: `templates/skills/{{PLATFORM_PREFIX}}-*-expert/SKILL.md`（若无，到目标项目 `.github/skills/` 找）

**纯目标项目模式**：
1. MCP `get_file_content`(repo=`AdvAppCommonKnowledge`, path=`templates/skills/_templates/module-expert-skill.md`) — 远程读取模版
2. 如目标项目 `.github/skills/_templates/module-expert-skill.md` 存在（GUI 部署时已复制），优先用本地版本
3. 格式参考同上，优先本地 `.github/skills/` 下已有的 Skill

### 1b. 分批深度研究

将模块按 **每批 ≤6 个** 分组，对每一批使用 `runSubagent` 进行深度研究。

**Subagent 研究指令模板**：

```
请对以下 {N} 个模块进行深度研究，目标项目在 {target_project_root}。

模块列表：{module1}, {module2}, ...

对每个模块，请调查以下内容并输出结构化报告：

1. **目录结构**: 列出各代码层级目录下的相关子目录和文件数量
2. **关键类清单**: 找出 3-8 个核心类/接口名称（精确大小写）
3. **命名空间/包名**: 查找模块的命名空间或包名模式
4. **导出/公开接口**: 查找公开接口和导出符号
5. **常见拼写陷阱**: 搜索非标准拼写
{tech_specific_instructions}
```

**技术栈特定研究指令** (`{tech_specific_instructions}`):

| 来源 | 注入内容 |
|--------|----------|
| project-profile.json | 根据 `techStack` 和 `layers` 动态构建 |
| 平台默认（无 profile） | `6. 命名空间宏: {{PLATFORM_NS_PREFIX}}_*_BEGIN_NAMESPACE` + `7. 导出宏: *_Export` + `8. XML 配置关联` |
| C#/.NET 项目 | `6. 命名空间: namespace 声明` + `7. DI 注册: AddScoped/AddTransient` |
| Python 项目 | `6. 包结构: __init__.py 导出` + `7. 装饰器: @app.route/@router.post` |
| Java 项目 | `6. 包名: package 声明` + `7. 注解: @Service/@Controller/@Bean` |
| TypeScript 项目 | `6. 模块导出: export default/export class` + `7. 路由: @Controller/@Get/@Post` |

研究报告产出到对话中，不写文件。每批完成后输出进度。

### 1c. 基于研究逐批生成 SKILL.md

依据研究报告 + 模版结构，为当前批次的每个模块生成 SKILL.md。

**生成位置**:
- **多根工作区模式**: `templates/skills/{app}-{module}-expert/SKILL.md`（工具项目内）
- **纯目标项目模式**: `.github/skills/{app}-{module}-expert/SKILL.md`（目标项目内，本地预览）

**生成规则**：

1. **YAML frontmatter 必填**：`name` 与目录名相同，`description` 含 ≥3 触发关键词
2. **必填章节** — 参考 `module-expert-skill.md` 的标记系统（`[通用]`/`[应用必填]`/`[平台必填]`）
3. **精确性要求**（v3 核心原则）：
   - 类名、文件路径必须来自研究报告的实际扫描结果
   - 禁止编造或推测不存在的符号
   - 拼写陷阱必须有具体文件名为证
4. **行数控制**: 应用层 ≤ 120 行 / 平台层 ≤ 150 行
5. **内容完整性红线**（强制）：
   - ❗ **模板格式不可简化**: 执行声明规范、必填章节等固定格式必须完整保留，禁止压缩或省略
   - ❗ **必要内容不可删减**: 场景入口、陷阱条目、依赖行、配置映射等经验证的内容不得为了行数限制而删除或合并
   - ✅ **超限时拆分到 reference**: 若行数超限，将较大的独立章节（如运行时配置映射、大型表格）拆分到 `references/` 目录
   - 拆分后在 SKILL.md 中保留指针: `📖 详细内容见 \`references/xxx.md\``
6. **业务规则**: 框架完整但内容标记 `🔴 TODO: 待补充`

每生成 3 个 Skill 后输出进度：
> ✅ 批次 {B}/{total}: 已生成 {app}-{mod1}-expert, {app}-{mod2}-expert, {app}-{mod3}-expert

### 1d. [应用层] 配置文件自动填充

> 仅应用层执行，平台层跳过。配置格式从模板 v4 的配置发现规则获取。

**配置发现策略**：

1. **如有 `project-profile.json`**: 使用 `configDiscovery.format` 和 `configDiscovery.basePath`
   - XML: 搜索 `{basePath}/**/*.xml`，提取 `<Operation>`/`<Handler>` 等节点
   - YAML/JSON: 搜索 `{basePath}/**/*.{yaml,yml,json}`，提取路由/服务配置
   - none: 跳过此步
2. **平台默认（无 profile）**: 搜索 XML 配置文件
   - 搜索路径: `file_search("**/appdata/*/config/[你的配置目录]/[配置文件]")`
   - 核心文件: `[后端配置文件]`、`BE/WorkflowController.xml`、`[前端命令配置]`
   - 提取内容: 按模块名 grep 相关 Operation/Widget/Model 注册项
3. **自动填充**: 将提取结果写入各 SKILL.md 的「运行时配置映射」章节，标记 🤖

### 1e. 自动 lint 验证

所有 Skill 生成完毕后，自动在终端运行 lint 检查：

```
python scripts/lint_skills.py --skill {app}-*-expert
```

**lint 检查项**：
- YAML frontmatter 必填字段（name + description）
- 触发词冲突检测（与现有 Skill 无重复）
- references 文件引用有效性
- 名称规范（连字符格式，≤64 字符）

将 lint 结果纳入 CP1 评分卡。如果有 lint 错误，先自动修复，修复后重新 lint，确认全部通过后再进入 CP1。

---

## 🔴 检查点 1：生成质量确认

**必须暂停**，向用户展示 lint 结果 + 质量评分卡：

```markdown
## 📊 生成质量评分卡

### Lint 检查
✅ 全部通过（{N} 个 Skill, 0 个错误）

### 内容评分

| Skill | 行数 | frontmatter | 场景入口 | 上下游 | 得分 |
|-------|------|:-----------:|:--------:|:------:|------|
| `{app}-xxx-expert` | 95 | ✅ | ✅ 3个 | ✅ | 4/4 |
| ... | | | | | |

**评分标准**:
- frontmatter: name + description（含 ≥3 触发关键词）
- 行数: 应用层 ≤120 / 平台层 ≤150
- 场景→入口: ≥ 2 个场景有搜索关键词
- 上下游依赖: 标注了影响程度

> ⚠️ 所有业务规则已标记 🔴 TODO，待领域专家后续补充
```

使用 ask_questions 让用户确认：
- header: "质量确认"
- question: "请看评分卡，如有不满意的可以在输入框里告诉我哪个 Skill 需修改"
- 选项A（推荐）: "都没问题，继续"
- 选项B: "需要调整" (allowFreeformInput: true)

---

## Step 2：注册类别 + 配置

### 2a. 编辑 skill_categories.json

**多根工作区模式** — 本地编辑 `data/skill_categories.json`：

```json
"{app}": {
  "display_name": "{app}",
  "prefixes": ["{app}-"],
  "description": "{AppName} 应用/平台",
  "default_selected": false
}
```

在 `presets` 中添加对应预设：

```json
"{AppName}应用开发": ["platform", "{app}"]
```

**纯目标项目模式** — 通过 MCP `create_commit` 的 search/replace 模式远程修改：
- 先 MCP `get_file_content` 读取当前 `skill_categories.json` 内容
- 用 search/replace 在 `"categories"` 和 `"presets"` 中各插入一条

### 2b. 验证 + 部署说明

执行 `python -c "import json; ..."` 验证 `skill_categories.json` 配置正确、`{app}-*` Skills 数量匹配。

**多根工作区模式 — 部署到目标项目**：使用 ask_questions 询问是否自动部署：
- header: "自动部署"
- question: "是否立即将 Skills 部署到目标项目？"
- 选项A（推荐）: "是，自动部署"
- 选项B: "否，我稍后手动运行 GUI"

如果选择自动部署，在工具项目根目录执行：
```
python scripts/deploy_skills.py --target-path "{target_project_root}" --categories platform,{app} --force
```

> 💡 其他开发者需各自运行 GUI 或 CLI 部署。

**纯目标项目模式**：Skill 已直接生成在 `.github/skills/` 下，无需额外部署。

### 2c. 更新用户偏好（user_preferences.json）

读取 `data/user_preferences.json`，在 `selected_skill_categories` 数组中追加 `"{app}"`（如果不存在的话），确保 GUI 下次启动时默认勾选新应用类别。

---

## 🔴 检查点 2：交付确认

**必须暂停**，向用户展示以下交付清单：

```markdown
## 📦 交付清单

**应用名**: {AppName}
**Skill 数量**: {N} 个模块

### 生成的文件

| 文件路径 | 行数 | 类型 |
|---------|------|------|
| `templates/skills/{app}-xxx-expert/SKILL.md` | ... | SKILL.md |
| `templates/skills/{app}-xxx-expert/references/xxx.md` | ... | reference |
| ... | | |

### 配置注册

| 配置文件 | 变更内容 |
|---------|---------|
| `data/skill_categories.json` | 新增 `{app}` 分类 + `"{AppName}应用开发"` 预设 |

### 部署方式
重启 VS Code 后，通过 `#{app}-xxx-expert` 调用。
每位开发者需各自运行 GUI 工具部署 Skill。
```

展示完清单后，**必须使用 ask_questions 弹出两个交互选项**：

**选择 1 — PR 操作**：
- header: "提交PR"
- question: "Skill 已生成完毕。是否自动创建 PR 并通知审阅人？"
- 选项A（推荐）: "创建 PR 并飞书通知审阅人"
- 选项B: "只创建 PR，不发通知"
- 选项C: "跳过，我手动处理"

**选择 2 — PR 审阅人**（仅选择 A/B 时展示）：
- header: "审阅人"
- question: "PR 审阅人（默认从 shared_config.json 读取）"
- 选项A（推荐）: "YourName (your.email@example.com)" — 从 `shared_config.json` 的 `notification_recipients` 动态读取
- allowFreeformInput: true — 用户可输入其他审阅人姓名或邮箱

> ⚠️ **禁止跳过此 ask_questions 步骤**。展示文件清单 ≠ 交付确认完成，必须等用户通过交互选项选择后才算 CP2 完成。

**A/B** → Step 3 | **C** → 输出部署说明，结束

---

## Step 3：[可选] 提交 PR + 飞书通知

> 📚 **实现原理参考**: `read_file("references/pr-notification.md")` — Step 3 执行前必须读取！

根据 Step 0-pre 选择的运行模式，执行对应的 PR 创建流程。
根据 CP2 的选择确定通知模式：选项 A → PR 并通知 | 选项 B → 仅 PR

### 3-local. 多根工作区模式：本地脚本

在**工具项目根目录**执行（通过 `run_in_terminal`）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_skill_pr.ps1 `
    -AppName "{AppName}" -AppPrefix "{app}" -ModuleCount {N} `
    -Mode "{PRAndNotify|PROnly}"
```

脚本输出 `===RESULT_JSON_BEGIN===`/`===RESULT_JSON_END===` 之间的 JSON 摘要。
退出码: `0`=全成功, `1`=配置错, `2`=Git 失败, `3`=PR 失败, `4`=部分成功。

### 3-remote. 纯目标项目模式：MCP 远程操作

使用 `azureDevOpsHSW` MCP server（工具仓库在 HSW Collection）：

1. **创建分支**: MCP `create_branch` — repo `AdvAppCommonKnowledge`, source `master`, new `skill/{app}-experts`
2. **推送文件**: MCP `create_commit` — 将本地 `.github/skills/{app}-*-expert/` 内容推送到 `templates/skills/{app}-*-expert/`
   - 新文件用 `--- /dev/null` 格式的 unified diff
   - `skill_categories.json` 用 search/replace 模式修改
3. **创建 PR**: MCP `create_pull_request` — reviewers 从 CP2 用户选择获取
4. **飞书通知**（如选择 A）: 通过飞书 MCP 或 `create_skill_pr.ps1` 的飞书 API 发送卡片消息

> 🔴 任何失败都不阻断，降级为提示用户手动处理。详见 `references/pr-notification.md` 中的错误处理表。

---

## 🔴 检查点 3：最终交付确认

展示最终交付结果：Skill 文件列表 + PR 链接 + 飞书通知状态 + 后续事项（业务规则 TODO、等待审阅、GUI 部署）。

---

## 进度模板

每次向用户展示消息时，在开头显示当前进度：

```
📋 Skill 向导 — {AppName}（{层级}）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Step 0: 环境 + 信息收集
✅ CP0: 模块清单确认 (用户已确认)
⭕ Step 1: 分批研究 + 生成 (批次 2/4, 已完成 8/20)
⬜ CP1: 生成质量确认
⬜ Step 2: 注册 + 配置
⬜ CP2: 交付确认（含 PR 选择）
⬜ Step 3: 提交 PR + 飞书通知
⬜ CP3: 最终交付确认
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

状态图标: ✅ 完成 | ⭕ 进行中 | ⬜ 未开始

---

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 工作区未包含目标项目且无 HSW MCP | 引导用户二选一：添加工具项目到工作区 或 运行 GUI 配置 MCP |
| 用户未提供应用名 | 直接询问，不要猜测 |
| 没有找到模块清单文件 | 扫描目录结构推断，或询问用户 |
| `skill_categories.json` 已有同名类别 | 使用 ask_questions 询问是否覆盖 |
| 生成的 Skill 超过行数上限 | 将较大的独立章节拆分到 `references/` 目录，SKILL.md 中保留 `📖 ... 见 references/xxx.md` 指针。**禁止**通过简化模板格式或删减必要内容来降低行数 |
| `templates/skills/{app}-*` 目录已存在 | 使用 ask_questions 询问是否覆盖 |
| runSubagent 研究报告信息不足 | 补发更具针对性的研究指令 |
| DevOps PAT 未配置 | 提示用户运行 GUI 工具配置 PAT |
| `git push` 失败（无远程/权限不足） | 跳过 PR 创建，输出部署说明 |
| DevOps PR API 返回 401/403 | 先检查 PAT Collection 是否匹配 |
| MCP `create_commit` search 不匹配 | 先 `get_file_content` 读取最新内容，调整 search 文本 |
| MCP `azureDevOpsHSW` 不可用 | 降级提示运行 GUI 配置或手动处理 |
| lint 检查发现错误 | 自动修复后重新 lint，全部通过才进 CP1 |
| 飞书通知收件人未配置 | 使用 CP2 用户输入的审阅人邮箱，或提示补充配置 |
| `user_preferences.json` 被外部覆盖 | 写入前先读取最新内容，合并而非全量覆盖 |
| `skill_categories.json` 被外部覆盖丢失类别 | 写入前先读取，确保新增类别不会覆盖已有的其他类别 |
| 飞书 MCP 不可用 | 不阻断流程，提示用户手动发送 PR 链接 |

---

## 参考文件

- **统一模版**: `read_file("templates/skills/_templates/module-expert-skill.md")` — Step 1 前读取（纯目标项目模式用 MCP `get_file_content`）
- **质量标准**: `read_file("references/details.md")`
- **PR + 通知**: `read_file("references/pr-notification.md")` — Step 3 前**必须读取**
- **格式参考**: 任意 `templates/skills/app-*-expert/SKILL.md`（应用层）或 `{{PLATFORM_PREFIX}}-*-expert/SKILL.md`（平台层）
