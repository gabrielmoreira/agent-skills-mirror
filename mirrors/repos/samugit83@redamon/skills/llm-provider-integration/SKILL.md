---
name: llm-provider-integration
description: >
  Adding an LLM provider to RedAmon: the credential boundary (keys must never
  reach scan containers), prefix-routed model ids, and the provider registry. A
  misrouted model id or a leaked key are the two failures this guards.
  Trigger: adding or editing an LLM provider; editing parse_model_provider in
  agentic/orchestrator_helpers/llm_setup.py, the webapp provider-type registry,
  the user_llm_providers model, or an LLM call site that passes an API key.
license: MIT
metadata:
  author: redamon
  version: "1.0.0"
  scope: [agentic, webapp]
  auto_invoke:
    - "Adding or integrating an LLM provider"
    - "Editing model-id routing or provider credential handling"
---

## When to Use

- Adding a new LLM provider (OpenAI-compatible or otherwise) the agent can use.

For a non-LLM external API *tool*, use `agentic-tool-integration`.

---

## Critical Rules

- **NEVER let a provider API key reach a scan container.** Keys live in exactly
  two places: Postgres `user_llm_providers` rows and, in transit, on the wire
  between webapp and agent. The recon / scan / MCP containers must **never** see
  them. Do not thread a provider key through recon settings or container env.
- **NEVER add a model id that is not prefix-routed.** Anything other than
  `claude-*` and bare OpenAI ids MUST carry a `provider/<model>` prefix, resolved by
  `parse_model_provider()` at
  [agentic/orchestrator_helpers/llm_setup.py:67](../../agentic/orchestrator_helpers/llm_setup.py#L67).
  An unprefixed id routes to the wrong provider silently.
- **ALWAYS register the provider in the webapp provider-type registry** and
  **propagate the key kwarg into every LLM call site.** A provider registered but
  not propagated builds a client with no credentials. The guide enumerates all
  11 integration points; touch each.

---

## The two invariants

| Invariant | Where | Failure if broken |
| --- | --- | --- |
| Keys only in Postgres + webapp<->agent transit | [webapp/prisma/schema.prisma](../../webapp/prisma/schema.prisma) `user_llm_providers`; agent settings fetch | key leaks into scan/MCP containers |
| Model id prefix routing | `parse_model_provider()` [llm_setup.py:67](../../agentic/orchestrator_helpers/llm_setup.py#L67) | model routes to the wrong provider |

## Commands

```bash
docker compose build agent && docker compose up -d agent   # agentic/ is baked
docker compose exec webapp npx prisma db push              # provider schema changes (NEVER prisma migrate)
```

## Resources

- [docs/readmes/coding_agent_prompts/PROVIDER_INTEGRATION_GUIDELINES.md](../../docs/readmes/coding_agent_prompts/PROVIDER_INTEGRATION_GUIDELINES.md) - the 11 integration points, decision tree, and model-id prefix table
- Related skill: `agentic-tool-integration`
