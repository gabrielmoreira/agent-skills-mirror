# 开发路线图

路线图可能会经常变更，如果有强烈的建议，可以在 [issue](https://github.com/xerrors/Yuxi/issues) 中提。

日志添加规范（For Agent）:

- 同一版本的多次功能更新时，应以功能为单位进行更新，比如之前添加了 A 功能的更新，在后续的更新中修复了因 A 功能引入的 bug，那么这个修复说明应该和 A 功能描述放在一起，而不是新增一条修复记录，功能更新同理。

### 看板

- Langfuse 增加 self-host 模式支持，补齐私有化部署与配置说明（已支持 cloud，待调试）
- 检索测试中，添加问答
- 集成 Memory，基于 deepagents 的文件后端实现，需要考虑定位
- Yuxi-cli 相关的功能，放在后续版本中实现（不是类似于编程助手，而是管理平台的工，等各个 router 接口优化之后）
- 完善测试基准自动生成功能，目前的实现过于简单，无法覆盖实际需求
- 完善 Skills 的环境变量注入
- 拓宽检索的知识源，统一多知识源（channel），目前已知知识库/知识图谱/网页，可拓展：个人知识库、数据库、历史对话等
    - 前置任务，多知识库并行检索（扩展 query_kb）
    - 新增 query_keywords 工具，专门用于基于关键词命中的排序，也结合词频（和 BM25 的区别？）
- 调研将当前知识库映射为虚拟文件系统工具的可行性，先明确文件树映射、权限边界、内容读取与 Agent 工具调用形态，再决定是否实现
- 参考 AgenticRAG 方案扩展当前 Search 工具：基于知识库工具返回的 resource_id/file_id 改进 Search 返回递增文件序列 ID，完善 Find 与 Open 能力；Summary 暂缓
- 评估，基于 Agent 的评估，这里应该是结合 Langfuse 实现

### Bugs
- 目前的知识库的图片存在公开访问风险

### BREAKING CHANGE（不兼容变更，0.7 版本）
- Provider 与模型配置收敛：移除旧版 v1 模型配置与 Ollama 支持，运行时模型统一使用 `provider_id:model_id` 与独立 provider 模块；自定义 provider 实现逻辑从文件移动到数据库，并从 config 文件迁移到 provider 模块。
- 智能体运行时语义收敛：用户可见的 `AgentConfig` 收敛为数据库持久化的一级 `Agent`，内置 Python Agent 改为智能体后端；聊天、运行任务、恢复审批和文件预览均从线程绑定的 Agent 解析运行时上下文，前端只提交 `agent_id`。
- 知识库能力边界收敛：移除 Upload 与 LightRAG 知识库/图谱能力，知识库类型收敛为 Milvus 与只读连接器；知识库 API 统一使用 `/{db_id}/xxx` 形式，并整合 mindmap / eval 等子接口。
- Agent 资源默认选择与权限过滤：未显式配置工具、知识库、MCP、Skills 时默认启用当前用户可访问/可用的全部资源，子智能体默认不启用，显式保存空列表仍表示不启用对应资源；Agent 创建前统一完成最终资源权限过滤、知识库 `db_id` 可见范围派生和 Skill prompt/readable 依赖闭包派生。
- Skill 安装与权限模型收敛：Skill 元数据使用 `source_type/share_config/enabled` 表达来源、生效范围与启用状态；内置 Skill 启动或同步时自动写入数据库并默认全局启用，上传和远程添加统一改为解析草稿后确认安装，不保留旧直接安装兼容路径。
- 历史兼容层精简：移除 sandbox provisioner `local` 后端别名、ask_user_question 单问题旧协议、JWT 历史默认密钥特殊判断、内置 Skill `SKILLS.md` 文件名回退、运行事件数字 seq 兼容和前端旧字段回退。
- 用户身份命名收敛：原业务登录标识统一改为 `uid`，Agent/LangGraph runtime、conversation、agent_run、sandbox 路径和前端用户态均使用字符串 `uid`；`user_id` 仅保留给外部响应中的数值 `users.id` 或真实外键场景。

## 版本记录

### 0.7.0 开发记录

<!-- 0.7.0 的内容请放在这里 -->
- 收敛 MCP 创建与编辑入口：前端移除整段配置文本入口和模式切换器，仅保留表单字段提交；后端 MCP 创建/更新请求拒绝额外配置字段，避免绕过表单约束。
- 调整内置 MCP 默认项：移除 `sequentialthinking` 的系统内置同步，启动同步时清理历史系统内置记录，保留用户手动创建的同名 MCP。
- 图片生成能力迁移为 Skill：Qwen-Image 从内置 Python 生成工具迁移到内置 Skill `image-gen`，模型调用与图片下载在 Agent 沙盒中完成，生成结果保存到 outputs 并通过 `present_artifacts` 展示，为多图片生成模型接入复用同一产物展示链路。
- 降低知识库路由与工具模块复杂度：示例问题生成迁移到知识库 utils，文件上传统一 100 MB 限制，URL 预处理入库路径与旧 `content_type=url` 行为收敛，并修复 uid、导出 MIME 与异常透传等路由问题。
- 重构智能体配置语义：用户可见的 `AgentConfig` 收敛为数据库持久化的一级 `Agent`，内置 Python Agent 改为智能体后端；新增 `/api/agent` 管理与运行接口，聊天、运行任务、恢复审批和文件预览均从线程绑定的 Agent 解析运行时上下文，前端只提交 `agent_id`，并在模型配置页新增“智能体”管理页签。
- 删除 Upload 与 LightRAG 图谱/知识库能力：知识库类型收敛为 Milvus 与 Dify，只保留 Milvus 知识库内图谱构建/展示/检索，移除独立 `/graph` 页面和默认上传图谱工具。
- 收敛只读知识源连接器：新增 `ReadOnlyConnectors` 基类，Dify 改为声明自身创建参数与校验规则，新增 Notion Data Source 只读知识库并支持 Search/Find/Open；知识库类型接口返回创建参数 schema，前端新建表单按类型动态渲染非 Milvus 配置并统一保存到 `additional_params`。
- 新增知识库 Chunk 持久化：Milvus 知识库索引/更新流程会将 chunks 双写到 PostgreSQL `knowledge_chunks` 表与 Milvus，文件内容查看优先查询 PostgreSQL，并为位置信息、图谱实体关联、标签和抽取结果预留结构化字段。
- 完善 Milvus 知识库图谱构建：修复 Chunk 图谱写入返回值、Neo4j 同步写入阻塞事件循环、重复构建任务竞态、图谱查询提前终止、Neo4j 连接复用、LLM 抽取超时重试和前端错误详情展示等问题；图谱构建会将 entity/triple 本体与 chunk 引用写入 PostgreSQL，并为唯一 entity/triple 建立 Milvus 语义索引，单文件删除时同步清理图谱引用和孤儿向量。
- 优化图谱抽取器配置：未配置时在图谱中心展示配置入口，抽取方案收敛为 LLM，前端仅保留“更多拓展中”占位；LLM 抽取器使用固定 Prompt + 自定义 Schema，并支持模型参数与并发队列数；已配置后允许修改参数并提示重置重抽风险。修复上传并入库新文件时旧内存 metadata 覆盖数据库图谱配置的问题。
- 新增 Milvus 图谱检索链路：Query 可召回图谱实体和三元组，结合 Chunk 命中实体构造 seed entity，读取 Neo4j 2-hop 子图后用 igraph 执行 PPR，最终以 Chunk 为产物并通过 RRF 与原 Chunk 召回融合；检索配置改为 dataclass 元数据生成，支持 `depend_on` 控制重排序和图检索参数展示。
- 收紧用户管理部门隔离：普通管理员创建用户时固定归属本部门，用户列表、访问选项、详情、更新和删除接口均限制在本部门范围内。
- 调整 Agent 资源默认选择与运行时上下文：未显式配置工具、知识库、MCP、Skills 时默认启用当前用户可访问/可用的全部资源，子智能体默认不启用，显式保存空列表仍表示不启用对应资源；Agent 创建前统一完成最终资源权限过滤、知识库 `db_id` 可见范围派生和 Skill prompt/readable 依赖闭包派生，聊天运行时与文件系统预览复用同一结果。
- 重构 Skills 权限与安装流程：Skill 增加 `source_type/share_config/enabled`，内置 Skill 作为启动同步入库的全局资源，不再保留前端安装/更新状态，支持启停但不允许删除；上传和远程添加统一为解析草稿后确认生效范围，安装 slug 优先读取 `SKILL.md` 的 `slug` 字段并保留 `name` 展示名，压缩包名称不参与 slug 校验；管理端新增推荐 Skill 分组，未安装时可从卡片 `+` 直接拉取 ModelScope 来源并进入安装草稿确认，上传入口补充安装文档链接，文档补充 ModelScope 单个 Skill 与合集安装说明；管理端支持编辑生效范围与启停；Agent 运行时按当前用户可访问 Skills 派生 prompt/readable 依赖闭包并限制挂载/激活，Skills prompt 改为模型请求级注入以避免污染 runtime context；主智能体恢复 `install_skill` 工具，允许当前用户安装私有 Skill 并激活当前会话，子智能体配置和运行态均禁用该工具。
- 精简历史兼容层：移除 sandbox provisioner `local` 后端别名、ask_user_question 单问题旧协议、JWT 历史默认密钥特殊判断、内置 Skill `SKILLS.md` 文件名回退、运行事件数字 seq 兼容和前端若干旧字段回退。
- 重构知识库共享权限：`share_config` 改为全局共享、部门共享、指定人可访问三档，部门共享必须包含当前用户部门，指定人可访问必须包含当前用户，并补充权限过滤测试。
- 移除知识库沙盒文件系统映射：不再通过 `/home/gem/kbs` 暴露知识库文件树，Agent 继续使用 `query_kb` 与 `open_kb_document` 访问知识库内容。
- 规范 Agent 知识库 Search/Find/Open 工具协议：`resource_id` 统一表示知识库 `kb_id`，Search 返回结构化 `resource_id/file_id/chunk` 结果，新增 `find_kb_document` 在已知文件内做关键词或正则定位，Open 默认窗口扩大到 1800 行。
- 收敛知识库分块配置：分块预设仅表达策略选择，通用分块参数统一通过 `chunk_parser_config` 传递；移除 `chunk_size`、`chunk_overlap`、`qa_separator` 等旧 root 字段兼容。
- 收敛知识库文件解析参数：文件级 `processing_params` 统一保存 `ocr_engine` 与 `ocr_engine_config`，解析阶段直接使用该结构并保留分块参数快照。
- 修复知识库文件大小显示为 0 的问题：文件上传时 `file_sizes` 参数未正确传播或历史数据缺失导致 DB 中 `file_size` 为 `None`；新增 `MinIOClient.stat_file/astat_file` 获取文件大小方法，`add_file_record` 在 `size` 缺失时从 MinIO 回补，`_load_metadata` 加载元数据后自动为缺少 `size` 的文件从 MinIO 补全并持久化。
- 优化评估基准自动生成：生成任务支持配置队列并发数，默认 10，范围 1-20。
- 重梳理知识库评估存储：评估数据集、题目、评估运行和逐题结果统一入库，JSONL 仅作为导入/导出格式；后端和前端 API 统一使用 dataset/run 语义；评估运行支持用户命名，历史记录按名称展示，综合评分只聚合检索指标。
- 扩展知识库上传来源：添加“从工作区上传”模式，后端将当前用户工作区文件预处理上传到 MinIO，前端沿用现有 `addDocuments` 入库链路提交 MinIO URL、内容哈希和文件大小。
- 重构知识库详情页布局：`DatabaseInfo` 改为顶部详情 header + 左侧功能 tab 侧边栏 + 右侧内容区，Milvus 默认进入文件管理，并将检索测试、知识图谱、知识导图、检索配置、RAG 评估和评估基准统一纳入侧边栏导航；只读连接器保留检索测试与检索配置。
- 整合知识导图接口：移除独立 mindmap router 与前端 API 模块，思维导图生成、查询和文件列表接口统一收敛到知识库 API 下。
- 收敛独立模型配置模块运行时：运行时 chat / embedding / rerank 均统一从 provider 模块与模型缓存读取 `provider_id:model_id`；旧版静态模型配置、v1 slash spec、旧模型列表接口和 Ollama 适配已移除；内置 provider 模板补充 XiaomiMiMo、XiaomiMiMo Token Plan CN 与 Kimi Code（`kimi-for-coding`）。
- 调整智能体配置归属与字段权限：`AgentConfig` 从部门共享改为按 `uid` 隔离，所有登录用户可管理自己的配置；`BaseContext` 支持字段级 `auth` 元数据，后端按用户角色过滤可见与可保存的配置项。
- 新增用户级沙盒环境变量：增加 `agent_envs` 表与 `/api/user/agent-env` 接口，设置面板支持当前用户维护 Agent 沙盒环境变量；创建新沙盒时与全局 `sandbox.env` 合并注入，用户变量优先。
- 收敛用户身份命名：原业务登录标识统一改为 `uid`，Agent/LangGraph runtime、conversation、agent_run、sandbox 路径和前端用户态均使用字符串 `uid`；`user_id` 仅保留给外部响应中的数值 `users.id` 或真实外键场景。
- 工作区知识库分类显示：知识库侧边栏按创建者分组为“我的知识库”和“共享知识库”，自己创建的知识库显示在“我的知识库”下，非自己创建的显示在“共享知识库”下；`knowledge_bases` 表新增 `created_by` 字段记录创建者 uid。
- 工作区文件上传支持多选：`/workspace/upload` 与 Viewer 工作区上传统一使用 `files` 多文件字段，一次最多上传 50 个文件，批量上传失败时清理本次已写入文件。
- 聊天附件新增 MinIO tmp 临时上传、可选 PDF/图片解析、确认后加入线程附件的流程；前端改为弹窗内上传、解析与确认。
- 标准化 Agent run/SSE 执行链路：run 创建时持久化输入消息并提交后入队，worker 统一写入 Redis Stream envelope，SSE 输出 `event/data/id`、心跳注释、`Last-Event-ID` 回放和终止 `end` 事件；前端强制使用 run API 并支持 ask_user_question 中断后以 resume run 恢复；事件 envelope 构造收敛到统一 helper，前端优先使用 envelope 一级 `thread_id` 路由。
- 收敛后端模块边界：文档解析从 `plugins.parser` 移动到 `knowledge.parser`，内容审查从 `plugins.guard` 移动到 `services.guard`。
- 收敛文件服务边界：文件预览判断抽为独立服务，Viewer 文件系统的 workspace 分支复用用户 workspace 服务，线程运行时上下文解析从泛化 `filesystem_service` 拆出为 agent runtime helper。
- 升级 DeepAgents 到 0.6.7 并适配新版文件系统协议：SubAgentMiddleware 改为显式 subagent spec，Skills prompt 补齐新版占位符；sandbox/skills backend 复用新版 `ReadResult`、`GlobResult`、`GrepResult` 等协议类型，文件权限在 backend 层明确区分 skills、uploads、outputs 与 workspace，保留最小 `CustomCompositeBackend` 以避免非 route glob 误扫其他 route；Agent 上下文压缩改为复用 DeepAgents SummarizationMiddleware，历史摘要与大工具结果统一 offload 到 outputs。
- 优化聊天输入 @ 文件提及：未创建 Thread 时可搜索用户 workspace，创建 Thread 后按当前对话文件优先、workspace 兜底的来源顺序搜索，并拆分 workspace/thread 缓存避免假 thread 与跨用户缓存污染；输入框与用户消息支持将 raw mention 渲染为带类型图标的引用单元，文件仅显示文件名且保留原始沙盒路径文本。
- 重构子智能体为 Agent-backed 形态：移除旧 `subagents` 表与 `/api/system/subagents` 管理链路，子智能体改为 `agents.is_subagent=true` 且使用 `SubAgentBackend`，创建/编辑统一走 Agent 管理入口；内置后端收敛为 `ChatbotAgent` 与 `SubAgentBackend`，Context 分为 `BaseContext`、`ChatBotContext` 与 `SubAgentContext`；主 Agent 通过 Yuxi task middleware 启动真实子 Agent graph，子智能体不再嵌套调用子智能体。沙盒挂载同步拆分为 child checkpoint thread、父对话 uploads/outputs、用户级 workspace 与子 Agent skills scope；主线程状态记录 `subagent_runs` 并在前端 task 工具中展示子智能体名称、执行状态、child thread 和产物，task 工具结果会暴露 child thread ID 且支持传回 `thread_id` 继续既有子智能体线程；子智能体执行复用 `agent_runs(run_type=subagent)` 记录父 run、child thread 与状态，child thread state 查询以 `agent_runs` 关系为准，不再解析 thread ID 反推父线程；真实流式 E2E 覆盖子智能体输出文件可由父线程文件/Viewer API 读取。流式链路参考 DeepAgents event streaming，后端将 LangGraph v3 raw event 归一化为 Yuxi semantic stream event，按父/子线程归属隔离 run SSE chunk，并支持通过 child thread state 拉取子智能体中间过程。
- 修正评估综合得分计算：`overall_score` 改为有答案准确率时取各题准确率平均，否则取各题 `recall@10` 平均，不再把 recall/f1/各 k 检索指标混合平均；历史已存运行不回填。

---

历史版本发布记录已迁移到 [版本变更记录](./changelog.md)。

维护说明：
- roadmap 仅保留未来规划（看板/Bugs/里程碑方向）。
- 具体版本发布内容统一维护在 changelog。
