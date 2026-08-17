# 文档约定

本目录包含用户文档、开发规范、决策记录和 changelog。根文件 `../AGENTS.md` 的系统不变量仍然适用。

## 一个事实一个 Owner

- 当前系统边界和主链路属于根 `ARCHITECTURE.md`。
- 用户行为、配置和操作方法属于对应 `docs/` 页面。
- 测试层级与命令属于 `develop-guides/testing-guidelines.md`。
- 非平凡变更从提案到证据收敛的流程属于 `develop-guides/spec-loop.md`。
- 当前决定、替代方案、后果和验证属于 `develop-guides/decisions/`。
- 工程主张由最接近行为的代码、数据约束、契约和测试共同拥有；`develop-guides/engineering-trust.md` 只说明闭环规则，verifier 报告只是按需派生的审计投影。
- 事故因果、漏网机制和 guardrail 属于满足 `develop-guides/postmortems/README.md` 门槛的 postmortem；不要混入普通 changelog。
- `docs/vibe/` 是被忽略的临时计划，不是当前权威，也不保存唯一的设计理由。

## 写作与维护

- 正式文档描述当前行为，不把 PR 过程、实现步骤和旧计划混在当前契约中。
- 代码、配置、API 或命令变化时同步更新 owning page；其他页面只链接，不复制完整规则。
- 新增正式页面时更新 `.vitepress/config.mts` 导航并运行 docs build。
- 用户可见完成项更新 `develop-guides/changelog.md`；未完成事项属于 roadmap，二者不能同时声明同一状态。
- 决策记录遵循 [decisions/README.md](develop-guides/decisions/README.md) 的 lifecycle 和格式；implemented 记录描述当前问题、决定和验证，不用“计划、待办、应当”等提案口吻。

```bash
python3 scripts/verify_engineering_contracts.py
cd docs && pnpm run build
```
