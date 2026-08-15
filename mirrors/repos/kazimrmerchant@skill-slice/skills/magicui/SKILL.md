---
name: magicui
description: "Installs Magic UI animated React components through magicui-cli into a Tailwind + shadcn tree (marquee, shimmer-button, number-ticker, animated-beam). Trigger on magicui/magic-ui landing kits or those registry names. Do not use for stock shadcn primitives, Emil-style popover craft, or Remotion frame animation."
version: 1.0.1
---

# Magic UI

## Overview

Magic UI is a collection of animated React components built on Tailwind CSS and shadcn/ui. Components are installed via CLI directly into your project — you own the source code and can customize freely.

**Key traits:**
- CLI-based install (no runtime package dependency)
- Tailwind CSS + CSS variables for theming
- shadcn/ui compatible
- TypeScript first
- React 18+ (works with 19), Tailwind 3+ (works with v4)

## When to Use

Use this skill when the user:
- Explicitly asks for **magicui** or **Magic UI** components
- Needs animated React UI components (marquees, counters, shimmer buttons, ripple backgrounds, meteors, confetti, etc.)
- Is building a landing page, hero section, or marketing page with motion effects
- Wants to install, customize, or troubleshoot Magic UI components
- Needs frontend UI/UX guidance for React + Tailwind + shadcn/ui projects
- Asks about responsive layout, accessibility, component states, or design-system integration with Magic UI

## Prerequisites

Before installing Magic UI components, ensure the project has Tailwind CSS and shadcn/ui configured.

### 1. Install Tailwind CSS (if not present)

```bash
npm install tailwindcss @tailwindcss/typography
```

### 2. Initialize shadcn/ui (if not present)

```bash
npx shadcn@latest init
```

This sets up the `cn` utility in `lib/utils.ts` (requires `clsx` + `tailwind-merge`).

### 3. Verify `cn` utility exists

```bash
# Check for the utility file
cat lib/utils.ts
```

If missing, create `lib/utils.ts`:

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

Install dependencies if needed:

```bash
npm install clsx tailwind-merge
```

## Procedure

### Install a Component

```bash
npx magicui-cli add <component-name>
```

This copies the component source into `components/magicui/`. You own the code and can edit it freely.

> **Windows (PowerShell):** If `npx` prompts to install, confirm with `y`. Use `npx magicui-cli@latest` if you hit a "component not found" error.

### List All Available Components

```bash
npx magicui-cli list
```

### Popular Component Catalog

`animated-beam`, `animated-gradient-text`, `animated-grid-pattern`, `animated-list`, `animated-shiny-text`, `aurora-text`, `blur-in`, `blur-fade`, `border-beam`, `confetti`, `cool-mode`, `dock`, `dot-pattern`, `file-tree`, `flip-text`, `globe`, `grid-pattern`, `hyper-text`, `interactive-hover-button`, `letter-pullup`, `magic-card`, `marquee`, `meteors`, `morphing-text`, `neon-gradient-card`, `number-ticker`, `orbiting-circles`, `particles`, `pointer`, `pulsating-button`, `rainbow-button`, `retro-grid`, `ripple`, `safari`, `scroll-based-velocity`, `shimmer-button`, `shine-border`, `shiny-button`, `sparkles-text`, `spinning-text`, `terminal`, `text-reveal`, `ticker`, `typing-animation`, `vanish-input`, `wavy-text`, `word-fade-in`, `word-pull-up`, `word-rotate`

### Component Examples

#### AnimatedBeam — connecting lines between elements

```bash
npx magicui-cli add animated-beam
```

```tsx
import { AnimatedBeam } from "@/components/magicui/animated-beam";
import { useRef } from "react";

export function BeamDemo() {
  const containerRef = useRef<HTMLDivElement>(null);
  const fromRef = useRef<HTMLDivElement>(null);
  const toRef = useRef<HTMLDivElement>(null);

  return (
    <div ref={containerRef} className="relative flex h-64 items-center justify-between p-10">
      <div ref={fromRef} className="h-12 w-12 rounded-full bg-blue-500" />
      <div ref={toRef} className="h-12 w-12 rounded-full bg-purple-500" />
      <AnimatedBeam containerRef={containerRef} fromRef={fromRef} toRef={toRef} />
    </div>
  );
}
```

#### Marquee — infinite scrolling ticker

```bash
npx magicui-cli add marquee
```

```tsx
import Marquee from "@/components/magicui/marquee";

const logos = ["Vercel", "Stripe", "Linear", "Notion", "Figma"];

export function LogoMarquee() {
  return (
    <Marquee pauseOnHover className="[--duration:20s]">
      {logos.map((name) => (
        <div key={name} className="mx-8 text-xl font-semibold text-muted-foreground">
          {name}
        </div>
      ))}
    </Marquee>
  );
}
```

#### ShimmerButton — animated gradient CTA

```bash
npx magicui-cli add shimmer-button
```

```tsx
import { ShimmerButton } from "@/components/magicui/shimmer-button";

export function HeroCTA() {
  return (
    <ShimmerButton
      shimmerColor="#ffffff"
      shimmerSize="0.1em"
      shimmerDuration="2s"
      background="linear-gradient(135deg, #6366f1, #8b5cf6)"
      className="px-8 py-3 text-white font-semibold"
    >
      Get Started Free
    </ShimmerButton>
  );
}
```

#### NumberTicker — animated counting up

```bash
npx magicui-cli add number-ticker
```

```tsx
import NumberTicker from "@/components/magicui/number-ticker";

export function StatsSection() {
  return (
    <div className="grid grid-cols-3 gap-8 text-center">
      <div>
        <NumberTicker value={10000} className="text-5xl font-bold" />
        <p className="text-muted-foreground">Active Users</p>
      </div>
      <div>
        <NumberTicker value={99} className="text-5xl font-bold" />
        <span className="text-5xl font-bold">%</span>
        <p className="text-muted-foreground">Uptime</p>
      </div>
      <div>
        <NumberTicker value={500} className="text-5xl font-bold" />
        <p className="text-muted-foreground">Customers</p>
      </div>
    </div>
  );
}
```

#### SparklesText — glittering highlight text

```bash
npx magicui-cli add sparkles-text
```

```tsx
import SparklesText from "@/components/magicui/sparkles-text";

export function HeroHeading() {
  return (
    <h1 className="text-6xl font-bold">
      Build{" "}
      <SparklesText text="faster" colors={{ first: "#6366f1", second: "#ec4899" }} />
      {" "}with AI
    </h1>
  );
}
```

#### Ripple — pulsing circle effect

```bash
npx magicui-cli add ripple
```

```tsx
import { Ripple } from "@/components/magicui/ripple";

export function HeroBackground() {
  return (
    <div className="relative flex h-96 items-center justify-center overflow-hidden bg-background">
      <Ripple mainCircleSize={200} numCircles={8} />
      <p className="z-10 text-4xl font-bold">Connect Everything</p>
    </div>
  );
}
```

#### Confetti — celebration burst

```bash
npx magicui-cli add confetti
```

```tsx
import { useConfetti } from "@/components/magicui/confetti";

export function SuccessButton() {
  const { fire } = useConfetti();

  return (
    <button
      onClick={() => fire({ particleCount: 100, spread: 70, origin: { y: 0.6 } })}
      className="rounded-lg bg-green-500 px-6 py-3 text-white font-semibold"
    >
      Complete Purchase
    </button>
  );
}
```

#### Meteors — falling meteor streaks background

```bash
npx magicui-cli add meteors
```

```tsx
import { Meteors } from "@/components/magicui/meteors";

export function HeroCard() {
  return (
    <div className="relative overflow-hidden rounded-2xl border bg-background p-8">
      <Meteors number={20} />
      <h2 className="relative z-10 text-3xl font-bold">Your Product Name</h2>
      <p className="relative z-10 mt-2 text-muted-foreground">Tagline goes here</p>
    </div>
  );
}
```

#### BlurIn — text fade-in with blur

```bash
npx magicui-cli add blur-in
```

```tsx
import BlurIn from "@/components/magicui/blur-in";

export function AnimatedHero() {
  return (
    <BlurIn
      word="The Future of Development"
      className="text-5xl font-bold tracking-tight"
      duration={1.2}
    />
  );
}
```

#### Globe — 3D interactive globe

```bash
npx magicui-cli add globe
```

```tsx
import Globe from "@/components/magicui/globe";

export function GlobalSection() {
  return (
    <div className="flex flex-col items-center">
      <h2 className="text-3xl font-bold">Available Worldwide</h2>
      <Globe className="h-[500px] w-[500px]" />
    </div>
  );
}
```

### Full Landing Page Pattern

```tsx
// app/page.tsx — typical hero section with Magic UI components
import BlurIn from "@/components/magicui/blur-in";
import { ShimmerButton } from "@/components/magicui/shimmer-button";
import { Ripple } from "@/components/magicui/ripple";
import Marquee from "@/components/magicui/marquee";
import NumberTicker from "@/components/magicui/number-ticker";

export default function LandingPage() {
  return (
    <main>
      {/* Hero */}
      <section className="relative flex h-screen flex-col items-center justify-center text-center">
        <Ripple mainCircleSize={300} numCircles={6} />
        <BlurIn word="Ship Faster Than Ever" className="z-10 text-6xl font-bold" />
        <p className="z-10 mt-4 text-xl text-muted-foreground">
          The platform that gets you from idea to production
        </p>
        <ShimmerButton className="z-10 mt-8">Start for free</ShimmerButton>
      </section>

      {/* Social proof logos */}
      <section className="py-12">
        <Marquee className="[--duration:30s]">
          {["Company A", "Company B", "Company C", "Company D", "Company E"].map((name) => (
            <span key={name} className="mx-12 text-lg text-muted-foreground">{name}</span>
          ))}
        </Marquee>
      </section>

      {/* Stats */}
      <section className="py-20 text-center">
        <div className="grid grid-cols-3 gap-12">
          <div><NumberTicker value={50000} className="text-4xl font-bold" /><p>Users</p></div>
          <div><NumberTicker value={99} className="text-4xl font-bold" /><span>%</span><p>Uptime</p></div>
          <div><NumberTicker value={200} className="text-4xl font-bold" /><span>+</span><p>Countries</p></div>
        </div>
      </section>
    </main>
  );
}
```

### UI/UX Design Workflow

When the user asks for design or implementation guidance (not just component installation):

1. **Start from the user task and information architecture**, not decoration.
2. **Map key states**: empty, loading, success, error, disabled, permission-limited, offline, and responsive variants.
3. **Apply accessibility requirements early**: keyboard flow, focus visibility, labels, contrast, reduced motion, touch targets, text resizing, and semantic structure.
4. **Use design-system primitives** where available; otherwise define tokens for spacing, color, type, elevation, radius, and motion.
5. **Design responsive layouts** with stable dimensions and no text overlap across desktop and mobile.
6. **Validate with realistic content**: long labels, error text, touch/keyboard interaction.
7. **Deliver concrete implementation guidance**, not vague aesthetic notes.

**Output format for design tasks:** Return a plan with user goal, layout structure, component list, states, accessibility checks, responsive behavior, copy notes, and verification steps. For code tasks, include exact files/components and testing guidance.

## Pitfalls

| Issue | Fix |
|------|-----|
| `cn` not found | Install `clsx` + `tailwind-merge` and add `lib/utils.ts` (see Prerequisites) |
| Animation not working (Tailwind v4) | Define keyframes/CSS vars in your CSS via `@theme` and add the dark variant with `@custom-variant dark (&:where(.dark, .dark *))` |
| Animation not working (Tailwind v3) | Ensure `tailwind.config.ts` has `darkMode: "class"` plus the animation keyframes in the `theme.extend.keyframes` and `theme.extend.animation` sections |
| Component not found | Run `npx magicui-cli@latest add <name>` (use `@latest` to get the current registry) |
| Peer dep warnings | Magic UI needs React 18+ (works with 19) and Tailwind 3+ (works with v4). Update if on older versions |
| Motion causes vestibular issues | Wrap animations in `prefers-reduced-motion` checks; provide static fallbacks for users with reduced motion enabled |
| Text overlap on mobile | Avoid fragile viewport-scaled text; use responsive font classes (`text-sm md:text-lg`) instead of `vw` units |
| Layout shift on state change | Reserve space for loading/error states with fixed dimensions or skeletons |

## Verification

After installing and using Magic UI components, verify:

### 1. Component file exists

```bash
# Check the installed component
ls components/magicui/<component-name>.tsx
```

### 2. Dev server compiles without errors

```bash
npm run dev
```

Open the page using the component — confirm no TypeScript or import errors in the terminal or browser console.

### 3. Accessibility checks

- Tab through the page: all interactive elements are keyboard-reachable with visible focus
- Run a screen reader pass: semantic headings and labels are announced correctly
- Check contrast ratios meet WCAG 2.2 AA (4.5:1 for normal text, 3:1 for large text)
- Enable `prefers-reduced-motion` in OS settings: animations should degrade gracefully

### 4. Responsive checks

- Test at 375px (mobile), 768px (tablet), 1280px (desktop) widths
- Confirm no text overlap, no horizontal scroll, no layout shift
- Verify touch targets are at least 44×44px on mobile

### 5. Dark/light mode

- Toggle between light and dark themes
- Confirm CSS variables resolve correctly in both modes

## Quality Checklist

- [ ] User can complete the core task quickly and repeatedly
- [ ] UI supports keyboard, screen readers, visible focus, and sufficient contrast
- [ ] Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text
- [ ] Controls use familiar affordances and expose state clearly
- [ ] Motion is purposeful and respects `prefers-reduced-motion`
- [ ] Visual direction is intentional and consistent with the product domain
- [ ] All component states implemented: empty, loading, success, error, disabled
- [ ] Styling follows the app's existing design system — no ornamental drift

## Failure Handling

If requirements conflict, prioritize **usability, accessibility, and product fit** over novelty. If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant. Verify current platform guidance when building for Apple, Android, or a specific design system.

## References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- W3C WCAG FAQ: https://www.w3.org/WAI/standards-guidelines/wcag/faq/
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html

> **Re-check official/current docs before relying on provider-specific APIs, policy, pricing, security behavior, or platform rules.** Sources verified 2026-05-31.
