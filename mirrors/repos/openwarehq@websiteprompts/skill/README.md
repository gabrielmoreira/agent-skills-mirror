<div align="center">

<h1>The skill that makes these</h1>

<b>Every prompt in this repo came out of this skill.</b><br>
Install it once, and your coding agent can build cinematic sites —<br>
and write new prompts — on its own.

</div>

<br>

## What it is

A [Claude Code skill](https://code.claude.com/docs/en/skills): a folder of
instructions your agent loads by itself when the work matches. Where a prompt
builds *one* site, the skill knows the whole craft — picking the mechanic, writing
the clip prompt, wiring the scroll, catching the mistakes that only show up once
the page is moving.

It works in any agent that reads a skills folder. It also works with no agent at
all: `SKILL.md` and `references/` are plain markdown, so you can read them, or
paste one into any chat.

<br>

## Install

**Claude Code — available in every project:**

```bash
git clone https://github.com/openwarehq/websiteprompts.git /tmp/wp
mkdir -p ~/.claude/skills
cp -R /tmp/wp/skill ~/.claude/skills/cinematic-sites
```

**Or just this project:**

```bash
mkdir -p .claude/skills && cp -R /tmp/wp/skill .claude/skills/cinematic-sites
```

Then ask for what you want — *"build me a cinematic hero for a whiskey brand"* —
and it loads on its own. No command to remember.

**Cursor, Copilot and others:** point your agent at `skill/SKILL.md`, or paste it
in. It is written to be read cold.

<br>

## What is in here

| | |
|---|---|
| **[SKILL.md](SKILL.md)** | The skill. Five steps, four non-negotiable rules, the mechanic decision tree, and a mistakes table. |
| **[references/prompt-bank.md](references/prompt-bank.md)** | The 5-part video prompt formula and 37 prompts that work. This is why the clips do not look AI-generated. |
| **[references/hero-recipes.md](references/hero-recipes.md)** | Full code per mechanic — crossfade loop player, scroll-scrub canvas, cursor seeker, liquid-glass nav. |
| **[references/generating-video.md](references/generating-video.md)** | Getting footage from any model, cost control, and the failure table. |
| **[references/writing-prompts.md](references/writing-prompts.md)** | How to distil a finished build back into one pasteable prompt — how the `prompts/` folder was made. |
| **[lib/](lib/)** | `scrubber.ts` (frame-strip scroll scrubbing) and `smooth.ts` (inertial scroll + reveals). Drop-in, no dependencies. |
| **[templates/base/](templates/base/)** | A complete React 18 + Vite 5 + Tailwind 3 + TypeScript scaffold. Copy, `npm install`, build. |
| **verify.mjs · capture-stops.mjs** | Headless screenshot harness. Proves the page actually *moves* — the one thing a code review cannot catch. |

<br>

## You do not need a video model

Every prompt in this repo ships with a hosted clip. The skill treats
`prompts/*.md` as a footage library — `curl` one into `public/` and build against
it for free. Generation is an upgrade, not a requirement.

<br>

## Requirements

**Node 18+.** That is the whole install.

Optional: `ffmpeg` for frame strips and poster stills; Chrome-for-Testing
(`npx puppeteer browsers install chrome`) plus `npm install` in this folder for the
verification harness; a video model of your choice for new footage.

<br>

<div align="center">
<sub>CC0-1.0, like the rest of the repo — use it commercially, no credit needed.</sub><br>
<sub><a href="../README.md">← back to the prompts</a></sub>
</div>
