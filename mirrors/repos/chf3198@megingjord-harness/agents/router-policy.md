# Router Policy Spec v1.0.0

## Routing Principles
- Prefer deterministic constraints before any score-based choice.
- Prefer the lowest-capable tier that can still satisfy the task.
- Treat empirical scores as a tie-breaker and fallback signal.
- Treat rate limits, offline providers, and sensitivity constraints as hard stops.

## Hard Constraints
- Privacy or local-only requirement → avoid cloud-only providers.
- Availability or rate-limit failure → skip the candidate.
- Context or tool requirements not met → skip the candidate.
- Ambiguous scope or multi-solution request → route to `planner`.

## Ranking Signals
- Task fit: security, implementation, quick lookup, or design complexity.
- Empirical quality: controlled eval score or proven provider performance.
- Cost class: choose the cheapest option that clears the quality bar.
- Latency and throughput: prefer fast tiers when the task is latency-sensitive.
- Risk: prefer higher-control tiers for security-sensitive or high-impact work.

## Minimum Task Metadata
- Intent class
- Sensitivity or privacy level
- Context length expectation
- Latency budget
- Tool-use requirement
- Offline/local execution requirement

## Fallback Guidance
1. Pick the best-fit tier from the classification rules.
2. If the preferred model or provider is unavailable, fall back to the next best empirical option that satisfies the hard constraints.
3. If the task is still ambiguous after filtering, choose `planner`.

## Decision Rule
If the request is simple and low-risk, route to `quick`.
If it is a clear implementation task, route to `implementer`.
If it is high-risk, architectural, or security-sensitive, route to `architect`.
If it needs clarification or multi-step planning, route to `planner`.

## Implementation
This policy is implemented in `scripts/global/task-router-policy.json` and `scripts/global/task-router.js`.

```json
{
  "version": "1.0.0",
  "defaultLane": "free",
  "lanes": {
    "free": {
      "backend": "auto",
      "recommendedModel": "Auto",
      "keywords": [
        "search", "grep", "find", "explain", "read", "docs",
        "rename", "boilerplate", "simple", "small", "single-file"
      ]
    },
    "fleet": {
      "backend": "openclaw",
      "recommendedModel": "qwen2.5-7b",
      "keywords": [
        "multi-file", "tests", "refactor", "implement", "migration",
        "pattern", "transform", "integration", "batch", "known"
      ]
    },
    "premium": {
      "backend": "sonnet",
      "recommendedModel": "Claude Sonnet 4.6",
      "keywords": [
        "architecture", "ambiguous", "complex", "hard", "risk",
        "security", "performance", "concurrency", "incident", "design"
      ]
    }
  },
  "escalation": {
    "premiumOn": ["failed", "stuck", "unclear", "cross-system", "trade-off"],
    "fleetOn": ["medium", "repeated", "workflow", "generate", "coverage"]
  }
}
```

This policy routes tasks based on keyword matching, with escalation triggers for complex or stuck tasks.