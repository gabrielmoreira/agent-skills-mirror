---
name: org-report
description: Generate an executive organization brief (leadership chain, direct reports, extended teams, and vendor partners) for a target person. Produces a Word + PDF report from a directory MCP source (WorkIQ is the reference implementation) and displays it in a Copilot canvas. Triggers on "generate org report for X", "build org brief for X", "make an org report for X", "org profile document for X".
---

# Org Report

Generate a polished executive organization brief for a target person. The report includes:

- Cover page with target, generation timestamp, FTE / vendor counts, byline, methodology, and disclosure
- Full management chain (up to the top)
- Team index (color-coded)
- Individual profiles: chain, target, each team's FTEs, individual contributors
- Appendix: all contractors and vendors grouped by team

Output is a Word `.docx`, a `.pdf` rendered from it, and a live Copilot canvas view.

## When to use

Trigger on any of:

- "Generate an org report for {Person}"
- "Build an org brief for {Person}"
- "Make an executive org report for {Person}"
- "Create an org profile document for {Person}"
- "Produce an organization brief for {Person}"

If the user asks for a report on themselves, use their profile as the target.

## Prerequisites (verify before starting)

1. **Directory MCP** — a Model Context Protocol server that exposes org-tree queries and person profiles. This plugin was built against Microsoft's [WorkIQ](https://aka.ms/workiq) MCP (`workiq-ask` tool); any MCP that answers equivalent queries about a corporate directory and communication signals will work with minor prompt adjustments in Phases 2–4.
2. **Python 3.11+** with `python-docx` and `docx2pdf` installed:
   ```powershell
   pip install python-docx docx2pdf
   ```
3. **Microsoft Word** (Windows/macOS) — required by `docx2pdf`. On Linux, swap in LibreOffice via a headless converter and pass `--pdf-out ''` to skip in-script PDF.
4. **Canvas extension** — the `org-directory` extension should be installed at
   `~/.copilot/extensions/org-directory/`. This plugin ships a copy in
   `extensions/org-directory/`; copy it once, then `extensions_reload`.
5. **Configuration (optional)** — cover byline, methodology, disclosure, base font, and vendor-detection rules can be customized via `config.json`. See § Configuration below. Without a config file the plugin uses tenant-neutral defaults.

If any prerequisite is missing, stop and tell the user what to install.

## Workflow

### Phase 1 — Confirm the target and reset state

Ask the user to confirm the target (UPN, email, or full name). Then create a
fresh state file at `~/.copilot/extensions/org-directory/artifacts/directory.json`:

```json
{ "orgChart": null, "profiles": {}, "updatedAt": null }
```

### Phase 2 — Resolve the org structure via the directory MCP

Use the MCP's directory query (e.g., WorkIQ `workiq-ask`, or `workiq-fetch` on `/users/...` where available) to build the tree:

1. **Target profile**: get `displayName`, `jobTitle`, `department`, `email`, `officeLocation`.
2. **Management chain**: walk up via `/users/{id}/manager` until you reach the top
   (e.g., the CEO). Save as `managementChain` (ordered top → target's manager).
3. **Direct reports**: recursively fetch `/users/{id}/directReports` for the target
   and every descendant. Attach as nested `reports: [...]`.

Persist to `directory.json`:

```json
{
  "orgChart": {
    "managementChain": [ { "displayName": "...", "jobTitle": "..." }, ... ],
    "target": { "displayName": "...", "jobTitle": "...", "email": "...", "department": "..." },
    "directReports": [
      { "displayName": "...", "jobTitle": "...", "email": "...",
        "reports": [ { "displayName": "...", ... } ] }
    ]
  },
  "profiles": {},
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

**Vendor detection:** in tenants that use the `First Last (Company Name)` display-name
convention (Microsoft is one example), contractors are identified by that parenthetical
plus an email prefix. Both signals are configurable — see `vendor_detection` in
`scripts/config.example.json`. Without configured rules the plugin treats all directory
entries as FTEs.

### Phase 3 — Enrich every person's profile

For every person in the tree (target + all descendants), call the directory MCP in
**parallel batches of 10–15** with this exact prompt:

```
For {Full Name} ({title, if known}, in {target}'s org), produce a concise
professional profile grounded in accessible communication signals (email,
meetings, chat, documents). Return ONLY this JSON in a ```json fence:

{
  "displayName": "{Full Name}",
  "jobTitle": "...",
  "department": "...",
  "email": "...",
  "summary": "2-3 sentence executive summary of their role and focus areas",
  "recentWork": ["3-6 recent projects or themes"],
  "topics": ["4-8 short tags describing what they work on"],
  "expertise": ["3-6 specific skills or domains"],
  "collaborators": ["6-8 people they work most closely with"],
  "signalDensity": "high | medium | low | none",
  "signalCounts": { "emails": 0, "meetings": 0, "chats": 0, "docs": 0 },
  "signalCountsWindow": "e.g. Jul-Aug 2026",
  "officeLocation": "..."
}
```

**About the new optional fields**:

- `signalDensity` — coarse indicator of how much verifiable signal grounded this
  profile. Use `high` when 30+ signals, `medium` for 10-30, `low` for 3-10,
  `none` for < 3. Renderer displays a colored dot next to the name.
- `signalCounts` — approximate counts per channel over the last 60 days. The
  renderer prints "Grounded in N emails · N meetings · N chats · N docs
  ({signalCountsWindow})" as an attribution footer. Skip channels with 0.
- `signalCountsWindow` — the human-readable date range the counts cover.

Rules:

- **Parallel batches only.** MCP directory calls can take 10–60 s per query. Fire
  10–15 calls in a single response, never sequential loops.
- **Retry MCP failures individually.** `No MCP client found` and timeouts happen —
  retry the specific failed call once.
- **Self-identify.** The `displayName` field lets you match responses back to
  people even in a mixed batch.
- **Merge into state.** Key by `displayName.lower().strip()`. Update `updatedAt`
  on each profile.
- **Empty responses.** If the MCP returns nothing usable (common for niche
  contractors), store:
  ```json
  "collaboratorsNote": "Collaborator network not surfaced in accessible signals"
  ```
- **Skip execs above the target.** External executives (CEO, presidents,
  large-org GMs) have collaborators legitimately outside the org and produce
  noisy profiles. Enrich the target and everyone below; leave upstream chain
  members as chain entries only.

### Phase 4 — (Optional) Validate collaborators

The first-pass collaborator list often includes people from unrelated meetings.
For any profile whose collaborators look off (mostly outside the org, unfamiliar
names), do a second pass with a narrower prompt:

```
Who are the 6-8 people {Name} ({title/company}, in {target}'s org) works most
closely with day-to-day? Return only this exact JSON in a ```json fence:
{"person": "{Name}", "collaborators": ["Name1", "Name2", ...]}
```

Same batch pattern (10–15 parallel). Merge overwrites the previous
`collaborators` list and clears any `collaboratorsNote`. Accept ~5% empties.

### Phase 4.2 — (Optional) Deep dive for the target and direct reports

For the target and each of their direct reports, run a second MCP pass with a
longer prompt to fill the `deepDive` object. This costs an extra ~10-25 MCP
calls per report but adds a dedicated "DEEP DIVE" section to the highest-signal
profiles.

```
For {Full Name} ({title}, in {target}'s org), summarize the leadership shape
of their work in the last 6 months, grounded strictly in accessible
communication signals. Return ONLY this JSON in a ```json fence:

{
  "displayName": "{Full Name}",
  "deepDive": {
    "strategicBets": ["3-5 concrete initiatives or bets they are driving"],
    "recentDecisions": ["3-5 explicit decisions or trade-offs they have made"],
    "crossTeamDependencies": ["3-5 dependencies on other teams or partners"]
  }
}
```

Same parallel-batch rules as Phase 3. Merge by `displayName.lower().strip()` —
`deepDive` overwrites any prior deepDive object. Skip anyone not in
`target + directReports` — depth beyond that is noisy and expensive.

### Phase 4.5 — (Optional) Fetch profile photos

If your application layer supplies a photo fetcher (e.g., the Microsoft Graph
fetcher at [OrgReports/scripts/fetch_photos.py](https://github.com/fabioc-aloha/OrgReports/blob/main/scripts/fetch_photos.py)),
run it now to populate the photo cache. The renderer picks photos up
automatically if they land at `<photos.directory>/<email>.jpg` (see
§ Configuration).

```powershell
python scripts/fetch_photos.py
```

Photos are optional — skip this phase and the report renders name-only cards.

### Phase 5 — Generate the DOCX + PDF

Run the export script. It reads `directory.json`, writes the DOCX and PDF, and
copies them into the canvas extension's artifacts folder. If a `config.json`
lives in the current working directory, cover copy and vendor rules load from
it; otherwise built-in tenant-neutral defaults apply.

```powershell
python ~/.copilot/installed-plugins/alex-mall/org-report/scripts/export_org.py

# Explicit config path:
python ~/.copilot/installed-plugins/alex-mall/org-report/scripts/export_org.py --config config.json
```

If that path does not resolve, the plugin was installed by a route other than
the Alex ACT Mall. Locate the installed `scripts/export_org.py` under
`~/.copilot/installed-plugins/` and use that path instead of guessing.

Optional flags:

- `--state <path>` — override the state file (default: canvas artifacts)
- `--docx-out <path>` — override the DOCX output path
- `--pdf-out <path>` — override the PDF output path (set to empty string to skip PDF)
- `--config <path>` — explicit config file path (default: `./config.json`, then user scope, then built-in defaults)

### Phase 6 — Refresh the canvas

```
extensions_reload
open_canvas({ canvasId: "org-directory", instanceId: "org-report-1" })
```

The canvas embeds the fresh PDF with a "Download PDF" button.

### Phase 7 — Report completion

Tell the user:

- Target name and how many FTE + vendor profiles were enriched
- Where the DOCX lives (path)
- That the canvas is open and refreshable

## Editing the cover copy

Cover byline, methodology paragraph, and disclosure paragraph are all
configurable via `config.json`. See § Configuration below. The default
disclosure covers three things every exec brief of this kind should say:

1. **Data-access limits** — information barriers, sensitivity labels, DLP policies
2. **AI accuracy** — summaries may contain errors, verify before acting
3. **Confidentiality** — organizational confidential personnel info, do not
   redistribute

## Configuration

`export_org.py` loads its cover copy, byline, base font, prose labels, vendor
rules, and photo settings from `config.json`. Discovery order:

1. `--config PATH` (explicit CLI flag)
2. `./config.json` in the current working directory
3. `~/.copilot/extensions/org-directory/config.json` (user-level default)
4. Built-in tenant-neutral defaults

Any subset of keys is valid; missing keys fall back to defaults. See
`scripts/config.example.json` for the full schema and a starting template.

### Available config sections

| Section | Purpose |
|---|---|
| `byline` | Cover byline (author + org). Empty → paragraphs skipped. |
| `cover_copy` | Methodology + disclosure paragraphs. |
| `typography` | Base font family. |
| `vendor_detection` | Email prefixes + display-name paren excludes. |
| `labels` | Prose strings the renderer uses (e.g., "no profile available"). |
| `photos` | Profile photo directory, lookup key, and rendered size. |
| `tenure` | Enable/disable the "N years <suffix>" line under contact. |
| `signal_density` | Colored dot per profile keyed by `signalDensity`. |
| `deep_dive` | Whether to render the "DEEP DIVE" section when `deepDive` is populated. |
| `attribution` | Whether to print the "Grounded in N emails · ..." footer. |
| `team_stats` | Extra TOTAL/DEPTH columns on the team index table. |
| `cross_team` | Cross-team collaboration table (top N pairs by shared collaborators). |

### Profile photos

Set `photos.directory` to a folder of image files named `<email>.jpg` (or
`.jpeg` / `.png`). The renderer looks up each entry's email (with `.upn`
fallback), then their normalized `displayName`. Missing photos are silently
skipped. The plugin does not fetch photos itself — pair it with an
application-layer fetcher (see OrgReports' `scripts/fetch_photos.py` for the
Microsoft Graph reference implementation).

For the Microsoft-tenant configuration used by the [OrgReports](https://github.com/fabioc-aloha/OrgReports)
application, see that repo's `config.json`.

## Known limits

- **MCP latency:** directory queries can take 10–60 s each; some questions run
  minutes. Always batch in parallel.
- **MCP flakiness:** occasional `No MCP client found` / timeouts. Retry the
  specific failed call once.
- **Empty profiles:** ~5–10% of contractors have no surfaceable signals. Mark
  with `collaboratorsNote` and move on.
- **Vendor name format:** relies on the `First Last (Company)` directory
  convention. Configure `vendor_detection.email_prefixes` and
  `display_name_paren_excludes` in `config.json` for your tenant.
- **Directory vs contacts:** `/users/{id}` is the corporate directory;
  `/me/contacts` is personal contacts. IDs are not interchangeable.
- **Binary content:** most directory MCPs don't yet expose files or profile
  photos as bytes — only structured metadata.
- **`docx2pdf` on Windows:** requires Microsoft Word. On macOS/Linux, substitute
  LibreOffice or a headless converter and pass `--pdf-out ''`.
