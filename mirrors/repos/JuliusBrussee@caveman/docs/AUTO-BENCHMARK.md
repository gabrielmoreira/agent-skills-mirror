# Auto benchmark: SWE-Interact + SWE-Together

Interim result, 2026-10-03. The run was paused at 85 paired tasks of 169. One attempt per task and arm.

**Auto on a Claude-only pool resolved 43.7% of tasks against 44.3% for Opus 5.5 at xhigh effort, at 0.46× the cost per attempt.**

## What was compared

The same coding agent (Claude Code 2.1.284, run under Harbor) on the same tasks, three ways:

| Arm | What it is |
|---|---|
| Baseline | Opus 5.5 at xhigh effort for every request, no routing |
| Auto, Claude pool | The router picks model and effort per ask from Opus 5.5 and Sonnet 5.5 |
| Auto, wide pool | Same router, plus GPT-6.1 Sol, GPT-6 Luna, Kimi, GLM, MiMo, DeepSeek and Qwen |

Tasks: SWE-Interact (76) and SWE-Together (110), minus 17 excluded, which leaves 169. A simulated user (Sonnet 5.5, medium effort, same in every arm) holds hidden requirements and reveals them as the agent works. SWE-Interact is scored 0 or 1 on hidden tests; SWE-Together gives a fractional score.

## Results, 85 paired tasks

| Arm | Suite | n | Resolved | $ per attempt |
|---|---|---:|---:|---:|
| Baseline | SWE-Interact | 32 | 43.8% | $10.17 |
| Auto, Claude pool | SWE-Interact | 32 | 37.5% | $4.41 |
| Auto, wide pool | SWE-Interact | 32 | 37.5% | $4.21 |
| Baseline | SWE-Together | 53 | 44.7% | $6.42 |
| Auto, Claude pool | SWE-Together | 53 | 47.4% | $3.09 |
| Auto, wide pool | SWE-Together | 53 | 46.2% | $3.02 |
| **Baseline** | **both** | 85 | **44.3%** | **$7.83** |
| **Auto, Claude pool** | **both** | 85 | **43.7%** | **$3.59** |
| **Auto, wide pool** | **both** | 85 | **42.9%** | **$3.47** |

Paired against the baseline on the same tasks (bootstrap 95% interval over tasks, 10,000 resamples):

| Arm | Suite | Resolve difference, points | Cost ratio |
|---|---|---:|---:|
| Auto, Claude pool | SWE-Interact | −6.2 [−21.9, +6.2] | 0.43× |
| Auto, Claude pool | SWE-Together | +2.9 [−1.5, +7.3] | 0.49× |
| Auto, Claude pool | both | **−0.5 [−6.8, +5.7]** | **0.46×** |
| Auto, wide pool | both | −1.4 [−8.9, +6.0] | 0.44× |

| Arm | Total, 85 tasks | $ per solved task | Median wall time | Agent timeouts |
|---|---:|---:|---:|---:|
| Baseline | $665.64 | $17.66 | 35.2 min | 9 |
| Auto, Claude pool | $305.05 | $8.21 | 15.9 min | 1 |
| Auto, wide pool | $294.78 | $8.08 | 16.7 min | 1 |

## What Auto actually did

| Arm | Model and effort mix, share of requests |
|---|---|
| Baseline | Opus 5.5 xhigh 100% |
| Auto, Claude pool | Opus medium 87%, Opus high 8%, Sonnet 5.5 5% |
| Auto, wide pool | Opus medium 85%, Opus high 9%, Sonnet 3%, DeepSeek V4.1 Flash 3% |

## Read this before you quote it

- **The baseline is Opus at xhigh effort.** Most of the saving comes from lower effort (Opus xhigh to Opus medium or high), not from cheaper models. Against an agent already on Opus at medium effort, expect much less. Not measured.
- **The quality gap is not resolved.** At 85 tasks the arms cannot be told apart: the interval is about ±7 points. On SWE-Interact alone Auto is 6 points behind, with an interval that includes zero.
- **Interim.** About half the tasks are paired. One attempt per task, so single tasks flip on luck.
- **Cost is list price,** from the router's price catalog, not billed amounts.
- **Router build.** The run used the router at build `3c0841c`. Whether the service behind Auto today behaves the same has not been re-measured.
- The raw trajectories are not in this repository.
