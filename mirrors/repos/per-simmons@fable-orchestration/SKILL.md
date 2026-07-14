---
name: fable-orchestration
description: How to prompt Claude Fable 5 so it ORCHESTRATES a build correctly and cheaply — Fable as the architect/advisor that plans and delegates while Opus 4.8 does the token-heavy execution. Covers the two wiring patterns (advisor mode + architect-and-delegate), effort-level routing as the cost lever, parallel subagents, verification loops, and the failure modes that silently reroute Fable to Opus or tank its output. Use whenever setting up or prompting a Fable-driven pipeline (e.g. the Damon / agent-harness build), or when someone says "prompt Fable," "Fable orchestration," "advisor mode," "route Fable to Opus," "Fable as the architect," or "make Fable delegate."
---

# Fable 5 Orchestration

Fable = architect only (~5–15% of the work: high-level structure + ambiguous judgment). **Opus 4.8 does everything else** — research, execution, verification. No Sonnet.

The loop: **Opus 4.8 researches → Fable architects → Opus 4.8 executes → Opus 4.8 verifies.** Fable only touches the middle step; you pay its rate only for the thinking that needs it.

Without a Claude Code subscription you can drop Fable entirely and run **GPT-5.6 Sol as the architect** instead — it's close enough now that the cost math often wins. See [Add GPT-5.6 Sol (Codex)](#add-gpt-56-sol-codex--solo-or-in-tandem-with-fable) below.

## Wire it (pick one)

- **Advisor mode** — set active model to **Opus 4.8**, then `/advisor fable`. Opus writes everything; Fable steers when Opus is stuck. One clean session. Simplest to run/film.
- **Architect + delegate** — Fable writes the plan, then **parallel Opus 4.8 subagents** (or a separate Opus 4.8 session) execute it. Bigger spectacle: a rail of Opus agents building while Fable conducts.

## Effort = the cost lever

`/effort low|medium|high|xhigh|max`. **Cap at `high` — avoid `xhigh` and `max`.** On Fable they usually make things worse: it over-reasons, runs in loops, and ships overdone code with too many changes at a much higher cost. Higher effort doesn't let it work longer or solve harder problems — it just thinks more per step. Use `low`/`medium` for routine work (Fable low often beats prior models at their max, for a fraction of the cost); `high` is the ceiling.

## Add GPT-5.6 Sol (Codex) — solo, or in tandem with Fable

Fable is still the sharpest orchestrator, but **GPT-5.6 Sol is now right behind it for a fraction of the cost** (roughly $5/$30 per million tokens vs Fable's $10/$50). Two ways to run it, depending on whether you already pay for Claude Code.

**No Claude Code subscription — run Sol on its own.** Use the Codex CLI directly; Sol plans and builds the whole thing itself:

```
codex exec -m gpt-5.6-sol "<the build task>"
```

`gpt-5.6-sol` is the model id. Keep effort matched to difficulty (medium/high for most work; skip the top `ultra` tier, which burns tokens for little gain).

**Have Claude Code + a ChatGPT account — run them in tandem.** Sign Codex into Claude Code with OpenAI's official plugin, then let Fable orchestrate and delegate implementation to Sol. Needs a ChatGPT plan (or OpenAI API key) and Node 18.18+:

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

Then sign in with `!codex login` (ChatGPT account or API key); usage counts against your Codex limits. Now **Fable architects up top and delegates implementation** to Opus 4.8 agents and to Sol via the plugin's `/codex:*` commands.

Which you pick is a budget call: on cost alone Sol-only is the easy default; if you already have Claude Code, Fable as the top conductor with Sol underneath is still a touch sharper all around.

## Paste-in prompt kit

Drop into the Fable setup's system prompt / CLAUDE.md / skills. Short instructions steer better than rule-piles — state each behavior once.

**Act, don't overplan:**
```
When you have enough information to act, act. Don't re-derive established facts, re-litigate a settled decision, or narrate options you won't pursue. If weighing a choice, give a recommendation, not a survey.
```
**No unrequested tidying/refactor:**
```
Don't add features, refactor, or introduce abstractions beyond what the task requires. Do the simplest thing that works. Only validate at system boundaries; don't handle scenarios that can't happen.
```
**Delegate to subagents:**
```
Delegate independent subtasks to subagents and keep working while they run. Prefer async over blocking until each returns. Intervene only if a subagent goes off track or lacks context.
```
**Ground progress claims:**
```
Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if unverified, say so. If tests fail, say so with the output.
```
**State the boundaries:**
```
When the user is describing a problem or asking a question rather than requesting a change, the deliverable is your assessment — report and stop; don't fix until asked. Before a state-changing command, check the evidence supports that specific action.
```
**Verify with fresh eyes:**
```
Every [interval], verify your work with a fresh subagent against the specification.
```
**Give the why:**
```
I'm working on [larger task] for [who it's for]. They need [what the output enables]. With that in mind: [request].
```
**Autonomous run:**
```
You're operating autonomously; the user can't answer mid-task, so don't ask "Want me to…?". For reversible actions that follow from the request, proceed. Before ending your turn, if your last paragraph is a plan, a question, or a promise ("I'll…"), do that work now. End only when done or blocked on user-only input.
```
**Memory:**
```
Store one lesson per file, one-line summary at top. Record corrections and confirmed approaches and why they mattered. Don't duplicate what the repo records; update rather than duplicate; delete notes that turn out wrong.
```

## Hard don'ts

- **Never tell Fable to show/echo/"explain your reasoning" in the response** — trips the reasoning-extraction classifier and **silently reroutes to Opus 4.8**. Audit system prompts/skills for it. For visibility, read the `thinking` blocks instead.
- **Don't over-instruct.** Strip legacy rule-piles; a brief instruction steers Fable better.
- **Don't block on subagents** — bottlenecks on the slowest, burns context.
- **Don't predefine subagent archetypes** (reviewer, adversarial, explorer). Fable invents the right roles per task — prescribing them just narrows it.
- **Don't leave effort on high for routine work.**
- **Don't send research/boilerplate to Fable** — that's Opus 4.8 work; hand Fable the results.

## Pre-run checklist

1. Is Fable actually needed for this step, or does Opus 4.8 take it? (~5–15% Fable.)
2. Effort matched to difficulty, not defaulted to high?
3. Advisor mode or architect+delegate wired?
4. System prompt free of any "show/explain your reasoning" language?
5. Delegate + verify + boundaries blocks in place?
