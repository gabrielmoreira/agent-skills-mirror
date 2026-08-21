---
name: community-evals
description: "Runs local GPU Hugging Face Hub evaluations with inspect-ai and lighteval, choosing vLLM, Transformers, or accelerate backends and smoke-test limits. Use when benchmarking a Hub model on local hardware before a full run. Not for writing model-card eval tables (hugging-face-evaluation), publishing .eval_results, or orchestrating Hugging Face Jobs."
version: 1.0.1
---

## Overview

This skill covers **running evaluations against models on the Hugging Face Hub on local hardware** using `inspect-ai` and `lighteval`. It guides backend selection (`vllm`, Hugging Face Transformers, `accelerate`), smoke testing, task selection, and fallback strategy.

It does **not** cover:
- Hugging Face Jobs orchestration
- Model-card or `model-index` edits
- README table extraction
- Artificial Analysis imports
- `.eval_results` generation or publishing
- PR creation or community-evals automation

**Remote boundary:** If the user wants to run the same eval on Hugging Face Jobs, hand off to the `hugging-face-jobs` skill and pass it one of the local scripts in this skill.

**Publishing boundary:** If the user wants to publish results into the community evals workflow, stop after generating the evaluation run and hand off that publishing step to `~/code/community-evals`.

> All paths below are relative to the directory containing this `SKILL.md`.

## When to Use

- User wants to evaluate a Hugging Face Hub model locally on GPU or via inference providers.
- User needs to choose between `vllm`, Hugging Face Transformers (`hf`), or `accelerate` backends.
- User wants a quick smoke test before scaling up a full benchmark run.
- User is working with `inspect-ai` tasks or `lighteval` task strings (e.g., Open LLM Leaderboard style).
- User asks about local GPU eval setup, backend fallback, or benchmark task selection.

**Do NOT use for:** HF Jobs orchestration, model-card PRs, `.eval_results` publication, or community-evals automation.

## Prerequisites

- **Prefer `uv run`** for all local execution.
- Set `HF_TOKEN` for gated or private models. Use a placeholder like `YOUR_KEY` in examples — never hardcode live secrets.
- For local GPU runs, verify GPU access before starting.

### Environment Check (PowerShell)

```powershell
uv --version
$env:HF_TOKEN  # Should be set; do not print the value in logs
nvidia-smi
```

If `nvidia-smi` is unavailable, either:
- Use `scripts/inspect_eval_uv.py` for lighter provider-backed evaluation, or
- Hand off to the `hugging-face-jobs` skill if the user wants remote compute.

### Script Reference Table

| Use case | Script |
|---|---|
| Local `inspect-ai` eval on a Hub model via inference providers | `scripts/inspect_eval_uv.py` |
| Local GPU eval with `inspect-ai` using `vllm` or Transformers | `scripts/inspect_vllm_uv.py` |
| Local GPU eval with `lighteval` using `vllm` or `accelerate` | `scripts/lighteval_vllm_uv.py` |
| Extra command patterns | `examples/USAGE_EXAMPLES.md` |

**When to load each reference:**
- Load `examples/USAGE_EXAMPLES.md` when the user asks for additional command patterns beyond the Quick Start below, or when troubleshooting a specific backend combination.
- Load `scripts/inspect_eval_uv.py` when using the inference providers path (Option A).
- Load `scripts/inspect_vllm_uv.py` when running `inspect-ai` on local GPU (Option B).
- Load `scripts/lighteval_vllm_uv.py` when running `lighteval` on local GPU (Option C).

## Procedure

### Step 1 — Choose the Evaluation Framework

- Use `inspect-ai` when you want explicit task control and inspect-native flows.
- Use `lighteval` when the benchmark is naturally expressed as a lighteval task string, especially leaderboard-style tasks.

### Step 2 — Choose the Inference Backend

- **Prefer `vllm`** for throughput on supported architectures.
- Use Hugging Face Transformers (`--backend hf`) or `accelerate` as compatibility fallbacks.

### Step 3 — Start With a Smoke Test

- `inspect-ai`: add `--limit 10` or similar.
- `lighteval`: add `--max-samples 10`.

### Step 4 — Scale Up Only After the Smoke Test Passes

Remove the `--limit` / `--max-samples` flag and run the full benchmark.

### Step 5 — If Remote Execution Is Needed, Hand Off

Switch to the `hugging-face-jobs` skill and pass it the same script plus the chosen arguments.

---

### Quick Start

#### Option A: inspect-ai with Local Inference Providers

Best when the model is already supported by Hugging Face Inference Providers and you want the lowest local setup overhead.

```powershell
uv run scripts/inspect_eval_uv.py `
  --model meta-llama/Llama-3.2-1B `
  --task mmlu `
  --limit 20
```

Use this path when:
- You want a quick local smoke test.
- You do not need direct GPU control.
- The task already exists in `inspect-evals`.

#### Option B: inspect-ai on Local GPU

Best when you need to load the Hub model directly, use `vllm`, or fall back to Transformers for unsupported architectures.

**vLLM (default):**

```powershell
uv run scripts/inspect_vllm_uv.py `
  --model meta-llama/Llama-3.2-1B `
  --task gsm8k `
  --limit 20
```

**Transformers fallback:**

```powershell
uv run scripts/inspect_vllm_uv.py `
  --model microsoft/phi-2 `
  --task mmlu `
  --backend hf `
  --trust-remote-code `
  --limit 20
```

#### Option C: lighteval on Local GPU

Best when the task is naturally expressed as a `lighteval` task string, especially Open LLM Leaderboard style benchmarks.

**vLLM (default):**

```powershell
uv run scripts/lighteval_vllm_uv.py `
  --model meta-llama/Llama-3.2-3B-Instruct `
  --tasks "leaderboard|mmlu|5,leaderboard|gsm8k|5" `
  --max-samples 20 `
  --use-chat-template
```

**accelerate fallback:**

```powershell
uv run scripts/lighteval_vllm_uv.py `
  --model microsoft/phi-2 `
  --tasks "leaderboard|mmlu|5" `
  --backend accelerate `
  --trust-remote-code `
  --max-samples 20
```

---

### Task Selection

**`inspect-ai` examples:**
- `mmlu`
- `gsm8k`
- `hellaswag`
- `arc_challenge`
- `truthfulqa`
- `winogrande`
- `humaneval`

**`lighteval` task strings** use the format `suite|task|num_fewshot`:
- `leaderboard|mmlu|5`
- `leaderboard|gsm8k|5`
- `leaderboard|arc_challenge|25`
- `lighteval|hellaswag|0`

Multiple `lighteval` tasks can be comma-separated in `--tasks`.

### Backend Selection Summary

| Scenario | Recommended backend / script |
|---|---|
| Fast GPU inference, supported architecture | `inspect_vllm_uv.py --backend vllm` |
| `vllm` does not support the model (inspect-ai) | `inspect_vllm_uv.py --backend hf` |
| Fast GPU inference, lighteval, supported model | `lighteval_vllm_uv.py --backend vllm` |
| `vllm` does not support the model (lighteval) | `lighteval_vllm_uv.py --backend accelerate` |
| Inference Providers already cover the model, no GPU needed | `inspect_eval_uv.py` |

### Hardware Guidance

| Model size | Suggested local hardware |
|---|---|
| `< 3B` | Consumer GPU / Apple Silicon / small dev GPU |
| `3B – 13B` | Stronger local GPU |
| `13B+` | High-memory local GPU or hand off to `hugging-face-jobs` |

For smoke tests, prefer cheaper local runs plus `--limit` or `--max-samples`.

## Pitfalls

- **CUDA or vLLM OOM:**
  - Reduce `--batch-size`.
  - Reduce `--gpu-memory-utilization`.
  - Switch to a smaller model for the smoke test.
  - If necessary, hand off to `hugging-face-jobs`.

- **Model unsupported by `vllm`:**
  - Switch to `--backend hf` for `inspect-ai`.
  - Switch to `--backend accelerate` for `lighteval`.

- **Gated or private repo access fails:**
  - Verify `HF_TOKEN` is set and valid. Do not print the token value in any logs or output.

- **Custom model code required:**
  - Add `--trust-remote-code` to the command.

- **PowerShell line continuation:** Use backtick (`` ` ``) for multi-line commands on Windows PowerShell, not backslash (`\`).

- **Do not cross the remote boundary:** This skill intentionally stops at local execution and backend selection. Do not attempt to orchestrate Hugging Face Jobs, create PRs, or publish `.eval_results` from within this skill.

## Verification

After running a smoke test, verify the eval completed successfully:

```powershell
# Check that the eval produced output files (inspect-ai)
ls ./*.eval 2>$null; ls ./logs/ 2>$null

# Check that the eval produced output files (lighteval)
ls ./results/ 2>$null; ls ./outputs/ 2>$null

# Confirm GPU was utilized during the run (run nvidia-smi during or after)
nvidia-smi
```

**Expected indicators of success:**
- The command exits with code `0`.
- `inspect-ai` produces a `.eval` log file or a `logs/` directory with results.
- `lighteval` produces a `results/` or `outputs/` directory with evaluation scores.
- `nvidia-smi` shows GPU memory was allocated during the run (for GPU backends).
- The smoke test with `--limit 20` or `--max-samples 20` completes in a reasonable time (seconds to minutes depending on model size).

**If verification fails:**
- Re-check `HF_TOKEN` for gated models.
- Confirm the model name is correct on the Hugging Face Hub.
- Try a smaller model or fewer samples to isolate the issue.
- Switch backend (`vllm` → `hf` or `accelerate`) if architecture support is the problem.

## Examples

See:
- `examples/USAGE_EXAMPLES.md` — additional local command patterns and edge cases.
- `scripts/inspect_eval_uv.py` — inference providers path source.
- `scripts/inspect_vllm_uv.py` — local GPU inspect-ai source.
- `scripts/lighteval_vllm_uv.py` — local GPU lighteval source.

## Related Skills

- **`hugging-face-jobs`** — hand off here when the user wants remote execution on Hugging Face Jobs, remote hardware selection, secret passing, job scheduling, or job monitoring.
- **`community-evals` (automation)** — hand off to `~/code/community-evals` when the user wants to publish evaluation results into the community evals workflow.
