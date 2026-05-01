---
name: fleet-model-optimizer
description: Analyze any fleet's inventory/devices.json and recommend optimal Ollama models per device based on hardware constraints, inference tier, and current LLM landscape. Generates pull/delete commands and a safe transition plan.
argument-hint: "[focus: analyze|recommend|commands|all] [tier: slm|mid|high|all]"
user-invocable: true
disable-model-invocation: false
---

# Fleet Model Optimizer Skill

Use this skill to audit and improve Ollama model selections across a device fleet.
Invoke when models feel stale, performance is low, or after a major LLM release cycle.

## Scope Boundary

**Owns**: hardware-to-tier mapping, model scoring, pull/delete command generation.
**Hands off to**: Admin for actual `ollama pull/delete` execution on remote devices.

## Hard Constraints

- Never reference specific device IPs, hostnames, or user credentials.
- Never recommend proprietary closed-weight models — Ollama registry only.
- Always produce a pull-before-delete transition plan (no service gaps).
- Respect RAM budget: leave ≥20% free after all models loaded.
- Verify Ollama registry availability before recommending any model.

## Tier Classification

Classify each device from `inventory/devices.json` by available RAM:

| Available RAM | Tier | Max model size | Examples |
|---|---|---|---|
| < 1.5 GB | slm | ~500 MB | gemma3:270m, qwen3.5:0.5b |
| 1.5–4 GB | slm+ | ~1.5 GB | gemma4:e4b, qwen3.5:1.5b |
| 4–10 GB | mid | 7–8 B | qwen3:8b, mistral-nemo:12b* |
| 10–20 GB | mid+ | 8–14 B | qwen3:8b, phi4:14b |
| 20+ GB | high | 30–70 B | deepseek-r1:32b, qwen3:30b |

*Only if swap or GPU offload is available.

## Step-by-Step Execution

### 1. Inventory Read
Read `inventory/devices.json`. For each device extract:
`id`, `ram.available`, `gpu` (if present), `ollamaModels`, `ollamaWarmTokPerSec`.

### 2. Tier Classification
Apply the table above to assign each Ollama-enabled device a tier.
Note any GPU presence — it enables larger models and faster inference.

### 3. Model Scoring (per tier)
Search Ollama registry trends (pull counts, recency) for top candidates:
- Prioritize: reasoning quality, coding capability, pull count > 1M (community validation).
- Include 1 primary + 1–2 fallback models per device.
- Flag models with < 100K pulls as experimental.

### 4. Delta Analysis
Compare recommended models to current `ollamaModels` list.
Identify: models to keep, models to add (pull), models to remove (delete).

### 5. Command Generation
Output per-device commands in this format:
```
# <device-id> (<tier>)
ollama pull <new-model>
ollama rm <old-model>   # only after pull confirmed
```

### 6. Transition Plan
State the safe sequence: pull new → verify via `GET /api/tags` → delete old.
Confirm at least one fallback model remains at all times.

### 7. Inventory Update Guidance
Provide the updated `ollamaModels` array and estimated `ollamaWarmTokPerSec`
(use tier baselines: slm≈5, mid≈15, mid+≈20, high≈25+) for the operator to
apply to `inventory/devices.json`.

## Verification

- [ ] Every recommended model confirmed present in Ollama registry.
- [ ] No device left with zero models after transition.
- [ ] RAM budget respected: model size ≤ 80% of `ram.available`.
- [ ] Pull/delete commands syntactically valid (`ollama pull <name>` format).
- [ ] `inventory/devices.json` update values provided with source rationale.
