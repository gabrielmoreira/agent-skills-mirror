# Rules / 流程规则

> 顶层 `CLAUDE.md`（Claude Code）和 `AGENTS.md`（Codex）只保留每次都要知道的最小规则；
> 长流程、模板、词典类细则拆到这里，按需查阅。
>
> **为什么放 `docs/rules/` 而不是 `.claude/rules/`**：本项目是 Claude Code + Codex 双 agent。
> `.claude/rules/` 是 Claude Code 专属机制（官方支持 path-scoped 按需加载），但 Codex 读不到它、
> 只读 `AGENTS.md`。放 `docs/rules/` 是 **single source**，两个 agent 都能按需读同一份，不依赖
> 某一家的自动加载、也不需要引入 Ruler 之类工具去同步两份目标文件（Ruler-compatible first）。

| 文件 | 内容 | 什么时候读 |
|------|------|-----------|
| [reporting.md](reporting.md) | 完成状态词典 + 简化汇报协议 | 每次汇报 / 判断"做完了没" |
| [release.md](release.md) | 完整发版流程 + Release Notes 模板 + 写作规则 | 发版时 |

规则增删后更新本索引。

与 [`../guardrails/`](../guardrails/README.md) 分工：
- **guardrails** = 改**某个模块的代码**前读（不变量 / 关键文件 / 测试覆盖）。
- **rules** = **流程怎么走**（汇报、完成状态、发版）。
