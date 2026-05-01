---
name: openrouter-free-failover
description: Configure and maintain optimal OpenRouter free model failover for OpenClaw. Prioritized cascade of free models ranked by coding capability, with automatic failover on rate limits, downtime, and errors. Load this skill when configuring models, troubleshooting model availability, or refreshing the free model inventory.
argument-hint: "[goal: configure|refresh|status|troubleshoot] [context: coding|general|lightweight]"
user-invocable: true
disable-model-invocation: false
---

# OpenRouter Free Model Failover

## Purpose

Ensure OpenClaw always uses **free** OpenRouter models with intelligent priority-based failover. No paid model should ever be invoked. The cascade is ranked by coding/agentic capability and falls over automatically on rate limits, downtime, moderation blocks, or context overflow.

---

## Architecture (Two-Layer Failover)

### Layer 1: OpenClaw-side fallback chain (primary)

OpenClaw's native failover via `agents.defaults.model.primary` + `agents.defaults.model.fallbacks`:

- Tries primary model first
- On ANY error (rate limit, auth, billing, timeout, overloaded), rotates to next fallback
- Exponential cooldown: 1min → 5min → 25min → 1hr cap
- Session-sticky: pins to working model until session reset or cooldown clears
- `FallbackSummaryError` when all candidates exhausted (includes soonest cooldown expiry)

### Layer 2: OpenRouter-side server failover (complementary)

OpenRouter's `models` array parameter handles per-request failover transparently:

- If a model returns error (429, 503, moderation, context overflow), tries next in array
- Pricing based on model actually used (all free = $0)
- Works automatically with OpenAI-compatible API

### Combined: OpenClaw chains across models; within each model attempt, OpenRouter can cascade if the `models` param is forwarded.

---

## Rate Limits (Critical Constraints)

| Constraint | Limit |
|---|---|
| `:free` model requests per minute | **20 req/min** |
| Daily limit (< 10 credits purchased) | **50 req/day** |
| Daily limit (≥ 10 credits purchased) | **1,000 req/day** |
| Negative credit balance | **402 errors even for free models** |

**Implications**:
- Free tier (50/day) is extremely limited for agentic coding — consider purchasing 10 credits ($10 one-time) for 20x daily capacity
- 20 req/min shared across ALL free model calls on the key
- Multiple API keys do NOT bypass limits (governed globally per account)
- Different models have different per-model rate limits (spreading across models helps)

---

## Prioritized Free Model Cascade (Coding/Agentic)

Ranked by: coding benchmark scores, parameter count, context window, tool/function calling support.

### Tier 1: Heavy Hitters (primary + first fallbacks)

| Priority | OpenClaw Model Ref | Params | Context | Strength |
|---|---|---|---|---|
| 1 | `openrouter/qwen/qwen3-coder:free` | 480B MoE/35B active | 262K | Agentic coding champion, largest context |
| 2 | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | 120B MoE/12B active | 262K | Programming #6 ranked, 262K context |
| 3 | `openrouter/minimax/minimax-m2.5:free` | — | 197K | SWE-Bench 80.2%, strong coding |
| 4 | `openrouter/nousresearch/hermes-3-llama-3.1-405b:free` | 405B | 131K | Largest dense model, advanced agentic |
| 5 | `openrouter/openai/gpt-oss-120b:free` | 117B MoE/5.1B active | 131K | Tool use + reasoning |

### Tier 2: Solid Performers (secondary fallbacks)

| Priority | OpenClaw Model Ref | Params | Context | Strength |
|---|---|---|---|---|
| 6 | `openrouter/meta-llama/llama-3.3-70b-instruct:free` | 70B | 65K | Battle-tested, reliable |
| 7 | `openrouter/z-ai/glm-4.5-air:free` | MoE | 131K | Agent-focused, thinking modes |
| 8 | `openrouter/arcee-ai/trinity-large-preview:free` | 400B MoE | 131K | ⚠️ May expire — check availability |
| 9 | `openrouter/openai/gpt-oss-20b:free` | 21B MoE | 131K | Tool support, lightweight |
| 10 | `openrouter/google/gemma-3-27b-it:free` | 27B | 131K | Multimodal capable |

### Tier 3: Lightweight Fallbacks (emergency)

| Priority | OpenClaw Model Ref | Params | Context |
|---|---|---|---|
| 11 | `openrouter/google/gemma-4-26b-a4b-it:free` | 26B MoE | 131K |
| 12 | `openrouter/nvidia/nemotron-3-nano-30b-a3b:free` | 30B MoE | 131K |
| 13 | `openrouter/google/gemma-3-12b-it:free` | 12B | 131K |
| 14 | `openrouter/nvidia/nemotron-nano-9b-v2:free` | 9B | 131K |
| 15 | `openrouter/google/gemma-3-4b-it:free` | 4B | 131K |
| 16 | `openrouter/meta-llama/llama-3.2-3b-instruct:free` | 3B | 131K |

### Meta-Router (last resort)

| Priority | Model | Notes |
|---|---|---|
| 17 | `openrouter/openrouter/free` | Random selection from available free models — no priority control |

---

## OpenClaw Configuration

### Config location

`~/.openclaw/openclaw.json` (Windows: `%USERPROFILE%\.openclaw\openclaw.json`)

### Required config changes (JSON5)

```json5
{
  // Environment
  env: {
    OPENROUTER_API_KEY: "sk-or-v1-...",
  },

  // Model cascade — free only
  agents: {
    defaults: {
      model: {
        primary: "openrouter/qwen/qwen3-coder:free",
        fallbacks: [
          "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
          "openrouter/minimax/minimax-m2.5:free",
          "openrouter/nousresearch/hermes-3-llama-3.1-405b:free",
          "openrouter/openai/gpt-oss-120b:free",
          "openrouter/meta-llama/llama-3.3-70b-instruct:free",
          "openrouter/z-ai/glm-4.5-air:free",
          "openrouter/arcee-ai/trinity-large-preview:free",
          "openrouter/openai/gpt-oss-20b:free",
          "openrouter/google/gemma-3-27b-it:free",
          "openrouter/google/gemma-4-26b-a4b-it:free",
          "openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
          "openrouter/google/gemma-3-12b-it:free",
        ],
      },
      // Allowlist — all free models
      models: {
        "openrouter/qwen/qwen3-coder:free": { alias: "qwen-coder" },
        "openrouter/nvidia/nemotron-3-super-120b-a12b:free": { alias: "nemotron-super" },
        "openrouter/minimax/minimax-m2.5:free": { alias: "minimax" },
        "openrouter/nousresearch/hermes-3-llama-3.1-405b:free": { alias: "hermes" },
        "openrouter/openai/gpt-oss-120b:free": { alias: "gpt-oss" },
        "openrouter/meta-llama/llama-3.3-70b-instruct:free": { alias: "llama" },
        "openrouter/z-ai/glm-4.5-air:free": { alias: "glm" },
        "openrouter/arcee-ai/trinity-large-preview:free": { alias: "trinity" },
        "openrouter/openai/gpt-oss-20b:free": { alias: "gpt-oss-sm" },
        "openrouter/google/gemma-3-27b-it:free": { alias: "gemma-27b" },
        "openrouter/google/gemma-4-26b-a4b-it:free": { alias: "gemma-4" },
        "openrouter/nvidia/nemotron-3-nano-30b-a3b:free": { alias: "nemotron-nano" },
        "openrouter/google/gemma-3-12b-it:free": { alias: "gemma-12b" },
      },
      // Image model (multimodal free)
      imageModel: {
        primary: "openrouter/google/gemma-3-27b-it:free",
        fallbacks: [
          "openrouter/google/gemma-4-26b-a4b-it:free",
          "openrouter/google/gemma-3-12b-it:free",
        ],
      },
    },
  },

  // OpenRouter provider definition
  models: {
    providers: {
      openrouter: {
        baseUrl: "https://openrouter.ai/api/v1",
        apiKey: "${OPENROUTER_API_KEY}",
        api: "openai-completions",
        models: [
          // Populate via `openclaw models scan` or manually
        ],
      },
    },
  },
}
```

### Key config rules

1. **Every model ref must use `openrouter/` prefix** in OpenClaw (e.g., `openrouter/qwen/qwen3-coder:free`)
2. **`:free` suffix is part of the model ID** — OpenRouter uses this to route to free endpoints
3. **`agents.defaults.models` acts as an allowlist** — if set, only listed models can be selected
4. **Config hot-reloads** — model/agent changes apply without gateway restart
5. **Remove ALL paid models** from `models.providers.openrouter.models` array

---

## Dynamic Model Refresh (canonical — use this, not manual CLI)

`scripts/refresh-openclaw-models.js` replaces all manual model selection.

It:
1. Fetches `/api/v1/models` live from OpenRouter.
2. Filters to `:free` models only (zero prompt + completion cost).
3. Scores each model per task profile using quantitative signals.
4. Reads the current Windows OpenClaw config via SSH.
5. Writes the new ranked chain (primary + fallbacks) back via SCP.
6. Verifies the result with `openclaw models status`.

### Scoring formula

For each model:
```
score = log2(context_length) × ctxWeight
      + log2(max_completion_tokens) × outWeight
      + boostScore  (if model id matches profile keyword set)
```

| Profile | ctxWeight | outWeight | Boost keywords | Boost amount |
|---------|-----------|-----------|----------------|--------------|
| coding  | 2.0       | 0.5       | coder, qwen3, deepseek, nemotron, codestral | +30 |
| general | 1.5       | 0.3       | llama, hermes, glm, mistral, gemma | +12 |
| image   | 1.0       | 0.2       | gemma, llava, pixtral, qwen-vl | +20 |

Context length is weighted most heavily for coding because agentic coding tasks require reading full file trees, long diffs, and accumulated context.

### Usage

```bash
# Session start or after any model changes — coding tasks (default)
npm run models:refresh

# For general-purpose work
npm run models:refresh:general

# For multimodal / image-input tasks
npm run models:refresh:image

# Custom: top-N, explicit profile
node scripts/refresh-openclaw-models.js coding 10
```

Run at session start and after any reported model degradation or failover exhaustion.

## CLI Operations (fallback — when script cannot run)

### Troubleshoot failures

```bash
# Check model status and auth
openclaw models status --probe

# Check cooldown state
cat ~/.openclaw/agents/default/agent/auth-state.json

# Check gateway health
openclaw health
openclaw doctor

# View recent logs
openclaw logs --tail 50

# Force clear cooldowns (nuclear option)
rm ~/.openclaw/agents/default/agent/auth-state.json
openclaw gateway restart
```

---

## Failover Behavior Reference

### What triggers failover

| Error Type | OpenClaw Action | Cooldown |
|---|---|---|
| 429 Rate limit | Auth profile rotation → model fallback | 1min → 5min → 25min → 1hr |
| 503 Service unavailable | Immediate model fallback | 1min backoff |
| Billing/credit errors | Profile disabled, long backoff | 5hr → 10hr → 24hr cap |
| Timeout | Classified as failover-worthy | 1min backoff |
| Moderation block | Model fallback | No cooldown |
| Context overflow | Stays in compaction/retry (no fallback) | N/A |
| Auth failure | Profile rotation → model fallback | Immediate skip |

### Cooldown recovery

- Cooldowns use exponential backoff: 1min → 5min → 25min → 1hr cap
- Billing disables: 5hr → doubling → 24hr cap
- Counters reset after 24hr of no failures
- Primary model can be probed near cooldown expiry (auto-recovery)

---

## Edge Cases & Gotchas

1. **Expiring models**: Some free models (e.g., `trinity-large-preview`) are temporary promotions. Check OpenRouter's model page for expiry dates. Remove expired models from fallbacks.

2. **Negative credit balance**: Even free models return 402 if account balance is negative. Keep balance ≥ $0.

3. **Tool calling support**: Not all free models support function/tool calling. The `openclaw models scan` probes for this. Prefer models with confirmed tool support for agentic work.

4. **Context window mismatch**: Free models range from 65K to 262K tokens. OpenClaw does NOT failover on context overflow — it retries with compaction. Set `maxTokens` appropriately per model.

5. **Model ID normalization**: OpenRouter uses `provider/model:free` format. OpenClaw prepends `openrouter/` prefix. The full ref is `openrouter/provider/model:free`.

6. **Z.AI normalization**: OpenClaw normalizes `z.ai/*` to `zai/*` internally. Use `openrouter/z-ai/glm-4.5-air:free` as the ref.

7. **Daily limit exhaustion**: At 50 req/day (free tier), an agentic coding session can exhaust limits in ~30 minutes. Buying 10 credits ($10) increases to 1,000/day.

8. **Config validation**: OpenClaw strictly validates `openclaw.json`. Unknown keys prevent gateway startup. Always run `openclaw doctor` after manual edits.

---

## Maintenance Schedule

| Task | Frequency | Command |
|---|---|---|
| Refresh free model list | Session start + monthly | `npm run models:refresh` |
| Refresh after degradation | After failover exhaustion | `npm run models:refresh` |
| General/image profile refresh | Task-type change | `npm run models:refresh:general` or `:image` |
| Verify no paid models | After any config change | `openclaw models status` on inference host |
| Check rate limit status | When failures increase | `curl https://openrouter.ai/api/v1/auth/key -H "Authorization: Bearer $KEY"` |
| Clear stale cooldowns | After extended downtime | Delete `auth-state.json` + restart |

---

## Quick Decision Matrix

| Scenario | Action |
|---|---|
| Need to configure from scratch | Use CLI commands in "Initial setup" section |
| Model returning errors | Check `openclaw models status --probe` → verify `:free` suffix |
| All models failing | Check daily limit (`/api/v1/key`), credit balance, auth-state cooldowns |
| New free model launched | `openclaw models scan` → add to fallbacks if ranked high |
| Model expired/removed | `openclaw models fallbacks remove <ref>` → remove from allowlist |
| Need more daily requests | Purchase 10 credits on OpenRouter ($10 one-time) |
| Agent not using expected model | Check `/model status` in chat, verify allowlist includes model |
