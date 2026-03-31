# Creative Tim UI — Design & Usage Guide

**Version 1.0.0**
Creative Tim
March 2026

> **Note:**
> This document is primarily for AI agents and LLMs generating, reviewing, or modifying
> UI code that uses the Creative Tim UI block library. Guidance is optimised for
> automation and consistency. Humans may also find it useful as a reference.

---

## Abstract

Creative Tim UI is a block library of 390+ React + Tailwind CSS components built on shadcn/ui.
This guide covers the design philosophy behind every block, installation patterns, brand identity
rules, Tailwind v4 constraints, and component conventions so AI-generated code stays consistent
with the library — not just visually, but in the decisions it makes.

---

## Table of Contents

0. [Design Philosophy](#0-design-philosophy)
1. [Installing Blocks](#1-installing-blocks)
2. [PRO Blocks & API Key](#2-pro-blocks--api-key)
3. [Brand Identity](#3-brand-identity)
4. [Typography Rules](#4-typography-rules)
5. [Tailwind v4 Constraints](#5-tailwind-v4-constraints)
6. [Component Patterns](#6-component-patterns)
7. [Hydration Safety](#7-hydration-safety)
8. [Block Authoring Guide](#8-block-authoring-guide)

---

## 0. Design Philosophy

Across 300+ products and categories, Creative Tim has applied the same discipline: identify what developers actually need, build that exceptionally well, and cut everything else.

That discipline — research first, build only what's necessary, remove rather than add — is the foundation of every block in this library.

**The five principles:**

### 0.1 The 95% Rule

Build the common case exceptionally well. Do not reach for complex solutions to simple problems. A developer dropping in a block should not unwrap three layers of abstraction to change a label.

### 0.2 The "Light" Principle

A block is done not when there's nothing left to add, but when there's nothing left to remove. No feature flags for things that can be changed in code. No helper components used only once. No animations on elements that don't need to communicate state. No extra wrappers that exist only to satisfy a mental model.

### 0.3 Research Before Rendering

The first question is always: what problem does this solve for the person looking at the screen? Not what looks good in isolation. A pricing table reduces friction in a purchase decision. A dashboard surfaces the one number a person needs to act on. If the purpose isn't clear, the block isn't clear.

### 0.4 Standing on Foundations

shadcn/ui's `Table`, `Card`, `Button`, `Badge`, `Dialog` are well-designed, accessible, and maintained. Do not rebuild them. Do not wrap them unnecessarily. The Creative Tim contribution is the **composition** — how primitives are assembled into something useful for real work.

### 0.5 Real Use, Not Demo Use

The standard is: would a real team ship this to solve a real problem? Avoid visual complexity that doesn't carry information. A status badge that turns red when something is wrong is communication. A gradient that doesn't indicate anything is decoration. Only the first belongs.

Full detail with code examples: `rules/brand-philosophy.md`

---

---

## 1. Installing Blocks

### 1.1 Creative Tim CLI

The preferred method. Installs the block and all shadcn/ui primitive dependencies automatically.

```bash
# Initialize project (auto-detects Next.js / Vite / Remix / Astro)
npx @creative-tim/ui@latest init

# Add a block
npx @creative-tim/ui@latest add <block-name>
```

**Package:** `@creative-tim/ui` (v0.4.x+)
**Binaries:** `creative-tim-ui`, `creative-tim` (aliases for the same CLI)

```bash
# All of these are equivalent:
npx @creative-tim/ui@latest add hero-01
npx creative-tim-ui add hero-01
npx creative-tim add hero-01
```

**Examples:**
```bash
npx @creative-tim/ui@latest add hero-01
npx @creative-tim/ui@latest add ai-agent-activity-01
npx @creative-tim/ui@latest add agent-management-list-01
npx @creative-tim/ui@latest add pricing-01
```

The CLI copies the component into `components/ui/` (or your configured components directory) and runs `npx shadcn@latest add` for each dependency.

### 1.2 shadcn CLI (Full URL)

Use this when you prefer the shadcn workflow or when integrating with shadcn's registry tooling.

```bash
npx shadcn@latest add https://www.creative-tim.com/ui/r/<block-name>.json
```

**Examples:**
```bash
npx shadcn@latest add https://www.creative-tim.com/ui/r/hero-01.json
npx shadcn@latest add https://www.creative-tim.com/ui/r/testimonials-03.json
```

### 1.3 Block Discovery

Browse all blocks:
- Website: https://www.creative-tim.com/ui
- AI index: https://www.creative-tim.com/ui/llms.txt (grouped by category, machine-readable)

Individual block JSON (for programmatic access):
```
https://www.creative-tim.com/ui/r/<block-name>.json
```

---

## 2. PRO Blocks & API Key

PRO blocks require a `Creative-Tim-Api-Key` header when fetching the block JSON. Obtain a key at https://www.creative-tim.com/ui.

### 2.1 Environment Setup

```bash
# .env.local (never commit this)
CREATIVE_TIM_UI_API_KEY=pk_live_xxxxxxxxxxxxxxxx
```

### 2.2 CLI Install with Key

```bash
npx @creative-tim/ui@latest add <pro-block-name> --api-key $CREATIVE_TIM_UI_API_KEY
```

### 2.3 Global Login (persists across sessions)

```bash
npx @creative-tim/ui@latest login --api-key pk_live_xxxxxxxxxxxxxxxx
```

After login, all `add` commands automatically include the key — no `--api-key` flag needed.

### 2.4 Detecting PRO Blocks

PRO blocks are marked on the website. In the registry JSON they include `"pro": true`. Free-tier blocks have no `pro` field.

---

## 3. Brand Identity

### 3.1 Primary Accent — Orange

**Rule:** Use `orange` as the primary brand accent for interactive elements, icons, CTAs, and highlights.

```tsx
// CORRECT — orange accent
<div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-600">
  <Bot className="h-4 w-4 text-white" />
</div>
<AvatarFallback className="bg-orange-100 text-orange-700">JD</AvatarFallback>
<Badge className="bg-orange-50 text-orange-700 border-orange-200">OpenClaw</Badge>
```

```tsx
// WRONG — violet/purple signals AI-generated defaults, not Creative Tim
<div className="bg-violet-600">...</div>
<Badge className="text-purple-700">...</Badge>
```

**Why:** Purple/violet is the default accent in many AI coding tools. Any block using it looks auto-generated and inconsistent with the library.

### 3.2 Status Colors

| State | Color |
|-------|-------|
| Active / Success | `emerald` |
| Warning / Pending | `amber` |
| Error / Stopped | `red` |
| Info / In-Progress | `blue` |
| Neutral / Inactive | `slate` |

### 3.3 Surface Colors

- Card backgrounds: `bg-background` (default card) or `bg-muted/30` (subtle areas like sidebars)
- Borders: use `border` (theme token) — never hardcode `border-gray-200`
- Text hierarchy: `text-foreground` (primary), `text-muted-foreground` (secondary)

---

## 4. Typography Rules

### 4.1 `text-sm` for Readable Content

**Rule:** Use `text-sm` for all body text that users need to read.

```tsx
// CORRECT
<TableCell className="text-sm font-medium">{agent.name}</TableCell>
<p className="text-sm text-muted-foreground">{description}</p>
<span className="text-sm">{agent.lastActive}</span>
```

```tsx
// WRONG — text-xs for readable body content is too small
<TableCell className="text-xs">{agent.name}</TableCell>
<p className="text-xs text-muted-foreground">{description}</p>
```

### 4.2 `text-xs` Only for Tiny/Supplementary Elements

`text-xs` is acceptable for:
- Avatar initials (`AvatarFallback`)
- `font-mono` timestamps and IDs
- Badge/pill labels (priority, status)
- Sidebar group headers (`uppercase tracking-wider`)
- Action buttons with h-6 or h-7 (`className="h-6 px-2 text-xs"`)

### 4.3 Never Use Arbitrary Font Sizes

```tsx
// WRONG
<span className="text-[10px]">...</span>
<p className="text-[11px]">...</p>
<div className="text-[0.65rem]">...</div>
```

---

## 5. Tailwind v4 Constraints

### 5.1 No Arbitrary Values

Tailwind v4 uses a continuous numeric scale. Arbitrary bracket values are not allowed.

```tsx
// WRONG — arbitrary values
<div className="h-[380px] w-[280px]">
<div className="max-w-[85%] min-w-[80px]">
<div className="gap-[14px] p-[18px]">
```

```tsx
// CORRECT — use the numeric scale
<div className="h-96 w-72">         // h-96 = 384px, w-72 = 288px
<div className="max-w-sm">          // 384px — close enough, or max-w-xs / max-w-md
<div className="gap-3.5 p-4">       // gap-3.5 = 14px, p-4 = 16px
```

### 5.2 Numeric Scale Reference

```
h-6  = 24px     h-8  = 32px     h-10 = 40px
h-12 = 48px     h-16 = 64px     h-20 = 80px
h-24 = 96px     h-32 = 128px    h-48 = 192px
h-64 = 256px    h-80 = 320px    h-96 = 384px

gap-1 = 4px     gap-2 = 8px     gap-3 = 12px
gap-4 = 16px    gap-5 = 20px    gap-6 = 24px

p-2 = 8px       p-3 = 12px      p-4 = 16px
p-5 = 20px      p-6 = 24px
```

### 5.3 Use Semantic Width Utilities

```tsx
// CORRECT
<div className="max-w-sm">    // 384px
<div className="max-w-md">    // 448px
<div className="max-w-lg">    // 512px
<div className="max-w-xl">    // 576px
<div className="max-w-2xl">   // 672px
<div className="w-64">        // sidebar = 256px
<div className="w-72">        // kanban column = 288px
```

### 5.4 Responsive Breakpoints Only

```tsx
// CORRECT
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">

// WRONG — custom media query
<div className="[@media(min-width:640px)]:grid-cols-2">
```

---

## 6. Component Patterns

### 6.1 Card Structure

Use `Card > CardHeader + CardContent` for content grouping.

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Section Title</CardTitle>
  </CardHeader>
  <CardContent>
    {/* content */}
  </CardContent>
</Card>
```

### 6.2 KPI / Stat Cards — py-0

KPI cards use `py-0` on CardContent to let the parent padding control vertical rhythm.

```tsx
// CORRECT
<Card>
  <CardContent className="px-4 py-0">
    <p className="text-muted-foreground text-sm">Total Agents</p>
    <p className="text-2xl font-bold">42</p>
  </CardContent>
</Card>

// WRONG — default py causes too much padding in stat grids
<Card>
  <CardContent className="p-4">
```

### 6.3 Sidebar Navigation

Standard sidebar width is `w-64` (256px), with `bg-muted/30 border-r`.

```tsx
<aside className="bg-muted/30 flex h-full w-64 flex-col border-r">
  {/* logo row */}
  <div className="flex items-center gap-2.5 border-b px-5 py-4">
    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-600">
      <Bot className="h-4 w-4 text-white" />
    </div>
    <span className="text-sm font-semibold">App Name</span>
  </div>
  {/* nav */}
  <nav className="flex-1 space-y-0.5 p-3">
    {NAV_ITEMS.map((item) => (
      <button
        key={item.label}
        className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
          item.active
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:bg-background/60 hover:text-foreground"
        }`}
      >
        <item.icon className="h-4 w-4" />
        {item.label}
      </button>
    ))}
  </nav>
</aside>
```

### 6.4 ScrollArea for Overflow

Any list that may overflow its container must use `ScrollArea`.

```tsx
import { ScrollArea } from "@/components/ui/scroll-area"

<ScrollArea className="flex-1">
  <div className="space-y-2 p-4">
    {items.map((item) => <Item key={item.id} {...item} />)}
  </div>
</ScrollArea>
```

### 6.5 Badge Variants

```tsx
// Status badge (with dot)
<div className="inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium bg-emerald-50 text-emerald-700 border-emerald-200">
  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
  Active
</div>

// Type badge
<Badge variant="outline" className="text-xs font-medium bg-orange-50 text-orange-700 border-orange-200">
  OpenClaw
</Badge>
```

### 6.6 Avoid Inline Styles

```tsx
// WRONG
<div style={{ color: '#ff6b35', padding: '16px' }}>

// CORRECT
<div className="text-orange-500 p-4">
```

---

## 7. Hydration Safety

### 7.1 Never Use Date in useState Initializer

`new Date()`, `Date.now()`, and `toLocaleTimeString()` return different values on the server vs. the client, causing React hydration errors.

```tsx
// WRONG — causes "Hydration failed" error
const [events, setEvents] = useState(() => [
  { id: "1", timestamp: new Date().toLocaleTimeString() },
])

// WRONG — locale-dependent
const [time, setTime] = useState(new Date().toLocaleTimeString())
```

```tsx
// CORRECT — static strings for initial SSR state
const INITIAL_TIMESTAMPS = ["10:30:00", "10:30:04", "10:30:08"]

const [events, setEvents] = useState(() =>
  INITIAL_DATA.slice(0, 3).map((e, i) => ({
    ...e,
    id: `init-${i}`,
    timestamp: INITIAL_TIMESTAMPS[i],
  }))
)

// Live timestamps only inside useEffect / setInterval (client-only)
function nowTimeString() {
  const d = new Date()
  return [d.getHours(), d.getMinutes(), d.getSeconds()]
    .map((n) => String(n).padStart(2, "0"))
    .join(":")
}

useEffect(() => {
  const interval = setInterval(() => {
    setEvents((prev) => [
      ...prev,
      { id: `evt-${Date.now()}`, timestamp: nowTimeString(), ... }
    ])
  }, 2000)
  return () => clearInterval(interval)
}, [])
```

### 7.2 suppressHydrationWarning for Intentional Mismatches

If a mismatch is truly intentional (e.g. a live clock that intentionally differs):
```tsx
<time suppressHydrationWarning>{displayTime}</time>
```

---

## 8. Block Authoring Guide

### 8.1 File Structure

Every block consists of two files:
1. `registry/creative-tim/blocks/<name>.tsx` — the component
2. `registry/creative-tim/blocks/<name>/page.tsx` — the page wrapper

The page wrapper simply renders the block:
```tsx
import BlockName from "@/registry/creative-tim/blocks/<name>"
export default function Page() {
  return <BlockName />
}
```

### 8.2 Registry Entry

Add to `registry/registry-blocks.ts`:
```ts
{
  name: "my-block-01",
  type: "registry:block",
  categories: ["my-category"],
  meta: {
    isFree: true,
    label: "My Block",
    createdAt: "2026-03-14",
  },
  registryDependencies: ["button", "card", "badge"],  // SHORT NAMES ONLY
  files: [
    {
      path: "registry/creative-tim/blocks/my-block-01.tsx",
      type: "registry:component",
    },
    {
      path: "registry/creative-tim/blocks/my-block-01/page.tsx",
      type: "registry:page",
      target: "app/blocks/my-block-01/page.tsx",
    },
  ],
}
```

**IMPORTANT:** `registryDependencies` must use **short names** (`"button"`, `"card"`, `"badge"`) — never full URLs.

### 8.3 After Adding Blocks

Rebuild the registry:
```bash
pnpm --filter www registry:build
```

This regenerates `public/r/*.json`, `__index__.tsx`, and `__blocks__.json` (which powers `llms.txt`).

### 8.4 Import Paths in Blocks

Use the registry alias, not relative paths:
```tsx
import { Button } from "@/registry/creative-tim/ui/button"
import { Card, CardContent } from "@/registry/creative-tim/ui/card"
```

### 8.5 Block Checklist

Before submitting a new block:
- [ ] No `violet` or `purple` colors — use `orange` for brand accent
- [ ] All readable text uses `text-sm` minimum
- [ ] No arbitrary Tailwind values (`[10px]`, `[85%]`, etc.)
- [ ] KPI/stat `CardContent` uses `px-4 py-0`
- [ ] No `new Date()` in `useState` initializers
- [ ] No inline `style={{}}` attributes
- [ ] `registryDependencies` uses short names
- [ ] `registry:build` completes without errors
