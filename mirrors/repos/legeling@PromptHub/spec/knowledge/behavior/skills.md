# Skills Spec

## Purpose

本规范定义 PromptHub Skill 体系的稳定真相源，包括 Skill 文件格式、仓库同步、版本管理与相关设计入口。

## Stable Requirements

### 1. Skill Package Contract

- Skill 是目录级 package；`SKILL.md` 是 package 内的必需入口文件，不是 Skill 的完整边界。
- 只有一个 `SKILL.md` 的 Skill 仍然合法，但它仍然必须被视为 `<skill-root>/SKILL.md` 形式的目录包。
- 导入、商店安装、Git/Gitea 安装、本地目录安装、同步、导出、项目分发和平台分发必须保留整个 Skill 目录树，除非命中显式忽略规则（例如 `.git` 与 `.prompthub`）。
- Skill package fingerprint 必须使用显式忽略规则，而不是笼统忽略所有隐藏文件。PromptHub 内部目录（`.prompthub/`）、VCS 元数据、依赖目录、缓存、日志、临时文件、本地环境密钥（例如 `.env` / `.env.local`）、虚拟环境与运行态 pid/socket 文件不参与 fingerprint；可分发模板文件（例如 `.env.example` / `.env.sample` / `.env.template`）仍然参与 fingerprint。
- 仅写入 `SKILL.md` 内容的 API 只适用于新建 UI 原生 Skill 或编辑入口文件；不得作为已有包来源导入/安装的最终持久化路径。

### 1.1 Skill File Contract

- Skill 采用 `SKILL.md` 文件与 YAML frontmatter。
- `name` 为必填字段，且必须符合小写短横线命名规则。
- Desktop、CLI、Web、市场源适配器与 Skill 详情展示必须复用 `packages/core` 所有的标准 YAML parser/serializer，不得各自维护逐行切分或正则提取的 frontmatter 子集。
- 从 HTML、API payload 或其他外层文档提取嵌入式 `SKILL.md` 时，必须保留 YAML 前导缩进后再调用共享 parser。
- Frontmatter 必须支持 YAML literal/folded block scalar、quoted scalar、flow collection 与 nested map，并识别 `license`、`compatibility`、`metadata`、`allowed-tools` 等 Agent Skills 标准可选字段。
- 元数据编辑触发 `SKILL.md` 重写时，必须保留 PromptHub 当前不编辑的标准字段与未知扩展字段；允许规范化 YAML 表达形式，但不得改变字段值或静默删除字段。
- Malformed YAML、非 object root、自定义 tag、重复 key 和超限 alias expansion 必须明确解析失败，不得返回部分可信元数据。
- Skill 元数据与正文分工明确：UI 展示元数据与版本信息由数据库维护，说明正文与指令正文由 `SKILL.md` 持有。

### 2. Sync Contract

- PromptHub 必须支持 DB 与本地 Skill 仓库之间的双向同步。
- UI 编辑元数据后，需要同步 frontmatter；文件系统变更后，需要同步回 DB。
- My Skills 的本地 package source 有两种合法形态：
  - 复制导入：`local_repo_path` 指向 PromptHub 托管 package，托管 package 是 My Skills 的内容真相源。
  - 链接导入：`local_repo_path` 指向用户选择的外部本地 Skill 目录，外部目录是 My Skills 的内容真相源。
- 链接导入的 My Skills 文件浏览、读取、编辑、同步与 fingerprint 刷新必须使用该外部目录；不得在解析路径时静默复制为托管 package。
- 删除链接导入的 My Skills 记录时，只能删除 PromptHub 记录和 PromptHub 拥有的分发链接；不得删除外部源目录。
- 通过 backup/restore 恢复 Skill 时，`local_repo_path` 属于机器本地的写入目标，不能作为可移植数据回放。恢复必须从备份的内容和文件树重建当前机器的 PromptHub 托管 package，同时保留来源标识、来源地址和 package 对账基线。
- Desktop 自部署 Web 同步必须在发送前移除 `local_repo_path` 以及非 HTTP(S) 的 `source_url`、`content_url` 和本地 icon 路径；Skill 正文、文件树和可移植的远程来源元数据必须保留。拉取合并不能只按数据库 ID 判断同一 Skill，必须优先按 `source_id`、package/content fingerprint 或旧记录规范化名称对齐，并同步重映射版本与文件快照，避免重复名称和孤儿文件写入。

### 2.1 Source Update Reconciliation Contract

- My Skills 的来源更新必须按三方对账处理：`B` 是上次来源安装基线，`L` 是当前本地 package，`R` 是当前来源 package。
- 目录级 Skill 必须优先使用 package fingerprint 对账。`directory_fingerprint` 表示当前本地 package，`installed_directory_fingerprint` 表示上次来源安装基线，`fingerprint_algorithm` 记录算法版本。
- v1 durable package fingerprint 使用 `skill-package-sha256-v1`；桌面主进程、CLI 和 renderer 远程包指纹解析不得把旧版 stable-text 目录摘要标记为该算法。Git tree/API 中只有 blob hash、没有包文件内容时，不得直接产出 durable `directory_fingerprint`；必须留空等待 clone/materialize 后按 v1 计算，或在未来能取得文件内容时按 v1 manifest 计算。旧版只记录 `SKILL.md` hash 的安装，只能在旧 hash 证明本地与远程入口一致时静默升级基线，否则进入无法确定历史的状态。
- 兼容旧版安装时，如果缺少 `installed_directory_fingerprint` 但旧 `installed_content_hash` 与远程入口 hash 一致，来源检查可以把当前本地 package fingerprint 作为可推断基线，再判断远程 package 是否变化；这只用于维持旧安装的资源更新检测，不允许绕过 `baseline-missing` 的冲突保护。
- 来源更新检查必须通过共享的 `B/L/R` 对账逻辑产生 `localModified`、`remoteChanged` 和状态，UI/store 不得各自手写不一致的状态机。
- 来源更新状态限定为 `no-source`、`source-unavailable`、`baseline-missing`、`up-to-date`、`update-available`、`local-modified`、`conflict`。`source-moved` 和 `downstream-stale` 不属于 v1 来源更新主状态。
- `downstream-stale` 属于 Project/Agent 分发拓扑数据，只能作为辅助扫描结果或 `hasStaleTargets` / `staleTargets` 类字段暴露，不得污染 My Skills 来源对账状态机。
- `local-linked` 外部目录是用户外部文件夹的内容真相源。v1 不允许直接把远程来源更新覆盖进外部链接目录；UI 必须引导用户转换为 PromptHub 托管副本或手动更新外部目录。
- 来源解析必须先归类为明确 adapter kind：`remote-store`、`remote-git`、`remote-zip`、`content-url`、`local-linked` 或 `managed-copy`。raw `content-url` 是单文件来源，安装基线与远程 package fingerprint 必须等于该 `SKILL.md` 的内容 hash，不得信任 registry 中陈旧或外部提供的目录指纹。
- 非本地远程来源更新必须先完成内容落盘，再写入 DB 元数据和来源基线。远程 Git/Zip package 更新必须先通过暂存/安全检查/落盘流程；raw `content-url` 更新在单文件写入前也必须运行安全扫描，且只有 `SKILL.md` 写入成功后才允许刷新基线。任何远程内容落盘失败都不得提前把 DB 标记为已更新。
- 远程 Git/Zip 更新的本地 package 结构、路径穿越与禁止模式预检始终启用；可选 AI 扫描与本地预检的结果必须在首次人工复核前合并。`blocked`、路径穿越、无效 package 结构和不安全 archive 不可绕过；`high-risk` 必须返回结构化 findings 供用户复核，不得退化为仅含错误字符串的 IPC 失败。
- `high-risk` 更新批准必须绑定本次暂存 package 的 SHA-256 fingerprint，并在重试时重新暂存、扫描与比对；内容变化后旧批准失效。复核未产生内容变更时不得留下多余版本快照。
- 用户可显式信任一个确切 Skill 来源，作用域必须是 `source_id` 或规范化的 repo/branch/directory，不得扩大为整个 Git/Gitea host。信任只允许扫描后的 fingerprint 自动重试，不跳过扫描；首次信任只能在人工批准成功后持久化，并且必须可在设置中撤销。持久化来源键不得包含 URL userinfo、query 或 fragment。
- 来源地址验证必须有超时边界。对于已经暂存并完成本地 package 扫描的更新，无法解析的自建来源只能产生可见的 provenance warning，不得令更新请求长期挂起；尚未物化本地 package 的内部/不可验证来源继续采用严格阻断策略。
- 如果 raw `content-url` 已写入但最终 DB 基线写入失败，必须通过更新前创建的版本快照回滚，避免本地文件内容与数据库来源基线长期不一致。
- PromptHub 托管 repo 替换必须使用 staging/backup swap；复制、校验或 sidecar 写入失败时，应保留上一个可用 managed repo。
- 来源检查失败时，PromptHub 应保留本地内容，返回 `source-unavailable`，并只保存净化后的 `source_last_error` 摘要，避免把 URL userinfo、token、query secret、堆栈换行等细节暴露到持久化错误字段。
- Cloud Store 的安装与更新必须先读取已发布 package，展示版本、文件/内容差异和安全扫描结果，等待用户明确确认后才写入本地；“检查更新”本身不得直接覆盖 Skill。
- Cloud release 的 `store-package-sha256-v1` 只用于远程交付 intent 的版本期望；桌面本地 package 仍必须计算并持久化 `skill-package-sha256-v1`，不得把两种 fingerprint 直接比较或互相标记。
- Cloud 多文件 package 写入失败时必须恢复已写入文件并清理新建文件；安装失败不得留下半成品 Skill，更新失败不得提前刷新来源基线。

### 3. Versioning Contract

- Skill 版本历史属于稳定产品能力。
- 版本快照、恢复、差异对比与平台分发属于 Skill 域内关键流程。

### 3.1 Platform Distribution Feedback Contract

- 当用户选择符号链接方式分发 Skill 到平台目录时，PromptHub 必须明确区分“真实 symlink 成功”和“因权限/文件系统限制而回退为 copy 安装”。
- 如果主进程回退为 copy 安装，渲染层必须收到结构化结果，并向用户显示包含受影响平台与原因的警告提示。
- 回退 copy 安装仍属于成功分发，但不得伪装成普通 symlink 成功。

### 3.2 Project-Local Distribution Contract

- PromptHub 必须支持将项目级 Skill 直接分发到当前项目内的本地目录，而不强制要求先纳入 `My Skills`。
- PromptHub CLI 必须支持从现有 `My Skills` 中选择一个 Skill，并直接安装到当前项目的本地 Skill 目录，而不强制要求先在桌面端登记项目。
- 项目级分发默认目标为当前项目的 `.agents/skills`，并允许用户额外选择多个目标目录。
- 项目级分发必须复制整个 Skill 目录到 `<target>/<skill-name>/`，而不是只写单个 `SKILL.md` 文件；这是全局 Skill package contract 在项目分发场景下的具体要求。

### 3.3 Agent Platform Visibility Contract

- Skill 平台分发的可见目标由“已检测到的平台”与“用户显式配置的平台”共同决定。
- 已启用的 custom Agent 和存在用户覆盖配置的 built-in Agent 必须作为可分发目标显示，即使其根目录当前还不存在；安装流程负责创建缺失目录。
- `disabledPlatformIds` 始终优先于检测和显式配置，用于隐藏用户不希望看到的平台。
- 平台检测仍用于默认 built-in 平台降噪和状态提示，但不得单独作为分发目标可见性的唯一门禁。

### 4. Translation Contract

- Skill 详情页的 AI 翻译结果属于可恢复的本地用户状态。
- 翻译结果不得改写原始 `SKILL.md`，应作为 sidecar 文档保存在 Skill 本地 repo 的 `.prompthub/translations/` 目录下。
- 翻译是否仍然有效必须基于当前 `SKILL.md` 内容 fingerprint 判断，而不是仅凭页面内存态。
- 当 `SKILL.md` 变化导致旧译文失效时，UI 必须回退原文并提供明确的重翻入口。
- `.prompthub/` 目录属于 PromptHub 内部文件空间，默认不参与普通文件树、导出和分发流程。

### 5. Stable Internal Sources

- Skill 体系设计见 `spec/knowledge/structure/skill-system-design.md` 与 `spec/knowledge/structure/skill-system-design-zh.md`
- Skill 商店需求见 `spec/knowledge/structure/skill-store-requirements.md` 与 `spec/knowledge/structure/skill-store-requirements-zh.md`
- 历史测试演进与状态记录保存在 `spec/changes/legacy/docs-08-todo/`

## Stable Scenarios

### Scenario: Defining a new Skill workflow

When Skill behavior changes materially:

- contributors create a delta spec under `spec/changes/active/<change-key>/specs/skills/spec.md`
- they sync durable behavior back into this stable spec after implementation

### Scenario: Persisting translated Skill content

When a user has already translated a Skill detail page:

- reopening the same Skill with unchanged `SKILL.md` content restores the saved sidecar translation by default
- changing `SKILL.md` content invalidates the old translation and requires a fresh translation before it is shown again

### Scenario: Recovering Skill knowledge

When historical Skill plans or test rounds are still useful but no longer current source of truth:

- they remain readable under `spec/changes/legacy/`
- they are not deleted or replaced with git-history placeholders
