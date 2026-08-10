# 版权与私有处理

## 默认边界

- 本流程从不写原始图书，并用前后 checksum 检测意外变化；无法保证流程之外的“永久只读”；
- 未知许可按 `unknown/private-local-use` 处理；
- 不把原始全文、连续长引文、清洗全文或原图放入候选 Skill；
- 必要引用保持最短，并保存 locator；公开产物优先使用原创概括；
- 私人对话、未公开手稿、凭证和敏感信息不得进入可发布目录。
- 来源中立候选和公开任务输出不包含题名、作者、出版者、ISBN、系列/文件名、归因句、
  引文或可识别的命名来源案例；这些信息只留在私有 provenance 记录。

把权限拆开记录：

- lawful local processing：是否可在本地私有处理；
- upload：是否可发送到云端工具或服务；
- public quotation：是否可在公开产物引用；
- derivative publication：是否可公开发布衍生 Skill。

未知公开许可不自动阻断有合法来源的本地私有分析，但始终阻断未获授权的上传、公开
引用和衍生物发布。若连合法本地处理边界也无法建立，则 Gate 1/2 全局停止。

## 工具与数据目的地

调用任何可能联网、云端上传或收费的工具前，说明上传内容、目的地、用途和保留风险，并获得批准。没有批准时只在本地处理，不安装依赖来绕过边界。

受版权约束的 raw evidence payload 保存在私有且被 Git 忽略的路径；Git-safe ledger
只保存 locator/hash、最短必要摘录或原创概括。manifest 中
`allow_public_quotes: false` 的来源不得因为 validator 通过而进入公开候选内容。

来源中立投影不是规避署名或许可义务的手段。如果公开衍生物依法或依许可必须显示会暴露
来源的归因，则阻断来源中立公开，保留私有候选并请求单独权利处置；不得静默删除必需归因，
也不得把私有 provenance 打包进公开运行内容。详见
[source-neutral-method-distillation.md](source-neutral-method-distillation.md)。

本地 Tesseract/Poppler OCR 的页图、原图、TSV 和全文同样留在私有忽略区；随附 runner
不联网、不上传、不安装依赖。若改用云端 OCR，必须另行说明内容、目的地与保留风险并取得
明确上传批准。

Gate 4 artifact 即使通过严格 JSON、身份和 hash 校验，也只证明记录可重放且未发生已检测
的 byte 漂移。每个 fixture 仍必须逐项复核 source IDs、合法本地处理、上传/数据目的地、
holdout 答案隔离与上下文差异；结构 PASS 不产生使用、上传、引用或发布授权。

## 候选与发布

review 候选留在蒸馏目录。接受知识记录、接受 Skill、进入正式目录、初始化 Git、公开和部署是彼此独立的决定。

Gate 5 使用逐项授权矩阵：进入 `skills/`、初始化 Git、公开和 Wisp 部署分别记录请求、
授权、范围和结果。缺少某项授权只阻断该项，不得从 Gate 4 acceptance 或另一项授权推定。

dry-run、目标 diff、覆盖确认、部署后发现/解析/启用验证和回滚只适用于 Wisp 部署或任何
会覆盖现有内容的操作。普通 Git 初始化或公开决定应执行各自的边界检查，但不能被描述为
已经完成部署协议。

Gate 5 必须重新检查来源 manifest、候选目录、累计引用、references 和目标 runtime；
只验证 source ID 存在不等于完成版权审核。还要逐文件确认公开 candidate tree 未携带来源
身份、归因措辞、引文、文件名或可识别的命名案例。存在译名、转写/romanization、旧或来源
派生 slug、系列别名、特有术语或具名案例时，必须加载完整 private extra-terms 重新 lint；
缺失或覆盖不完整时停止公开。

## 引用外部作品

图书内嵌论文截图、图表和长摘录仍受原作品权利约束。评测若需要干净论文输入，应使用合法获得的本地材料，并将其登记为独立来源；不得从图书点评中重构后伪称为原论文。
