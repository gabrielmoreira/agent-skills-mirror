---
name: expert-index
description: |
  专家索引 - 智能推荐合适的领域专家。
  触发关键词: 推荐专家、不确定找谁、哪个专家、专家列表、帮我选专家、有哪些专家。
  输入: 问题描述或功能关键词。
  输出: 推荐的专家列表及调用方式。
  **重要**: 这是唯一维护专家列表的地方，其他 skill 通过引用此索引获取专家信息。
---

# 专家索引

帮助用户找到最合适的领域专家，提供智能路由服务。

## 使用方式

当你不确定该问哪个专家时，描述你的问题，我会推荐合适的专家。

---

## 专家分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    专家四层路由架构                           │
└─────────────────────────────────────────────────────────────┘

【Layer 1】工作流专家 - 研发阶段驱动
  pbi-reviewer, roundtable-debate, coding-agent
              ↓
【Layer 2】应用业务专家 (Layer 4 代码) - 应用特定业务
  {app-prefix}-*-expert
              ↓ 继承/扩展 or 独立
【Layer 3】平台模块专家 (Layer 3 代码) - 通用平台能力
  {{PLATFORM_REPO}}-roi-expert, {{PLATFORM_REPO}}-suv-expert, {{PLATFORM_REPO}}-layout-expert
              ↓
【Layer 4】平台框架知识 - 已整合到各专家中
```

### 🔑 关键判断：应用专家 vs 平台专家

| 用户问题特征 | 推荐专家类型 | 示例 |
|-------------|-------------|------|
| 提到具体应用名 | 应用专家 | `app-[模块名]-expert` |
| 提到业务场景关键词 | 应用专家 | 匹配触发词最相关的专家 |
| 问"应用中的XXX"或"当前项目" | 应用专家 | 根据功能匹配 |
| 问"平台组件"或"框架" | 平台专家 | `{{PLATFORM_REPO}}-[模块名]-expert` |
| 未指定应用，问通用功能 | 使用 ask_questions 对话框先问用户确认 | ROI→先确认是应用还是平台（header: "专家类型"，选项: 应用专家/平台专家） |

---

## 路由策略（四层优先级）

AI 执行此 skill 时，按以下优先级查找专家：

### 0️⃣ 应用上下文识别（新增）

**首先判断用户当前工作区属于哪个应用**：

```markdown
1. 检查工作区名称 → 优先匹配对应应用的域专家
2. 检查 user_preferences.json 的 last_target_path
3. 如果明确在某应用上下文，同类问题优先推荐该应用的专家
```

### 1️⃣ 扫描 Skills 目录（唯一数据源）

**🔴 扫描 `.github/skills/*/SKILL.md` 的 frontmatter**

```python
# 执行方式
for skill_dir in list_dir(".github/skills/"):
    if skill_dir.startswith("_"):  # 跳过 _templates 等
        continue
    skill_md = read_file(f".github/skills/{skill_dir}/SKILL.md")
    # 解析 YAML frontmatter 中的 name 和 description
    # description 包含触发关键词
```

> ⚠️ **触发关键词在每个 SKILL.md 的 description 字段中定义**
> 
> 格式示例: `触发关键词: ROI、轮廓、测量、标注`

**匹配方式**: 
1. 解析每个 SKILL.md 的 `description` 字段
2. 提取"触发关键词:"后面的词汇
3. 用户问题与触发词进行正则匹配（忽略大小写）

### 2️⃣ 分类优先级

匹配到多个专家时，按以下优先级排序：
1. **工作流专家** - pbi-reviewer、coding-agent、platform-architecture
2. **应用专家** - app-*-expert（与当前工作区匹配时优先）
3. **平台专家** - {{PLATFORM_REPO}}-*-expert
4. **工具专家** - 其他辅助工具

### 3️⃣ 用户确认（多选情况）

如果匹配到多个专家，使用 ask_questions 对话框列出候选让用户选择：
- header: "专家选择"
- question: "匹配到多个专家，请选择最匹配的"
- 选项: 每个候选专家作为一个选项，最相关的标记为 recommended

---

## 动态发现机制

**AI 执行此 skill 时，请先扫描 `.github/skills/` 目录获取最新的专家列表。**

扫描方式:
1. 读取 `.github/skills/*/SKILL.md` 文件
2. 解析 YAML frontmatter 中的 `name` 和 `description`
3. 根据 description 中的触发词进行匹配

这样用户添加新 skill 后，无需手动更新此索引。

---

## 内置工作流 Skills (研发阶段)

按研发流程顺序使用:

| Skill | 触发词 | 说明 |
|-------|--------|------|
| `#platform-architecture` | 平台、组件、架构、框架 | 🆕 **首先识别代码层级**，避免混淆平台和应用代码 |
| `#pbi-reviewer` | 需求返讲、评审需求、分析需求、看PBI | 需求分析、返讲流程和文档生成 |
| `#coding-agent` | 开发、实现、编码、按设计实现 | 设计驱动编码、逐任务自动实现 |

### ⚠️ 重要提示：先识别代码层级

当用户问到 **平台**、**组件**、**平台** 相关问题时：
1. 先参考 `#platform-architecture` 确定代码在哪个仓库
2. **{{PLATFORM_REPO}}** = 平台层代码，需通过 MCP DevOps 搜索
3. **app-*** = 应用层代码，在当前工作区搜索

---

## 领域专家 Skills (动态加载)

> **注意**: 以下是常见的领域专家示例。实际可用专家请扫描 `.github/skills/` 目录。
> 用户可以通过将专家 skill 复制到 skills 目录来扩展。

### 常见关键词 → 专家映射

```
# 数据管理
DICOM|数据加载|PA加载 → dataload 相关专家
保存|导出|截图|发送 → datasave 相关专家
联动|同步|翻页 → datalinkage 相关专家

# 图像显示
布局|Layout|Cell → layout 相关专家
窗宽窗位|缩放|平移 → imagetools 相关专家
伪彩|调色板|LUT → palette 相关专家
VRT|3D|体绘制 → vrt 相关专家
Cine|播放|动画 → cine 相关专家

# 测量分析
ROI|轮廓|测量|标注 → roi 相关专家
VOI|组织|分割|病灶 → tissue 相关专家
SUV|PET|摄取值 → suv 相关专家
密度|HU值|CT值 → density 相关专家

# 框架架构
Workflow|WorkStep|BE层 → be-framework 相关专家
ViewModel|Command|FE层|WPF → fe-framework 相关专家
TypeScript|Vue|WebFE → webfe-framework 相关专家
```

---

## 📱 应用层域专家 (Layer 4)

<!-- 🤖 AI 填充指南
将以下提示词发送给你的 AI 助手：

---
我的应用有以下业务模块：
[列出你应用的核心业务模块]

请帮我生成域专家映射表，格式如下：
| 专家 Skill 名 | 触发词 | 说明 |

每个模块对应一个域专家，触发词应包含用户可能使用的中英文关键词。
---
-->

> 以下是应用层的业务域专家示例。实际可用专家请扫描 `.github/skills/` 目录。
> 使用 `#app-skill-wizard` 可以交互式创建新的域专家。

| 专家 | 触发词 | 说明 |
|------|--------|------|
| `#app-[模块名]-expert` | [业务关键词] | [模块功能描述] |

### 应用专家使用示例

```
用户: [某业务功能]怎么实现的?

AI执行:
1. 匹配关键词 → 对应的域专家
2. 读取专家 Skill 获取模块知识
3. 在 src/ 目录搜索相关代码
```

---

## 执行流程

```
用户问题
    ↓
1. 【SKILL.md 扫描】读取 .github/skills/ 目录下各 SKILL.md 的 YAML frontmatter
    ↓
2. 【description 匹配】根据 description 字段的触发词匹配用户问题
    ↓
3. 【返回结果】推荐专家列表，多选时使用 ask_questions 对话框让用户确认
    - header: "专家推荐"
    - question: "为您推荐以下专家，请选择"
    - 选项: 各候选专家（最匹配的标记为 recommended）
```

> ⚠️ **注意**: Skill 触发词定义在各 SKILL.md 的 YAML frontmatter 中。
> PBI CSV 路径等敏感配置存储在 `data/user_preferences.json`（已 .gitignore 排除）。

## 使用示例

### 示例1: 不确定问哪个专家

```
用户: 病灶分割的代码在哪里?

AI执行:
1. 扫描 skills 目录
2. 匹配关键词 "病灶|分割" → tissue 相关
3. 推荐找到的 tissue 专家 + coding-agent
```
### 示例2: 查看所有专家

```
用户: 有哪些专家可以用?

AI执行:
1. 扫描 skills 目录
2. 列出所有找到的专家及其触发词
```

---

## 维护说明

**唯一真相源**: 此文件是专家列表的唯一维护点。

**添加新专家**: 
1. 将专家 skill 文件夹复制到 `.github/skills/` 
2. 确保 SKILL.md 有正确的 YAML frontmatter (name, description, 触发关键词)
3. 无需手动更新此索引 - AI 会动态发现

**其他 skill 如何获取专家**:
- 不要硬编码专家列表
- 使用 "请参考 `#expert-index`" 引导用户

---

用户问题: {{ input }}
