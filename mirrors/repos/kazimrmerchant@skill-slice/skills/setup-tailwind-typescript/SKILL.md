---
name: setup-tailwind-typescript
description: "Scaffolds Tailwind CSS v4 in a TypeScript app (Next.js, Vite, or React) via @tailwindcss/postcss, CSS-first @theme tokens, cn() (clsx + tailwind-merge), and class-based dark mode. Use when adding Tailwind v4, a css-first theme, or a dark-mode toggle to a TS project. Not for Tailwind v3 tailwind.config.js, native CSS without Tailwind (modern-css), or glassmorphism recipes. Never run npx tailwindcss init — v4 dropped it and the content array."
version: 1.0.1
---

# Set Up Tailwind CSS v4 with TypeScript

## Overview

This skill configures Tailwind CSS v4 in a TypeScript project (Next.js, Vite, or standalone React) using the CSS-first `@theme` approach. It covers PostCSS setup, custom design tokens, global styles, type-safe class merging with `cn()`, dark mode, optional plugins, and accessibility-aware UI/UX verification.

**Key shift in Tailwind v4:** Theme configuration is done in CSS via `@theme` blocks, not in a `tailwind.config.ts` file. The `content` array is no longer needed—Tailwind v4 auto-detects used classes. `autoprefixer` is bundled and no longer a separate dependency. The `npx tailwindcss init` command is no longer required.

## When to Use

- Adding Tailwind CSS to an existing TypeScript project (Next.js App Router, Vite, or standalone React)
- Customizing the Tailwind theme for a project's design system (colors, fonts, spacing)
- Setting up type-safe component styling patterns with `clsx` and `tailwind-merge`
- Configuring dark mode with a class-based toggle
- Adding Tailwind plugins (typography, forms)
- Reviewing or auditing frontend UI for accessibility, responsive layout, and interaction states

## Prerequisites

- **Required:** An existing TypeScript project (Next.js, Vite, or React)
- **Optional:** Design system tokens (colors, spacing, fonts)
- **Optional:** List of Tailwind plugins to include
- **Windows host (primary):** Commands below assume PowerShell. Use `npm` as shown; no platform-specific path changes are needed for the npm commands.

## Procedure

### Step 1: Install Tailwind CSS v4

```bash
npm install -D tailwindcss @tailwindcss/postcss postcss
```

Create `postcss.config.mjs` at the project root:

```javascript
// postcss.config.mjs
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

**Expected:** `tailwindcss`, `@tailwindcss/postcss`, and `postcss` installed as dev dependencies. `postcss.config.mjs` registers the `@tailwindcss/postcss` plugin. Tailwind v4 bundles autoprefixer—no separate install needed. No `npx tailwindcss init` required.

**On failure:** If classes don't apply, verify `postcss.config.mjs` exists at the project root and `@tailwindcss/postcss` is listed. In a monorepo, place the file in the application's root directory, not the workspace root.

### Step 2: Configure the Theme with `@theme`

In Tailwind v4, the theme is defined in CSS using the `@theme` block. Add it to `src/app/globals.css` (combined with Step 3):

```css
@theme {
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-900: #1e3a5f;

  --color-secondary-500: #6366f1;
  --color-secondary-600: #4f46e5;

  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  --spacing-18: 4.5rem;
  --spacing-88: 22rem;
}
```

**Expected:** Theme tokens defined as CSS variables inside `@theme`. They generate utilities automatically: `bg-primary-500`, `font-sans`, `p-18`, etc. No `content` array needed—Tailwind v4 auto-detects used classes.

**On failure:** If custom utilities don't render, verify variable names follow the correct namespace (`--color-*`, `--font-*`, `--spacing-*`) and that the `@theme` block is in a CSS file processed by Tailwind.

### Step 3: Configure Global Styles

Edit `src/app/globals.css` (combined with the `@theme` block from Step 2):

```css
@import "tailwindcss";

@layer base {
  html {
    @apply antialiased;
  }

  body {
    @apply bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary-600 text-white px-4 py-2 rounded-lg
           hover:bg-primary-700 focus:outline-none focus:ring-2
           focus:ring-primary-500 focus:ring-offset-2
           transition-colors duration-200;
  }
}
```

**Expected:** `globals.css` starts with `@import "tailwindcss";` (the single Tailwind v4 directive replacing `@tailwind base/components/utilities`) plus any custom base and component layer styles. The file is imported in the root layout.

**On failure:** If styles don't apply, verify `globals.css` is imported in `layout.tsx` (or `_app.tsx` for Pages Router). Confirm `@import "tailwindcss";` is present and not commented out.

### Step 4: Create Type-Safe Utility Helpers

Create `src/lib/cn.ts`:

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

Install the dependencies:

```bash
npm install clsx tailwind-merge
```

Usage in components:

```tsx
import { cn } from "@/lib/cn";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
}

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "px-4 py-2 rounded-lg font-medium transition-colors",
        variant === "primary" && "bg-primary-600 text-white hover:bg-primary-700",
        variant === "secondary" && "bg-secondary-500 text-white hover:bg-secondary-600",
        variant === "outline" && "border border-gray-300 hover:bg-gray-50",
        className
      )}
      {...props}
    />
  );
}
```

**Expected:** `src/lib/cn.ts` exports a `cn()` function. `clsx` and `tailwind-merge` installed as dependencies. Components use `cn()` to combine class names without conflicts.

**On failure:** If `clsx` or `tailwind-merge` can't be found, run `npm install clsx tailwind-merge`. If TypeScript reports type errors in `cn.ts`, verify `ClassValue` is imported from `clsx`.

### Step 5: Add Dark Mode Support

By default, Tailwind v4's `dark:` variant responds to `prefers-color-scheme` (system preference). To toggle dark mode with a class, add a `@custom-variant` to `src/app/globals.css`:

```css
@custom-variant dark (&:where(.dark, .dark *));
```

Theme toggle implementation:

```tsx
"use client";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <button onClick={() => setDark(!dark)}>
      {dark ? "Light" : "Dark"} Mode
    </button>
  );
}
```

**Expected:** Dark mode toggles correctly between light and dark themes. The `dark` class is applied to the `<html>` element, and `dark:`-prefixed utilities respond accordingly.

**On failure:** If dark mode doesn't activate, verify `@custom-variant dark (&:where(.dark, .dark *));` is in your global CSS. Ensure the `dark` class is toggled on `<html>` (not `<body>`). For system-preference mode, omit the `@custom-variant` and Tailwind will use `prefers-color-scheme` automatically.

### Step 6: Add Plugins (Optional)

```bash
npm install -D @tailwindcss/typography @tailwindcss/forms
```

In Tailwind v4, plugins are loaded with `@plugin` in CSS (not in a `plugins` array). Add to `src/app/globals.css`:

```css
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

**Expected:** Plugins installed as dev dependencies and loaded with `@plugin` in global CSS. Plugin-provided classes (e.g., `prose` from typography, styled form elements from forms) are available in components.

**On failure:** If plugin classes don't render, verify the plugin is installed (`npm ls @tailwindcss/typography`) and loaded with `@plugin` in CSS. Restart the dev server after changes.

## Pitfalls

- **Missing import:** If no classes render, verify `globals.css` starts with `@import "tailwindcss";` and is imported in the root layout. Tailwind v4 auto-detects used classes—there is no `content` array to maintain.
- **Class conflicts:** Use `tailwind-merge` (via `cn()`) to prevent conflicting utility classes from both applying.
- **Custom values not working:** Define tokens inside `@theme` with the correct namespace (`--color-*`, `--font-*`, `--spacing-*`); each added variable extends Tailwind's defaults.
- **Dark mode not activating:** Verify `@custom-variant dark` is in CSS and the `dark` class is on `<html>`, not `<body>`.
- **Monorepo PostCSS config:** Place `postcss.config.mjs` in the application root, not the workspace root.
- **Accessibility drift:** Do not sacrifice readability or keyboard/screen-reader usability for visual novelty. If a requested pattern harms accessibility, explain the tradeoff and offer a better variant.
- **Layout fragility:** Avoid hover/loading/error states that cause layout shift. Test with longest labels and realistic content.

## Verification

Run these checks after completing the procedure:

- [ ] Tailwind classes render correctly in the browser (inspect an element with a Tailwind class)
- [ ] Custom theme values work: `bg-primary-600`, `font-sans`, `p-18` produce expected output
- [ ] `cn()` combines classes without conflicts (test: `cn("px-2", "px-4")` should output only `px-4`)
- [ ] Dark mode toggles correctly (click toggle, verify `<html class="dark">` and `dark:` styles apply)
- [ ] TypeScript shows no errors in configuration or components (`npx tsc --noEmit`)
- [ ] Production build purges unused styles (`npm run build` completes without errors)
- [ ] Accessibility: keyboard flow works, focus is visible, contrast meets WCAG 2.2, touch targets are adequate
- [ ] Responsive: no text overlap or layout shift across desktop and mobile viewports

## UI/UX Quality Checklist (2026)

- User can complete the core task quickly and repeatedly.
- UI supports keyboard, screen readers, visible focus, and sufficient contrast (WCAG 2.2).
- Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
- Controls use familiar affordances and expose state clearly.
- Motion is purposeful and respects `prefers-reduced-motion`.
- Visual direction is intentional and consistent with the product domain.
- All component states implemented: empty, loading, success, error, disabled, validation, permission, offline, long-content.

## Related Skills

- `scaffold-nextjs-app` — project scaffolding before Tailwind configuration
- `deploy-to-vercel` — deploying the application with styles

## References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material Design 3: https://m3.material.io/
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html
