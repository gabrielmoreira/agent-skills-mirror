# CLAUDE.md

This file provides guidance to AI coding assistants (e.g., Claude Code, GitHub Copilot, Cursor) when working with this repository.

## Project Overview

Nanobrowser is an open-source AI web automation Chrome extension that runs multi-agent systems locally in the browser. It's a free alternative to OpenAI Operator with support for multiple LLM providers (OpenAI, Anthropic, Gemini, Ollama, etc.).

## Development Commands

**Package Manager**: Always use `pnpm` 10.34.6 (pinned in `package.json`). Use Node.js 24 LTS; any global pnpm 10+ (or `corepack enable`) switches to the pinned version, and `engines` refuses pnpm 9 and npm. `.npmrc` sets `minimum-release-age=1920`, so pnpm refuses package versions published less than 32 hours ago.

**Core Commands**:

- `pnpm install` - Install dependencies
- `pnpm dev` - Start WXT development mode with page HMR and extension reloads
- `pnpm build` - Build the Chromium MV3 extension with WXT
- `pnpm type-check` - Regenerate i18n types and `.wxt/`, then run TypeScript type checking
- `pnpm lint` - Run ESLint with auto-fix
- `pnpm prettier` - Format code with Prettier

**Testing**:

- `pnpm zip` - Build and create an extension zip for distribution
- `pnpm test` - Run unit tests (Vitest)
  - Targeted example: `pnpm test -t "Sanitizer"`

Targeted examples (fast path):
- `pnpm exec eslint src/side-panel/components/ChatInput.tsx` — lint a file without auto-fix
- `pnpm exec prettier --write src/side-panel` — format a directory

**Cleaning**:

- `pnpm clean` - Remove build outputs (`dist/`, `dist-zip/`, `.wxt/`)
- `pnpm clean:node_modules` - Remove dependencies
- `pnpm clean:install` - Clean node_modules and reinstall dependencies
- `pnpm update-version` - Update the version in `package.json`

## Architecture

This is a **single pnpm package** built by **WXT**, with WXT's default layout at the repo root.

### Project Structure

- `wxt.config.ts` - Manifest, Vite settings, aliases, and build hooks
- `entrypoints/` - Thin wrappers importing the background, content, side panel, and options source
- `public/` - Static files copied into the build: icons, `permission/`, `buildDomTree.js`, and `_locales/`
- `src/background/` - Background service worker with multi-agent system
  - `src/background/agent/` - AI agent implementations (Navigator, Planner, Validator)
  - `src/background/browser/` - Browser automation and DOM manipulation
  - `src/background/llm/` - AI SDK provider setup, structured generation, and LLM error handling
- `src/side-panel/` - Main chat interface (React + TypeScript + Tailwind)
- `src/options/` - Extension settings page (React + TypeScript)
- `src/content/` - Content script for page injection
- `src/storage/` - Chrome extension storage abstraction (`@extension/storage`); LLM providers and default models are defined in `src/storage/lib/settings/types.ts`
- `src/i18n/` - Internationalization (`@extension/i18n`)
- `src/ui/` - Shared React components and the `withUI` Tailwind helper (`@extension/ui`)
- `src/shared/` - Common hooks, HOCs, and utilities (`@extension/shared`)
- `scripts/zip.ts` - Zips `dist/` into `dist-zip/`

### Multi-Agent System

The core AI system consists of three specialized agents:

- **Navigator** - Handles DOM interactions and web navigation
- **Planner** - High-level task planning and strategy
- **Validator** - Validates task completion and results

Agent logic is under `src/background/agent/`.

### Build System

- **WXT** uses Vite to bundle every entrypoint, including shared code, directly from source
- `@extension/*` imports are aliases to `src/<name>` defined in `wxt.config.ts`; `vitest.config.mts` repeats them, so update both when adding an alias
- **TypeScript** with strict configuration; the root `tsconfig.json` extends the generated `.wxt/tsconfig.json` for alias paths only
- **ESLint** + **Prettier** for code quality

### Key Technologies

- **Chrome Extension Manifest V3**
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **WXT** with Vite for extension bundling and development
- **Puppeteer** for browser automation
- **Chrome APIs** for browser automation
- **Vercel AI SDK v7** (`ai` + `@ai-sdk/*` providers) for LLM integration, isolated in `src/background/llm/`

## Development Notes

- Extension loads as unpacked from `dist/` directory after build
- WXT uses Vite HMR for pages and reloads the extension for background/content changes
- Load `dist/` unpacked manually; the browser runner is disabled in `web-ext.config.ts`
- Shared code under `src/` is bundled from source, so `pnpm dev` hot-updates it without a rebuild
- Locale edits during `pnpm dev` regenerate the i18n types, and WXT copies `public/_locales` and reloads the extension
- WXT is pinned to 0.21.4 because the config compensates for version-specific behavior; verify these hooks on upgrades
- Background scripts run as service workers (Manifest V3)
- Content scripts inject into web pages for DOM access
- Multi-agent coordination happens through Chrome messaging APIs
- Distribution zips are written to `dist-zip/`
- Use `pnpm dev` for development and `pnpm build` for production; Vite sets `import.meta.env.DEV`.
- Do not edit generated outputs: `dist/**`, `.wxt/**`, `src/i18n/lib/type.ts`

## Unit Tests

- Framework: Vitest
- Location/naming: `src/**/__tests__` with `*.test.ts`
- Run: `pnpm test`
- Targeted example: `pnpm test -t "Sanitizer"`
- Prefer fast, deterministic tests; mock network/browser APIs

## Testing Extension

After building, load the extension:

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `dist/` directory

## Internationalization (i18n)

### Key Naming Convention

Follow the structured naming pattern: `component_category_specificAction_state`

**Semantic Prefixes by Component:**

- `bg_` - Background service worker operations
- `exec_` - Executor/agent execution lifecycle
- `act_` - Agent actions and web automation
- `errors_` - Global error messages
- `options_` - Settings page components
- `chat_` - Chat interface elements
- `nav_` - Navigation elements
- `permissions_` - Permission-related messages

**State-Based Suffixes:**

- `_start` - Action beginning (e.g., `act_goToUrl_start`)
- `_ok` - Successful completion (e.g., `act_goToUrl_ok`)
- `_fail` - Failure state (e.g., `exec_task_fail`)
- `_cancel` - Cancelled operation
- `_pause` - Paused state

**Error Categorization:**

- `_errors_` subcategory for component-specific errors
- Global `errors_` prefix for system-wide errors
- Descriptive error names (e.g., `act_errors_elementNotExist`)

**Command Structure:**

- `_cmd_` for command-related messages (e.g., `bg_cmd_newTask_noTask`)
- `_setup_` for configuration issues (e.g., `bg_setup_noApiKeys`)

### Usage

```typescript
import { t } from '@extension/i18n';

// Simple message
t('bg_errors_noTabId')

// With placeholders
t('act_click_ok', ['5', 'Submit Button'])
```

### Placeholders

Use Chrome i18n placeholder format with proper definitions:

```json
{
  "act_goToUrl_start": {
    "message": "Navigating to $URL$",
    "placeholders": {
      "url": {
        "content": "$1",
        "example": "https://example.com"
      }
    }
  }
}
```

**Guidelines:**

- Use descriptive, self-documenting key names
- Separate user-facing strings from internal/log strings
- Follow hierarchical naming for maintainability
- Add placeholders with examples for dynamic content
- Group related keys by component prefix

### Generation

- Do not edit the generated `src/i18n/lib/type.ts`.
- The generator `src/i18n/generate-i18n.mjs` (re)generates it on `pnpm install`,
  `pnpm type-check`, `pnpm build`, and locale changes during `pnpm dev`.
  Edit source locale JSON in `public/_locales/**` instead.

## Code Quality Standards

### Development Principles

- **Simple but Complete Solutions**: Write straightforward, well-documented code that fully addresses requirements
- **Modular Design**: Structure code into focused, single-responsibility modules and functions
- **Testability**: Design components to be easily testable with clear inputs/outputs and minimal dependencies
- **Type Safety**: Leverage TypeScript's type system for better code reliability and maintainability

### Code Organization

- Extract reusable logic into utility functions or shared packages
- Use dependency injection for better testability
- Keep functions small and focused on a single task
- Prefer composition over inheritance
- Write self-documenting code with clear naming

### Style & Naming

- Formatting via Prettier (2 spaces, semicolons, single quotes,
  trailing commas, `printWidth: 120`)
- ESLint rules include React/Hooks/Import/A11y + TypeScript
- Components: `PascalCase`; variables/functions: `camelCase`;
  directories: `kebab-case`
- Enforced rule: `@typescript-eslint/consistent-type-imports`
  (use `import type { ... } from '...'` for type-only imports)

### Quality Assurance

- Run `pnpm type-check` before committing to catch TypeScript errors
- Use `pnpm lint` to maintain code style consistency
- Write unit tests for business logic and utility functions
- Test UI components in isolation when possible

### Security Guidelines

- **Input Validation**: Always validate and sanitize user inputs, especially URLs, file paths, and form data
- **Credential Management**: Never log, commit, or expose API keys, tokens, or sensitive configuration
- **Content Security Policy**: Respect CSP restrictions and avoid `eval()` or dynamic code execution
- **Permission Principle**: Request minimal Chrome extension permissions required for functionality
- **Data Privacy**: Handle user data securely and avoid unnecessary data collection or storage
- **XSS Prevention**: Sanitize content before rendering, especially when injecting into web pages
- **URL Validation**: Validate and restrict navigation to prevent malicious redirects
- **Error Handling**: Avoid exposing sensitive information in error messages or logs
 - **Secrets/Config**: Use `.env.local` (git‑ignored) and prefix variables with `VITE_`.
   Example: `VITE_POSTHOG_API_KEY`. Vite loads `VITE_*` from the repo root.

## Important Reminders

- Always use `pnpm` package manager (required for this project)
- Node.js version: 24 LTS recommended; `package.json` engines sets the minimum (`>=24.11.0`, the first 24 LTS)
- `engine-strict=true` is enabled in `.npmrc`; non-matching engines fail install
- Extension builds to `dist/` directory which is loaded as unpacked extension
- Zipped distributions are written to `dist-zip/`
- Only supports Chrome/Edge 
- Keep diffs minimal and scoped; avoid mass refactors or reformatting unrelated files
- Do not modify generated artifacts (`dist/**`, `.wxt/**`, the generated `src/i18n/lib` files)
  or global configs (`wxt.config.ts`, `tsconfig.json`, `package.json` scripts)
  without approval
 - Run checks before committing: `pnpm type-check`, `pnpm lint`, `pnpm test`,
   and `pnpm build` if applicable
- Vite aliases: `@root` is the repo root, `@src` is `src/`, and `@extension/{storage,i18n,ui,shared}`
  are `src/<name>` (see `wxt.config.ts`). Page code uses relative imports.
  Keep WXT entrypoints thin and reuse existing page/background source.
 - Only use scripts defined in `package.json`; do not invent new commands
 - Change policy: ask first for new deps, file renames/moves/deletes, or
   global config changes; allowed without asking: read/list files,
   lint/format/type-check/test/build, and small focused patches
 - Reuse existing building blocks: `src/ui` components and the page
   Tailwind configs instead of re-implementing
