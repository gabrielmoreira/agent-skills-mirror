---
name: orchestration-bundle-candidate
description: Select one route and return one adaptive one-to-four-workgroup bundle candidate as reply-only evidence.
---

# Orchestration Bundle Candidate

Use this skill once per immaculate orchestrator activation. Consume only the
controller-supplied task packet, execution contract, detail artifacts,
effective-capacity snapshot, and expected bundle revision.

## Reply Contract

1. Return exactly one route decision:
   `direct_execution`, `needs_detail`, `macro_adjustment_request`, `blocked`,
   or `partial_completion`.
2. Return compact `orchestration_notes` citing the supplied task and contract
   refs.
3. For Config V3 `direct_execution` or `partial_completion`, always include
   exactly one `orchestration_bundle:` heading immediately followed by a code
   fence whose language tag is literally `json`. Put the schema identifier
   `ccb.loop.orchestration_bundle_candidate.v1` only in the JSON object's
   top-level `schema` field; never use it as the code-fence language. Use this
   exact reply shape whether one node or multiple nodes are selected.
4. Config V2 may omit the candidate only for deterministic one-node
   compatibility. A decomposed Config V2 route must include it.

Candidate root fields are exactly `schema`, `task_id`, `bundle_revision`,
`selection`, `nodes`, `integration`, and `policy`. Selection fields are exactly
`workgroup_count`, `complexity`, `cutability`, `execution_shape`, and
`rationale`. `workgroup_count` must equal the node count. `rationale` must be
one non-empty line of at most 500 characters; target 300 characters or fewer
and do not repeat node work packets in it. `integration` fields
are exactly `verification_refs` and `project_root_verification_refs`; do not
emit `mode`, `order`, merge strategy, dependency order, execution order, or
controller-owned integration settings. Both integration arrays must be
non-empty and must reference known task artifacts containing direct
verification commands. For a one-node bundle, copy the execution-contract
artifact ref into both `verification_refs` and
`project_root_verification_refs`; never emit an empty
`project_root_verification_refs` list. `policy` fields are exactly
`max_node_rework_rounds`, `on_required_node_failure`, and
`on_structural_failure`; do not emit capacity, workspace, release, topology, or
runtime policy fields. Policy values are literal: `max_node_rework_rounds`
must be the supplied integer within policy, `on_required_node_failure` must be
`partial_or_blocked`, and `on_structural_failure` must be `replan_required`.
Do not replace these with semantic alternatives such as rework, retry,
return_failed_node_for_rework, fail, abort, or controller_owned.

## Adaptive Selection

Choose the smallest justified workgroup count from 1 to 4 using task
complexity, cutability, independently reviewable scopes, explicit dependency
needs, and supplied effective-capacity evidence. Capacity is a ceiling, not a
target. Do not target a desired count, split work to fill capacity, or reduce a
semantically required count because dispatch would be inconvenient.

Use one node for atomic or tightly coupled work. Use additional nodes only
when every node has a complete bounded work packet, independently checkable
acceptance and verification refs, safe allowed paths, and explicit
dependencies where outputs interact. Independent nodes require disjoint
allowed paths.

Apply these selection rules before emitting the candidate:

- If two or more units have disjoint allowed paths, independently observable
  acceptance, and can implement against already declared interfaces without
  consuming a predecessor's new output, emit separate nodes in the same ready
  parallel group. This is required parallelism, not capacity filling.
- A shared package, stable API, product-level acceptance document, or final
  project verification command does not make units inseparable. Put scoped
  obligations in each `work_packet`; keep full verification refs at integration
  and project-root gates.
- Add dependencies only for real data, schema, generated artifact, or accepted
  predecessor evidence. Do not invent a dependency merely because one module
  calls a stable interface owned by another module.
- Treat an interface as stable only when the supplied artifacts give the exact
  module/import path and callable/signature, CLI contract, or data/error shape
  required by cross-node consumers. Behavioral acceptance prose is not enough.
  If a downstream implementation, test, or documentation example would need to
  guess a new symbol name, signature, or output shape, add the producer as a
  dependency or keep the work in one node.
- Use `serial` or `mixed_dag` only when `Unresolved ordering constraints
  requiring predecessor output` names a newly produced artifact or accepted
  result. Calls and examples against a concrete supplied interface and final
  root verification do not justify a dependency edge; guessed APIs do.
- Use one node only when candidate units have unavoidable path overlap or one
  cannot be implemented and reviewed against the supplied contract without a
  predecessor result. State that concrete reason in `selection.rationale`.
- For three or four such units, preserve all justified independent nodes up to
  the supplied capacity. Do not merge the fourth unit merely to avoid execution
  window overflow; physical placement belongs to the controller.

Each node must include `node_id`, `workgroup_id`, `worker_profile`,
`reviewer_profile`, `depends_on`, `parallel_group`, a complete bounded
`work_packet`, `allowed_paths`, `acceptance_refs`, `verification_refs`, and a
unique deterministic `integration_order`. Set `worker_profile` to `coder` and
`reviewer_profile` to `code_reviewer`. Do not emit nested `coder` or
`code_reviewer` objects; put role-specific instructions inside `work_packet`.
`node_id` and `workgroup_id` must be short agent-name-safe identifiers: start
with a letter, use only letters, digits, `_`, or `-`, and contain at most 32
characters total. Prefer compact IDs such as `node-001`, `node-cli`, `wg-001`,
or `wg-cli`; do not use long task-title slugs.
`work_packet` must be one JSON string, not an object, array, or nested schema.
The work packet string must state its goal, declared refs, scope, non-goals,
dependency evidence, expected evidence, and verification obligations.
`parallel_group` is evidence only; it is not a topology communication edge or
dispatch instruction.

Every `verification_refs` and `project_root_verification_refs` artifact must
contain a `Verification:` or `Verification Commands:` section whose bullet
items are direct argv commands. They are executed without a shell by the
controller. Do not rely on `Verification Contract:` prose, `&&`, pipes,
redirection, command substitution, variable assignment, `cd`, `source`, or
`export`. If supplied refs do not contain bounded direct verification commands,
return structural `replan_required` evidence instead of emitting an execution
bundle.

Structural ambiguity requires `replan_required` evidence. Do not hide it with
silent serialization, count reduction, overlapping independent scopes, scope
shrinkage, fallback, or degradation.

## Authority Boundary

- Reply only; do not run `ccb`, `ccb_test`, wrappers, provider CLIs, or
  authority commands.
- Do not submit downstream asks or dispatch any role.
- Do not create task artifacts, work packets, tasks, loops, topology, agent
  names, panes, sessions, worktrees, branches, commits, or status transitions.
- The controller validates and imports candidate evidence, binds concrete
  agents, submits asks, integrates reviewed results, promotes or rolls back,
  records authority, and releases dynamic roles.
- Provider and model selection remain project configuration concerns. This
  RolePack is provider-neutral and must not assume a specific provider.
- There is no normal post-worker orchestrator activation. Only structural
  replan starts a new immaculate activation.
