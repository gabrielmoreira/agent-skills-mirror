---
name: shadcn
description: "Manages shadcn/ui as copied source: npx shadcn add/search/docs/info, registry items, design-system presets, and updates that preserve local edits. Use when adding, styling, composing, or documenting shadcn components in a supported framework. Not for maintaining a private npm component library or rewriting Tailwind from scratch; never hardcode import aliases — read them from shadcn info."
version: 1.0.1
---

# shadcn/ui

A framework for building UI, components, and design systems. Components are added as source code to the user's project via the CLI.

> **IMPORTANT:** Run all CLI commands using the project's package runner: `npx shadcn@latest`, `pnpm dlx shadcn@latest`, or `bunx --bun shadcn@latest` — based on the project's `packageManager`. Examples below use `npx shadcn@latest` but substitute the correct runner for the project.

## When to Use

- Adding new components from shadcn/ui or community registries (`@magicui`, `@bundui`, `@tailark`, etc.).
- Styling, composing, or debugging existing shadcn/ui components.
- Initializing a new project or switching design system presets.
- Retrieving component documentation, examples, and API references.
- Updating installed components from upstream while preserving local changes.

## Prerequisites

- Node.js and a compatible package manager (`npm`, `pnpm`, `yarn`, or `bun`) installed on the host.
- For existing projects: a supported framework (Next.js, Vite, Remix, Astro, React Router, Laravel, or Start).
- Windows host is primary (PowerShell). All commands below work in PowerShell unless noted.

## Procedure

### 1. Get Project Context

Run the info command to inspect the current project configuration and installed components:

```bash
npx shadcn@latest info --json
```

The JSON output contains the project config and installed components. Key fields to reference:

| Field | Purpose |
|---|---|
| `aliases` | Actual alias prefix for imports (e.g. `@/`, `~/`). Never hardcode. |
| `isRSC` | When `true`, components using `useState`, `useEffect`, event handlers, or browser APIs need `"use client"` at the top of the file. |
| `tailwindVersion` | `"v4"` uses `@theme inline` blocks; `"v3"` uses `tailwind.config.js`. |
| `tailwindCssFile` | The global CSS file where custom CSS variables are defined. Always edit this file, never create a new one. |
| `style` | Component visual treatment (e.g. `nova`, `vega`). |
| `base` | Primitive library (`radix` or `base`). Affects component APIs and available props. |
| `iconLibrary` | Determines icon imports. Use `lucide-react` for `lucide`, `@tabler/icons-react` for `tabler`, etc. Never assume `lucide-react`. |
| `resolvedPaths` | Exact file-system destinations for components, utils, hooks, etc. |
| `framework` | Routing and file conventions (e.g. Next.js App Router vs Vite SPA). |
| `packageManager` | Use this for any non-shadcn dependency installs (e.g. `pnpm add date-fns` vs `npm install date-fns`). |

See `cli.md` for the full field reference. Load this file when you need detailed CLI flag or field documentation.

### 2. Check Installed Components

Before running `add`, always check the `components` list from project context or list the `resolvedPaths.ui` directory. Don't import components that haven't been added, and don't re-add ones already installed.

### 3. Find Components

```bash
npx shadcn@latest search
npx shadcn@latest search @shadcn -q "sidebar"
npx shadcn@latest search @tailark -q "stats"
```

### 4. Get Docs and Examples

**When creating, fixing, debugging, or using a component, always run `npx shadcn@latest docs` and fetch the URLs first.** This ensures you're working with the correct API and usage patterns rather than guessing.

```bash
npx shadcn@latest docs button dialog select
```

Use `npx shadcn@latest view` to browse registry items you haven't installed:

```bash
npx shadcn@latest view @shadcn/button
```

### 5. Install or Update Components

```bash
# Add components.
npx shadcn@latest add button card dialog
npx shadcn@latest add @magicui/shimmer-button
npx shadcn@latest add --all

# Preview changes before adding/updating.
npx shadcn@latest add button --dry-run
npx shadcn@latest add button --diff button.tsx
npx shadcn@latest add @acme/form --view button.tsx
```

When updating existing components, use `--dry-run` and `--diff` to preview changes first (see [Updating Components](#updating-components) below).

### 6. Fix Imports in Third-Party Components

After adding components from community registries (e.g. `@bundui`, `@magicui`), check the added non-UI files for hardcoded import paths like `@/components/ui/...`. These won't match the project's actual aliases. Use `npx shadcn@latest info` to get the correct `ui` alias (e.g. `@workspace/ui/components`) and rewrite the imports accordingly. The CLI rewrites imports for its own UI files, but third-party registry components may use default paths that don't match the project.

### 7. Review Added Components

After adding a component or block from any registry, **always read the added files and verify they are correct**. Check for:

- Missing sub-components (e.g. `SelectItem` without `SelectGroup`).
- Missing imports or incorrect composition.
- Violations of the [Critical Rules](#critical-rules).
- Icon imports that don't match the project's `iconLibrary` (e.g. registry item uses `lucide-react` but project uses `hugeicons` — swap the imports and icon names accordingly).

Fix all issues before moving on.

### 8. Registry Must Be Explicit

When the user asks to add a block or component, **do not guess the registry**. If no registry is specified (e.g. user says "add a login block" without specifying `@shadcn`, `@tailark`, etc.), ask which registry to use. Never default to a registry on behalf of the user.

### 9. Initialize a New Project

```bash
# Create a new project.
npx shadcn@latest init --name my-app --preset base-nova
npx shadcn@latest init --name my-app --preset a2r6bw --template vite

# Create a monorepo project.
npx shadcn@latest init --name my-app --preset base-nova --monorepo
npx shadcn@latest init --name my-app --preset base-nova --template next --monorepo

# Initialize existing project.
npx shadcn@latest init --preset base-nova
npx shadcn@latest init --defaults  # shortcut: --template=next --preset=base-nova
```

**Named presets:** `base-nova`, `radix-nova`

**Templates:** `next`, `vite`, `start`, `react-router`, `astro` (all support `--monorepo`) and `laravel` (not supported for monorepo)

**Preset codes:** Base62 strings starting with `a` (e.g. `a2r6bw`), from [ui.shadcn.com](https://ui.shadcn.com).

**Never decode or fetch preset codes manually.** Pass them directly to `npx shadcn@latest init --preset <code>`.

### 10. Switching Presets

Ask the user first: **reinstall**, **merge**, or **skip**?

- **Reinstall**: `npx shadcn@latest init --preset <code> --force --reinstall`. Overwrites all components.
- **Merge**: `npx shadcn@latest init --preset <code> --force --no-reinstall`, then run `npx shadcn@latest info` to list installed components, then for each installed component use `--dry-run` and `--diff` to smart merge it individually.
- **Skip**: `npx shadcn@latest init --preset <code> --force --no-reinstall`. Only updates config and CSS, leaves components as-is.

### Updating Components

When the user asks to update a component from upstream while keeping their local changes, use `--dry-run` and `--diff` to intelligently merge. **NEVER fetch raw files from GitHub manually — always use the CLI.**

1. Run `npx shadcn@latest add <component> --dry-run` to see all files that would be affected.
2. For each file, run `npx shadcn@latest add <component> --diff <file>` to see what changed upstream vs local.
3. Decide per file based on the diff:
   - No local changes → safe to overwrite.
   - Has local changes → read the local file, analyze the diff, and apply upstream updates while preserving local modifications.
   - User says "just update everything" → use `--overwrite`, but confirm first.
4. **Never use `--overwrite` without the user's explicit approval.**

## Critical Rules

These rules are **always enforced**. Each links to a reference file with Incorrect/Correct code pairs. Load the relevant reference file when working on a component in that category.

### Styling & Tailwind → `rules/styling.md`

- **`className` for layout, not styling.** Never override component colors or typography.
- **No `space-x-*` or `space-y-*`.** Use `flex` with `gap-*`. For vertical stacks, `flex flex-col gap-*`.
- **Use `size-*` when width and height are equal.** `size-10` not `w-10 h-10`.
- **Use `truncate` shorthand.** Not `overflow-hidden text-ellipsis whitespace-nowrap`.
- **No manual `dark:` color overrides.** Use semantic tokens (`bg-background`, `text-muted-foreground`).
- **Use `cn()` for conditional classes.** Don't write manual template literal ternaries.
- **No manual `z-index` on overlay components.** Dialog, Sheet, Popover, etc. handle their own stacking.

### Forms & Inputs → `rules/forms.md`

- **Forms use `FieldGroup` + `Field`.** Never use raw `div` with `space-y-*` or `grid gap-*` for form layout.
- **`InputGroup` uses `InputGroupInput`/`InputGroupTextarea`.** Never raw `Input`/`Textarea` inside `InputGroup`.
- **Buttons inside inputs use `InputGroup` + `InputGroupAddon`.**
- **Option sets (2–7 choices) use `ToggleGroup`.** Don't loop `Button` with manual active state.
- **`FieldSet` + `FieldLegend` for grouping related checkboxes/radios.** Don't use a `div` with a heading.
- **Field validation uses `data-invalid` + `aria-invalid`.** `data-invalid` on `Field`, `aria-invalid` on the control. For disabled: `data-disabled` on `Field`, `disabled` on the control.

### Component Structure → `rules/composition.md`

- **Items always inside their Group.** `SelectItem` → `SelectGroup`. `DropdownMenuItem` → `DropdownMenuGroup`. `CommandItem` → `CommandGroup`.
- **Use `asChild` (radix) or `render` (base) for custom triggers.** Check `base` field from `npx shadcn@latest info`. → `rules/base-vs-radix.md`
- **Dialog, Sheet, and Drawer always need a Title.** `DialogTitle`, `SheetTitle`, `DrawerTitle` required for accessibility. Use `className="sr-only"` if visually hidden.
- **Use full Card composition.** `CardHeader`/`CardTitle`/`CardDescription`/`CardContent`/`CardFooter`. Don't dump everything in `CardContent`.
- **Button has no `isPending`/`isLoading`.** Compose with `Spinner` + `data-icon` + `disabled`.
- **`TabsTrigger` must be inside `TabsList`.** Never render triggers directly in `Tabs`.
- **`Avatar` always needs `AvatarFallback`.** For when the image fails to load.

### Use Components, Not Custom Markup → `rules/composition.md`

- **Use existing components before custom markup.** Check if a component exists before writing a styled `div`.
- **Callouts use `Alert`.** Don't build custom styled divs.
- **Empty states use `Empty`.** Don't build custom empty state markup.
- **Toast via `sonner`.** Use `toast()` from `sonner`.
- **Use `Separator`** instead of `<hr>` or `<div className="border-t">`.
- **Use `Skeleton`** for loading placeholders. No custom `animate-pulse` divs.
- **Use `Badge`** instead of custom styled spans.

### Icons → `rules/icons.md`

- **Icons in `Button` use `data-icon`.** `data-icon="inline-start"` or `data-icon="inline-end"` on the icon.
- **No sizing classes on icons inside components.** Components handle icon sizing via CSS. No `size-4` or `w-4 h-4`.
- **Pass icons as objects, not string keys.** `icon={CheckIcon}`, not a string lookup.

## Key Patterns

```tsx
// Form layout: FieldGroup + Field, not div + Label.
<FieldGroup>
  <Field>
    <FieldLabel htmlFor="email">Email</FieldLabel>
    <Input id="email" />
  </Field>
</FieldGroup>

// Validation: data-invalid on Field, aria-invalid on the control.
<Field data-invalid>
  <FieldLabel>Email</FieldLabel>
  <Input aria-invalid />
  <FieldDescription>Invalid email.</FieldDescription>
</Field>

// Icons in buttons: data-icon, no sizing classes.
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

// Spacing: gap-*, not space-y-*.
<div className="flex flex-col gap-4">  // correct
<div className="space-y-4">           // wrong

// Equal dimensions: size-*, not w-* h-*.
<Avatar className="size-10">   // correct
<Avatar className="w-10 h-10"> // wrong

// Status colors: Badge variants or semantic tokens, not raw colors.
<Badge variant="secondary">+20.1%</Badge>    // correct
<span className="text-emerald-600">+20.1%</span> // wrong
```

## Component Selection

| Need | Use |
|---|---|
| Button/action | `Button` with appropriate variant |
| Form inputs | `Input`, `Select`, `Combobox`, `Switch`, `Checkbox`, `RadioGroup`, `Textarea`, `InputOTP`, `Slider` |
| Toggle between 2–5 options | `ToggleGroup` + `ToggleGroupItem` |
| Data display | `Table`, `Card`, `Badge`, `Avatar` |
| Navigation | `Sidebar`, `NavigationMenu`, `Breadcrumb`, `Tabs`, `Pagination` |
| Overlays | `Dialog` (modal), `Sheet` (side panel), `Drawer` (bottom sheet), `AlertDialog` (confirmation) |
| Feedback | `sonner` (toast), `Alert`, `Progress`, `Skeleton`, `Spinner` |
| Command palette | `Command` inside `Dialog` |
| Charts | `Chart` (wraps Recharts) |
| Layout | `Card`, `Separator`, `Resizable`, `ScrollArea`, `Accordion`, `Collapsible` |
| Empty states | `Empty` |
| Menus | `DropdownMenu`, `ContextMenu`, `Menubar` |
| Tooltips/info | `Tooltip`, `HoverCard`, `Popover` |

## Principles

1. **Use existing components first.** Use `npx shadcn@latest search` to check registries before writing custom UI. Check community registries too.
2. **Compose, don't reinvent.** Settings page = Tabs + Card + form controls. Dashboard = Sidebar + Card + Chart + Table.
3. **Use built-in variants before custom styles.** `variant="outline"`, `size="sm"`, etc.
4. **Use semantic colors.** `bg-primary`, `text-muted-foreground` — never raw values like `bg-blue-500`.

## Detailed References

Load these files when working on the corresponding area:

- `rules/forms.md` — FieldGroup, Field, InputGroup, ToggleGroup, FieldSet, validation states. Load when building or debugging forms.
- `rules/composition.md` — Groups, overlays, Card, Tabs, Avatar, Alert, Empty, Toast, Separator, Skeleton, Badge, Button loading. Load when composing components.
- `rules/icons.md` — data-icon, icon sizing, passing icons as objects. Load when adding icons to components.
- `rules/styling.md` — Semantic colors, variants, className, spacing, size, truncate, dark mode, cn(), z-index. Load when styling or theming.
- `rules/base-vs-radix.md` — asChild vs render, Select, ToggleGroup, Slider, Accordion. Load when the project uses `base` primitives or you need to know which prop to use.
- `cli.md` — Commands, flags, presets, templates. Load when you need detailed CLI documentation.
- `customization.md` — Theming, CSS variables, extending components. Load when customizing the design system.

## Pitfalls

- **Hardcoded aliases:** Third-party registry components often use `@/components/ui/...` which won't match the project's actual aliases. Always rewrite these imports using the `aliases` field from `npx shadcn@latest info`.
- **Wrong icon library:** Registry items may import from `lucide-react` when the project uses a different `iconLibrary`. Always swap icon imports and names to match the project's configured library.
- **Missing `"use client"` directive:** When `isRSC` is `true`, any component using hooks, event handlers, or browser APIs must have `"use client"` at the top of the file.
- **Overwriting local changes:** Never use `--overwrite` without the user's explicit approval. Always use `--dry-run` and `--diff` first.
- **Fetching raw files from GitHub:** Never do this. Always use the CLI for adding, updating, or viewing components.
- **Guessing the registry:** When the user doesn't specify a registry, ask. Never default to one on their behalf.
- **Using `space-y-*`/`space-x-*`:** Always use `flex` with `gap-*` instead.
- **Missing overlay titles:** Dialog, Sheet, and Drawer always require a Title component for accessibility. Use `className="sr-only"` if visually hidden.
- **Missing `AvatarFallback`:** `Avatar` always needs `AvatarFallback` for when the image fails to load.
- **Manual `z-index` on overlays:** Dialog, Sheet, Popover, etc. handle their own stacking context. Don't override.
- **Raw color values:** Never use `bg-blue-500` or `text-emerald-600`. Use semantic tokens or Badge variants.
- **Editing the wrong CSS file:** Always edit `tailwindCssFile` from project context. Never create a new global CSS file.

## Verification

1. **Verify project context is loaded:**
   ```bash
   npx shadcn@latest info --json
   ```
   Confirm the output includes `aliases`, `resolvedPaths`, `tailwindVersion`, `base`, and `iconLibrary`.

2. **Verify components are installed:**
   ```bash
   npx shadcn@latest info --json
   ```
   Check that the `components` list includes the component you intend to use. Alternatively, list the `resolvedPaths.ui` directory.

3. **Verify docs are accessible:**
   ```bash
   npx shadcn@latest docs button
   ```
   Confirm the output returns documentation, example, and API reference URLs.

4. **Verify dry-run before updates:**
   ```bash
   npx shadcn@latest add button --dry-run
   ```
   Confirm no unexpected files are affected before proceeding.

5. **Verify imports match project aliases:**
   After adding any component (especially from third-party registries), grep the added files for hardcoded `@/components/ui/` paths and confirm they match the project's `aliases` field.

6. **Verify icon imports match `iconLibrary`:**
   Grep added files for icon imports and confirm they use the project's configured icon library, not a default assumption.

7. **Verify no Critical Rule violations:**
   Review added files for: `space-y-*`/`space-x-*` usage, missing Group wrappers, missing overlay Titles, missing `AvatarFallback`, raw color values, manual `z-index` on overlays, and icons with sizing classes inside components.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
