---
name: hugging-face-evaluation
description: "Adds Hugging Face model-card evaluation scores: Hub .eval_results YAML, legacy model-index EvalResult, README table extraction, and Artificial Analysis imports. Use when publishing benchmark numbers on a model repo or mapping vLLM/lighteval/inspect-ai scores onto the card. Not for running the GPU eval harness itself (hugging-face-community-evals) or training/fine-tuning models."
version: 1.3.1
risk: unknown
source: community
---

## When to Use

- You need to add structured evaluation results to a Hugging Face model card.
- You want to import benchmark data from Artificial Analysis into a model card.
- You are running custom model evaluations with vLLM, lighteval, or inspect-ai.
- You are preparing leaderboard-compatible `model-index` metadata for a model release.
- You need to inspect or extract evaluation tables from a README before pushing changes.

Trigger keywords: `hugging face evaluation`, `model card`, `model-index`, `lighteval`, `inspect-ai`, `vLLM evaluation`, `Artificial Analysis`, `benchmark scores`, `leaderboard`, `eval table`.

## Prerequisites

- Python 3.10+ with `huggingface_hub` (installs the `hf` CLI). Optional: `markdown-it-py` for README table extraction, `requests` for Artificial Analysis.
- Authenticated Hub token with **write** access to the target model repo: `hf auth login` or `HF_TOKEN`.
- For Artificial Analysis imports: an API key in `AA_API_KEY` (sent as the `x-api-key` header). Do not commit keys.
- For vLLM / GPU evals: CUDA GPU (`nvidia-smi`) and enough VRAM for the model.
- This folder does **not** ship eval runners. Use the published `lighteval` and `inspect` CLIs, or the sibling skill `hugging-face-community-evals` when that pack is installed.

## Procedure

### 1. Check open PRs before proposing card changes

Required before any `create_pr=True` push.

```python
from huggingface_hub import get_repo_discussions

repo_id = "username/model-name"
open_prs = list(get_repo_discussions(
    repo_id=repo_id,
    discussion_type="pull_request",
    discussion_status="open",
))
for pr in open_prs:
    print(pr.num, pr.title, pr.author)
```

CLI: `hf discussions list username/model-name`

If open PRs exist, do **not** open another. Warn, show the PR numbers/titles, and continue only if the user confirms.

### 2. Load the card and inspect README tables

```python
from huggingface_hub import ModelCard, hf_hub_download

repo_id = "username/model-name"
card = ModelCard.load(repo_id)
print(card.data.to_dict())          # existing YAML metadata, including model-index
readme_path = hf_hub_download(repo_id=repo_id, filename="README.md")
```

Number markdown tables in `card.text` (or the downloaded README). Identify:

- table index (1-based)
- whether benchmarks are rows and models are columns, or the transpose
- the exact column header / row label for **this** model (copy text, including markdown)

**Name matching (exact normalized tokens, do not guess):**

- Strip markdown (`**`, `[text](url)`).
- Lowercase; replace `-` and `_` with spaces; compare token sets.
- `"OLMo-3-32B"` → `{"olmo", "3", "32b"}` matches `"**Olmo 3 32B**"`.
- Fail closed if no exact match.

Only extract the **main** model’s scores. Skip training checkpoints and unrelated columns/rows.

### 3. Review YAML, then apply `model-index` (legacy Hub metadata)

Hub still renders `model-index` in the model card YAML. `huggingface_hub.EvalResult` is the supported builder ([model cards guide](https://huggingface.co/docs/huggingface_hub/en/guides/model-cards)).

```python
from huggingface_hub import EvalResult, ModelCard

card = ModelCard.load(repo_id)
existing = card.data.eval_results
results = [] if existing is None else (existing if isinstance(existing, list) else [existing])
results.append(EvalResult(
    task_type="text-generation",
    dataset_type="cais/mmlu",
    dataset_name="MMLU",
    metric_type="mmlu",
    metric_name="MMLU",
    metric_value=85.2,
    source_name="README table",
    source_url="https://huggingface.co/username/model-name",
))
card.data.model_name = card.data.model_name or "Model Name"
card.data.eval_results = results
print(card.data.to_yaml())   # review before push — default is print, not apply
card.validate()
```

Apply:

- Own repo, user confirmed: `card.push_to_hub(repo_id)`
- Not owned, or review wanted: `card.push_to_hub(repo_id, create_pr=True)` (after Step 1)

**Do not** put markdown in the model name. Use URLs only in `source_url`.

Generated shape:

```yaml
model-index:
  - name: Model Name
    results:
      - task:
          type: text-generation
        dataset:
          name: MMLU
          type: cais/mmlu
        metrics:
          - name: MMLU
            type: mmlu
            value: 85.2
        source:
          name: README table
          url: https://huggingface.co/username/model-name
```

### 4. Prefer `.eval_results/` for current Hub leaderboards

The Hub’s current eval-results format is YAML under `.eval_results/` ([eval results](https://huggingface.co/docs/hub/en/eval-results)). `task_id` must match a task in the benchmark dataset’s `eval.yaml`.

```yaml
# .eval_results/mmlu.yaml
- dataset:
    id: cais/mmlu
    task_id: default
  value: 85.2
  date: "2026-08-14"
  source:
    url: https://huggingface.co/username/model-name
    name: Model Card
```

```python
from huggingface_hub import upload_file

upload_file(
    path_or_fileobj=b"...yaml bytes...",
    path_in_repo=".eval_results/mmlu.yaml",
    repo_id=repo_id,
    create_pr=True,          # after Step 1
    commit_message="Add MMLU eval result",
)
```

Open PRs show as community-provided on the model page until merged.

### 5. Import scores from Artificial Analysis

Auth: `x-api-key` header. Base URL `https://artificialanalysis.ai/api/v2` ([Data API docs](https://artificialanalysis.ai/data-api/docs)).

- Free: `GET /language/models/free` — headline indices only (not a full per-benchmark dump).
- Pro: `GET /language/models/{slug}` — model detail including `evaluations` (per-benchmark scores). Example slugs: `claude-sonnet-4`, `gpt-4o`.
- Do not invent a creator-slug query param. Filter the list client-side, or call the slug detail endpoint.

```bash
curl "https://artificialanalysis.ai/api/v2/language/models/free" \
  -H "x-api-key: YOUR_KEY"

curl "https://artificialanalysis.ai/api/v2/language/models/claude-sonnet-4" \
  -H "x-api-key: YOUR_KEY"
```

Map `data.evaluations` keys to `EvalResult` / `.eval_results` entries. Attribute `source_name` to Artificial Analysis and `source_url` to `https://artificialanalysis.ai`. Review YAML, then push via Step 3 or 4. Free-tier 403 on `{slug}` means upgrade or stay on `/language/models/free`.

### 6. Run custom evals (lighteval / inspect-ai / vLLM)

Install the **published** CLIs (`pip install lighteval` / `inspect-ai inspect-evals`, plus `vllm` when using that backend). Do not look for runners inside this skill folder.

**lighteval + vLLM** ([vLLM backend](https://huggingface.co/docs/lighteval/en/use-vllm-as-backend)):

```bash
lighteval vllm "model_name=meta-llama/Llama-3.2-1B" mmlu

# multi-GPU
VLLM_WORKER_MULTIPROC_METHOD=spawn lighteval vllm \
  "model_name=meta-llama/Llama-3.2-70B,tensor_parallel_size=4" mmlu
```

PowerShell: `$env:VLLM_WORKER_MULTIPROC_METHOD = "spawn"`

Preferred inspect-backed entry: `lighteval eval vllm/meta-llama/Llama-3.2-1B-Instruct gpqa:diamond`

**inspect-ai** ([inspect evals MMLU](https://ukgovernmentbeis.github.io/inspect_evals/evals/knowledge/mmlu/)):

```bash
inspect eval inspect_evals/mmlu_5_shot --model vllm/meta-llama/Llama-3.2-1B-Instruct
inspect eval inspect_evals/mmlu_0_shot --model hf/meta-llama/Llama-3.2-1B --limit 10
```

vLLM OOM: lower GPU memory utilization / context, or raise `tensor_parallel_size`. Architecture unsupported by vLLM: use `hf/` (inspect) or lighteval’s accelerate/transformers backends. Chat templates only on instruction-tuned models that ship one.

**Hardware (HF Jobs flavors, from Hub Jobs docs):**

| Model size | Flavor |
|------------|--------|
| < 3B | `t4-small` |
| 3B–13B | `a10g-small` |
| 13B–34B | `a10g-large` |
| 34B+ | `a100-large` |

Remote GPU without local CUDA — `huggingface_hub.run_job` ([Jobs guide](https://huggingface.co/docs/huggingface_hub/en/guides/jobs)). Payment method required for non-CPU flavors. Example:

```python
from huggingface_hub import run_job, wait_for_job
import os

job = run_job(
    image="pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
    command=["bash", "-lc", "pip install -U lighteval && lighteval vllm 'model_name=meta-llama/Llama-3.2-1B' mmlu"],
    flavor="a10g-small",
    secrets={"HF_TOKEN": os.environ["HF_TOKEN"]},
    timeout="2h",
)
print(job.url, job.id)
print(wait_for_job(job_id=job.id).status.stage)
```

Packaged local GPU wrappers live in sibling `hugging-face-community-evals` when that skill is present — do not copy them here.

After the eval, feed scores into Step 3 or 4.

## Pitfalls

- **Never create a PR without listing open PRs first.** Duplicate eval PRs spam maintainers.
- **Inspect tables before extracting.** Wrong table index or transposed layout yields the wrong model’s scores.
- **Exact header text for column match.** Token-set match is exact; do not fuzzy-guess.
- **No markdown in YAML names.**
- **One model per repo `model-index`.** Skip checkpoints and sibling columns.
- **`.eval_results` `task_id` must exist** in the benchmark’s `eval.yaml`.
- **AA free vs Pro.** Per-benchmark `evaluations` on `{slug}` is Pro; free is headline indices on `/language/models/free`.
- **HF_TOKEN needs write access** for push/PR.
- **vLLM OOM / unsupported arch.** Larger flavor, tensor parallel, or `hf`/accelerate fallback.
- **Default is print YAML** — review before `push_to_hub` / `upload_file`.
- **`--create_pr` when you do not own the model**; direct push only for repos you own.

## Verification

1. Print `card.data.to_yaml()` (or the `.eval_results` file) and compare numbers to the README table or AA payload by hand.
2. `card.validate()` succeeds before push.
3. After apply: `ModelCard.load(repo_id)` still shows the new metrics; or Hub model page shows the eval badge / community PR.
4. Open-PR check: `get_repo_discussions(..., discussion_type="pull_request", discussion_status="open")` — expected: number, title, author per PR, or an empty list.
5. GPU path: `nvidia-smi` (local) or `job.status.stage == "COMPLETED"` (Jobs).
6. CLI smoke: `lighteval --help` and/or `inspect eval --help`.

## Related Skills

- **hugging-face-community-evals** — local GPU inspect-ai / lighteval runners (separate pack).
- **hugging-face-jobs** — general HF Jobs submission, when installed.
- **hugging-face-spaces** — evaluation dashboards as Spaces.
- **model-card-authoring** — README prose and card structure.
