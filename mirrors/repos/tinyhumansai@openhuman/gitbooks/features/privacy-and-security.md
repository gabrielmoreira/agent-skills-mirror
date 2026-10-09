---
description: >-
  Where your memory is stored, what stays on your machine, what the backend
  brokers, and which of these layers are enforced by default.
icon: shield
---

# Privacy & Security

Your workspace files, settings and audio buffers stay on your machine. **Your memory does not**: memory items are stored in CortexDB, either the hosted CortexDB that TinyHumans runs for you or a CortexDB you point OpenHuman at. The OpenHuman backend brokers the rest of what has to leave the device (LLM calls, OAuth tokens, search proxying, hosted memory).

---

## Privacy by Design

**You choose where memory lives.** [Memory](memory.md) is stored by the engine you select: hosted TinyHumans (CortexDB behind the OpenHuman backend, requires sign-in) or your own CortexDB endpoint. With neither, memory is off and nothing is stored. Secrets and personal identifiers are scrubbed from every item before it is sent, tool-call arguments are never stored, and you can delete any item. See [Where your memory is stored](#where-your-memory-is-stored) below.

**Integration tokens are held by the backend, not on your laptop.** OAuth tokens are never written to disk in plaintext on your device. The OpenHuman backend brokers each integration request, the core never speaks any third-party API directly.

**OS-level credential storage.** Sensitive local secrets are rooted in your platform's secure keychain, macOS Keychain, Windows Credential Manager, Linux Secret Service. See [OS Keyring & Secret Storage](os-keyring-and-secret-storage.md).

**No training on your data.** Your conversations, your memories, and your personal information are never used to train AI models or improve systems.

**Optional** [**Local AI**](model-routing/local-ai.md)**.** If you want embeddings and summary-tree building to stay on your machine, run a local runtime such as Ollama, pull the models yourself, and add it as a provider. Learning and reflection passes, and chat if you choose, can be moved on-device the same way. OpenHuman does not install the runtime or download models.

---

## What stays on your machine

|                                 |                                                                 |
| ------------------------------- | --------------------------------------------------------------- |
| **Memory items**                | **Not local with hosted memory.** Stored in CortexDB by your selected engine (see below); a CortexDB you self-host on your own machine keeps it there. |
| **Memory bookkeeping**          | Local: the job queue and sync, backfill and import progress under `<workspace>/memory/`, the sources list in `config.toml`, a CortexDB key in the OS keychain. No memory content. |
| **Audio capture buffers**       | Local. Discarded after STT.                                     |
| **Local model state**           | Local.                                                          |

## Where your memory is stored

Memory items are your brain documents, logged conversation turns, learnings, and the facts and beliefs the engine builds from them. They are stored in CortexDB, never in a database on your machine. Which CortexDB depends on the engine:

| Engine | Path | Who can reach it |
| --- | --- | --- |
| **TinyHumans** (hosted) | The core sends each request over TLS to the TinyHumans backend's `/memory/*` routes, authenticated with your session or TinyHumans API key. The backend applies a per-user rate limit and billing, then forwards to a CortexDB proxy that places every scope under your own tenant root. | Only your account. The proxy derives the tenant from your credential, not from the request, so one user cannot read or write another's memory. TinyHumans operates the service. |
| **CortexDB** (direct) | The core calls CortexDB itself (`api-v1.cortexdb.ai`, or a self-hosted endpoint) with your own CortexDB API key, kept in the OS keychain. It does not go through the TinyHumans backend. | Whoever holds that key, and the operator of that endpoint. |

Inside either engine, memory is kept below a root derived from the active config identity (`org:<id>` for a TinyHumans account, `org:local-<digest>` for a local identity; on hosted memory this is the tenant root the backend pins, so paths read `org:<id>/ws:main/…`), so it can be listed, confined and erased as one tree. Learnings and the brain are shared by your agents; each agent's conversations are tagged with that agent.

We make no claim beyond TLS in transit and per-user tenant isolation for hosted memory. In particular, these docs do not promise end-to-end or client-side encryption: the hosted service can read what it stores, which is how it answers recall.

### Deleting memory

- **One item:** **Forget** in the Memory page's **Explorer**, on a memory chip under an answer, on the **Learnings** tab, or through the agent's `memory` tool (`forget`).
- **One source:** **Forget source** on the **Brain** tab, or tick **Also delete memory from this source** when disconnecting an integration.
- **Everything:** the `openhuman.memory_erase_all` RPC (`{"confirm": true}`) erases all memory the selected engine holds, for good. On hosted memory it calls the backend's `DELETE /memory`, which erases your whole tenant. On a direct CortexDB it erases your own `org:<id>` tree (and the earlier `user:<id>` tree while it is still read); memory written there before the per-user layout, which other accounts on a self-hosted CortexDB may share, is left for you to delete with your CortexDB account or endpoint. The **Settings** tab of the Memory page has an **Erase memory** card that calls the same RPC after you confirm.

Signing out does **not** delete stored memory, and neither does disconnecting an integration unless you tick that box.

## What the OpenHuman backend handles

|                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **LLM calls**                      | Proxied through the backend under one subscription, then forwarded to the underlying provider (Anthropic / OpenAI / Google / etc.) per the [model router](model-routing/README.md).                                                                                                                                                                                                                                                                                                                                                                                               |
| **Web search proxy**               | The native [web search tool](native-tools/web-search.md) can use the backend proxy, so you don't carry a search API key. Only **Exa** and **Gemini** have a managed route; Brave, Querit, Tavily, Seltz, Parallel, TinyFish and Gemini Deep Research are bring-your-own-key and go **directly** to that provider, and SearXNG goes to the instance you configured. With Tavily selected, the `tavily_extract` tool also sends extraction requests, including the URLs being extracted, directly to Tavily. |
| **Integration OAuth & tool proxy** | Token storage and rate-limited request brokering for [the connected integrations](integrations/README.md).                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **TTS streaming**                  | Hosted [text-to-speech](native-tools/voice.md) audio streams. Audio is generated and discarded - not retained.                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

---

## Permissions and access control

OpenHuman accesses an integration only after you complete its OAuth flow. Each connection has its own scope; you can revoke any of them at any time from the **Connections** page.

[Memory sources](memory.md) sync on a schedule while they exist, which is the point. Integration sync is bound by:

- The **OAuth scope** you granted that integration.
- A **per-provider sync interval** (e.g. Gmail every 15 min by default).
- A **daily budget** per connection that caps API usage.

If you revoke a connection, the next sync stops; items already stored in your memory engine remain until you forget them.

---

## Why memory is scrubbed and scoped

Memory only helps if it is safe to keep. Every item passes through secret and PII scrubbing before it is stored, conversations record tool-call names and ids but never arguments, and the agent only sees what a recall or fetch returns at the moment of a turn. You can inspect and delete items from **Connections → Memory** (see [Deleting memory](#deleting-memory)).

Scrubbing and scoped retrieval together become the privacy architecture.

## Security

**Encrypted in transit.** All communication between the application and the OpenHuman backend uses TLS, and so do hosted memory requests and direct calls to CortexDB's managed API. A self-hosted CortexDB endpoint is only as protected as the URL you configure.

**Key in keyring, ciphertext on disk.** For local secrets that must be persisted in app files, OpenHuman stores encrypted ciphertext on disk and keeps the master decryption key in the OS keyring. See [OS Keyring & Secret Storage](os-keyring-and-secret-storage.md).

**Sandboxed execution.** Shell and code the agent runs goes through a sandbox backend chosen per session: none, the OS jail (Landlock on Linux, Seatbelt on macOS), or a Docker container with no network, dropped capabilities and a read-only root filesystem by default. Skills are not separately sandboxed: the in-app JavaScript sandbox was removed, and a skill now runs as its own agent session subject to the same execution policy as any other turn.

**Working-folder-scoped tools.** The native [filesystem tools](native-tools/coder.md) act inside the agent's working folder. That confinement is part of the autonomy policy, which is **off by default**: until you set `[autonomy] enabled = true` it is not enforced. What is enforced either way is the hard floor, credential stores and system roots. See [Approval Gate](approval-gate.md).

**Short-lived tokens.** Authentication tokens between the app and the backend are time-limited.

---

## Trust & Risk Intelligence

OpenHuman includes an intelligence layer designed to help you reason about credibility, information quality, and potential risks across your connected sources.

**Scam and impersonation signals.** Behavioral patterns associated with scams, impersonation, or coordinated abuse can surface as warnings. Signals come from patterns, not from sharing individual message content.

**Contextual dynamic trust.** Trust is contextual, credibility in one domain does not automatically transfer to another. OpenHuman represents trust through aggregated artifacts and historical accuracy rather than static scores.

**Advisory, not enforcement.** Trust and risk outputs are advisory signals to inform your judgment. OpenHuman does not ban users, remove messages, or enforce moderation decisions.

---

## Shared environments

In team or community settings, privacy remains user-centric. Each user's connected sources are scoped to their account; admins do not get a backdoor into other users' memory.

Community-level intelligence is derived from aggregated and anonymized signals, never from direct access to individual message content.
