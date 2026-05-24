# Web Video Presentation Skill

**A method-driven agent skill for turning scripts and articles into click-driven 16:9 web presentations that can be screen-recorded as cinematic videos.**

[中文文档](./README.zh-CN.md) · [Back to collection root](../../README.md)

![Web Video Presentation Skill](../../dist/imgs/web-video-presentation-skill.png)

---

## What Is This?

`web-video-presentation` helps an agent build a Vite + React + TypeScript presentation that behaves like a video production surface rather than a slide deck. Each click advances one narration beat, each step owns the whole 1920×1080 stage, and the progress UI stays hidden unless hovered so the output is clean for screen recording.

It is designed for:

- Turning a written article into a Bilibili / YouTube / video-channel narration script
- Turning an existing voiceover script into a cinematic web presentation
- Building product demos, tutorials, keynote-style explainers, and visual talks
- Creating “dynamic PPT, but not PPT” experiences with strong motion and pacing
- Optionally synthesizing narration audio after the visual outline is approved

The skill is primarily a **methodology and collaboration workflow**. The scaffold supplies reusable tokens, stage primitives, themes, and examples, but each project should still choose a visual language that fits the topic.

---

## Core Ideas

- **Fixed 16:9 stage** — content is authored in a stable 1920×1080 coordinate system and scaled to the viewport.
- **One global step cursor** — click or keyboard advances `(chapter, step)`, with the cursor persisted locally.
- **One step, one idea** — every beat gets a focused full-screen scene instead of accumulating slide bullets.
- **Script beats drive structure** — narration rhythm maps directly to visual steps.
- **Hidden chrome** — progress controls are hover-only, keeping recordings clean.
- **Motion first** — each scene needs a moving visual anchor; static paragraphs are treated as a smell.
- **Theme tokens** — visual decisions flow through semantic tokens so themes can change the whole feel.
- **Pluggable TTS** — provider-agnostic audio runner ships **two built-in providers** (MiniMax `mmx-cli` and OpenAI TTS via curl); swap to ElevenLabs / edge-tts / Azure / Google Cloud / macOS `say` / any self-hosted TTS by dropping a single shell file into `tts-providers/`.
- **Hard checkpoints** — the agent pauses after script/theme alignment, after outline approval, and before optional audio synthesis.

---

## Workflow

```text
Phase 1.1  Identify input
Phase 1.2  Article -> narration script
   |
Checkpoint A1  Script, theme, and rough asset plan
   |
Phase 1.3  Script + article -> outline.md
   |
Checkpoint A2  Outline approval + development mode
   |
Phase 2    Build the Vite / React / TS presentation
   |
Checkpoint B   Ask whether to synthesize audio
   |
Phase 3    Optional audio synthesis
Phase 4    Recording and post-production
```

The checkpoints are part of the skill contract: the agent should not silently rush from raw article to finished code. Theme choice influences motion design, and outline approval keeps chapter pacing from drifting.

---

## What It Ships

```text
skills/web-video-presentation/
├── SKILL.md
├── README.md / README.zh-CN.md
├── references/
│   ├── PRINCIPLES.md
│   ├── CHAPTER-CRAFT.md
│   ├── OUTLINE-FORMAT.md
│   ├── SCRIPT-STYLE.md
│   ├── THEMES.md
│   ├── AUDIO.md
│   └── RECORDING.md
├── scripts/
│   └── scaffold.sh
├── templates/
│   ├── index.html
│   ├── vite.config.ts
│   ├── scripts/
│   │   ├── extract-narrations.ts
│   │   ├── synthesize-audio.sh       # provider-agnostic runner
│   │   └── tts-providers/            # 1 file = 1 TTS backend
│   │       ├── README.md             # contract + ready-to-paste ElevenLabs / edge-tts / Azure / Google / say snippets
│   │       ├── minimax.sh            # default — uses mmx-cli
│   │       └── openai.sh             # built-in — uses OPENAI_API_KEY via curl
│   └── src/
└── themes/                    # 23 themes, each with its own signature
    ├── midnight-press/
    ├── warm-keynote/
    ├── newsroom/
    ├── bauhaus-bold/
    └── ...                     # full list in references/THEMES.md
```

---

## Quick Start

Copy the skill into the directory your agent scans, then ask it to turn a script or article into a web-video presentation.

To scaffold manually from inside a project:

```bash
bash skills/web-video-presentation/scripts/scaffold.sh ./presentation --theme=paper-press
```

List available themes:

```bash
bash skills/web-video-presentation/scripts/scaffold.sh --list-themes
```

The generated `presentation/` project is a normal Vite + React + TypeScript app. Run it like any other Vite project, then record the 16:9 stage with your screen recorder.

---

## Built-In Theme Directions

The skill ships **23 themes**, each with its own design DNA — not a simple color swap. Browse the two groups below by canvas tone, pick one that fits, or use any of them as a starting point for a derived theme.

### Dark (8 themes)

- `midnight-press` — cinematic editorial dark, warm espresso + hot orange
- `chalk-garden` — slate chalkboard, handwritten Patrick Hand + chalk-yellow
- `terminal-green` — 80s phosphor CRT, mono-only + scanlines
- `blueprint` — drafting board, deep navy + cyan + 60px grid
- `dark-botanical` — premium editorial dark, terracotta / blush / gold glow
- `neon-cyber` — cyberpunk future, cyan + magenta double-neon
- `bold-signal` — hero pitch deck, dark gradient + orange focal card
- `creative-voltage` — saturated electric blue + neon yellow halftone

### Light (15 themes)

- `paper-press` — editorial paper, warm cream + hot orange
- `warm-keynote` — modern SaaS keynote, glass slab + teal + warm grid
- `newsroom` — NYT broadsheet, newsprint cream + banner red
- `bauhaus-bold` — manifesto modernist, 0 radius + 4px thick frame
- `sunset-zine` — risograph zine, peach + magenta + dashed cut lines
- `monochrome-print` — refined Monocle / Wallpaper print restraint
- `vintage-editorial` — witty Fraunces + geometric overlay (circle / line / dot)
- `pastel-dream` — soft pastel + sage + right-edge pill ribbon
- `split-canvas` — dual-tone, peach left + lavender right
- `electric-studio` — corporate clarity, crisp white + electric-blue base bar
- `indigo-porcelain` — indigo IS the ink (not just an accent) + porcelain white
- `forest-ink` — forest green IS the ink + ivory (vintage National Geographic)
- `kraft-paper` — deep brown IS the ink + kraft beige + copper accent
- `dune` — charcoal + sand, near-zero accent (architecture brochure)
- `swiss-ikb` — extra-light 200 weight Helvetica + IKB + 1px hairline grid

See [THEMES.md](./references/THEMES.md) for the full token contract, signature for each theme, and how to derive new themes from existing ones (including Swiss yellow / green / orange variants).

---

## Reference Map

- [PRINCIPLES.md](./references/PRINCIPLES.md) — core rules for video-like web presentations
- [CHAPTER-CRAFT.md](./references/CHAPTER-CRAFT.md) — chapter implementation rules and visual checklist
- [OUTLINE-FORMAT.md](./references/OUTLINE-FORMAT.md) — required outline structure
- [SCRIPT-STYLE.md](./references/SCRIPT-STYLE.md) — article-to-narration rewrite guidance
- [PATTERNS.md](./references/PATTERNS.md) — optional visual primitive recipes
- [AUDIO.md](./references/AUDIO.md) — optional narration synthesis workflow (provider-agnostic)
- [tts-providers/README.md](./templates/scripts/tts-providers/README.md) — TTS provider contract + 2 built-ins (minimax / openai) + ready-to-paste snippets for ElevenLabs / edge-tts / Azure / Google Cloud / macOS say
- [RECORDING.md](./references/RECORDING.md) — screen recording and post-production notes

