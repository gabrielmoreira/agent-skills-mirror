---
name: continuous-learning-v2
description: 基于本能（Instinct）的学习系统，通过钩子（hooks）观察会话，创建带有置信度评分的原子本能，并将其演化为技能（Skills）、命令（Commands）或智能体（Agents）。v2.1 版本增加了项目作用域（project-scoped）的本能，以防止跨项目污染。
origin: ECC
version: 2.1.0
---

# 持续学习（Continuous Learning）v2.1 - 基于本能（Instinct）的架构

一个先进的学习系统，通过原子级“本能（Instincts）”——带有置信度评分的小型学习行为，将你的 Claude Code 会话转化为可复用的知识。

**v2.1** 增加了 **项目作用域本能（project-scoped instincts）** —— React 模式保留在你的 React 项目中，Python 约定保留在你的 Python 项目中，而通用模式（如“始终验证输入”）则在全局共享。

## 何时激活

- 设置从 Claude Code 会话中自动学习
- 配置通过钩子（hooks）提取基于本能的行为
- 调整学习行为的置信度阈值
- 查看、导出或导入本能库
- 将本能演化为完整的技能（Skills）、命令（Commands）或智能体（Agents）
- 管理项目作用域与全局本能
- 将本能从项目作用域提升（Promote）到全局作用域

## v2.1 的新特性

| 特性 | v2.0 | v2.1 |
|---------|------|------|
| 存储 | 全局 (~/.claude/homunculus/) | 项目作用域 (projects/<hash>/) |
| 作用域 | 所有本能应用于所有地方 | 项目作用域 + 全局 |
| 检测 | 无 | git remote URL / 仓库路径 |
| 提升 | 不适用 | 当在 2 个以上项目中看到时，由项目 → 全局 |
| 命令 | 4 个 (status/evolve/export/import) | 6 个 (+promote/projects) |
| 跨项目 | 存在污染风险 | 默认隔离 |

## v2 的新特性（对比 v1）

| 特性 | v1 | v2 |
|---------|----|----|
| 观察 | Stop 钩子（会话结束） | PreToolUse/PostToolUse (100% 可靠) |
| 分析 | 主上下文 | 后台智能体 (Haiku) |
| 粒度 | 完整技能 | 原子级“本能” |
| 置信度 | 无 | 0.3-0.9 加权 |
| 演化 | 直接到技能 | 本能 -> 聚类 -> 技能/命令/智能体 |
| 分享 | 无 | 导出/导入本能 |

## 本能模型（The Instinct Model）

本能是一个小型学习行为：

```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# 偏好函数式风格

## 动作（Action）
在适当时使用函数式模式而非类（classes）。

## 证据（Evidence）
- 观察到 5 次偏好函数式模式的实例
- 用户在 2025-01-15 将基于类的方案纠正为函数式
```

**属性：**
- **原子性（Atomic）** —— 一个触发器，一个动作
- **置信度加权（Confidence-weighted）** —— 0.3 = 尝试性， 0.9 = 几乎确定
- **领域标签（Domain-tagged）** —— code-style, testing, git, debugging, workflow 等
- **证据支持（Evidence-backed）** —— 追踪哪些观察结果创建了它
- **作用域感知（Scope-aware）** —— `project`（默认）或 `global`

## 工作原理

```
会话活动 (在 git 仓库中)
      |
      | 钩子（Hooks）捕获提示词 + 工具使用 (100% 可靠)
      | + 检测项目上下文 (git remote / 仓库路径)
      v
+---------------------------------------------+
|  projects/<project-hash>/observations.jsonl  |
|   (提示词, 工具调用, 结果, 项目)              |
+---------------------------------------------+
      |
      | 观察者智能体读取 (后台, Haiku)
      v
+---------------------------------------------+
|                模式检测                      |
|   * 用户纠正 -> 本能                         |
|   * 错误解决 -> 本能                         |
|   * 重复工作流 -> 本能                       |
|   * 作用域决策：项目还是全局？                |
+---------------------------------------------+
      |
      | 创建/更新
      v
+---------------------------------------------+
|  projects/<project-hash>/instincts/personal/ |
|   * prefer-functional.yaml (0.7) [project]   |
|   * use-react-hooks.yaml (0.9) [project]     |
+---------------------------------------------+
|  instincts/personal/  (全局 GLOBAL)          |
|   * always-validate-input.yaml (0.85) [global]|
|   * grep-before-edit.yaml (0.6) [global]     |
+---------------------------------------------+
      |
      | /evolve 聚类 + /promote 提升
      v
+---------------------------------------------+
|  projects/<hash>/evolved/ (项目作用域)       |
|  evolved/ (全局)                             |
|   * commands/new-feature.md                  |
|   * skills/testing-workflow.md               |
|   * agents/refactor-specialist.md            |
+---------------------------------------------+
```

## 项目检测（Project Detection）

系统会自动检测你当前的项目：

1. **`CLAUDE_PROJECT_DIR` 环境变量** (最高优先级)
2. **`git remote get-url origin`** —— 通过哈希创建可移植的项目 ID (不同机器上的同一仓库获得相同的 ID)
3. **`git rev-parse --show-toplevel`** —— 使用仓库路径作为回退方案 (机器特定)
4. **全局回退** —— 如果未检测到项目，本能将进入全局作用域

每个项目获得一个 12 位的哈希 ID (例如 `a1b2c3d4e5f6`)。位于 `~/.claude/homunculus/projects.json` 的注册文件将 ID 映射到人类可读的名称。

## 快速开始

### 1. 启用观察钩子（Observation Hooks）

添加到你的 `~/.claude/settings.json`。

**如果作为插件安装** (推荐):

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```

**如果手动安装** 到 `~/.claude/skills`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```

### 2. 初始化目录结构

系统在首次使用时会自动创建目录，但你也可以手动创建：

```bash
# 全局目录
mkdir -p ~/.claude/homunculus/{instincts/{personal,inherited},evolved/{agents,skills,commands},projects}

# 项目目录会在钩子首次在 git 仓库中运行时自动创建
```

### 3. 使用本能命令

```bash
/instinct-status     # 显示已学习的本能 (项目 + 全局)
/evolve              # 将相关的本能聚类为技能/命令
/instinct-export     # 将本能导出到文件
/instinct-import     # 从他人处导入本能
/promote             # 将项目本能提升到全局作用域
/projects            # 列出所有已知的项目及其本能数量
```

## 命令

| 命令 | 描述 |
|---------|-------------|
| `/instinct-status` | 显示所有本能 (项目作用域 + 全局) 及其置信度 |
| `/evolve` | 将相关的本能聚类为技能/命令，并建议提升 |
| `/instinct-export` | 导出本能 (可按作用域/领域过滤) |
| `/instinct-import <file>` | 带有作用域控制地导入本能 |
| `/promote [id]` | 将项目本能提升到全局作用域 |
| `/projects` | 列出所有已知的项目及其本能数量 |

## 配置

编辑 `config.json` 以控制后台观察者：

```json
{
  "version": "2.1",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  }
}
```

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `observer.enabled` | `false` | 启用后台观察者智能体 |
| `observer.run_interval_minutes` | `5` | 观察者分析观察结果的频率 |
| `observer.min_observations_to_analyze` | `20` | 分析运行前最少需要的观察次数 |

其他行为 (观察捕获、本能阈值、项目作用域划分、提升标准) 通过 `instinct-cli.py` 和 `observe.sh` 中的代码默认值进行配置。

## 文件结构

```
~/.claude/homunculus/
+-- identity.json           # 你的个人资料，技术水平
+-- projects.json           # 注册表：项目哈希 -> 名称/路径/远程地址
+-- observations.jsonl      # 全局观察结果 (回退方案)
+-- instincts/
|   +-- personal/           # 全局自动学习的本能
|   +-- inherited/          # 全局导入的本能
+-- evolved/
|   +-- agents/             # 全局生成的智能体
|   +-- skills/             # 全局生成的技能
|   +-- commands/           # 全局生成的命令
+-- projects/
    +-- a1b2c3d4e5f6/       # 项目哈希 (来自 git remote URL)
    |   +-- observations.jsonl
    |   +-- observations.archive/
    |   +-- instincts/
    |   |   +-- personal/   # 项目特定的自动学习
    |   |   +-- inherited/  # 项目特定的导入
    |   +-- evolved/
    |       +-- skills/
    |       +-- commands/
    |       +-- agents/
    +-- f6e5d4c3b2a1/       # 另一个项目
        +-- ...
```

## 作用域决策指南

| 模式类型 | 作用域 | 示例 |
|-------------|-------|---------|
| 语言/框架约定 | **项目 (project)** | "使用 React hooks", "遵循 Django REST 模式" |
| 文件结构偏好 | **项目 (project)** | "测试文件位于 `__tests__`/", "组件位于 src/components/" |
| 代码风格 | **项目 (project)** | "使用函数式风格", "偏好数据类 (dataclasses)" |
| 错误处理策略 | **项目 (project)** | "使用 Result 类型处理错误" |
| 安全实践 | **全局 (global)** | "验证用户输入", "清理 SQL (Sanitize SQL)" |
| 通用最佳实践 | **全局 (global)** | "先写测试", "始终处理错误" |
| 工具工作流偏好 | **全局 (global)** | "修改前先 Grep", "写入前先读取" |
| Git 实践 | **全局 (global)** | "约定式提交", "小型专注的提交" |

## 本能提升 (项目 -> 全局)

当同一个本能在多个项目中以高置信度出现时，它是提升到全局作用域的候选者。

**自动提升标准：**
- 相同的本能 ID 出现在 2 个以上项目中
- 平均置信度 >= 0.8

**如何提升：**

```bash
# 提升特定的本能
python3 instinct-cli.py promote prefer-explicit-errors

# 自动提升所有符合条件的本能
python3 instinct-cli.py promote

# 预览而不应用更改
python3 instinct-cli.py promote --dry-run
```

`/evolve` 命令也会建议提升候选者。

## 置信度评分

置信度随时间演化：

| 分数 | 含义 | 行为 |
|-------|---------|----------|
| 0.3 | 尝试性 | 建议但不强制执行 |
| 0.5 | 中等 | 在相关时应用 |
| 0.7 | 强 | 自动批准应用 |
| 0.9 | 几乎确定 | 核心行为 |

**置信度增加** 当：
- 模式被重复观察到
- 用户未纠正建议的行为
- 来自其他来源的类似本能达成一致

**置信度降低** 当：
- 用户明确纠正该行为
- 长期未观察到该模式
- 出现矛盾证据

## 为什么使用钩子（Hooks）而非技能（Skills）进行观察？

> "v1 依赖技能进行观察。技能是概率性的 —— 基于 Claude 的判断，它们大约有 50-80% 的触发率。"

钩子（Hooks）是 **100% 触发** 的，具有确定性。这意味着：
- 每一个工具调用都被观察到
- 不会遗漏任何模式
- 学习是全面的

## 向后兼容性

v2.1 完全兼容 v2.0 和 v1：
- `~/.claude/homunculus/instincts/` 中现有的全局本能仍作为全局本能工作
- v1 中现有的 `~/.claude/skills/learned/` 技能仍可工作
- Stop 钩子仍运行 (但现在也向 v2 提供数据)
- 平滑迁移：并行运行两者

## 隐私

- 观察结果保存在你的机器 **本地**
- 项目作用域本能按项目隔离
- 只有 **本能** (模式) 可以被导出 —— 而不是原始观察结果
- 不会分享实际的代码或对话内容
- 你可以控制哪些内容被导出和提升

## 相关内容

- [Skill Creator](https://skill-creator.app) - 从仓库历史生成本能
- Homunculus - 启发了 v2 基于本能的架构的社区项目 (原子观察、置信度评分、本能演化流水线)
- [长篇指南 (The Longform Guide)](https://x.com/affaanmustafa/status/2014040193557471352) - 持续学习章节

---

*基于本能的学习：教会 Claude 你的模式，一次一个项目。*
