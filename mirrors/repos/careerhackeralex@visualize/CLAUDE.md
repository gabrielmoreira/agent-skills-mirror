# CLAUDE.md

This is the **Visualize** plugin — an open-source Claude Code plugin that turns any idea, data, or content into beautiful, self-contained HTML visualizations.

## Repo Structure

```
visualize/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest (name, version, author)
├── skills/
│   └── visualize/
│       ├── SKILL.md           # Main skill file (loaded by Claude Code)
│       └── references/        # Detailed specs (progressive disclosure Level 3)
│           ├── design-system.md
│           ├── skeleton.md
│           ├── types.md
│           ├── libraries.md
│           ├── menu.md
│           ├── css-techniques.md
│           ├── animations.md
│           └── eval.md
├── examples/                  # 15 example HTML files
├── eval/                      # Eval infrastructure
│   ├── EVAL.md               # 3-layer scoring specification
│   ├── LOOP.md               # Self-improvement loop methodology (v6)
│   ├── SKILL.md              # Evaluator skill
│   ├── loop-state.json       # Current round + score history
│   ├── stress-tests.md       # 40 test cases
│   ├── OPENCLAW-SETUP.md     # Prompt to set up automated cron job on OpenClaw
│   ├── pipeline/             # Automated eval pipeline (Node.js)
│   │   ├── run.js            # Orchestrator: node run.js --dir examples/
│   │   ├── format-detect.js  # Layer 1: auto-detect visualization format
│   │   ├── vision-eval.js    # Layer 3: vision eval helper (agent scores, not API)
│   │   ├── checks/           # Layer 2: 45 deterministic DOM checks
│   │   ├── calibration/      # Anchor screenshots for vision eval
│   │   └── LOOP-PROMPT.md    # Self-improvement loop agent prompt
│   ├── rounds/               # Per-round results
│   └── archive/              # Rounds 1-38 (historical)
├── docs/plans/               # Design & implementation docs
├── CLAUDE.md                  # This file
├── README.md                  # GitHub-facing docs
└── LICENSE                    # MIT
```

## Installation

```bash
# Via Claude Code plugin system
/plugin marketplace add careerhackeralex/visualize
/plugin install visualize@careerhackeralex

# Or clone directly
git clone https://github.com/careerhackeralex/visualize.git
```

## Key Decisions

- **Single-file HTML output** — inline CSS/JS, opens in any browser
- **Dark theme default** — class-based theming (NO @media prefers-color-scheme)
- **CSS-first animations** — no Motion.js, pure @keyframes + vanilla JS
- **`var` for all top-level JS** — prevents TDZ errors (root cause of many past bugs)
- **CDN libraries encouraged** — Chart.js, D3, Tailwind, Mermaid, Reveal.js, html-to-image
- **Inter font** via Google Fonts + Noto Sans for CJK/Arabic
- **Visual restraint** — no floating orbs, gradient text, scale transforms, glow effects

## Working on This Repo

When editing skills/visualize/SKILL.md:
- Keep it under **5,000 words** (Anthropic best practice for progressive disclosure)
- Move detailed specs to `skills/visualize/references/` and link from SKILL.md
- YAML frontmatter must have `name` and `description` with trigger phrases

When editing examples:
- Always start from the skeleton in `skills/visualize/references/skeleton.md`
- Test both dark and light themes
- Verify hamburger menu (theme toggle, PNG download, print)

When running eval:
- `eval/loop-state.json` tracks round number and score history
- Quality gates: SHIP ≥9.0, ACCEPTABLE ≥8.0, NEEDS WORK ≥7.0
- **Automated pipeline:** `cd eval/pipeline && node run.js --dir ../../examples/`
  - Runs Layer 1 (format detection) + Layer 2 (45 DOM checks) + captures screenshots
  - Layer 3 (visual/IA quality) is done by the AI agent reviewing the screenshots
- **Self-improvement loop:** pass `eval/pipeline/LOOP-PROMPT.md` to any Claude Code / OpenClaw agent
- **Automated scheduling:** see `eval/OPENCLAW-SETUP.md` for setting up a cron job on OpenClaw (every 3 hours)
- No API keys needed — the agent harness (Claude Code, OpenClaw) handles authentication
- See `eval/EVAL.md` for the 3-layer scoring specification

## Common Pitfalls

- Chart.js: must add `Chart.defaults.animation = false` before creating charts
- Theme toggle: charts must be destroyed and recreated (colors read at render time)
- `let`/`const` at top level → TDZ errors. Always use `var`.
- `@media (prefers-color-scheme)` fights with `.theme-dark` class → class-only theming
