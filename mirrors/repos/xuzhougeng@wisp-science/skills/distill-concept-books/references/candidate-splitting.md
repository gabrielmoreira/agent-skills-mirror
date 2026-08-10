# Skill 候选拆分规则

## 准入测试

只在同时满足以下条件时建立候选：

- 对应一个稳定、可独立触发的任务；
- 输入、输出、检查和停止条件清楚；
- 存在可重复执行的 capability rules；
- 规则可以回溯到 claim 和 evidence；
- rule 的 checks/actions/outputs/stop conditions 具有逐项 semantic support；
- 能设计 should-trigger、should-not-trigger 和陌生任务评测；
- 候选不会把作者风格、教学类比或背景事实伪装成领域能力。
- 候选可在不读取方法来源的情况下处理目标任务；私有 provenance 仍能从 owning
  distillation 完整回溯；
- candidate tree、公开 reference、触发示例和输出合同不含来源题名、人物、出版信息、
  ISBN、系列/文件名、归因句、引文或可识别的命名案例。

## 拆分信号

在以下情况下拆分：

- 用户意图、输入载体或输出结构显著不同；
- 一个任务可在不加载另一任务规则的情况下独立完成；
- 风险等级、停止条件或核验要求不同；
- 触发边界会因合并而变得过宽；
- 不同规则集合需要不同留出评测。

在规则高度共享、触发与输出一致时保持一个候选，通过 references 渐进加载细节。

## 不按来源机械拆分

一本书可以产生零个、一个或多个候选；多本书也可以共同支撑一个稳定能力。术语、案例、历史和详细事实通常进入 references，不单独生成 Skill。

其中来源专属的术语、案例、历史和详细事实只能留在私有治理 references。下游候选的
references 必须从获准的 T3 `distiller-synthesis` 重新表达 problem、premises、invariant、
derivation、assumptions、boundaries/falsifiers/stops，不能复制或轻度改写私有来源内容。

## 每个候选的最小记录

记录 `candidate_id`、`name`、人读 `stable_task`、机器可读 `stable_task_ids`、case IDs、
should-trigger、should-not-trigger、输入、输出、`rule_ids`、风险、停止条件和 lifecycle。
每个 active task 必须在 `task-coverage.yml` 完整映射；人工审核前 lifecycle 保持 `review`。

## Specification、决定与物化

Gate 3 前形成 candidate specification 和审阅视图，不把 pending T4 当作已批准的激活后
运行协议。Gate 3 决定按 `sequence / supersedes / is_current` 链写入
`gate-decisions.yml`；只有当前决定生效：

- `approved-for-eval`：允许物化候选并取得受控 Gate 4 资格；只有 matching completed
  materialization 后才可实际执行；
- `revise`：保留 specification，修订后重新审阅；
- `rejected`：保留拒绝理由，不物化。

`approved-for-eval` 必须逐条覆盖当前 rule 集并同步 rule status、human decision 和
history；旧 approval、`pending`、`revise`、`rejected` 或不完整 rule_decisions 均不授权
物化。

`approved-for-eval` 不是 lifecycle。物化步骤：

1. Gate 3 前从 `assets/templates/candidate-SKILL.md` 形成最终 review-only tree，包括
   `SKILL.md`、必要 references 和两份 JSON eval definitions；frontmatter 只保留
   name/description，并由 activation guard 阻止 pending 规则执行；
   该 tree 同时必须完成
   [source-neutral-method-distillation.md](source-neutral-method-distillation.md) 的投影审查；
   私有 evidence/claim/locator 不复制入 tree，运行时也不读取方法来源；
2. 计算并展示 `gate3-approval-snapshot:v2`，绑定 candidate path/tree hash、三份权威知识
   YAML、current Gate 1、task contract、coverage 和 candidate stable task IDs；
   如需修改已有候选，先显示 diff 并取得维护授权，然后重新计算 snapshot；
3. 用户以 current `approved-for-eval` 接受该精确 snapshot 后，不再改写候选 bytes；
4. 运行项目当前认可的 `quick_validate.py`，将同一 candidate hash 写入 quick-validation；
5. 在 `gate-decisions.yml.materializations` 记录 Gate 3 decision、相同路径/hash、完整 rule
   集合和验证结果；lifecycle 仍保持 `review`。

不能被 current approval snapshot 精确识别的旧 pre-approval prototype 必须保持
`legacy-quarantined`，不得反推或回填 Gate 3 approval。

activation guard 的三种正常路由加 `invalid` fail-closed、approval snapshot、唯一 matching
materialization 条件和状态检查命令见 [validation-contract.md](validation-contract.md)；
此处不重复一份容易漂移的状态规范。

## Gate 4 准入

只有 completed materialization 以及可重放 fixture、candidate hash、rule IDs、
基线/实验输出、rubric、阈值与人工评分都记录在 `eval-runs.yml` 后，才能请求 Gate 4
接受。completed run 必须绑定该物化；测试定义、quick validation、`planned/blocked`
run 或 `legacy-quarantined` 原型均不构成行为通过。

Gate 4 产物是供用户决定的 review package，而不是 agent 代写的 accepted decision。
fixture 缺失、权利不足、污染或未授权数据目的地先阻断相应 run；覆盖不足、非
completed/pass、无人工评分或混用 materialization 阻断 Gate 4 接受。

MRULE-005 只评测本元 Skill 的 matching materialization；MRULE-006 只为本流程产出且经
Gate 4 接受的同一候选准备逐项授权移交。二者都不是通用测试、Git、发布或部署 Skill。

`method-transfer` 的 holdout 必须是登记为 `target-material` 的独立来源，未参与规则提取，
记录 hash、输入类型和陌生 domain/case/mechanism/method，并覆盖合同的 required input types。
