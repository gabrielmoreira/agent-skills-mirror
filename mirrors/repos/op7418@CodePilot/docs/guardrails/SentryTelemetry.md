# Sentry Telemetry Guardrail

## 1. 词汇表

- **U0**：只含匿名错误与 main-process Release Health session，不含 user/install id 或行为分析。
- **official stable**：CI 显式注入 `CODEPILOT_APP_CHANNEL=stable`、DSN 与 release source maps 的构建。
- **normalized event**：没有可信 stack grouping 时，以稳定枚举 fingerprint 分组的事件。
- **root-cause normalizer**：只读取有界的 `cause/error/lastError/reason/errors` 与 status/code/name/message allow-list，不遍历 body/chunk/request/data 的共享分类器。
- **packaged bundle**：electron-builder 最终复制的 `dist-electron`、`.next/standalone/.next/server` 与 `.next/static` JavaScript。

## 2. 不变量

| 编号 | 契约 |
|---|---|
| ST-01 | 只有 production + stable + DSN + 未 opt-out 才能初始化；dev/preview/fork 默认 no-op。 |
| ST-02 | U0 只有一个 Electron `MainProcessSession`，且 tray-resident 应用必须用 `sendOnCreate:true` 在启动时立即发送；renderer `BrowserSession`、server `ProcessSession` 必须过滤，Node `Http` 必须以 `trackIncomingRequestsAsSessions:false` 替换默认实例（保留 Http 本身）。 |
| ST-03 | U0 不设置 user identity、did、安装 ID、设备名或永久指纹。三层 error event 必须发送 `user.ip_address:null` tombstone，禁止 Relay 按连接补 IP/Geo；除该 null 字段外不得保留任何 user 字段。 |
| ST-04 | 三层 `sendDefaultPii:false`、traces=0；截图、console breadcrumb、local variables 禁止。 |
| ST-05 | 所有事件必须经过 `sanitizeTelemetryEvent`；禁止全量 `setExtras(object)`。 |
| ST-06 | message、URL、model/session/request id、provider name/base URL 不得进入 fingerprint。 |
| ST-07 | 有 stack 的 product fault 与 unknown 不得强设 fingerprint；unknown 必须标 `needs_classification=yes`，normalized fingerprint 必须包含 provider.class。 |
| ST-08 | provider test、user cancel、expected lifecycle、`user_action_required` 都生成 0 个 Sentry event；禁止用 info/message health-summary 绕过 Issue 合同。 |
| ST-09 | rich provider body 只供 UI；共享边界必须在 async capture / rethrow 前写 non-enumerable marker，Node auto-capture 必须丢弃原始异常；受控事件只能发送固定 message 或保留原 stack frame 的安全副本。 |
| ST-10 | Electron init 保持在应用 import 之前，不得用 async policy 推迟；不得用 `integrations: []` 清空 native/minidump 默认能力。 |
| ST-11 | auth token 只在 CI upload step；DSN 不得以 literal 提交；public env 不得含上传权限。 |
| ST-12 | stable source-map upload 必须覆盖最终 packaged JS；临时失败最多重试 3 次，最终仍失败必须 fail closed；任何 DMG/ZIP/EXE/AppImage/deb/rpm/app.asar 不得含 `.map`。 |
| ST-13 | 真实 Sentry smoke 只能由手动 CI 的显式 boolean 输入编译开启；tag、普通本地构建、Windows 与 Linux 必须编译为关闭。Native crash 还必须同时提供运行时开关，smoke 产物不得上传为可下载 artifact 或发布。 |
| ST-14 | stable Linux 必须在原生 Ubuntu 22.04 x64/arm64 runner 构建 AppImage、deb、rpm；两种架构都要验证包架构、better-sqlite3 Electron ABI、packaged server 启动与 0 map，任一失败都阻断 Release。 |
| ST-15 | HTTP 4xx（含 429）、缺凭据、模型不支持 → `user_action_required`；5xx、DNS、timeout 只有 retry exhausted 才能上报 `transient_upstream`；NoOutput 与已 resolve 的 in-band stream error 必须先解包可信 cause/status/code/type，无 upstream 根因才归 `EMPTY_RESPONSE`。 |
| ST-16 | packaged Next utility 的运行期 fatal/error/unexpected exit 每个 generation 最多上报一个 normalized product-fault event。事件只允许稳定 reason、平台定义的有界整数退出码和 utility/host memory 数值；退出码接受 signed int32 至 Windows DWORD 范围，内存指标仍只接受非负有限数。Electron diagnostic report 原文、argv、env、路径和 server stdout/stderr 禁止进入 Sentry。SDK `ChildProcess` 必须保留 breadcrumb 但以 `events:[]` 关闭自动 message event，避免 `abnormal-exit` 与自定义边界双报。启动探测失败、dev、正常 quit 与 telemetry opt-out 必须为 0 event。 |

## 3. 关键文件与责任

- `src/lib/telemetry/contract.ts`：ST-01/02/06/07/08/15。
- `src/lib/telemetry/sanitize.ts`：ST-03/04/05。
- `src/lib/telemetry/root-cause.ts`：ST-08/09/15 的共享有界 normalizer 与安全 stack 副本。
- `src/lib/telemetry/provider-failure.ts` + `provider-marker.ts`：ST-08/09/15。
- `src/lib/telemetry/native-stream-boundary.ts`：每 step 保存 in-band structured error，并在 resolved terminal / catch 之间提供 one-shot capture 与去重。
- `src/lib/telemetry/utility-process-failure.ts`：ST-16 的稳定分类、normalized fingerprint 与纯数值 payload。
- `src/lib/agent-loop.ts` + `src/lib/experimental/agent-loop-toolloop-poc.ts`：`onError` 只保留结构化 root cause 并提前 marker；在 response/finish-step 或 catch 确认 terminal 后统一 capture。
- `src/instrumentation.ts`、`SentryInit.tsx`、`electron/main.ts`：三层 adapter 与 session policy。
- `scripts/build-electron.mjs`、`scripts/sentry-source-maps.mjs`、`.github/workflows/build.yml`、`electron-builder.yml`：ST-11/12/14。
- `src/lib/telemetry/smoke.ts` 与 `.github/workflows/build.yml`：ST-13 的测试专用错误与双门禁。

## 4. 改动检查表

- [ ] 新 tag/extra 是否是低基数枚举，且已加入 sanitizer allow-list？
- [ ] 新 capture 是否在共享边界，是否可能与 SDK auto-capture 重复？
- [ ] 新 expected failure 是否仍保持用户可见，但不冒充 product fault？
- [ ] Provider/Native capture 是否统一经过 root-cause normalizer；4xx/user-action 是否确实 0 event，transient 是否带 retry-exhausted 事实？
- [ ] NoOutput wrapper 与 resolved in-band error 是否先解包 cause/status/code/type；空响应与 partial-content 两种 stream 是否都经过 one-shot terminal capture；新增字段是否在 allow-list、深度/节点/字符串预算内，且未读取 body/chunk/request/data？
- [ ] Utility failure 是否按 generation exactly-once；是否只从 allowlisted 数值快照构造事件，并在 API 形状上拒绝 diagnostic report 原文？
- [ ] Utility exit code 是否按平台整数单独校验（`[-2^31, 2^32-1]`），没有误套 memory 的非负规则或接受浮点/越界值？
- [ ] Electron SDK `ChildProcess` 是否仍以 `events:[]` 替换默认实例（保留 breadcrumb、禁止 abnormal-exit/launch-failed/integrity-failure 自动 Issue），避免和 ST-16 自定义事件双源？
- [ ] “必须 0 event”的 transport/envelope 测试是否在同文件包含至少一个已知应产生 event 的阳性对照，证明 SDK carrier 与捕获链路实际接通？
- [ ] SDK 升级后用真实 SDK client 重新枚举三层 default integrations，并以 request 行为确认只有 main session。
- [ ] sanitizer transport 是否真的序列化 `user.ip_address:null`，且 Sentry project 的 Prevent Storing IP Addresses 仍开启？不要把代码 tombstone 冒充 project 设置已核验。
- [ ] Electron session 是否替换默认实例而非追加第二个 `MainProcessSession`，并以新 stable release 验证 `hasHealthData:true`？
- [ ] official build 的 release/channel 与 package version 一致。
- [ ] upload 使用最终 bundle，package 扫描仍为 0 map。
- [ ] Linux x64/arm64 均由原生 runner 产出三种格式，且架构/ABI/server/0-map 门禁没有被降级为文件存在检查。
- [ ] 修改 source path 时同步处理 debug_meta，保留行列号/debug ID。
- [ ] 真实 smoke 仍是手动 macOS-only；正式 tag 的 compile flag 为 `0`，native crash 无运行时 flag 时不可触发。

## 5. 常见坑

- `sendDefaultPii:false` 不是完整脱敏；server event 删除 `user` 后 Relay 仍可能按连接补 IP/Geo，必须保留 null tombstone，并把 project IP scrubbing 作为纵深防御。
- Electron `MainProcessSession` 默认可只在退出/异常时发送；长驻托盘应用不能把“最终会退出”当及时 Release Health 证据，也不能为修复空数据并存两个 session producer。
- Sentry SDK 默认集成会随版本变化，不能把“当前默认”当合同。
- Electron SDK `ChildProcess` 默认会为 `abnormal-exit` 等 reason 调用 `captureMessage`；只给自定义 utility 边界做 generation one-shot 不能阻止这个第二事件源。应替换为 `childProcessIntegration({events:[]})`，不要整体禁用而丢失 breadcrumb。
- Node `Http` integration 自带 request-mode Release Health session；只过滤 `ProcessSession` 并不能得到 main-only 分母。
- `captureMessage(..., 'info')` 仍会形成 Issue，不能拿它冒充无成本 metrics/activity。
- Native `onError` 不是 retry-exhausted boundary；直接在回调 capture 会把 SDK 后续 finish/catch 再报一次，并把未耗尽的 transient 提前变成 Issue。反过来，只依赖 catch 也会漏掉 promise 正常 resolve 的 in-band error。
- fullStream 正常结束不代表 result promise 一定 resolve；初始 HTTP/DNS 失败可能先产生 error part，再以 fresh、无 cause 的 NoOutput 拒绝 `response`/`finishReason`。resolved-stream fallback 必须排在 result promise 之后，避免先报 root cause、catch 又报虚假 `EMPTY_RESPONSE`。
- `utilityProcess` 的 `error` 回调报告可能包含命令行、环境和绝对路径；不能因为它能解释 native crash 就直接 capture/log。应只保留 Electron 类型映射后的稳定枚举与已有数值观测。
- `exitCode` 不是内存计数：Electron 在 POSIX 暴露 waitpid status、在 Windows 暴露 `GetExitCodeProcess` 结果。复用“非负数”过滤器会静默丢掉负 sentinel；应使用独立的有界整数合同，且不要把退出码加入 fingerprint。
- Electron SDK v7 默认 `SentryMinidump` 不在崩溃时直传（Crashpad `uploadToServer:false`）；隔离崩溃 smoke 必须再无 crash flag 启动一次，让 SDK 读取并上传 completed dump。
- `productionBrowserSourceMaps` + debug ID 不保证 Turbopack 产生真实 map；必须检查非占位产物。
- standalone tracer 会漏掉 server map；必须按最终 JS 图复制并验证。
- map 上传成功也不代表安全；electron-builder 每个 FileSet 都要排除 `.map`。
- source-map upload 可以对临时网络/API 故障做有界重试，但不得跳过失败继续 package；测试可用 `SENTRY_UPLOAD_RETRY_DELAY_MS=0` 取消等待，生产固定保留退避。

## 6. 测试覆盖

- `telemetry-contract.test.ts`：enable、main-only eager session、breadcrumb-only ChildProcess、outcome、fingerprint。
- `telemetry-sanitizer.test.ts`：PII/content/path/debug_meta 清洗与真实 Node transport null-IP tombstone。
- `telemetry-provider-failure.test.ts`：全 4xx、5xx/DNS/timeout retry、NoOutput 解包、循环/深度/恶意对象、safe stack 与 anti-double-capture。
- `telemetry-native-stream-boundary.test.ts`：真实 AI SDK error-part 生命周期、resolved promise、partial content、one-shot terminal/catch 去重。
- `telemetry-native-stream-loop.test.ts`：真实 Native/ToolLoop + Anthropic SSE/初始 HTTP 失败 + Sentry transport，锁定 resolved/rejected 两种生命周期下 5xx exactly-once 与 4xx zero-Issue；零事件断言与阳性 5xx 对照共用同一 carrier。
- `telemetry-native-boundary-shape.test.ts`：Native/ToolLoop `onError` 延后到 terminal finish/catch 与 shared marker 所有权。
- `sentry-should-report.test.ts`：user-action 0 event、无 info/message health-summary、transient retry gate 与默认 stack grouping。
- `telemetry-build-wiring.test.ts`：DSN/Secret/init/source-map CI 形状。
- `telemetry-smoke.test.ts`：三层静态故障、手动 CI 编译门禁、native crash 双门禁与 smoke artifact 排除。
- `telemetry-utility-process-failure.test.ts` + `electron-server-recovery.test.ts`：utility failure 稳定分组、数值 allow-list、任意 reason 归一化、raw report 丢弃与 generation one-shot 接线。
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
- 2026-08-04：Phase 6 P1 统一 shared/native normalizer；429 随全部 4xx 固定为 user action，移除 `telemetry-health-v1.json`/info Issue 代码；不新增 user/did、metrics 或行为遥测。
- 2026-08-04：Claude 独立复核证明 AI SDK 的 in-band error 可在 `response`/`finishReason` 均 resolve 时绕过 catch；Native 两条 loop 改为 shared per-step terminal state，在 response/finish-step 与 catch 之间 exactly-once capture。只接受有界 provider `type` enum 映射，不读取 SSE body/chunk；同时只保留 V8 frame line，避免多行 Error message 混入 safe stack。
- 2026-08-05：Claude 同 tip 复审补出 ToolLoop POC 的 rejected-promise P2：fullStream 后过早执行 fallback，会先标 reported，再把 fresh NoOutput 当无关故障二报。POC 改为先 await `result.response`，仅在 promise resolve 后执行 defensive terminal fallback；真实初始 403/503 对照锁定两条 loop 为 0/1 event。
- 2026-08-07：0.65 真实 server event 证明删除 `user` 后仍出现 IP/Geo；三层 sanitizer 改发 `ip_address:null`，真实 Node transport 锁定序列化结果。Electron 唯一 main session 改为 `sendOnCreate:true`，解决 tray-resident 应用等待退出导致的 `hasHealthData:false`；外部 project IP scrub 与新 stable cohort 仍需发布侧验证。
- 2026-08-12：只读复核发现 v0.66 发布后 72 小时 official project 没有新 Issue；这不能单独证明 telemetry 失效，也不能替代 Release Health/session 分母。用户事故中的四次 Next utility exit 5 没有进入 Sentry，确认是 Main 只写本地日志的观测缺口；补充 ST-16，未来 stable opt-in 构建按 generation 上报一次脱敏 fatal event。
- 2026-08-12：Claude 复审发现 Electron SDK 默认 `ChildProcess` 对 `abnormal-exit` 仍自动 `captureMessage`，会和 ST-16 自定义 event 双报。Main 改为显式替换 `childProcessIntegration({events:[]})`，保留 process breadcrumb，只让 normalized generation boundary 拥有 utility Issue。
- 2026-08-12：复审 P3 follow-up 将 utility `exitCode` 从 memory-style 非负过滤中分离；保留 Electron 平台整数（signed int32 至 Windows DWORD），拒绝浮点、非有限与越界值，且 fingerprint 不变。
