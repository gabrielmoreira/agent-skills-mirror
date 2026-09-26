# AI Frontmatter Studio

## Project Context

- This is a CommonJS VS Code extension for visually editing `*.agent.md` frontmatter.
- Read [README.md](README.md) for the user-facing MVP scope and official documentation links.
- There is no build step; the extension entry point is `src/extension.js`.

## Commands

- Run `npm test` for the Node.js native test suite.
- Run `npm run lint` for syntax checks across `src/*.js` and `test/*.test.js`.

## Code Boundaries

- Keep YAML parsing, state normalization, validation, and serialization in `src/frontmatter.js`.
- Keep asset categories and discovery in `src/assets/assetProvider.js`.
- Keep artifact adapters in `src/artifacts/`; an adapter owns the semantic contract for one artifact type and delegates shared agent rules to `frontmatter.js` where appropriate.
- Keep shared webview lifecycle and file I/O in `src/editors/artifactEditor.js`.
- Keep artifact-specific editor commands in `src/editors/<artifact>Editor.js` and artifact-specific browser rendering in `media/artifacts/<artifact>/editor.js`.
- Keep `src/extension.js` limited to activation, registrations, and event wiring.
- Add behavior tests in `test/frontmatter.test.js` when changing parsing, validation, or serialization.

## Frontmatter Invariants

- Preserve parse/serialize round trips, including unknown keys in `extraPropertiesYaml`.
- Treat `tools` and `agents` as three modes: selected, all (`*`), and none (`[]`).
- Preserve explicit `false` values and intentional empty arrays where serialization supports them.
- Validate all state before writing a file; validation returns accumulated errors rather than only the first error.
- Keep structured YAML shape rules: `mcp-servers` is an array, `hooks` and extra properties are objects.
- When agents are configured, tools must include `agent` or allow all tools.

## Extension Workflow

- Agents are the editable asset category; other discovered asset types open as regular files.
- Webview messages are untyped input. Check `message.type`, validate state, then serialize and write through the VS Code workspace filesystem API.
- Preserve the existing glob exclusions and deduplication behavior when changing asset discovery.
- Keep the extension compatible with the declared VS Code engine and CommonJS module style.
- Adding a new artifact type should add a catalog entry, adapter, editor module, and renderer while reusing the shared webview shell.

## Change Discipline

- Prefer focused changes that preserve the public state shape and existing UI workflow.
- Update or add tests for behavior changes before broad refactoring.
- Run both `npm test` and `npm run lint` after edits.