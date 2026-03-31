# Codex 插件外层约束（工作区约束）

当前目录只负责 Codex plugin 的包装说明，不是运行时 plugin root。

规则：

- 唯一可安装插件根目录固定为同级 `rdc-debugger/`。
- 运行时约束、skills、workspace 语义、`common/` / `tools/` 占位都只在 `rdc-debugger/` 与共享 `debugger/common/` 中维护。
- 当前外层目录只允许放包装说明、安装说明与 marketplace 示例，不要在这里复制 framework 运行规则。
- `references/personal-marketplace.sample.json` 必须继续指向 `./plugins/rdc-debugger`，不要改成旧路径或 source repo 路径。
