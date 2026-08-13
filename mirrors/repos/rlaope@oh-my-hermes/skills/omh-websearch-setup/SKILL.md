---
name: omh-websearch-setup
description: [omh] Hermes Web Search Setup workflow: diagnose scraper and auxiliary extract-model configuration, guide account setup, and apply each change as its own diff approval. Use when the user says: websearch-setup, web search setup, make web search cheaper, set up web search, configure web search, reduce web search cost, connect scraper api key, set up auxiliary web-extract model.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, hermes-setup]
    category: hermes-setup
    phase: setup
    role: guide
    quality_tier: hermes-setup-gated
---

# Websearch Setup

This is a Hermes-native `websearch-setup` workflow skill.

## Why This Exists

`websearch-setup` exists to make web search cost and routing configurable through two clearly separated, diff-approved steps instead of one opaque edit.

## Do Not Use When

- The user wants Hermes to run a web search now, not configure how web search is set up.
- No scraper key or auxiliary extract-model intent has been named yet.
- The request needs a repository code change rather than a local `.env` or routing edit.

## Examples

Good example:

- Prompt: make web search cheaper — I have a scraper account I want to use, and I want an auxiliary model handling extraction.
- Expected behavior: Diagnose the current `.env` and routing state, guide the scraper API key setup as one diff approval, then the auxiliary web-extract model routing as a second, separate diff approval.
- Why: The request needs the two independently-approved writes this skill exists to keep separate.

Bad example:

- Prompt: websearch-setup: search the web for the latest news.
- Expected behavior: Run or route to the search request directly instead of starting a setup walkthrough.
- Why: A live search request is not a configuration request.

## Completion Checklist

- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- The scraper API key write and the auxiliary web-extract model write were verified as two separate, independently-approved changes.

## Recovery Notes

- If the scraper provider prerequisite is unmet, mark that step "not applicable" and continue with the auxiliary model routing step alone.
- If either diff is rejected, keep the other step's state independent and do not roll both back together.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `buzz`, `agent-board`, `gateway-intent-card`, `+34 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user wants to reduce web search cost or configure web search by setting up a scraper API key or an auxiliary web-extract model routing block, following the shared prerequisite-check, diagnose, guide, diff-approved apply, and verify contract.

    Strong routing signals: `websearch-setup`, `web search setup`, `make web search cheaper`, `set up web search`, `configure web search`, `reduce web search cost`, `connect scraper api key`, `set up auxiliary web-extract model`, `웹 검색 싸게 만들어줘`, `웹 검색 설정`, `웹서치 설정`, `웹 검색 비용 줄이기`

## Catalog Metadata

Category: `hermes-setup`
Phase: `setup`
Hermes role: `guide`
Quality tier: `hermes-setup-gated`
Reasoning demand: `light`

Quality bar:

- Prerequisite check: confirm the subscription, account, or capability the step needs exists before continuing; mark unmet prerequisites "not applicable" and skip them explicitly.
- Read-only diagnose: read the current Hermes config, `.env` keys, and installed version without writing anything.
- Guide: walk the user through any account creation, OAuth, or token issuance they must complete themselves.
- Diff-approved apply: show the exact config or `.env` diff and write only after the user explicitly approves it.
- Verify: re-read the updated config and report a completion checklist covering every applicable item.
- Show the scraper API key diff as one diff approval and the auxiliary web-extract model routing diff as a second, separate diff approval; never merge them.

Handoff policy:

Run diagnosis and guidance directly in Hermes for web search setup. Diagnosis only reads the existing Hermes config, `.env` keys, and installed version; it never writes anything on its own. Show the exact diff for any config or `.env` change and write it only after the user explicitly approves that diff. Secret values such as tokens and API keys are pasted by the user directly in chat and are never stored, logged, or echoed back beyond the immediate diff confirmation. Delegate to a selected coding executor only if the user needs a change outside chat-driven config or `.env` edits.

Required inputs:

- scraper API key issued by the user's chosen web-extraction provider
- target auxiliary web-extract model role slot

Expected outputs:

- read-only diagnosis of the current scraper `.env` key and auxiliary web-extract model routing state
- a diff-approved `.env` write adding the scraper API key, approved on its own
- a diff-approved routing block change assigning the auxiliary web-extract model, approved separately from the key write
- verification checklist confirming both writes were applied

Artifact expectations:

- setup verification note when the wrapper captures it

Safety rules:

- Never combine the scraper API key `.env` write and the auxiliary web-extract model routing write into a single apply step; each gets its own diff and its own approval.
- Do not name a specific scraper product, extract-model provider, or price; ask the user which provider they hold an account with and read the current config instead of assuming one.

## Runtime Evidence

Preferred harness for this skill: `coding-handling`.

```sh
omh runtime record --skill websearch-setup --harness coding-handling --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
