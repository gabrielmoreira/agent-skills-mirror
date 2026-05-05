---
name: foundry-models
description: |
  Discover, deploy, and manage models on Microsoft Foundry. Covers preset (quick) deployments, customized deployments (version/SKU/capacity/RAI policy), capacity discovery across regions, quota management, and PTU vs pay-as-you-go choice. Uses Azure MCP foundry tool, az cognitiveservices, and discovery flows.
  Triggers: "deploy model Foundry", "Foundry model deployment", "AZURE_AI_MODEL_DEPLOYMENT_NAME", "model capacity", "quota Foundry", "QuotaExceeded", "PTU", "GlobalStandard", "DataZoneStandard", "model SKU", "RAI policy", "content filter Foundry", "model catalog", "gpt-4o deploy", "gpt-5-mini deploy".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry Models — Deploy + Capacity + Quota

Language-agnostic guidance for landing the right model in the right region with the right SKU and quota — without inventing CLI flags from memory.

## Before You Build — Discovery (MANDATORY)

Foundry's model catalog, SKU mix, and per-region capacity move every week. Always confirm current syntax and availability **before** generating code or commands.

**1. Microsoft Docs MCP queries (run these first):**

- `Foundry model catalog`
- `Foundry model deployment SKU`
- `Foundry quota request increase`
- `Foundry capacity per region`
- `Foundry RAI policy content filter`
- `Azure OpenAI provisioned managed throughput PTU`

**2. Azure MCP `foundry` tool methods (call the tool with no args first to enumerate; the surface evolves):**

| Method | Use it for |
|---|---|
| `models_list` | Catalog of models supported by an account or region (filter by version, SKU) |
| `model_deployment_list` | Existing deployments on a Foundry account |
| `model_deployment_create` | Preset or customized deployment (set `name`, `model`, `version`, `sku`, `capacity`, optional `rai_policy_name`) |
| `model_deployment_get` / `model_deployment_delete` | Inspect or remove a deployment |
| `quota_get` / `quota_list` | Per-region, per-SKU, per-model quota allocations |
| `model_capacity_list` | Physical capacity available right now in a region for a model + SKU |
| `region_list` | Foundry-supported regions for an account |

**3. CLI fallbacks (when MCP not configured):**

- `az cognitiveservices account deployment --help`
- `az cognitiveservices account list-models --help`
- `az cognitiveservices usage list --help`
- `az rest` against `https://management.azure.com/.../modelCapacities?api-version=...` (look up the exact api-version via docs MCP — do not assume)

> If a method or flag isn't in the live tool/CLI output, do **not** invent it. Ask docs MCP, then ask the user.

---

## Mental Model

A **Foundry resource** (an `AIServices` Cognitive Services account) hosts one or more **model deployments**. Each deployment is the addressable thing your app code points at.

```
Foundry account (per region)
└── Model deployment ── this is what AZURE_AI_MODEL_DEPLOYMENT_NAME refers to
    ├── name         → your alias (e.g. "gpt-5-mini-prod")  ← what apps use
    ├── model        → catalog id (e.g. "gpt-5-mini")       ← what Microsoft ships
    ├── version      → catalog version (e.g. "2025-08-07")
    ├── sku          → capacity tier (see below)
    ├── capacity     → units of throughput
    └── rai policy   → content filter (default: Microsoft.DefaultV2)
```

**SKU types** (capacity tier — defer pricing/latency tradeoffs to docs MCP):

| SKU | Where capacity lives | When to pick |
|---|---|---|
| `Standard` | Pinned to a single region | Region-locked workload; no cross-region failover needed |
| `GlobalStandard` | Spread across global pool | Default cost-effective production |
| `DataZoneStandard` | Pinned to a data residency zone | Compliance / data residency |
| `ProvisionedManagedV2` (PTU) | Reserved units | Predictable high volume, no rate limits, monthly commit |

**Resource hierarchy — keep these straight:**

- **Subscription** — billing + quota boundary
- **Resource group** — deployment / lifecycle boundary
- **Foundry account** (`Microsoft.CognitiveServices/accounts`, kind `AIServices`) — region-pinned, hosts deployments
- **Foundry project** — logical scope inside an account; agents/threads/connections live here
- **Model deployment** — the addressable inference endpoint your code talks to

A deployment lives on the **account** (region-pinned), not on the project — but projects reference it. Quota is **subscription × region × model × SKU**, so two accounts in the same subscription + region share quota.

---

## Three Deployment Paths

| Path | When | What you control |
|---|---|---|
| **Preset (quick)** | Prototyping, "just give me gpt-4o" | Model name + (sometimes) region. Defaults to `GlobalStandard` + sensible capacity. |
| **Customize** | Production, compliance, PTU | Version, SKU, capacity, RAI policy, upgrade policy |
| **Capacity discovery** | Quota errors, multi-region, capacity-constrained models | None yet — read-only ranking that *feeds* one of the above |

Capacity discovery is **read-only**. After it returns the best region(s), the agent hands off to preset or customize to actually deploy.

---

## Preset Deployment Flow

For "deploy `<model>` and let me get on with it":

1. Resolve target Foundry account + region (env var, user prompt, or `az cognitiveservices account list`).
2. Confirm the target with the user — never deploy without showing **account / region / resource group**.
3. Call Azure MCP `model_deployment_create` with the minimum fields:
   - `name` (your alias — this becomes `AZURE_AI_MODEL_DEPLOYMENT_NAME`)
   - `model` (catalog id)
   - `version` (latest, unless user pins one)
   - `sku` = `GlobalStandard` (preset default)
   - `capacity` (sensible default; e.g. ~50% of available)
4. CLI fallback: `az cognitiveservices account deployment create --name <account> -g <rg> --deployment-name <alias> --model-name <model> --model-version <ver> --model-format OpenAI --sku-name GlobalStandard --sku-capacity <units>`.
5. Verify: `az cognitiveservices account deployment list -n <account> -g <rg> -o table`.
6. Echo the resolved env vars back to the user so they can paste them into `.env`:

   ```
   AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
   AZURE_AI_MODEL_DEPLOYMENT_NAME=<alias>     # NOT the catalog id
   ```

> If the user prefers the portal, generate a deep link via `az` (or ask docs MCP for the current portal URL pattern). Do not hand-craft portal URLs.

---

## Customize Deployment Flow

For production / compliance / PTU. Walk the user through each choice **dynamically** — never present a hardcoded SKU list.

1. **Pick model + version** — `models_list` filtered to the target region. Show only versions actually offered there.
2. **Pick SKU** — query the model entry's supported SKUs. For tradeoffs (cost, latency, residency, throughput guarantee) defer to docs MCP query "Azure OpenAI deployment types".
3. **Set capacity** — query the SKU's `min` / `max` / `step`. Validate the user's number against this range *before* calling create. Capacity can be scaled later via `update`.
4. **Set RAI policy** — default `Microsoft.DefaultV2`, or a custom policy. Full policy authoring lives in `foundry-governance`; cross-link rather than duplicating.
5. **Set version upgrade policy** — `OnceNewDefaultVersionAvailable` (default), `OnceCurrentVersionExpired`, or `NoAutoUpgrade`.
6. **Validate capacity in target region BEFORE create** — call `model_capacity_list` so you fail fast instead of waiting on a deployment error.
7. **Show full config summary, get confirmation, then create.**
8. Poll the deployment until `provisioningState` is `Succeeded`; surface endpoint + portal link.

For PTU: defer sizing math to docs MCP query "Foundry PTU calculator". Do not bake formulas into this skill — they change.

**Verify after deploy (any path):**

- `model_deployment_get` → confirm `provisioningState=Succeeded`, capacity matches, RAI policy matches.
- Smoke-test the endpoint with one inference call (the appropriate SDK / `curl` for the user's stack — defer syntax to the language-specific Foundry skill, e.g. `azure-ai-projects-py`).
- If a 429 fires immediately after deploy, capacity propagation can lag a minute or two — retry with backoff before assuming a real quota issue.

---

## Capacity Discovery Workflow

**Goal:** find the best region(s) where the desired `model + SKU + capacity` is actually available right now.

**Why this isn't a script:** Foundry-supported regions, capacity APIs, and SKU availability all churn. A baked-in script goes stale silently. Compose the query at runtime instead.

**Steps the agent should compose:**

1. **Enumerate candidate regions** — `region_list` (Azure MCP `foundry`) or `az account list-locations` filtered to Foundry-enabled regions per docs MCP.
2. **For each region, query physical capacity** — `model_capacity_list` filtered by `model_id` + `sku` (and optionally `model_version`). This returns *platform* availability — what the region can host.
3. **For each candidate region, also check subscription quota** — `quota_get` (or `az cognitiveservices usage list --location <region>` matching usage name pattern `OpenAI.<SKU>.<model-name>`). Subscription quota is *separate* from physical capacity; both must be > 0.
4. **Rank candidates** by: meets-capacity-target → has-subscription-quota → user's preferred regions (data residency / latency) → descending available capacity.
5. **Re-query at deployment time** — capacity is volatile. The region you pick at planning time may be drained 10 minutes later.

**Discovery prompt the LLM should compose at runtime** (substitute concrete values):

> "Use Azure MCP `foundry.model_capacity_list` for each of these regions: `[eastus, eastus2, westus3, swedencentral, ...]`. Filter `model_id=gpt-5-mini`, `sku=GlobalStandard`. Then call `foundry.quota_get` for each region with the same model + SKU. Return a table sorted by `min(physical_capacity_remaining, subscription_quota_remaining)` descending, marking rows where either value is 0."

**Output shape to give the user:**

| Region | Model capacity | Subscription quota | Meets target | Notes |
|---|---|---|---|---|
| `eastus2` | 120K | 80K | ✅ | Recommended |
| `swedencentral` | 100K | 100K | ✅ | Data zone EU |
| `westus3` | 90K | 0 | ❌ | Quota exhausted — request increase |

If one canonical helper script is genuinely required (e.g. for a CI job), point the user at the docs MCP "Foundry capacity discovery" example. **Do not bake a `.sh` into this skill.**

---

## Quota Management

Quotas are per-**subscription** × per-**region** × per-**model** × per-**SKU**. Bumping one combo does not bump others.

**Diagnose** with Azure MCP `quota_get` (preferred) or `az cognitiveservices usage list --location <region>` matching `OpenAI.<SKU>.<model-name>`. Compute `available = limit - currentValue` per row.

**Common runtime errors:**

- `QuotaExceeded` / `InsufficientQuota` — at the subscription cap for that combo
- `RateLimitExceeded` (HTTP 429) — runtime token throughput exceeds the deployment's allocated capacity
- `DeploymentLimitReached` — hit the per-resource deployment slot cap (typically 10–20)

**Free quota fast:** delete unused deployments — quota is released immediately. List candidates with `model_deployment_list`, then `model_deployment_delete` on anything stale.

**Scale an existing deployment:** capacity can be updated in place — no need to delete + recreate. Use Azure MCP `model_deployment_create` with the same `name` (it updates) or `az cognitiveservices account deployment update --sku-capacity <new-units>`. Updates are bounded by the SKU's `max` and your remaining quota.

**Request a quota increase:** docs MCP query "Foundry request quota increase Azure portal". The request requires a **business justification** (workload, traffic estimate, current vs requested TPM, target date). Approval is typically 3–5 business days, up to 10.

**PTU vs pay-as-you-go:** docs MCP queries "Foundry PTU provisioned managed throughput units guide" and "Azure OpenAI deployment types". Rule of thumb:

- Pick **PTU** when traffic is consistent enough that a monthly commit beats per-token billing **and** you need no-rate-limit guarantees / consistent latency.
- Stay on **GlobalStandard** for variable, bursty, or development workloads.
- Mixing is fine: PTU for the steady baseline + a `GlobalStandard` spillover deployment for bursts.

---

## RAI / Content Filter Policies

Every deployment carries a **Responsible AI policy**. Defaults to `Microsoft.DefaultV2` unless overridden.

- Custom policies tighten or loosen filters per category (Hate, Sexual, Violence, Self-harm, Jailbreak, Profanity).
- Set at deployment time via the `rai_policy_name` field; can be updated on an existing deployment.
- Policy applies to the **model deployment**, not to the agent that calls it. Per-agent overrides live in Foundry-side agent policies.

For policy authoring, allowlists, custom categories, transparency notes, and governance — see the **`foundry-governance`** skill. This skill intentionally keeps the RAI surface minimal.

---

## Common Errors

| Error | Likely cause | Fix |
|---|---|---|
| `QuotaExceeded` | Region/model/SKU at subscription cap | Capacity discovery → alternate region, OR request increase, OR delete unused deployments |
| `InsufficientCapacity` | No physical capacity in region (platform-side) | Capacity discovery to find another region; not solvable by quota request |
| `RateLimitExceeded` (429) at runtime | Tokens/min exceeds deployed capacity | Scale deployment capacity, OR distribute traffic across deployments, OR move to PTU |
| `ContentFilter` block at runtime | RAI policy blocked the request or response | Tune RAI policy (`foundry-governance`), or rephrase prompt, or add allowlist |
| `ModelNotFound` | Wrong model id, or region doesn't carry it | Verify with `models_list` in target region — model availability is region-specific |
| `DeploymentLimitReached` | Hit per-account deployment slot cap | Delete unused deployments; consolidate across resources |

---

## Critical Gotchas — Do Not Confuse

1. **Deployment name (alias) vs model name (catalog id).** `AZURE_AI_MODEL_DEPLOYMENT_NAME` is your **alias** (e.g. `gpt-5-mini-prod`), not the catalog id (`gpt-5-mini`). Apps reference the alias; the catalog id only appears at deployment-create time.
2. **`GlobalStandard` ≠ `DataZoneStandard` ≠ `Standard`.** Global = cheapest, region-agnostic routing. DataZone = pinned to a residency zone. Standard = pinned to one region. Picking the wrong one breaks compliance silently.
3. **Capacity is in *units*, not raw TPM.** 1 unit ≈ 1K TPM for some models, varies by model and SKU. Check the live `model_capacity_list` response — do not assume a conversion factor.
4. **Physical capacity ≠ subscription quota.** A region can have 500K capacity available platform-side while *your* subscription has zero quota there. Always check both.
5. **RAI policy is per deployment, not per agent.** To override per-agent, configure agent-side policies (see `foundry-governance`), not the deployment policy.
6. **`Standard` ≠ `GlobalStandard` for failover.** A `Standard` deployment in eastus is *not* automatically reachable from another region. Multi-region apps need either `GlobalStandard` or a deployment per region.
7. **Capacity is volatile.** Discovery results expire in minutes. Re-query right before `model_deployment_create` for high-demand models.
8. **Model availability is regional.** A model listed in the catalog may not be deployable in your chosen region. Always filter `models_list` by target region.

---

## Reference Links

- Microsoft Docs MCP — primary source of truth (always query before generating code)
- Azure MCP `foundry` tool — `models_list`, `model_deployment_create`, `model_capacity_list`, `quota_get`
- `az cognitiveservices` CLI — `account deployment`, `account list-models`, `usage list`
- Cross-skill: **`foundry-governance`** — RAI policy authoring, content filter customization
- Cross-skill: **`foundry-projects-resources`** — Foundry account + project provisioning, before any deployment
- Cross-skill: **`foundry-observability`** — runtime metrics, 429 / latency / content-filter monitoring
