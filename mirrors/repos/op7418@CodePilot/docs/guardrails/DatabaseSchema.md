# DatabaseSchema Guardrail

> **Status: Stub** — 七节模板占位。首次真实改动触发时由实施 Agent 按 [`README.md`](./README.md) 的七节模板填充。
> **为什么先读**：用户真实数据在 `~/.codepilot/codepilot.db`；schema 迁移**必须 backfill，不能 DELETE 用户数据**（`feedback_db_migration_safety.md`）。一次错误的 migration 可能让用户丢失所有历史会话 / Provider 配置。
> **已知关键文件**：`src/lib/db.ts`（schema + migration runner）；`src/types/index.ts`（DB 行类型）。

## 词汇表

（待填充）

## 不变量 / 契约表

| # | 不变量 | 由谁守 |
|---|--------|--------|
| 1 | Migration 必须保留所有用户数据（backfill 而不是 DELETE）；新增字段用默认值填，不要求用户手动迁移 | `src/lib/db.ts` migration 函数 |
| 2 | （待填充——示例：每个 migration 必须可重入；执行多次结果相同） | |

## 关键文件 + 责任

| 文件 | 守哪条不变量 |
|------|--------------|
| `src/lib/db.ts` | schema 定义 + migration runner + better-sqlite3 句柄管理 |
| `src/types/index.ts` | DB 行类型与运行时形状一致 |

## 改动检查表

- [ ] 加新列时填默认值不要让历史行变 NULL
- [ ] 加新表时考虑用户已有的同名表冲突（不应该发生但要兜底）
- [ ] 改字段类型时必须有显式 migration step，不能依赖 SQLite 隐式 coerce
- [ ] 删字段 / 删表前先确认无用户数据依赖
- [ ] （待填充）

## 常见坑

- 跨 Worktree / 多进程共用同一份 DB 文件时会抢 SQLite 锁（Phase 5b round 6 的 30 分钟卡死事件根因）。测试要用 `CODEX_DISABLED=1` 隔离。
- tech-debt #7 — `claude-settings-credentials.test.ts` 和 `project-mcp-injection.test.ts` 的 DB-related test 在 CI 上 skip，本地通过；疑似 tsx + node 20 ESM module identity 去重在 linux 行为差异。

## 测试覆盖

| 契约 | 测试文件 |
|------|----------|
| | （待填充） |

## 设计决策日志

- YYYY-MM-DD — 首次真实改动时记入第一条
