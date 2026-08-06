# Org Report

![Org Report](https://raw.githubusercontent.com/fabioc-aloha/org-report/main/assets/banner.svg)

[Core](https://github.com/fabioc-aloha/Alex_ACT_Core) · [Manager](https://github.com/fabioc-aloha/Alex_ACT_Manager) · [Illustrator](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin) · [Document Tools](https://github.com/fabioc-aloha/Alex_ACT_Document_Tools) · [Enterprise](https://github.com/fabioc-aloha/alex-act-enterprise) · [Org Report](https://github.com/fabioc-aloha/org-report)

Org Report turns one directory walk into a sourced, shareable executive brief. Given a target person, it walks the reporting tree exposed by your directory MCP, synthesizes a profile for every individual from accessible communication signals, and produces a Word + PDF report displayed live in a Copilot canvas.

The reference implementation targets Microsoft's [WorkIQ](https://aka.ms/workiq) MCP. Any MCP that exposes equivalent directory and communication-signal queries works with minor prompt tweaks.

## Status

**Released as `v1.4.1`.** Source:
[`fabioc-aloha/org-report`](https://github.com/fabioc-aloha/org-report).
Install from the Alex ACT Mall as `org-report@alex-mall`.

## Install

```powershell
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
copilot plugin install org-report@alex-mall
```

The plugin installs under `~/.copilot/installed-plugins/alex-mall/org-report/`.

> Direct installs (`copilot plugin install fabioc-aloha/org-report`) are
> deprecated by the Copilot CLI and will stop working. Use the Mall path above.

Three steps remain after the plugin install: copy the canvas extension, install
the Python dependencies, and configure a directory MCP. Each is covered below.

## What You Get

| Output | Contents |
| --- | --- |
| Word document | Cover page (target, timestamp, FTE/vendor counts, byline, methodology, disclosure), management chain, color-coded team index, individual profiles for chain + target + team FTEs + individual contributors, full contractor/vendor appendix |
| PDF | Rendered from the DOCX for shareable, read-only distribution |
| Live canvas | Embedded PDF viewer with a download button, refreshed on every regen |

A GM-level org typically yields ~200 profiles, ~120 FTEs, and ~75 vendors in a
single self-contained PDF.

## What Ships

| Component | Responsibility |
| --- | --- |
| `skills/org-report/` | The workflow Copilot follows: confirm target, walk the tree, enrich, render, display |
| `extensions/org-directory/` | Canvas extension that serves the PDF viewer |
| `scripts/export_org.py` | DOCX + PDF renderer |
| `scripts/config.py` | Configuration loader with a four-level resolution order |
| `scripts/config.example.json` | Annotated configuration template |

## Prerequisites

| Requirement | Needed for |
| --- | --- |
| [GitHub Copilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli) with plugin and extension support | Everything |
| Python 3.11+ with `pip` | Rendering |
| A configured directory MCP, signed in with an authorized account | Directory and signal queries |
| Microsoft Word on Windows or macOS | PDF output through `docx2pdf` |

Confirm the local tools before installing:

```powershell
copilot --version
python --version
```

PDF conversion is not built in on Linux. Run the exporter with `--pdf-out ''`
to produce only the DOCX, or configure a separate LibreOffice-based step.

## Setup

### 1. Install the canvas extension

The report is served through a canvas extension. Copy the extension shipped
with the plugin into your user extension directory.

```powershell
# Windows
$src = "$env:USERPROFILE\.copilot\installed-plugins\alex-mall\org-report\extensions\org-directory"
$dst = "$env:USERPROFILE\.copilot\extensions\org-directory"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item "$src\*" $dst -Recurse -Force
New-Item -ItemType Directory -Force -Path "$dst\artifacts" | Out-Null
```

```bash
# macOS / Linux
mkdir -p ~/.copilot/extensions/org-directory/artifacts
cp -r ~/.copilot/installed-plugins/alex-mall/org-report/extensions/org-directory/* \
      ~/.copilot/extensions/org-directory/
```

Run `extensions_reload` inside Copilot CLI after copying. Repeat this step
after every plugin update so the installed canvas matches the plugin version.

```text
extensions_reload
```

### 2. Install Python dependencies

```powershell
python -m pip install -r "$env:USERPROFILE\.copilot\installed-plugins\alex-mall\org-report\scripts\requirements.txt"
```

```bash
python3 -m pip install -r ~/.copilot/installed-plugins/alex-mall/org-report/scripts/requirements.txt
```

### 3. Configure your directory MCP

Ensure a directory MCP is configured in your `.mcp.json` and sign in with an
account authorized to access the relevant organization data. The reference
implementation uses WorkIQ; another MCP must provide equivalent org-tree and
per-person communication-signal queries.

### 4. Verify

```powershell
copilot plugin list
```

Confirm `org-report` appears. Restart Copilot CLI, run `extensions_reload`,
then ask:

```text
Generate an org report for <person>
```

Copilot should load the `org-report` skill, confirm the target, and begin the
directory lookup. Do not continue if the target resolves to the wrong person.

## Configuration

The plugin ships with tenant-neutral defaults so it runs out of the box for any
organization. To customize the byline, cover copy, base font, prose labels,
vendor-detection rules, profile-photo settings, or enrichment display, drop a
`config.json` in one of these locations, checked in order:

1. Path passed via `python export_org.py --config PATH`
2. `./config.json` in the current working directory
3. `~/.copilot/extensions/org-directory/config.json`
4. Built-in generic defaults

Copy `scripts/config.example.json` as a starting template. Any subset of keys
is valid; missing keys inherit from the defaults.

### Feature sections

| Section | What it controls | Data source |
| --- | --- | --- |
| `byline` / `cover_copy` / `typography` | Cover page, methodology, disclosure, base font | config only |
| `vendor_detection` | Email prefixes and display-name paren excludes | config only |
| `labels` | Prose strings such as "no profile available" | config only |
| `photos` | Inline profile thumbnails | photo file per `<email>.jpg` |
| `tenure` | `N years <suffix>` under the contact line | `entry.employeeHireDate` |
| `signal_density` | Colored dot next to the display name | `profile.signalDensity` |
| `deep_dive` | Strategic bets, decisions, dependencies section | `profile.deepDive` |
| `attribution` | "Grounded in N emails · ..." footer | `profile.signalCounts`, `signalCountsWindow` |
| `team_stats` | Extra TOTAL and DEPTH columns on the team index | computed from state |
| `cross_team` | Cross-team collaboration table | computed from `profile.collaborators` |

Every enrichment feature is additive. Sections that reference missing data are
silently skipped, so the plugin works end-to-end even when only the baseline
directory prompt has run.

### Profile photos

Set `photos.directory` to a folder of `<email>.jpg` (or `.jpeg` / `.png`)
files. The renderer looks up each entry's email with a `displayName` fallback,
embeds a thumbnail inline before the name, and silently skips people without a
matching file.

The plugin does not fetch photos itself. Pair it with an application-layer
fetcher — see OrgReports'
[`scripts/fetch_photos.py`](https://github.com/fabioc-aloha/OrgReports/blob/main/scripts/fetch_photos.py)
for a Microsoft Graph reference implementation. For the Microsoft-tenant
configuration used by the
[OrgReports](https://github.com/fabioc-aloha/OrgReports) application of this
plugin, see that repo's `config.json`.

## Usage

In Copilot CLI, ask any of:

- "Generate an org report for Jane Doe"
- "Build an executive org brief for `jane.doe@contoso.com`"
- "Make an org profile document for Jane"

Copilot will:

1. Confirm the target and reset the state file.
2. Walk the directory MCP for the management chain and full report tree.
3. Enrich every person's profile in parallel batches of 10 to 15.
4. Optionally re-validate suspect collaborator networks.
5. Run `scripts/export_org.py` to produce the DOCX and PDF.
6. Reload the extension and open the canvas.

Expect the enrichment phase to take 10 to 30 minutes for a ~200-person org.
Directory MCP queries typically run 10 to 60 seconds per call, parallelized.

## Manual regeneration

If you edit `directory.json` by hand and want to re-render only:

```powershell
python "$env:USERPROFILE\.copilot\installed-plugins\alex-mall\org-report\scripts\export_org.py"
```

| Flag | Default | Purpose |
| --- | --- | --- |
| `--state PATH` | canvas artifacts `directory.json` | Override state file |
| `--docx-out PATH` | `<Target>-Org-Report.docx` next to the script | Override DOCX path |
| `--pdf-out PATH` | canvas artifacts `report.pdf` | Override PDF path; empty string skips PDF |
| `--config PATH` | `./config.json` → user scope → defaults | Explicit config file |
| `--photos-dir PATH` | `photos.directory` from config | Override the photo source folder |

The script prints `Config source: <path>` after each run so it is obvious which
config was applied.

## Repository layout

```text
org-report/
├── plugin.json                  # plugin manifest
├── assets/banner.svg            # repository banner
├── skills/org-report/SKILL.md   # workflow instructions Copilot follows
├── extensions/org-directory/    # canvas extension (copy to ~/.copilot/extensions/)
│   └── extension.mjs
├── scripts/
│   ├── export_org.py            # DOCX + PDF renderer
│   ├── config.py                # configuration loader
│   ├── config.example.json      # annotated template
│   └── requirements.txt         # python-docx, docx2pdf
├── CHANGELOG.md
├── README.md
└── LICENSE
```

## Disclosure and data handling

Every generated report includes a cover-page disclosure covering:

1. Data-access limits (information barriers, sensitivity labels, DLP policies)
2. AI accuracy caveat — verify before acting on specific claims
3. Confidentiality — organizational confidential personnel information; do not redistribute

Both the methodology and disclosure paragraphs are configurable via
`config.json > cover_copy`. Tailor them for your tenant, audience, and
classification.

The generated `directory.json` at `~/.copilot/extensions/org-directory/artifacts/`
contains personal names, emails, and signal-derived summaries. Treat it as
confidential and set a retention policy appropriate for your organization. The
plugin does not auto-expire it.

## Relationship to the Alex ACT constellation

Org Report is a standalone first-party plugin, not a constellation baseline
plugin. It ships and versions independently. The Alex ACT MSFT plugin installs
it as part of the Microsoft-internal stack, and
[Illustrator](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin)
pairs well with it for output styling, but neither is required. Any directory
MCP works.

## Would Revise If

Revisit by **2026-11-05** or sooner if the canvas extension still requires a
manual copy step after the Copilot CLI stabilizes an `extensions` component
path, if the Mall install path proves less reliable than direct install, or if
no directory MCP other than WorkIQ is exercised against the plugin.

## License

MIT. See [LICENSE](LICENSE).
