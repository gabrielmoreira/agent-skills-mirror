# Documentation Sync Rules

## 基本原则

- 代码、测试、README 和 SDD 文档必须一起演进。
- 文档不是发布后补写的说明书，而是实现前后的工作约束。

## 同步要求

- 需求变化：更新 `docs/workflow/01-requirements/README.md`
- 设计变化：更新 `docs/workflow/02-design/README.md`
- 长期稳定业务或结构变化：更新 `docs/knowledge/`
- 交付顺序变化：更新 `docs/workflow/03-implementation/README.md`
- 测试策略变化：更新 `docs/workflow/04-verification/README.md`
- 任务拆解变化：更新 `docs/workflow/05-tasks/README.md`
- 新需求、bugfix、重构变化：更新 `docs/changes/active/` 或对应归档位置
- 版本发布变化：更新 `docs/releases/`
- 项目结构变化：更新 `README.md` 和必要的规则文档

## 审查问题

- 这次代码改动是否还能回链到原有 `FR -> DES -> TEST -> T`
- 是否产生了新的 `[待确认]` 但还没写入文档
- 是否有新规则只停留在口头说明，尚未沉淀到 `docs/rules/`
- 是否只更新了 workflow，却忘记同步 knowledge 或 change workspace
