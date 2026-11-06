---
name: api-key-audit
description: Use when user says api check, key verify, validate keys, zip of keys, txt of keys, or bulk API key audit. Fast validation for API keys from .txt/.zip with auth, capability, quota, billing, and error classification.
---

# API Key Audit (TXT/ZIP Fast Checker)

Use this skill to quickly verify API keys from `.txt`, `.csv`, `.json`, or `.zip` files.

Goal: not only "valid/invalid" but also whether the key is actually usable for real workloads.

## Trigger Rules

Activate when user asks to:
- check API keys
- validate keys from txt/zip
- bulk verify keys
- test which keys are usable right now

## Input Rules

Accepted input:
- `.txt` (one key per line or mixed text)
- `.csv` (columns can include `key`, `api_key`, `token`)
- `.json` / `.jsonl`
- `.zip` containing any of the above

If `.zip` is provided:
1. extract to temp folder
2. parse all supported files recursively
3. deduplicate keys before network checks

## Safety & Privacy

- Never print full keys in output.
- Always mask keys as `prefix...suffix`.
- Never save raw keys to git.
- Do not brute-force or spam endpoints.
- Keep concurrency controlled (default 5-10 workers).

## Fast Validation Pipeline

### Phase 1 - Parse & Normalize (no network)

1. Read file(s), trim whitespace, ignore comments/empty lines.
2. Extract possible keys with provider regex.
3. Deduplicate exact matches.
4. Classify probable provider.

Suggested provider hints:
- OpenAI: `^sk-(proj-)?[A-Za-z0-9_-]{20,}$`
- Anthropic: `^sk-ant-[A-Za-z0-9_-]{20,}$`
- Google/Gemini: `^AIza[0-9A-Za-z_-]{35}$`
- Groq: `^gsk_[A-Za-z0-9]{20,}$`
- OpenRouter: `^sk-or-v1-[A-Za-z0-9]{20,}$`
- Cohere: long base62 token (no strict universal prefix)
- Unknown: keep for fallback probe

### Phase 2 - Auth Check (cheap endpoint)

For each provider, hit the lightest authenticated endpoint first.

Expected result classes:
- `AUTH_OK`
- `AUTH_FAILED` (401/403 invalid or revoked)
- `RATE_LIMITED` (429)
- `TEMP_ERROR` (5xx/network)

### Phase 3 - Capability Check (only AUTH_OK)

Verify practical usability:
1. model list access
2. minimal inference request
3. permission/scope limits
4. org/project mismatch errors

Mark result:
- `USABLE_FULL`
- `USABLE_LIMITED`
- `AUTH_OK_BUT_NO_MODEL_ACCESS`

### Phase 4 - Billing/Quota Signal

Infer billing state from response codes/messages:
- `QUOTA_EXCEEDED`
- `BILLING_REQUIRED`
- `CREDIT_EXHAUSTED`
- `TRIAL_EXPIRED`

### Phase 5 - Reliability Signal

Optional quick quality probe:
- 2 lightweight requests per usable key
- capture latency (p50/p95)
- detect flaky keys (intermittent 429/5xx)

Mark:
- `STABLE`
- `UNSTABLE`

## Provider Check Playbooks

## OpenAI
- Auth/model: `GET /v1/models`
- Minimal inference: `POST /v1/chat/completions` with tiny prompt
- Detect: invalid key, project restriction, model not permitted, quota errors

## Anthropic
- Auth/model: `GET /v1/models` (with `anthropic-version` header)
- Minimal inference: `POST /v1/messages` with low token request
- Detect: permission model limits, quota/rate details

## Gemini (Google AI Studio)
- Probe: `POST /v1beta/models/{model}:generateContent?key=...`
- Detect: API enabled/disabled, project billing state, model availability

## Groq
- Auth/model: `GET /openai/v1/models`
- Minimal inference: `POST /openai/v1/chat/completions`

## OpenRouter
- Auth/model: `GET /api/v1/models`
- Minimal inference: `POST /api/v1/chat/completions`
- Detect provider routing issues and model entitlement errors

## Unknown Provider Fallback

If pattern unknown:
1. do not guess aggressively
2. run non-destructive classification only
3. report `UNKNOWN_PROVIDER` with masked key

## Output Format (Required)

Always produce:

1. `summary.txt`
- total keys
- deduplicated keys
- provider breakdown
- usable/full, usable/limited, invalid

2. `results.json`
Each entry:
- `masked_key`
- `provider`
- `auth_status`
- `capability_status`
- `billing_status`
- `stability`
- `http_code`
- `error_hint`
- `latency_ms`

3. `usable_keys.txt`
- only keys with `USABLE_FULL` or `USABLE_LIMITED`
- masked by default; full value only if user explicitly requests and context is secure

## Error Classification Standard

Use exact categories:
- `INVALID_KEY`
- `REVOKED_KEY`
- `INSUFFICIENT_SCOPE`
- `MODEL_NOT_ALLOWED`
- `QUOTA_EXCEEDED`
- `BILLING_REQUIRED`
- `RATE_LIMITED`
- `ORG_MISMATCH`
- `PROVIDER_DOWN`
- `NETWORK_ERROR`
- `UNKNOWN_PROVIDER`

## Performance Rules (Fastest Practical)

- Parse/extract first, network second.
- Deduplicate before any API call.
- Run provider checks in parallel pools.
- Stop early on definitive `INVALID_KEY`.
- Only run deep checks on auth-valid keys.

Default limits:
- concurrency: 8
- request timeout: 10s
- retries: 1 (only for 5xx/network)

## Execution Checklist

1. ingest file/zip
2. extract + normalize
3. dedupe + classify provider
4. auth probe
5. capability probe
6. quota/billing classification
7. optional stability probe
8. generate summary + json + usable list

## Final Response Style

When reporting to user:
- show totals first
- show usable count by provider
- show top failure reasons
- include exact next actions (rotate, enable billing, request scope, change model)
