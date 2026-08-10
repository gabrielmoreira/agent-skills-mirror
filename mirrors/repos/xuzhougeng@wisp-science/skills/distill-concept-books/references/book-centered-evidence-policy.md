# 图书中心证据政策

## 可靠性的含义

分别回答：

1. 指定版本图书是否确实表达了该内容；
2. 该内容是否代表当前领域证据或共识。

本 Skill 默认解决第一问。记录为 `accepted` 不自动回答第二问。各层 accepted 只回答该
层问题：evidence 的提取/定位、claim 的忠实性、relation 的语义强度、rule 的评测准入，
不得把 accepted rule 描述为已验证有效的 Skill。

## 来源分层

- 以登记的主图书为知识体系主线；
- 书中引用的论文只记录引文身份，不声称已经阅读原文；
- 图书作者观点、教学类比、案例和历史叙述保持原有地位；
- 书外来源使用独立 `source_id`，不得无痕改写主图书 claim；
- 模型已有知识只能作为明确标注的书外补充，不能充当图书 evidence。
- OCR 是载体提取方法，不是新的知识来源。识别文字仍属于原 source；OCR confidence 不证明
  文字正确，更不证明图中关系、公式含义或外部事实。

## 需要核验的情况

将内容置为 `needs-verification`，而不是自动纠正：

- 图书内部冲突、疑似 OCR/转录错误或术语不一致；
- 论断可能已过时或明显过度概括；
- 图像、箭头、公式或上下文不清；
- 医疗、临床、安全或其他高风险结论；
- 用户要求判断当前外部共识。

联网、扩大来源或上传原文之前必须获得批准。

高风险缺少所需外部核验时，只阻断依赖该结论的 rule；若冻结任务本身就是临床处置、
设备控制或安全关键 SOP，应转交专用高风险能力而不是继续套用本 Skill。

## 私有来源中心与公开来源中立

“图书中心”只描述私有证据治理：来源身份、locator、作者地位、最短必要摘录、权利和
审核历史必须完整保留。它不授权在下游候选或公开输出中复现书目身份、归因句、原句、
章节顺序或命名案例。

能够形成稳定任务的内容先以 T3 `distiller-synthesis` 从 problem、premises、invariant、
derivation、assumptions 与 boundaries/falsifiers/stops 重建，再形成 T4 rule。无法脱离专名、
原句或可识别案例而成立的内容留作私有 reference，不强行投影。候选只使用目标任务材料，
不得要求在运行时读取方法来源；详细约束见
[source-neutral-method-distillation.md](source-neutral-method-distillation.md)。

## 规则准入

accepted capability rule 必须完整回溯到 accepted claim 和可定位的 accepted evidence，
且每个 check/action/output/stop condition 有逐项 semantic support。`needs-verification`、
不可读图像、缺失 locator 或未解决冲突不得进入 accepted rule 的支撑链。rule accepted
只表示获准进入 Gate 4；Skill acceptance 还需要 completed/pass eval runs 和 Gate 4
人工决定。

`method-transfer` 不能把方法来源中的案例事实写成目标材料事实。目标材料必须用独立
source ID 和直接 target-material evidence；类比、外推或推测明确进入
`analogy-hypothesis` 层。三层 canonical 记录供私有审计；公开结果不得渲染
`method-source-evidence`，也不得用来源身份或归因措辞装饰目标结论。
