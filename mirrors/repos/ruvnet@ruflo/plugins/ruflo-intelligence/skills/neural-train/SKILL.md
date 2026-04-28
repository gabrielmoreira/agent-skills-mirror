---
name: neural-train
description: Train SONA neural patterns from successful task completions, view learned patterns, and optimize the intelligence pipeline
allowed-tools: mcp__claude-flow__neural_train mcp__claude-flow__neural_status mcp__claude-flow__neural_patterns mcp__claude-flow__neural_predict mcp__claude-flow__neural_optimize mcp__claude-flow__neural_compress mcp__claude-flow__hooks_pretrain mcp__claude-flow__hooks_intelligence_trajectory-start mcp__claude-flow__hooks_intelligence_trajectory-step mcp__claude-flow__hooks_intelligence_trajectory-end mcp__claude-flow__hooks_intelligence_pattern-store mcp__claude-flow__hooks_intelligence_learn mcp__claude-flow__ruvllm_sona_create mcp__claude-flow__ruvllm_sona_adapt Bash
---

# Neural Training

Train and manage SONA neural patterns for self-learning.

## When to use

After completing a successful task, use this skill to capture what worked and train the intelligence system so future tasks benefit from learned patterns.

## Steps

1. **Check current neural status** — call `mcp__claude-flow__neural_status` to see active patterns and training state
2. **Start a trajectory** — call `mcp__claude-flow__hooks_intelligence_trajectory-start` with the task context
3. **Record steps** — for each significant action, call `mcp__claude-flow__hooks_intelligence_trajectory-step`
4. **End trajectory** — call `mcp__claude-flow__hooks_intelligence_trajectory-end` with outcome (success/failure)
5. **Train patterns** — call `mcp__claude-flow__neural_train` with `--pattern-type coordination --epochs 10`
6. **Store patterns** — call `mcp__claude-flow__hooks_intelligence_pattern-store` to persist learnings
7. **Verify** — call `mcp__claude-flow__neural_patterns` to confirm patterns were stored

## CLI alternative

```bash
npx @claude-flow/cli@latest neural train --pattern-type coordination --epochs 10
npx @claude-flow/cli@latest neural patterns --list
npx @claude-flow/cli@latest neural status
npx @claude-flow/cli@latest hooks pretrain --model-type moe --epochs 10
```

## SONA adaptation

For real-time micro-adaptation (<0.05ms), use:
- `mcp__claude-flow__ruvllm_sona_create` to initialize a SONA instance
- `mcp__claude-flow__ruvllm_sona_adapt` to adapt weights based on feedback
