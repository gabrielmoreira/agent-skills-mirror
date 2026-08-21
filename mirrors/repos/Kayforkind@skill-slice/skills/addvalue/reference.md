# addvalue — reference

## Opportunity card schema

Use one card per candidate (keep short):

```yaml
id: short-kebab
title: One-line capability or fix
kind: bug | feature | ux | docs | perf | security | platform
source: issue URL | local observation | docs gap
impact: 1-5
leverage: 1-5
fit: 1-5
feasibility: 1-5
novelty: 1-5
risk: 1-5   # higher = more dangerous
score: <computed>
why_not: optional reject reason
```

**score** = impact + leverage + fit + feasibility + novelty − risk

## Target intake checklist

```
[ ] Name / path
[ ] License allows contribution (if upstream)
[ ] CONTRIBUTING / AI_POLICY read
[ ] Primary verify command known
[ ] Open PR / issue collision check done
[ ] User intent: roadmap | fix | upstream PR
```

## Upstream collision check (GitHub)

```powershell
gh repo view OWNER/REPO --json description,stargazerCount,pushedAt,url
gh issue list --repo OWNER/REPO --state open --limit 30
gh pr list --repo OWNER/REPO --state open --limit 30
gh issue view N --repo OWNER/REPO
gh pr list --repo OWNER/REPO --search "N" --state all --limit 10
```

## Local / non-git targets

Treat the folder as the product:

1. Find run/build/test entrypoints (`package.json`, `pyproject.toml`, `Makefile`, `README`)
2. Exercise the happy path once
3. Note friction, missing features, brittle edges
4. Prefer improvements the owner can demo in <5 minutes

## Partner prompt skeleton (Ollama / agy)

Pass **paths and titles**, not whole repos:

```
Target: <path or OWNER/REPO>
Intent: <one sentence>
Constraints: <AI policy, max PRs, stack>
Signals: <bullet list of issue titles + 3 friction notes>
Ask: Rank 5 opportunities with scores; pick one winner; give a 6-step implement plan.
Do not invent files that were not listed.
```

## Inspiration prompts (force non-bug thinking)

Ask yourself (or the partner):

1. What does a power user do with workarounds today?
2. What error message have I seen that dumps a stack with no fix hint?
3. What config is possible but undocumented?
4. What sibling tool does better that this project could absorb tastefully?
5. What would make the next contributor succeed without asking Slack?

## Ship bar

| Kind | Minimum evidence |
|------|------------------|
| Bug | Failing test → pass, or recorded repro before/after |
| Feature | Acceptance checks listed + automated or scripted demo |
| Docs | Followed the new path cold |
| UX | Before/after of the message or flow |
