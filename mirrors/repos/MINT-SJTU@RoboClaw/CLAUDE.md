# RoboClaw Agent 开发指南

> 相关文档：
> - 产品愿景：[`docs/product-vision.md`](docs/product-vision.md)
> - 架构设计：[`docs/architecture.md`](docs/architecture.md)
> - 架构对比（LeRobot / dimos / RoboClaw）：[`docs/architecture-comparison.md`](docs/architecture-comparison.md)

---

运用第一性原理思考，拒绝经验主义和路径盲从，不要假设我完全清楚目标，保持审慎，从原始需求和问题出发，若目标模糊请停下和我讨论，若目标清晰但路径非最优，请直接建议更短、更低成本的办法。

---

## 前置依赖

建议安装 [Codex 插件](https://github.com/openai/codex-plugin-cc) 以启用 Claude + Codex 并行协作。

## 工作规范

### 并行协作（Claude sub-agent + Codex sub-agent）

所有非 trivial 的实现任务，必须起两个并行 **sub-agent** 写完全相同的代码：
- **Claude sub-agent**：用 Agent tool 启动，`isolation: "worktree"` 在独立 git worktree 中工作。
- **Codex sub-agent**：手动创建 git worktree（`git worktree add /tmp/roboclaw-codex-xxx HEAD`），然后用 `/codex:rescue` 在该 worktree 中执行。
- 两个 sub-agent **同时启动**，写完全相同的任务。完成后对比两个版本，取各自优点合并到主分支。
- 合并后清理所有 worktree。

### 提交前双路审查

commit 前必须跑两个 review（同样用 sub-agent 并行）：
- **Claude sub-agent** 执行 `/simplify`：检查代码复用、质量、效率。发现问题直接修。
- **Codex sub-agent** 执行 `/codex:review`：从独立视角审查，发现盲点。大的改动可追加 `/codex:adversarial-review` 挑战设计假设。
- 审查必须覆盖本文件中的所有代码规范（缩进层数、文件行数、try/except、复用等），不能只看功能正确性。

### 架构原则

- 对象优先：所有功能从对象建模出发——先识别实体与职责边界，再设计对象间的协作关系。
- 物理文件组织必须直接反映逻辑架构。目录名、文件名、包结构要让人一眼看出模块职责和层级关系。如果架构调整了，文件结构必须同步调整。

### 代码规范

- 框架代码放 `roboclaw/embodied/`，用户资产放 `~/.roboclaw/workspace/embodied/`。
- 不写向后兼容代码。不保留旧接口、不做 fallback 适配、不写 deprecated wrapper。旧的不要了就直接删掉。
- 不用 try/except 吞错误。有报错就让它直接抛出来，不要静默捕获。只在确实需要处理特定异常时才 catch。
- 复用优先。已有实现的功能不要重复造轮子，先找现有代码再决定是否新写。
- 单个 .py 文件不超过 1000 行。超过时必须将独立逻辑拆分到单独的模块。
- 嵌套不超过 3 层缩进。超过时应将内层逻辑提取为独立函数。

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health


---
