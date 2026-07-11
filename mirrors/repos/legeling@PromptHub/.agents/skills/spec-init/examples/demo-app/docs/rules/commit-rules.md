# 提交规范

## 职责边界

- 本文件负责：提交标题、提交正文结构、提交与文档记录的关联方式。
- 本文件不负责：变更工作区生命周期或文档归档路径；分别见 `change-management-rules.md` 和 `document-archive-rules.md`。

## 基本原则

- 每次提交必须对应一个清晰的改动点，不把多个无关需求、bugfix 或重构揉进同一个提交。
- 每次提交必须能关联到一个主要文档入口：`docs/changes/active/<change-key>/`、`docs/issues/`、`docs/workflow/01-requirements/README.md` 或其他明确的需求 / 设计 / 验证文档。
- 提交语言应跟随当前项目主要文档语言。中文项目用中文标题和正文；英文项目用英文标题和正文。
- 提交正文必须记录修改目的、修改范围、影响范围和测试状态，不能只写一个短标题。
- 提交正文中没有内容的关联项或状态项必须整行省略，不要写 `无`、`不适用` 或空占位。
- 提交前必须完成必要的一致性分析和文档收敛检查，并确认文档、测试和变更记录已经同步。

## 标题格式

```text
<type>: <简短标题>
```

常用 `type`：

- `feat`: 新功能、需求新增或能力扩展
- `fix`: bug 修复、异常路径修复
- `docs`: 文档、规则、示例或说明变更
- `test`: 测试、回归套件、fixtures 或覆盖映射变更
- `refactor`: 不改变外部行为的结构调整
- `chore`: 构建、脚本、依赖、仓库维护
- `release`: 发布记录、版本说明或交付整理

标题要求：

- 使用当前项目语言写一句可读标题。
- 标题说明结果，不只描述动作。
- 标题不超过 72 个字符；超过时把细节放进正文。

## 正文格式

```text
摘要：
一句话说明本次提交的核心目的。

关联：
- Issue: #123 或 docs/issues/README.md#...
- Change: docs/changes/active/CHG-0001-xxx/
- Requirement: FR-001 / AC-001 / docs/workflow/01-requirements/README.md
- Design: DES-001 / docs/workflow/02-design/README.md
- Verification: TEST-001 / docs/workflow/04-verification/README.md

修改范围：
- [文件或模块 1]
- [文件或模块 2]

影响范围：
- [可能受影响的功能、模块、用户流程或发布面]

测试状态：
- [已运行的测试命令和结果]
- [未运行的测试及原因]
- [残余风险或需要人工复核的点]

详细变更：
- [具体变更 1]
- [具体变更 2]
```

如果某一条目没有内容，整行省略；不要写 `无`、`不适用`、`N/A` 或类似空值。

示例：

```text
关联：
- Change: docs/changes/completed/CHG-20260624-001-homepage-hero/
- Frontend: frontend/web@bd4be12
```

不要写：

```text
关联：
- Change: docs/changes/completed/CHG-20260624-001-homepage-hero/
- Requirement: 无
- Design: 无
- Test: 无
```

## 关联规则

- 一个提交只能绑定一个主要 change workspace 或一个主要 Issue。
- 一个提交可以引用多个 `FR-*` / `DES-*` / `TEST-*`，但必须有一个主线目标。
- 新需求、bugfix、重构或流程变化必须关联 `docs/changes/active/<change-key>/` 或对应的 completed / legacy 记录。
- bugfix 必须关联 Issue 或 bug 记录，并在测试状态中写明回归验证。
- 纯文档提交也必须说明关联的规则、需求、设计或变更文档。
- 如果没有现成 Issue 或 change workspace，先补文档记录，再提交。

## 范围规则

- 一次提交只解决一个需求、一个 bug、一个重构目标或一个文档规则改动。
- 不要把“实现功能 + 修无关 bug + 格式化全仓库”放在同一提交。
- 如果同一轮工作必须修改多个模块，正文必须解释这些模块为什么属于同一个改动点。
- 只允许在正文中记录本提交实际修改过的文件、模块和影响面，不要写泛泛的项目愿景。

## 测试状态规则

- `测试状态` 必须写明实际运行过的命令，例如 `bash tests/spec-init.sh`。
- 测试失败时不能提交为完成态，除非提交目的就是记录失败测试或测试基线，并且正文明确说明。
- 未运行测试时必须说明原因，例如“仅修改 README，无可执行测试；已人工检查链接和示例格式”。
- 涉及高风险路径、bugfix、数据模型、接口契约或权限边界时，必须写明回归测试和残余风险。

## 示例

```text
docs: 补充提交规范和文档关联规则

摘要：
为项目脚手架新增结构化提交规范，要求每次提交记录关联文档、修改范围、影响范围和测试状态。

关联：
- Change: docs/changes/active/CHG-0001-template/
- Requirement: FR-001 / docs/workflow/01-requirements/README.md
- Design: DES-001 / docs/workflow/02-design/README.md
- Verification: TEST-001 / docs/workflow/04-verification/README.md

修改范围：
- skills/spec-init/assets/templates/project/zh/docs/rules/commit-rules.md.tmpl
- skills/spec-init/assets/templates/project/en/docs/rules/commit-rules.md.tmpl
- skills/spec-init/scripts/spec-init.sh
- tests/spec-init.sh

影响范围：
- 新项目初始化后会生成提交规范文档
- agent 和开发者提交变更时需要补充结构化提交正文

测试状态：
- 已运行：bash tests/spec-init.sh，结果通过
- 残余风险：旧项目需要手动复制该规则文件

详细变更：
- 新增 `docs/rules/commit-rules.md` 模板
- 在规则导航、AGENTS、README 和 smoke test 中登记提交规范
- 明确一次提交只能关联一个主变更点，并必须说明测试状态
```
