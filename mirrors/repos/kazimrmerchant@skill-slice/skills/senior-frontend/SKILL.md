---
name: senior-frontend
version: 1.1.1
description: "Scaffolds React/Next.js TypeScript apps, generates components/hooks, and audits bundle size via this skill's Python scripts. Use when scaffolding a Next.js or React app, generating components, or analyzing package.json for heavy imports. Not for CSS animation craft (emil-design-eng) or Vercel UI guideline audits (web-interface-guidelines). Never a backend or data-layer skill."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Senior Frontend

Frontend development patterns, performance optimization, and automation tools for React/Next.js applications.

This skill favors a small set of opinionated defaults — TypeScript in `strict` mode, Tailwind design tokens, tree-shakeable dependencies, and accessibility baked in — because the cost of these decisions is paid once at the start, while the cost of retrofitting them grows with every file added. The scripts under `scripts/` exist to make the *correct* path the *fast* path: scaffolding a project, generating a component, or auditing a bundle should take seconds and produce a result you do not have to clean up afterward.

## When to Use

- **Scaffolding a new React or Next.js app.** A generated baseline gives every project the same `strict` tsconfig, lint/format rules, and Tailwind tokens. That consistency removes per-project config bikeshedding and means a reviewer can move between repos without relearning conventions.
- **Generating components or custom hooks.** The generator enforces one predictable file layout (component + optional test + story + barrel export). Predictable structure is what lets both humans and tooling (codemods, import resolvers) reason about the codebase reliably.
- **Analyzing and optimizing bundle size.** Bundle weight is the single largest lever on first-load performance and Core Web Vitals. The analyzer catches heavy dependencies and import anti-patterns *before* they reach users, when fixing them is cheap.
- **Implementing advanced React patterns** such as Compound Components or custom hooks. These patterns keep complex, stateful UI composable and accessible without prop-drilling — reach for them when a widget has several interdependent parts, not for simple leaf components where they add indirection for no gain.
- **Ensuring accessibility and testing.** Accessibility and tests are dramatically cheaper to build in from the first commit than to bolt on later. Treat a missing label or an untested interaction as a defect, not a follow-up.

### When this skill is the wrong tool

- **Backend or server-side data-layer work.** Database access, auth issuance, and infrastructure are different concerns with different failure modes. The generators here assume the React/Next *client* surface, so use a backend-focused skill for those layers.
- **Reaching for heavyweight legacy libraries** like `moment` or a full `lodash` import. They ship large, often unused code and carry ongoing maintenance and security risk. Prefer `date-fns`/`dayjs` for dates and native ES methods or `lodash-es` (with tree-shaking) for utilities. The exception is a codebase already standardized on one — consistency can outweigh a few KB until a planned migration.
- **Shipping Next.js experimental features to production unguarded.** Experimental APIs can change or break between minor releases. Use them only behind a clear upgrade plan and with a fallback, so an upstream change does not become an incident.
- **Skipping accessibility to move faster.** Semantic HTML and correct ARIA are part of "done," not an enhancement. Broken keyboard navigation or missing labels exclude real users and are treated as bugs.

## Prerequisites

- **Python 3.8+** installed and on `PATH` — all scripts under `scripts/` are Python-based.
- **Node.js 18+** and **npm** — required for installing dependencies and running the dev server.
- **Windows host (PowerShell)** is the primary environment. Use backslash paths or forward-slash paths consistently within a single command. On Windows PowerShell, use `python` (not `python3`).

## Procedure

### 1. Project Scaffolding

Generate a new Next.js or React project with TypeScript, Tailwind CSS, and best-practice configurations.

1. Run the scaffolder with your project name and template. The template choice (`nextjs` vs `react`) determines the routing model and build tool — pick `nextjs` for server components and file-based routing, `react` for a lean SPA (React + Vite):

   ```powershell
   python scripts/frontend_scaffolder.py my-app --template nextjs
   ```

2. Add optional features only as you need them. Valid features are `auth`, `api`, `forms`, `testing`, and `storybook`:

   ```powershell
   python scripts/frontend_scaffolder.py dashboard --template nextjs --features auth,api
   ```

   Inspect what a feature brings in before committing:

   ```powershell
   python scripts/frontend_scaffolder.py dashboard --list-features
   ```

   Preview the full file tree without writing to disk (dry run):

   ```powershell
   python scripts/frontend_scaffolder.py dashboard --template nextjs --features auth,api --dry-run
   ```

3. Navigate to the project and install dependencies:

   ```powershell
   cd my-app; npm install
   ```

4. Start the development server and confirm the home page renders before building on top of it:

   ```powershell
   npm run dev
   ```

### 2. Component Generation

Generate React components with TypeScript, tests, and Storybook stories.

1. Generate a **client component** when the UI needs browser-only APIs, state, or event handlers (`'use client'` is added automatically):

   ```powershell
   python scripts/component_generator.py Button --dir src/components/ui
   ```

2. Generate a **server component** when the UI only renders data and needs no interactivity — server components ship zero client JS, the cheaper default in Next.js:

   ```powershell
   python scripts/component_generator.py ProductCard --type server
   ```

3. Generate with test and story files when the component has behavior or visual states worth documenting:

   ```powershell
   python scripts/component_generator.py UserProfile --with-test --with-story
   ```

4. Generate a **custom hook** to extract reusable, stateful logic out of components:

   ```powershell
   python scripts/component_generator.py FormValidation --type hook
   ```

   Preview files with `--dry-run` before anything is written:

   ```powershell
   python scripts/component_generator.py UserProfile --with-test --with-story --dry-run
   ```

### 3. Bundle Analysis

Analyze `package.json` and project structure for bundle optimization opportunities. Run this regularly — regressions creep in one dependency at a time.

1. Run the analyzer on your project (positional argument is the project directory to scan):

   ```powershell
   python scripts/bundle_analyzer.py /path/to/project
   ```

2. Review the health score and issues. A high grade means no urgent action; flagged "heavy dependencies" point to the changes with the biggest payoff. Each entry pairs the cost with a lighter alternative:

   ```
   Bundle Health Score: 75/100 (C)

   HEAVY DEPENDENCIES:
     moment (290KB)
       Alternative: date-fns (12KB) or dayjs (2KB)

     lodash (71KB)
       Alternative: lodash-es with tree-shaking
   ```

3. Apply recommended fixes by replacing heavy dependencies. Prioritize by size saved versus migration effort — swapping `moment` for `date-fns` removes ~280KB and is usually mechanical.

4. Re-run with verbose mode to inspect import patterns (barrel/whole-library imports that defeat tree-shaking):

   ```powershell
   python scripts/bundle_analyzer.py . --verbose
   ```

   For CI gating or scripted checks, request machine-readable output:

   ```powershell
   python scripts/bundle_analyzer.py . --json
   ```

### 4. Advanced React Patterns

#### Compound Components

Use compound components when several parts of a widget must share state but you still want a flexible, declarative markup API. The pattern keeps shared state in a context so the parts coordinate without the parent wiring props through every level.

Key defensive choices in the implementation below:
- Context defaults to `null` (so "used outside the provider" is detectable).
- A single reader hook throws a precise error naming the exact component.
- The markup carries the ARIA wiring a tablist needs.

```tsx
import {
  createContext,
  useContext,
  useId,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { cn } from '@/lib/utils';

interface TabsContextValue {
  activeTab: string;
  selectTab: (id: string) => void;
  baseId: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext(componentName: string): TabsContextValue {
  const context = useContext(TabsContext);
  if (context === null) {
    throw new Error(
      `<Tabs.${componentName}> must be rendered inside a <Tabs> provider.`
    );
  }
  return context;
}

interface TabsProps {
  defaultTab: string;
  children: ReactNode;
}

export function Tabs({ defaultTab, children }: TabsProps): JSX.Element {
  if (!defaultTab) {
    throw new Error('<Tabs> requires a non-empty `defaultTab` id.');
  }

  const baseId = useId();
  const [activeTab, setActiveTab] = useState<string>(defaultTab);

  const value = useMemo<TabsContextValue>(
    () => ({ activeTab, selectTab: setActiveTab, baseId }),
    [activeTab, baseId]
  );

  return <TabsContext.Provider value={value}>{children}</TabsContext.Provider>;
}

interface TabsListProps {
  children: ReactNode;
  'aria-label': string;
}

function TabsList({ children, 'aria-label': ariaLabel }: TabsListProps): JSX.Element {
  return (
    <div role="tablist" aria-label={ariaLabel} className="flex gap-1 border-b">
      {children}
    </div>
  );
}

interface TabProps {
  id: string;
  children: ReactNode;
}

function Tab({ id, children }: TabProps): JSX.Element {
  const { activeTab, selectTab, baseId } = useTabsContext('Tab');
  const isActive = activeTab === id;

  return (
    <button
      type="button"
      role="tab"
      id={`${baseId}-tab-${id}`}
      aria-selected={isActive}
      aria-controls={`${baseId}-panel-${id}`}
      tabIndex={isActive ? 0 : -1}
      onClick={() => selectTab(id)}
      className={cn(
        'px-4 py-2 text-sm font-medium transition-colors',
        isActive
          ? 'border-b-2 border-primary text-foreground'
          : 'text-muted-foreground hover:text-foreground'
      )}
    >
      {children}
    </button>
  );
}

interface TabPanelProps {
  id: string;
  children: ReactNode;
}

function TabPanel({ id, children }: TabPanelProps): JSX.Element | null {
  const { activeTab, baseId } = useTabsContext('Panel');
  if (activeTab !== id) {
    return null;
  }

  return (
    <div
      role="tabpanel"
      id={`${baseId}-panel-${id}`}
      aria-labelledby={`${baseId}-tab-${id}`}
      tabIndex={0}
      className="p-4"
    >
      {children}
    </div>
  );
}

Tabs.List = TabsList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;
```

Usage — ids tie each `Tab` to its `Panel`, and `aria-label` is required by the `TabsList` type:

```tsx
export function AccountTabs(): JSX.Element {
  return (
    <Tabs defaultTab="overview">
      <Tabs.List aria-label="Account sections">
        <Tabs.Tab id="overview">Overview</Tabs.Tab>
        <Tabs.Tab id="billing">Billing</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel id="overview">Account overview content.</Tabs.Panel>
      <Tabs.Panel id="billing">Billing details content.</Tabs.Panel>
    </Tabs>
  );
}
```

#### Custom Hooks

Extract reusable logic into a hook when the same stateful behavior is needed in more than one place, or when a component's logic is complex enough to test independently. The generic `<T>` preserves the caller's type end to end, and the runtime guard rejects delay values that would produce silently wrong behavior.

```tsx
import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, delay: number = 500): T {
  if (!Number.isFinite(delay) || delay < 0) {
    throw new RangeError(
      `useDebounce: \`delay\` must be a finite, non-negative number, received ${String(delay)}.`
    );
  }

  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

Usage inside a component — only the settled value reaches `onSearch`, so a 10-character query triggers one search instead of ten:

```tsx
import { useEffect, useState } from 'react';
import { useDebounce } from '@/hooks/use-debounce';

interface SearchBoxProps {
  onSearch: (query: string) => void;
}

export function SearchBox({ onSearch }: SearchBoxProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const debouncedSearch = useDebounce<string>(searchTerm, 300);

  useEffect(() => {
    const query = debouncedSearch.trim();
    if (query.length > 0) {
      onSearch(query);
    }
  }, [debouncedSearch, onSearch]);

  return (
    <input
      type="search"
      value={searchTerm}
      onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
        setSearchTerm(event.target.value)
      }
      placeholder="Search..."
      aria-label="Search"
      className="w-full rounded-md border px-3 py-2"
    />
  );
}
```

## Pitfalls

- **Defaulting context to an empty object instead of `null`.** An empty-object default lets children render in a broken state silently. Default to `null` and throw a precise error in the reader hook so misuse is caught at the call site, not deep in a child component.
- **Using `any` to silence type errors.** Explicit types end to end (no `any`) is a hard rule. A clear error at the misuse site is far cheaper to debug than corrupted state discovered later. Validate inputs a caller could realistically get wrong and fail loudly with actionable errors.
- **Importing entire libraries (`import _ from 'lodash'`).** Barrel/whole-library imports defeat tree-shaking. This often matters more than the dependency choice itself. Use `lodash-es` with tree-shaking or native ES methods.
- **Shipping `moment` or full `lodash` to production.** `moment` is ~290KB; `date-fns` is ~12KB and `dayjs` is ~2KB. `lodash` is ~71KB; `lodash-es` with tree-shaking ships only what you use. The exception is a codebase already standardized on one — consistency can outweigh a few KB until a planned migration.
- **Shipping Next.js experimental features unguarded.** Experimental APIs can change or break between minor releases. Use them only behind a clear upgrade plan and with a fallback.
- **Skipping accessibility to move faster.** Semantic HTML and correct ARIA are part of "done," not an enhancement. Broken keyboard navigation or missing labels exclude real users and are treated as bugs.
- **Treating a failing or skipped test as a follow-up.** A failing or skipped test is an unfinished change. Fix it before merging.
- **Adding all optional features at scaffold time.** Each feature pulls in real dependencies. Add features on demand to keep the dependency graph honest.
- **Using `python3` on Windows PowerShell.** On Windows, the command is `python`, not `python3`. Verify with `python --version` before running scripts.

## Verification

Run through these checks because each catches a different class of failure the others miss — types confirm the code compiles, the dev server confirms it renders, and accessibility/test passes confirm it works for real users and stays working.

- [ ] Review the generated project structure and configuration files so the baseline matches your team's conventions before you build on it.
- [ ] Run the development server and confirm the application renders and is interactive:

  ```powershell
  npm run dev
  ```

  A clean type-check does not prove the UI works — verify in the browser.

- [ ] Run the bundle analyzer, apply the highest-value fixes (largest size saved for least migration effort), and re-check the score:

  ```powershell
  python scripts/bundle_analyzer.py . --verbose
  ```

- [ ] Exercise the feature across the golden path and edge cases (empty, loading, and error states) to catch regressions early.
- [ ] Verify accessibility: keyboard-only navigation works, interactive elements are labeled, and ARIA roles match the widget pattern.
- [ ] Run the test suite and confirm it passes:

  ```powershell
  npm test
  ```

  A failing or skipped test is an unfinished change, not a follow-up.

- [ ] Review the diff for security and performance issues (unsanitized input, secrets in client code, unnecessary re-renders or heavy imports).

## Related Skills

- **`emil-design-eng`** — animation/motion craft (easing, transform, popover/drawer). Hand off polish-of-feel work; this chair owns scaffold, generators, and bundle analysis.
- **`web-interface-guidelines`** — Vercel UI a11y, CLS, reduced-motion, and Lighthouse execute path. Hand off guideline audits.
- **`shadcn`** — shadcn/ui CLI and component install, not this scaffolder.
