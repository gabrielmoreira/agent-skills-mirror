---
name: creative-tim-ui
description: Creative Tim UI block library assistant. Use when adding, generating, or modifying UI blocks/components/pages from creative-tim.com/ui. Covers design philosophy (minimalism, the 95% rule, research-first), block discovery, both CLI install methods, PRO API key setup, and Creative Tim design rules (orange brand, shadcn/ui base, Tailwind v4). Generates blocks that are deliberate and restrained, not maximal.
license: MIT
metadata:
  author: creative-tim
  version: "1.0.0"
---

# Creative Tim UI

A comprehensive block library built on top of [shadcn/ui](https://ui.shadcn.com), with 390+ production-ready blocks across 40+ categories. All blocks are React + Tailwind CSS, compatible with Next.js (App Router), Remix, and Vite.

Browse the full library: **https://www.creative-tim.com/ui**
AI-readable index: **https://www.creative-tim.com/ui/llms.txt**

## Install This Skill

```bash
# Install via skills CLI (recommended)
npx skills add creativetimofficial/ui

# Install globally (available in all projects)
npx skills add creativetimofficial/ui -g

# Or install to a specific agent only
npx skills add creativetimofficial/ui --agent claude-code
```

Skill page: **https://skills.sh/creativetimofficial/ui/creative-tim-ui**

## Design Philosophy

Across 300+ products and categories, Creative Tim has applied the same discipline: identify what developers actually need, build that exceptionally well, and cut everything else. That restraint is the core of the library.

When generating or modifying blocks, follow these principles:

**The 95% Rule** — build the common case exceptionally well. Don't add configuration, abstraction, or flexibility for problems that rarely exist. A developer should be able to read a block and immediately understand what it does.

**The "Light" Principle** — a block is finished when there is nothing left to remove, not when there is nothing left to add. Question every wrapper div, every prop, every animation, every icon. If the block works without it, it probably should.

**Research before rendering** — ask what the person looking at this screen is trying to *do*. A dashboard surfaces the number someone needs to act on. A form collects information with the least possible resistance. Design toward the purpose, not toward the surface.

**Build on foundations** — shadcn/ui primitives (`Card`, `Table`, `Button`, `Badge`) are well-designed and maintained. Compose them; don't reimplement them. The Creative Tim contribution is in the composition and the judgment, not in the primitives.

**Real use, not demo use** — the standard is: would a real team ship this in a production app? Avoid visual complexity that doesn't carry information. Communication beats decoration every time.

Full detail with code examples: `rules/brand-philosophy.md`

---

## When to Apply

Use this skill when:
- Installing or customising a Creative Tim UI block in a project
- Generating new blocks that should match Creative Tim's design system
- Reviewing generated UI code for brand/style compliance
- Setting up PRO API key access for premium blocks
- Onboarding a new project to use the Creative Tim UI library

## Block Categories

| Category | Slug | Description |
|----------|------|-------------|
| AI Agents | `ai-agents` | Chat interfaces, activity feeds, tool use, transcription |
| Pages | `pages` | Full-page agent management layouts |
| Account | `account` | Profile, settings, billing management |
| Authentication | `authentication` | Login, register, 2FA flows |
| Hero | `hero` | Landing page hero sections |
| Pricing | `pricing` | Pricing tables and billing plans |
| Charts | `charts` | Data visualisation |
| KPI | `kpi` | Metric cards and dashboards |
| Stats | `stats` | Statistics sections |
| Tables | `table` | Data tables with sorting/filtering |
| Ecommerce | `ecommerce` | Product listings, carts, checkout |
| Blog | `blog` | Article lists, post layouts |
| Testimonials | `testimonials` | Social proof sections |
| ... | | [Full list at /ui/llms.txt] |

## Installing Blocks

Two methods are fully supported — choose whichever fits your setup.

### Option 1 — Creative Tim CLI (recommended)

```bash
npx @creative-tim/ui@latest add <block-name>
```

Initialize a new project first (auto-detects Next.js / Vite / Remix / Astro):
```bash
npx @creative-tim/ui@latest init
```

Examples:
```bash
npx @creative-tim/ui@latest add hero-01
npx @creative-tim/ui@latest add ai-agent-activity-01
npx @creative-tim/ui@latest add agent-management-list-01
```

The package also ships named binaries (`creative-tim-ui`, `creative-tim`) — same commands:
```bash
npx creative-tim-ui add hero-01
npx creative-tim add hero-01
```

### Option 2 — shadcn CLI (full URL)

```bash
npx shadcn@latest add https://www.creative-tim.com/ui/r/<block-name>.json
```

Example:
```bash
npx shadcn@latest add https://www.creative-tim.com/ui/r/hero-01.json
npx shadcn@latest add https://www.creative-tim.com/ui/r/ai-agent-activity-01.json
```

Both methods copy the component source into your project and install all required shadcn/ui primitives (Button, Card, Badge, etc.) automatically.

## PRO Blocks (API Key)

Some blocks are marked **PRO** and require a Creative Tim API key. You can get a free key at **https://www.creative-tim.com/ui**.

### Setup

Add the key to your environment:
```bash
# .env.local
CREATIVE_TIM_UI_API_KEY=pk_live_xxxxxxxxxxxxxxxx
```

Pass the key when using either CLI:
```bash
# Creative Tim CLI
npx @creative-tim/ui@latest add pro-block-name --api-key $CREATIVE_TIM_UI_API_KEY

# shadcn CLI — set Authorization header via registry config
```

Or set it globally via the Creative Tim CLI config:
```bash
npx @creative-tim/ui@latest login --api-key pk_live_xxxxxxxxxxxxxxxx
```

After setting the key, PRO blocks install identically to free blocks.

## Design Rules

See individual rule files for full detail. Quick summary:

### Brand Colors
- **Primary accent: orange** (`orange-500` / `orange-600`) — Creative Tim's brand color
- Never use `violet`, `purple`, or `indigo` as accent colors — these signal AI-generated defaults
- Neutral surfaces: `slate`, `gray`, `zinc`
- Status: `emerald` (success), `amber` (warning), `red` (error), `blue` (info)

### Typography
- **`text-sm`** for all readable body content — labels, descriptions, table cells, list items
- `text-xs` only for: avatar initials, `font-mono` timestamps, badge pills (status/priority), sidebar group headers (uppercase + tracking-wider), tiny h-6/h-7 action buttons
- Never use `text-[10px]`, `text-[11px]`, or any arbitrary font-size values

### Tailwind v4 — No Arbitrary Values
- Use the numeric scale for spacing/sizing: `h-8`, `w-12`, `gap-3`, `p-4` — never `h-[32px]`
- Use standard fractions for widths: `max-w-sm`, `max-w-2xl`, `w-1/2` — never `max-w-[85%]`
- Responsive breakpoints only: `sm:`, `md:`, `lg:`, `xl:` — never `[@media(min-width:640px)]:`

### Component Patterns
- Prefer `Card > CardHeader + CardContent` for content grouping
- KPI / stat cards: `CardContent className="px-4 py-0"` (py-0, not default py-6)
- Use `ScrollArea` for any list that can overflow
- Sidebar navigation: 64 (`w-64`), border-r, `bg-muted/30`
- Avoid inline `style={{}}` — always use Tailwind classes

### Hydration Safety
- Never use `new Date()`, `Date.now()`, or `toLocaleTimeString()` in `useState` initializers
- Use static/hardcoded strings for SSR-safe initial state; switch to live values inside `useEffect` / `setInterval`

## Full Design Guide

For the complete rules with code examples: `AGENTS.md`

Individual rules:
```
rules/install-blocks.md     — CLI install walkthrough
rules/pro-api-key.md        — PRO key setup and auth
rules/design-brand.md       — Brand colors and identity
rules/tailwind-rules.md     — Tailwind v4 coding constraints
rules/component-patterns.md — Preferred component patterns
rules/hydration-safety.md   — SSR/CSR hydration rules
```

## Deploying This Skill

This skill lives in the repo at `.claude/skills/creative-tim-ui/`. Anyone can install it in their own Claude Code setup by running:

```bash
claude skill install github.com/creativetimofficial/ui .claude/skills/creative-tim-ui
```

Or by cloning and symlinking manually:
```bash
# Clone or copy the skills directory into your project
cp -r path/to/ui-repo/.claude/skills/creative-tim-ui .claude/skills/creative-tim-ui
```

Once installed the skill is available as `/creative-tim-ui` in any Claude Code session inside that project.
