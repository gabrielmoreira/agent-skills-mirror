---
name: weights-and-biases
description: "Logs ML training with wandb.init/log, hyperparameter sweeps, artifact lineage, and the model registry. Use when tracking experiments, comparing runs, or sweeping hyperparameters in PyTorch, TensorFlow, or HuggingFace. Not for LLM app tracing and prompts (langfuse) or local Hub eval harnesses (community-evals)."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [wandb]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MLOps, Weights And Biases, WandB, Experiment Tracking, Hyperparameter Tuning, Model Registry, Collaboration, Real-Time Visualization, PyTorch, TensorFlow, HuggingFace]
---

# Weights & Biases: ML Experiment Tracking & MLOps

## When to Use

Use this skill when you need to:

- **Track ML experiments** with automatic metric, config, and system logging
- **Visualize training** in real-time dashboards and compare runs across hyperparameters
- **Run hyperparameter sweeps** (grid, random, Bayesian) to optimize model performance
- **Manage model registry** with versioning, aliases, and lineage
- **Track artifacts** (datasets, models, code) with full provenance
- **Integrate W&B** into PyTorch, TensorFlow/Keras, HuggingFace, or PyTorch Lightning workflows
- **Collaborate on ML projects** with shared team workspaces and reports

**Trigger keywords:** wandb, weights and biases, experiment tracking, sweep, hyperparameter tuning, model registry, artifact lineage, training dashboard, `wandb.init`, `wandb.log`, `wandb.sweep`

## Prerequisites

- Python 3.8+
- A W&B account (free tier sufficient for public projects)
- `pip install wandb`
- API key obtained from https://wandb.ai/authorize

### Authentication

```powershell
# Windows PowerShell (primary host)
$env:WANDB_API_KEY = "YOUR_KEY"
wandb login
```

```bash
# Linux / macOS
export WANDB_API_KEY=YOUR_KEY
wandb login
```

> **Never commit live API keys.** Use `YOUR_KEY` placeholder in all shared files. Store real keys in environment variables or a secrets manager.

## Procedure

### 1. Install and Authenticate

```bash
pip install wandb
wandb login   # prompts for API key from https://wandb.ai/authorize
```

Or set the key programmatically before any `wandb.init` call:

```bash
export WANDB_API_KEY=YOUR_KEY
```

### 2. Initialize a Run

```python
import wandb

run = wandb.init(
    project="my-project",
    name="resnet50-lr0.001-bs32",
    tags=["baseline", "resnet"],
    group="resnet-experiments",
    job_type="train",
    notes="First baseline run with standard augmentation",
    config={
        "learning_rate": 0.001,
        "epochs": 10,
        "batch_size": 32,
        "architecture": "ResNet50",
    },
)

print(f"Run ID: {run.id}")
print(f"Run URL: {run.url}")
```

### 3. Log Metrics During Training

```python
for epoch in range(run.config.epochs):
    train_loss = train_epoch()
    val_loss = validate()

    wandb.log({
        "epoch": epoch,
        "train/loss": train_loss,
        "val/loss": val_loss,
        "train/accuracy": train_acc,
        "val/accuracy": val_acc,
    })
```

Log with an explicit x-axis step:

```python
wandb.log({"loss": loss}, step=global_step)
```

Log media, histograms, and tables:

```python
wandb.log({"examples": [wandb.Image(img) for img in images]})
wandb.log({"gradients": wandb.Histogram(gradients)})

table = wandb.Table(columns=["id", "prediction", "ground_truth"])
table.add_data(0, "cat", "cat")
wandb.log({"predictions": table})
```

### 4. Save Model Checkpoints

**Quick save (file upload):**

```python
import torch

checkpoint = {
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": loss,
}
torch.save(checkpoint, "checkpoint.pth")
wandb.save("checkpoint.pth")
```

**Artifact save (recommended for lineage):**

```python
artifact = wandb.Artifact("model", type="model")
artifact.add_file("checkpoint.pth")
wandb.log_artifact(artifact)
```

### 5. Run a Hyperparameter Sweep

**Define sweep config:**

```python
sweep_config = {
    "method": "bayes",          # or "grid", "random"
    "metric": {"name": "val/accuracy", "goal": "maximize"},
    "parameters": {
        "learning_rate": {"distribution": "log_uniform", "min": 1e-5, "max": 1e-1},
        "batch_size": {"values": [16, 32, 64, 128]},
        "optimizer": {"values": ["adam", "sgd", "rmsprop"]},
        "dropout": {"distribution": "uniform", "min": 0.1, "max": 0.5},
    },
}

sweep_id = wandb.sweep(sweep_config, project="my-project")
```

**Define training function and launch agent:**

```python
def train():
    wandb.init()
    lr = wandb.config.learning_rate
    batch_size = wandb.config.batch_size
    optimizer_name = wandb.config.optimizer

    model = build_model(wandb.config)
    optimizer = get_optimizer(optimizer_name, lr)

    for epoch in range(NUM_EPOCHS):
        train_loss = train_epoch(model, optimizer, batch_size)
        val_acc = validate(model)
        wandb.log({"train/loss": train_loss, "val/accuracy": val_acc})

wandb.agent(sweep_id, function=train, count=50)
```

> **Load `references/sweeps.md`** when the user needs advanced sweep strategies, parallel agents, or Bayesian early-stopping configurations.

### 6. Log and Consume Artifacts

**Log an artifact:**

```python
artifact = wandb.Artifact(
    name="training-dataset",
    type="dataset",
    description="ImageNet training split",
    metadata={"size": "1.2M images", "split": "train"},
)
artifact.add_file("data/train.csv")
artifact.add_dir("data/images/")
wandb.log_artifact(artifact)
```

**Download and use an artifact:**

```python
run = wandb.init(project="my-project")
artifact = run.use_artifact("training-dataset:latest")
artifact_dir = artifact.download()
data = load_data(f"{artifact_dir}/train.csv")
```

> **Load `references/artifacts.md`** when the user needs artifact versioning patterns, dataset lineage graphs, or cross-project artifact reuse.

### 7. Register a Model

```python
model_artifact = wandb.Artifact(
    name="resnet50-model",
    type="model",
    metadata={"architecture": "ResNet50", "accuracy": 0.95},
)
model_artifact.add_file("model.pth")
wandb.log_artifact(model_artifact, aliases=["best", "production"])

# Link to model registry
run.link_artifact(model_artifact, "model-registry/production-models")
```

### 8. Framework Integrations

**HuggingFace Transformers:**

```python
from transformers import Trainer, TrainingArguments
import wandb

wandb.init(project="hf-transformers")

training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",
    run_name="bert-finetuning",
    logging_steps=100,
    save_steps=500,
)

trainer = Trainer(model=model, args=training_args,
                  train_dataset=train_dataset, eval_dataset=eval_dataset)
trainer.train()
```

**PyTorch Lightning:**

```python
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import WandbLogger

wandb_logger = WandbLogger(project="lightning-demo", log_model=True)
trainer = Trainer(logger=wandb_logger, max_epochs=10)
trainer.fit(model, datamodule=dm)
```

**Keras / TensorFlow:**

```python
import wandb
from wandb.keras import WandbCallback

wandb.init(project="keras-demo")
model.fit(x_train, y_train, validation_data=(x_val, y_val),
          epochs=10, callbacks=[WandbCallback()])
```

> **Load `references/integrations.md`** when the user needs framework-specific examples beyond the three above (e.g., XGBoost, Scikit-learn, JAX).

### 9. Offline Mode (Unstable Connections)

```python
import os
os.environ["WANDB_MODE"] = "offline"

wandb.init(project="my-project")
# ... training code ...

# Sync later
# wandb sync <run_directory>
```

## Examples

### Custom Charts and Confusion Matrix

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x, y)
wandb.log({"custom_plot": wandb.Image(fig)})

wandb.log({
    "conf_mat": wandb.plot.confusion_matrix(
        probs=None,
        y_true=ground_truth,
        preds=predictions,
        class_names=class_names,
    )
})
```

### Descriptive Run Naming

```python
# Good
wandb.init(project="nlp-classification",
           name="bert-base-lr0.001-bs32-epoch10")

# Bad
wandb.init(project="nlp", name="run1")
```

### Log System and Data Metrics

```python
wandb.log({
    "gpu/util": gpu_utilization,
    "gpu/memory": gpu_memory_used,
    "cpu/util": cpu_utilization,
    "git_commit": git_commit_hash,
    "data/train_size": len(train_dataset),
    "data/val_size": len(val_dataset),
})
```

## Pitfalls

- **Forgetting `wandb.finish()`**: Always call `wandb.finish()` at the end of training. If the process crashes, the run may remain in a "running" state. Use `with wandb.init(...) as run:` context manager to guarantee cleanup.
- **Logging too frequently**: Calling `wandb.log` every batch with high-frequency data can slow training and flood dashboards. Batch logging every N steps (e.g., `if batch_idx % 100 == 0`) is preferred.
- **Mismatched metric keys across runs**: W&B groups metrics by key. If one run logs `"val/loss"` and another logs `"validation_loss"`, they will not appear on the same chart. Standardize key names.
- **Not setting `WANDB_MODE=offline` on air-gapped machines**: Training will hang or fail on network timeouts. Set offline mode and `wandb sync` later.
- **Hardcoding API keys in source files**: Never embed real keys. Use environment variables (`WANDB_API_KEY`) or a secrets manager. Use `YOUR_KEY` in all shared examples.
- **Sweep agent count too high without resources**: `wandb.agent(..., count=50)` launches 50 sequential trials by default. For parallel sweeps, launch multiple agent processes pointing to the same `sweep_id`.
- **Artifact name collisions**: Artifact names must be unique within a project and type. Re-logging with the same name creates a new version, not an overwrite. Use aliases (`:latest`, `:best`) to reference specific versions.
- **Large file uploads blocking training**: `wandb.save` and `artifact.add_file` upload synchronously by default. For very large checkpoints, consider logging artifacts less frequently or using `artifact.add_reference` for cloud-stored files.
- **Windows path issues**: Use raw strings or forward slashes in Python paths on Windows (`r"~\data"` or `"data/train.csv"`). W&B artifacts handle both but mixing backslashes in artifact names is unsupported.

## Verification

### Verify Installation and Auth

```bash
wandb --version
# Expected: wandb, version X.Y.Z

wandb status
# Expected: "Logged in" with entity name
```

### Verify a Run Was Logged

After running a training script:

```bash
wandb sync --view <run_directory>   # offline mode
# Or check the printed run URL in stdout:
# https://wandb.ai/<entity>/<project>/runs/<run_id>
```

### Verify Artifacts

```python
import wandb
run = wandb.init(project="my-project")
art = run.use_artifact("training-dataset:latest")
print(art.version)   # Expected: v0, v1, ...
print(art.manifest.entries)  # Lists files in artifact
```

### Verify Sweep Is Running

```bash
# In the W&B UI:
# https://wandb.ai/<entity>/<project>/sweeps/<sweep_id>
# Expected: agent runs appearing with logged val/accuracy
```

### Verify Offline Sync

```bash
wandb sync ./wandb/offline-run-20250101_000000-<run_id>
# Expected: "Synced <N> files" and a live run URL
```

## Related Skills

- `references/sweeps.md` — Comprehensive hyperparameter optimization guide (load when configuring advanced sweeps)
- `references/artifacts.md` — Data and model versioning patterns (load when building artifact pipelines)
- `references/integrations.md` — Framework-specific integration examples (load when integrating beyond PyTorch/Lightning/Keras/HuggingFace)

## Resources

- **Documentation**: https://docs.wandb.ai
- **GitHub**: https://github.com/wandb/wandb
- **Examples**: https://github.com/wandb/examples
- **Community**: https://wandb.ai/community
- **Discord**: https://wandb.me/discord
