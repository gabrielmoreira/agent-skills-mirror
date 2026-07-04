# CLAUDE.md

Guidance for AI agents (Claude Code, Cowork, and others) working in this repository. This file is the single source of truth for how the project is structured and maintained.

## Project Overview

**PM Skills** (`phuryn/pm-skills`) — a marketplace of **9 independent plugins** (68 skills, 42 commands) that bring structured product-management workflows to AI coding assistants. Built for Claude Code and Claude Cowork; the skills are also compatible with other agents (Gemini CLI, Cursor, Codex CLI).

Owner: Paweł Huryn — pawel@productcompass.pm — https://www.productcompass.pm

## Repo Structure

```
pm-skills/                           <- repo root
├── .claude-plugin/marketplace.json  <- root marketplace manifest (lists all 9 plugins)
├── .docs/images/                    <- images used by README (webp, gif)
├── .gitattributes
├── .gitignore
├── .github/workflows/               <- CI: tests.yml (every PR/push), tag-on-merge.yml (auto-release)
├── CHANGELOG.md                     <- release source of truth (new ## vX.Y.Z heading on main = release)
├── CLAUDE.md                        <- this file (agent guidance, single source of truth)
├── AGENTS.md                        <- pointer to CLAUDE.md (for non-Claude agents)
├── CONTRIBUTING.md                  <- contributor guidelines
├── README.md                        <- public documentation (GitHub)
├── LICENSE                          <- MIT
├── validate_plugins.py              <- plugin validator
├── tests/                           <- unit + docs-consistency tests (unittest)
└── pm-{name}/                       <- 9 plugin directories
    ├── .claude-plugin/plugin.json   <- per-plugin manifest
    ├── skills/{skill}/SKILL.md      <- one folder per skill
    ├── commands/{command}.md        <- one file per command
    └── README.md                    <- per-plugin documentation
```

### The 9 plugins

| Plugin | Focus |
|--------|-------|
| `pm-product-discovery` | Ideation, experiments, assumption testing, prioritization, interview synthesis |
| `pm-product-strategy` | Vision, strategy/lean/business-model canvas, SWOT, PESTLE, Ansoff, Porter, monetization |
| `pm-execution` | PRDs, OKRs, roadmaps, sprints, pre-mortems, stakeholder maps, user stories, red-teaming |
| `pm-market-research` | Personas, segmentation, sentiment analysis, competitive analysis, market sizing |
| `pm-data-analytics` | SQL query generation, cohort/retention analysis |
| `pm-go-to-market` | GTM strategy, growth loops, motions, beachhead segments, ICPs |
| `pm-marketing-growth` | Marketing ideas, value-prop statements, North Star metrics, naming, positioning |
| `pm-toolkit` | Resume review, NDA drafting, privacy policy, grammar/flow checking |
| `pm-ai-shipping` | AI Shipping Kit: document a vibe-coded app, map test coverage, audit security/performance against intended behavior, compile a shipping packet |

## Key Design Rules

- **Skills = nouns/concepts.** Frameworks and analytical knowledge Claude auto-loads when the topic matches (`lean-canvas`, `pre-mortem`, `market-sizing`).
- **Commands = verbs.** User-triggered workflows that chain one or more skills (`/write-prd`, `/discover`, `/plan-launch`).
- **No cross-plugin references.** Commands suggest follow-ups in natural language only ("Want me to design growth loops?"). Never hard-reference a command from another plugin — plugins install independently, so a hard reference can break.
- **Intra-plugin "Uses" references are fine** — skills and commands in the same plugin always ship together.
- Commands use a single `$ARGUMENTS` placeholder. Skills need no placeholders (they read context from the conversation).
- **Frontmatter required:** Skills need `name` + `description`; commands need `description` + `argument-hint`.
- A skill's `name` **must match its directory name**.
- Skills can be force-loaded with `/plugin-name:skill-name` or `/skill-name`.
- Keep frontmatter lean (always loaded); put detail in the SKILL.md body (loaded when triggered) — progressive disclosure.

## What's Visible Where

| Location | Visible in | Notes |
|----------|-----------|-------|
| `marketplace.json` → `description` | Cowork marketplace browser, Claude Code | One-liner for the whole marketplace |
| `plugin.json` → `description` | Cowork plugin list, Claude Code | Per-plugin summary; concise and functional |
| `SKILL.md` frontmatter → `description` | Cowork skill list, Claude auto-loading | Include trigger phrases so Claude loads the skill at the right time |
| Command frontmatter → `description` + `argument-hint` | Cowork and Claude Code (typing `/`) | Short and actionable |
| `README.md` (repo root) | GitHub only | Full docs; not loaded by Claude at runtime |

Descriptions in `plugin.json` and the repo `README.md` should stay aligned (identical text).

## Versioning & Releases

- **`CHANGELOG.md` is the source of truth.** The newest `## vX.Y.Z — YYYY-MM-DD` heading is the released version. Pushing a commit to `main` that adds a new heading makes CI (`.github/workflows/tag-on-merge.yml`) verify the version sync and test suite, tag `vX.Y.Z`, and publish a GitHub Release with that section as notes.
- **Keep every version in sync.** `marketplace.json`, all 9 `plugin.json` files, and the newest CHANGELOG heading always carry the same version (enforced by `tests/test_consistency.py`). There is no independent per-plugin versioning.
- Every user-facing change gets a CHANGELOG bullet under `## Unreleased`; contributors are credited inline (`#PR, thanks @handle`). Full procedure: CONTRIBUTING.md § Releases.
- Semver: breaking = major; new skills/commands or changed behavior = minor; fixes/docs = patch.

## Article Links in Skills (Further Reading)

- Mapped skills end with a `### Further Reading` section linking to relevant Product Compass articles.
- **Tone must stay neutral** — no promotional language, no CTAs, no "subscribe"/"check out". Just the article title and URL.
- Claude surfaces these links based on conversational relevance, not on every response.
- Posts whose title contains "Masterclass" or "Course" are video courses — tag them `(video course)`.

## Operational Procedures

### After any skill/command change
1. Run `python3 validate_plugins.py` and `python3 -m unittest discover -s tests` from the repo root.
2. If skills/commands were added or removed, update the counts in `README.md` (headline + per-plugin summary + plugin README section headers — the tests check all three).
3. If totals changed, update the count in the `marketplace.json` description.
4. Add a `CHANGELOG.md` bullet under `## Unreleased` for any user-facing change.
5. Bump versions across all manifests at release time (see Versioning & Releases).

### After a description change
- A `plugin.json` description changed → check whether `README.md` needs the same edit (they stay aligned).
- A `SKILL.md` description changed → no other sync needed (it's the single source for that skill).

## Validation

`validate_plugins.py` checks: `plugin.json` required fields / name match / semver / author / keywords; skill frontmatter and name-matches-directory; command frontmatter (`description` + `argument-hint`); README presence; and intra-plugin command→skill references.

`tests/` adds the consistency layer: README counts vs. disk, marketplace plugin list vs. directories, version sync across all manifests + CHANGELOG, CHANGELOG heading format, and `/plugin:command` references in plugin READMEs. Both run in CI on every PR and push to `main`, and gate releases.

```
python3 validate_plugins.py
python3 -m unittest discover -s tests
```

## What to Suggest After Completing Work

Offer relevant follow-ups:
- After structural changes: "Want me to run the validator?"
- After adding/removing skills or commands: "Should I update the counts in README.md and marketplace.json?"
- After editing descriptions: "Should I sync this to README.md / plugin.json?"
- After any repo change: "Want me to bump the version?"
