# Creative Tim UI — Agent Skills

Reusable skills for AI coding agents. Compatible with Claude Code, Cursor, Cline, GitHub Copilot, Windsurf, and 40+ other agents via the [skills CLI](https://skills.sh).

## Install

```bash
npx skills add creativetimofficial/ui
```

Install globally (available in all your projects):

```bash
npx skills add creativetimofficial/ui -g
```

Install for a specific agent only:

```bash
npx skills add creativetimofficial/ui --agent claude-code
npx skills add creativetimofficial/ui --agent cursor
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [creative-tim-ui](./creative-tim-ui/) | Block library assistant — design philosophy, install commands, PRO API key, design rules |

## What the Skill Does

Once installed, your AI agent knows how to:

- Discover and install any of the 390+ blocks via `npx @creative-tim/ui@latest add <block>`
- Follow Creative Tim's design philosophy — minimalism, the 95% rule, deliberate restraint
- Apply the correct design rules (brand colors, typography scale, Tailwind v4 constraints)
- Set up PRO block access with `CREATIVE_TIM_UI_API_KEY`
- Compose shadcn/ui primitives correctly without reimplementing them

Browse blocks: https://www.creative-tim.com/ui
Skill page: https://skills.sh/creativetimofficial/ui/creative-tim-ui
