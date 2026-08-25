# Release Guardrail

> **Status: Active contract** — 已覆盖版本 source of truth、tag/资产不可变、stable 三平台分发与 macOS-only updater、真实 ABI/server-health、attestation 与失败后的补丁版本策略。
> **为什么先读**：发版有严格顺序（RELEASE_NOTES → package.json version → npm install → 提交推送 → tag → CI 自动构建发布）；**不能删 tag**——一旦 tag 被删再重建，已发布的 Release 会变 Draft（`feedback_never_delete_release_tags.md`）。CI 会自动建 Release 并上传产物，不要手动建。
> **已知关键文件**：`RELEASE_NOTES.md`、`package.json`（version 字段）、`package-lock.json`、`.github/workflows/*`（CI 发版流程）。

## 词汇表

- `RELEASE_NOTES.md` — 当前版本 Release 正文 source of truth；CI 读它作为 GitHub Release body。
- `tag` — `v{版本号}`；推送后触发 CI 构建发布。
- `Shipped` — tag CI 成功且 GitHub Release 与全部平台资产真实存在；只推送 tag 不算发布完成。
- `immutable asset graph` — 同一 build 输出中的 installer、builder metadata、blockmap、checksum；central job 只审计并一次上传，不重算/替换二进制。
- `publisher identity` — macOS Apple Team ID / Windows Authenticode subject；自动更新跨版本必须稳定。

## 不变量 / 契约表

| # | 不变量 | 由谁守 |
|---|--------|--------|
| 1 | 不能删 release tag——删了再建会让已发布 Release 变 Draft，丢失下载链接 | 人 + CI |
| 2 | 必须等用户明确指示才 `git push` + `git tag`；commit 可以正常进行 | 人（执行 Agent） |
| 3 | RELEASE_NOTES.md 格式必须严格遵循 CLAUDE.md "Release Notes 格式" 一节 | 人 |
| 4 | 更新内容必须用用户能理解的语言，不要出现 commit hash / 函数名 / 文件路径 | 人 |
| 5 | 下载链接必须是完整 GitHub release download URL，用户点击即可下载 | 人 |
| 6 | tag CI 任一平台失败时不得删除/重建该 tag；修复后递增 patch 版本重新发布 | 人 + CI |
| 7 | stable tag 的 macOS arm64/x64/universal、Windows x64、Linux x64/arm64 版本/真实 Main health/ABI/source-map 与资产门禁均通过且 Release job 成功，才能报告 Shipped | `.github/workflows/build.yml` + 执行 Agent |
| 8 | stable/preview 的 macOS app+DMG 必须签名、公证、staple 并通过 Gatekeeper。Windows stable 手动包在 signer 全配置时校验两个 CodePilot 自有 EXE 的同一 Authenticode subject/timestamp；完全未配置时两者必须明确为 `NotSigned`，半配置必须失败 | CI verifier |
| 9 | 当前 macOS installer、`latest-mac.yml`/`preview-mac.yml`、blockmap、checksum 来自同一输出；metadata 必须恰好一条 universal ZIP entry，DMG 不生成 update blockmap；缺失/错 hash/重复 basename/stagingPercentage 均阻断 | `verify-update-assets.mjs` |
| 10 | stable 资产发布后不可变；坏版本只发更高 patch。preview metadata 独立且 prerelease 不得覆盖 stable feed | 人 + CI |
| 11 | 私钥只存在于 secret/signing service；轮换/丢失按 `docs/rules/release.md` runbook，publisher/Team ID 变化不得直接自动更新 | 人 + CI |
| 12 | stable tag 发布三平台安装包，但只允许 macOS updater graph；Windows/Linux official updater provenance 必须为 `0`，不得发布 `latest.yml` / `latest-linux*.yml` 或外置 updater blockmap。preview Release 仍为 macOS-only | workflow + verifier |
| 13 | Windows stable 手动包的 signer 三件套必须 all-or-none：全有则签名并校验，全无则显式关闭签名且校验 `NotSigned`，部分配置 fail closed。未签名状态必须在 Release Notes 明示，不得冒充可信 publisher | workflow + docs |
| 14 | workflow 顶层只有 `contents: read`；`contents`/OIDC/attestation 写权限只授予 stable/preview 发布 job。发布 job 先把完整资产图上传到可恢复 draft，全部成功后才一次切为公开 stable/prerelease；上传中断不得留下用户可见的半 feed | workflow + source-contract test |
| 15 | universal 合并时，按目录选型的 SDK/Sharp Darwin 预编译文件与 already-universal Trash helper 只能由精确 `x64ArchFiles` glob 保留；`better-sqlite3` / `zlib-sync` 必须先逐架构替换再由 universal 合并，合并后的 `afterPack`（Arch=4）必须 no-op，不得把 fat binary 覆盖回单架构 | builder config + hooks + source-contract test + universal package probe |
| 16 | 分发 DMG 容器必须在 package step 的临时 keychain 仍可用时由同一 Developer ID Application identity 签名；提交公证前先校验配置 Team，公证/staple 后再用 `codesign`、`stapler` 与 DMG 专用 Gatekeeper `open/context:primary-signature` 三重验收 | builder config + notarizer + final verifier |

## 关键文件 + 责任

| 文件 | 守哪条不变量 |
|------|--------------|
| `RELEASE_NOTES.md` | Release 正文 source of truth |
| `package.json` | version 字段 |
| `package-lock.json` | 同步版本号（`npm install` 后会自动更新） |
| `.github/workflows/*` | CI 签名、公证、构建、资产审计、attestation 与上传 |
| `scripts/after-pack.js` / `scripts/after-sign.js` | better-sqlite3 Electron ABI + macOS Developer ID identity gate |
| `scripts/notarize-macos-dmgs.mjs` / `verify-macos-notarization.mjs` | DMG 公证/staple 与 app/DMG/ZIP Gatekeeper 门禁 |
| `scripts/verify-windows-signing.ps1` | CodePilot installer + 顶层 app EXE publisher/timestamp 门禁；禁止递归要求第三方 EXE 同 publisher |
| `scripts/verify-update-assets.mjs` | stable/preview metadata/hash/blockmap 原子图 |

## 改动检查表

- [ ] 更新 RELEASE_NOTES.md 之前先看 `git log --oneline` 但不要原样复制
- [ ] 每个 Release Notes 条目必须说清楚"用户能感知到什么变化"
- [ ] 跳过没内容的分类（如没有"修复问题"则删掉那个标题）
- [ ] `npm install` 同步 lock 后再提交
- [ ] 用户明确指示后才 `git push origin main && git tag v{版本号} && git push origin v{版本号}`
- [ ] 不要手动建 GitHub Release——CI 会自动建并上传产物
- [ ] tag 后持续监控 CI；核实 Release URL、macOS 双架构 DMG/ZIP、universal ZIP、Windows NSIS、Linux 双架构三种包、`latest-mac.yml`、Mac ZIP blockmap、SHA256SUMS 与 attestations 均存在；不得出现 Windows/Linux metadata/blockmap，mac DMG 不得有 update blockmap/metadata entry
- [ ] macOS app/DMG/ZIP 的 Developer ID、公证、staple、Gatekeeper 与 Team ID 全通过
- [ ] `dmg.sign=true` 是否保持；DMG 是否在提交 Apple 前已验证为配置 Team 的 Developer ID，而不是只有 notarization ticket 的未签名容器
- [ ] Windows signer 全配置时 installer 与顶层 CodePilot.exe 的 Authenticode subject、SHA-256 与 RFC3161 timestamp 全通过；全未配置时两者为 `NotSigned` 且 Release Notes 明示；签名密码只注入 package step，不写 `GITHUB_ENV`
- [ ] preview 使用 `preview-mac.yml` + prerelease；stable 只含 `latest-mac.yml`，不包含 `stagingPercentage` 或非 Mac metadata；central distribution asset audit 全通过
- [ ] metadata 是否恰好一条 universal ZIP；stable/preview 是否先完整上传 draft，再一次切换可见性；失败 draft 是否可由同 tag workflow rerun 恢复
- [ ] universal package 是否实际合并成功；双架构 Sharp 是否在 `next build` 前按 lockfile integrity 准备；`x64ArchFiles` 是否仍为逐路径 allow-list；最终 SQLite/zlib 与主程序是否保留 arm64+x86_64 双 slice，并由 Intel universal health gate 验证？
- [ ] signer 到期/轮换窗口已检查；identity 变化或 key loss 已按 release runbook 处理
- [ ] packaged server 必须在 Electron runtime 下启动并通过 `/api/health`，不能只凭打包成功、Next.js `Ready` 或 native ABI 判定可发布
- [ ] CI 失败时保留失败 tag，修复后发新 patch 版本

## 常见坑

- 删 tag 重建：已发布的 Release 变 Draft（`feedback_never_delete_release_tags.md`）。如果发版后发现 RELEASE_NOTES 错了，**新建一个 patch 版本**而不是重发同版本。
- Release Notes 写成给开发看的（commit hash / 函数名）：用户读不懂；必须用面向用户的语言。
- 自动发版：禁止；commit 可以做，但 push + tag 必须等用户明确指示。
- 把“tag 已推送”报告成“已发布”：Release job 可能因任一平台构建失败被跳过；必须查看最终 Release 与资产。
- 只验 ABI、不启动 server：v0.58.3 的安装包通过版本与 better-sqlite3 ABI 检查，但缺少 Next.js 哈希 external alias，用户界面永久停在 `Starting CodePilot...`。
- 只签 app、不公证/staple DMG：下载后的分发路径仍会被 Gatekeeper 拦截；三层都必须验。
- 只给未签名 DMG 提交公证并 staple：`stapler validate` 可以看到票据，但 Gatekeeper 会以 `source=no usable signature` 拒绝容器。必须先用 Developer ID Application 签 DMG，再公证/staple。
- 只上传 installer：electron-updater 还需要 builder metadata 与 blockmap；缺任一项就是不可用 feed。
- 让 mac DMG 进入 update metadata：builder 先写 sha512，后置 staple 再改写 DMG，central audit 必然失败。DMG 只做手工 bootstrap，mac updater 只引用 ZIP。
- 更新已发布 YAML 或复用版本：破坏不可变证据和客户端缓存。恢复必须递增 patch。
- 递归要求 `win-unpacked/**/*.exe` 都由 CodePilot 证书签名：会把 Electron/Chromium helper 与第三方工具的合法 publisher 当失败。只验两个 CodePilot 自有入口。
- 把 Windows PFX 密码写入 `GITHUB_ENV`：secret 会跨后续 step 常驻。只在 electron-builder package step 的 `env` 注入。
- 把 native 双架构与 universal 包塞进同一个 45 分钟 step：第二段没有独立预算。三段 package/package/notarize 各自有界。
- 先创建公开 Release 再逐个上传：上传中断会让客户端或用户看到半套资产。必须先写入 draft；重跑只允许恢复同 tag 的 draft，发现同 tag 已公开则 fail closed。
- 把 universal 合并失败粗暴修成宽泛 `x64ArchFiles`：会让 native ABI 错误绕过 lipo 检查。只允许逐路径选型的 SDK/Sharp 与 already-universal Trash 文件；SQLite/zlib 必须真实合并。
- universal 合并成功后仍在 `afterPack` 用 Arch=4 重编 native：会把刚生成的 fat binary 覆盖成宿主单 slice。Arch=4 只允许保留合并结果。

## 测试覆盖

| 契约 | 测试文件 |
|------|----------|
| 构建产物 server 启动 | `scripts/verify-packaged-server.mjs` + `.github/workflows/build.yml` |
| tag/version、P0 regression、macOS version/ABI/server-health/checksum | `.github/workflows/build.yml` |
| release notes / package version drift | `scripts/lint-docs-drift.mjs` + CI verify-source |
| macOS Developer ID + notarization | `macos-signing-policy.test.ts` + final CI verifier |
| Windows Authenticode | `release-trust-update-assets.test.ts` + final CI PowerShell verifier |
| metadata/blockmap/checksum/channel | `release-trust-update-assets.test.ts` + `verify-update-assets.mjs` |
| 真实 Main→utilityProcess→SQLite ABI | `electron-packaging-hygiene.test.ts` + `verify-electron-main-health.mjs` |

## 设计决策日志

- 2026-07-20 — v0.58.2 tag 的 macOS 成功但 Windows `EBUSY`，Release job 因 fail-closed 被跳过；保留 tag，修复后改发 v0.58.3。
- 2026-08-23 — stable/preview 均 fail-closed 签名；macOS 增加公证/staple，Windows 增加固定 publisher/timestamp 校验。
- 2026-08-23 — updater 资产改为 builder metadata/blockmap/installer/checksum 同输出审计与一次上传；不采用 stagingPercentage，坏 stable 只发更高 patch。
- 2026-08-23 — macOS `dmg.writeUpdateInfo=false`：公证/staple 后的 DMG 仍发布供手工安装，但不进入 updater graph；`latest-mac.yml` 只引用 ZIP，verifier 拒绝 DMG entry，避免后置 staple 令 metadata hash 失真。
- 2026-08-24 — stable/preview macOS 都产出 arm64+x64 手工 DMG 与 universal updater ZIP，native/universal/notarize 分别计时。Windows verifier 收窄到两个 CodePilot 自有 EXE，签名密码只在 package step 注入，不跨 step 持久化。
- 2026-08-24 — 用户决定本轮只交付 macOS 自动更新。tag/prerelease 发布依赖收窄到 Mac，central verifier 使用 `macos` target 并拒绝非 Mac 资产；Windows/Linux job 保留为 updater provenance 关闭的手工 artifact 入口。
- 2026-08-24 — 发布写权限从 workflow 顶层收窄到 stable/preview 发布 job；两条发布链先上传/恢复 draft，完整后再公开。mac metadata 收紧为恰好一条 universal ZIP，Mac-only preview 与 stable 对称拒绝 Windows/Linux 资产。
- 2026-08-24 — 用户澄清“先做 Mac 自动更新”不是“只发布 Mac”。stable 恢复同一 Release 的 Windows/Linux 手动安装包，且保持 provenance=0、拒绝非 Mac updater metadata；当前 Windows signer 三件套全缺时允许诚实的未签名手动包，部分配置仍 fail closed。preview 保持 macOS-only。
- 2026-08-24 — `v0.67.2` 首次正式 CI 在 universal 合并处发现同 app tree 预编译文件。真实本地探针完整枚举并分型：SDK/Sharp 按目录选型、Trash 已是 universal，逐路径 allow-list；zlib 与 SQLite 则逐架构重编、真实 lipo。探针还发现 universal 后置 `afterPack` 会用 Arch=4 覆盖 fat binary，因此明确 no-op。旧 tag 保留且未创建 Release，修复后递增 `v0.67.3`。
- 2026-08-24 — `v0.67.3` 正式 CI 的 app/原生/universal 签名与公证均通过，但最终 DMG Gatekeeper 验证发现容器只有 notarization ticket、没有可用 Developer ID signature。保留失败 tag；启用 `dmg.sign=true`，并把 DMG Team/signature 检查前移到 notary submission 之前，修复后递增 `v0.67.4`。
