# 文档归档规则

## 职责边界

- 本文件负责：记录型文档的编号、索引、状态目录和按年份 / 月份归档规则。
- 本文件不负责：判断一份文档语义上应该放到哪个目录；语义路由见 `document-routing-rules.md`。

## 基本原则

- 文档分成两类：长期状态文档和记录型文档。
- 长期状态文档保持稳定路径，用于描述当前需求、设计、验证、任务、知识和规则。
- 记录型文档必须带 ID，并按年份和月份归档，避免长期维护后目录平铺失控。
- 记录型文档的 ID 使用 `TYPE-YYYYMMDD-NNN`，其中 `NNN` 是同类型同日期的 3 位序号。
- 记录型文档必须进入对应索引，方便提交、回溯、发布和归档时引用。

## 长期状态文档

长期状态文档默认不使用全局记录 ID：

- `docs/workflow/00-intake/README.md`
- `docs/workflow/01-requirements/README.md`
- `docs/workflow/02-design/README.md`
- `docs/workflow/03-implementation/README.md`
- `docs/workflow/04-verification/README.md`
- `docs/workflow/05-tasks/README.md`
- `docs/knowledge/context/README.md`
- `docs/knowledge/structure/README.md`
- `docs/knowledge/behavior/README.md`
- `docs/knowledge/reference/README.md`
- `docs/rules/*.md`

如果某类长期文档持续膨胀，可以按功能模块拆分，例如：

```text
docs/knowledge/behavior/
  README.md
  auth.md
  billing.md
  notification.md
```

拆分后必须保留目录级 `README.md` 作为索引和导航。

## 记录型文档

记录型文档包括：

- `CHG`: 单次变更工作区
- `BUG`: 缺陷记录
- `ISS`: issue、风险、阻塞、技术债
- `CR`: 变更请求
- `ADR`: 架构或关键技术决策

ID 格式：

```text
TYPE-YYYYMMDD-NNN
```

示例：

```text
CHG-20260624-001
BUG-20260624-001
ISS-20260624-001
CR-20260624-001
ADR-20260624-001
```

## 归档路径

变更工作区：

```text
docs/changes/active/CHG-20260624-001-commit-rules/
docs/changes/completed/2026/06/CHG-20260624-001-commit-rules/
docs/changes/legacy/2026/06/CHG-20260624-001-commit-rules/
```

Issue、bug、风险和技术债：

```text
docs/issues/open/ISS-20260624-001-doc-numbering/
docs/issues/resolved/2026/06/ISS-20260624-001-doc-numbering/
docs/issues/legacy/2026/06/ISS-20260624-001-doc-numbering/

docs/issues/open/BUG-20260624-001-login-timeout/
docs/issues/resolved/2026/06/BUG-20260624-001-login-timeout/
```

变更请求：

```text
docs/changes/requests/open/CR-20260624-001-new-export-flow/
docs/changes/requests/resolved/2026/06/CR-20260624-001-new-export-flow/
```

ADR 默认单文件平铺；数量变多后按年份归档：

```text
docs/adr/ADR-20260624-001-doc-id-strategy.md
docs/adr/2026/ADR-20260624-001-doc-id-strategy.md
```

Release 继续使用版本号：

```text
docs/releases/v0.2.0.md
```

## 索引要求

记录型文档必须写入对应目录的 `README.md` 索引：

```text
| ID | 标题 | 状态 | 路径 | 关联文档 | 创建日期 | 更新日期 |
```

最低要求：

- `docs/changes/README.md` 索引所有 active / completed / legacy change
- `docs/issues/README.md` 索引 open / resolved / legacy issue、bug、风险和技术债
- `docs/adr/README.md` 索引所有 ADR
- `docs/releases/README.md` 索引所有 release
- `docs/archive/README.md` 索引所有废弃或迁移文档

## 提交关联

提交正文必须引用记录型文档 ID 和路径：

```text
Change: CHG-20260624-001 / docs/changes/active/CHG-20260624-001-commit-rules/
Issue: ISS-20260624-001 / docs/issues/open/ISS-20260624-001-doc-numbering/
ADR: ADR-20260624-001 / docs/adr/ADR-20260624-001-doc-id-strategy.md
```

没有记录型文档时，不要用口头描述替代；先建立记录，再提交。
