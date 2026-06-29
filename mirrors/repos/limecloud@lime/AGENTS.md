# AI Agent 指南

本文件只用于 **开发 Lime 源码仓库本身**。根 `AGENTS.md` 只保留仓库级约束、导航和统一入口；模块细节与长流程统一下沉到 `internal/`。

## 原则

1. **代码仓库是唯一的记录系统** - 不在 repo 里的知识对智能体不存在；凡影响开发的讨论、决策、外部资料，都必须落成 repo 内的 versioned artifact
2. **本文件是地图，不是百科全书** - 保持约 `100` 行，只暴露本层信息和下一步导航
3. **把品味编码为规则** - 优先用 linter、结构测试、CI 检查约束质量；可机械验证优先于散文指南
4. **计划是一等工件** - 执行计划带进度日志，集中存放于 `internal/exec-plans/`
5. **持续垃圾回收** - 技术债按小额、持续方式偿还；差距追踪见 `internal/exec-plans/tech-debt-tracker.md`
6. **卡住时修环境，不是更用力** - 先补上下文、工具、约束，再继续实现；缺口也要写回 repo

## 工程协作方式

1. **默认以完整交付为单位** - 不把可自行判断的实现细节、下一步动作或可逆选择转嫁给用户；读代码、做判断、完成闭环后再报告结果
2. **少问但不越权** - 只有真实需求歧义、不可逆 / 高风险操作、生产环境影响、凭证缺失，或继续会明显偏离用户意图时才停下来询问
3. **结果汇报优先** - 收尾说明做了什么、为什么这样做、验证了什么、还剩什么缺口；避免过程性礼貌汇报
4. **任务完成标准优先** - 以可编译、类型正确、测试通过、功能真实可用作为完成依据；实现细节服从项目既有模式和当前主线目标
5. **不主动扩大承诺** - 不在完成后追问“要不要继续做 X/Y/Z”；如存在自然下一刀，只简短列出建议，等待用户明确要求
6. **并行协作仅在多 Agent 时启用** - 默认按单 Agent 模式直接动手；只有用户明确说明同时有其他 Agent / 进程在跑，或工作树有未知改动时，才启用 `internal/aiprompts/parallel-agent-collaboration.md` 的写集认领协议（盘点 `git status --short`、声明窄写集、避让脏文件）。不要把它当成默认开工仪式
7. **复核结论先行** - 用户问“结论 / 复核 / 是否能删 / 是否 dead”时，先用 `3-8` 行给可执行结论和关键证据；除非用户明确要求修文档、补守卫或继续实现，不自动扩展成治理文档清理、全量 inventory 或长 checklist

## 基础约束

1. **始终使用中文** - 回复、文档、代码注释默认使用中文；若文件已有其他注释语言，保持与现有代码库一致
2. **先读后写** - 修改文件前先读现状和相邻边界
3. **代码体量边界** - 非生成代码文件接近 `800` 行进入拆分预警，超过 `1000` 行时触碰前必须按领域 / 职责 / 数据边界 / 协议边界拆分；优先复用项目已有模块化模式，如 facade + 子模块、service / repository 分层、projection / selector / helper 分离。无法本轮拆分时，必须在执行计划登记 blocker、风险、退出条件和下一次拆分入口，不得继续追加新业务逻辑
4. **避免无关变更** - 不顺手重构、不扩大范围、不主动做 git 提交或分支操作
5. **默认双平台** - 新增功能、脚本、路径处理默认同时考虑 macOS 与 Windows
6. **禁止硬编码平台路径** - 用户数据、日志、缓存、凭证等目录必须走系统 API 或统一封装
7. **优先平台无关入口** - 优先复用 `npm`、`cargo`、Electron / App Server 命令和仓库脚本，不新增只适用于 Bash/zsh 的流程
8. **未验证的平台假设要显式说明** - 涉及文件系统、进程、终端、快捷键、窗口、托盘、权限时尤其如此
9. **新增命名禁止品牌前缀** - 新程序、目录、crate/package、Electron IPC channel、App Server 方法、API 网关、类型、模块和脚本默认不得添加 `Lime` / `lime_` / `lime-` 品牌前缀；直接使用领域名，如 `app_server_*`、`app-server`。只有对外发布品牌标识、历史兼容或第三方生态已固定命名时才允许保留，并在执行计划说明原因
10. **`scripts/` 目录冻结** - `scripts/` 根目录和一级领域目录都是受治理边界；新增可执行脚本默认放到已有 `scripts/<domain>/`、`scripts/lib/` 或所属 package，并通过 `npm run governance:scripts` 守住根目录与领域目录基线。只有公开稳定入口且无法归入已有领域目录时才允许例外，必须同步 `scripts/README.md`、`scripts/script-root-governance-baseline.json` 和执行计划退出条件
11. **新增 Agent 逻辑默认走 App Server** - 新 AI Agent、runtime、host integration、跨 App 复用能力默认落到 `app-server` crates、JSON-RPC 协议、client 与 RuntimeCore；Electron 只作为 Desktop Host bridge，负责 IPC、窗口、托盘、Dock、updater 和 sidecar 生命周期，不是第二套后端或业务 adapter；旧 `agent_runtime_*` / Aster 命令只允许作为 retired guard、历史 evidence、test-only fixture 或受控迁移残留，不再作为生产 truth 或新增能力入口
12. **`lime-rs/src/**`已物理删除** - 该目录是脱离 cargo 构建图的孤儿目录，2026-06-10 整目录删除（约 18.7 万行旧 Tauri command 宏标注代码）。新 Rust 后端能力一律进入`lime-rs/crates/\*\*`：App Server、RuntimeCore、services、core、agent、协议/client crate；桌面壳能力进入 Electron Desktop Host
13. **旧 Tauri wrapper 删除清理已收口** - `lime-rs/src/commands/**` 旧 Tauri wrapper 清理区已随 `lime-rs/src/**` 一并删除，不得恢复任何文件；不再承接业务逻辑、API adapter、runtime 分支、领域服务、compat wrapper、退场 stub 或 thin facade。新增 Rust 后端能力落到 App Server crates / RuntimeCore / services 等 current 事实源；桌面壳能力落到 Electron Desktop Host。守卫见 `src/lib/governance/rustCommandsCurrentBoundary.test.ts`
14. **前端 DevBridge 按职责治理** - `src/lib/dev-bridge/**` 不是整体删除对象：`safeInvoke`、HTTP client、`app_server_handle_json_lines`、bridge availability / event listener capability 是 current renderer bridge；`commandPolicy` 中旧命令 truth / no-mock fallback 是迁移期 `compat / deprecated`；已迁旧命令名只能进入 `dead` / `test-only` guard。后续治理优先收缩 policy、mock、fallback、负向测试和 contract guard，不得为清旧命令误删 current App Server 传输链；删不动且会跨命令组长期存在的 residual 必须回挂 `internal/exec-plans/tech-debt-tracker.md` 的 `CCD-012`
15. **Electron 打包事实源统一 Forge** - Electron packaging / installer / signing / notarization / updater metadata 的 current 配置只允许走 `forge.config.mjs`、`electron-forge package`、`electron-forge make` 与 Forge 官方 maker；运行时更新只允许走 `electron/updateHost.ts` + Electron 内置 `autoUpdater`。旧 builder 配置 / CLI、自定义 Windows installer maker、旧 YAML / blockmap updater metadata 均按 `dead` 处理，不得新增引用或写回文档、CI、守卫、i18n evidence；Windows current installer 为 Forge Squirrel，macOS current updater metadata 为 `RELEASES.json`，Windows current updater metadata 为 `RELEASES`。
16. **不要继续扩展 compat / deprecated 路径** - 新 API、新命令、新前端入口默认落在当前 `current` 主路径
17. **规划改了且明确无需兼容时，优先删旧实现** - 如果用户已明确“上一版无人使用 / 不用兼容 / 旧实现阻碍主线”，旧实现默认按 `dead` 或带退出条件的 `deprecated` 处理，不要继续修补、包裹或平移
18. **`legacy current reference` 不是续命许可** - 旧路线图、旧实现锚点只用于理解现状与迁移，不等于允许继续往旧页面、旧命令、旧协议上加功能
19. **目录级 dead 快速判定** - 对整目录旧实现，如果同时满足：已不在构建 / workspace manifest 中，当前工作树已物理删除或 staged delete，已有 current owner 承接，且边界守卫 / 契约检查能防回流，可直接按目录级 `dead / deleted / forbidden-to-restore` 处理；不要求逐文件证明“业务语义无价值”
20. **历史 checkpoint 不当 current 残留** - `internal/exec-plans/**`、旧路线图和 git history 中记录的历史写集 / 搜索证据默认是 evidence，不是当前 owner 引用；只在这些历史文本被当前规则段落、当前状态摘要或 active checklist 当成现役落点时才清理
21. **Rust crate 抗膨胀** - 新增 Rust 逻辑禁止默认落 `lime-core` / `services` 平铺层，必须先回答"为什么不是独立模块 / 既有 domain"；参照 Codex "resist adding to core"（见 `internal/refactor/codex-engineering-patterns.md` § 2）。`processor.rs` / `runtime.rs` 等中心文件新增方法时，优先放到对应 domain 子模块（如 `processor/project_git.rs`），中心文件只做 dispatch 接线

## 工程硬规则

1. **默认统一校验入口** - 提交前默认执行 `npm run verify:local`
2. **版本改动必须校验一致性** - 改 `package.json`、`package-lock.json`、`forge.config.mjs`、Electron 配置、`lime-rs/Cargo.toml` 或 App Server release manifest 时执行 `npm run verify:app-version`
3. **协议改动必须同步四侧** - Electron Desktop Host bridge / preload 白名单、App Server JSON-RPC 协议、前端 `safeInvoke(...)` / API 网关、`agentCommandCatalog`、`mockPriorityCommands` / `defaultMocks` 必须保持一致，并执行 `npm run test:contracts`；只有触碰 legacy desktop facade 时才额外检查 legacy host 注册，新增 current 能力不得把旧注册表作为事实源。生产路径禁止 mock：`safeInvoke` / `invoke` / Electron Host / App Server / GUI smoke 不能回退 `mockPriorityCommands`、`defaultMocks`、`invokeMockOnly` 或 mock backend；这些只允许测试夹具显式使用
4. **前端全量测试优先续跑和缩小范围** - `npm test` 已由 `scripts/run-vitest-smart.mjs` 分批记录状态到 `.lime/test/`；全量测试失败或被中断后，默认用 `npm run test:resume`、`npm test -- --from-batch N` 或 `npm test -- --only-batch N` 续跑，不从头重跑。局部改动优先用 `npm run test:related -- <files>`、`npm run test:changed -- <ref>` 和定向测试证明风险，再决定是否扩大到全量
5. **Lime 是 GUI 桌面产品** - 不能只以 `lint`、`typecheck`、单测通过作为“可交付”判断
6. **高风险 GUI 改动必须做最小冒烟** - 涉及 GUI 壳、DevBridge、Workspace、主路径时执行 `npm run verify:gui-smoke`
7. **Playwright 续测优先稳定桌面 Chrome 会话** - 真实交互验证优先复用已有 Lime 页签；需要新启浏览器时走持久化 Chrome 上下文，避免本地桌面出现自动化横幅或 `--no-sandbox` 安全横幅，细则见 `internal/aiprompts/playwright-e2e.md`
8. **用户可见 UI 改动必须补稳定回归** - 优先补现有 `*.test.tsx` 或 snapshot 断言
9. **测试用例必须迁到 current 事实源** - 新增或迁移测试默认覆盖 Electron Desktop Host bridge、App Server JSON-RPC、`src/lib/desktop-host/` mock 与 `packages/app-server-client`；legacy host / legacy mock path / legacy host 注册测试只允许证明 legacy facade 未回流，不得作为 GUI 产品可交付证据
10. **前端新代码先守住测试分层** - 新增或重写复杂 UI / hook 逻辑时，先抽到 View Model / projection / selector / reducer 并用 `*.unit.test.ts` 覆盖；`*.test.tsx` / component 测试只保留渲染、事件接线和少量关键回归。禁止把业务状态机、筛选/分组/格式化、运行时参数拼装等可纯化分支继续塞进 React 挂载测试；确实不能纯化时，必须在对应路线图或执行计划说明原因、风险层级和验证入口
11. **用户可见文案必须全球本地化** - 新增或改动的按钮、标题、空态、toast、confirm、prompt、placeholder、aria/title、错误提示、导出 Markdown / copy prompt / artifact title 等 presentation 文案，必须覆盖 Lime current 五语言 `zh-CN / zh-TW / en-US / ja-JP / ko-KR`；前端走 key-based resources，Rust / Electron host / App Server 导出走 locale copy service；禁止只做中文 / 英文双语兜底，除非路线图明确写出临时例外和退出条件
12. **配置与依赖改动要成组更新** - schema、校验器、消费者、文档、锁文件保持同步
13. **Rust 变更先小测后全量** - 先跑受影响 crate / 模块 / 定向测试，优先 `npm run test:rust:changed`、`npm run test:rust:related -- <paths...>`、`npm run test:rust:unit -- -p <crate> <filter>` 或 `npm run test:rust:integration -- -p <crate> --test <target>`；`changed/related` 会按 `lime-rs` 路径推导 workspace crate 并用 `cargo metadata` 扩展反向依赖，根 `Cargo.toml` / `Cargo.lock` 等 workspace 边界自动扩大到 `--workspace`，无法映射 crate 时必须 fail closed。只有跨 crate 协议、workspace 版本 / schema、发布最终门禁或定向覆盖不足时，才扩大到 `--workspace` / `npm run test:rust`。冷编译慢时优先复用 `lime-rs/target`、增量缓存和可选 `RUSTC_WRAPPER=sccache` / Nextest 环境能力，不用反复无差别全量重跑；新增模块尽量控制在 `500 LoC` 内，文件接近 `800 LoC` 时优先拆新模块；Rust 文件超过 `1000` 行时同样遵守基础约束中的代码体量边界
14. **Rust 构建必须走 workspace manifest** - 在仓库根运行 Rust 校验必须带 `--manifest-path "lime-rs/Cargo.toml"`，或先 `cd lime-rs`；禁止直接 `rustc lime-rs/src/*.rs` 编译 Lime 主 crate，避免绕过 workspace 依赖导致 `can't find crate for lime_*` 误报
15. **Harness Engine 只认单一事实源** - handoff / evidence / replay / analysis / review / GUI 统一消费 App Server `evidence/export` 与 `agentSession/*/export` current 导出链；旧 `agent_runtime_export_*` 只允许作为 retired guard / 历史 evidence / 迁移残留出现；`requestTelemetry` 需要按 `session/thread/turn` 真实关联导出，无匹配请求时输出空摘要，不再保留伪 `unlinked`

## 执行与路线图

1. **主线任务先重述目标** - 用户要求“对齐路线图 / 继续主线”时，先说明当前主目标、阶段和下一刀
2. **先补主缺口再磨细节** - 多阶段主线未到可用闭环前，优先做直接提高整体完成度的缺口；协议 polish、错误分类、额外 seam、边缘校验、文案润色、内部抽象等梢枝末节，只有在阻塞主路径、会造成假入口/假配置，或用户明确要求时才做
3. **下一刀必须按目标增量排序** - 选择下一步前先列出 1-3 个未完成主问题，并优先选“对整体目标完成度提升最大”的一项；不要因为当前文件顺手、测试容易、局部更完整，就继续做低杠杆小项
4. **每一刀都要可追踪** - 改动要么回挂到 `internal/roadmap/`，要么登记到 `internal/exec-plans/` 或技术债追踪
5. **清理不能替代交付** - 连续两轮主要在做治理减法后，下一轮优先回到未完成主线
6. **长任务必须落计划** - 超过一轮的实现、迁移、清理，写入 `internal/exec-plans/` 并持续更新进度日志
7. **主线冲突先清障，不保旧面** - current 规划与旧实现直接冲突时，先删或下线阻碍主线的旧页面、旧命名、旧命令、旧文档，再继续实现；不要为了“看起来兼容”保留双轨
8. **默认不为顺手问题偏航** - 已经选定本轮主线后，除非该问题直接阻塞当前交付、会让新改动变假配置/假入口，或用户明确要求，否则不要切去处理旁支优化、额外治理、零引用清理或“顺手再修一个”
9. **清理必须有主线收益句** - 任何治理/重构/删除动作，动手前都要能用一句话说明“它如何直接帮助当前主线交付”；如果说不出来，就记录为后续项而不是立即执行
10. **顺手项一次只收一刀** - 实现主线时即使发现多个周边问题，默认只处理其中最直接阻塞的一项；其余登记后立即回到主线，不串行深挖
11. **完成判定先看主线，再看周边** - 用户问“完成了么”时，先回答主线目标是否完成；周边清理、额外校验、可选优化必须单独标为“已做 / 未做”，不能混成“还差一点边角所以整体未完成”
12. **验证以证明交付为上限** - 校验应先覆盖当前改动的真实风险；在已经证明主线可交付后，不要因为还能继续跑更重检查，就无限追加验证并拖延收口
13. **开发任务结束必须给完成度百分比** - 非纯问答的开发任务收尾时，必须给“本轮完成度：X%”，并说明主线目标是否完成、验证情况、剩余缺口和下一刀；路线图 / 长任务 / 多阶段主线还要额外给“整体目标完成度：Y%”，并说明百分比口径

## 文档导航

- **文档中心**：`docs/README.md`
- **模块级工程导航**：`internal/aiprompts/README.md`
- **架构概览**：`internal/aiprompts/overview.md`
- **工程质量 / 校验**：`internal/aiprompts/quality-workflow.md`
- **UI 规范**：`internal/aiprompts/design-language.md`
- **Desktop Host / App Server 命令边界**：`internal/aiprompts/commands.md`
- **命令运行时**：`internal/aiprompts/command-runtime.md`
- **任务 / 子代理 taxonomy**：`internal/aiprompts/task-agent-taxonomy.md`
- **远程运行时**：`internal/aiprompts/remote-runtime.md`
- **记忆 / 压缩主链**：`internal/aiprompts/memory-compaction.md`
- **文件持久化主链**：`internal/aiprompts/persistence-map.md`
- **状态 / 历史 / 遥测主链**：`internal/aiprompts/state-history-telemetry.md`
- **任务分层 / 模型经济调度路线图**：`internal/roadmap/task/README.md`
- **治理与收口**：`internal/aiprompts/governance.md`
- **并行 Agent 协作**：`internal/aiprompts/parallel-agent-collaboration.md`
- **Harness Engine 治理**：`internal/aiprompts/harness-engine-governance.md`
- **Playwright / GUI 续测**：`internal/aiprompts/playwright-e2e.md`
- **计划与进度**：`internal/exec-plans/README.md`
- **技术债追踪**：`internal/exec-plans/tech-debt-tracker.md`
- **路线图**：`internal/roadmap/`
- **Codex Skills 索引**：`.codex/skills/README.md`

## 高频命令

```bash
npm run verify:local
npm run verify:local:full
npm run verify:gui-smoke
npm run smoke:electron
npm run typecheck:electron
npm run bridge:health -- --timeout-ms 120000
npm run test:contracts
npm run test:resume
npm run test:related -- <files>
npm run test:changed -- <ref>
npm run test:rust:unit
npm run test:rust:changed
npm run test:rust:related -- <paths...>
npm run test:rust:layers:stats
npm run governance:legacy-report
npm run electron:dev
cargo test --manifest-path "lime-rs/Cargo.toml"
```

## 维护规则

1. 改仓库级规则时，同时更新本文件和对应 `internal/` 入口；对外文档站规则同步更新 `docs/README.md`
2. 新增长期流程优先落到 `internal/`；高频复用后再沉淀为 `.codex/skills/`
3. 如果某条规则已经能被 linter、结构测试或 CI 机械约束，就把约束写进工具链，而不是继续往本文件堆说明
