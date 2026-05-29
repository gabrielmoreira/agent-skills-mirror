# demo-app Agent Rules

## Goal

先把当前交付目标、长期稳定真相、验证方式和变更工作区写清楚，再开始编码，减少返工和误解。

## Working Order

1. `docs/workflow/00-intake/README.md`
2. `docs/workflow/01-requirements/README.md`
3. `docs/workflow/02-design/README.md`
4. `docs/knowledge/context/README.md`
5. `docs/knowledge/structure/README.md`
6. `docs/knowledge/behavior/README.md`
7. `docs/knowledge/reference/README.md`
8. `docs/workflow/03-implementation/README.md`
9. `docs/workflow/04-verification/README.md`
10. `docs/workflow/05-tasks/README.md`
11. `docs/issues/README.md`
12. `docs/changes/active/<change-key>/`
13. `docs/releases/README.md`
14. `docs/archive/README.md`
15. `docs/adr/README.md`
16. `docs/rules/README.md`
17. 实现代码
18. 回写文档、测试、变更记录和 README

## Document Boundaries

| File | Focus | Do not put here |
|---|---|---|
| `docs/workflow/00-intake/README.md` | 背景、用户、目标、非目标、约束 | 具体技术方案 |
| `docs/workflow/01-requirements/README.md` | what / why / success | 框架、库、表名、接口实现 |
| `docs/workflow/02-design/README.md` | how / architecture / current-stage decisions | 执行顺序和碎任务 |
| `docs/knowledge/context/README.md` | 术语、角色、核心实体、长期业务边界 | 本轮临时任务 |
| `docs/knowledge/structure/README.md` | 模块边界、系统结构、集成关系 | 具体交付排期 |
| `docs/knowledge/behavior/README.md` | 关键流程、状态流转、业务规则 | 低层实现细节 |
| `docs/knowledge/reference/README.md` | 样例、协议、schema、素材和固定参考 | 临时讨论记录 |
| `docs/workflow/03-implementation/README.md` | 里程碑、依赖、交付顺序 | 细碎的底层实现细节 |
| `docs/workflow/04-verification/README.md` | 如何验证需求落地 | 只有“后面补测试”这种空话 |
| `docs/workflow/05-tasks/README.md` | 可执行动作 | 抽象愿景和泛泛而谈 |
| `docs/changes/active/<change-key>/` | 单次变更的工作区和影响分析 | 项目长期稳定真相 |
| `docs/rules/` | 项目级规范与完成定义 | 具体业务需求细节 |

## Delivery Rules

- 存在阻塞性的 `[待确认]` 时，不要开始大规模实现。
- 对需求边界、架构方向、技术栈、数据模型或覆盖策略存在关键疑点时，必须先向用户确认，不能自行定案。
- 新功能必须同步更新 workflow、knowledge、verification 和 tasks 中受影响的部分。
- 新接口、数据结构、配置项变化，必须同时更新设计文档、知识层文档和测试。
- 修 bug 必须补回归测试，并记录进当前变更工作区。
- 新需求、bugfix、重构或流程变化，应同步更新 `docs/changes/active/` 或其归档位置。
- 版本发布或对外交付变化，应同步更新 `docs/releases/`。
- 未解决问题、风险和技术债，应同步更新 `docs/issues/`。
- 被替代或废弃的文档，应同步归档到 `docs/archive/`。
- 目录结构变化必须更新 `README.md`、`spec-init.topology.yml` 和 `docs/rules/document-routing-rules.md`。
- 关键技术权衡写入 `docs/adr/`。
- 每个任务都应该关联 `FR-*`、`DES-*`、`TEST-*` ID。
- 不确定的信息要显式标成 `[待确认]`，不要编造。
- 开始编码前，至少保证一条完整追踪链已经存在：`FR -> DES -> TEST -> T`
- 具体编码、测试和文档同步规范，优先遵循 `docs/rules/` 下的规则文件。

## Project Commands

根据实际技术栈补充：

- Install: `[命令]`
- Dev: `[命令]`
- Test: `[命令]`
- Build: `[命令]`
- Lint: `[命令]`

## Definition of Done

- 需求、设计、验证、任务之间存在可追踪关系。
- 长期稳定事实已沉淀到 `docs/knowledge/`。
- 当前 change 已记录在 `docs/changes/active/`、`completed/` 或 `legacy/` 中的正确位置。
- 代码与文档保持一致。
- 高优先级需求有自动化验证。
- README 能帮助新成员快速理解项目结构。
- 已知风险和取舍已记录到文档或 ADR。
- `docs/rules/definition-of-done.md` 中的检查项通过。
