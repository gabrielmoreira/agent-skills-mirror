---
name: omh-memory-sync
description: [omh] English-canonical Hermes memory-review guidance: inspect USER.md and MEMORY.md claims and prepare a native write diff without invoking, applying, or observing a native write; for a new fact use memory-new, and for a past decision use decision-recall. Use when the user says: memory-sync, memory curation, memory review, memory inspect, memory check, memory update, context cleanup, curate memory.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, memory]
    category: memory
    phase: curation-review
    role: memory-keeper
    quality_tier: workflow-surface-gated
---

# Memory Sync

This is a Hermes-native `memory-sync` workflow skill.

## Why This Exists

`memory-sync` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: memory-sync inspect stale MEMORY.md claims, prepare a native write diff, and ask which claims to keep, revise, or archive.
- Expected behavior: Produce `prepare_memory_sync` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: memory-sync claim a prepared native diff changed MEMORY.md or USER.md.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Workflow Lane

- Current lane: **Retained knowledge** (`memory-new`, `memory-sync`, `decision-recall`, `wiki`) - memory, rejected alternatives, wiki notes, retrieval, and staleness.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## English-Canonical Interview Protocol

- **Inventory (목록)** - Nobody hands you the material: call `omh_memory` with `action="status"` to get the entry inventory - per-file entry counts, per-entry index and size, headroom, and which entries have no OMH record. It returns counts and hashes, never entry text, because the text is already yours.
- **Claim extraction (추출)** - Break the `USER.md` and `MEMORY.md` material into claims. Quote only observed claims; never invent provenance.
- **Provenance (출처)** - Ask for the source class and distinguish Hermes-native, provider, and vector material as `not_omh_reviewed`.
- **Target (대상)** - Review existing native-memory claims only. Route a new project/product fact to `memory-new`.
- **Per-entry confirmation (확인)** - Walk the inventory in order. For each entry, quote it back from your own memory file and state what you take it to mean, then ask the user to keep, revise, or archive it before moving on. Do not summarize the whole file and ask one question about all of it; a review the user cannot correct entry by entry is not a review.
- **Review (검토)** - Prioritize stale, conflicting, duplicate, and overgeneralized claims. Offer keep, revise, or archive choices; do not describe an archive as removal.
- **Attention (주의)** - For a reviewed OMH-local record, keep/archive is an attention tier: `active` leads the working context, `reference` stays recallable behind active peers, `archive` leaves default recall. Preview with `omh memory attention <record-id> --tier <tier>`, say which records stay in the working context and which leave it, then apply with `--apply` only after the user agrees. The preview writes nothing.
- **Diff (차이)** - Prepare one concise native write diff with before/after claims and counts. Keep the caps: MEMORY.md about 2,200 characters and USER.md about 1,375 characters.
- **Native-write boundary (쓰기)** - This skill can prepare guidance and a native write diff only. It never invokes, applies, or observes a `MEMORY.md`/`USER.md` write.

## Memory Boundaries

The prepared artifact is `memory_curation_review/v1`, not native-memory mutation evidence. Hermes-native and external provider/vector context is `not_omh_reviewed`: it can nominate an OMH candidate but never inherits OMH approval. A configured Hermes runtime may transmit rendered OMH prefetch content in its model request.

Use lifecycle words literally: expire removes influence only; retire archives recoverably; restore creates a new pending revision while preserving the archive; prune hard-deletes only the manifest-declared OMH-local target set. Report restore and prune first. No lifecycle result proves anything outside that named local target set.

An attention tier is not a lifecycle state, and the two uses of "archive" are different: the `archive` tier only stops a record from occupying the default working context, leaving it in the store, readable, and answerable by `omh memory recall --include-archived`, while `retire` moves an expired revision into the local archive directory. Neither is deletion; never describe either as one.

Legacy v1 material is migration/review-required. Present `memory inventory` counts and the report-first per-artifact `memory reactivate ... --apply` path; inventory and reactivation never silently grant replay eligibility.

Dreaming runs automatically in reminder mode at five scheduler points: `turn` when the interval is due (default five turns), `compaction` before compression discards messages, `session_end` after a productive session, `shutdown` as the final process opportunity, and `session_start_recovery` when the prior session ended without consolidation. It prepares reminders for duplicate clusters, records at or near their deadline, headroom below the configured floor, `stale_review_required`, and `expired_volatile_records`; an unchanged standing condition is suppressed until its value changes. Anything whose source OMH cannot explain is not a candidate. Dreaming never invokes a model or performs consolidation, retirement, restore, or prune.

Treat ranking signals within their limits: pins guarantee inclusion but never override expiry, scope, perspective, or review eligibility; attention tiers control working-context occupancy, not truth; `approved_manual` has 100% veracity weight and `approved_auto_safe` 90%, while an unknown approval mode fails closed to the lower weight; age only breaks ties within an equal relevance rank; and usage uses saturating buckets so repeated delivery cannot compound into a permanent lead.

Normal users use natural-language Hermes chat. `omh memory ...` commands are agent/operator control-plane references, not normal-user setup.

## Use When

Use when existing Hermes USER.md, MEMORY.md, or accumulated skill memories need an English-canonical, claim-by-claim review. It prepares native write guidance only; it never invokes, applies, or observes a native write. Do not use for new project or product candidates.

    Strong routing signals: `memory-sync`, `memory curation`, `memory review`, `memory inspect`, `memory check`, `memory update`, `context cleanup`, `curate memory`, `stale memory`, `hermes remembers`, `conflicting memory`, `duplicate skill`, `MEMORY.md`, `USER.md`, `기억하고 있는`, `기억하고 있는 프로젝트 맥락`, `기억하는 맥락`, `현재 hermes가 기억하는 맥락`, `현재 헤르메스가 기억하는 맥락`, `헤르메스가 기억하는 맥락`, `오래된 맥락`, `오래된 기억`, `기억 점검`, `기억 정리`, `메모리 업데이트`, `메모리 검사`, `메모리 점검`, `메모리 정리`, `맥락 점검`, `맥락 정리`, `맥락 피드백`, `등록된 맥락`, `헤르메스 기억`, `중복 스킬`, `나에 대해 잘못 알고`, `저장된 내 정보`, `너한테 저장된`, `저장된 프로필`, `기억 바로잡`, `what you remember about me`, `your memory about me`

## Catalog Metadata

Category: `memory`
Phase: `curation-review`
Hermes role: `memory-keeper`
Quality tier: `workflow-surface-gated`
Reasoning demand: `light`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.
- State that Hermes-native and external provider/vector context is not_omh_reviewed, can nominate a candidate only, and may receive rendered OMH prefetch content through a configured Hermes runtime model request.

Handoff policy:

Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- memory-sync/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- memory-sync/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A memory-sync review is prompt guidance only. It can prepare a native MEMORY.md or USER.md write diff but never invokes, applies, or observes that write. Hermes-native and external provider/vector context is not_omh_reviewed and never inherits OMH approval.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.
- Keep English as the canonical protocol; Korean routing triggers and concise Korean help labels remain available.
- Quote claims only when observed, do not invent provenance, and keep the prepared native diff separate from any native write.

## Runtime Evidence

Preferred harness for this skill: `memory-sync`.

```sh
omh runtime record --skill memory-sync --harness memory-sync --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
