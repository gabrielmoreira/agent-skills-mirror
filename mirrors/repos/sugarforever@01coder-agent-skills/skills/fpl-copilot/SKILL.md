---
name: fpl-copilot
version: 1.3.0
description: "Use when the user asks about Fantasy Premier League player stats, transfer advice, captain picks, fixture difficulty, gameweek strategy, or saved squad management."
---

# FPL Copilot

Analyze current FPL data, maintain saved squads, and produce self-contained reports. This skill specifies operations and completion criteria; choose suitable tools or commands from the actual environment.

## Workflow

### 1. Establish capabilities and storage

Inspect the available tools and locate this skill’s resources relative to its installed location. Identify capabilities for HTTP requests, JSON processing, SQLite 3 queries and writes, document persistence, and report delivery. On a shell-equipped host, infer suitable installed commands or scripting libraries; on other hosts, use exposed native tools. Tool names and executables are implementation choices.

Resolve storage once using the rule below, then reuse the resulting mapping for every reference and operation. Keep FPL data separate from the agent application's internal storage.

**Storage resolution (in precedence order):**

1. Use an explicit user-selected FPL location or a host-provided binding for the stable namespace `fpl-copilot`. If these disagree, ask which to use before writing.
2. Without an explicit selection or host binding, use the desktop root `~/.fplcopilot/`, expanded to an absolute path through the current user's home directory. Reuse this root even when the working directory or conversation changes.
3. On a host without a desktop home, request persistent storage for namespace `fpl-copilot` from its storage capability. Reopen its existing binding; if the host cannot provide a stable binding, ask the user to select a durable location before creating state. Conversation-local storage must be identified as such and selected explicitly.

Derive `fplcopilot.db`, `squads/`, `reports/`, and `player-history-sync.json` from that one root. If the host uses separate resource handles, persist their mapping under the same namespace through the host's storage configuration. Verify that mapping can be reopened before claiming cross-conversation persistence. Every mention of a “resolved” location in the references means this mapping, never a fresh location choice.

Inspect the selected location before initializing it. When competing existing mappings are discovered, ask which is authoritative; preserve existing data until the user selects a migration. Report the chosen root or handles and persistence scope when first establishing the mapping.

SQLite 3 is required for structured FPL storage; the `sqlite3` executable is one possible interface, not a dependency. Use an available SQLite interface: the CLI, a scripting-language library, or a native primitive/tool backed by SQLite (such as Expo SQLite). Discover which interface is available and use it consistently. Initialize a new database from `references/schema.sql`; execute reference SQL through the selected interface, preserving the schema and calculation semantics. If a required capability is missing, identify the blocked operation and complete only the supported parts; distinguish unsaved output and unavailable live data explicitly.

**Complete when:** the agent has identified working operations and persistent locations for the requested task, or reported a specific missing capability.

### 2. Establish data freshness

Before data analysis, read `references/sync.md` and the relevant mappings in `references/api.md`. Inspect successful-refresh metadata and refresh missing or stale datasets according to that contract. Fetch only the player histories required for the requested calculation; a full-player batch requires an explicit user request.

**Complete when:** required datasets have successful refresh timestamps and verified persisted records, or the answer can identify the age and limitations of a usable cached snapshot. An unsuccessful refresh is not evidence of fresh data.

### 3. Load squads and analyze

For “my squad/team,” check saved squads before asking the user to share again. Read `references/squad.md` for selection, persistence, and validation. Read `references/analysis.md` for metrics and decision frameworks; use the documented formulas with the available query/calculation capabilities. Resolve player IDs by stored names, checking ambiguity before selecting a player.

Save newly shared squads and confirmed changes using the squad reference. Keep hypothetical transfers in draft plans; recording a change locally does not submit it to the user's FPL account. After squad analysis, persist key takeaways in Notes.

**Complete when:** recommendations are backed by retrieved data and documented calculations, and every required squad write is verified or explicitly reported as unsaved.

### 4. Deliver the result

Use Markdown for quick lookups, short reasoning, deadlines, and small results. For the spatial or comparative outputs below, read `references/html-output.md` and adapt the matching template with actual data.

| Output | Template |
|--------|----------|
| Squad formation, bench, totals | `templates/squad-view.html` |
| Fixture difficulty matrix | `templates/fixture-matrix.html` |
| Transfer comparison | `templates/transfer-comparison.html` |
| Captain ranking with reasoning | `templates/captain-ranking.html` |
| Gameweek strategy | `templates/gameweek-report.html` |

Create one self-contained HTML report with inline CSS, JavaScript, and SVG; use vanilla HTML/CSS/JS and responsive layouts. Store it under the resolved `reports/` location as `{YYYY-MM-DD}-{slug}.html`. Provide the supported preview, attachment, share link, or accessible file path. Infer an appropriate viewing operation when available. When report creation or delivery is unavailable, provide the substantive result in chat and identify the missing report capability.

**Complete when:** the user has a substantive answer and an accessible report reference where supported, with data freshness and any limitations stated.

## Reference routing

Read each resource before performing its operation:

| Resource | Operation |
|----------|-----------|
| `references/sync.md` | Refresh, normalize, persist, and verify FPL datasets |
| `references/api.md` | Resolve endpoints and API-to-storage field mappings |
| `references/schema.sql` | Initialize storage or resolve tables, types, and keys |
| `references/analysis.md` | Compute metrics and recommendations |
| `references/squad.md` | Load, validate, create, or update squads |
| `references/html-output.md` | Generate and deliver reports |

## Data conventions

- Resolve names against `web_name`, then partial display names and full names; clarify ambiguous matches.
- Prices use 0.1m units: `130` means £13.0m. Display as `£X.Xm`; normalize by cost in millions for value comparisons.
- Positions are GKP, DEF, MID, FWD, mapped from API codes 1–4.
- Availability codes: `a` available, `d` doubtful, `i` injured, `s` suspended, `u` unavailable.
- FDR runs from 1 (very easy) to 5 (very hard).
