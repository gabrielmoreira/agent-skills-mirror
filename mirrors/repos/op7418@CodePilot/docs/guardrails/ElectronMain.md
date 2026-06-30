# ElectronMain Guardrail

> **Status: Stub** — 七节模板占位。首次真实改动触发时由实施 Agent 按 [`README.md`](./README.md) 的七节模板填充。
> **为什么先读**：主进程无自动化测试覆盖（tech-debt #6）；外链拦截 / 窗口管理 / 菜单栏常驻 / better-sqlite3 ABI rebuild 全在主进程；改错会让构建产物启不来，且现有 Playwright 测试无法捕获。
> **已知关键文件**：`electron/*`（如果存在）、`scripts/build-electron.mjs`、`scripts/after-pack.js`、`scripts/after-sign.js`、`electron-builder.yml`。

## 词汇表

- `after-pack` / `after-sign` — electron-builder 的 hook，在打包 / 签名后跑。
- `better-sqlite3 ABI rebuild` — `scripts/after-pack.js` 把 native module 重编译为 Electron ABI。

## 不变量 / 契约表

| # | 不变量 | 由谁守 |
|---|--------|--------|
| 1 | better-sqlite3 必须在 after-pack 阶段重编译为 Electron ABI，否则启动崩溃 | `scripts/after-pack.js` |
| 2 | 构建前清理 `release/` + `.next/`，避免 stale artifacts 进 app.asar（v0.34 的 crash on upgrade 原因） | `scripts/build-electron.mjs` |
| 3 | （待填充——示例：外链拦截策略） | |

## 关键文件 + 责任

| 文件 | 守哪条不变量 |
|------|--------------|
| `scripts/build-electron.mjs` | esbuild + standalone 符号链接解析 + 清理 dist-electron |
| `scripts/after-pack.js` | better-sqlite3 ABI rebuild |
| `scripts/after-sign.js` | macOS 签名后处理 |
| `electron-builder.yml` | 打包配置（DMG / NSIS / arm64 + x64） |

## 改动检查表

- [ ] 改 after-pack 前在本地完整跑一次打包，确认产物可启动
- [ ] 改 native module 依赖时确认 ABI rebuild 仍工作
- [ ] 多平台改动分别在 macOS / Windows 验证（CLAUDE.md 要求）
- [ ] （待填充）

## 常见坑

- tech-debt #6 — 主进程行为无自动化覆盖；现有 Playwright 测试只覆盖 Next.js web 层。改主进程后必须手动验证。
- 历史：v0.34 crash on upgrade 根因是 `dist-electron/` 没清理就打包，stale artifacts 进 app.asar。

## 测试覆盖

| 契约 | 测试文件 |
|------|----------|
| 主进程 E2E | （tech-debt #6：待搭 `@playwright/test` + `_electron.launch()`） |

## 设计决策日志

- YYYY-MM-DD — 首次真实改动时记入第一条
