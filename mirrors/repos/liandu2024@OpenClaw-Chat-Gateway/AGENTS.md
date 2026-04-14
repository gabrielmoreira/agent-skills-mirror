# AGENTS.md

## 项目概述
- OpenClaw Chat Gateway 是 OpenClaw 的 Web 客户端 / 控制台。
- 运行前提是已安装 OpenClaw 的 Linux 主机；README 明确要求原生安装，而非 Docker。
- 仓库采用前后端分离结构：前端为 React + Vite，后端为 Express + TypeScript。
- 生产模式下由后端服务 `frontend/dist`，同时提供 `/api`、`/uploads`、`/openclaw` 等接口。
- 运行数据保存在 `$HOME/$CLAWUI_DATA_DIR`；后端还会直接读写 `$HOME/.openclaw`。

## 仓库结构
- `backend/`: 后端服务、OpenClaw gateway 客户端、SQLite、agent/session/group/file 管理。
- `frontend/`: Web UI，包含单聊、群聊、设置、模型管理、文件预览等功能。
- `docs/`: 项目截图和文档资源。
- `install.sh`, `deploy-release.sh`, `clawui.service`: 安装与部署脚本。

## 启动 / build / test / lint 命令
- `npm run dev`: 同时启动前后端开发环境。
- `cd backend && npm run dev`: 启动后端开发服务。
- `cd frontend && npm run dev`: 启动前端开发服务。
- `npm run build`: 同时构建前后端。
- `npm run release`: 构建后启动 release 预览流程。
- `./deploy-release.sh [port]`: 安装依赖、构建并部署 user-level systemd 服务。
- `npm run test`: 运行仓库级最小自动检查；当前仅覆盖前后端 TypeScript 类型检查，不等于完整业务测试。
- `cd backend && npm run test`: 后端 TypeScript 类型检查。
- `cd frontend && npm run test`: 前端 TypeScript 类型检查。
- `lint`: Unknown。未找到 root / backend / frontend 的标准 lint 命令或 lint 配置。

## 工程约定
- 保持当前前后端边界：前端通过 `/api`、`/uploads`、`/openclaw` 与后端交互。
- 保持前端产物兼容后端静态托管，不要假设生产环境一定存在独立前端服务。
- 开发环境前端端口固定为 `3105`；启动、调试、文档和协作过程中都应保持一致，不要随意变更。
- 版本号唯一真值源必须是仓库根 `package.json` 的 `version`；前端、后端、构建产物元数据、发布脚本和 GitHub Release 只能从这里读取版本，`package-lock.json` 等派生文件不得作为人工维护的版本真值源。
- 修改升级链路、`deploy-release.sh`、`update.sh`、OpenClaw runtime 收敛脚本或升级状态机时，“升级成功”不得只以 build 完成为准；必须同时包含 OpenClaw runtime 收敛成功、device repair 收敛成功、browser runtime 验收成功，才允许进入 `complete` / `update_succeeded`。
- 聊天页中的 `loadHistory` 只用于切换单聊 / 群聊后的首屏初始化，职责是加载“当前上下文最新一页”；不要把它当作发送完成或 `regenerate` 完成后的通用刷新入口。
- 聊天历史分页统一使用基于自增消息 ID 的 cursor 协议：`beforeId + limit`；不要改成 `offset` 分页，也不要在单聊和群聊里各自维护不同协议。
- 发送完成或 `regenerate` 完成后，应继续在当前分页状态内通过 append / patch / ID 替换收敛消息，不要重新引入整页 reload；否则会清掉已加载的旧页。
- 群聊多 agent live 场景下，assistant 消息一旦已展开显示，不应因为后续其他 agent 开始发言而自动收起，造成“正文假性缩短”；涉及 `MessageBubble`、`ProcessStepBlock`、`isLatest` 或群聊消息渲染逻辑的修改时，必须显式检查这一点。
- 新增模块的风格和样式必须参考现有模块；颜色、字号、按钮尺寸、边框、间距、交互反馈等保持一致，不要单独做一套新视觉。
- 全局不要使用阴影；需要层级或分隔时，优先使用浅灰色边框。
- 不要保留死代码。
- 不要把对用户有意义的参数、阈值、开关、配置做成隐藏实现；应优先提供界面入口让用户配置。
- 涉及 `~/.openclaw`、agent provisioning、reset/delete 路由、任意文件下载/预览的改动，必须先说明影响范围、风险点和验证方式，再实施修改。

## 国际化要求
- 所有新增的用户可见功能，默认必须同时支持 `zh-CN`、`zh-TW`、`en`。
- 不要在组件中新增硬编码用户可见文案。
- 所有新增文案必须进入语言资源文件，不得只写单语版本。
- 新增功能涉及按钮、标题、提示、空状态、表单校验、错误提示、成功提示、弹窗文案、菜单项等时，必须同步补齐三语文案。
- 新增系统消息或接口错误时，优先使用结构化 `messageCode` / `errorCode`；前端负责本地化主句，诊断信息使用 `rawDetail` / `errorDetail` 独立展示。
- 若本轮任务新增功能但未补齐三语支持，任务不算完成；若确实无法完成，必须明确标记 `TODO` 并说明原因。

## 禁止事项
- 不要假设该仓库支持 Docker 部署。
- 不要给新模块引入与现有系统不一致的 UI 风格。
- 不要全局使用阴影。
- 不要新增死代码、废弃分支或只留不用的参数。
- 不要新增没有界面入口的用户配置。
- 不要使用 `alert` 弹窗。
- 不要把带有机器路径硬编码的脚本当作通用工作流。
- 不要声称仓库已有 CI、lint 或自动化测试覆盖，除非仓库内实际存在证据。

## 完成标准
- 至少运行与改动范围对应的构建命令；跨前后端改动时优先运行 `npm run build`。
- 若改动影响聊天、群聊、文件预览/上传、agent 管理或 OpenClaw 集成，应在真实 OpenClaw Linux 主机上验证；无法验证时标记 `TODO`。
- 若改动影响 `MessageBubble`、`ProcessStepBlock`、`isLatest`、群聊 live 消息合并或群聊消息渲染展开/收起逻辑，必须做真实页面的多 agent 协作群 live 回归验证，并明确记录每条 assistant 消息是否出现 `long -> short` 回退。
- 若改动影响单聊后端收尾链路，例如 `onFinal`、`scheduleCompletionProbe`、`probeCompletion`、`finalizeRun`，必须逐项对账并验证 `JSONL` 原始终态、`chat.history`、`chat_messages`、`/api/history/:sessionId`、真实页面 `DOM` 五处一致，且页面最终不能停在半句位置。
- 发布前必须显式校验以下四项一致：根 `package.json.version`、目标 `git tag`、GitHub Release、实际发布 commit；若其中任一项不一致，不得把该版本视为已完成发布。
- 仓库没有标准自动化保障时，用 `Unknown` 或 `TODO` 明确说明，不要猜测。
- 新增配置项时，用户应可在界面中查看和配置；若暂时做不到，标记 `TODO` 并说明原因。
- 只有在相关命令仍可执行、且剩余运行时风险已写明时，任务才算完成。

## 发布关键步骤
- 本仓库正式发布依赖两部分同时成功：`git tag` 推送成功，以及 GitHub Actions `Release Sync` 成功创建 GitHub Release；只有 tag 没有 Release，不算发布完成。
- 发布前先把根 `package.json.version` 改到目标版本；`package-lock.json` 作为派生文件同步更新，但版本真值源仍然只有根 `package.json`。
- 发布前必须新增对应的 release notes 文件，命名固定为 `docs/release-notes-vX.Y.Z.md`；内容可精简，但文件必须存在。GitHub Actions 会读取这个文件创建 Release，缺失时会导致 tag 已推送但 Release 失败。
- 发布顺序固定为：更新版本号 -> 新增 `docs/release-notes-vX.Y.Z.md` -> 运行必要的 `npm run test` / `npm run build` -> 提交到 `main` -> 推送 `main` -> 执行 `npm run release:publish` 推送 tag。
- `npm run release:publish` 只负责创建并推送 tag；GitHub Release 由 `.github/workflows/release-sync.yml` 在 tag push 后自动创建，不要每次都重新寻找手工发布方法。
- 发布后必须显式核对四项一致：根 `package.json.version`、远端 `main` 对应 commit、远端 tag `vX.Y.Z^{}`、GitHub Release 页面；四项不一致时，不得宣称版本已发布完成。
- 若 tag 已推送但 GitHub Release 缺失，第一检查项就是对应的 `docs/release-notes-vX.Y.Z.md` 是否随 tag 所指 commit 一起存在；如果缺失，应补文件、提交、将 tag 重新指向新提交并重新推送，再等待 `Release Sync` 重跑成功。

## 已知残余风险
- 同一 `sessionId` 叠发多条请求时，旧 run 的 `cleanup` 仍可能影响新 run 的活动状态、SSE 附着或最终消息落库；这是独立的并发风险，不能与已解决的“单聊半句截断”问题混为同一根因，也不能按“长文本被短文本覆盖”处理。
