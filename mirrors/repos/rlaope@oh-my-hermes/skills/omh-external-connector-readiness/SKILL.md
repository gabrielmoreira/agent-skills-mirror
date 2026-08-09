---
name: omh-external-connector-readiness
description: [omh] External connector readiness - assess whether a named plugin, connector, API, data provider, or multimodal route is safe, affordable, fresh, and observable; use executor-runtime-readiness for coding-owner choice and toolbelt-readiness for missing capability inventory. Use when the user says: external-connector-readiness, external connector readiness, connector readiness matrix, plugin readiness matrix, provider readiness, api readiness, connector adoption, external plugin adoption.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, connector]
    category: connector
    phase: connector-readiness
    role: guide
    quality_tier: workflow-surface-gated
---

# External Connector Readiness

This is a Hermes-native `external-connector-readiness` workflow skill.

## Why This Exists

`external-connector-readiness` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: external-connector-readiness compare weather plugin and wxtrain candidates with cost, freshness, multimodal evidence, and fallback routes before adoption.
- Expected behavior: Produce `prepare_external_connector_readiness` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: external-connector-readiness silently enable a paid connector and claim weather, SQL, and screenshot results without observed provider evidence.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- Candidate connector, target domain, read/write scope, modality needs, provider owner, fallback workflow, and stop condition are explicit.
- Cost, quota, credential, permission, live-data freshness, multimodal capture, safety, and compliance boundaries are marked ready, missing, risky, or not_observed.
- Route live read-only lookups to live-info-operator, external writes to connector-operator, datasets/SQL to data-analysis, and missing tools to toolbelt-readiness before claiming results.
- Provider responses, screenshots, audio/video/file captures, query outputs, message ids, and external mutations are reported only from observed trial evidence.

## Recovery Notes

- If the candidate list is unknown, route to skill-scout or source-finder before readiness scoring.
- If credentials, cost authority, or connector installation is missing, keep readiness blocked and route setup to toolbelt-readiness.
- If a specific provider action is already selected, route read-only live data to live-info-operator or write/mutation tasks to connector-operator.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use before adopting, enabling, or routing an external plugin/connector/API when Hermes must compare capability, auth, cost, modality, freshness, safety, fallback, and observable trial evidence.

    Strong routing signals: `external-connector-readiness`, `external connector readiness`, `connector readiness matrix`, `plugin readiness matrix`, `provider readiness`, `api readiness`, `connector adoption`, `external plugin adoption`, `weather plugin readiness`, `weather connector readiness`, `wxtrain readiness`, `onequery read-only sql`, `read-only sql connector`, `sql connector readiness`, `nextcloud connector`, `microsoft workspace connector`, `microsoft graph connector`, `chainlink connector`, `solana connector`, `monero gateway`, `xmr gateway`, `private crypto transaction`, `private cryptocurrency connector`, `crypto transaction plugin`, `blockchain gateway`, `composio connector`, `composio universal cli`, `universal cli connector`, `universal cli skill adoption`, `skill connector adoption`, `connector auth risk`, `connector cost auth risk`, `agentchat connector`, `peer-to-peer agent messaging connector`, `websocket identity connector`, `websocket connector trial`, `clawsocial connector`, `social discovery connector`, `windy pairing`, `windymail mailbox connector`, `matrix chat identity`, `antigravity cli connector`, `agy cli bridge`, `agy bridge connector`, `macos keychain oauth connector`, `oracle oci connector`, `oracle genai connector`, `miniverse bridge`, `crustocean platform connector`, `cost-aware connector`, `multimodal connector`, `multimodal routing`, `screenshot connector`, `audio connector`, `video connector`, `video generation`, `generate a video`, `product demo video`, `text to video`, `home assistant connector`, `home assistant integration`, `home assistant device control`, `home assistant smart home`, `smart home connector`, `device control connector`, `plugin auto-routing`, `connector auto-routing`, `external tool trial`, `커넥터 준비도`, `외부 커넥터 준비`, `외부 플러그인 채택`, `플러그인 준비도`, `커넥터 도입`, `플러그인 도입`, `비용 인증 리스크`, `인증 리스크`, `도입 비용`, `비용 기준 커넥터`, `자동 라우팅`, `멀티모달 커넥터`, `멀티모달 라우팅`, `영상 생성`, `제품 데모 영상`, `홈 어시스턴트 커넥터`, `홈 어시스턴트 연동`, `홈 어시스턴트 기기 제어`, `홈 어시스턴트 스마트홈`, `홈어시스턴트 커넥터`, `홈어시스턴트 연동`, `홈어시스턴트 기기 제어`, `홈어시스턴트 스마트홈`, `스마트홈 커넥터`

## Catalog Metadata

Category: `connector`
Phase: `connector-readiness`
Hermes role: `guide`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- external_connector_readiness_card/v1
- connector_capability_matrix/v1
- auth_cost_boundary/v1
- live_data_freshness_policy/v1 when live data is required
- multimodal_routing_policy/v1 when screenshots, audio, video, or files are involved
- fallback_route_policy/v1
- connector_trial_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

Artifact expectations:

- external_connector_readiness_card/v1 metadata-only wrapper card when prepared
- connector_capability_matrix/v1 with candidate, domain, read/write shape, modality, owner workflow, and fallback route
- auth_cost_boundary/v1 separating missing connector, missing credentials, paid/provider cost risk, quota, and user authority
- live_data_freshness_policy/v1 for requested recency, provider timestamp, stale-result handling, and source-quality thresholds
- multimodal_routing_policy/v1 for screenshot, audio, video, file, OCR, or visual QA evidence routes when needed
- connector_trial_manifest/v1 only when a provider response, capture id, query transcript, message id, or tool-call observation is recorded

Safety rules:

- An external connector readiness card is not connector installation, credential validation, provider access, API invocation, multimodal capture, live-data retrieval, external mutation, cost authorization, or successful trial evidence unless observed connector-trial evidence records it.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `external-connector-readiness`.

```sh
omh runtime record --skill external-connector-readiness --harness external-connector-readiness --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
