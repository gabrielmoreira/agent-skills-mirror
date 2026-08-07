[中文](README.md) · **English**

# shuohao-skills

A collection of skills for AI coding agents. **Runs in both Claude Code and codex.**

| Skill | What it does |
| --- | --- |
| [**novel-characters**](skills/novel-characters/README.en.md) | Turns a novel into a character bible: profiles, cartoon-design prompts, voice prompts, turnaround sheets |

## Install

```bash
git clone https://github.com/eternityspring/shuohao-skills.git
cd shuohao-skills
./scripts/install.sh
```

It detects whether you have Claude Code or codex installed and **symlinks** every skill into place — so `git pull` takes effect immediately, with no reinstall.

```bash
./scripts/install.sh novel-characters   # just one skill
./scripts/install.sh --codex            # only into codex
./scripts/install.sh --uninstall        # remove the symlinks
```

Prefer to do it by hand:

```bash
ln -s "$PWD/skills/novel-characters" ~/.claude/skills/novel-characters
ln -s "$PWD/skills/novel-characters" ~/.codex/skills/novel-characters
```

## Requirements

| | Required? | Notes |
| --- | --- | --- |
| **Node** | Yes | ≥ 18. The skill scripts use only the standard library — **no npm dependencies, nothing to install** |
| **Model quota** | Yes | Uses your current session's quota. **No API key needed** |
| **codex CLI** | Optional | Only for image generation (via its built-in `$imagegen`). Without it, image steps are skipped and everything else still runs |

> **Note on output language.** These skills are Chinese-first. `novel-characters` produces Chinese character profiles even for an English source novel, and its validator actively rejects English in those fields. See that skill's README for what it would take to change.

## Repository conventions

One directory per skill, **self-contained and copyable on its own**:

```
skills/<skill-name>/
├── SKILL.md          the workflow the agent reads (required)
├── README.md         the docs a human reads
├── scripts/
│   ├── <name>.mjs    deterministic helpers, zero dependencies
│   └── selftest.mjs  self-test, never calls a model (required)
├── references/       detailed instructions, loaded on demand
├── examples/         bundled samples that double as test fixtures
└── assets/           screenshots
```

Two hard requirements:

- Every skill must have a `SKILL.md`
- Every skill must have a `scripts/selftest.mjs` that **calls no model and costs no quota**, covering all deterministic logic

(`ci/selftest.yml` enforces both, but that workflow **is not enabled yet** — see below.)

Run every self-test locally:

```bash
for f in skills/*/scripts/selftest.mjs; do node "$f"; done
```

### Enabling CI (not enabled yet)

`ci/selftest.yml` is a ready-to-go GitHub Actions workflow: Ubuntu + macOS × Node 18/22/24, auto-discovering `skills/*/scripts/selftest.mjs` so adding a skill needs no change to it.

It is **not** under `.github/workflows/`, so it does not run — pushing to that path requires the `workflow` token scope. Which means: **everything here has only been tested on macOS with Node 24.** To enable:

```bash
gh auth refresh -h github.com -s workflow   # authorize once
mkdir -p .github/workflows
git mv ci/selftest.yml .github/workflows/
git commit -m "ci: enable selftest workflow" && git push
```

## License

[Apache 2.0](LICENSE)
