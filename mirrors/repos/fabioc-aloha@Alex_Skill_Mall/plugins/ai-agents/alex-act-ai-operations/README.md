# Alex ACT AI Operations

![Alex ACT AI Operations](assets/banner.svg)

[Core](https://github.com/fabioc-aloha/Alex_ACT_Core) | [Illustrator](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) | [Document Tools](https://github.com/fabioc-aloha/Alex_ACT_Document_Tools) | [Enterprise](https://github.com/fabioc-aloha/alex-act-enterprise)

Alex ACT AI Operations is an **optional** provider-routing plugin. It turns a
task into an evidence-backed model plan, explains provider tradeoffs, obtains
explicit approval, and then calls the selected provider tools.

It is installed separately. It is not part of Manager/Core brain health and is
never included in the default constellation installation. Provider API keys
are optional until a selected model requires one. Microsoft Foundry uses
Microsoft Entra ID through its hosted MCP and does not require an API key.

> **Version 0.2.0.** Installation remains optional and separate from the Alex
> ACT brain spine.

## What It Does

1. Decomposes a request into model-sized operations.
2. Captures modality, quality, privacy, region, license, latency, and budget
   constraints.
3. Queries current provider tools instead of relying on a static model list.
4. Removes infeasible candidates and reports unknown evidence honestly.
5. Produces an executable plan with a primary choice and fallbacks.
6. Displays provider, model, data boundary, and cost status for approval.
7. Guides provider-native login, the host environment, or approved secret
   storage only for the selected provider/model when access is required.
8. Executes approved calls, tracks asynchronous work, and records provenance.

## Providers

| Provider | Connection | Initial role |
| --- | --- | --- |
| Microsoft Foundry | First-party hosted MCP (preview) | Model discovery, metadata, and Foundry project tools |
| Hugging Face | First-party hosted MCP | Hub search, models, datasets, Spaces, jobs, sandboxes |
| ElevenLabs | Exact first-party local MCP 0.12.2 | Models, voices, speech, transcription, audio, music, agents |

Provider tools remain owned by their publishers. This plugin owns the workflow
that decides when and how to use them.

## What Ships

| Surface | Role |
| --- | --- |
| `model-router` | Advisory planning and explainable provider/model selection |
| `model-task-execution` | Consent-gated execution and evidence capture |
| `setup-ai-operations` | Provider authentication and local runtime setup |
| `/alex-act-ai-operations choose-model` | Create an executable plan without running it |
| `/alex-act-ai-operations execute-model-task` | Review, approve, and execute a plan |
| `/alex-act-ai-operations setup-ai-operations` | Configure provider access |

## Install

Install from the Alex ACT Mall:

```powershell
copilot plugin install alex-act-ai-operations@alex-mall
```

This is a separate action from installing Alex ACT Core or running Manager's
constellation setup. See `INSTALL.md` for provider configuration.

Onboarding ends when installation is verified. During onboarding, do not ask
for API keys, tokens, or other credentials, and do not initiate provider login.
Defer provider login and authentication until an approved execution plan
selects a provider and execution requires access.

## Consent Contract

Discovery and planning do not authorize execution. Before a paid or
data-transmitting call, the user must see and approve:

- Provider and model
- Operation and expected output
- Data sent outside the workspace
- Region, retention, and license evidence when available
- Estimated cost or an explicit statement that cost is unknown
- Maximum approved cost
- Approved fallbacks

Changing the provider, model, data boundary, or cost ceiling invalidates prior
approval and requires renewed consent.

## Limitations

- Provider catalogs and prices change. The router must query live evidence.
- Authentication remains provider-specific.
- Cross-provider benchmarks are not automatically comparable.
- A recommendation may be a set of Pareto choices rather than one winner.
- No paid provider canary runs as part of source validation.

## Governance

The source boundary is defined by Alex ACT Steward ADR-026. Releases use
semantic versioning and Mall origin delivery from immutable source tags.
