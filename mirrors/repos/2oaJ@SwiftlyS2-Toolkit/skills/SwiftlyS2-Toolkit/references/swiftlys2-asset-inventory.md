# SwiftlyS2-Toolkit Asset Inventory

This inventory explains the **public assets** in the current `.github/` that are directly related to the SwiftlyS2 engineering workflow.

## 1. Core assets

### Skill
- `skills/SwiftlyS2-Toolkit/SKILL.md`

### Prompts
- `prompts/SwiftlyS2-Toolkit-Plan.prompt.md`
- `prompts/SwiftlyS2-Toolkit-Audit.prompt.md`
- `prompts/SwiftlyS2-Toolkit-Edit.prompt.md`

### References
- `skills/SwiftlyS2-Toolkit/references/swiftlys2-plugin-playbook.md`
- `skills/SwiftlyS2-Toolkit/references/swiftlys2-kb-index.md`
- `skills/SwiftlyS2-Toolkit/references/swiftlys2-official-docs-map.md`
- `skills/SwiftlyS2-Toolkit/references/swiftlys2-asset-inventory.md`

### Templates / Assets
- `skills/SwiftlyS2-Toolkit/assets/README.md`
- `skills/SwiftlyS2-Toolkit/assets/development/getting-started/partial-plugin-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/development/using-attributes/attribute-registration-checklist.md`
- `skills/SwiftlyS2-Toolkit/assets/development/swiftly-core/core-service-entrypoints.md`
- `skills/SwiftlyS2-Toolkit/assets/development/commands/command-attribute-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/development/commands/command-service-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/development/menus/menu-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/development/netmessages/protobuf-handler-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/development/native-functions-and-hooks/hook-handler-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/development/thread-safety/thread-sensitivity-checklist.md`
- `skills/SwiftlyS2-Toolkit/assets/development/profiler/hotpath-gc-checklist.md`
- `skills/SwiftlyS2-Toolkit/assets/development/entity/schema-write-checklist.md`
- `skills/SwiftlyS2-Toolkit/assets/development/core-events/lifecycle-checklist.md`
- `skills/SwiftlyS2-Toolkit/assets/development/scheduler/scheduler-vs-worker-guide.md`
- `skills/SwiftlyS2-Toolkit/assets/development/shared-api/shared-interface-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/development/game-events/game-events-usage-notes.md`
- `skills/SwiftlyS2-Toolkit/assets/development/configuration/README.md`
- `skills/SwiftlyS2-Toolkit/assets/development/translations/README.md`
- `skills/SwiftlyS2-Toolkit/assets/development/permissions/README.md`
- `skills/SwiftlyS2-Toolkit/assets/guides/dependency-injection/di-service-plugin-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/guides/dependency-injection/service-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/guides/terminologies/README.md`
- `skills/SwiftlyS2-Toolkit/assets/guides/html-styling/README.md`
- `skills/SwiftlyS2-Toolkit/assets/patterns/background-workers/worker-template.cs.md`
- `skills/SwiftlyS2-Toolkit/assets/workflows/planning/method-level-plan-template.md`
- `skills/SwiftlyS2-Toolkit/assets/workflows/audit/audit-report-template.md`

### Toolkit Docs
- `skills/SwiftlyS2-Toolkit/README.md`

### Workspace Layer
- `.github/copilot-instructions.md`
- `.github/knowledge-base.md`

## 2. Counting scope

- Skill: 1
- Prompts: 3
- References: 4
- Templates / Assets: 26
- Toolkit README: 1
- Workspace Layer: 2

**Total: 37 core assets**

## 3. Layering principles

### Public layer

The following content is suitable for public distribution with the toolkit:

- Skill
- General prompts
- General references
- General templates and checklists

### Workspace layer

The following content is used to hold workspace-specific customization information:

- `copilot-instructions.md`
- `knowledge-base.md`

These files may record:

- current workspace project mappings
- local reference repository paths
- workspace-specific build commands
- current maintainer-team constraints

But this information should not be written back into public skills / prompts / templates.

## 4. Naming conventions

The current general toolkit uses the following naming strategy:

- skill / prompt / reference files consistently use the `swiftlys2-` prefix
- assets use the pattern “directories carry semantics, filenames carry responsibility”, preferably named by official Development / Guides categories
- this improves discoverability and avoids repeating long prefixes in deep asset paths

## 5. Maintenance suggestions

- When adding new general SwiftlyS2 tools, prefer placing them in the current toolkit structure and keep the `swiftlys2-` prefix
- If the new document is for a one-off task, it should stay separate from the public toolkit
- If local paths, workspace-specific project names, or personal repository names leak into public docs, move them back into `copilot-instructions.md` or `knowledge-base.md`
