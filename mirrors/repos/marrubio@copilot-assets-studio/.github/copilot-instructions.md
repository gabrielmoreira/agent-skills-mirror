# Copilot Assets Studio instructions

## Project and commands

- This is a CommonJS VS Code extension targeting VS Code `^1.106.0`; `src/extension.js` only activates the extension, registers commands, and refreshes the asset tree.
- There is no build step. Install dependencies with `npm install`, run the complete native Node.js suite with `npm test`, and run syntax checks with `npm run lint`.
- Run one test file with `node --test test/frontmatter.test.js`. Run one named test with `node --test --test-name-pattern="parseAgentDocument loads official" test/frontmatter.test.js`.
- For manual verification, open the repository in VS Code and press `F5` to launch an Extension Development Host. Package with `npx --yes @vscode/vsce package`.
- Releases run `npm ci`, `npm test`, and `npm run lint`; the release tag must be `v` followed by the `package.json` version.

## Architecture

- `src/assets/assetProvider.js` owns the sidebar catalog and workspace discovery. `CATEGORY_DEFINITIONS` is the source of truth for categories, glob patterns, editability, and open commands. Discovery excludes `node_modules`, deduplicates files across patterns, and sorts by filesystem path.
- The extension supports four editable artifacts: agents (`*.agent.md`), skills (`SKILL.md`), prompts (`*.prompt.md`), and instructions (`*.instructions.md`). Each `src/artifacts/<kind>Artifact.js` adapter defines its semantic contract: parser, validator, serializer, initial state, renderer, and optional webview data/diagnostics.
- `src/editors/artifactEditor.js` is the shared editor shell. It reads the document, builds a CSP-protected webview from the shared HTML/CSS/preview/token scripts plus the artifact renderer, and handles webview messages. It must validate incoming untyped save state through the adapter before writing with `vscode.workspace.fs`.
- `src/editors/<kind>Editor.js` owns artifact-specific open/create commands and default file locations. `src/editors/frontmatterEditor.js` routes the generic Markdown command by path/name first, then infers `.copilot` Markdown from frontmatter.
- `src/frontmatter.js` is the central state contract for parsing, normalization, validation, and YAML serialization. `media/artifacts/<kind>/editor.js` is browser-side rendering only: it mutates the state supplied by the host and sends messages; it must stay aligned with the state shape from `frontmatter.js`.
- `media/webview/markdownPreview.js` and `media/webview/tokenCounter.js` are injected into every editor. Token estimates are UTF-8 bytes divided by four and rounded up; they are approximate section counts, not model billing.

## Frontmatter and UI contracts

- Preserve parse/serialize round trips, especially unknown YAML keys in `extraPropertiesYaml`, explicit `false` booleans, and supported intentional empty arrays. YAML frontmatter must remain an object.
- Agent `tools` and `agents` each have three distinct modes: selected values, all (`['*']`), and none (`[]`). Do not collapse these representations. If agents are configured, tools must include `agent` or allow all tools.
- Instruction frontmatter recognizes optional `name`, `description`, and `applyTo` fields. Preserve unknown YAML properties in `extraPropertiesYaml`, and do not require optional fields when editing valid instruction files.
- Validate all fields before writes and return accumulated errors. `mcp-servers` must parse to an array; `hooks` and extra properties must parse to objects. Invalid original YAML is reported through `validationError` and should not be silently normalized into a clean form.
- Use `getAgentDiagnostics` for agent validation because it combines errors with non-blocking advice, including unknown properties and the cloud instruction-body limit. Skill and prompt validation remain separate because their contracts differ.
- The webview state and all messages are untyped input. Check `message.type`; only use recognized messages (`save`, `estimateTokens`, `diagnose`, `openSource`, `openDoc`) and ensure any new message path validates or safely handles its payload.
- Escape values inserted into generated HTML and retain the template CSP/nonce model. `getArtifactEditorHtml` serializes initial JSON with `<` escaped because it is embedded in a script element.
- When adding an artifact type, add a discovery catalog entry, an adapter, an artifact-specific editor module, and a browser renderer, while reusing the shared artifact editor shell.

## Tests

- Add parsing, normalization, validation, or serialization coverage to `test/frontmatter.test.js`.
- `test/tokenEstimate.test.js` covers the shared estimator and malformed-draft fallback behavior.
- `test/markdownPreview.test.js` executes injected webview scripts in a VM; update it when changing the shared webview template, injected scripts, or renderer assumptions.
- Prompt files remain editable and creatable for compatibility, but the prompt editor must retain its non-blocking deprecation notice recommending migration of reusable prompts to agent skills.
