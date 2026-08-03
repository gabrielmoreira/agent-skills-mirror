# Sentry Telemetry Guardrail

## 1. 词汇表

- **U0**：只含匿名错误与 main-process Release Health session，不含 user/install id 或行为分析。
- **official stable**：CI 显式注入 `CODEPILOT_APP_CHANNEL=stable`、DSN 与 release source maps 的构建。
- **normalized event**：没有可信 stack grouping 时，以稳定枚举 fingerprint 分组的事件。
- **health summary**：user-action 类问题按 release/bucket 24h 去重的低频 info Issue，不是逐错误事件。
- **packaged bundle**：electron-builder 最终复制的 `dist-electron`、`.next/standalone/.next/server` 与 `.next/static` JavaScript。

## 2. 不变量

| 编号 | 契约 |
|---|---|
| ST-01 | 只有 production + stable + DSN + 未 opt-out 才能初始化；dev/preview/fork 默认 no-op。 |
| ST-02 | U0 只有 Electron `MainProcessSession`；renderer `BrowserSession`、server `ProcessSession` 必须过滤，Node `Http` 必须以 `trackIncomingRequestsAsSessions:false` 替换默认实例（保留 Http 本身）。 |
| ST-03 | U0 不设置 user、did、安装 ID、设备名或永久指纹。 |
| ST-04 | 三层 `sendDefaultPii:false`、traces=0；截图、console breadcrumb、local variables 禁止。 |
| ST-05 | 所有事件必须经过 `sanitizeTelemetryEvent`；禁止全量 `setExtras(object)`。 |
| ST-06 | message、URL、model/session/request id、provider name/base URL 不得进入 fingerprint。 |
| ST-07 | 有 stack 的 product fault 与 unknown 不得强设 fingerprint；unknown 必须标 `needs_classification=yes`，normalized fingerprint 必须包含 provider.class。 |
| ST-08 | provider test、user cancel、expected lifecycle 不生成 Error Issue；user-action 只能走有界 health summary。 |
| ST-09 | rich provider body 只供 UI；共享边界 capture 后必须 marker，Node auto-capture 必须丢弃原始异常。 |
| ST-10 | Electron init 保持在应用 import 之前，不得用 async policy 推迟；不得用 `integrations: []` 清空 native/minidump 默认能力。 |
| ST-11 | auth token 只在 CI upload step；DSN 不得以 literal 提交；public env 不得含上传权限。 |
| ST-12 | stable source-map upload 必须覆盖最终 packaged JS；临时失败最多重试 3 次，最终仍失败必须 fail closed；任何 DMG/ZIP/EXE/AppImage/deb/rpm/app.asar 不得含 `.map`。 |
| ST-13 | 真实 Sentry smoke 只能由手动 CI 的显式 boolean 输入编译开启；tag、普通本地构建、Windows 与 Linux 必须编译为关闭。Native crash 还必须同时提供运行时开关，smoke 产物不得上传为可下载 artifact 或发布。 |
| ST-14 | stable Linux 必须在原生 Ubuntu 22.04 x64/arm64 runner 构建 AppImage、deb、rpm；两种架构都要验证包架构、better-sqlite3 Electron ABI、packaged server 启动与 0 map，任一失败都阻断 Release。 |

## 3. 关键文件与责任

- `src/lib/telemetry/contract.ts`：ST-01/02/06/07/08。
- `src/lib/telemetry/sanitize.ts`：ST-03/04/05。
- `src/lib/telemetry/health-summary.ts`：ST-08。
- `src/lib/telemetry/provider-failure.ts` + `provider-marker.ts`：ST-08/09。
- `src/instrumentation.ts`、`SentryInit.tsx`、`electron/main.ts`：三层 adapter 与 session policy。
- `scripts/build-electron.mjs`、`scripts/sentry-source-maps.mjs`、`.github/workflows/build.yml`、`electron-builder.yml`：ST-11/12/14。
- `src/lib/telemetry/smoke.ts` 与 `.github/workflows/build.yml`：ST-13 的测试专用错误与双门禁。

## 4. 改动检查表

- [ ] 新 tag/extra 是否是低基数枚举，且已加入 sanitizer allow-list？
- [ ] 新 capture 是否在共享边界，是否可能与 SDK auto-capture 重复？
- [ ] 新 expected failure 是否仍保持用户可见，但不冒充 product fault？
- [ ] SDK 升级后用真实 SDK client 重新枚举三层 default integrations，并以 request 行为确认只有 main session。
- [ ] official build 的 release/channel 与 package version 一致。
- [ ] upload 使用最终 bundle，package 扫描仍为 0 map。
- [ ] Linux x64/arm64 均由原生 runner 产出三种格式，且架构/ABI/server/0-map 门禁没有被降级为文件存在检查。
- [ ] 修改 source path 时同步处理 debug_meta，保留行列号/debug ID。
- [ ] 真实 smoke 仍是手动 macOS-only；正式 tag 的 compile flag 为 `0`，native crash 无运行时 flag 时不可触发。

## 5. 常见坑

- `sendDefaultPii:false` 不是完整脱敏；request body、breadcrumb、extra 仍需 allow-list。
- Sentry SDK 默认集成会随版本变化，不能把“当前默认”当合同。
- Node `Http` integration 自带 request-mode Release Health session；只过滤 `ProcessSession` 并不能得到 main-only 分母。
- `captureMessage(..., 'info')` 仍会形成 Issue，不能拿它冒充无成本 metrics/activity。
- Electron SDK v7 默认 `SentryMinidump` 不在崩溃时直传（Crashpad `uploadToServer:false`）；隔离崩溃 smoke 必须再无 crash flag 启动一次，让 SDK 读取并上传 completed dump。
- `productionBrowserSourceMaps` + debug ID 不保证 Turbopack 产生真实 map；必须检查非占位产物。
- standalone tracer 会漏掉 server map；必须按最终 JS 图复制并验证。
- map 上传成功也不代表安全；electron-builder 每个 FileSet 都要排除 `.map`。
- source-map upload 可以对临时网络/API 故障做有界重试，但不得跳过失败继续 package；测试可用 `SENTRY_UPLOAD_RETRY_DELAY_MS=0` 取消等待，生产固定保留退避。

## 6. 测试覆盖

- `telemetry-contract.test.ts`：enable、main-only session、outcome、fingerprint。
- `telemetry-sanitizer.test.ts`：PII/content/path/debug_meta 清洗。
- `telemetry-health-summary.test.ts`：跨重启 24h 去重与 bucket 限界。
- `telemetry-provider-failure.test.ts`：provider test/cancel/retry 分类与 anti-double-capture。
- `telemetry-build-wiring.test.ts`：DSN/Secret/init/source-map CI 形状。
- `telemetry-smoke.test.ts`：三层静态故障、手动 CI 编译门禁、native crash 双门禁与 smoke artifact 排除。
- `electron-packaging-hygiene.test.ts`：所有 package FileSet 排除 map。
- `instrumentation-shape.test.ts` + `sentry-dev-guard.test.ts`：dev 不加载 Node SDK。

## 7. 决策日志

- 2026-08-02：默认采用 U0；U1a/U1b/U2 不在本轮实现。
- 2026-08-02：升级 browser/node 到 10.69.0、Electron 到 7.16.0；三层 default integrations 改为显式过滤而非整体替换。
- 2026-08-02：Turbopack output maps 可覆盖三层，compile 从 9.2s 增至 22.6s；用户已接受 stable tag 绝对增加约 13.4s 的取舍。
- 2026-08-02：三层 symbolication 与 native minidump 采用手动 macOS CI 的隔离夹具；编译时 + 运行时双门禁防止正式发布误触发。
- 2026-08-02：首次 native smoke 只证明 `process.crash()` 非零退出，新 project 无 native Issue；核对 SDK 本体后补上崩溃后恢复启动，禁止把“已生成 dump”冒充为“已送达 Sentry”。
- 2026-08-02：CI #312 的恢复启动成功上传真实 minidump；Sentry event `778040c8b19a40ee983c2b3bfe79cb1c` 解析为 `electron::ElectronBindings::Crash` / `EXC_BAD_ACCESS`，release `0.63.0`、environment `production`、Electron 40.2.1 macOS arm64。
- 2026-08-03：stable Linux 恢复为原生 Ubuntu 22.04 x64/arm64 matrix；CI #313 的六个 v0.64.0 安装包全部通过架构、Electron ABI、packaged server、0-map 与 glibc 2.35 基线门禁。
