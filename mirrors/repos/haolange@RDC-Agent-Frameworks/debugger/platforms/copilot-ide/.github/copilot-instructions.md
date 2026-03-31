# Copilot IDE Instructions

当前目录是 Copilot IDE / VS Code 的 platform-local 模板。Agent 的目标是使用 RenderDoc/RDC platform tools 调试 GPU 渲染问题。

先阅读：

1. AGENTS.md
2. common/docs/platform-capability-model.md
3. references/entrypoints.md

未先将顶层 `debugger/common/` 拷入当前平台根目录的 `common/` 之前，不允许在宿主中使用当前平台模板。

运行时工作区固定为平台根目录下的 `workspace/`
