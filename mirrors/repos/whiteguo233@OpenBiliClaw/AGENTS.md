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
**每次合回 main / 发版前都必须同步更新文档与架构图**。不限于"todolist 任务完成时"——任何改动接口、模块边界、数据流、配置、CLI、依赖、对外集成的提交都触发本规则。缺少文档更新的分支不应合入。

### 必须更新（按 PR 范围适配）
1. **模块文档** `docs/modules/<模块>.md`：改动了某模块的代码 → 更新该模块文档的"已实现功能"表格和"公开 API"部分。新增 / 移除的类、方法、异常都要记录。
2. **变更日志** `docs/changelog.md`：每次发版都在顶部追加版本条目（`## vX.Y.Z: 主题（YYYY-MM-DD）`），列出该版本的核心交付。每个 PR 也至少在当前版本块里加一条短描述。
3. **架构图与架构说明** `docs/architecture.md` + `docs/spec.md` §3 系统架构图 + `README.md` / `README_EN.md` 顶部架构图：改动涉及跨模块交互、新增模块、新增源 / adapter、数据流变化、新增大块依赖（如 embedding 服务、xhs 路径） → 更新对应文字层次和 ASCII / Mermaid 图。**架构图不是装饰——它必须反映 main 上的实际代码状态**。
4. **CLI 命令参考** `docs/modules/cli.md`：新增 / 删除 / 重命名 CLI 命令时一并更新命令一览表和详细子节。
5. **配置参考** `docs/modules/config.md`：新增 / 重命名 / 删除 `config.toml` 字段时一并更新对应段落。

### 按 PR 类型按需更新
6. **文档导航** `docs/index.md`：新增模块文档、模块状态变化、新增高亮文档。
7. **README** `README.md` 和 `README_EN.md`：定位变化、Tagline 变化、核心特性变化、安装 / 一键脚本流程变化、新版本 release。
8. **GitHub About**（`gh repo edit --description`）：项目定位发生变化时同步刷新仓库 About 描述和 topics。
9. **install / agent docs**（`scripts/install.sh`、`docs/agent-install.md`、`docs/docker-deployment.md`）：装机流程、依赖、可选启用项变化。
10. **changelog 顶部 highlights / README 📌 callout**：每次有用户可感知的较大变化（性能、行为差异、新依赖）都顶到 README 顶部的 v0.X.Y 重要更新块里。

### 文档模板
所有 `docs/modules/*.md` 遵循统一结构：概述 → 已实现功能（表格）→ 公开 API（代码示例）→ 配置项 → 设计决策。详见现有模块文档作为参考。

### 检查清单（PR 自检）
合并前过一遍：

- [ ] 改动的模块对应的 `docs/modules/<模块>.md` 已更新
- [ ] `docs/changelog.md` 顶部已追加条目
- [ ] 改了架构 / 数据流 / 新增源 → `docs/architecture.md` + `docs/spec.md` 架构图 + `README.md` 顶部架构图都已同步
- [ ] 改了 CLI / config → `docs/modules/cli.md` / `docs/modules/config.md` 同步
- [ ] 装机 / 安装流程变化 → `scripts/install.sh` 输出 + `docs/agent-install.md` + `docs/docker-deployment.md` 同步
- [ ] 项目定位 / tagline 变化 → README 中英文 + GitHub About 同步
