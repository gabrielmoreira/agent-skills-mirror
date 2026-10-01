# Adaptive Agent Teams

## Status and scope

Adaptive agent teams are a post-MVP architecture profile for investigations that benefit from sustained exploration of competing approaches. A team owns an approach to a shared objective while its members perform bounded work. The portfolio of teams can change as evidence develops.

This profile combines established delegation, parallel search, shared findings, and adaptive allocation. It documents proposed provider-neutral contracts, not a recovered vendor implementation or a new model, training method, or autonomy level. A durable team identity is a reconstruction requirement here, not a claim about every reported system. See [source evidence and limitations](source-links.md#adaptive-agent-teams).

Use it when a measured single-loop or ordinary worker workflow misses useful coverage, loses distinct approaches, or cannot adapt work allocation effectively. A routine task does not need a team portfolio. Agent count and different prompt wording do not establish useful diversity.

This reference owns approach charters, work-intent overlap policy, team-level sharing policy, and portfolio transitions. Reuse the canonical owners for:

| Concern | Source of truth |
|---|---|
| objective, completion criteria, checkpoints, and scope changes | [planning and goals](planning-and-goals.md) |
| bounded packets, independent verification, and final integration | [workflow orchestration](workflow-orchestration.md) |
| child identities, admission, message delivery, cancellation, recovery, and aggregate reservations | [recursive child-session protocol](self-refining-recursive-harnesses.md#recursive-child-session-protocol) |
| tool schemas, execution authority, approvals, and sandboxes | [tools and permissions](tools-and-permissions.md) |
| context selection, compaction, and rehydration | [context and memory](context-memory-compaction.md) |
| cost telemetry and cache behavior | [prompt caching and cost](prompt-caching-and-cost.md) |
| trace storage, redaction, and incident handling | [security and observability](security-observability.md) |
| evaluation methodology and the team diagnostic matrix | [adaptive agent team evals](evals.md#adaptive-agent-team-evals) |

## Contents

- [Taxonomy](#taxonomy)
- [Authority boundary](#authority-boundary)
- [State and interfaces](#state-and-interfaces)
- [Work intent and overlap](#work-intent-and-overlap)
- [Communication and independence](#communication-and-independence)
- [Portfolio transitions](#portfolio-transitions)
- [Failure semantics](#failure-semantics)
- [Observability and evidence](#observability-and-evidence)
- [Safe build sequence](#safe-build-sequence)
- [Evaluation requirements](#evaluation-requirements)
- [Anti-patterns](#anti-patterns)

## Taxonomy

| Pattern | Distinguishing boundary |
|---|---|
| bounded worker workflow | Workers execute declared packets and return results for integration. |
| retained recursive child | A child session remains addressable; persistence alone does not give it approach ownership. |
| adaptive team portfolio | Teams retain explicit approach charters while membership, work, and allocation evolve under a parent goal. |
| ensemble voting | Agreement aggregates outputs; it does not establish independent evidence or manage work intentions. |
| continual harness refinement | Supplemental harness state changes through its own promotion contract; retasking teams changes assignments instead. |

A team is a coordination identity, not a required process topology. It may use a lead, a shared work registry, or bounded peer routing. Its approach charter identifies the formulation, assumptions, method, and owned question. Roles may shift from hypothesis development to challenge or experiment without silently abandoning that charter.

Alternative formulations can seek different answers to the same research question. Each must explain how its evidence contributes to the parent acceptance criterion. The parent goal/version stays authoritative; local charters can change through recorded transitions. Broadening the parent objective is a separate goal change, not an allocation update.

## Authority boundary

Models propose charters, work intentions, findings, recipient selections, and portfolio changes. The trusted host checks current goal alignment, authorization, versions, and capacity before recording or executing them. Identify whether a human, model-assisted coordinator, or runtime policy chooses among valid proposals.

An accepted allocation does not authorize its tools or side effects. Team membership, peer requests, and shared evidence use the existing permission owners. A split or merge cannot widen authority by combining member scopes. Changes to risk, tools, spending ceilings, or the parent objective follow [planning and authorization rules](planning-and-goals.md#workflow-orchestration).

## State and interfaces

Extend existing goal, workflow, child, and message records with team-specific identities. Do not create a second child registry, budget ledger, or message transport.

| Record | Required distinguishing fields |
|---|---|
| Portfolio | ID and version; parent goal/version reference; current team/charter references; allocation policy reference; decision history |
| Team charter | Team ID and charter version; approach ID/version; formulation, assumptions, method, owned question, boundaries; evidence references; member-registry and budget references; active/draining/retired status |
| Work intent | ID; producing team/charter; question/method/input snapshot/artifact scope; expected evidence; owner; reservation/lease reference; dependencies; purpose; status |
| Finding share | Existing message/artifact ID; producing charter and intent; evidence and validation references; dependencies on received findings; recipients and adoption receipts |
| Portfolio decision | ID; expected portfolio and affected charter versions; proposed transition; cited observations and uncertainty; authorized decision-maker; before/after references; resource changes; disposition of outstanding work |

Charter versions are immutable historical records. Member handles refer to host-owned child identities. Every work intent and finding retains its producing charter even after a team changes approach. Resuming a portfolio rehydrates these references alongside existing goal and child state; a stored active team label does not prove its workers are alive.

Use narrow host-mediated operations with explicit outcomes. The following is an interface sketch, not an implementation dependency:

```text
register_team(charter, expected_portfolio_version, idempotency_key)
  -> applied | denied | stale | no_capacity
declare_work(intent, expected_charter_version, idempotency_key)
  -> reserved | conflict | denied | stale | no_capacity
share_finding(finding_ref, recipient_scope, idempotency_key)
  -> recorded | denied | recipient_unavailable
propose_change(proposal, expected_portfolio_version, idempotency_key)
  -> pending | invalid | stale
apply_change(decision_id, expected_portfolio_version, idempotency_key)
  -> applied | draining | denied | stale | no_capacity
```

Every operation may also return `invalid` for malformed arguments or a conflicting idempotency payload. Each outcome includes its request/record identity, current version, reason, and relevant evidence or conflict references. `pending` means a proposal awaits a host-authorized decision. `recorded` means a share was recorded, not delivered, adopted, or independently verified; use existing delivery semantics for those receipts. `applied` describes a ledger transition, not success of the admitted children. An unavailable recipient must produce an explicit disposition under the existing message contract.

Retries of a committed operation return its recorded outcome. A changed payload under an existing idempotency key is invalid. Proposals referencing an obsolete parent goal or charter are stale and must be re-evaluated, not automatically rewritten against current state.

## Work intent and overlap

Choose differences that affect exploration: formulation, assumptions, method, evidence source, or experiment. Record the reason each approach could add useful coverage and what would challenge it. Share a compact view of active intentions so teams can inspect current ownership before expensive work.

Distinguish four situations:

| Situation | Treatment |
|---|---|
| accidental duplicate | Similar question, method, inputs, and expected evidence; separate scope, hand off, or decline the second claim. |
| competing hypothesis | Same question with a materially different explanation or method; preserve both when justified. |
| intentional replication | Repeated work with a declared validation/reproducibility purpose and bounded resources; record its independence policy. |
| reuse of findings | Consume a cited artifact and disclose that dependence; do not report it as a new independent result. |

A registry can detect declared overlap, not every semantic duplicate. Use a bounded coordinator decision for ambiguous cases. Labels or string hashes alone are insufficient to classify approaches.

Reserve approved work atomically against the current charter and relevant ownership/version. Simultaneous incompatible claims return a conflict with the existing intent; they must not both become exclusive owners. Independent read-only exploration may overlap by policy, while artifact write ownership requires the existing isolation and execution controls.

Intent statuses distinguish reserved, running, completed, failed, and relinquished work. Lease expiry triggers reconciliation; it is not proof that the prior worker stopped. Fence or confirm termination of obsolete writers before granting a conflicting write scope, using existing cancellation contracts. Charge intentional replication separately from unintended repetition.

## Communication and independence

Use team-local exchange and selective cross-team sharing. Direct peer questions and coordinator-consolidated findings are both possible; an all-to-all network is not required. Routing policy should expose current work and useful evidence without flooding every worker with every transcript.

A share carries artifact references, producing charter/intent, source provenance, validation state, and known dependencies. Keep proposed findings, observations, verified claims, and unresolved contradictions distinct. Record whether the receiving team used a finding to change its approach or merely received it.

Cross-pollination can reduce independent evidence. Teams repeating a received claim do not supply independent corroboration. Before a replication or challenge, declare visible findings and whether sharing is delayed until result artifacts are sealed. A verifier may need the claim and original sources while remaining blind to the producer's intermediate reasoning; use [workflow verification](workflow-orchestration.md#verification) for that boundary.

Preserve dissent and counterevidence. A useful finding may justify concentration, but a popular unverified claim is insufficient to retire every alternative. Define a task-specific safeguard such as protected challenge work, delayed sharing, or an exploration reserve; these are design choices to evaluate, not universal quotas.

## Portfolio transitions

Use an evidence-triggered decision loop:

```text
inspect intentions and findings
  -> propose a portfolio change with evidence and opportunity cost
  -> validate goal, versions, authority, ownership, and capacity
  -> record an authorized decision
  -> drain or fence affected work when required
  -> apply charter/member/allocation changes
  -> reconcile outstanding work and results
```

| Transition | Required disposition |
|---|---|
| create | New team identity and charter; explicit differentiating approach; host-admitted members and capacity references. |
| split | New team identities derived from an existing charter; partition or declare overlap in open intents, artifacts, and remaining reservations. |
| merge | Explicit surviving or new identity; reconcile charter differences and member/work ownership; preserve provenance of both approaches. |
| retask | New charter version for the chosen identity; explain the changed method/question and disposition of each old intent. |
| retire | Stop new admissions, drain or cancel outstanding work, retain historical charter/result references and terminal disposition. |

Record why the new allocation is preferable, which observations support it, what remains uncertain, and what exploration or verification it displaces. Separate exploratory concentration from acceptance of a result. Approval to redirect workers is not validation of their shared hypothesis.

Use expected-version checks for the portfolio and affected charters. Record the decision and its outstanding child operations durably; reconcile interrupted execution rather than claiming an atomic transaction across remote workers. If stopping old work is required, return `draining` until termination or fencing is confirmed. No operation may silently release spent budget or duplicate a reservation; [child resource accounting](self-refining-recursive-harnesses.md#resource-limits) remains canonical.

## Failure semantics

| Failure | Required team-specific response |
|---|---|
| duplicate proposal or retry | Return the prior decision/outcome; a retry cannot create another team or debit capacity again. |
| stale portfolio/charter | Reject against current versions and cite the changed record; request a revised proposal. |
| denied change or insufficient capacity | Preserve the current allocation; return the policy/capacity boundary rather than spawning anyway. |
| conflicting intentions | Record the conflict; resolve separate scope, handoff, or intentional replication before admission. |
| interrupted transition | Reconcile each recorded child operation and outstanding reservation before continuing; do not replay ambiguous effects blindly. |
| late result after retasking | Preserve its old charter and disposition; independently assess whether it remains relevant to the current goal. |
| contradiction or unsupported shared claim | Retain conflicting artifacts and their dependencies; route for validation instead of majority-vote acceptance. |
| coordinator or recipient unavailable | Use existing durable recovery/delivery handling; pause affected decisions without inventing adoption or completion. |

A rollback is a recorded transition to a prior or replacement charter with obsolete work fenced. It cannot undo external side effects, erase provenance, or refund actual usage. Generic retries, child termination, and restore controls stay with the existing owners.

## Observability and evidence

Trace charter/version changes, declared overlap, conflict resolution, shares and adoption references, portfolio decisions, outstanding transition operations, and producing charter IDs on results. Reconstruct why a team was created or redirected from durable evidence rather than hidden reasoning.

Link operational usage to the existing aggregate cost records. Distinguish useful independent coverage, intentional replication, accidental repetition, communication overhead, failed work, and unfinished investigations. Completion uses the parent goal's acceptance criterion and [verified integration](workflow-orchestration.md#integration); report unresolved questions and budget-limited coverage explicitly.

## Safe build sequence

1. Establish a measured single-loop investigation with an explicit acceptance criterion.
2. Compare ordinary bounded parallel workers and independent verification using the same tasks and resources.
3. Add a small fixed portfolio with explicit approach charters only where sustained distinct exploration addresses a measured gap.
4. Add work-intent visibility and overlap resolution; preserve declared replication.
5. Add bounded finding exchange and dependence-aware acceptance.
6. Add evidence-linked portfolio transitions with version checks and interrupted-transition reconciliation.

Advance only when the new stage earns its complexity on the task's evaluation. Keep manual allocation and the simpler workflow available as fallbacks; model and topology changes require separate attribution.

## Evaluation requirements

Use [adaptive agent team evals](evals.md#adaptive-agent-team-evals) for matched baselines, mechanism ablations, failure probes, metrics, and launch criteria. This profile defines the contracts those tests exercise; it does not duplicate their matrix or claim that the architecture outperforms a smaller baseline.

## Anti-patterns

- Calling retained children a team portfolio without approach ownership.
- Treating different wording or more agents as demonstrated diversity.
- Preventing all overlap, including useful competing hypotheses and independent replication.
- Treating a work registry as perfect semantic duplicate detection.
- Sharing everything immediately and later counting correlated results as independent checks.
- Retiring alternatives because an unverified finding is popular.
- Expanding the parent goal or permissions under an allocation-change label.
- Changing charters without versioning outstanding work and late results.
- Calling a recorded share delivered, or an admitted team successful.
- Replaying interrupted transitions without reconciling child operations and actual usage.
- Treating agreement, agent scale, or promising findings as the completion criterion.
