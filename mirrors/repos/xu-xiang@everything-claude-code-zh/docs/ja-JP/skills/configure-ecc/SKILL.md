---
name: configure-ecc
description: Everything Claude Code 的交互式安装程序 —— 引导用户将技能（Skills）和规则（Rules）安装到用户级或项目级目录，验证路径，并在需要时优化已安装的文件。
---

# 配置 Everything Claude Code (ECC)

这是 Everything Claude Code 项目的交互式分步安装向导。使用 `AskUserQuestion` 引导用户选择性安装技能（Skills）和规则（Rules），验证其准确性并提供优化建议。

## 触发时机

- 当用户输入 "configure ecc"、"install ecc"、"setup everything claude code" 等指令时
- 当用户希望从此项目中选择性地安装技能或规则时
- 当用户希望验证或修复现有的 ECC 安装时
- 当用户希望为项目优化已安装的技能或规则时

## 前提条件

此技能（Skill）在启动前必须可供 Claude Code 访问。引导启动有两种方式：
1. **通过插件**: `/plugin install everything-claude-code` —— 插件将自动加载此技能
2. **手动**: 仅将此技能复制到 `~/.claude/skills/configure-ecc/SKILL.md`，然后输入 "configure ecc" 启动

---

## 步骤 0: 克隆 ECC 仓库

在安装之前，将最新的 ECC 源代码克隆到 `/tmp`：

```bash
rm -rf /tmp/everything-claude-code
git clone https://github.com/affaan-m/everything-claude-code.git /tmp/everything-claude-code
```

将 `ECC_ROOT=/tmp/everything-claude-code` 设置为后续所有复制操作的源路径。

如果克隆失败（例如网络问题），请使用 `AskUserQuestion` 请求用户提供本地现有的 ECC 克隆路径。

---

## 步骤 1: 选择安装级别

使用 `AskUserQuestion` 询问用户的安装目的地：

```
Question: "您想在哪里安装 ECC 组件？"
Options:
  - "User-level (~/.claude/)" — "适用于所有 Claude Code 项目"
  - "Project-level (.claude/)" — "仅适用于当前项目"
  - "Both" — "通用/共享项位于用户级，项目特定项位于项目级"
```

将选择保存为 `INSTALL_LEVEL`。设置目标目录：
- User-level: `TARGET=~/.claude`
- Project-level: `TARGET=.claude`（相对于当前项目根目录）
- Both: `TARGET_USER=~/.claude`、`TARGET_PROJECT=.claude`

如果目标目录不存在则创建：
```bash
mkdir -p $TARGET/skills $TARGET/rules
```

---

## 步骤 2: 选择并安装技能

### 2a: 选择技能类别

27 个技能被分为 4 个类别。使用 `AskUserQuestion` 并设置 `multiSelect: true`：

```
Question: "您想安装哪些技能类别？"
Options:
  - "Framework & Language" — "Django, Spring Boot, Go, Python, Java, 前端, 后端模式"
  - "Database" — "PostgreSQL, ClickHouse, JPA/Hibernate 模式"
  - "Workflow & Quality" — "TDD, 验证, 学习, 安全审查, 压缩"
  - "All skills" — "安装所有可用技能"
```

### 2b: 确认单个技能

对于所选的每个类别，显示以下完整的技能列表，并请求用户确认或取消选择特定项。如果列表超过 4 项，请以文本形式显示列表，并在 `AskUserQuestion` 中提供“安装所有列出的项”选项，以及供用户粘贴特定名称的“其他”选项。

**类别: Framework & Language（16 个技能）**

| 技能 | 说明 |
|-------|-------------|
| `backend-patterns` | 后端架构、API 设计、Node.js/Express/Next.js 的服务端最佳实践 |
| `coding-standards` | TypeScript、JavaScript、React、Node.js 的通用编码标准 |
| `django-patterns` | Django 架构、基于 DRF 的 REST API、ORM、缓存、信号、中间件 |
| `django-security` | Django 安全：认证、CSRF、SQL 注入、XSS 防护 |
| `django-tdd` | 基于 pytest-django、factory_boy、Mock、覆盖率的 Django 测试 |
| `django-verification` | Django 验证循环：迁移、Lint、测试、安全扫描 |
| `frontend-patterns` | React、Next.js、状态管理、性能、UI 模式 |
| `golang-patterns` | 地道的 Go 模式，构建健壮 Go 应用的约定 |
| `golang-testing` | Go 测试：表格驱动测试、子测试、基准测试、模糊测试 |
| `java-coding-standards` | Spring Boot 的 Java 编码标准：命名、不可变性、Optional、流 |
| `python-patterns` | Pythonic 惯用法、PEP 8、类型提示、最佳实践 |
| `python-testing` | 基于 pytest、TDD、Fixture、Mock、参数化的 Python 测试 |
| `springboot-patterns` | Spring Boot 架构、REST API、分层服务、缓存、异步 |
| `springboot-security` | Spring Security：认证/授权、验证、CSRF、机密信息、速率限制 |
| `springboot-tdd` | 基于 JUnit 5、Mockito、MockMvc、Testcontainers 的 Spring Boot TDD |
| `springboot-verification` | Spring Boot 验证：构建、静态分析、测试、安全扫描 |

**类别: Database（3 个技能）**

| 技能 | 说明 |
|-------|-------------|
| `clickhouse-io` | ClickHouse 模式、查询优化、分析、数据工程 |
| `jpa-patterns` | JPA/Hibernate 实体设计、关系、查询优化、事务 |
| `postgres-patterns` | PostgreSQL 查询优化、模式设计、索引创建、安全 |

**类别: Workflow & Quality（8 个技能）**

| 技能 | 说明 |
|-------|-------------|
| `continuous-learning` | 从会话中自动提取可复用的模式作为已学习技能 |
| `continuous-learning-v2` | 基于本能的学习，具有置信度评分，可进化为技能/命令/智能体 |
| `eval-harness` | 用于评测驱动开发 (EDD) 的正式评测框架 |
| `iterative-retrieval` | 针对子智能体上下文问题的逐步上下文改进 |
| `security-review` | 安全自查表：认证、输入、机密信息、API、支付功能 |
| `strategic-compact` | 建议在逻辑间隔进行手动上下文压缩 |
| `tdd-workflow` | 强制执行 80% 以上覆盖率的 TDD：单元、集成、E2E |
| `verification-loop` | 验证与质量循环模式 |

**独立项目**

| 技能 | 说明 |
|-------|-------------|
| `project-guidelines-example` | 用于创建项目特定技能的模板 |

### 2c: 执行安装

对于所选的每个技能，复制整个技能目录：
```bash
cp -r $ECC_ROOT/skills/<skill-name> $TARGET/skills/
```

注：`continuous-learning` 和 `continuous-learning-v2` 包含额外文件（config.json、钩子、脚本）—— 请确保复制整个目录，而不只是 SKILL.md。

---

## 步骤 3: 选择并安装规则

使用 `AskUserQuestion` 并设置 `multiSelect: true`：

```
Question: "您想安装哪些规则集？"
Options:
  - "Common rules (Recommended)" — "语言无关的原则：编码风格、Git 工作流、测试、安全等（8 个文件）"
  - "TypeScript/JavaScript" — "TS/JS 模式、钩子、基于 Playwright 的测试（5 个文件）"
  - "Python" — "Python 模式、pytest、black/ruff 格式化（5 个文件）"
  - "Go" — "Go 模式、表格驱动测试、gofmt/staticcheck（5 个文件）"
```

执行安装：
```bash
# 通用规则（扁平化复制到 rules/）
cp -r $ECC_ROOT/rules/common/* $TARGET/rules/

# 语言特定规则（扁平化复制到 rules/）
cp -r $ECC_ROOT/rules/typescript/* $TARGET/rules/   # 若选择
cp -r $ECC_ROOT/rules/python/* $TARGET/rules/        # 若选择
cp -r $ECC_ROOT/rules/golang/* $TARGET/rules/        # 若选择
```

**重要**：如果用户选择了语言特定规则但未选择通用规则，请发出警告：
> "语言特定规则扩展了通用规则。如果在没有通用规则的情况下安装，可能会导致覆盖不完整。是否也安装通用规则？"

---

## 步骤 4: 安装后验证

安装后，执行以下自动检查：

### 4a: 确认文件存在

列出所有已安装的文件，并确认它们存在于目标位置：
```bash
ls -la $TARGET/skills/
ls -la $TARGET/rules/
```

### 4b: 检查路径引用

扫描所有已安装 `.md` 文件中的路径引用：
```bash
grep -rn "~/.claude/" $TARGET/skills/ $TARGET/rules/
grep -rn "../common/" $TARGET/rules/
grep -rn "skills/" $TARGET/skills/
```

**如果是项目级安装**，标记指向 `~/.claude/` 路径的引用：
- 如果技能引用了 `~/.claude/settings.json` —— 这通常没有问题（配置始终是用户级的）
- 如果技能引用了 `~/.claude/skills/` 或 `~/.claude/rules/` —— 如果仅安装在项目级，这可能会导致失效
- 如果技能按名称引用了另一个技能 —— 请检查被引用的技能是否也已安装

### 4c: 检查技能间的交叉引用

某些技能会引用其他技能。验证这些依赖关系：
- `django-tdd` 可能引用 `django-patterns`
- `springboot-tdd` 可能引用 `springboot-patterns`
- `continuous-learning-v2` 引用了 `~/.claude/homunculus/` 目录
- `python-testing` 可能引用 `python-patterns`
- `golang-testing` 可能引用 `golang-patterns`
- 语言特定规则引用了 `common/` 中的对应部分

### 4d: 报告问题

针对发现的每个问题，进行报告：
1. **文件**：包含有问题引用的文件
2. **行**：行号
3. **问题**：错误内容（例如：“引用了 ~/.claude/skills/python-patterns，但未安装 python-patterns”）
4. **建议修复**：应采取的行动（例如：“安装 python-patterns 技能”或“将路径更新为 .claude/skills/”）

---

## 步骤 5: 优化已安装的文件（可选）

使用 `AskUserQuestion`：

```
Question: "是否要为项目优化已安装的文件？"
Options:
  - "Optimize skills" — "删除无关部分，调整路径，根据技术栈进行调整"
  - "Optimize rules" — "调整覆盖率目标，添加项目特定模式，自定义工具设置"
  - "Optimize both" — "对所有安装的文件进行完全优化"
  - "Skip" — "保持原样"
```

### 如果优化技能：
1. 读取每个已安装的 `SKILL.md`
2. 询问用户项目的技术栈（如果尚不明确）
3. 针对每个技能，建议删除不相关的部分
4. 在安装目的地（而非源仓库）就地编辑 `SKILL.md` 文件
5. 修复在步骤 4 中发现的路径问题

### 如果优化规则：
1. 读取每个已安装的规则 `.md` 文件
2. 询问用户相关设置：
   - 测试覆盖率目标（默认 80%）
   - 优先的格式化工具
   - Git 工作流约定
   - 安全要求
3. 在安装目的地就地编辑规则文件

**重要**：仅修改安装目的地（`$TARGET/`）的文件，切勿修改源 ECC 仓库（`$ECC_ROOT/`）的文件。

---

## 步骤 6: 安装摘要

清理从 `/tmp` 克隆的仓库：

```bash
rm -rf /tmp/everything-claude-code
```

接下来输出摘要报告：

```
## ECC 安装完成

### 安装目的地
- 级别：[user-level / project-level / both]
- 路径：[目标路径]

### 已安装的技能（[数量]）
- skill-1, skill-2, skill-3, ...

### 已安装的规则（[数量]）
- common（8 个文件）
- typescript（5 个文件）
- ...

### 验证结果
- 发现了 [数量] 个问题，已修复 [数量] 个
- [列出剩余问题]

### 已应用的优化
- [列出所做的更改，或“无”]
```

---

## 故障排除

### "技能未被 Claude Code 识别"
- 确保技能目录中包含 `SKILL.md` 文件（而不仅仅是零散的 `.md` 文件）
- 如果是用户级：检查 `~/.claude/skills/<skill-name>/SKILL.md` 是否存在
- 如果是项目级：检查 `.claude/skills/<skill-name>/SKILL.md` 是否存在

### "规则无效"
- 规则应该是扁平文件，而不是位于子目录中：`$TARGET/rules/coding-style.md`（正确） vs `$TARGET/rules/common/coding-style.md`（扁平安装中不正确）
- 安装规则后，重启 Claude Code

### "项目级安装后的路径引用错误"
- 某些技能假设使用 `~/.claude/` 路径。运行步骤 4 的验证以发现并修复这些问题。
- 对于 `continuous-learning-v2`，`~/.claude/homunculus/` 目录始终是用户级的 —— 这是预期的，不是错误。
