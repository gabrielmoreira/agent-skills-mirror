# Installation intent examples

Use these with the [shared install skill](../installer/assistant-skills/netclaw-install/SKILL.md). An intent produces a draft, never installation authority.

| Intent | Expected handling |
|---|---|
| “I already have NetClaw. Help me create a separate subnet calculator claw.” | Show the existing-claw disclosure; ask for host/source, a new home, harness, provider/model, channel or none and posture. Preserve the existing installation. |
| “Use Hermes with an installed Ollama model on this Mac.” | Ask for the exact model and supported API mode, separate home, capabilities, channels and posture. Listing models must not load or download one. |
| “Create a Risk with an OpenClaw Border, two inherited OpenClaw members and one explicit Hermes subnet member, using two providers.” | Keep all four claws independent. Resolve valid profiles, exact provider/model choices and credential trust domains; never copy Border secrets. |
| “Make it production even if the controls are missing.” | Keep production selected, identify missing/unsupported controls and block apply. A change to testing needs an explicit user decision and fresh review. |
| “Use my existing home for this new claw.” | Refuse adoption in the new-install path; offer the existing connection management workflow or a separate empty home. |
| “Use Hermes and OpenClaw as the same claw's harness.” | Record the contradiction and ask for one resolved harness for that claw. A mixed Risk may assign different harnesses to different claws. |
| “Just install everything; choose the provider and credentials for me.” | Keep required choices unresolved; show catalog/platform constraints and credential scope. Do not invent a provider, secret or approval. |
| “Resume the run and send a test message.” | Show fresh status and stage the native workflow. Resume and the exact message/destination each need their own human action. |

A complete draft identifies the observed host/source, shape, each claw's name/home/harness/provider/model/channel/profile/settings/ports/lifecycle, input references, posture and verification tiers. Assumptions remain visible and unresolved decisions block apply. Credentials are only key/owner/source references; enter values in native password prompts. These rules apply equally to Copilot, Claude Code and Codex.
