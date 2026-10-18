# 贡献指南

[English](CONTRIBUTING.md)

感谢你考虑为 `claude-tap` 做出贡献。

本项目是面向 AI 编程客户端的本地代理和 trace 查看器。变更可能影响请求路由、凭证处理、trace 文件和生成的 HTML，因此范围明确的小型 PR 更便于 review。

## 从这里开始

1. 为缺陷、功能请求和行为变更创建 issue，修复方式显而易见时可直接提交。
2. 每个 PR 聚焦一个问题。
3. 提供执行过的命令，以及相关 trace、截图或录屏证据。
4. 不要在 issue 或 PR 中包含私密提示词、API 密钥、认证 token、本地文件内容或未脱敏的 `.traces/` 输出。

维护者和自动化专用流程见 `AGENTS.md`。外部贡献者不需要遵守仅适用于 agent 的步骤，例如使用 `gh` 创建 PR 或使用仓库 skill。

## 开发环境

```bash
git clone https://github.com/liaohch3/claude-tap.git
cd claude-tap
uv sync --extra dev
```

开发时运行本地 CLI：

```bash
uv run python -m claude_tap --help
```

## 本地检查

运行与变更相关的检查：

```bash
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
uv run --extra dev pytest tests/ -x --timeout=60
```

修改查看器或浏览器相关行为时，先安装 Playwright 浏览器：

```bash
uv run playwright install chromium
uv run --extra dev pytest tests/test_nav_browser.py tests/test_responses_browser.py -x --timeout=60
```

真实端到端测试需要可用的 Claude CLI 或 Codex CLI 账号，并且需要显式启用：

```bash
uv run --extra dev pytest tests/e2e/ --run-real-e2e --timeout=300
```

## PR 检查清单

- 说明问题和用户可见的行为变更。
- 列出验证命令及结果。
- 行为变化时添加或更新测试。
- 用户可见行为变化时，同步更新相关英文和简体中文文档。
- 查看器 UI 变更应包含截图或录屏。
- 对所有 trace 证据中的私密数据脱敏。

## 发布说明

已发布版本记录在 `CHANGELOG.md` 和 `CHANGELOG.zh.md` 中。需要出现在下次发布中的变更，应在两份文件的 `## [Unreleased]` 下添加对应的英文和简体中文说明，或写入维护者指定的版本章节。发布生成器会同时转移两种语言的说明；只有一种语言有内容时会拒绝更新。

## 报告安全问题

不要为敏感安全问题创建公开 issue。在分享利用细节、私密 trace、凭证或其他敏感材料前，请私下联系维护者。
