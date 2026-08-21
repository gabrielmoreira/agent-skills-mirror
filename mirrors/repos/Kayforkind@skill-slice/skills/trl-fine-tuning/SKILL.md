---
name: trl-fine-tuning
description: "Post-trains LLMs with Hugging Face TRL trainers: SFT, DPO, reward modeling, PPO, GRPO, and RLHF pipelines on CUDA. Use when instruction-tuning, preference-aligning, or running online RL with a reward function. Not for HuggingFace Trainer-only SFT without preferences, Unsloth/Axolotl YAML stacks, or CPU-only training; never skip LoRA/QLoRA on 7B-class models without checking VRAM."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [trl, transformers, datasets, peft, accelerate, torch]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Post-Training, TRL, Reinforcement Learning, Fine-Tuning, SFT, DPO, PPO, GRPO, RLHF, Preference Alignment, HuggingFace]
---

# TRL — Transformer Reinforcement Learning Fine-Tuning

## Overview

TRL (Transformer Reinforcement Learning) is the HuggingFace library for post-training language models. It provides trainers for supervised fine-tuning (SFT), preference alignment (DPO and variants), reward modeling, and online reinforcement learning (PPO, GRPO, RLOO, OnlineDPO). This skill covers the full lifecycle from base model to human-aligned model, with copy-pasteable commands and progressive disclosure into reference files for advanced topics.

## When to Use

Use this skill when any of the following apply:

- You need to **instruction-tune** a base model with prompt-completion pairs → SFT
- You have **preference data** (chosen/rejected pairs) and want alignment without a reward model → DPO
- You are building a **full RLHF pipeline** (SFT → Reward Model → PPO)
- You need to **train a reward model** to score generations
- You want **online RL** with a custom reward function, especially under memory constraints → GRPO
- You need **PPO, RLOO, or OnlineDPO** for maximum control over reinforcement learning

**Trigger keywords**: fine-tune, fine-tuning, SFT, DPO, PPO, GRPO, RLHF, reward model, preference alignment, post-training, instruction tuning, RL, reinforcement learning, TRL.

**Use alternatives instead:**

- **HuggingFace Trainer** — basic fine-tuning without RL or preferences
- **Axolotl** — YAML-based training configuration workflows
- **Unsloth** — fast LoRA training for single-GPU scenarios
- **LitGPT** — educational / minimal fine-tuning

## Prerequisites

### Installation

```bash
pip install trl transformers datasets peft accelerate
```

For GPU support ensure `torch` is installed with the correct CUDA build for your platform.

### Hardware Requirements

| Method | Model Size | Approx. VRAM | Notes |
|--------|-----------|-------------|-------|
| SFT (LoRA) | 7B | 16 GB | LoRA/QLoRA required |
| DPO | 7B | 24 GB | Stores reference model in memory |
| PPO | 7B | 40 GB | Policy + reward model + value model |
| GRPO | 7B | 24 GB | More memory-efficient than PPO |

- **GPU**: NVIDIA with CUDA required for all methods.
- **Multi-GPU**: Supported via `accelerate`. Use `accelerate launch` for distributed training.
- **Mixed precision**: BF16 recommended on A100/H100. Use FP16 on older architectures (V100, T4).
- **Memory optimization**: Use LoRA/QLoRA for all methods, enable gradient checkpointing, reduce batch size with gradient accumulation to maintain effective batch.

### Windows Host Notes

Primary development environment is Windows with PowerShell. When running CLI commands on Windows:

- Use PowerShell syntax (backticks for line continuation, or keep commands on one line).
- Paths use backslashes in PowerShell: `~\models\Qwen2.5-0.5B-SFT`.
- Python virtual environments: `.\venv\Scripts\Activate.ps1`.
- For `accelerate launch`, use `accelerate launch` directly in PowerShell — no special quoting needed.

## Procedure

### Method Selection Guide

| You have… | You want… | Use |
|-----------|----------|-----|
| Prompt-completion pairs | Basic instruction following | **SFT** |
| Chosen/rejected preference pairs | Simple alignment, no reward model | **DPO** |
| A trained reward model | Maximum RL control | **PPO** |
| A reward function, limited VRAM | Online RL | **GRPO** |
| Preference data, building RLHF | Score generations | **Reward Model** |

---

### Workflow 1: Supervised Fine-Tuning (SFT)

Instruction-tune a base model on prompt-completion pairs.

**Step 1 — Load model, tokenizer, and dataset:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")

dataset = load_dataset("trl-lib/Capybara", split="train")
```

**Step 2 — Configure and train:**

```python
training_args = SFTConfig(
    output_dir="Qwen2.5-0.5B-SFT",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=2e-5,
    logging_steps=10,
    save_strategy="epoch"
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer
)
trainer.train()
trainer.save_model()
```

> **Load `references/sft-training.md`** when you need: dataset format details, chat template configuration, packing strategies, multi-GPU training setup, or LoRA/QLoRA configuration for SFT.

---

### Workflow 2: DPO — Preference Alignment Without a Reward Model

Align a model with chosen/rejected preference pairs. No reward model required.

**Step 1 — Prepare preference dataset:**

Required format (JSON):

```json
{
  "prompt": "What is the capital of France?",
  "chosen": "The capital of France is Paris.",
  "rejected": "I don't know."
}
```

```python
from datasets import load_dataset

dataset = load_dataset("trl-lib/ultrafeedback_binarized", split="train")
# Or load your own:
# dataset = load_dataset("json", data_files="preferences.json")
```

**Step 2 — Configure DPO:**

```python
from trl import DPOConfig

config = DPOConfig(
    output_dir="Qwen2.5-0.5B-DPO",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=5e-7,
    beta=0.1,               # KL penalty strength (default 0.1)
    max_prompt_length=512,
    max_length=1024,
    logging_steps=10
)
```

**Step 3 — Train with DPOTrainer:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOTrainer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

trainer = DPOTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    processing_class=tokenizer
)
trainer.train()
trainer.save_model()
```

**CLI alternative:**

```bash
trl dpo \
    --model_name_or_path Qwen/Qwen2.5-0.5B-Instruct \
    --dataset_name argilla/Capybara-Preferences \
    --output_dir Qwen2.5-0.5B-DPO \
    --per_device_train_batch_size 4 \
    --learning_rate 5e-7 \
    --beta 0.1
```

> **Load `references/dpo-variants.md`** when you need: IPO, cDPO, RPO, or other DPO loss functions, or recommended hyperparameters for DPO variants.

---

### Workflow 3: Full RLHF Pipeline (SFT → Reward Model → PPO)

Complete pipeline from base model to human-aligned model.

**Checklist:**

```
RLHF Training:
- [ ] Step 1: Supervised fine-tuning (SFT)
- [ ] Step 2: Train reward model
- [ ] Step 3: PPO reinforcement learning
- [ ] Step 4: Evaluate aligned model
```

**Step 1 — SFT:** Follow Workflow 1 above. Save to `Qwen2.5-0.5B-SFT`.

**Step 2 — Train reward model:**

```python
from transformers import AutoModelForSequenceClassification
from trl import RewardTrainer, RewardConfig
from datasets import load_dataset

model = AutoModelForSequenceClassification.from_pretrained(
    "Qwen2.5-0.5B-SFT",
    num_labels=1  # Single reward score
)
tokenizer = AutoTokenizer.from_pretrained("Qwen2.5-0.5B-SFT")

dataset = load_dataset("trl-lib/ultrafeedback_binarized", split="train")

training_args = RewardConfig(
    output_dir="Qwen2.5-0.5B-Reward",
    per_device_train_batch_size=2,
    num_train_epochs=1,
    learning_rate=1e-5
)

trainer = RewardTrainer(
    model=model,
    args=training_args,
    processing_class=tokenizer,
    train_dataset=dataset
)
trainer.train()
trainer.save_model()
```

> **Load `references/reward-modeling.md`** when you need: outcome vs process reward models, Bradley-Terry loss details, reward model evaluation metrics, or reward hacking mitigation.

**Step 3 — PPO reinforcement learning:**

```bash
python -m trl.scripts.ppo \
    --model_name_or_path Qwen2.5-0.5B-SFT \
    --reward_model_path Qwen2.5-0.5B-Reward \
    --dataset_name trl-internal-testing/descriptiveness-sentiment-trl-style \
    --output_dir Qwen2.5-0.5B-PPO \
    --learning_rate 3e-6 \
    --per_device_train_batch_size 64 \
    --total_episodes 10000
```

> **Load `references/online-rl.md`** when you need: PPO, RLOO, or OnlineDPO detailed configurations, KL coefficient tuning, or multi-GPU online RL setup.

**Step 4 — Evaluate:**

```python
from transformers import pipeline

generator = pipeline("text-generation", model="Qwen2.5-0.5B-PPO")

prompt = "Explain quantum computing to a 10-year-old"
output = generator(prompt, max_length=200)[0]["generated_text"]
print(output)
```

---

### Workflow 4: GRPO — Memory-Efficient Online RL

Train with reinforcement learning using a custom reward function. GRPO is more memory-efficient than PPO because it does not require a separate value model.

> **Load `references/grpo-training.md`** when you need: reward function design philosophy, training insights (why loss increases, mode collapse detection), hyperparameter tuning, multi-stage training, or troubleshooting. A production-ready training script is in `templates/basic_grpo_training.py`.

**Step 1 — Define reward function:**

```python
def reward_function(completions, **kwargs):
    """
    Compute rewards for completions.

    Args:
        completions: List of generated texts

    Returns:
        List of reward scores (floats)
    """
    rewards = []
    for completion in completions:
        score = len(completion.split())                    # Favor longer responses
        score += len(set(completion.lower().split()))      # Reward unique words
        rewards.append(score)
    return rewards
```

Or use a trained reward model:

```python
from transformers import pipeline

reward_model = pipeline("text-classification", model="reward-model-path")

def reward_from_model(completions, prompts, **kwargs):
    full_texts = [p + c for p, c in zip(prompts, completions)]
    results = reward_model(full_texts)
    return [r["score"] for r in results]
```

**Step 2 — Configure GRPO:**

```python
from trl import GRPOConfig

config = GRPOConfig(
    output_dir="Qwen2-GRPO",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=1e-5,
    num_generations=4,       # Generate 4 completions per prompt
    max_new_tokens=128
)
```

**Step 3 — Train with GRPOTrainer:**

```python
from datasets import load_dataset
from trl import GRPOTrainer

dataset = load_dataset("trl-lib/tldr", split="train")

trainer = GRPOTrainer(
    model="Qwen/Qwen2-0.5B-Instruct",
    reward_funcs=reward_function,
    args=config,
    train_dataset=dataset
)
trainer.train()
```

**CLI:**

```bash
trl grpo \
    --model_name_or_path Qwen/Qwen2-0.5B-Instruct \
    --dataset_name trl-lib/tldr \
    --output_dir Qwen2-GRPO \
    --num_generations 4
```

---

## Pitfalls

### OOM during DPO training

DPO stores both the policy and a frozen reference model in memory. Reduce batch size and sequence length, or enable gradient checkpointing:

```python
config = DPOConfig(
    per_device_train_batch_size=1,       # Reduce from 4
    max_length=512,                      # Reduce from 1024
    gradient_accumulation_steps=8        # Maintain effective batch
)
```

```python
model.gradient_checkpointing_enable()
```

### Poor DPO alignment quality

The `beta` parameter controls the KL penalty strength. Tune it:

- **Higher beta** (e.g. `0.5`) = more conservative, stays closer to reference model.
- **Lower beta** (e.g. `0.01`) = more aggressive alignment, risk of over-optimization.

```python
config = DPOConfig(beta=0.5)   # More conservative
config = DPOConfig(beta=0.01)  # More aggressive
```

### Reward model not learning

Check loss type and learning rate. Reward models often need lower LR and more epochs:

```python
config = RewardConfig(
    learning_rate=1e-5,    # Try different LR
    num_train_epochs=3     # Train longer
)
```

Verify your preference dataset has clear winners:

```python
print(dataset[0])
# Should show clear chosen > rejected quality difference
```

### PPO training unstable

Adjust KL coefficient and clip range:

```python
config = PPOConfig(
    kl_coef=0.1,      # Increase from 0.05 to stabilize
    cliprange=0.1     # Reduce from 0.2 to limit policy updates
)
```

### GRPO loss increasing

GRPO loss can increase during training — this is expected behavior and does not necessarily indicate a problem. The loss in RL is not directly comparable to supervised losses. See `references/grpo-training.md` for detailed explanation and mode collapse detection.

### General memory optimization

- Use LoRA/QLoRA for all methods to drastically reduce VRAM.
- Enable gradient checkpointing: `model.gradient_checkpointing_enable()`.
- Reduce `per_device_train_batch_size` and compensate with `gradient_accumulation_steps`.
- Use BF16 mixed precision on A100/H100.

## Verification

### Verify SFT model was saved

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen2.5-0.5B-SFT")
tokenizer = AutoTokenizer.from_pretrained("Qwen2.5-0.5B-SFT")
print("Model loaded successfully:", model.config.model_type)
```

### Verify DPO model generates aligned outputs

```python
from transformers import pipeline

generator = pipeline("text-generation", model="Qwen2.5-0.5B-DPO", tokenizer="Qwen2.5-0.5B-DPO")
output = generator("What is the capital of France?", max_new_tokens=50)[0]["generated_text"]
print(output)
# Expect: response aligned with preference data style
```

### Verify reward model produces scores

```python
from transformers import pipeline

reward_pipe = pipeline("text-classification", model="Qwen2.5-0.5B-Reward")
score = reward_pipe("The capital of France is Paris.")
print("Reward score:", score)
# Expect: a float score in the "score" field
```

### Verify training logs

Check that loss is decreasing (SFT, DPO, Reward Model) or that reward is increasing (PPO, GRPO):

```bash
# Check trainer_state.json in output directory
cat Qwen2.5-0.5B-SFT/trainer_state.json | python -m json.tool | head -20
```

On Windows PowerShell:

```powershell
Get-Content Qwen2.5-0.5B-SFT\trainer_state.json | ConvertFrom-Json | Select-Object -ExpandProperty log_history | Select-Object -First 5
```

### Verify GRPO reward trend

```python
import json

with open("Qwen2-GRPO/trainer_state.json") as f:
    state = json.load(f)

rewards = [entry.get("reward") for entry in state["log_history"] if "reward" in entry]
print("Reward trend:", rewards)
# Expect: generally increasing reward over training steps
```

## Related Skills

- **peft-lora** — LoRA/QLoRA configuration for memory-efficient fine-tuning
- **huggingface-training** — Base HuggingFace Trainer for non-RL fine-tuning
- **axolotl-training** — YAML-based training configuration alternative
- **unsloth-finetuning** — Fast LoRA training for single-GPU scenarios

## Resources

- **TRL Docs**: https://huggingface.co/docs/trl/
- **TRL GitHub**: https://github.com/huggingface/trl
- **Example scripts**: https://github.com/huggingface/trl/tree/main/examples/scripts
- **Key papers**:
  - "Training language models to follow instructions with human feedback" (InstructGPT, 2022)
  - "Direct Preference Optimization: Your Language Model is Secretly a Reward Model" (DPO, 2023)
  - "Group Relative Policy Optimization" (GRPO, 2024)

## Reference Files

Load these when the corresponding topic is needed — do not load all at once:

| File | When to load |
|------|-------------|
| `references/sft-training.md` | Dataset formats, chat templates, packing, multi-GPU SFT |
| `references/dpo-variants.md` | IPO, cDPO, RPO, other DPO loss functions and hyperparameters |
| `references/reward-modeling.md` | Outcome vs process rewards, Bradley-Terry loss, RM evaluation |
| `references/online-rl.md` | PPO, RLOO, OnlineDPO detailed configs and KL tuning |
| `references/grpo-training.md` | GRPO reward design, loss behavior, mode collapse, multi-stage training |
| `templates/basic_grpo_training.py` | Production-ready GRPO training script template |
