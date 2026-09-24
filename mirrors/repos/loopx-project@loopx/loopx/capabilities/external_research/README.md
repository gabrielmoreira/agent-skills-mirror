# External Evidence Research / 外部证据研究

`external-evidence-research` is LoopX's provider-neutral contract for turning a
decision-bound research question into compact, auditable evidence. It unifies
two provider classes without pretending they are the same implementation:

- a host method such as the `external-research` skill; and
- a connector provider such as an official-document search integration.

`external-evidence-research` 是 LoopX 面向决策的通用外部证据合同。它统一两类
provider 的调用与回执语义，但不把两者伪装成同一种实现：

- host 提供的研究方法，例如 `external-research` skill；
- connector provider，例如官方文档搜索连接器。

## Contract / 合同

The lifecycle is:

1. `discover`: project method and connector inventory plus current readiness,
   while explicitly keeping registry presence, execution, and evidence coverage
   false unless separately observed;
2. `plan`: bind **object + user activity + decision** and required evidence
   kinds to one provider that is currently declared, installed, enabled, and
   ready, then content-address the normalized request, candidate inventory,
   selection, and execution envelope as `plan_id`;
3. provider execution: the selected host method or connector reads external
   sources under its own adapter and permission boundary;
4. `receipt`: require the caller-presented provider receipt to echo `plan_id`,
   reconstruct and verify the canonical plan, then record the receipt
   observation without treating it as provider execution attestation or
   claiming evidence coverage, admission, or automatic promotion;
5. `admit`: validate the exact request/provider identity and source-level
   provenance, bind the complete receipt digest, then record the parent agent's
   admit/reject decision;
6. downstream projection: pass only compact findings, limitations, direct
   references, evidence basis, dates, and content digests;
7. `retire`: revalidate the complete content-addressed admission, then retire
   rejected evidence immediately, or admitted evidence only after every
   admitted source reference appears in downstream readback.

生命周期为：`discover` 只读投影 method/connector 库存与当前 readiness，并明确区分
registry presence、真实执行和证据覆盖；`plan` 绑定“对象 + 用户活动 + 决策”并选择当前
真实 ready 的 provider，并用 `plan_id` 对规范化请求、候选库存、选择和 execution envelope
做内容寻址；provider 在自己的权限边界内执行；`receipt` 回传并校验 `plan_id`，只记录
caller 提交的回执，不把它冒充 provider 执行证明、证据覆盖、采纳或自动晋升；`admit` 校验请求、provider、完成时间、
完整 receipt digest 与逐来源 provenance，并记录父 Agent 的采纳/拒绝；下游只投影紧凑证据；被采纳的来源全部完成
下游读回后才可 `retire`，且 retirement 会先重验完整 admission identity。

The connector registry is only inventory and telemetry. A connector row marked
`supported` is projected as `ready=false` until a current provider lifecycle
readback proves installation, enablement, and readiness. Registration never
counts as execution or evidence coverage.

Connector registry 仅拥有库存与遥测。即使 connector 标为 `supported`，在当前
provider 生命周期读回证明 installed/enabled/ready 之前仍投影为 `ready=false`。
注册不等于调用，更不等于证据覆盖。

## CLI / 命令行

```bash
loopx external-evidence discover \
  --connector-registry \
  --format json

loopx external-evidence plan \
  --objective "Compare current behavior" \
  --user-activity "Choose an implementation" \
  --decision "Whether to adopt it" \
  --evidence-kind current_behavior \
  --evidence-kind counterexample \
  --provider-inventory-json providers.json \
  --format json

loopx external-evidence receipt \
  --plan-json plan.json \
  --receipt-json receipt.json \
  --format json

loopx external-evidence admit \
  --plan-json plan.json \
  --receipt-json receipt.json \
  --decision admit \
  --reason "Direct source answers the decision" \
  --admit-source https://example.com/original \
  --format json

loopx external-evidence retire \
  --admission-json admission.json \
  --downstream-source https://example.com/original \
  --format json
```

Provider inventory is an observation, not authority. A ready provider row uses
protocol `external_evidence_research_v0` and carries explicit `declared`,
`installed`, `enabled`, and `ready` booleans. Raw pages, transcripts, cookies,
credentials, and private notes remain provider-private.

## Ownership and product surfaces / 归属与产品入口

- The TypeScript contract owns request identity, provider admission, provenance
  validation, parent admission, compact projection, and retirement readiness.
- Python adapts the existing CLI and effect-runtime transport; it does not
  reimplement those decisions.
- Managed Turn callers can invoke the same effect-runtime methods:
  `external_evidence.discover`, `external_evidence.plan`,
  `external_evidence.receipt`, `external_evidence.admit`, and
  `external_evidence.retire`.
- Frontend and Lark are companion slices. They should render the same plan and
  admission projection; neither gets an independent provider registry or
  evidence state machine.

TypeScript 是 discovery 真值边界、请求身份、provider 准入、provenance 校验、父 Agent 采纳、紧凑投影与
退休条件的唯一语义 owner。Python 仅适配 CLI 与 effect-runtime transport。Managed
Turn 复用同一方法；frontend/Lark 后续只渲染同源投影，不新建 registry 或状态机。
