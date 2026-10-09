---
description: >-
  Memory: a pluggable engine that stores your documents, conversations and
  learnings, recalls what matters before every turn, and answers questions
  with citations.
icon: brain
---

# Memory

OpenHuman's memory lets the agent remember you across chats: what you are working on, what you prefer, what is in your documents. Memory is a feature of the app, not a hidden database. You pick who stores it, see what is stored, and delete anything.

Open it from **Connections → Memory**. It has eight tabs (chips): **Engine**, **Ask**, **Explorer**, **Learnings**, **Conversations**, **Brain**, **Background** and **Settings**. The old `/brain` and `/settings/memory-engine` addresses redirect there.

## How the agent uses memory

Memory works around every turn, without the agent having to ask:

- **Before the model answers**, OpenHuman logs what you said and recalls a short, token-budgeted *memory pack* for the turn: relevant learnings (and beliefs the engine has built from them), documents from your brain, this agent's earlier conversations and, briefly, other agents'. The pack is added to the model request for that turn only. It is never written into the chat, so the conversation itself stays exactly as you had it.
- **After the answer**, the reply is logged together with a one-line result for each tool it used.
- **When a long chat is compacted**, OpenHuman recalls what the folded-away turns covered and adds it to the summary that replaces them.
- **In the background**, every few minutes, the engine builds beliefs from what was stored ("the user prefers short answers", "deploys happen on Fridays").

The answer's memory chips show which stored items the pack cited. To see what a turn would get, open **Ask → Pack preview**.

## Engines

An engine stores your memory and answers questions about it. There are two:

| Engine | What it is | Needs |
| --- | --- | --- |
| **TinyHumans** | Hosted CortexDB run by TinyHumans, reached through the TinyHumans backend | You are signed in, or the host supplies a TinyHumans API key (headless and library hosts) |
| **CortexDB** | Your own CortexDB, called directly (managed `api-v1.cortexdb.ai` or self-hosted) | A CortexDB API key (kept in the OS keychain), and an endpoint if not the managed one |

Either way your memory items are stored in CortexDB, not on your computer; OpenHuman keeps only bookkeeping (queued jobs, sync and import progress) locally. See [Where your memory is stored](privacy-and-security.md#where-your-memory-is-stored).

Pick one on the **Engine** tab. If you are signed out and have neither a CortexDB key nor a host-supplied TinyHumans API key, memory is **off**: the agent has no memory tool, nothing is stored, and the Memory page tells you why.

## What the engine does

- **Recall** answers a question in plain language and cites the stored items it relied on. The engine implements it.
- **Fetch** is raw search over stored items with metadata filters (folder, repo, thread, source, time window). Both launch engines support hybrid search only.
- **Store** takes three kinds of items: documents, conversations and learnings.

## What gets stored

### The brain: documents

The **Brain** tab holds documents every agent shares, filed by source type: `pdf`, `markdown`, `notion`, `github`, `web`, and one per other source (`gmail`, `docx`, …). It shows how many documents each source holds, lets you search them, add one (pasted text or a file on your computer), and forget a whole source.

Below that, **Synced sources** keep the brain up to date. A source is one of:

| Kind | Target | Filed under |
| --- | --- | --- |
| `folder` | A folder on your computer | `pdf`, `web` (HTML) or `markdown` by file type |
| `file` | A single file | as for a folder |
| `link` | A web page | `web` |
| `github` | A repository (`owner/repo`) | `github` |
| `rss` | A feed URL | `web` |

Sources sync when you press sync and on a schedule you set per source. An unchanged file that syncs again is not stored twice. Removing a source can also forget the items it produced.

### Conversations

Every turn is logged as it happens: your message before the model runs, the reply after. Each agent's turns are kept apart. Tool calls are stored by name and id with a one-line result, never their arguments. Turn logging can be switched off on the **Conversations** tab, which also lists each agent's stored turns.

### Learnings

A learning is one durable statement: a preference, fact, procedure or correction. The agent saves them with its `memory` tool (`learn` action), and you can add or delete them on the **Learnings** tab. Beliefs the engine built are listed there too, marked **Built belief**.

Everything is scrubbed for secrets and personal identifiers before it leaves your machine.

### Past conversations

Chats from before turn logging are not in memory until you sync them. The **Conversations** tab shows how many chats and turns are still unsynced; **Sync past conversations** uploads them (after you confirm) in the same form as new turns, without tool arguments. You can close the page while it runs, and syncing again later only sends what is new.

## Exploring what memory holds

The **Explorer** tab shows everything your memory holds, grouped by one property at a time: type, memory node, source, workspace, folder, file, language, repository, link, thread, agent, tool or tag. Each value shows how many items carry it. Click one to narrow to those items, then group again by another property; the breadcrumb at the top takes you back up. The items at each step are listed below, and **Open** shows one in full with all its details and a **Forget** button.

On a very large memory the counts may cover only the items scanned so far; the tab says so when that happens.

## Each agent's own memory

Memory is organised the way a team works:

- **Shared by every agent:** learnings and the brain.
- **Each agent's own:** its conversations. The pack an agent gets leads with its own history; other agents' turns appear only briefly.
- **Teams and tenants:** an agent team gets a memory of its own, below its own root (`team:<id>`), apart from everyone else's.

By default an agent's memory id is its definition id. In `config.toml`, `[memory.agents.<id>]` can give a definition another memory id (`agent_id`), another root (`root`), or switch its per-turn pack off (`recall = false`). A host that runs OpenHuman agents as part of something larger (an AI company, a multi-agent product) binds each agent to its own memory: `[memory] agent_id` and `root` on that agent's config, or `AgentSpec::memory(MemoryBinding::new("employee-7").root("team:acme"))` through the [embedding library](../developing/embedding.md).

## The agent's memory tool

The agent has one tool, `memory`, with four actions: `recall`, `fetch`, `learn` and `forget`. OpenHuman's own [MCP server](../developing/mcp-server.md) exposes the same abilities to other apps as `memory.recall`, `memory.fetch`, `memory.list`, `memory.learn` and `memory.forget`.

## Settings and background work

The **Settings** tab sets the pack's shape: on or off, its size in tokens, how many learnings, documents and turns it holds, and how often beliefs are built. The **Background** tab lists queued belief builds and recent runs, with **Run now**. With the TinyHumans engine, beliefs are built on the service's own schedule.

## Importing your previous memory

If OpenHuman finds memory from the earlier (v1) version, the Memory page offers a one-time import. It uploads that data to the engine you selected, so it only starts after you explicitly consent. It resumes if interrupted.

## Removed

The memory tree, graph view, goals list, people and contacts, learning profile, `MEMORY.md` and `PROFILE.md`, the Obsidian vault, the local TinyCortex engine and the Supermemory, Mem0, Cognee and agentMemory engines are gone, as is engine migration. The compiled `context.md` brief is replaced by the per-turn memory pack. See the [spec](https://github.com/tinyhumansai/openhuman/blob/main/docs/specs/memory-v2.md).

## See also

- [Memory architecture](../developing/architecture/memory.md)
- [Pluggable engines](../developing/engines.md)
- [Privacy and security](privacy-and-security.md)
