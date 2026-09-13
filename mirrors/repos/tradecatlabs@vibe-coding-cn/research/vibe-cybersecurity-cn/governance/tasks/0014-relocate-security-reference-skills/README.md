# Task Overview

- Task ID: `0014`
- Slug: `relocate-security-reference-skills`
- Objective: 将 Codex 全局 skill 根中的安全/逆向 reference-only 来源移动到本项目 `skills/reference-only/`，不扩大 active 运行面。
- Status: `Done`

## In Scope

- 移动 7 个固定来源及其项目级 source registry、逐文件 SHA-256 manifest。
- 保留 `skills/` 下现有 13 个 active skill 不变。
- 更新全局 catalog 的项目根路径校验入口与项目架构文档。
- 验证移动前后文件集合、摘要、来源和许可证元数据一致。

## Out of Scope

- 不将 reference-only 内容注册为全局或 active skill。
- 不运行上游 `SKILL.md`、脚本、安装器、hook、插件或工具命令。
- 不修改来源 commit、许可证或上游内容。
- 不执行提交、推送、reset、clean、stash 或强制 checkout。

## Requirement Alignment

- 用户要求安全/逆向上游 reference skill 不进入 Codex 全局根目录，以避免全局上下文膨胀。
- 终态是：全局仅保留轻量 catalog 与校验能力，完整参考包唯一存放于项目 `skills/reference-only/`，并继续按 reference-only 数据边界处理。

## Task Package Overview

| Node | Output | Acceptance |
|---|---|---|
| TP-01 | 迁移前置检查与路径契约 | 来源、目标、active 边界和回滚路径明确 |
| TP-02 | `skills/reference-only/` 目录移动 | 7 个来源及 metadata 到位，未覆盖 active skill |
| TP-03 | 完整性与治理验证 | catalog、manifest、边界、governance strict/health 通过 |
| TP-04 | 文档与状态收口 | 任务文档结构完整、状态为 Done、无陈旧路径 |

## Reading Order

1. `README.md`
2. `CONTEXT.md`
3. `PLAN.md`
4. `ACCEPTANCE.md`
5. `ACCEPTANCE_CHECKLIST.md`
6. `TODO.md`
7. `STATUS.md`
8. `REUSE_SAMPLING.json`

## Task Package Tree

```text
ROOT
├── TP-01 迁移前置检查与路径契约
├── TP-02 跨仓库目录移动
├── TP-03 完整性、边界与治理验证
└── TP-04 文档与状态收口
```

## Risk

`high`：跨 Git 仓库移动 5,671 个文件，涉及全局 catalog 的路径契约和项目供应链边界；回滚为将同一目录整体移回原路径，并恢复对应文本契约。
