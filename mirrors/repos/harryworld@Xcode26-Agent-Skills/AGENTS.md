# AGENTS.md

## Purpose
- This repository is a documentation skill pack for Xcode 26 era Apple framework updates.
- Content lives in Markdown; there is no compiled source code or app target here.
- When writing, prefer crisp summaries and actionable guidance.

## Repository Layout
- `README.md` explains how to install the skill.
- `xcode-26/SKILL.md` defines the skill metadata and the reference map.
- `xcode-26/references/` holds the detailed topic notes used by agents.
- Images such as `source.png` live at the repo root.

## Build, Lint, Test
- No build system, package manager, or CI config is present in this repo.
- There are no lint or test scripts configured.
- If you need to validate Swift snippets, do it in a host app or scratch Xcode project.
- Prefer manual review: check code blocks compile and match Apple API naming.

### Single Test Execution
- Not applicable; there is no test harness in this repository.
- If a user wants a single test, instruct them to run it in their app target.

## Cursor/Copilot Rules
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found.
- If these appear later, append their guidance here and follow them.

## Documentation Style
- Use Markdown with ATX headings (`#`, `##`, `###`) as seen in reference files.
- Start files with an overview section when writing new topic docs.
- Keep paragraphs short; prefer 1-3 sentences before a list.
- Use bullet lists for features, steps, and callouts.
- Use numbered lists for procedures that must be followed in order.
- Keep line length around 100-120 characters when convenient.
- Use backticks for identifiers, API names, file paths, and commands.
- Place code in fenced blocks with a language tag (usually `swift` or `bash`).
- Avoid fancy typography; stick to ASCII punctuation.
- Prefer neutral, instructional tone; avoid marketing language.

## Skill File Conventions
- Skill files start with YAML front matter (`---`), `name`, and `description`.
- The `name` should match the folder (`xcode-26`) and be lowercase.
- Keep the description action-oriented and mention the supported domains.
- Maintain the "Reference map" section listing all reference docs.
- When adding a new reference doc, update the map in `xcode-26/SKILL.md`.

## Reference Doc Conventions
- Use `## Overview` and `## Basic Implementation` when relevant.
- Use `###` for subtopics such as setup, customization, or testing.
- Include short "Key features" or "Key updates" lists near the top.
- Provide both explanation and code examples when a feature is complex.
- Call out platform availability and OS requirements explicitly.
- Prefer specific API names and modifiers rather than broad prose.
- Note any feature caveats or gotchas as short bullet points.

## Swift Code Snippet Style
- Use Swift 6 idioms unless the feature is older.
- Use `import` statements only for frameworks actually referenced.
- Keep sample code minimal but complete enough to compile.
- Use `UpperCamelCase` for types and `lowerCamelCase` for variables/functions.
- Use trailing closures and shorthand arguments when they aid clarity.
- Prefer `let` over `var` unless mutation is required.
- Use `@MainActor`/`@Observable`/`@Environment` where appropriate and documented.
- Show `Task {}` or `async`/`await` for concurrency examples rather than callbacks.

## Error Handling Guidance
- Use `do`/`try`/`catch` when the API throws; surface meaningful errors in text.
- Mention error types or domains only when relevant to the feature.
- For optional-returning APIs, use `guard let` with a short fallback.
- Avoid silent failures in sample code; show a minimal error path.

## Naming and Terminology
- Use Apple's official framework names (SwiftUI, UIKit, AppKit, WidgetKit).
- Use platform names with correct casing (iOS, iPadOS, macOS, visionOS).
- Use "Liquid Glass" capitalization as seen in reference docs.
- Prefer "App Intents" (plural) and "Foundation Models Framework" naming.
- When referencing APIs, include the module if it helps disambiguate.

## Imports and Module Organization
- Group imports at the top of code blocks; avoid unused imports.
- If multiple frameworks are required, list system frameworks first.
- Avoid third-party frameworks in examples unless explicitly requested.

## Formatting and Layout
- Keep indentation at 4 spaces in Swift code blocks.
- Align chained modifiers vertically when readability improves.
- Use blank lines between conceptual sections in long code samples.
- Avoid overly long chained expressions; split into intermediate `let` bindings.

## Content Accuracy
- Prefer direct guidance based on these reference docs.
- If information is missing, say so and suggest where to look next.
- When summarizing, keep the mapping between feature and framework clear.
- Avoid guessing APIs; if unsure, state the uncertainty.

## Agents Workflow
- For user requests about Xcode 26 features, open the relevant file in `xcode-26/references/`.
- Summarize using the repository's phrasing and terminology.
- If multiple references apply, merge the guidance and note intersections.
- Keep answers short unless the user asks for deep dives.

## Adding New Docs
- Name files using Title-Case words with hyphens, e.g. `SwiftUI-New-Toolbar-Features.md`.
- Place new docs under `xcode-26/references/`.
- Add the file to `xcode-26/SKILL.md` under "Reference map".
- Update `README.md` only if install or usage changes.

## Markdown Quality Checks
- Ensure all headings are properly nested (no skipping levels).
- Verify code fences are closed and language tags are correct.
- Avoid duplicate headings in the same file unless intentional.
- Keep images local when possible and include alt text.

## Suggested Local Validation (Optional)
- Use a scratch Xcode project to compile Swift snippets.
- Run examples on the minimum OS versions mentioned in the docs.
- If validating widgets or StoreKit, use local configuration files as described.

## Known Gaps
- No automated tooling or CI configuration is present.
- No Swift packages, Xcode projects, or tests are included.
- This repo is documentation-first; treat it like a knowledge base.

## Security and Safety
- Do not include real API keys or credentials in examples.
- Avoid writing code that requires private entitlements unless noted.
- Prefer on-device testing recommendations when Apple requires it.

## Update Process
- Keep edits scoped to the topic being addressed.
- Preserve existing structure and wording unless updating for clarity.
- When adding major sections, match the tone of the surrounding document.
- Re-run spelling and grammar checks mentally after edits.

## Attribution and Links
- When linking to Apple docs, use official developer.apple.com URLs.
- Use link text that describes the destination (not "click here").
- Keep reference links at the end of sections when possible.

## Agent Notes
- If the `xcode-26` skill is referenced, load only the needed reference files.
- Mention when guidance is not covered by the current reference set.
- Avoid inventing new APIs; prefer "check the latest docs" if uncertain.

## Maintenance
- Keep this AGENTS.md aligned with repository contents.
- If new tooling appears, update Build/Lint/Test sections first.
- Revisit style guidelines after major content restructuring.

## End
