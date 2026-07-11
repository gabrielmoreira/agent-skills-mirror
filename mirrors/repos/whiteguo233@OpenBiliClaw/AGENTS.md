# Repository Guidelines

## 项目结构与模块组织
主代码位于 `src/openbiliclaw/`：`agent/` 负责编排，`bilibili/` 负责站点接入，`memory/`、`soul/`、`discovery/`、`recommendation/` 分别承载理解、发现与推荐链路。测试位于 `tests/`，命名采用 `test_*.py`。设计和路线文档集中在 `docs/`，其中 `docs/v0.1-todolist.md` 是当前 v0.1 的开发主线。浏览器插件代码单独放在 `extension/`，其中 `extension/src/` 为脚本源码，`extension/popup/` 为弹窗页面。

## 构建、测试与开发命令
先创建虚拟环境并安装开发依赖：`pip install -e ".[dev]"`。常用检查命令如下：

```bash
ruff format src/ tests/
ruff check src/ tests/
mypy src/
pytest
pytest --cov=openbiliclaw
```

本地体验 CLI 可使用 `openbiliclaw start`、`openbiliclaw profile`、`openbiliclaw recommend`。如修改配置相关逻辑，请同步验证 `openbiliclaw config-show`。`extension/` 当前未声明独立包管理脚本；若修改插件，请在 PR 中写明手动验证步骤。

## 开发顺序与配置约定
v0.1 开发建议以 `docs/v0.1-todolist.md` 为准，按“连接 -> 理解 -> 发现 -> 推荐 -> 学习 -> 插件 -> 稳定交付”的里程碑顺序推进，避免跳过底层依赖直接做上层体验。配置样例使用 `config.example.toml`；本地调试时基于它生成 `config.toml`，并仅在本机保存 API Key、Cookie 等敏感信息。

## 编码风格与命名约定
Python 统一使用 4 空格缩进、类型注解和清晰的模块边界；公开 API 与核心数据结构应补充简洁 docstring。格式化与 lint 由 Ruff 管理，静态类型检查使用 MyPy 严格模式。模块文件名使用小写下划线风格，如 `openai_provider.py`；测试函数采用 `test_<behavior>` 命名。

## 测试要求
新增功能默认同时补充单元测试；涉及真实 B 站或模型服务的流程，优先拆成可 mock 的单元测试，并将真实调用保留为手动或集成测试。v0.1 目标覆盖率参考 `docs/v0.1-todolist.md`，保持在 70% 以上。提交前至少运行 `pytest`，改动接口、配置或类型定义时同时运行 `mypy src/` 和 `ruff check src/ tests/`。

## 提交与 Pull Request 要求
提交信息遵循 Conventional Commits，例如 `feat: add bilibili auth status command`、`fix: validate missing api key`。PR 说明应包含：变更摘要、测试命令与结果、关联任务或文档入口；如改动 CLI 输出或插件页面，请附终端输出或截图。不要提交真实 `config.toml`、Cookie、API Key 或其他本地敏感数据。

## 文档更新要求（强制）
每次提交、合回 main 或发版，以及任何改动接口、模块边界、数据流、配置、CLI、依赖或对外集成的变更，均强制按范围同步模块文档、变更日志、架构图、CLI 与配置文档、安装器文档；权威逐项清单见 [CLAUDE.md「Documentation Requirements」](CLAUDE.md#documentation-requirements)。

AGENTS.md 面向可能不会自动加载 CLAUDE.md 的非 Claude agent，因此本义务在此独立生效：即使未自动读取 CLAUDE.md，也必须打开上述链接并遵循清单，缺少相应文档更新的分支不得合入。
