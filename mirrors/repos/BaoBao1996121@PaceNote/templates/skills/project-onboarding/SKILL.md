---
name: project-onboarding
description: |
  项目接入辅助 Skill - 提供 ProjectSetup Agent 的 schema 定义、subAgent prompt 模板和质量标记规范。
  触发关键词: project-onboarding, 项目接入辅助, 接入schema, component-map
---

# 项目接入辅助 Skill

> 为 `ProjectSetup` Agent 提供 schema 定义、subAgent prompt 模板、信息分级策略和质量标记规范。
> 不直接面向用户，由 Agent 内部调用。

---

## project-profile.json Schema

```json
{
  "$schema": "project-profile-v1",
  "projectName": "string — 项目显示名",
  "identifier": "string — 英文标识（全小写，用于 Skill 命名前缀）",
  "techStack": ["string — 如 C#, C++, Python, TypeScript"],
  "layers": [
    {
      "name": "string — 层名称（如 Frontend, Backend, Algorithm）",
      "language": "string — 该层主要语言",
      "dirPattern": "string — 该层在仓库中的目录 glob 模式"
    }
  ],
  "platform": {
    "name": "string | null — 平台/框架名称",
    "identifier": "string | null — 平台英文标识（用于 Skill 前缀）",
    "repoPath": "string | null — 平台仓库本地路径",
    "repoUrl": "string | null — 平台仓库远程 URL"
  },
  "repos": [
    {
      "name": "string — 仓库名",
      "localPath": "string — 本地 clone 路径",
      "remoteUrl": "string | null — 远程 URL",
      "type": "platform | application"
    }
  ],
  "configDiscovery": {
    "format": "xml | yaml | json | ini | none",
    "basePath": "string | null — 配置文件根目录（相对于仓库根）",
    "coreFiles": [
      {
        "path": "string — 文件路径（相对于 basePath）",
        "purpose": "string — 此配置文件驱动什么行为",
        "parseTarget": "string — 需要从中提取什么信息"
      }
    ]
  },
  "devopsProject": "string | null — Azure DevOps 项目名",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

## component-map.json Schema

> 平台架构发现阶段的中间产物，由 runSubagent 提取后汇总。

```json
{
  "$schema": "component-map-v1",
  "platform": "string — 平台名称",
  "source_level": "document | description | code_analysis",
  "components": [
    {
      "name": "string — 英文标识（用于 Skill 命名）",
      "displayName": "string — 显示名/中文名",
      "responsibility": "string — 一句话职责（≤50字）",
      "keyInterfaces": ["string — 关键接口/类名"],
      "directory": "string — 代码目录路径（相对于仓库根）",
      "dependencies": ["string — 依赖的其他组件 name"],
      "searchKeywords": ["string — grep 搜索关键词"]
    }
  ],
  "layerMapping": {
    "组件name": ["层name — 该组件涉及的代码层级"]
  }
}
```

**容量约束**: `components` 数组中每个组件的 JSON 表示不超过 200 tokens，总 `component-map.json` 不超过 2000 tokens。

---

## 质量来源标记规范

### Skill 文件内标记

每个由 ProjectSetup 生成的 Skill 文件，在 YAML frontmatter 之后、`# 标题` 之前插入来源标记注释：

```markdown
---
name: xxx-expert
description: |
  ...
---

<!-- generated-by: ProjectSetup v1 -->
<!-- source: document | description | code-analysis -->
<!-- generated-at: 2026-03-27T10:00:00Z -->

# xxx 专家
```

### 质量分级含义

| 标记 | 来源 | 质量预期 | 建议操作 |
|------|------|---------|---------|
| 📗 `document` | 架构文档提供了组件清单和接口信息 | **高** — 组件边界和关键接口准确 | 快速通读确认 |
| 📙 `description` | 用户口头/对话描述了组件信息 | **中等** — 组件存在但接口名可能不全 | 重点检查代码入口和搜索策略 |
| 📕 `code-analysis` | AI 自动分析代码仓库推断 | **需人工把关** — 组件边界可能不准确 | 逐个检查关键接口名称和模块边界 |

### 检查点展示格式

在 CP1/CP2 展示时，质量提示根据 source_level 动态显示：

- `document` → `✅ 本批 Skill 基于架构文档生成，质量较高`
- `description` → `⚠️ 本批 Skill 基于对话描述生成，建议重点检查代码入口`
- `code-analysis` → `🔴 无文档输入情况下生成的平台 Skill 质量需要人工把关，建议逐个 review`

---

## subAgent Prompt 模板

### 文档摘要提取 Prompt

```
你是一个信息提取助手。请从以下文档段落中提取平台/框架的组件信息。

**文档内容**（第 {startLine}-{endLine} 行）:
---
{content}
---

**输出要求**: JSON 数组，每个元素包含:
- name: 组件英文名（适合作为 Skill 命名，全小写连字符）
- displayName: 组件中文/显示名
- responsibility: 一句话职责（≤50字）
- keyInterfaces: 关键接口/类名数组（只写文档中明确提到的）
- directory: 代码目录路径（如文档中提到）
- dependencies: 依赖的其他组件名

**规则**:
1. 只提取文档中**明确提到的**组件，不要推断
2. 如果文档段落不包含组件信息，返回空数组 []
3. 每个组件的 JSON 不超过 200 tokens
```

### 代码仓库扫描 Prompt

```
你是一个代码分析助手。请分析以下仓库的目录结构并识别可能的组件/模块边界。

**仓库路径**: {repoPath}
**技术栈**: {techStack}
**已知分层**: {layers}

**任务**:
1. 用 list_dir 扫描仓库根目录和前 2 层子目录
2. 识别组件/模块边界（按目录名、命名空间推断）
3. 对每个识别到的组件，搜索 1 个代表性头文件/入口文件
4. 搜索通用接口模式: *Interface*, *Service*, *Manager*, *Handler*, *Provider*

**限额**:
- 最多扫描 3 层目录
- 每个组件最多读取 10 个文件的前 50 行
- 总读取量不超过 5000 行

**输出**: JSON 数组（同文档摘要格式） + 置信度标注（high/medium/low）
```

### 平台架构 Skill 生成 Prompt

```
你是一个 Copilot Skill 生成助手。请基于以下组件映射表生成平台架构 Skill。

**平台名**: {platformName}
**平台标识**: {platformIdentifier}
**组件映射**:
{component-map JSON}

**代码分层**:
{layers JSON}

**生成目标**: `{platformIdentifier}-architecture` Skill
**参考格式**: 现有的 `platform-architecture` Skill 结构（分层说明 + 搜索策略 + 意图识别）

**生成规则**:
1. 分层结构按 project-profile.layers 动态构建，不硬编码 平台 层名
2. 搜索策略基于实际仓库路径和组件目录
3. 意图识别关键词从 component-map 的 searchKeywords 提取
4. 不使用 平台/{{PLATFORM_NAME}} 特有术语
5. ≤150 行
```

---

## 配置发现规则模板

> 当 `configDiscovery.format` != "none" 时，指导 AI 如何自动提取运行时配置映射。

### XML 配置发现（兼容现有 平台 结构）

```
搜索路径优先级:
1. {configDiscovery.basePath}/
2. appdata/{identifier}/config/
3. BE/appdata/{identifier}/config/ + FE/appdata/{identifier}/config/
4. 用户自定义路径（ask_questions 收集）

核心文件:
{configDiscovery.coreFiles 数组}
```

### YAML/JSON 配置发现

```
搜索路径优先级:
1. {configDiscovery.basePath}/
2. config/
3. settings/
4. {仓库根}/*.{yaml,yml,json}

提取规则:
- 搜索包含 "route", "handler", "service", "endpoint" 等关键词的配置段
- 提取模块间的路由/消息映射
```

---

## 信息输入安全阈值

| 指标 | 阈值 | 超限行为 |
|------|------|---------|
| 单次文档读取 | ≤500 行 | 分段 + runSubagent 隔离 |
| component-map 总量 | ≤2000 tokens | 压缩 responsibility 字段 |
| 代码扫描深度 | ≤3 层目录 | 停止深入，用关键词搜索补充 |
| 代码扫描文件数 | ≤10 个/组件 | 只读取前 50 行 |
| 单轮收集组件数 | ≤5 个 | 分批收集 |
| 总 Skill 生成批次 | ≤6 个/批 | 与 app-skill-wizard 一致 |
