# 任务合同与上下文防漂移

## 权威层级

产品级稳定任务只来自 current 正向 Gate 1 所绑定的 `task-contract*.yml`。`brief.md` 是审阅
视图；current stage objective 只说明当前阶段；temporary operational constraints 只限制
当前操作。后两者均不能新增、删除、defer、reject 或改写 stable task。

若产品要求下游 candidate 来源中立，合同中的 stable task、正反例、required input/output 和
验收问题必须描述目标任务，而不是“应用某书/某作者的方法”。方法来源仅作为私有 provenance
输入；候选运行时不得要求它。来源中立要求的任何实质变化同样遵守下述不可变版本规则。

## 不可变版本

- v1 使用 `task-contract.yml`；Gate 1 绑定后不得改写。
- 后续使用 `task-contract.v2.yml`、`task-contract.v3.yml`；保留全部旧 bytes。
- 合同从 `draft` 整理为 `frozen` 后才可提交 Gate 1；正向决定绑定完整 raw-byte SHA-256。
- stable task 的实质变化需要新合同版本和 superseding Gate 1 用户决定，不能回填旧记录。

## 覆盖矩阵

`task-coverage.yml` 对每个 stable task 建立 candidate、rule、trigger、nontrigger、task eval、
holdout 和 rubric dimension 的外键链。active 必须完整 covered；deferred/rejected 必须与合同
状态一致并引用 current Gate 1 决定及理由。candidate、rule 和 eval case 同时声明
`stable_task_ids`；每个 schema v2 case 显式登记 `positive_example_ids` 与
`negative_example_ids`。trigger/nontrigger 只允许相应极性的非空列表，task case 两类均须
非空，并且所有 example ID 都必须回指同一 stable task 的合同正反例。

## 恢复协议

在新会话、上下文压缩/裁剪、checkpoint 后、阶段切换、后台返回或 agent handoff 后：

1. 读取 task contract 和 current Gate 1 snapshot，复算 path/hash/ID/version/active IDs；
2. 读取 coverage，列出 covered/uncovered/deferred/rejected；
3. 核对 current candidate/rule/case 的 stable task IDs；
4. 核对 Gate 3 v2、materialization 与 candidate tree；
5. 分栏输出 authoritative product contract、stage objective 和 temporary constraints。

可选 `context-checkpoint.yml` 必须重新绑定 current contract。它只能选择 active task 作为
阶段工作，不能声明 `supersedes_product_contract: true` 或排除 active task。漂移时只允许
review/repair，禁止物化和 Gate 4。

## 确定性边界

validator 使用稳定 ID、显式映射和 hash；不使用模糊相似度推断文本语义。人工 Gate 3
必须并排查看 stable task 原文、candidate trigger/nontrigger、task/holdout/rubric、coverage、
provenance contract 和 deferred/rejected 决定，负责发现“文字不同但 ID 被错误标注”的冲突。
