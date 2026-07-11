# 文档同步规则

## 职责边界

- 本文件负责：代码、测试、README、当前状态文档和长期知识之间的同步触发条件。
- 本文件不负责：变更工作区生命周期、文档语义路由或记录型文档归档编号；分别见 `change-management-rules.md`、`document-routing-rules.md` 和 `document-archive-rules.md`。

## 基本原则

- 代码、测试、README 和 spec 文档必须一起演进。
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
- 实现前一致性分析发现缺口：先补需求、设计、验证、任务和变更记录，再进入实现
- 实现后文档收敛发现偏差：回写真实行为、验证结果、长期知识、变更状态和记录型文档

## 审查问题

- 这次代码改动是否还能回链到原有 `FR -> DES -> TEST -> T`
- 是否产生了新的 `[待确认]` 但还没写入文档
- 是否有新规则只停留在口头说明，尚未沉淀到 `docs/rules/`
- 是否只更新了当前状态文档，却忘记同步长期知识或变更工作区
- 是否完成实现前一致性分析和实现后文档收敛
