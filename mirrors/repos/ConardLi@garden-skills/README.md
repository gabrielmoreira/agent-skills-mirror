<div align="center">

# Garden Skills

**A curated collection of production-ready [Agent Skills](https://support.claude.com/en/articles/12512176-what-are-skills) for Claude Code, Cursor, Codex, and other AI coding agents.**

<a id="skills-gallery"></a>

<table>
<tr>
<td width="50%" valign="top">
<a href="#web-video-presentation"><img src="./dist/imgs/web-video-presentation-skill.png" alt="Web Video Presentation Skill" width="100%"></a>
<br/><a href="#web-video-presentation"><strong>web-video-presentation</strong></a>
<br/><sub>Web video / presentation</sub>
</td>
<td width="50%" valign="top">
<a href="#web-design-engineer"><img src="./dist/imgs/web-design-skill.png" alt="Web Design Skill" width="100%"></a>
<br/><a href="#web-design-engineer"><strong>web-design-engineer</strong></a>
<br/><sub>Design / frontend</sub>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<a href="#gpt-image-2"><img src="./dist/imgs/gpt-image-2-skill.png" alt="GPT Image 2 Skill" width="100%"></a>
<br/><a href="#gpt-image-2"><strong>gpt-image-2</strong></a>
<br/><sub>Image generation / prompting</sub>
</td>
<td width="50%" valign="top">
<a href="#kb-retriever"><img src="./dist/imgs/kb-retriever-skill.png" alt="KB Retriever Skill" width="100%"></a>
<br/><a href="#kb-retriever"><strong>kb-retriever</strong></a>
<br/><sub>Local knowledge retrieval</sub>
</td>
</tr>
</table>

[![License: MIT](https://img.shields.io/github/license/ConardLi/garden-skills?style=flat-square&color=blue)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ConardLi/garden-skills?style=flat-square)](https://github.com/ConardLi/garden-skills/stargazers)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](#contributing)
[![Skills count](https://img.shields.io/badge/skills-4-orange?style=flat-square)](#skills-gallery)
[![Spec](https://img.shields.io/badge/spec-SKILL.md-black?style=flat-square)](https://agentskills.io)

[English](./README.md) · [中文文档](./README.zh-CN.md)

</div>

---

## Table of contents

| Install | Use | Contribute |
|---|---|---|
| [Install](#install)<br>[`skills` CLI (npx)](#option-a--skills-cli-npx)<br>[Claude Code plugin marketplace](#option-b--claude-code-plugin-marketplace)<br>[Pinned `.zip` from Releases](#option-c--pinned-zip-from-releases)<br>[Manual copy](#option-d--manual-copy-into-your-project)<br>[Git submodule](#option-e--git-submodule) | [Compatibility](#compatibility)<br>[What is a Skill?](#what-is-a-skill) | [Contributing](#contributing)<br>[Acknowledgments](#acknowledgments)<br>[License](#license) |

---

### [`web-video-presentation`](./skills/web-video-presentation)

![Web Video Presentation Skill](./dist/imgs/web-video-presentation-skill.png)

**Category:** Web Video / Presentation Engineering  
**Best for:** turning scripts, articles, lessons, product demos, and talks into click-driven 16:9 web presentations that can be screen-recorded as cinematic videos.

`web-video-presentation` builds record-ready Vite + React + TypeScript presentations that behave like video production surfaces. The workflow turns raw articles into narration scripts, maps script beats to full-screen scenes, pauses at required checkpoints, and can optionally synthesize narration audio after the visual outline is approved.

Highlights:

- Fixed 1920×1080 stage that scales to the viewport for stable screen recording
- Click / keyboard driven `(chapter, step)` cursor, with one narration beat per visual step
- Hard collaboration checkpoints for script, theme, outline, implementation mode, and optional audio
- Hidden hover-only progress controls so the stage stays clean while recording
- Theme-token architecture with multiple visual languages, from `paper-press` to `terminal-green`
- Scaffolded Vite + React + TypeScript project with reusable stage primitives and recording guidance

Links: [README](./skills/web-video-presentation/README.md) · [SKILL.md](./skills/web-video-presentation/SKILL.md) · <!-- DOWNLOAD:web-video-presentation:start -->[Download v1.1.3 .zip](https://github.com/ConardLi/garden-skills/releases/download/web-video-presentation-v1.1.3/web-video-presentation-1.1.3.zip)<!-- DOWNLOAD:web-video-presentation:end -->

---

### [`web-design-engineer`](./skills/web-design-engineer)

![Web Design Skill](./dist/imgs/web-design-skill.png)

**Category:** Design / Frontend  
**Best for:** web pages, landing pages, dashboards, interactive prototypes, HTML slide decks, animations, UI mockups, data visualizations, and design-system explorations.

`web-design-engineer` turns AI-generated web artifacts from merely functional into polished, deliberate, and visually memorable front-end work. It treats the agent as a design engineer: first understanding product context, then declaring a design system, showing an early v0, building the full experience, and verifying the result.

Highlights:

- Defines a six-step design workflow: requirements → context → design system → v0 → full build → verification
- Pushes beyond generic AI UI patterns with an anti-cliché blocklist and stronger visual judgment
- Covers HTML / CSS / JavaScript / React prototypes, with guidance for responsive layout, motion, and interaction polish
- Includes practical implementation rules for inline React + Babel, CSS tokens, `oklch()` color work, container queries, and reduced-motion handling
- Ships an advanced patterns reference for device frames, slide engines, animation timelines, dashboards, and other reusable web artifacts

Links: [README](./skills/web-design-engineer/README.md) · [SKILL.md](./skills/web-design-engineer/SKILL.md) · [Website](./website/web-design-website) · [Demo](./demo/web-design-demo) · <!-- DOWNLOAD:web-design-engineer:start -->[Download v1.0.0 .zip](https://github.com/ConardLi/garden-skills/releases/download/web-design-engineer-v1.0.0/web-design-engineer-1.0.0.zip)<!-- DOWNLOAD:web-design-engineer:end -->

---

### [`gpt-image-2`](./skills/gpt-image-2)

![GPT Image 2 Skill](./dist/imgs/gpt-image-2-skill.png)

**Category:** Image Generation / Prompt Engineering  
**Best for:** posters, UI mockups, product visuals, infographics, academic figures, technical diagrams, comics, avatars, storyboards, branding boards, and image-editing workflows.

`gpt-image-2` is a focused image-generation skill for GPT Image 2 and OpenAI-compatible image APIs. It is designed to work across different agent environments: fully local Garden generation, host-native image-tool delegation, or prompt-only advisor mode when no image tool is available.

Highlights:

- Supports three runtime modes: **Mode A Garden local**, **Mode B host-native delegation**, and **Mode C advisor-only prompt writing**
- Starts every task with mode detection so the skill does not silently choose the wrong execution path
- Provides 18 visual categories and 80+ structured prompt templates under `references/`
- Covers both image generation and image editing through dedicated workflows and scripts
- Saves prompts and generated images under `garden-gpt-image-2/` in Garden mode for reuse, review, and versioning

Links: [README](./skills/gpt-image-2/README.md) · [SKILL.md](./skills/gpt-image-2/SKILL.md) · [Website](./website/gpt-image2-website) · <!-- DOWNLOAD:gpt-image-2:start -->[Download v1.0.3 .zip](https://github.com/ConardLi/garden-skills/releases/download/gpt-image-2-v1.0.3/gpt-image-2-1.0.3.zip)<!-- DOWNLOAD:gpt-image-2:end -->

---

### [`kb-retriever`](./skills/kb-retriever)

![Kb Retriever Skill](./dist/imgs/kb-retriever-skill.png)

**Category:** Retrieval / Local Knowledge Base  
**Best for:** answering questions from a local `knowledge/` directory, searching structured documentation, and extracting evidence from Markdown, text, PDF, and Excel files without flooding the agent context.

`kb-retriever` is a local knowledge-base retriever built around careful, progressive search. Instead of loading whole files, it navigates hierarchical index files, narrows the candidate set, processes complex file types correctly, and answers with sources.

Highlights:

- Uses layered `data_structure.md` files to navigate the knowledge base before searching content
- Enforces a **learn-before-process** rule for PDF and Excel files, using the included reference docs before extraction or analysis
- Combines precise keyword search, local windowed reads, synonyms, and iterative refinement
- Bounds retrieval to at most 5 search rounds so exploration stays controlled
- Includes workflows for `grep`, `pdftotext`, `pdfplumber`, and `pandas`, with source-aware answer formatting

Links: [README](./skills/kb-retriever/README.md) · [SKILL.md](./skills/kb-retriever/SKILL.md) · <!-- DOWNLOAD:kb-retriever:start -->[Download v1.0.0 .zip](https://github.com/ConardLi/garden-skills/releases/download/kb-retriever-v1.0.0/kb-retriever-1.0.0.zip)<!-- DOWNLOAD:kb-retriever:end -->

---

## Install

There are five supported install paths. Pick the one that fits your stack:

| # | Method | Best for | Pinned version? |
|---|---|---|---|
| A | [`skills` CLI (`npx skills add`)](#option-a--skills-cli-npx) | Any agent, one-line install, pick & choose skills | ✅ via tag URL |
| B | [Claude Code plugin marketplace](#option-b--claude-code-plugin-marketplace) | Claude Code users who want to subscribe to plugin packs | ✅ via marketplace version |
| C | [Pinned `.zip` from GitHub Releases](#option-c--pinned-zip-from-releases) | CI / air-gapped envs / reproducible installs | ✅ ✅ (immutable) |
| D | [Manual copy after `git clone`](#option-d--manual-copy-into-your-project) | Local hacking on the skill itself | ❌ (tracks `main`) |
| E | [Git submodule](#option-e--git-submodule) | Vendored into a larger project, want upstream updates | ✅ via submodule SHA |

> Each skill section above also has a **`Download v<version> .zip`** link in
> its "Links:" row that points at the current pinned release artifact. Those
> URLs are auto-rewritten by [`scripts/release/update-readme.mjs`](./scripts/release/update-readme.mjs)
> on every release, so they always advertise the latest immutable version.

### Option A · `skills` CLI (npx)

The fastest agent-agnostic path. Uses the standard [`npx skills` CLI](https://www.npmjs.com/package/skills),
which auto-detects your agent (Claude Code, Cursor, Codex, etc.) and drops the
skill into the right directory.

```bash
# Install all four skills (latest)
npx skills add ConardLi/garden-skills

# Install just one skill (latest)
npx skills add ConardLi/garden-skills -s web-design-engineer

# Install globally (~/.skills) instead of per-project (./.skills)
npx skills add ConardLi/garden-skills -s gpt-image-2 --global

# Target a specific agent
npx skills add ConardLi/garden-skills -s kb-retriever -a claude-code
```

> **Defaults to the latest commit on `main`.** That's what you want 95% of the
> time — the CLI tracks each skill's most recent published `SKILL.md` straight
> from the source tree.

**Want a pinned version? (CI / production)** Use a tag-scoped `tree/` URL —
this points at the exact commit a release was cut from:

```bash
# Pin one skill to a specific release
npx skills add ConardLi/garden-skills/tree/web-design-engineer-v1.0.0/skills/web-design-engineer
```

For each skill, the current pinned `.zip` URL is also shown inline in its
"Links:" row above (the `Download v<version> .zip` link).

Useful sub-commands:

```bash
npx skills list                 # what's installed
npx skills find web-design      # search registries
npx skills update               # bump everything
npx skills remove kb-retriever  # uninstall
```

### Option B · Claude Code plugin marketplace

If you use [Claude Code](https://docs.anthropic.com/en/docs/claude-code), you
can subscribe to the marketplace and install plugin packs that bundle one or
more skills together:

```bash
/plugin marketplace add ConardLi/garden-skills
/plugin install presentation-skills@garden-skills
/plugin install web-design-skills@garden-skills
/plugin install knowledge-base-skills@garden-skills
/plugin install image-generation-skills@garden-skills
```

Plugin packs are declared in [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json):

| Plugin pack | Skills included |
|---|---|
| `presentation-skills` | `web-video-presentation` |
| `web-design-skills` | `web-design-engineer` |
| `knowledge-base-skills` | `kb-retriever` |
| `image-generation-skills` | `gpt-image-2` |

### Option C · Pinned `.zip` from Releases

Every formal release publishes an immutable `.zip` (with a SHA-256 checksum) to
[GitHub Releases](https://github.com/ConardLi/garden-skills/releases). Pin to
this from CI, Dockerfiles, or air-gapped installers when you need the exact
bytes to never move under you.

```bash
# Replace <skill> and <version> with the version you want.
SKILL=web-design-engineer
VERSION=1.0.0

curl -fsSL -o "${SKILL}.zip" \
  "https://github.com/ConardLi/garden-skills/releases/download/${SKILL}-v${VERSION}/${SKILL}-${VERSION}.zip"

# Verify the checksum (highly recommended for unattended installs)
curl -fsSL -o "${SKILL}.zip.sha256" \
  "https://github.com/ConardLi/garden-skills/releases/download/${SKILL}-v${VERSION}/${SKILL}-${VERSION}.zip.sha256"
shasum -a 256 -c "${SKILL}.zip.sha256"

# Drop the folder into the agent's skills directory
unzip -q "${SKILL}.zip" -d .claude/skills/   # or .agents/skills/, .codex/skills/, ...
```

A floating "always-latest" URL is also available — useful for one-off installs:

```bash
https://github.com/ConardLi/garden-skills/releases/latest/download/<skill>-<version>.zip
```

> **Pinned URLs for every skill are listed inline in this README** — see the
> "Download" line under each skill's "Links" entry above. They are kept in sync
> automatically by the release pipeline.

### Option D · Manual copy into your project

Clone the repo and copy the skill folder you want — handy if you want to fork
or hack on the skill itself.

```bash
git clone https://github.com/ConardLi/garden-skills.git
cp -r garden-skills/skills/web-design-engineer  your-project/.claude/skills/
# Cursor / generic agent:
cp -r garden-skills/skills/web-design-engineer  your-project/.agents/skills/
```

The agent discovers the skill the next time it scans the workspace.

### Option E · Git submodule

For vendoring into a larger project where you want to track upstream updates:

```bash
git submodule add https://github.com/ConardLi/garden-skills.git vendor/garden-skills
ln -s ../../vendor/garden-skills/skills/web-design-engineer .claude/skills/web-design-engineer
```

Pin to a release tag for reproducibility:

```bash
cd vendor/garden-skills
git checkout web-design-engineer-v1.0.0
```

---

## Compatibility

| Agent / Runtime | Skill location | Status |
|---|---|---|
| **Claude Code** | `.claude/skills/<name>/` or via plugin marketplace | ✅ Tested |
| **Claude.ai** (web) | Settings → Capabilities → Skills | ✅ Tested |
| **Cursor** | `.agents/skills/<name>/` | ✅ Tested |
| **Codex CLI** | `.codex/skills/<name>/` | ✅ Tested |
| **Gemini CLI** | extension manifest | ✅ Tested |
| **OpenCode** | `.opencode/skills/<name>/` | ✅ Tested |

> The `SKILL.md` format is portable by design — if your agent supports skills, copy the folder into the directory it scans, and it should work. PRs welcome to extend this matrix.

---

## What is a Skill?

A **Skill** is a self-contained folder the agent can load on-demand. It's
just a `SKILL.md` (YAML frontmatter + instructions), optionally accompanied
by reference docs, scripts, and assets:

```text
<skill-name>/
├── SKILL.md      ← required: when to use it + how to do it
├── README.md     ← human-facing docs
├── references/   ← optional: extended docs the agent loads on demand
├── scripts/      ← optional: deterministic executable helpers
└── assets/       ← optional: templates, fonts, icons
```

The agent decides whether to activate the skill from the `description` line
in the frontmatter — so the description is the contract between you and the
agent. For the full spec, see [agentskills.io](https://agentskills.io) and
[Anthropic's reference repository](https://github.com/anthropics/skills).

---

## Contributing

Bug reports, new skills, and tooling improvements are all welcome.

The maintainer-facing docs — repository layout, release process, version
rules, CI workflow, troubleshooting — live in
[**`CONTRIBUTING.md`**](./CONTRIBUTING.md) ([中文](./CONTRIBUTING.zh-CN.md)).
Read that first if you want to add a skill or cut a release.

Quick orientation:

```bash
git clone https://github.com/ConardLi/garden-skills.git
cd garden-skills
npm run list      # show all skills + manifest status
npm run validate  # the same check CI runs on every PR
```

---

## Acknowledgments

This collection stands on the shoulders of:

- **[Anthropic](https://www.anthropic.com)** for the [Agent Skills spec](https://agentskills.io) and the [`anthropics/skills`](https://github.com/anthropics/skills) reference repository.
- **[Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs)** — the system prompt that inspired `web-design-engineer`. The original is preserved in [`dist/prompt/claude-design-system-prompt.md`](./dist/prompt/claude-design-system-prompt.md) for reference.
- The broader OSS skill community — see [`travisvn/awesome-claude-skills`](https://github.com/travisvn/awesome-claude-skills) and [`obra/superpowers`](https://github.com/obra/superpowers) for further discovery.

---

## License

[MIT](./LICENSE) © [ConardLi](https://github.com/ConardLi)
