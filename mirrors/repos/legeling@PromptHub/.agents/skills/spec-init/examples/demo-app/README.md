# demo-app

> 项目类型：web
>
> 初始化日期：2026-05-26

## 项目简介

[一句话说明这个项目帮助谁，用什么方式解决什么问题]

## 项目目标

- [目标 1]
- [目标 2]
- [目标 3]

## 开发方式

本项目采用 Spec-Driven Development (SDD) + Verification-Driven Delivery。

推荐顺序：

1. 填写 `docs/workflow/00-intake/README.md`
2. 明确 `docs/workflow/01-requirements/README.md`
3. 输出 `docs/workflow/02-design/README.md`
4. 沉淀 `docs/knowledge/` 中的长期真相
5. 拆分 `docs/workflow/03-implementation/README.md`
6. 制定 `docs/workflow/04-verification/README.md`
7. 生成 `docs/workflow/05-tasks/README.md`
8. 为本轮工作创建 `docs/changes/active/<change-key>/`
9. 阅读 `docs/rules/README.md`
10. 开始编码，并同步更新测试和文档

## 文档导航

- `docs/workflow/00-intake/README.md`: 项目背景、用户、目标、非目标
- `docs/workflow/01-requirements/README.md`: 当前交付需求，只写 what / why
- `docs/workflow/02-design/README.md`: 当前阶段设计，只写 how
- `docs/workflow/03-implementation/README.md`: 里程碑、顺序、依赖
- `docs/workflow/04-verification/README.md`: 验证策略与需求-测试映射
- `docs/workflow/05-tasks/README.md`: 可执行任务清单
- `docs/knowledge/context/README.md`: 术语、角色、实体和业务边界
- `docs/knowledge/structure/README.md`: 模块边界、系统结构、集成关系
- `docs/knowledge/behavior/README.md`: 核心流程、状态流转、规则
- `docs/knowledge/reference/README.md`: 样例、协议、schema、素材与固定参考
- `docs/issues/README.md`: 未解决问题、阻塞项、风险和技术债
- `docs/changes/README.md`: 变更层总览与归档规则
- `docs/changes/active/`: 当前进行中的 change 工作区
- `docs/releases/README.md`: 版本发布记录
- `docs/archive/README.md`: 归档和废弃文档索引
- `docs/adr/README.md`: 决策记录索引
- `docs/rules/README.md`: 编码、测试、文档同步和完成定义规则
- `docs/rules/document-routing-rules.md`: 文档语义到目录路径的映射规则
- `docs/rules/change-management-rules.md`: 变更记录与发布规则
- `docs/rules/issue-management-rules.md`: issue 跟踪与文档归档规则
- `docs/rules/clarification-rules.md`: 需求澄清与决策确认规则
- `docs/rules/bug-fix-rules.md`: bug 定位、根因修复与回归规则
- `spec-init.topology.yml`: 项目当前采用的文档拓扑与默认路由

## 追踪关系

本项目要求至少存在以下追踪链：

- `FR-*` 定义需求
- `DES-*` 定义如何满足需求
- `TEST-*` 定义如何验证需求
- `T-*` 定义实际执行任务

推荐在开始实现前，先确认至少一条完整链路：

`FR-001 -> DES-001 -> TEST-001 -> T-001`

## 目录结构

```text
.
|-- AGENTS.md
|-- README.md
|-- spec-init.topology.yml
|-- docs
|   |-- workflow
|   |   |-- 00-intake
|   |   |   `-- README.md
|   |   |-- 01-requirements
|   |   |   `-- README.md
|   |   |-- 02-design
|   |   |   `-- README.md
|   |   |-- 03-implementation
|   |   |   `-- README.md
|   |   |-- 04-verification
|   |   |   `-- README.md
|   |   `-- 05-tasks
|   |       `-- README.md
|   |-- knowledge
|   |   |-- context
|   |   |   `-- README.md
|   |   |-- structure
|   |   |   `-- README.md
|   |   |-- behavior
|   |   |   `-- README.md
|   |   `-- reference
|   |       `-- README.md
|   |-- issues
|   |   `-- README.md
|   |-- changes
|   |   |-- README.md
|   |   |-- active
|   |   |   `-- CHG-0001-template
|   |   |       |-- overview.md
|   |   |       |-- design.md
|   |   |       |-- verification.md
|   |   |       |-- tasks.md
|   |   |       `-- impact.md
|   |   |-- completed
|   |   |   `-- README.md
|   |   `-- legacy
|   |       `-- README.md
|   |-- releases
|   |   |-- README.md
|   |   `-- v0.1.0-template.md
|   |-- archive
|   |   `-- README.md
|   |-- adr
|   |   |-- README.md
|   |   `-- 0000-record-template.md
|   `-- rules
|       |-- README.md
|       |-- clarification-rules.md
|       |-- coding-standards.md
|       |-- bug-fix-rules.md
|       |-- testing-standards.md
|       |-- doc-sync-rules.md
|       |-- change-management-rules.md
|       |-- issue-management-rules.md
|       |-- document-routing-rules.md
|       `-- definition-of-done.md
|-- scripts
|   `-- .gitkeep
|-- src
|   `-- .gitkeep
`-- tests
    `-- .gitkeep
```

## 快速开始

补充项目实际命令：

```bash
# 安装依赖
[命令]

# 启动开发环境
[命令]

# 运行测试
[命令]

# 构建产物
[命令]
```

## 当前状态

- [当前进度]
- [已完成]
- [已知风险]

## 下一步

1. 完成 `docs/workflow/00-intake/README.md` 中的待确认项
2. 把关键目标转换成 `FR-*` / `NFR-*` / `AC-*`
3. 在 `docs/workflow/02-design/README.md` 中明确当前阶段设计与约定
4. 在 `docs/knowledge/` 中补齐长期稳定真相
5. 在 `docs/workflow/04-verification/README.md` 中定义首批红灯测试
6. 当引入新需求或 bugfix 时，把本轮工作拆进 `docs/changes/active/<change-key>/`
7. 当出现未解决问题或废弃文档时，维护 `docs/issues/` 和 `docs/archive/`
