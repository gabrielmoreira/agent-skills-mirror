向用户简洁呈现 `/guide` 的所有可用子命令（包括未在 `SKILL.md` 中默认展开的扩展子命令）。

若怀疑 `references/` 目录下有新增但尚未登记的子命令文件，可先查看 `references/` 目录下的文件列表再汇总输出。

当前可用子命令：
- `/guide load`: 探测项目环境，了解最近变更、工作流与项目规约，加载 `TODO.md`（`references/load.md`）
- `/guide spec [内容]`: 记录长期生效规范，或在偏离规范时重新加载并对照应用 Spec（`references/spec.md`）
- `/guide test [操作]`: 维护 `tests/` 下的测试用例集，或触发测试验证（`references/test.md`）
- `/guide log [简述]`: 记录开发日志到 `backlog/`、更新 `TODO.md`、清理已消费的 `HANDOFF.md` 并提交变更（`references/log.md`）
- `/guide handoff [焦点]`: 生成或更新跨会话工程交接文档 `HANDOFF.md`（`references/handoff.md`）
- `/guide readme [诉求]`: 创建或更新面向人类阅读的项目 `README.md`（`references/readme.md`）
- `/guide help`: 简洁呈现所有 `/guide` 子命令及其用途（`references/help.md`）
