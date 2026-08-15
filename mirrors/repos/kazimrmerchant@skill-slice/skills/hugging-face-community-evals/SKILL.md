---
name: hugging-face-community-evals
description: "Runs local GPU evaluations of Hugging Face Hub models with inspect-ai or lighteval and vLLM, Transformers, or accelerate backends (uv scripts). Use when choosing an eval framework, running a smoke test, or picking a local inference backend. Not for remote Hugging Face Jobs, model-card or model-index edits (hugging-face-evaluation), or publishing .eval_results."
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/huggingface-community-evals
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# Overview

This skill runs evaluations against models hosted on the Hugging Face Hub using **local hardware**. It covers two evaluation frameworks—`inspect-ai` and `lighteval`—and three inference backends: `vllm`, Hugging Face Transformers (`hf`), and `accelerate`.

It does **not** cover:
- Hugging Face Jobs orchestration (hand off to `hugging-face-jobs`)
- Model-card or `model-index` edits
- README table extraction
- Artificial Analysis imports
- `.eval_results` generation or publishing
- PR creation or community-evals automation

If the user wants to run the same eval remotely on Hugging Face Jobs, hand off to the `hugging-face-jobs` skill and pass it one of the local scripts from this skill.

If the user wants to publish results into the community evals workflow, stop after generating the evaluation run and hand off that publishing step to `~/code/community-evals`.

> All paths below are relative to the directory containing this `SKILL.md`.

## When to Use

- User wants to evaluate a Hugging Face Hub model on local GPU hardware
- User needs to choose between `inspect-ai` and `lighteval`
- User needs to choose between `vllm`, Transformers, or `accelerate` backends
- User wants to run a quick smoke test before scaling up
- User is doing backend selection or local GPU evals

**Do not use this skill for:** HF Jobs orchestration, model-card PRs, `.eval_results` publication, or community-evals automation.

## Prerequisites

1. Install `uv` (preferred runner for all scripts in this skill).
2. Set `HF_TOKEN` environment variable for gated or private models. Use `YOUR_KEY` as placeholder—never hardcode live secrets.
3. For local GPU runs, verify GPU access before starting:

```powershell
uv --version
$env:HF_TOKEN  # Should be set; verify it exists
nvidia-smi
```

If `nvidia-smi` is unavailable on Windows:
- Use `scripts/inspect_eval_uv.py` for lighter provider-backed evaluation (no local GPU needed), or
- Hand off to the `hugging-face-jobs` skill if the user wants remote compute.

## Procedure

### Step 1: Choose the Evaluation Framework

| Framework | When to choose |
|---|---|
| `inspect-ai` | You want explicit task control and inspect-native flows |
| `lighteval` | The benchmark is naturally expressed as a lighteval task string (leaderboard-style tasks) |

### Step 2: Choose the Inference Backend

| Backend | When to choose |
|---|---|
| `vllm` | Throughput on supported architectures (preferred) |
| `hf` (Transformers) | `vllm` does not support the model (inspect-ai fallback) |
| `accelerate` | `vllm` does not support the model (lighteval fallback) |
| Inference Providers | No direct GPU control needed; model already supported by HF Inference Providers |

### Step 3: Select the Script

| Use case | Script |
|---|---|
| Local `inspect-ai` eval via inference providers | `scripts/inspect_eval_uv.py` |
| Local GPU eval with `inspect-ai` using `vllm` or Transformers | `scripts/inspect_vllm_uv.py` |
| Local GPU eval with `lighteval` using `vllm` or `accelerate` | `scripts/lighteval_vllm_uv.py` |
| Extra command patterns | `examples/USAGE_EXAMPLES.md` |

**Load `examples/USAGE_EXAMPLES.md`** when the user asks for additional command patterns beyond the quick-start options below.

### Step 4: Run a Smoke Test First

Always start with a limited sample size:
- `inspect-ai`: add `--limit 10` (or similar small number)
- `lighteval`: add `--max-samples 10`

### Step 5: Scale Up

Only after the smoke test passes, remove the limit flag or increase it to the full dataset.

### Step 6: Remote Handoff (if needed)

If the user wants remote execution, hand off to `hugging-face-jobs` with the same script and arguments.

---

## Quick Start Commands

### Option A: inspect-ai with Inference Providers (no local GPU needed)

Best when the model is already supported by Hugging Face Inference Providers and you want the lowest local setup overhead.

```powershell
uv run scripts/inspect_eval_uv.py `
  --model meta-llama/Llama-3.2-1B `
  --task mmlu `
  --limit 20
```

Use this path when:
- You want a quick local smoke test
- You do not need direct GPU control
- The task already exists in `inspect-evals`

### Option B: inspect-ai on Local GPU

Best when you need to load the Hub model directly, use `vllm`, or fall back to Transformers for unsupported architectures.

**vLLM backend:**
```powershell
uv run scripts/inspect_vllm_uv.py `
  --model meta-llama/Llama-3.2-1B `
  --task gsm8k `
  --limit 20
```

**Transformers fallback (`--backend hf`):**
```powershell
uv run scripts/inspect_vllm_uv.py `
  --model microsoft/phi-2 `
  --task mmlu `
  --backend hf `
  --trust-remote-code `
  --limit 20
```

### Option C: lighteval on Local GPU

Best when the task is naturally expressed as a `lighteval` task string, especially Open LLM Leaderboard style benchmarks.

**vLLM backend:**
```powershell
uv run scripts/lighteval_vllm_uv.py `
  --model meta-llama/Llama-3.2-3B-Instruct `
  --tasks "leaderboard|mmlu|5,leaderboard|gsm8k|5" `
  --max-samples 20 `
  --use-chat-template
```

**accelerate fallback (`--backend accelerate`):**
```powershell
uv run scripts/lighteval_vllm_uv.py `
  --model microsoft/phi-2 `
  --tasks "leaderboard|mmlu|5" `
  --backend accelerate `
  --trust-remote-code `
  --max-samples 20
```

## Task Selection

### inspect-ai task names

- `mmlu`
- `gsm8k`
- `hellaswag`
- `arc_challenge`
- `truthfulqa`
- `winogrande`
- `humaneval`

### lighteval task strings

Format: `suite|task|num_fewshot`

- `leaderboard|mmlu|5`
- `leaderboard|gsm8k|5`
- `leaderboard|arc_challenge|25`
- `lighteval|hellaswag|0`

Multiple `lighteval` tasks can be comma-separated in `--tasks`.

## Backend Selection Summary

- Prefer `inspect_vllm_uv.py --backend vllm` for fast GPU inference on supported architectures.
- Use `inspect_vllm_uv.py --backend hf` when `vllm` does not support the model.
- Prefer `lighteval_vllm_uv.py --backend vllm` for throughput on supported models.
- Use `lighteval_vllm_uv.py --backend accelerate` as the compatibility fallback.
- Use `inspect_eval_uv.py` when Inference Providers already cover the model and you do not need direct GPU control.

## Hardware Guidance

| Model size | Suggested local hardware |
|---|---|
| `< 3B` | Consumer GPU / Apple Silicon / small dev GPU |
| `3B - 13B` | Stronger local GPU |
| `13B+` | High-memory local GPU or hand off to `hugging-face-jobs` |

For smoke tests, prefer cheaper local runs plus `--limit` or `--max-samples`.

## Remote Execution Boundary

This skill intentionally stops at **local execution and backend selection**.

If the user wants to:
- Run these scripts on Hugging Face Jobs
- Pick remote hardware
- Pass secrets to remote jobs
- Schedule recurring runs
- Inspect / cancel / monitor jobs

Then switch to the **`hugging-face-jobs`** skill and pass it one of these scripts plus the chosen arguments.

## Pitfalls

1. **CUDA or vLLM OOM**: Reduce `--batch-size`, reduce `--gpu-memory-utilization`, switch to a smaller model for the smoke test, or hand off to `hugging-face-jobs`.
2. **Model unsupported by `vllm`**: Switch to `--backend hf` for `inspect-ai`, or `--backend accelerate` for `lighteval`.
3. **Gated/private repo access fails**: Verify `HF_TOKEN` is set and valid. Use `YOUR_KEY` as placeholder in examples—never commit live tokens.
4. **Custom model code required**: Add `--trust-remote-code` flag.
5. **Skipping smoke test**: Always run with `--limit` or `--max-samples` first. Full runs on large datasets can consume significant GPU time and memory.
6. **Wrong framework for task type**: `lighteval` is better for leaderboard-style benchmarks expressed as task strings. `inspect-ai` is better for explicit task control and custom eval flows.
7. **Assuming remote execution**: This skill is local-only. Do not attempt to orchestrate Hugging Face Jobs from these scripts.

## Verification

1. **Verify `uv` is installed:**
```powershell
uv --version
```
Expected: prints a version number (e.g., `uv 0.x.x`).

2. **Verify `HF_TOKEN` is set (for gated models):**
```powershell
if ($env:HF_TOKEN) { "HF_TOKEN is set" } else { "HF_TOKEN is NOT set" }
```
Expected: `HF_TOKEN is set`

3. **Verify GPU access (for local GPU scripts):**
```powershell
nvidia-smi
```
Expected: GPU information table with memory and utilization stats.

4. **Verify smoke test passes before full run:**
```powershell
uv run scripts/inspect_vllm_uv.py `
  --model meta-llama/Llama-3.2-1B `
  --task gsm8k `
  --limit 10
```
Expected: evaluation completes with a results summary showing accuracy/score for the limited sample set.

5. **Verify lighteval task string is valid:**
```powershell
uv run scripts/lighteval_vllm_uv.py `
  --model meta-llama/Llama-3.2-1B `
  --tasks "leaderboard|mmlu|5" `
  --max-samples 10
```
Expected: task loads successfully and produces scores without task-not-found errors.

## Examples

See:
- `examples/USAGE_EXAMPLES.md` — load this reference when the user asks for additional command patterns beyond the quick-start options above.
- `scripts/inspect_eval_uv.py` — inspect-ai with inference providers
- `scripts/inspect_vllm_uv.py` — inspect-ai with local GPU (vllm or hf backend)
- `scripts/lighteval_vllm_uv.py` — lighteval with local GPU (vllm or accelerate backend)

## Related Skills

- `hugging-face-jobs` — for remote execution on Hugging Face Jobs infrastructure
- `community-evals` (`~/code/community-evals`) — for publishing evaluation results into the community evals workflow

## Limitations

- Use this skill only when the task clearly matches its upstream product or API scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
