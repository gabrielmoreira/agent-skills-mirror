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
- **native delivery owner**：始终由 Electron Main 领取 `electron-native` delivery；窗口可见性不会把 ownership 转给 Renderer。
- **OS accepted**：Electron `Notification` 发出 `show` lifecycle event。它证明系统接受展示请求，不等于用户看见或已读。
- **server recovery safe mode**：Electron Main 在 packaged Next utility 意外退出后持有的跨 generation 状态；通过只读 child env 注入，Renderer 无权自行清除。
- **descendant registry**：当前 utility generation 通过窄 lifecycle channel 登记其直接 child 的 role、PID、start identity、可执行文件 basename 与后代可验证性；Main 只用它决定能否重启，不凭不完整身份杀进程。

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
| 15 | HTML 缩略图 IPC 只接受当前 renderer 同源、无 interactive 参数且首段为一个完整 canonical `ws.<base64url absolute path>` 的 strict preview URL。派生后的精确 scope 才能进入 `webRequest` allowlist；包含性 token、前后缀和编码分隔符都 fail closed | `electron/html-thumbnail-security.ts` + main IPC |
| 16 | AI 输出的本地路径不得进入通用 `shell.openPath`。`/api/files/inspect` 只接受绝对路径 + `sessionId` 或固定 `home` scope，由服务端推导根并返回 canonical `realPath`；主进程在 OS 调用前再次 realpath/stat。目录只能 `showItemInFolder`，bundle 目录拒绝；文件只允许 workspace `.html/.htm` 走专用 open IPC | `local-path-security` + DevOutput / PreviewPanel / DiffSummary + inspect route + main IPC |
| 17 | `/api/files/open` fallback 不得拼 shell 字符串；可执行文件固定、路径只能作为单个 argv，`shell: false`，且 scope/realpath/bundle 规则与主进程一致 | files/open route + tests |
| 18 | 默认助理路径 IPC 无输入，只返回 `path.join(app.getPath('documents'), 'CodePilot', 'Assistant')`；不得演变成 Renderer 可控的通用路径 resolver | `default-assistant-home.ts` + main/preload |
| 19 | `electron-native` 只有 Main 一个 consumer，visible/hidden/tray 不切 owner；Renderer 只能 claim `renderer-toast` | native delivery service + route policy |
| 20 | native delivery 只有收到 `show` event 才 ack delivered；共同 throw/unsupported/timeout 收口 error，Windows 额外监听 `failed`，macOS/Linux 不等待不存在的事件 | `notification-lifecycle.ts` |
| 21 | 提示音服从系统 policy：macOS 使用 `sound:'default'` 且 `silent:false`，Windows/Linux 使用平台默认且不自播放音频；最终能力必须由对应 packaged smoke 证明 | native options builder + release smoke |
| 22 | 已 show 的 Notification 对象在 click/close 前由有界 retention 保活；点击在 Renderer ready 前进入有界队列，ready handshake 后按 event id 幂等投递。action 只能解析为应用内 route 或已验证的 task/session fallback | `notification-lifecycle.ts` + `notification-click-queue.ts` + main/preload/hooks |
| 23 | native delivery 的 stale claim lease 必须长于单次通知 lifecycle timeout，并保留可观测余量；调整 show timeout 时必须同步复核 lease，避免仍在等待系统回调的 delivery 被第二个 consumer 重新领取 | notification claim policy + native delivery service |
| 24 | 浏览器可触发的 HTML preview URL 只接受本机 POSIX 或 Windows drive 路径；UNC、SMB 与 Windows device namespace 必须在任何 `stat/realpath/readFile` 前拒绝，避免任意网页通过 loopback GET 诱发网络认证出站 | `html-preview-url.ts` + preview route |
| 25 | macOS 默认钥匙串缺失/未配置时，不得直接进入 Claude Code 的凭据 item 探测或 Electron `safeStorage`，避免系统 modal 阻塞会话。探测只能读取 default-keychain 配置与文件存在性；仅在确认不可用时给 Claude subprocess 前置窄 `security` shim，且只拒绝 `Claude Code*` service 与无参数 `show-keychain-info`，其他 argv 必须原样转发 `/usr/bin/security` | `macos-keychain-guard.ts` + packaged shim + Main/SDK env |
| 26 | 所有 `shell.openExternal` 返回的 Promise 必须由同一个边界消费。失败时只记稳定 reason code，不得记录 URL/query 或原始 OS 文本；用户必须收到按系统 locale 选择的默认浏览器修复提示，提示本身失败也不得产生 unhandled rejection | `external-navigation.ts` + `electron/main.ts` |
| 27 | packaged Next utility 的 unexpected exit 必须立即暂停 native poll，并切到不依赖 Next 的本地恢复页；intentional quit 不得触发恢复 | `server-supervisor.ts` + `electron/main.ts` |
| 28 | 自动恢复固定使用原 stable port，按 1s/2s/4s 退避，10 分钟最多 3 次；`/api/health` 成功前不得 reload route 或恢复 poll，持续健康 60s 才重置预算 | supervisor + Main |
| 29 | recovery safe mode 只由 Main 持有并经 `CODEPILOT_RECOVERY_SAFE_MODE` 注入。safe child 不得启动 Codex app-server 或 scheduler；Codex Runtime composer 必须显示原因并禁用发送 | Main + instrumentation + Runtime UI |
| 30 | descendant lifecycle 消息只接受当前 utility generation，register/unregister 必须精确匹配 PID + start identity + role + basename。live、PID 复用或更深树不可验证时 fail-closed 停在错误页；不得仅凭 PID/basename自动 kill | lifecycle contract + registry |
| 31 | Utility fatal report 原文不得写日志或复制诊断；只允许 reason、退出码、heap/RSS/private/host memory 等纯数值。恢复页 IPC 只接受当前 data: recovery renderer | Main + preload + recovery tests |
| 32 | blocked（ownership 不可证明）状态**不得提供任何可成功调用的 relaunch 入口**：descendant registry 是 per-Main 内存态，relaunch 后为空，会绕过 single-owner 门禁。blocked 页只渲染「退出应用」；Main restart handler 必须显式拒绝 blocked，quit handler 必须反向限定只接受 blocked，source-pin 断言状态门禁位于 `app.relaunch()` 前。给 blocked 加回自动/一键重开前必须先落地跨 relaunch 的持久化 registry 重验证（tech-debt #85） | `server-recovery-page.ts` + Main IPC + recovery tests |
| 33 | packaged Next utility 的运行期 fatal/error/unexpected exit 在 stable opt-in telemetry 中每个 generation 最多捕获一次；只传稳定枚举、平台定义的有界整数退出码与 utility/host memory 数值。负 POSIX/launch-failure sentinel 不得被当作无效内存指标丢弃；Electron diagnostic report 原文必须在 Main 边界丢弃，不得进入日志、Sentry 或恢复页 | `utility-process-failure.ts` + Main + telemetry/recovery tests |
| 34 | stable/preview macOS distributable 必须是 Developer ID Application 签名且 `TeamIdentifier` 精确匹配发布配置；证书打包步骤使用 `CSC_LINK` 时必须允许 electron-builder 发现并选择导入的身份，除非同时配置了显式 identity。缺证书、ad-hoc、Team ID 不一致、最终 bundle deep/strict 失败都必须阻断上传。最终 `codesign` inspect/deep verify 自身必须有进程级硬超时，不能只依赖 CI step timeout；ad-hoc 只允许显式本地包，不能作为发布证据 | `after-sign.js` + `verify-macos-developer-id.mjs` + workflows |
| 35 | packaged recovery smoke 跳过 provider Safe Storage 只允许 exact flag + packaged app + canonical realpath 位于 `os.tmpdir()/codepilot-packaged-recovery-*`；flag 不得传给 Next/Agent child。真实 userData、dev mode、symlink/不存在路径和近似 flag 全部 fail closed | `provider-secret-startup-policy.ts` + Main + recovery smoke/tests |

## 关键文件 + 责任

| 文件 | 责任 |
|---|---|
| `electron/main.ts` | 主窗口生命周期、导航拦截、原生编辑右键、托盘与系统集成 |
| `electron/html-thumbnail-security.ts` | HTML 缩略图 strict URL 解析、精确 request scope 与串行 deadline |
| `scripts/clean-electron-build.mjs` | 清理边界与 standalone allowlist |
| `scripts/build-electron.mjs` | Next standalone 复制与脱敏 |
| `scripts/after-pack.js` | better-sqlite3 ABI rebuild |
| `scripts/after-sign.js` | macOS 签名后处理 |
| `electron-builder.yml` | DMG / NSIS / arm64 + x64 打包配置 |
| `electron/preload.ts` + `src/components/layout/ThemeProvider.tsx` | app 主题到 `nativeTheme.themeSource` 的窄 IPC 桥 |
| `src/lib/xai-oauth-manager.ts` | loopback server 生命周期与端口策略 |
| `src/lib/env-proxy-fetch.ts` | packaged server 上游 HTTP(S) system-proxy bridge |
| `src/lib/process-proxy-env.ts` | child-process proxy 优先级、Windows key 归一与 bypass |
| `src/lib/local-path-security.ts` | 主进程/Next fallback 共用的绝对路径、bundle、HTML 扩展与固定 argv 策略 |
| `src/lib/local-path-navigation.ts` + `/api/files/inspect` | Renderer 本地路径 file/directory 分流；服务端从 session/home 推导 scope 并返回 canonical `realPath` |
| `electron/default-assistant-home.ts` | 默认助理 Documents 路径的无副作用纯解析 |
| `electron/notification-lifecycle.ts` | 平台 notification options 与 show/error/timeout 终态 |
| `electron/notification-click-queue.ts` | 点击 action 校验、有界 pending queue 与 event-id 去重 |
| `electron/external-navigation.ts` | HTTP(S) system-browser Promise 所有权、本地化失败提示与隐私边界 |
| `electron/server-supervisor.ts` | crash window、有限 backoff、safe-mode ownership 与健康重置 |
| `electron/server-descendant-registry.ts` + `src/lib/server-lifecycle-contract.ts` | generation/identity 校验与 single-owner restart gate |
| `electron/server-recovery-page.ts` | 不依赖 Next 的本地化错误面与 CSP |
| `src/lib/macos-keychain-guard.ts` + `resources/macos-keychain-guard/security` | default-keychain 只读探测、Claude credential 非交互降级与 packaged shim |

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
- [ ] 改 HTML thumbnail IPC/preview route 时运行 `electron-main-security`，覆盖 canonical token、包含性 token、编码分隔符、同源 scope、超时释放与外部请求拒绝
- [ ] 改聊天本地链接或系统路径消费方时覆盖：HTTP(S)、相对路径、工作区文件/目录、外部确认、symlink escape、`.app/.workflow` bundle、`.command` 非 HTML 与 Electron 错误字符串
- [ ] Renderer 不得新增通用 `openPath(path)` bridge；目录意图使用 scoped `revealPath`，HTML 使用 scoped `openHtmlFile`
- [ ] 改 native notification 时验证 Main 单 owner、visible/hidden 不切 owner、server restart stale claim 可恢复
- [ ] 文案把 delivered 描述为“系统已接受”，不写“用户已读”
- [ ] notification click 覆盖 before-ready、reload 和 duplicate event；队列必须有上限
- [ ] 已 show notification 的 JS 对象在 click/close/TTL 前保持引用，retention 必须有数量与时间上限
- [ ] 调整 native notification lifecycle timeout 时同步核对 stale claim lease；当前 12s timeout / 30s lease 不得被改成 timeout ≥ lease
- [ ] 默认助理 fixed-path IPC 保持无参数，路径 fixture 覆盖 macOS/Windows/Linux 分隔符
- [ ] HTML preview wire 变更覆盖 forged workspace token 与 Windows root token；`\\server\share`、`//server/share`（Windows）和 `\\?\` 必须在文件 I/O 前 fail closed
- [ ] 改 macOS 凭据启动链时覆盖：健康 default keychain 不改 PATH；缺失/未配置时不调用 `safeStorage`；shim 只拦 `Claude Code*` credential service、其余命令固定 `exec /usr/bin/security "$@"`；不得用 `password-store=basic` 或 `CLAUDE_CODE_SIMPLE` 扩大降级面
- [ ] 改 macOS 打包签名时验证最终 `.app` 的 Developer ID + exact Team ID + deep/strict；`CSC_LINK` 证书步骤不得在未配置显式 identity 时关闭 `CSC_IDENTITY_AUTO_DISCOVERY`；不得用 afterSign 中间态或 ad-hoc 包冒充正式发布证据
- [ ] 最终 artifact verifier 的每次 `codesign` 调用都有显式 timeout + kill signal；超时必须 fail closed，不能进入 checksum/upload
- [ ] recovery smoke 的 Safe Storage bypass 必须保留 packaged + canonical temp userData 双门禁，并覆盖 symlink/真实 userData 反例；flag 不得进入 child env
- [ ] 改外链导航时两个入口（`setWindowOpenHandler` / `will-navigate`）都走 `openExternalSafely`；拒绝 Promise 与失败 dialog 自身拒绝均必须被消费，日志/提示不得回显目标 URL 或 OS error。
- [ ] 改 packaged server lifecycle 时覆盖 intentional quit、单次/连续 crash、health-before-reload、poll pause/resume、stable port、safe-mode env 与 descendant fail-closed。
- [ ] 运行期 crash recovery 的发布证据必须来自 packaged app；Node source-pin/单测只能证明状态机和接线，不能标 `Smoke passed`。

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
- 不要用 `pathname.startsWith('/api/files/html-preview/ws.')` 代替 workspace token parser；前缀命中不是完整 segment，也不能证明 canonical base64url 或绝对 workspace root。
- 不要根据 `mainWindow.isVisible()` 在 Renderer 和 Main 间切换 native consumer；切换窗口会产生重复或漏投。
- 不要在调用 `notification.show()` 后立刻写 delivered；生命周期终态来自 `show` event，且需要有界 timeout。
- 不要只调大 native notification 的 show timeout；它必须始终短于 stale claim lease，否则同一 delivery 可能在首次消费尚未结束时被再次领取。
- 不要只依赖 CI job/step timeout 兜底 `codesign`；final artifact verifier 应在命令边界终止卡死进程并返回非零。
- 不要用 Web Notification 或 renderer toast 作为 packaged Electron native notification 的成功证据。
- 不要在 utility `exit` 后直接 `startServer()`：先停 poll、核对 generation registry，再走 bounded supervisor。无法证明孙进程已退出时宁可停在错误页。
- 不要记录 Electron UtilityProcess diagnostic report 原文；它可能含 argv、环境和绝对路径。

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
| HTML thumbnail canonical scope、外联阻断与 deadline queue | `src/__tests__/unit/electron-main-security.test.ts` |
| 聊天本地路径分类、canonical inspect、bundle/协议拦截与窄系统能力 | `local-link-detector.test.ts` + `local-path-navigation.test.ts` + `markdown-contract.test.ts` + `electron-main-security.test.ts` + `asset-library-ui.test.ts` |
| 默认助理 fixed-path、native lifecycle、点击队列与 Main 单 owner | `default-assistant-bootstrap.test.ts` + `electron-notification-lifecycle.test.ts` + `bg-poller-channel-parity.test.ts` + `bridge-delivery-visibility.test.ts` |
| HTML preview 本机路径限制、UNC/device token 拒绝 | `html-preview-url.test.ts` + `html-preview-route.test.ts` |
| macOS default-keychain 探测、Claude credential shim、safeStorage 前置门禁、packaged resource | `macos-keychain-guard.test.ts` + `provider-secret-electron-contract.test.ts` + `electron-packaging-hygiene.test.ts` |
| 外链默认应用失败、反馈失败与隐私日志边界 | `electron-external-navigation.test.ts` + `electron-main-security.test.ts` |
| utility supervisor、offline page、safe mode、descendant identity、poll/reload 顺序 | `electron-server-recovery.test.ts` + `scripts/smoke-packaged-server-recovery.mjs` |

## 设计决策日志

- 2026-07-20 — standalone 最小 root allowlist，并在打包边界 sanitize + fail-closed。
- 2026-08-07 — Windows 0.64 真实 `shell.openExternal` association failure 被全局 unhandled-rejection 捕获；两个外链入口统一进入可测试 Promise owner，失败给本地化默认浏览器提示且不记录动态 URL/系统正文。
- 2026-07-20 — Windows 重叠 FileSet 改为互斥资源组；packaged server health 升为发布门禁。
- 2026-07-21 — xAI OAuth 采用固定 loopback browser PKCE + device-code 双路径。
- 2026-07-27 — Electron child env 改为显式 proxy 优先 + system fallback + loopback bypass。
- 2026-07-29 — 输入框右键统一放在主进程 `webContents.context-menu`，业务对象右键仍由 Renderer 负责。
- 2026-07-30 — 用户否决用 82% window / 88% sidebar renderer tint 解决深色可读性：它会遮住浅/深两种模式的原生磨砂。改为 app mode 经窄 IPC 同步 `nativeTheme.themeSource`，外围透明、侧栏只保留 40% tint；见 `569b117d`。
- 2026-07-30 — Electron 没有可调的 vibrancy blur radius；用户反馈 `menu` 过糊后，以隔离 Electron 窗口对比材质并将默认值改为轮廓更清楚的 `under-window`，保留透明 backing 与环境变量诊断矩阵；见 `83e041cd`。
- 2026-07-31 — HTML thumbnail IPC 的初始 URL gate 从字符串前缀升级为 canonical workspace-segment parser。只有完整 `ws.<base64url absolute path>` 可派生 request scope；非法/包含性/编码分隔符输入在创建隐藏窗口前拒绝。
- 2026-07-31 — Codex Markdown 本地目录不再按“绝对路径 = 文件”送入 PreviewPanel。用户点击后由 scoped inspect 判型：文件进侧栏、目录进系统文件管理器；工作区外仍先确认。HTML DiffSummary 卡新增 workspace-only 系统浏览器图标。
- 2026-08-01 — Claude 复审发现目录 `shell.openPath` 可启动 macOS bundle、generic IPC 可被 AI 路径利用且 inspect/raw path 不同源。删除通用 bridge：目录只定位、bundle 拒绝、HTML 专用打开；inspect 根由 session/home 推导并返回 canonical path，主进程二次校验。既有 files/open shell 拼接同步改为固定 argv。
- 2026-08-03 — 默认助理路径改为无输入的 fixed-path IPC；native notification 改为 Main 单 owner 的 durable claim/ack。`show` 只表示 OS accepted，点击通过有界 pending queue 等待 Renderer ready，提示音服从系统设置且仍以各平台 packaged smoke 为发布证据。
- 2026-08-07 — 独立安全审查确认 preview token 能表达 UNC/device root，跨站页面虽读不到响应仍可诱发 loopback 文件探测与 SMB/NTLM 出站。Preview wire 收紧为 local-only；UNC workspace 的 HTML 预览暂不支持，普通文件能力不受影响。
- 2026-08-07 — B-018 再次收到真实截图后推翻旧 Chromium 归因：当前 Claude CLI 会在每个 subprocess 启动时用用户名探测 `Claude Code*` Keychain item，且 v0.65+ Electron 还会初始化 `safeStorage`。采用 default-keychain 配置的只读前置探测；确认缺失时跳过 safeStorage，并用 packaged 窄 shim 让 Claude 走既有回退。拒绝 `password-store=basic`（macOS 无效且会误导安全边界）和 `CLAUDE_CODE_SIMPLE`（会关闭正常 hooks/插件/项目指令能力）。
- 2026-08-11 — Next utility OOM containment 改为 Main-owned safe mode + 本地 recovery page + bounded supervisor。自动重启受 production descendant registry 硬门禁；未知/残留 owner fail-closed，不以无限重启换表面可用。
- 2026-08-12 — B-030 用户日志证明 utility fatal 只落本地主日志、Sentry 无对应事件。Main 新增 generation one-shot 的 normalized fatal capture，且继续在 API 入口丢弃 diagnostic report 原文；Electron 从 40.2.1 更新到同主版本 40.10.6，吸收后续 Chromium/Electron 补丁，不以全局关闭 GPU 规避旧 Graphite crash。
- 2026-08-12 — 第二台 Mac 的 `codepilot Safe Storage` 授权框与本机 `SecItemCopyMatching` 阻塞揭示 stable/preview CI 也在静默产出 ad-hoc 包。macOS distributable 改为 Developer ID + exact Team ID fail-closed，并在最终产物后置复核；本地 recovery smoke 只能在 canonical 临时 userData 隔离跳过 Safe Storage。
