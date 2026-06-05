# Copilot Meta-Instructions — Depth-Priority Hierarchical AI-INSTRUCT V2

**Role of this file**: META — explains HOW the instruction system works. This file does NOT define project rules. It defines how to read and apply all other `AI-INSTRUCT.md` files in this project.

**Last Updated**: 2026-05-12

---

## The Depth-Priority Hierarchical Paradigm

This project uses **Hierarchical Layering by Directory Depth**. The deeper your current working directory, the more authoritative its `AI-INSTRUCT.md` becomes.

### The Law

When you are working in a directory:
- **That directory's `AI-INSTRUCT.md` is authoritative** for your current context
- Shallower `AI-INSTRUCT.md` files provide **background/context only**
- Each level is **self-contained** — no delegation upward
- Deeper always wins

### Hierarchy

```
.github/copilot-instructions.md              ← META: explains HOW layering works (this file)
    ↓
AI-INSTRUCT.md                               ← AUTHORITATIVE at workspace root
    ↓
ResumeServer/AI-INSTRUCT.md                  ← AUTHORITATIVE for the server application
    ↓
ResumeServer/{layer}/AI-INSTRUCT.md          ← AUTHORITATIVE when working in that layer
```

### How to Use

1. **When you start working**: check what directory you're in
2. **Find the deepest `AI-INSTRUCT.md`** in or above your current directory
3. **That file is authoritative** — follow it
4. **Parent files** provide architectural context only
5. **Do not mix contexts**: don't apply `server/` rules in `client/`, etc.

---

## Global Shared Instructions (`AI-INSTRUCT/`)

Cross-cutting rules that would otherwise be duplicated across many files live here as single sources of truth.

```
AI-INSTRUCT/
├── AI-CONVENTIONS.md    ← Naming, file organization (canonical — reference, don't repeat)
└── AI-MAINTENANCE.md    ← .old, .archive, .dev.md patterns (canonical — reference, don't repeat)
```

**Rule**: If a directory's `AI-INSTRUCT.md` needs to reference a global convention, it should **link** to `AI-INSTRUCT/` rather than restate it.

---

## AI Prompt Files (`.github/prompts/`)

AI-invocable slash commands live as `.prompt.md` files in `.github/prompts/`.

```
.github/prompts/
└── [task-name].prompt.md    ← Invoke with /task-name in Copilot Chat
```

---

## `.dev.md/` — Development Documentation Convention

Every directory that accumulates development notes uses a `.dev.md/` subdirectory.

### Rules

1. **`.dev.md/`** holds dev notes, session reports, status tracking, architecture reviews — anything that supports development but is NOT a primary deliverable
2. **`.dev.md/.old.mds/`** holds stale or superseded docs. Move outdated files here instead of deleting. **Copilot should ignore `.old.mds/` contents** unless explicitly asked
3. **Keep at directory root**: `AI-INSTRUCT.md`, `README.md`, source code, essential config

```
any-directory/
├── AI-INSTRUCT.md               ← Authoritative rules (KEEP at root)
├── README.md                    ← Primary docs (KEEP at root)
├── [source code / config]       ← KEEP at root
└── .dev.md/
    ├── [active dev notes]
    └── .old.mds/                ← Stale/superseded docs (IGNORE by default)
```

---

## Archiving Conventions

See [AI-INSTRUCT/AI-MAINTENANCE.md](../AI-INSTRUCT/AI-MAINTENANCE.md) for full rules.

| Pattern | Use |
|---------|-----|
| `filename.old.ext` | Single file no longer active but kept for reference |
| `filename.archive.ext` | Single file intentionally archived |
| `.archive/` subdirectory | Batch of archived files in a directory |
| `.dev.md/.old.mds/` | Stale development docs specifically |
| `.junk/` | Artifacts from previous projects being cleaned up |

---

## Code Comment Convention

- Comment on **why**, not what
- One line preferred; no rambling
- Do not add comments to code you did not touch in the current change
- Do not add header blocks, file-level docstrings, or function docstrings unless explicitly asked
- If a line implements a non-obvious architectural constraint, a comment **may** name the governing `AI-INSTRUCT.md`:

```js
// See server/AI-INSTRUCT.md — all DB access must go through the centralized database layer
const result = await db.query(SQL, params);
```

---

## Read-Only Source Projects

`Resume/` is a reference copy — do not modify files inside it. Copy content into the appropriate layer if needed.
