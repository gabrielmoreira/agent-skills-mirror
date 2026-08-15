---
name: design-taste-frontend
description: "Builds and reviews React/Next.js/Tailwind interfaces under anti-generic taste: calibrated color, asymmetric layout, typography, motion, and loading/empty/error states. Use when creating or reviewing dashboards, heroes, landing pages, or feature sections that must avoid default LLM UI. Not for Vercel a11y/CLS compliance (web-interface-guidelines), GSAP timelines (gsap-web-animations), or SVG markup (svg-creator)."
version: 1.0.1
category: frontend
risk: safe
source: community
source_repo: Leonxlnx/taste-skill
source_type: community
date_added: "2026-04-17"
tags: [frontend, design, ui, react]
tools: [claude, cursor, codex, antigravity]
---

# High-Agency Frontend Skill

## When to Use

- Use when the user asks to create, improve, or review frontend UI with strong design taste and anti-generic constraints.
- Use when React, Next.js, Tailwind, motion, component states, typography, spacing, color, or responsive behavior need senior-level design judgment.
- Use when the output must override common LLM UI biases such as centered heroes, purple gradients, card overuse, poor states, and fragile layouts.
- Use when building SaaS dashboards, landing pages, marketing sites, or feature sections requiring a "Vercel-core meets Dribbble-clean" aesthetic.

## Prerequisites

- **Framework:** React or Next.js project with `package.json` present.
- **Styling:** Tailwind CSS v3 or v4 installed and configured.
- **Icons:** `@phosphor-icons/react` or `@radix-ui/react-icons` installed (or willingness to install).
- **Motion (optional):** `framer-motion` installed if `MOTION_INTENSITY > 3`.
- **Verify dependencies before importing:** Check `package.json` for any 3rd party library before importing it. If missing, output the install command (e.g. `npm install package-name`) before providing code. **Never** assume a library exists.

## Procedure

### 1. Set the Active Baseline Configuration

Use these global variables to drive all design decisions in subsequent steps. Adapt dynamically based on explicit user requests in chat prompts; otherwise use these defaults:

- **DESIGN_VARIANCE: 8** (1=Perfect Symmetry, 10=Artsy Chaos)
- **MOTION_INTENSITY: 6** (1=Static/No movement, 10=Cinematic/Magic Physics)
- **VISUAL_DENSITY: 4** (1=Art Gallery/Airy, 10=Pilot Cockpit/Packed Data)

### 2. Apply Architecture & Conventions

Unless the user explicitly specifies a different stack, follow these structural constraints:

1. **Framework & Interactivity:** Default to Server Components (`RSC`).
   - **RSC SAFETY:** Global state works ONLY in Client Components. In Next.js, wrap providers in a `"use client"` component.
   - **INTERACTIVITY ISOLATION:** If Motion or Liquid Glass sections are active, extract the interactive UI component as an isolated leaf component with `'use client'` at the very top. Server Components must exclusively render static layouts.
2. **State Management:** Use local `useState`/`useReducer` for isolated UI. Use global state strictly for deep prop-drilling avoidance.
3. **Styling Policy:** Use Tailwind CSS (v3/v4) for 90% of styling.
   - **TAILWIND VERSION LOCK:** Check `package.json` first. Do not use v4 syntax in v3 projects.
   - **T4 CONFIG GUARD:** For v4, do NOT use `tailwindcss` plugin in `postcss.config.js`. Use `@tailwindcss/postcss` or the Vite plugin.
4. **ANTI-EMOJI POLICY [CRITICAL]:** NEVER use emojis in code, markup, text content, or alt text. Replace symbols with high-quality icons (Radix, Phosphor) or clean SVG primitives. Emojis are BANNED.
5. **Responsiveness & Spacing:**
   - Standardize breakpoints (`sm`, `md`, `lg`, `xl`).
   - Contain page layouts using `max-w-[1400px] mx-auto` or `max-w-7xl`.
   - **Viewport Stability [CRITICAL]:** NEVER use `h-screen` for full-height Hero sections. ALWAYS use `min-h-[100dvh]` to prevent layout jumping on mobile browsers (iOS Safari).
   - **Grid over Flex-Math:** NEVER use complex flexbox percentage math (`w-[calc(33%-1rem)]`). ALWAYS use CSS Grid (`grid grid-cols-1 md:grid-cols-3 gap-6`).
6. **Icons:** Use exactly `@phosphor-icons/react` or `@radix-ui/react-icons` as import paths (check installed version). Standardize `strokeWidth` globally (e.g., exclusively `1.5` or `2.0`).

### 3. Apply Design Engineering Directives (Bias Correction)

Proactively construct premium interfaces using these engineered rules:

**Rule 1: Deterministic Typography**
- **Display/Headlines:** Default to `text-4xl md:text-6xl tracking-tighter leading-none`.
  - **ANTI-SLOP:** Discourage `Inter` for "Premium" or "Creative" vibes. Force unique character using `Geist`, `Outfit`, `Cabinet Grotesk`, or `Satoshi`.
  - **TECHNICAL UI RULE:** Serif fonts are strictly BANNED for Dashboard/Software UIs. Use exclusively high-end Sans-Serif pairings (`Geist` + `Geist Mono` or `Satoshi` + `JetBrains Mono`).
- **Body/Paragraphs:** Default to `text-base text-gray-600 leading-relaxed max-w-[65ch]`.

**Rule 2: Color Calibration**
- Max 1 Accent Color. Saturation < 80%.
- **THE LILA BAN:** The "AI Purple/Blue" aesthetic is strictly BANNED. No purple button glows, no neon gradients. Use absolute neutral bases (Zinc/Slate) with high-contrast, singular accents (e.g. Emerald, Electric Blue, or Deep Rose).
- **COLOR CONSISTENCY:** Stick to one palette for the entire output. Do not fluctuate between warm and cool grays within the same project.

**Rule 3: Layout Diversification**
- **ANTI-CENTER BIAS:** Centered Hero/H1 sections are strictly BANNED when `DESIGN_VARIANCE > 4`. Force "Split Screen" (50/50), "Left Aligned content / Right Aligned asset", or "Asymmetric White-space" structures.

**Rule 4: Materiality, Shadows, and "Anti-Card Overuse"**
- **DASHBOARD HARDENING:** For `VISUAL_DENSITY > 7`, generic card containers are strictly BANNED. Use logic-grouping via `border-t`, `divide-y`, or purely negative space. Data metrics should breathe without being boxed in unless elevation (z-index) is functionally required.
- Use cards ONLY when elevation communicates hierarchy. When a shadow is used, tint it to the background hue.

**Rule 5: Interactive UI States**
- **Mandatory Generation:** You MUST implement full interaction cycles:
  - **Loading:** Skeletal loaders matching layout sizes (avoid generic circular spinners).
  - **Empty States:** Beautifully composed empty states indicating how to populate data.
  - **Error States:** Clear, inline error reporting (e.g., forms).
  - **Tactile Feedback:** On `:active`, use `-translate-y-[1px]` or `scale-[0.98]` to simulate a physical push.

**Rule 6: Data & Form Patterns**
- **Forms:** Label MUST sit above input. Helper text is optional but should exist in markup. Error text below input. Use a standard `gap-2` for input blocks.

### 4. Apply Creative Proactivity (Anti-Slop Implementation)

Systematically implement these high-end coding concepts as baseline:

1. **"Liquid Glass" Refraction:** When glassmorphism is needed, go beyond `backdrop-blur`. Add a 1px inner border (`border-white/10`) and a subtle inner shadow (`shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]`) to simulate physical edge refraction.
2. **Magnetic Micro-physics (If MOTION_INTENSITY > 5):** Implement buttons that pull slightly toward the mouse cursor. **CRITICAL:** NEVER use React `useState` for magnetic hover or continuous animations. Use EXCLUSIVELY Framer Motion's `useMotionValue` and `useTransform` outside the React render cycle to prevent performance collapse on mobile.
3. **Perpetual Micro-Interactions (When MOTION_INTENSITY > 5):** Embed continuous, infinite micro-animations (Pulse, Typewriter, Float, Shimmer, Carousel) in standard components (avatars, status dots, backgrounds). Apply premium Spring Physics (`type: "spring", stiffness: 100, damping: 20`) to all interactive elements—no linear easing.
4. **Layout Transitions:** Always utilize Framer Motion's `layout` and `layoutId` props for smooth re-ordering, resizing, and shared element transitions across state changes.
5. **Staggered Orchestration:** Do not mount lists or grids instantly. Use `staggerChildren` (Framer) or CSS cascade (`animation-delay: calc(var(--index) * 100ms)`) to create sequential waterfall reveals. **CRITICAL:** For `staggerChildren`, the Parent (`variants`) and Children MUST reside in the identical Client Component tree. If data is fetched asynchronously, pass the data as props into a centralized Parent Motion wrapper.

### 5. Apply Performance Guardrails

- **DOM Cost:** Apply grain/noise filters exclusively to fixed, pointer-event-none pseudo-elements (e.g., `fixed inset-0 z-50 pointer-events-none`) and NEVER to scrolling containers to prevent continuous GPU repaints and mobile performance degradation.
- **Hardware Acceleration:** Never animate `top`, `left`, `width`, or `height`. Animate exclusively via `transform` and `opacity`.
- **Z-Index Restraint:** NEVER spam arbitrary `z-50` or `z-10` unprompted. Use z-indexes strictly for systemic layer contexts (Sticky Navbars, Modals, Overlays).

### 6. Use the Dial Definitions for Calibration

**DESIGN_VARIANCE (Level 1-10)**
- **1-3 (Predictable):** Flexbox `justify-center`, strict 12-column symmetrical grids, equal paddings.
- **4-7 (Offset):** Use `margin-top: -2rem` overlapping, varied image aspect ratios (e.g., 4:3 next to 16:9), left-aligned headers over center-aligned data.
- **8-10 (Asymmetric):** Masonry layouts, CSS Grid with fractional units (e.g., `grid-template-columns: 2fr 1fr 1fr`), massive empty zones (`padding-left: 20vw`).
- **MOBILE OVERRIDE:** For levels 4-10, any asymmetric layout above `md:` MUST aggressively fall back to a strict, single-column layout (`w-full`, `px-4`, `py-8`) on viewports `< 768px` to prevent horizontal scrolling and layout breakage.

**MOTION_INTENSITY (Level 1-10)**
- **1-3 (Static):** No automatic animations. CSS `:hover` and `:active` states only.
- **4-7 (Fluid CSS):** Use `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)`. Use `animation-delay` cascades for load-ins. Focus strictly on `transform` and `opacity`. Use `will-change: transform` sparingly.
- **8-10 (Advanced Choreography):** Complex scroll-triggered reveals or parallax. Use Framer Motion hooks. NEVER use `window.addEventListener('scroll')`.

**VISUAL_DENSITY (Level 1-10)**
- **1-3 (Art Gallery Mode):** Lots of white space. Huge section gaps. Everything feels very expensive and clean.
- **4-7 (Daily App Mode):** Normal spacing for standard web apps.
- **8-10 (Cockpit Mode):** Tiny paddings. No card boxes; just 1px lines to separate data. Everything is packed. **Mandatory:** Use Monospace (`font-mono`) for all numbers.

### 7. Apply the "Motion-Engine" Bento Paradigm (For SaaS Dashboards)

When generating modern SaaS dashboards or feature sections, use the following "Bento 2.0" architecture:

**A. Core Design Philosophy**
- **Aesthetic:** High-end, minimal, and functional.
- **Palette:** Background in `#f9fafb`. Cards are pure white (`#ffffff`) with a 1px border of `border-slate-200/50`.
- **Surfaces:** Use `rounded-[2.5rem]` for all major containers. Apply a "diffusion shadow" (e.g., `shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]`) to create depth without clutter.
- **Typography:** Strict `Geist`, `Satoshi`, or `Cabinet Grotesk` font stack. Use subtle tracking (`tracking-tight`) for headers.
- **Labels:** Titles and descriptions must be placed **outside and below** the cards to maintain a clean, gallery-style presentation.
- **Pixel-Perfection:** Use generous `p-8` or `p-10` padding inside cards.

**B. The Animation Engine Specs (Perpetual Motion)**
- **Spring Physics:** No linear easing. Use `type: "spring", stiffness: 100, damping: 20` for a premium, weighty feel.
- **Layout Transitions:** Heavily utilize the `layout` and `layoutId` props to ensure smooth re-ordering, resizing, and shared element state transitions.
- **Infinite Loops:** Every card must have an "Active State" that loops infinitely (Pulse, Typewriter, Float, or Carousel) to ensure the dashboard feels "alive".
- **Performance:** Wrap dynamic lists in `<AnimatePresence>` and optimize for 60fps. **PERFORMANCE CRITICAL:** Any perpetual motion or infinite loop MUST be memoized (`React.memo`) and completely isolated in its own microscopic Client Component. Never trigger re-renders in the parent layout.

**C. The 5-Card Archetypes (Micro-Animation Specs)**
Implement these specific micro-animations when constructing Bento grids (e.g., Row 1: 3 cols | Row 2: 2 cols split 70/30):
1. **The Intelligent List:** A vertical stack of items with an infinite auto-sorting loop. Items swap positions using `layoutId`, simulating an AI prioritizing tasks in real-time.
2. **The Command Input:** A search/AI bar with a multi-step Typewriter Effect. It cycles through complex prompts, including a blinking cursor and a "processing" state with a shimmering loading gradient.
3. **The Live Status:** A scheduling interface with "breathing" status indicators. Include a pop-up notification badge that emerges with an "Overshoot" spring effect, stays for 3 seconds, and vanishes.
4. **The Wide Data Stream:** A horizontal "Infinite Carousel" of data cards or metrics. Ensure the loop is seamless (using `x: ["0%", "-100%"]`) with a speed that feels effortless.
5. **The Contextual UI (Focus Mode):** A document view that animates a staggered highlight of a text block, followed by a "Float-in" of a floating action toolbar with micro-icons.

### 8. Draw from the Creative Arsenal (High-End Inspiration)

Do not default to generic UI. Pull from this library of advanced concepts to ensure the output is visually striking and memorable. When appropriate, leverage **GSAP (ScrollTrigger/Parallax)** for complex scrolltelling or **ThreeJS/WebGL** for 3D/Canvas animations, rather than basic CSS motion. **CRITICAL:** Never mix GSAP/ThreeJS with Framer Motion in the same component tree. Default to Framer Motion for UI/Bento interactions. Use GSAP/ThreeJS EXCLUSIVELY for isolated full-page scrolltelling or canvas backgrounds, wrapped in strict `useEffect` cleanup blocks.

**The Standard Hero Paradigm:** Stop doing centered text over a dark image. Try asymmetric Hero sections: Text cleanly aligned to the left or right. The background should feature a high-quality, relevant image with a subtle stylistic fade (darkening or lightening gracefully into the background color depending on if it is Light or Dark mode).

**Navigation & Menus:** Mac OS Dock Magnification, Magnetic Button, Gooey Menu, Dynamic Island, Contextual Radial Menu, Floating Speed Dial, Mega Menu Reveal.

**Layout & Grids:** Bento Grid, Masonry Layout, Chroma Grid, Split Screen Scroll, Curtain Reveal.

**Cards & Containers:** Parallax Tilt Card, Spotlight Border Card, Glassmorphism Panel, Holographic Foil Card, Tinder Swipe Stack, Morphing Modal.

**Scroll-Animations:** Sticky Scroll Stack, Horizontal Scroll Hijack, Locomotive Scroll Sequence, Zoom Parallax, Scroll Progress Path, Liquid Swipe Transition.

**Galleries & Media:** Dome Gallery, Coverflow Carousel, Drag-to-Pan Grid, Accordion Image Slider, Hover Image Trail, Glitch Effect Image.

**Typography & Text:** Kinetic Marquee, Text Mask Reveal, Text Scramble Effect, Circular Text Path, Gradient Stroke Animation, Kinetic Typography Grid.

**Micro-Interactions & Effects:** Particle Explosion Button, Liquid Pull-to-Refresh, Skeleton Shimmer, Directional Hover Aware Button, Ripple Click Effect, Animated SVG Line Drawing, Mesh Gradient Background, Lens Blur Depth.

### 9. Run the Final Pre-Flight Check

Evaluate code against this matrix before outputting. This is the **last** filter applied to logic:

- [ ] Is global state used appropriately to avoid deep prop-drilling rather than arbitrarily?
- [ ] Is mobile layout collapse (`w-full`, `px-4`, `max-w-7xl mx-auto`) guaranteed for high-variance designs?
- [ ] Do full-height sections safely use `min-h-[100dvh]` instead of the bugged `h-screen`?
- [ ] Do `useEffect` animations contain strict cleanup functions?
- [ ] Are empty, loading, and error states provided?
- [ ] Are cards omitted in favor of spacing where possible?
- [ ] Did you strictly isolate CPU-heavy perpetual animations in their own Client Components?

## Pitfalls

### Forbidden AI Tells (Strictly Avoid Unless Explicitly Requested)

**Visual & CSS**
- **NO Neon/Outer Glows:** Do not use default `box-shadow` glows or auto-glows. Use inner borders or subtle tinted shadows.
- **NO Pure Black:** Never use `#000000`. Use Off-Black, Zinc-950, or Charcoal.
- **NO Oversaturated Accents:** Desaturate accents to blend elegantly with neutrals.
- **NO Excessive Gradient Text:** Do not use text-fill gradients for large headers.
- **NO Custom Mouse Cursors:** They are outdated and ruin performance/accessibility.

**Typography**
- **NO Inter Font:** Banned. Use `Geist`, `Outfit`, `Cabinet Grotesk`, or `Satoshi`.
- **NO Oversized H1s:** The first heading should not scream. Control hierarchy with weight and color, not just massive scale.
- **Serif Constraints:** Use Serif fonts ONLY for creative/editorial designs. NEVER use Serif on clean Dashboards.

**Layout & Spacing**
- **Align & Space Perfectly:** Ensure padding and margins are mathematically perfect. Avoid floating elements with awkward gaps.
- **NO 3-Column Card Layouts:** The generic "3 equal cards horizontally" feature row is BANNED. Use a 2-column Zig-Zag, asymmetric grid, or horizontal scrolling approach instead.

**Content & Data (The "Jane Doe" Effect)**
- **NO Generic Names:** "John Doe", "Sarah Chan", or "Jack Su" are banned. Use highly creative, realistic-sounding names.
- **NO Generic Avatars:** DO NOT use standard SVG "egg" or Lucide user icons for avatars. Use creative, believable photo placeholders or specific styling.
- **NO Fake Numbers:** Avoid predictable outputs like `99.99%`, `50%`, or basic phone numbers (`1234567`). Use organic, messy data (`47.2%`, `+1 (312) 847-1928`).
- **NO Startup Slop Names:** "Acme", "Nexus", "SmartFlow". Invent premium, contextual brand names.
- **NO Filler Words:** Avoid AI copywriting clichés like "Elevate", "Seamless", "Unleash", or "Next-Gen". Use concrete verbs.

**External Resources & Components**
- **NO Broken Unsplash Links:** Do not use Unsplash. Use absolute, reliable placeholders like `https://picsum.photos/seed/{random_string}/800/600` or SVG UI Avatars.
- **shadcn/ui Customization:** You may use `shadcn/ui`, but NEVER in its generic default state. You MUST customize the radii, colors, and shadows to match the high-end project aesthetic.
- **Production-Ready Cleanliness:** Code must be extremely clean, visually striking, memorable, and meticulously refined in every detail.

### Common Technical Pitfalls

- **Tailwind v3/v4 mismatch:** Using v4 syntax in a v3 project. Always check `package.json` first.
- **RSC state leakage:** Using global state in Server Components. Wrap providers in `"use client"` components.
- **Magnetic hover with useState:** Using React `useState` for continuous animations causes performance collapse on mobile. Use Framer Motion's `useMotionValue` and `useTransform` exclusively.
- **GSAP + Framer Motion mixing:** Never mix GSAP/ThreeJS with Framer Motion in the same component tree. Use Framer Motion for UI/Bento, GSAP/ThreeJS for isolated full-page scrolltelling or canvas backgrounds only.
- **staggerChildren across component boundaries:** Parent `variants` and Children MUST reside in the identical Client Component tree. Pass async data as props into a centralized Parent Motion wrapper.
- **Grain/noise on scrolling containers:** Causes continuous GPU repaints. Apply only to fixed, pointer-event-none pseudo-elements.
- **Animating layout properties:** Never animate `top`, `left`, `width`, or `height`. Use `transform` and `opacity` exclusively.

## Verification

Before delivering the final output, verify each of the following:

1. **Dependency check:** Confirm all imported packages exist in `package.json`. If any are missing, provide the install command first.
   ```powershell
   # Check for a specific package
   Select-String -Path package.json -Pattern "framer-motion"
   ```
2. **Tailwind version check:** Confirm Tailwind version and use matching syntax.
   ```powershell
   Select-String -Path package.json -Pattern "tailwindcss"
   ```
3. **Pre-flight checklist:** All items in the Final Pre-Flight Check (Step 9) must pass.
4. **Anti-tell audit:** Scan generated code for banned patterns:
   - No `#000000` (use Zinc-950 or Charcoal)
   - No `Inter` font (use `Geist`, `Outfit`, `Cabinet Grotesk`, or `Satoshi`)
   - No `h-screen` (use `min-h-[100dvh]`)
   - No emojis in code, markup, text, or alt text
   - No purple/blue AI aesthetic (no neon gradients, no purple button glows)
   - No 3-column equal card layouts
   - No generic names ("John Doe", "Acme", "Nexus")
   - No Unsplash links (use `picsum.photos/seed/...`)
   - No filler words ("Elevate", "Seamless", "Unleash", "Next-Gen")
5. **State completeness:** Confirm loading, empty, and error states are implemented for all interactive components.
6. **Animation isolation:** Confirm all perpetual/infinite animations are memoized (`React.memo`) and isolated in their own Client Components.
7. **Build verification (if applicable):**
   ```powershell
   npm run build
   ```
   Confirm no TypeScript errors, no missing imports, and successful production build.
