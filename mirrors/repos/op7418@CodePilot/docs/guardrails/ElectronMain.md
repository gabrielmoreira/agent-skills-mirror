# ElectronMain Guardrail

> **Status: Active contract** — 覆盖主窗口安全与原生菜单、Electron 构建清理、standalone 内容边界、extraResources 互斥、native ABI 与 packaged server 启动门禁。
> **为什么先读**：主进程缺少完整 UI 自动化覆盖（tech-debt #6）；外链拦截、窗口管理、原生编辑菜单、better-sqlite3 ABI rebuild 和 packaged server 都在此边界，改错会让安全策略或发布产物失效。
> **已知关键文件**：`electron/*`、`scripts/build-electron.mjs`、`scripts/after-pack.js`、`scripts/after-sign.js`、`electron-builder.yml`。

## 词汇表

- **Main Process**：`electron/main.ts` 及其导入模块，拥有系统 API 和窗口生命周期。
- **Renderer**：Next.js 页面；不得直接获得 Node / Electron 主进程能力。
- **standalone**：Next.js `output: standalone` 产物，packaged server 的运行根。
- **packaged server smoke**：用产物内 Electron runtime 启动 `standalone/server.js` 并请求 `/api/health`。
- **FileSet destination**：electron-builder 把源文件复制到 `resources/` 下的目标路径；目标不得重叠。
- **native editing context menu**：主进程通过 Electron `role` 为 input / textarea / contenteditable 提供复制、粘贴等系统编辑动作。

## 不变量 / 契约表

| # | 不变量 | 由谁守 |
|---|---|---|
| 1 | better-sqlite3 必须在 after-pack 阶段重编译为 Electron ABI | `scripts/after-pack.js` |
| 2 | 构建前只清理 `release/` + `.next/` + `dist-electron/`，且先验证当前目录确为 CodePilot 项目 | `scripts/clean-electron-build.mjs` |
| 3 | standalone 根目录只允许 `.next`、`node_modules`、`server.js`、`package.json`、`cache-handler.js`；本地 DB、uploads、Git/agent/worktree 状态不得入包 | build scripts |
| 4 | `extraResources` 中 standalone root、`node_modules`、`.next` 的目标互斥；禁止 `**/*` 再叠加子目录 FileSet | `electron-builder.yml` + tests |
| 5 | macOS/Windows 产物必须校验版本、native ABI 与 packaged server health 后才能上传 | build workflow |
| 6 | 主窗口外部导航必须经过 `classifyNavigation`；非 http/https 协议不得交给系统 shell | `electron/main.ts` + tests |
| 7 | Renderer 的 input / textarea / contenteditable 使用 Electron role 菜单；密码框不得启用复制、剪切 | `attachRendererEditingContextMenu` |
| 8 | xAI browser OAuth callback 固定为 `127.0.0.1:56121/callback` 且只绑定 loopback | OAuth manager |
| 9 | packaged 无法打开浏览器或端口被占用时必须明确提示 device-code 登录 | Settings UI + routes |
| 10 | packaged Next server 的 xAI OAuth fetch 必须显式消费代理 dispatcher，不能假设 Node fetch 自动读取 env | `electron/main.ts` + env proxy fetch |
| 11 | Electron → packaged Next child env 保留显式 proxy、缺省时补 system proxy，并合并 loopback `NO_PROXY`；Windows 不得传大小写重复 key | process proxy env |
| 12 | bundled Codex 的 Windows system-proxy-only 路径必须以 packaged smoke 证明；静态 source pin 不能替代 | Windows release smoke |
| 13 | macOS 原生窗口材质必须跟随 app 的 `system/light/dark` 模式；IPC 只接受这三个枚举，renderer 外围保持透明，不能用高不透明度 CSS 遮罩伪造主题同步 | `ThemeProvider` + preload/main bridge + tests |
| 14 | macOS 整窗默认材质为 `under-window`；比较其他材质时用 `ELECTRON_VIBRANCY` 诊断开关，不能靠恢复高不透明 tint 调整磨砂强度 | `electron/main.ts` + `platform-marker` source-pin |

## 关键文件 + 责任

| 文件 | 责任 |
|---|---|
| `electron/main.ts` | 主窗口生命周期、导航拦截、原生编辑右键、托盘与系统集成 |
| `scripts/clean-electron-build.mjs` | 清理边界与 standalone allowlist |
| `scripts/build-electron.mjs` | Next standalone 复制与脱敏 |
| `scripts/after-pack.js` | better-sqlite3 ABI rebuild |
| `scripts/after-sign.js` | macOS 签名后处理 |
| `electron-builder.yml` | DMG / NSIS / arm64 + x64 打包配置 |
| `electron/preload.ts` + `src/components/layout/ThemeProvider.tsx` | app 主题到 `nativeTheme.themeSource` 的窄 IPC 桥 |
| `src/lib/xai-oauth-manager.ts` | loopback server 生命周期与端口策略 |
| `src/lib/env-proxy-fetch.ts` | packaged server 上游 HTTP(S) system-proxy bridge |
| `src/lib/process-proxy-env.ts` | child-process proxy 优先级、Windows key 归一与 bypass |

## 改动检查表

- [ ] 改 `BrowserWindow` / `webContents` 事件时运行 `electron-main-security` 与 `workspace-context-menus`
- [ ] 编辑右键菜单保持 Electron `role` 实现，避免硬编码快捷键或绕过密码保护
- [ ] 改 after-pack / native module 后完整打包并确认产物可启动
- [ ] 修改 `extraResources` 时检查所有 FileSet destination 不重叠
- [ ] 修改 standalone 资源时确认 `.next/node_modules` 的 Next.js 哈希 external alias 被显式打包
- [ ] 运行 `scripts/verify-packaged-server.mjs`，确认产物 `/api/health`
- [ ] 审计 packaged standalone 不含 DB、uploads、`.codepilot`、`.claude`、`.git` 或嵌套 release
- [ ] OAuth/代理改动在 macOS 与 Windows 分别验证 browser/device/cancel/端口占用和外网代理
- [ ] 改 macOS vibrancy / theme bridge 时运行 `native-theme-sync` 与 `platform-marker`，并在真实 Electron 窗口分别切换浅色、深色；两种模式的 body/window surface 都保持 transparent

## 常见坑

- tech-debt #6 — 现有 Playwright 主要覆盖 web 层，主进程变更仍需 packaged 人工验证。
- Electron 不自动给 renderer 输入框提供复制/粘贴菜单；逐组件实现会漏掉 CodeMirror / contenteditable。
- `context-menu.selectionText` 不能作为密码字段可复制依据；还要检查 `inputFieldType` 与 `editFlags`。
- v0.34 crash on upgrade 根因是 `dist-electron/` 未清理，stale artifacts 进入 app.asar。
- v0.58.2 Windows 构建暴露重叠 FileSet 的 `EBUSY`；资源组目标必须互斥。
- v0.58.3 `.next/node_modules` 被过滤导致 packaged server 无法启动；哈希 alias 必须独立复制并真实启动验证。
- OAuth loopback 在 web/dev 通过不代表 packaged 可用。
- Windows env key 是大小写不敏感语义；禁止用对象 spread 顺序决定 proxy。
- 不要用 `session.setProxy({ mode: 'direct' })` 解决 Codex loopback；它会关闭 Chromium 外网代理且管不到 app-server。
- `scripts/after-pack.js` 会把工作区 better-sqlite3 重编成 Electron ABI；之后跑 Node/Next 前需 `npm rebuild better-sqlite3` 恢复 Node ABI。

## 测试覆盖

| 契约 | 测试文件 |
|---|---|
| 主进程 E2E | tech-debt #6：待搭 `@playwright/test` + `_electron.launch()` |
| 外部导航与 export 边界 | `src/__tests__/unit/electron-main-security.test.ts` |
| 原生输入框编辑右键结构 | `src/__tests__/unit/workspace-context-menus.test.ts` |
| 清理、standalone allowlist、extraResources 互斥 | `src/__tests__/unit/electron-packaging-hygiene.test.ts` |
| packaged version + native ABI + server health | `scripts/verify-packaged-server.mjs`, build workflow |
| xAI loopback / proxy / child env | 对应 xAI、env-proxy、process-proxy 单测 + packaged smoke |
| 原生主题枚举、preload/main bridge、透明 surface | `src/__tests__/unit/native-theme-sync.test.ts` + `platform-marker.test.ts` |

## 设计决策日志

- 2026-07-20 — standalone 最小 root allowlist，并在打包边界 sanitize + fail-closed。
- 2026-07-20 — Windows 重叠 FileSet 改为互斥资源组；packaged server health 升为发布门禁。
- 2026-07-21 — xAI OAuth 采用固定 loopback browser PKCE + device-code 双路径。
- 2026-07-27 — Electron child env 改为显式 proxy 优先 + system fallback + loopback bypass。
- 2026-07-29 — 输入框右键统一放在主进程 `webContents.context-menu`，业务对象右键仍由 Renderer 负责。
- 2026-07-30 — 用户否决用 82% window / 88% sidebar renderer tint 解决深色可读性：它会遮住浅/深两种模式的原生磨砂。改为 app mode 经窄 IPC 同步 `nativeTheme.themeSource`，外围透明、侧栏只保留 40% tint；见 `569b117d`。
- 2026-07-30 — Electron 没有可调的 vibrancy blur radius；用户反馈 `menu` 过糊后，以隔离 Electron 窗口对比材质并将默认值改为轮廓更清楚的 `under-window`，保留透明 backing 与环境变量诊断矩阵；见 `83e041cd`。
