# `setup-matt-pocock-skills` 的 Verify/Check Mode

本项目不会为 `setup-matt-pocock-skills` 增加专门的 verify/check mode（或单独的 verify skill）。

## 为什么这不在范围内

第二个 skill，或一个 `--verify` flag，用来检查 `docs/agents/*.md` artifact 是否仍匹配 seed-template schema，会重复现有 setup skill 已经能在对话中完成的工作。

预期工作流是：**运行 `/setup-matt-pocock-skills`，并告诉它验证当前配置。** 这个 skill 是 prompt-driven 的，因此维护者可以把它限定为一次验证 pass（“不要重写任何内容，只检查我现有文件和当前 seed templates 的漂移并报告”），不需要单独代码路径。增加 flag 或姊妹 skill 会拆分一个已经能通过自然语言入口表达的功能面。

把配置管理保留在单个 skill 中，也能避免两个 skills 在 seed templates 演进时彼此漂移。

## Prior requests

- #106 — Feature request: verify/check mode for setup-matt-pocock-skills
