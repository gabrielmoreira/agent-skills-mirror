---
name: ollama
description: >-
  Calls Ollama Cloud for GLM 5.2 at high reasoning, then executes the returned
  plan. Use when the user types /ollama, says Ollama Cloud, cloud GLM, or asks
  to plan/execute via Ollama Cloud GLM 5.2. Not for local GPU Ollama (use
  ollama-local-setup). Never localhost:11434 for this chair. Never print
  OLLAMA_API_KEY.
disable-model-invocation: true
---

# /ollama — Ollama Cloud GLM 5.2

One capability: **Ollama Cloud API** as planner, then execute in this session.

This is **not** local GPU Ollama. Local install/run belongs to `ollama-local-setup`.

Official Cloud docs: https://docs.ollama.com/cloud

## When to Use

- User runs `/ollama <task>` or says Ollama Cloud / cloud GLM 5.2.
- User wants a Cloud GLM plan, then this agent to execute it.

**Do not use** for:

- Local models on `http://localhost:11434` — `ollama-local-setup` (and `/local` if that rule is installed).
- Robotics, hardware bring-up, or generic “run any LLM” tasks.
- Substituting Cloudflare GLM MCP when the user asked for `/ollama`.

## Prerequisites

- Env `OLLAMA_API_KEY` already set (create at https://ollama.com/settings/keys). **Never print the key.**
- Network to `https://ollama.com`.
- Optional helper on disk: `$env:LOCALAPPDATA\hermes\scripts\ollama_cloud_api.py` — use if present; do not require a machine-specific path.

## API contract

| Setting | Value | Source |
|--------|--------|--------|
| Native Cloud host | `https://ollama.com` | [docs.ollama.com/cloud](https://docs.ollama.com/cloud) |
| Native chat | `POST https://ollama.com/api/chat` | same |
| OpenAI-compatible | `POST https://ollama.com/v1/chat/completions` | Ollama as remote host + OpenAI compat |
| Auth | `Authorization: Bearer` + env `OLLAMA_API_KEY` | [docs.ollama.com/api/authentication](https://docs.ollama.com/api/authentication) |
| Default model | `glm-5.2` (no `:cloud` suffix on the Cloud host) | this chair |
| Reasoning | `reasoning_effort: "high"` | OpenAI-compat field; omit `max_tokens` unless the user caps |

## Procedure

1. **Parse the task** after `/ollama`. If missing, ask once.
2. **Gather minimal context** — file paths, not huge dumps.
3. **Call Cloud** (prefer the helper if the file exists; else curl). Do not print the key. Do not use `localhost:11434`. Do not use `ollama run glm-5.2:cloud` as a substitute for this chair.
4. **Execute** the returned steps (adapt for safety, project rules, PowerShell).
5. **Verify** with the project’s checks or the verification GLM specified.
6. **Report** what GLM decided, what ran, evidence, blockers.

### Native Cloud call (documented)

```powershell
curl.exe -sS https://ollama.com/api/chat `
  -H "Authorization: Bearer $env:OLLAMA_API_KEY" `
  -H "Content-Type: application/json" `
  -d '{"model":"glm-5.2","stream":false,"messages":[{"role":"user","content":"<TASK>"}]}'
```

### OpenAI-compatible call (remote host)

```powershell
curl.exe -sS https://ollama.com/v1/chat/completions `
  -H "Authorization: Bearer $env:OLLAMA_API_KEY" `
  -H "Content-Type: application/json" `
  -d '{"model":"glm-5.2","reasoning_effort":"high","messages":[{"role":"user","content":"<TASK>"}]}'
```

### Optional helper

```powershell
$helper = Join-Path $env:LOCALAPPDATA "hermes\scripts\ollama_cloud_api.py"
if (Test-Path $helper) {
  python $helper agent "<TASK>" --reasoning high
}
```

## Modes

| User says | Behavior |
|-----------|----------|
| `/ollama …` (default) | Plan via Cloud **then execute** |
| `/ollama plan …` or “plan only” | Call Cloud, present plan, **stop** |
| `/ollama <other-model> …` | Use that Cloud model id if listed by `GET https://ollama.com/api/tags`; else `glm-5.2` |

## Anti-patterns

- `http://localhost:11434` for `/ollama`
- `ollama run glm-5.2:cloud` instead of the API-key Cloud host
- Cloudflare `ask_glm_5_2` when the user asked `/ollama`
- Echoing or embedding `OLLAMA_API_KEY`
- Passing `max_tokens` by default
- Stopping after the plan when the user wanted the job done
- Robotics / TODO boilerplate — out of scope

## Related

- **`ollama-local-setup`** — local GPU Ollama on `localhost:11434` (install, verify script).
- Official Cloud: https://docs.ollama.com/cloud
- Model card: https://ollama.com/library/glm-5.2
