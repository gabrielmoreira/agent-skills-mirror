# EU Data Act Skill

A workflow-oriented skill for lawyers advising on the EU Data Act
(Regulation (EU) 2023/2854).

The skill produces lawyer-style Word output across five workflows —
classification, drafting, lookup, analysis, and audit — citing verbatim
from bundled source texts (Regulation 2023/2854 and EC FAQ v1.4) and
pointing to the Commission's model contractual terms (Recommendation,
19 November 2025) for direct consultation.

**Author:** Ryan Malek
**Feedback / questions:** [LinkedIn](https://www.linkedin.com/in/theryanmalek/)
**Distributed via:** Github, Counselcoder.com, Lawvable
**Project site:** [counselcoder.com](https://counselcoder.com)
**License:** AGPL-3.0 (see `LICENSE`)
**This is not legal advice.** See `LICENSE` for the full disclaimer.

---

## Who this is for

In-house counsel and external practitioners advising on EU Data Act
compliance — including industrial IoT, automotive, medical device,
SaaS, financial services, and cloud clients.

The skill assumes the user is a qualified lawyer. It does not explain
GDPR basics, what SaaS means, or other concepts a lawyer already knows.

## What it does

Five workflows, each with its own reference file:

| Mode      | Trigger                                                                         | Output (Word)                                              |
|-----------|---------------------------------------------------------------------------------|------------------------------------------------------------|
| classify  | "Is this offering a connected product / related service / DPS / overlap?"      | Classification memo with reasoning                         |
| draft     | "Draft me [pre-contract disclosure / Art. 25 clauses / refusal letter / etc.]" | Editable Word document, marked as starting point           |
| lookup    | "What does Article X say?" or "What is the deadline for Y?"                    | Verbatim quote + FAQ tie-ins + cross-refs                  |
| analyze   | "Can my client refuse on trade-secret grounds here?"                            | Structured legal analysis applying the framework           |
| audit     | "Compare this offering against the regulation"                                  | Gap-analysis checklist with severity flags                 |

The skill always:

- Asks for matter-specific facts (side advised, sector, member state) before drafting, rather than relying on global config.
- Surfaces a **sectoral overlay warning** when facts trigger automotive / medical / DORA / NIS2 / AI Act / CRA / other sectoral law.
- Cites **verbatim** from `assets/source/*` (no paraphrase from memory).
- Frames the **Commission FAQ as non-authoritative** in every output that relies on it.
- Appends a short **disclaimer** to every Word output.

## What it does not do

- **No legal advice.** The skill produces drafts the lawyer reviews.
- **No sectoral lex specialis.** Adjacent regimes (Reg. 2018/858, MDR, DORA, NIS2, AI Act, CRA, etc.) are flagged, not covered.
- **No member-state implementing law.** Skill points to Art. 37 competent authorities; national overlays must be checked independently.
- **No multilingual output.** English only. Use your own LLM for translation.
- **No automatic source updates.** The skill is a versioned static snapshot. Currency is checked through the verified-as-of stamp and new Lawvable releases.

## Install

### Claude Code (one command)

```bash
git clone https://github.com/counselos/eu-data-act ~/data-act-skill
cd ~/data-act-skill
bash install.sh
```

The script symlinks the folder to `~/.claude/skills/data-act-ryan-malek/` (auto-trigger by description) and adds `~/.claude/commands/data-act-ryan-malek.md` (explicit `/data-act-ryan-malek` slash command). Set `COPY=1` to install a fixed copy instead of symlinks.

Verify with `bash install.sh --check`. Uninstall with `bash install.sh --uninstall`.

### Other platforms

- **Claude Agent SDK** — same folder layout; register via the SDK's skill directory.
- **Codex CLI** — no native skill discovery; either `cd` into the folder when running `codex`, or open the prompt with `Use the skill at /path/to/data-act-ryan-malek/SKILL.md ...`.
- **No agent at all** — open templates and reference files directly. Python scripts run standalone.

### Dependencies

**Pandoc** (for Word export):

```bash
# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc
```

Word export uses pandoc with a reference template (`assets/styles/lawyer-reference.docx`) for proper Calibri / navy heading / page-number / table-grid styling. Without pandoc, `/data-act-ryan-malek` works for chat answers and lookups but the Word export step fails with a clear install message.

**Python** (3.10+) and these packages (only when scripts run):

```bash
pip install python-docx pypdf
```

The skill works offline. No network access is required for any end-user feature.

## How to use

Two invocation styles, both supported:

### Slash command (explicit)

```
/data-act-ryan-malek                                      ← shows the mode menu
/data-act-ryan-malek classify [offering description]      ← classify mode
/data-act-ryan-malek draft [what to draft]                ← draft mode
/data-act-ryan-malek lookup [Art. 25(2)(a)]               ← verbatim lookup
/data-act-ryan-malek analyze [scenario]                   ← apply law to facts
/data-act-ryan-malek audit [existing offering]            ← gap analysis
```

### Auto-trigger (implicit)

Just describe the task. The skill's description matches phrases like:

> "I need to classify my client's connected meter under the Data Act."
>
> "Draft me an Article 25 contract clause set."
>
> "What does Article 25(2)(g) say?"
>
> "Can my client refuse this access request on trade-secret grounds?"

The model invokes the skill automatically.

There is no setup. The skill is zero-config out of the box.

**The deliverable lives in chat by default.** After the chat answer, the skill offers to export to Word. Word files are saved to the lawyer's current working directory under `./Data Act outputs/{date}_{type}.docx` by default — never inside the skill folder. The lawyer can persist a different location with:

```
/data-act-ryan-malek save-here          # always save to current folder, don't ask
/data-act-ryan-malek save-to-desktop    # always save to ~/Desktop/Data Act outputs/
/data-act-ryan-malek ask-where-to-save  # ask each time (default)
```

## Update model

This skill is a **versioned static snapshot** of Regulation (EU) 2023/2854, the Commission Data Act FAQ, and related sources. It does not auto-update on your machine. Updates flow through new Lawvable releases.

**How you stay current:**

1. **A new release is published** when the European Commission ships a new FAQ version, when the Council adopts amendments, or when sectoral guidance changes affect the bundled materials. Each release updates `CHANGELOG.md` and the `_versions.json` verified-as-of date.
2. **Lawvable distributes new versions.** Update notifications surface in your Lawvable client. To get the latest, redownload through Lawvable. Your matter folders and Word outputs are untouched.
3. **Every deliverable stamps a "Sources verified [date]" line.** This appears at the end of every chat answer and Word memo, with the live EUR-Lex and EC FAQ URLs. If the stamped date looks old to you (more than a few months), redownload the skill before relying on the output. The verified-as-of stamp is the only signal you need; you do not have to monitor anything.

The static-snapshot model is deliberate: it keeps installation simple, never lets a background process touch your work, and puts the staleness signal directly into the work product where you can see it.

## Each downloader is the maintainer of their copy

The original creator does not maintain, update, monitor, or support copies of the Skill after distribution. Each downloader:

- Is solely responsible for the currency and accuracy of their copy.
- May freely modify, fork, and redistribute under the AGPL-3.0 license. Note that AGPL-3.0 is strong copyleft: derivative works (including those run as a network service) must be released under AGPL-3.0 with source available to users.
- Should remove the original creator's name from outputs they produce for clients (the Word footer is already clean of attribution).

This is by design — the skill is a starting point for your practice, not a service you are subscribing to.

## Folder layout

```
data-act/
├── SKILL.md                # Orchestrator (read first)
├── LICENSE                 # AGPL-3.0 + legal-advice disclaimer
├── README.md               # This file
├── CHANGELOG.md            # Version-only entries
├── install.sh              # One-command install for Claude Code
├── config.json             # output_dir preference (cwd / desktop / custom path)
├── commands/
│   └── data-act-ryan-malek.md   # Slash-command definition (/data-act-ryan-malek)
├── references/             # Knowledge layer, read on demand
├── assets/
│   ├── source/             # Verbatim regulation, FAQ; SCC pointer
│   ├── templates/          # Drafting starters (md → Word via pandoc)
│   ├── styles/             # lawyer-reference.docx for pandoc styling
│   ├── decision-trees/     # Walkable Q&A
│   └── examples/           # Worked examples
└── scripts/                # Python helpers
```

## Sources bundled

- Regulation (EU) 2023/2854 of 13 December 2023 (the Data Act) — verbatim text
- European Commission FAQ on the Data Act, v1.4, 22 January 2026 — verbatim text
- Commission "Data Act Explained" page — snapshot
- Commission Recommendation on standard contractual clauses / model contractual terms (annex), 19 November 2025 — **structured pointer only** (`assets/source/model-contractual-terms.md`); the canonical PDF is at the Commission's site and should be consulted directly for clause text

The first three are redistributed under their respective public-information regimes. The Recommendation is referenced but not redistributed.

## Versioning

Semantic versioning. Major version bump on substantive FAQ revisions, regulation amendments, or scope changes. Minor for added templates, examples, references. Patch for typos and clarifications.

This release: v1.0.0. See `CHANGELOG.md`.
