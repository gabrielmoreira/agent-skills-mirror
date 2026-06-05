---
mode: agent
description: Test model dispatcher—probe which models are loaded and route a test prompt.
---

# /ai-dispatch-test — Model Dispatcher Test

This command tests the **model-dispatch plugin runtime**, verifying which models are loaded and routing work to them without reload overhead.

## What it does

1. **Probes LM Studio / Ollama** to see which tier models are currently loaded
2. **Reports availability** so you know which tiers are ready to use
3. **Routes a test prompt** to a requested tier (with fallback to next available)
4. **Shows response** from the loaded model

## Usage

Run from the workspace root:

```powershell
# List all tiers + whether their models are loaded
pwsh -NoProfile -File .github/debug/dispatch-test.ps1 -Command probe

# Show which tiers have models loaded and ready
pwsh -NoProfile -File .github/debug/dispatch-test.ps1 -Command status

# Dispatch a test prompt to a specific tier
pwsh -NoProfile -File .github/debug/dispatch-test.ps1 -Command dispatch -Tier local-fast -Prompt "Say hello in one word"
```

## What to expect

**If LM Studio is running on localhost:1234 with models loaded:**
- `probe` lists tiers + "✓ LOADED" or "✗ not loaded"
- `status` shows tier names with loaded models
- `dispatch` executes inference to the tier (or fallback)

**If LM Studio is not running:**
- `probe` shows all models as "✗ not loaded"
- `dispatch` returns error + reason (endpoint unreachable)

## Next steps

1. Start LM Studio on `localhost:1234` with models loaded
2. Run `pwsh -NoProfile -File .github/debug/dispatch-test.ps1 -Command probe` to verify
3. Dispatch test prompts via `dispatch` subcommand
4. Use this workflow in agents to route real work to loaded models (no reload)

## Design

The dispatcher is **read-only**: it probes endpoints but never loads/unloads models. Models must be pre-loaded in LM Studio or Ollama. This avoids the reload overhead you wanted to eliminate.

Once a model is loaded, the dispatcher can route unlimited work to it until you manually unload it.
