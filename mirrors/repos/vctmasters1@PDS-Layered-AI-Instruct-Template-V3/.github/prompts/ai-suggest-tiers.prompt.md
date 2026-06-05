---
mode: agent
description: Analyze hardware + loaded models; recommend optimal tier configuration for best space/performance. Includes interactive choice and configuration management.
---

# /ai-suggest-tiers — Tier Configuration Advisor

Analyzes your machine hardware and currently-loaded LLMs to recommend the **best tier assignments** for optimal space and performance utilization.

## What it does

1. **Probes your hardware**: CPU cores, RAM, GPU count/VRAM
2. **Checks loaded models**: queries LM Studio for what's currently loaded and estimated size
3. **Recommends assignments**: which model should go to which tier
4. **Calculates utilization**: shows VRAM % usage across compute GPUs
5. **Outputs copy-paste config**: ready-to-use `tiers.yaml` tier definitions

## Example output

```
=== HARDWARE ===
CPU:  24 cores / 48 threads
RAM:  255.5 GB

=== GPUs ===
GPU 0: NVIDIA GeForce RTX 5090    32.0 GB  (compute)
GPU 1: NVIDIA GeForce RTX 5090    32.0 GB  (compute)
GPU 2: NVIDIA GeForce RTX 4060 Ti 16.0 GB  (display-only)
GPU 3: NVIDIA GeForce RTX 5090    32.0 GB  (compute)

Total compute VRAM: 96.0 GB

=== RECOMMENDATIONS ===
local-embed    → nomic-ai/text-embedding-...  ( 0.5 GB, GPUs [0])
local-fast     → qwen/qwen3.6-27b              ( 4.5 GB, GPUs [0])
local-strong   → qwen/qwen3.6-35b-a3b          (20.0 GB, GPUs [0, 1])
local-heavy    → qwen/qwen3-coder-next         (40.0 GB, GPUs [0, 1, 3])
cloud-frontier → copilot-chat                  ( 0.0 GB)

=== SPACE UTILIZATION ===
Assigned: 65 GB / 96 GB (67.7% utilization, 31 GB headroom)
```

## Usage

```powershell
pwsh .github/debug/suggest-tiers.ps1
```

Or directly:

```pwsh
python .ai/plugins/model-dispatch/suggest_tiers.py
```

## How to use the recommendations

### Standard Workflow (Verify → Analyze → Apply → Test)

1. **Verify current state first** (confirms your desired models match what's actually loaded):
   ```powershell
   pwsh .github/debug/verify-loaded-models.ps1
   ```
   Expected output: `√ STATE IS VALID: All desired models are loaded!`

2. **Run the advisor** to analyze your hardware and get recommendations:
   ```powershell
   pwsh .github/debug/suggest-tiers.ps1
   ```
   This shows your hardware + loaded models + optimal tier assignments.

3. **Choose how to proceed**:
   - **Option A**: Use the recommended config (suggested automatically)
   - **Option B**: Use your currently-loaded models as-is
   - **Option C**: Ask cloud-frontier (Copilot) to analyze and recommend based on latest model knowledge

4. **Apply the config**:
   ```powershell
   pwsh .github/debug/config-swap.ps1 -Command save -Name "experiment-v1"
   ```
   This saves your choice as a named snapshot you can revert to later.

5. **Validate & Test**:
   ```powershell
   pwsh .github/scripts/validate-instructions.ps1
   pwsh .github/debug/dispatch-test.ps1 -Command probe
   ```

### Configuration Management (Save, Switch, Compare)

All configurations are saved as **snapshots** (machine-specific, not committed):

```powershell
# List all saved configs
pwsh .github/debug/config-swap.ps1 -Command list
→ current | 2026-06-04 06:04:08 | tiers=✓ | strategy=✓

# Switch to a previous config (you'll be prompted to save first if current differs from backup)
pwsh .github/debug/config-swap.ps1 -Command switch -Name "experiment-v1"

# Save current as named snapshot
pwsh .github/debug/config-swap.ps1 -Command save -Name "production"

# Apply a config from file
pwsh .github/debug/config-swap.ps1 -Command apply -ConfigFile tiers-experimental.yaml
```

**Smart prompting**: If you switch or apply configs and your current config differs from the latest backup, you'll be prompted to save first (prevents accidental loss).

## Example: applying the advice

If the advisor recommends:

```yaml
local-heavy:
  provider: lmstudio
  model_id: qwen/qwen3-coder-next
  gpu_devices: [0, 1, 3]
```

This means:
- The 80B coder model should be loaded in LM Studio
- It will run on GPUs 0, 1, and 3 (in parallel; constrain via `CUDA_VISIBLE_DEVICES=0,1,3`)
- GPU 2 (your display-only 4060 Ti) is excluded from this tier
- When you dispatch work to `local-heavy`, it automatically routes to `qwen/qwen3-coder-next`

## Key insight

The advisor optimizes for **space and throughput**. It says:

> Given your 96 GB compute VRAM and these loaded models, the best utilization is to assign them as shown above. This keeps GPUs busy, avoids reloads, and leaves headroom for additional models if needed.

**You can now experiment safely**: Save a config as a snapshot, try a new setup, and revert in seconds if you want to compare.

No more guessing. No more wasted GPU time on reload overhead. And configuration history at your fingertips.
