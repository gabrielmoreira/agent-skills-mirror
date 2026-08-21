---
name: trl-training
description: "Trains Hugging Face TRL jobs: trl sft/dpo/grpo/kto/rloo/reward, YAML configs, LoRA/PEFT, and Accelerate multi-GPU. Use when fine-tuning or aligning transformer LMs with TRL CLI. Not for vLLM OpenAI serving, local Hub evals (hugging-face-community-evals), or sentence-transformers embedding training."
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/trl-training
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# TRL Training

## When to Use

Use this skill when the user needs to train or fine-tune transformer language models using the TRL (Transformers Reinforcement Learning) library. Trigger keywords and scenarios:

- **SFT** — supervised fine-tuning on instruction-following or conversational datasets
- **DPO** — direct preference optimization with chosen/rejected pairs
- **GRPO** — group relative policy optimization with reward functions or LLM-as-a-judge
- **KTO** — Kahneman-Tversky optimization (use `trl kto` CLI)
- **RLOO** — REINFORCE Leave-One-Out online RL with generation-based rewards
- **Reward Model** — training a reward model for RLHF
- Configuration via YAML, distributed training with Accelerate, LoRA/PEFT adapters, or troubleshooting TRL training runs

You are an expert at using the TRL library to train and fine-tune large language models.

## Prerequisites

1. **Install TRL** (requires Python ≥ 3.9, PyTorch, and Hugging Face Transformers):

   ```bash
   pip install trl
   ```

2. **Authenticate with Hugging Face Hub** (needed for gated models, pushing to hub, or private datasets):

   ```bash
   hf auth login
   ```

   Use a token placeholder such as `YOUR_HF_TOKEN` — never commit real tokens.

3. **Verify GPU availability** (training expects CUDA; CPU-only is impractical for all but tiny models):

   ```bash
   python -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"
   ```

4. **Windows host notes (PowerShell primary):**
   - Multi-line backslash-continuation commands shown below are bash syntax. In PowerShell, use backtick (`` ` ``) as the line-continuation character, or run the command as a single line.
   - For YAML config files, use forward slashes or escaped backslashes in paths.
   - Accelerate config default path on Windows: `~/.cache/huggingface/accelerate/default_config.yaml`

## Procedure

### 1. Choose the training method

| Goal | Command | Typical dataset schema |
|---|---|---|
| Instruction / chat fine-tuning | `trl sft` | `prompt` + `completion` or conversational |
| Preference alignment | `trl dpo` | `prompt`, `chosen`, `rejected` |
| RL with reward functions | `trl grpo` | `prompt` (+ reward function) |
| Online RL with reward model | `trl rloo` | `prompt` (+ reward model) |
| Train a reward model | `trl reward` | `chosen`, `rejected` |

**Best practice:** Always SFT a base model before preference alignment (DPO/GRPO/RLOO).

### 2. Supervised Fine-Tuning (SFT)

**Full training:**

```bash
trl sft \
  --model_name_or_path Qwen/Qwen2-0.5B \
  --dataset_name trl-lib/Capybara \
  --learning_rate 2.0e-5 \
  --num_train_epochs 1 \
  --packing \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 8 \
  --eos_token '<|im_end|>' \
  --eval_strategy steps \
  --eval_steps 100 \
  --output_dir Qwen2-0.5B-SFT \
  --push_to_hub
```

**LoRA adapter training (lower memory, faster):**

```bash
trl sft \
  --model_name_or_path Qwen/Qwen2-0.5B \
  --dataset_name trl-lib/Capybara \
  --learning_rate 2.0e-4 \
  --num_train_epochs 1 \
  --packing \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 8 \
  --eos_token '<|im_end|>' \
  --eval_strategy steps \
  --eval_steps 100 \
  --use_peft \
  --lora_r 32 \
  --lora_alpha 16 \
  --output_dir Qwen2-0.5B-SFT \
  --push_to_hub
```

### 3. Direct Preference Optimization (DPO)

**Full training:**

```bash
trl dpo \
  --dataset_name trl-lib/ultrafeedback_binarized \
  --model_name_or_path Qwen/Qwen2-0.5B-Instruct \
  --learning_rate 5.0e-7 \
  --num_train_epochs 1 \
  --per_device_train_batch_size 2 \
  --max_steps 1000 \
  --gradient_accumulation_steps 8 \
  --eval_strategy steps \
  --eval_steps 50 \
  --output_dir Qwen2-0.5B-DPO \
  --no_remove_unused_columns
```

**LoRA adapter training:**

```bash
trl dpo \
  --dataset_name trl-lib/ultrafeedback_binarized \
  --model_name_or_path Qwen/Qwen2-0.5B-Instruct \
  --learning_rate 5.0e-6 \
  --num_train_epochs 1 \
  --per_device_train_batch_size 2 \
  --max_steps 1000 \
  --gradient_accumulation_steps 8 \
  --eval_strategy steps \
  --eval_steps 50 \
  --output_dir Qwen2-0.5B-DPO \
  --no_remove_unused_columns \
  --use_peft \
  --lora_r 32 \
  --lora_alpha 16
```

### 4. Group Relative Policy Optimization (GRPO)

```bash
trl grpo \
  --model_name_or_path Qwen/Qwen2.5-0.5B \
  --dataset_name trl-lib/gsm8k \
  --reward_funcs accuracy_reward \
  --output_dir Qwen2-0.5B-GRPO \
  --push_to_hub
```

### 5. REINFORCE Leave-One-Out (RLOO)

```bash
trl rloo \
  --model_name_or_path Qwen/Qwen2.5-0.5B \
  --dataset_name trl-lib/tldr \
  --reward_model_name_or_path sentiment-analysis:nlptown/bert-base-multilingual-uncased-sentiment \
  --output_dir Qwen2-0.5B-RLOO \
  --push_to_hub
```

### 6. Reward Model Training

**Full training:**

```bash
trl reward \
  --model_name_or_path Qwen/Qwen2-0.5B-Instruct \
  --dataset_name trl-lib/ultrafeedback_binarized \
  --output_dir Qwen2-0.5B-Reward \
  --per_device_train_batch_size 8 \
  --num_train_epochs 1 \
  --learning_rate 1.0e-5 \
  --eval_strategy steps \
  --eval_steps 50 \
  --max_length 2048
```

**LoRA adapter training:**

```bash
trl reward \
  --model_name_or_path Qwen/Qwen2-0.5B-Instruct \
  --dataset_name trl-lib/ultrafeedback_binarized \
  --output_dir Qwen2-0.5B-Reward-LoRA \
  --per_device_train_batch_size 8 \
  --num_train_epochs 1 \
  --learning_rate 1.0e-4 \
  --eval_strategy steps \
  --eval_steps 50 \
  --max_length 2048 \
  --use_peft \
  --lora_task_type SEQ_CLS \
  --lora_r 32 \
  --lora_alpha 16
```

### 7. Configuration Files (YAML)

All CLI arguments can be placed in a YAML config for reproducibility.

**Example `sft_config.yaml`:**

```yaml
model_name_or_path: Qwen/Qwen2.5-0.5B
dataset_name: trl-lib/Capybara
learning_rate: 2.0e-5
num_train_epochs: 1
per_device_train_batch_size: 8
gradient_accumulation_steps: 2
output_dir: ./sft_output
use_peft: true
lora_r: 16
lora_alpha: 16
report_to: trackio
```

**Launch with config:**

```bash
trl sft --config sft_config.yaml
```

**Override individual values:**

```bash
trl sft --config sft_config.yaml --learning_rate 1.0e-5
```

### 8. Distributed Training (Accelerate)

TRL integrates with Accelerate for multi-GPU and multi-node training.

**Multi-GPU via `--num_processes`:**

```bash
trl sft --config sft_config.yaml --num_processes 4
```

**Predefined Accelerate configs** (provided by TRL): `single_gpu`, `multi_gpu`, `fsdp1`, `fsdp2`, `zero1`, `zero2`, `zero3`

```bash
trl sft --config sft_config.yaml --accelerate_config zero2
```

**FSDP:**

```bash
trl sft --config sft_config.yaml --accelerate_config fsdp2
```

**DeepSpeed ZeRO Stage 3:**

```bash
trl sft --config sft_config.yaml --accelerate_config zero3
```

**Custom Accelerate config:**

```bash
# Generate interactively
accelerate config

# Use the generated config
trl sft --config sft_config.yaml --config_file ~/.cache/huggingface/accelerate/default_config.yaml
```

### 9. Monitoring

Add `--report_to` to any command for experiment tracking:

- `--report_to trackio` (TRL's built-in)
- `--report_to wandb` (Weights & Biases — requires `WANDB_API_KEY=YOUR_KEY`)
- `--report_to tensorboard`

## Pitfalls

### CUDA Out of Memory

- Reduce `--per_device_train_batch_size` and increase `--gradient_accumulation_steps` to keep effective batch size constant.
- Enable `--use_peft` for LoRA training (dramatically lower VRAM).
- Enable `--gradient_checkpointing` to trade compute for memory.
- Try a smaller model or shorter sequence truncation.

### Dataset Loading Issues

- Verify the dataset exists on the Hugging Face Hub or at the local path provided.
- Check that dataset columns match the expected schema for the chosen method (see table in step 1).
- Use `--dataset_config` for multi-config datasets.
- Inspect before training:

  ```python
  from datasets import load_dataset
  ds = load_dataset("trl-lib/Capybara")
  print(ds)
  ```

### Model Loading Issues

- Verify the model exists on the Hugging Face Hub.
- Gated models require authentication: `hf auth login`.
- For local models, provide an absolute path.
- Ensure sufficient disk space and system RAM for model weights.

### Slow Training

- Enable `--packing` for short-sequence datasets (reduces padding waste).
- Increase `--per_device_train_batch_size` if VRAM allows.
- Enable `--tf32` on Ampere GPUs (A100, RTX 30xx+).
- Enable `--bf16` on supported hardware.
- Use multi-GPU via `--num_processes` or an Accelerate config.

### Generation Issues (GRPO / RLOO)

- Check prompt format in the dataset matches what the model expects.
- Adjust `--temperature` and `--top_p` for generation diversity.
- Verify the reward function (GRPO) or reward model path (RLOO) is correct and returns scalar scores.

### Windows / PowerShell Specific

- Multi-line bash commands with `\` will fail in PowerShell. Convert to single-line or use backtick continuation.
- Paths with spaces must be quoted in PowerShell.
- `~` expands correctly in most contexts but verify with `$HOME` if issues arise.

## Verification

1. **Confirm TRL is installed and CLI is available:**

   ```bash
   trl --help
   ```

   Expected: prints usage with subcommands `sft`, `dpo`, `grpo`, `kto`, `rloo`, `reward`.

2. **Confirm GPU is visible:**

   ```bash
   python -c "import torch; print('CUDA:', torch.cuda.is_available(), 'Devices:', torch.cuda.device_count())"
   ```

3. **Dry-run a small SFT job (quick smoke test):**

   ```bash
   trl sft --model_name_or_path Qwen/Qwen2-0.5B --dataset_name trl-lib/Capybara --max_steps 5 --output_dir ./trl-smoke-test
   ```

   Expected: training starts, logs loss, saves checkpoint to `./trl-smoke-test` within a few minutes.

4. **Check output directory after training:**

   ```bash
   ls ./trl-smoke-test
   ```

   Expected: `config.json`, `model.safetensors` (or adapter files for LoRA), `training_args.json`, and checkpoint subdirectories.

5. **Load the trained model to confirm it loads correctly:**

   ```python
   from transformers import AutoModelForCausalLM, AutoTokenizer
   model = AutoModelForCausalLM.from_pretrained("./trl-smoke-test")
   tokenizer = AutoTokenizer.from_pretrained("./trl-smoke-test")
   print("Model loaded successfully:", model.config.model_type)
   ```

## Related skills

- **huggingface-hub** — authentication, model upload/download, dataset management
- **accelerate** — distributed training configuration and launch
- **peft** — LoRA and other parameter-efficient fine-tuning methods
- **transformers** — base model loading, tokenization, inference

## Additional Resources

- **TRL Documentation:** https://huggingface.co/docs/trl
- **GitHub:** https://github.com/huggingface/trl
- **Examples:** https://github.com/huggingface/trl/tree/main/examples

## Limitations

- Use this skill only when the task clearly matches TRL's CLI scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- Never hardcode real API tokens or Hugging Face tokens in scripts or configs — use environment variables or `YOUR_KEY` placeholders.
