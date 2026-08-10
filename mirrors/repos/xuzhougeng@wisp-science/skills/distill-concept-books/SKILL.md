---
name: distill-concept-books
description: 将概念、理论或分析方法类图书蒸馏为证据可追溯、经人工门禁审核且不暴露书名、作者、出版社等来源身份的任务型 Skill 候选。用于新建或恢复图书蒸馏、以本地 Tesseract 扫描 DOCX 全部内嵌图像或 Poppler 渲染的扫描 PDF 全页、建立 source map 与 evidence/claim/relation/capability rule、用第一性原理重构可迁移方法，以及按权威 task contract 防止上下文压缩后的产品任务漂移；仅在本元 Skill 自身的 owning distillation 中路由其 Gate 4 评测。不用于单纯摘要、事实问答、人物思维模仿、实验或临床 SOP、临床决策，也不作为其他 Skill 的通用物化、评测、Git、发布或部署工具。
---

# 概念图书蒸馏

把来源限定的图书知识编译为可审核、来源中性的任务能力，不把全书压缩成摘要，也不把
来源身份复制到候选 Skill。私有治理记录保留追溯所需身份和 locator；候选 tree、评测输入
和运行输出只保留重新表达的方法、边界与停止条件。始终保持：

```text
evidence → claim → relation / capability rule → candidate specification
→ Gate 3 approved-for-eval → materialization → eval run → Gate 4 decision
```

不得先写候选结论再反向挑选证据，也不得把结构验证当作真实性或行为效果验证。

## 运行前检查

1. 判断请求是新建、恢复、候选维护、物化、评测还是已接受候选的安全移交。
2. 目标目录存在时先只读恢复，不复制模板、不清空数组、不改稳定 ID、不覆盖人工记录。
   新会话、checkpoint、上下文压缩/裁剪、阶段切换、后台任务返回或他人接手后，先重新读取
   current Gate 1 绑定的 task contract、`task-coverage.yml`、candidate `stable_task_ids` 和
   Gate 3/materialization；阶段目标和临时限制不能取代产品合同。
3. 执行任何规则前先证明当前 Skill tree 的 lifecycle 与来源。除非宿主权威记录以当前完整
   tree hash 明确证明它已 `accepted` 或 `deployed`，否则一律按 review candidate 处理。必须唯一
   定位 owning distillation、candidate ID/path 和 sources manifest；任一无法定位、冲突或不可读取
   都视为 `invalid`，只允许审阅和修复，不得因为副本被移动或复制而跳过治理。
4. 对 review candidate 从 owning distillation 的权威 YAML 读取实时状态；不依赖正文中的历史
   Gate、materialization ID、hash 或规则数量。运行：

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/inspect_distillation_state.py \
     <owning-distillation-dir> --candidate-id <candidate-id> \
     --candidate-path <candidate-path> --sources-manifest <sources-manifest>
   ```

5. 按检查结果路由：
   - `review-only`：只审阅或在用户明确授权下维护候选；
   - `materialization-required`：只物化获准规则、quick validate 并记账；
   - `gate4-eligible`：只允许加载唯一匹配版本执行获准评测；
   - `invalid`：停止受影响动作并修复治理歧义或结构错误。

三种受控状态均不改变 lifecycle；`approved-for-eval`、目录存在和 quick validation
都不等于 Skill accepted。状态契约见
[validation-contract.md](references/validation-contract.md)。

## 按需加载

| 判断或阶段 | 必读 reference |
|---|---|
| 图书任务是否适配 | [book-types-and-boundaries.md](references/book-types-and-boundaries.md) |
| Gate 1、恢复、目录和产物契约 | [input-output-contract.md](references/input-output-contract.md) |
| task contract、coverage、checkpoint 与防漂移 | [task-contract-and-drift-control.md](references/task-contract-and-drift-control.md) |
| 载体、adapter、checksum、locator 和 source map | [source-quality-preflight.md](references/source-quality-preflight.md) |
| evidence、claim、relation、rule、T0–T4 和 correction | [knowledge-model.md](references/knowledge-model.md) |
| 图书忠实性、作者观点、外部核验 | [book-centered-evidence-policy.md](references/book-centered-evidence-policy.md) |
| 第一性原理重构、去身份投影和候选禁入项 | [source-neutral-method-distillation.md](references/source-neutral-method-distillation.md) |
| 候选准入、拆分与 Gate 3 | [candidate-splitting.md](references/candidate-splitting.md) |
| Gate、materialization、validator 和 eval run | [validation-contract.md](references/validation-contract.md) |
| 私有处理、引用、上传、发布和移交 | [rights-and-private-processing.md](references/rights-and-private-processing.md) |

只加载当前判断需要的文件；YAML schema、长检查表和命令以 references 为准。

## 阶段协议

### MRULE-001：恢复并冻结任务（Gate 1）

- 先审计已有 task contract、coverage、brief、核心/治理 YAML、Gate 链、overlay、eval runs、候选和 hash；默认恢复。
- 冻结受众、至少三个稳定任务、范围、语言、运行时、验收问题、阅读/留出计划和失败条件。
- 把稳定任务写入不可覆盖、可哈希的 `task-contract.yml`；brief 只引用合同。current 正向
  Gate 1 必须绑定 `gate1-task-contract-snapshot:v1`。合同变化使用新版本文件和 superseding
  Gate 1 决定，不修改旧合同或历史决定。
- 分开主图书、补充来源、模型知识、用户新材料与项目政策；分别记录本地处理、上传、
  公开引用和衍生发布权利。
- 冻结两层边界：书目身份、文件名和完整 locator 只进入私有 provenance；下游候选及其
  用户可见输出不得出现书名、作者、出版社、ISBN、系列名或可识别的来源案例。
- 展示冻结项与未决项后暂停。只有用户明确决定后才追加 Gate 1 记录；无 current 正向
  Gate 1 时不得规范化、扫描正文或提取知识。

### MRULE-002：登记来源并扫描结构（Gate 2）

- Gate 1 正向通过后，在私有 manifest 中增量登记来源，校验合法本地处理边界、完整性与
  原文件 checksum；优先使用不含书名或作者的 opaque source ID 和载体路径。不写原件，
  派生产物仅进入私有忽略区，不把书目字段复制到候选或可发布审阅视图。
- DOCX adapter 先原样提取全部内嵌图像，再用本地 Tesseract 对全部图片执行 OCR；扫描 PDF
  使用 Poppler 固定 300 DPI 渲染全部页面后逐页 OCR。语言必须显式声明；缺少本地引擎、
  语言包、渲染器或任一未处理图片/页面时 fail closed；不得以“装饰图”为由静默跳过。
  其他 PDF/EPUB 仅做有限 preflight。
- 区分出版内容质量与派生载体保真度；建立可实际重解的 locator，扫描全书结构并隔离留出。
- 展示 source map、精读/快读/未读/留出范围和质量缺口后暂停。Gate 2 未由用户写回前，
  不进入 evidence/claim 提取。

### MRULE-003：建立四层记录

- 在冻结范围内先采集带 locator、载体内容和质量限制的 evidence，再形成单判断 claim，
  然后建立 relation 与 capability rule。
- 在私有治理层区分来源陈述、来源解释、教学类比、项目政策、蒸馏综合和任务迁移；不提升
  原文确定性，也不把这些 provenance 标签直接写入候选运行输出。
- 对拟进入规则的内容先建立 T3 `distiller-synthesis` 第一性原理重构：写明任务问题、最小
  前提、核心不变量、逐步推导、假设、边界、反例/证伪条件、停止条件和剩余不确定性。
  具名案例、修辞顺序或独特表达不能直接支撑 T4；无法在不改变含义的情况下去身份时，
  将其保留为私有 `reference-only`，不强制生成候选。
- 每个 rule 的 check、action、output、stop condition 都要有逐项 semantic support；
  T3/T4 和 inferred relation 必须保留显式人工决定。
- 缺字、OCR、转换、翻译或术语疑点进入 correction overlay，不改原值、不猜补；completed
  决定必须显式来自 `user | human-delegate`，不得用 agent 或 reviewer 字符串冒充人工。
- 先写权威 YAML，再生成 Markdown 审阅视图；两者冲突时停止修复。

### MRULE-004：拆分候选并取得 Gate 3 决定

- 按稳定任务而非书名/章节拆分；允许一本书产生零个、一个或多个候选。
- 先完成 `task-coverage.yml`；每个 active stable task 必须覆盖 candidate、rule、trigger、
  nontrigger、task eval、holdout 和 rubric dimension，不能通过后续沉默省略任务。
- Gate 3 前生成最终但不可激活的 review-only candidate tree、candidate specification 和
  review package。递归检查完整
  `rule → claim → evidence` 闭包与逐项语义支持，排除 unresolved/needs-verification 上游。
- candidate name、description、references、examples、eval prompts 和输出契约必须由稳定任务
  与 T3 重构原则生成，不得包含书名、作者、出版社、ISBN、系列/文件名、原书引语、来源归因
  或可识别的具名案例。治理 guard 可以使用 opaque ID/hash，但不得向普通运行输出泄露它们。
- 先确认 sources manifest 将方法来源显式分类为 method-source/primary-book/supplementary-book
  或 book 类型；分类缺失或冲突时阻断，不能把 target-material 或 project-policy 当成方法身份。
- 在形成 Gate 3 snapshot 前运行只读 disclosure lint。若存在译名、转写/romanization、旧名或
  来源派生 slug、系列别名、特有术语或具名案例，必须把它们完整写入私有 extra-terms 文件并
  在 Gate 3 与 Gate 5 使用同一禁词集合；缺失、不完整或无法确认时 fail closed。lint 报告不得
  回显被拦截的身份值：

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/audit_candidate_disclosure.py \
    <candidate-path> --sources-manifest <sources-manifest> \
    [--extra-terms-file <private-extra-terms-file>]
  ```

  任一 identity、归因短语、具名案例、缓存、symlink、非 UTF-8 或无法由该 lint 审计的二进制
  artifact 都先修复。候选 tree 只接受已审核的 UTF-8 文本；运行时必需二进制在建立专用审计
  路径前保持 Gate 3 blocked，不得静默跳过，也不得在批准后制作未被 snapshot 绑定的“清理版”。
- 展示触发、反触发、输入、输出、规则、推论、拒绝项、停止条件及 approval snapshot 后暂停；
  新 snapshot 必须使用 `gate3-approval-snapshot:v2`，绑定最终候选 tree、三份权威知识 YAML、
  current Gate 1、task contract、coverage 和 candidate stable task IDs。
- 只有用户写回 current `approved-for-eval`、逐条决定全部当前 rules 且 snapshot 仍精确匹配
  时才可物化。物化不得改写候选 bytes；记录相同 path/hash/rules 及绑定该 hash 的 quick
  validation，lifecycle 仍为 review。任一漂移都要求新的 Gate 3 决定。

### MRULE-005：执行受控评测（Gate 4）

- 本阶段只评测本元 Skill 自身的 matching materialization；其他候选必须使用其 owning
  distillation 和专属 eval contract，不把本元 Skill 当成通用 Gate 4 工具。
- 仅在 current approval snapshot 与唯一 matching completed materialization 的候选 ID、
  path/hash、全部获准 rules 和 quick-validation pass 一致时进入。
- 对逐项获权且可重放的 fixture，在隔离上下文中执行同一任务的无 Skill 基线与有 Skill 组；
  仅使用候选 eval definitions 中的 case ID/canonical hash。fixture 与两组输出必须是三个不同
  的根内 strict JSON 文件，现场复算 SHA-256，并绑定 run/case/condition、物化 rubric、逐维
  评分、fatal failures、holdout/泄漏控制、环境、人工 reviewer 和限制。
- 实际覆盖至少 3 个 trigger、3 个 nontrigger、3 个 task，并含未参与规则提取的 holdout。
- `method-transfer` 还必须使用独立 target-material source 的外部 holdout，覆盖合同声明的
  输入类型，并分别输出 method-source evidence、target-material evidence 与 analogy/hypothesis。
- 来源中性候选至少有一个不含方法来源身份、原案例或答案提示的合成/独立目标材料用例；
  出现来源身份、运行时要求读取原图书、强行套用原案例或把来源事实当作目标事实均为 fatal。
- 生成 Gate 4 review package 后暂停；不得代用户写 accepted。单个 blocked run 不抹除其他
  独立 completed runs，测试定义或计划不得冒充实测。

### MRULE-006：准备已接受候选的安全移交（Gate 5）

- 只处理本流程产出、已有权威 Gate 4 accepted 决定的同一候选；不是通用发布 Skill。
- 把进入正式 `skills/`、Git 初始化、公开和 Wisp 部署作为四项独立授权，并按目标动作
  复核版权、隐私、引用与数据目的地。
- 移交前对同一 snapshot-bound tree 重跑 disclosure lint；不得把私有 manifest、source map、
  evidence ledger、normalized/OCR bundle 或 extra-terms 文件复制进候选或部署目录。
- Wisp 部署另核对 runtime/schema；仅对部署或覆盖动作执行 dry-run、diff、覆盖确认、
  部署后验证和回滚记录。未授权或不满足条件时只阻断对应动作。

## 阻断与恢复

| 范围 | 阻断动作 | 可继续内容 | 恢复依据 |
|---|---|---|---|
| 单条 claim/rule | 依赖不可读图像、术语、correction、冲突或不稳定 locator 的判断 | 其他依赖闭包独立的记录 | 可解析 locator、人工 correction/推论决定或冲突处置 |
| 单一来源/全局 | 私有身份、合法本地处理、全局 locator 或冻结任务必需内容无法建立 | 不依赖该来源的已授权工作；全局前提失败则全部暂停 | 私有来源登记、权利确认或已验证 adapter/bundle |
| 候选去身份 | disclosure lint 命中书目身份、归因短语、具名案例或私有载体信息 | 私有证据整理与不依赖该候选的工作 | 重写为任务原则、排除不可抽象内容并对同一 tree 复查通过 |
| 候选状态 | 无 current approval、无唯一 matching materialization 或治理状态 invalid | 仅执行状态允许的 review/maintenance/materialization | 权威 Gate 决定、唯一匹配物化与通过的验证 |
| 单个 eval run | fixture 不可重放、权利不足、污染、泄漏不明或需要未批准的联网/上传/安装 | 其他独立合法 runs | fixture/hash/权利/隔离记录与所需授权 |
| Gate 4 acceptance | 3/3/3、holdout、对照、completed/pass 或人工评分不足 | 保留已完成 runs，继续补足评测 | 同一 materialization 上完整合格 runs |
| 移交操作 | 缺少该项授权、版权/隐私边界、目标 diff、回滚或 Wisp schema | 其他独立获准操作 | 对应的明确授权与操作前提 |

## 输出与诚实边界

- 核心知识 YAML、Gate decisions/materializations、eval runs 和适用的 overlay 是权威记录；
  Markdown 仅是审阅视图。
- 每次 Gate 报告精读、快读、未读、留出范围以及局部/全局缺口。
- `accepted` 知识记录只表示忠实、可追溯且适合当前用途，不表示外部共识。
- 去除来源身份不等于证明版权许可或方法的外部正确性；它只是候选 disclosure 边界。
- 普通运行输出只呈现目标材料证据、任务判断、假设、边界和未知项，不呈现私有 provenance。
- validator、locator resolver、tree hash 和 quick validation 只证明各自覆盖的结构约束；
  只有 completed behavior runs 加 Gate 4 人工决定才能支持 Skill acceptance。
