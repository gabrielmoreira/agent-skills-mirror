# 输入与输出契约

## Gate 1 必需输入

- 目标受众、真实任务、输出语言和目标运行时；
- 主图书的来源身份、版本、本地载体、完整性和权利边界；权利边界分别记录本地处理、
  上传、公开引用和衍生物发布；
- 精读、快读、未读和留出计划；
- 允许的补充来源、联网、上传、依赖安装、公开和部署范围；
- 验收问题、失败条件、人工门禁和候选粒度。

缺失项不能安全推断时，先请求决定。不得以模型常识替代来源或授权。

brief 先生成并展示，Gate 1 决定后写。不得在请求用户决定前预填 `approved`；只有用户
作出决定后，才能按 sequence/supersedes/is_current 链追加权威记录。Gate 1 无 current
正向决定（`approved` 或 `approved-with-conditions`）时，不进入来源规范化、结构扫描、
正式精读或知识提取；来源文件存在或 manifest 已登记都不能替代该决定。

稳定任务先写入 `task-contract.yml`，冻结后由 `gate1-task-contract-snapshot:v1` 绑定完整
bytes hash、ID、版本和 active IDs。brief 只引用合同。已绑定 v1 不得覆盖；实质变化创建
`task-contract.v2.yml` 等新文件并追加 superseding Gate 1 用户决定。

## 恢复优先

目标目录存在时先读取已有 brief、核心 YAML、Gate decision current/supersedes 链、
materializations、correction overlay、eval runs、候选文件和 hash。默认继续已有
`distillation_id`，不重新复制模板、清空数组、
改稳定 ID 或覆盖人工决定。只有用户明确选择新建或另存为时才创建新目录。

## 权威数据产物

一个完整蒸馏目录使用：

```text
evidence-ledger.yml    # evidence + claims
concept-map.yml        # relations
capability-rules.yml   # capability_rules + optional skill_candidates
task-contract.yml      # Gate 1 绑定的不可变产品任务合同
task-coverage.yml      # stable task 到 candidate/rule/eval/rubric 的覆盖矩阵
gate-decisions.yml     # Gate 1-5 决定链 + candidate materializations
eval-runs.yml          # Gate 4 实际执行、对照、评分和结果
correction-overlay.yml # 有缺字/OCR/转换/术语问题时必需
```

前三份是核心知识记录，后两份是治理记录；correction overlay 按问题条件出现。从
`assets/templates/` 内同名 YAML 示例复制工作副本，但只创建缺失文件。字段和校验规则
见 `knowledge-model.md` 与 `validation-contract.md`。YAML 是权威记录；Markdown 只是
审核视图，二者冲突时不得静默选择其一。目录中存在 `SKILL.md` 也不能替代
materialization 记录。

这些权威记录属于私有 provenance 平面，可以并且应当保存 source ID、locator、载体原值、
书中地位、correction 和权利边界。来源中立不允许删改该平面，也不允许用去标识后的候选
反向替代原记录。

对 OCR、转换、翻译或术语疑点，从 `assets/templates/correction-overlay.yml` 创建独立
overlay。保留原始值、候选修正、依据、影响范围和人工决定，不覆盖 evidence 中的
`raw_text` 或 `normalized_text`。使用修正解释的 claim 必须列出 `correction_ids`。completed
correction 必须含 `reviewer_type: user | human-delegate`；仅有 reviewer 名称或 agent 署名
不构成人工决定。

项目 validator 同时读取核心记录、Gate decisions、eval runs 和适用的 correction
overlay。PASS 只证明其实现的结构和治理约束，不证明知识真假、版权许可或行为效果。

来源登记位于工作区 `manifests/sources.yml`。若宿主项目没有兼容 manifest，可在用户批准
的新工作区从 `assets/templates/sources.yml` 创建；已有 manifest 必须先审计并增量登记，
不得由模板覆盖。Gate 4/5 validator 必须显式传入该 manifest。

## 载体输入边界

- 自动读取只承诺项目随附且已验证的 DOCX adapter；
- 也可接受符合项目 schema、带 source ID/checksum/locator 的规范化 bundle；
- `book-pdf-scan` 使用专用本地 adapter：Poppler `pdfinfo/pdftoppm` 固定 300 DPI 将每页渲染
  为 PNG，再由 Tesseract 全页 OCR；它不承诺恢复可编辑 PDF 的逻辑阅读顺序；
- 其他 PDF、EPUB 和第三方 OCR 输出没有兼容 bundle 时只能做有限 preflight；
- 不受支持的载体应请求规范化 bundle、批准专用 adapter 工作，或标记 blocked。

来源尚未登记不应造成“必须先登记才能登记”的循环：先以书内信息确认身份和合法本地
处理边界，再向已有 manifest 增量登记稳定 source ID。原文件不得写入，处理前后复核
checksum；规范化 bundle 和日志只进入私有、被忽略的来源区。DOCX locator 使用
source ID、heading path、OOXML block index、content hash 和可选 figure/table ID；兼容
非 DOCX bundle 使用自身已验证的可重复 locator 契约。

DOCX locator resolver 必须显式传入 sources manifest，稳定/no-follow 地复算 bundle 中生成
文件的完整 SHA-256/size、每个 block 的文本 hash，并把 normalization 前后 checksum 与
manifest 绑定。不得只核对 ledger 与可被同时改写的 bundle 内部是否自洽。

DOCX 图片与扫描 PDF 使用独立私有 OCR bundle：`ocr-manifest.yml`、`ocr-results.jsonl`、
`checksums.yml` 和原图/页图。全部图片/页面都必须产生 completed、empty 或 failed 记录；
failed 或未绑定 occurrence 使覆盖不完整。OCR evidence 使用 `ocr-region` locator，并必须再用
`verify_ocr_locators.py` 对原来源、normalization/PDF 页数、派生清单、图片、region、bbox 和
文本 hash 做只读解析。result 同时保留引擎原始文本与仅执行 NFC/换行规范化的文本；不得
用 strip、拼写修正或术语替换伪装成规范化。

## 人工审核视图

从 `assets/templates/` 复制并填写：

- `brief.md`：冻结需求、来源边界和门禁；
- `source-map.md`：全书结构、载体质量和读取范围；
- `overview.md`：基于已登记 claim 的知识路线；
- `concept-map.md`：关系、限定和证据索引；
- `candidates.md`：稳定任务、触发/反触发和拆分方案；
- `decisions.md`：处置、T3/T4 和生命周期决定。

Markdown 决定表必须从 `gate-decisions.yml` 的 current/supersedes 决定链、materializations
和各记录的 decision/history 生成；只填写 Markdown 或只保留一个候选目录不构成批准或
物化完成。

`brief.md`、`source-map.md`、`overview.md`、`concept-map.md`、`candidates.md` 和
`decisions.md` 均是私有人工审核视图，不是可发布 candidate references。实际书目身份只在
private sources manifest 或必要权利记录中单点保存；这些 Markdown 使用 opaque source/section
ID、hash、locator 状态和原创概括，不重复渲染题名、作者、出版信息、原文件名、引文或具名
案例。审核需要查看最短必要原文时回到私有 evidence ledger/normalized bundle，不把内容复制
到候选 tree。

## 来源中立 candidate/public output

候选从已获人工决定的 T3 `distiller-synthesis` 与 T4 rules 重新投影。投影必须能在不读取
方法来源的情况下运行，并只输出目标观察、来源中立分析、假设、限制、未知项和停止理由。
候选的 `SKILL.md`、references、trigger/nontrigger、示例与输出合同均不得包含：来源题名、
作者、出版者、ISBN、系列名、原文件名或路径、归因句、引文/连续近似改写、章节/页码/
locator、私有 provenance ID，或可识别的命名案例。

method-transfer 的 `method-source-evidence`、`target-material-evidence` 与
`analogy-hypothesis` 仍按现有 schema 保存在私有 canonical 记录中；公开输出不渲染第一层，
并继续把目标直接证据与推论分开。具体重建、去标识和 fail-closed 规则见
[source-neutral-method-distillation.md](source-neutral-method-distillation.md)。

## Review 候选的状态路由

目录存在不代表候选可执行，`legacy-quarantined` 也不能支撑评测。三种正常路由加
`invalid` fail-closed、Gate 3 approval snapshot、唯一 matching materialization 要求和
只读状态检查器统一见
[validation-contract.md](validation-contract.md)；任何状态都不自动改变 `review` lifecycle。
运行前还必须唯一定位 owning distillation、candidate ID/path 和 sources manifest，并由宿主
权威记录以当前完整 tree hash 证明 lifecycle/Gate 状态；无法证明或出现多个可能来源时
路由为 `invalid`，不得因副本路径或正文自述跳过治理。

## Gate 4 artifact 输入

completed run 只接受来自物化定义的真实 case，并记录 canonical `case_definition_hash`。
fixture、baseline output 和 with-Skill output 必须是三个不同的根内严格 JSON 普通文件，分别
绑定 fixture/run、case、request、source IDs、holdout 与 baseline/with_skill condition；rubric
ID、最大分、阈值、逐维评分、fatal failures 和 leakage controls 必须与定义一致。planned 或
blocked 记录可以保留空 artifact 字段，但不能冒充 completed 实测。

## 目录边界

- 本流程不写原始材料，并在关键阶段复核 checksum；“永久只读”不是 Skill 能保证的
  外部属性；
- 规范化全文、缓存、索引和原图留在私有且被忽略的来源区；
- 受版权限制的 raw evidence payload 也留在私有、被 Git 忽略的区域；可进入 Git 的
  ledger 使用 locator/hash、最短必要摘录或原创概括；
- 过程记录和 review 候选留在 `distillations/<id>/`；
- 只有经 Gate 4 接受并另获批准的版本才可进入正式 `skills/`；
- 部署、Git 初始化和公开发布均是 Gate 5 的独立决定。
