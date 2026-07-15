# OpenAI-compatible endpoints for SkillOpt-Sleep (DeepSeek, local vLLM, …)

This document describes the `azure_openai` backend in
`skillopt_sleep/backend.py`, which can drive servers that implement the expected
OpenAI-compatible Chat Completions request shape — for example DeepSeek's hosted
API or a self-hosted vLLM/Ollama server — in addition to native Azure OpenAI
deployments. The included runner is a sanitized unattended-launch example that
was originally used alongside Antigravity; it is not an Antigravity transcript
integration.

> **Version requirement.** This capability landed after v0.2.0. Until the next
> release, install SkillOpt from the latest `main`; the current PyPI 0.2.0
> package does not provide this compatible-endpoint path.

## What changed

All changes are backward-compatible — the default managed-identity Azure path
is unchanged:

1. **CLI acceptance.** `skillopt-sleep run --backend azure_openai` is now an
   accepted choice in `skillopt_sleep/__main__.py` (it was previously rejected
   by argparse even though `get_backend()` understood the name).

2. **Endpoint resolution honors `AZURE_OPENAI_ENDPOINT`.**
   `AzureOpenAIBackend.__init__` resolves the endpoint as `explicit arg` →
   `AZURE_OPENAI_ENDPOINT` env → the built-in `_AZURE_ENDPOINTS` table.
   Previously a non-Azure endpoint could not be supplied at all.

3. **`openai_compatible` auth mode.** When
   `AZURE_OPENAI_AUTH_MODE=openai_compatible` (also accepts `compat`/`openai`),
   `_get_client()` builds a plain `openai.OpenAI(base_url=…)` client with
   `AZURE_OPENAI_API_KEY` instead of an `AzureOpenAI` client. This mirrors the
   auth mode already supported by the sibling `skillopt/model/azure_openai.py`
   module. (The `AzureOpenAI` client rewrites request URLs with Azure-only
   `?api-version=…` query params and deployment path segments, which non-Azure
   servers reject with `404 Resource not found` — the sleep cycle then scores
   every rollout `0.0` with no diagnostic.)

4. **Managed-identity credential guard.** The managed-identity path attaches an
   Azure AD bearer token to every request. It therefore accepts only an **HTTPS**
   endpoint whose hostname ends in `*.openai.azure.com` or
   `*.cognitiveservices.azure.com`. An HTTP endpoint — even one with an
   Azure-looking hostname — and any host outside those suffixes are rejected
   before a credential-bearing client is created.

5. **Provider-neutral request shape.** In compat mode the backend sends only the
   standard OpenAI-compatible contract (`model`, `messages`, `max_tokens`).
   Provider-specific request fields are **opt-in** via environment variables
   (below) and are attached only in compat mode — nothing is inferred from
   model-name substrings, and the native Azure request remains unchanged.

6. **Reliable error state.** `_call()` records the last exception in
   `self.last_call_error` (surfaced in `diagnostics.json`), clears it when a
   retry recovers, and sets an explicit `"empty response on all N attempts"`
   diagnostic when every attempt returns empty text.

## Configuration reference

SkillOpt-Sleep's `azure_openai` backend reads these environment variables
(unprefixed only — the `OPTIMIZER_*`/`TARGET_*` dual-role variables belong to
the separate `skillopt.model.azure_openai` module and are **not** used by the
sleep cycle):

| Variable | Meaning |
|---|---|
| `AZURE_OPENAI_AUTH_MODE` | `openai_compatible` (or `compat`/`openai`) selects the plain OpenAI client. Unset/other = Azure managed identity (default). |
| `AZURE_OPENAI_ENDPOINT` | Base URL of the server, e.g. `https://api.deepseek.com`. Azure managed identity requires HTTPS plus an approved Azure hostname. |
| `AZURE_OPENAI_API_KEY` | API key sent by the compat client to the configured base URL. |
| `SKILLOPT_SLEEP_COMPAT_MAX_TOKENS` | Optional int (default `8192`): `max_tokens` sent in compat mode. |
| `SKILLOPT_SLEEP_CHAT_EXTRA_BODY` | Optional JSON object passed as `extra_body` for provider-specific fields in compat mode only. It is ignored in native Azure mode. |

## Data and transport boundaries

- Harvesting reads local transcripts without modifying them, and the `mock`
  backend makes no provider calls. A real backend sends **truncated transcript
  excerpts and derived task content** to the selected provider for mining,
  replay, judging, and reflection.
- Outbound prompts are not currently guaranteed to be free of secrets. Review
  the provider's data policy and avoid a third-party endpoint for sensitive
  transcripts unless you have first inspected and redacted the task material.
  One reviewable path is `skillopt-sleep harvest --output tasks.json`, followed
  by a reviewed `--tasks-file` run.
- Use HTTPS for every remote compatible provider. Plain HTTP is appropriate only
  for an explicitly trusted loopback development server such as
  `http://127.0.0.1:8000/v1`; the compat client sends its API key to the configured
  URL.
- Azure managed-identity credentials have the stricter invariant described
  above: HTTPS **and** an approved Azure hostname are both mandatory.

## How to use it

```bash
export AZURE_OPENAI_AUTH_MODE=openai_compatible
export AZURE_OPENAI_ENDPOINT=https://api.deepseek.com   # DeepSeek base URL
export AZURE_OPENAI_API_KEY=sk-...                       # your provider key

# DeepSeek reasoning models: enable the thinking channel (opt-in, not inferred)
export SKILLOPT_SLEEP_CHAT_EXTRA_BODY='{"thinking": {"type": "enabled"}}'
export SKILLOPT_SLEEP_COMPAT_MAX_TOKENS=8192

skillopt-sleep run \
  --backend azure_openai \
  --model deepseek-v4-pro \
  --project /path/to/your/project
```

The same pattern works for a server that implements this Chat Completions
contract: point `AZURE_OPENAI_ENDPOINT` at the provider-specific base URL, set a
matching `--model`, and omit `SKILLOPT_SLEEP_CHAT_EXTRA_BODY` unless the provider
needs extra request fields. Self-hosted vLLM and Ollama commonly use a `/v1` base
path, for example `http://127.0.0.1:8000/v1` or
`http://127.0.0.1:11434/v1`.

`--project` selects the project/transcript scope and the project `CLAUDE.md`; it
does **not** by itself select an arbitrary project `SKILL.md`. Pass
`--target-skill-path path/to/SKILL.md` when a specific skill is the optimization
target. Without that flag, SkillOpt-Sleep uses its configured managed skill.

## Unattended runner example (originally used with Antigravity)

The [`examples/`](https://github.com/microsoft/SkillOpt/tree/main/docs/sleep/examples) directory contains a sanitized reference for running
the compatible backend unattended:

- **`examples/runner.py`** — a thin launcher that loads a provider key from an
  `.env` file, exports the variables above, invokes `skillopt-sleep run` with
  the DeepSeek backend, and **exits with the child's return code** so
  supervisors see failures as failures. Its `session-end` action writes a small
  local rollout-evidence event as an example hook target.
- **`examples/watchdog.py`** — a minimal supervisor loop that invokes the runner
  on a fixed interval (e.g. every 4 hours) and logs non-zero exits as failures.
  On Windows this is registered as a Scheduled Task so it survives logout; on
  Linux/macOS a `systemd` timer or cron entry serves the same role.

The current engine does **not** read `brain/rollout-evidence.jsonl`, and it does
not harvest Antigravity transcripts. That hook output is illustrative metadata,
not additional training evidence. A real run must use a supported Claude
Code/Codex transcript source or a reviewed task file converted by the operator.

### Contributor-reported validation

The contributor reported the following results from a private Windows 11 setup
driving the cycle against `deepseek-v4-pro` in `openai_compatible` mode. They are
useful integration evidence, but the private session set is not a reproducible
benchmark bundled with this repository:

- A direct backend smoke test returns a live completion (no `404`,
  `last_call_error` empty, client type `OpenAI`).
- A full nightly cycle using the configured session source moved the held-out
  validation gate from `0.250 → 1.000`, **accepting** a DeepSeek-authored
  skill edit (`accept_new_best`). `diagnostics.json` for that night reports
  `"backend": "azure_openai"` with a non-empty token count and an empty
  `call_error` — i.e. a genuine optimization night, versus the prior all-`0.0`
  nights that the endpoint bug produced.
- A subsequent unattended night triggered by the watchdog completed the full
  chain (watchdog → runner → `skillopt-sleep` → DeepSeek) and the gate correctly
  **rejected** a non-improving proposal (`0.3 → 0.3`), confirming the validation
  gate behaves normally on the new backend.

Deterministic no-network coverage for the new behavior lives in
`tests/test_azure_openai_compat.py` (CLI acceptance, client selection,
endpoint/auth guard, request kwargs, retry error-state, empty-response
diagnostics, and runner exit-code propagation).

## Unsupported Gemini proxy branch in the example

`examples/runner.py` still contains an illustrative branch that routes the
**`claude` CLI backend** through a loopback Anthropic-compatible proxy such as
[LiteLLM](https://github.com/BerriAI/litellm). It is not a native Gemini backend,
has no validated model mapping in this example, and is not part of the supported
path documented here. The sample currently enters that branch whenever no
DeepSeek key is found, so a production adaptation should remove it or replace it
with an explicit opt-in, a separately configured model, and a trusted isolated
loopback proxy. Do not treat this branch as tested Gemini support.
