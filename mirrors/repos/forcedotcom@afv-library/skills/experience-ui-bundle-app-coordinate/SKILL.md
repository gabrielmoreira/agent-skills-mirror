---
name: experience-ui-bundle-app-coordinate
description: "MUST activate when the user wants to build, create, or generate a React application, React app, web application, single-page application (SPA), or frontend application — even if no project files exist yet. MUST also activate when the project contains a uiBundles/*/src/ directory or sfdx-project.json and the prompt says create, build, construct, or generate a new app, site, or page from scratch — even if the prompt also describes visual styling. MUST also activate when the task spans more than one ui-bundle skill. Use this skill when building a complete app end-to-end. Do NOT use for Lightning Experience apps with custom objects (use platform-lightning-app-coordinate). Do NOT use for single-concern edits to an existing page (use experience-ui-bundle-frontend-generate)."
metadata:
  version: "1.0"
  relatedSkills: experience-ui-bundle-metadata-generate, experience-ui-bundle-features-generate, experience-ui-bundle-salesforce-data-access, experience-ui-bundle-frontend-generate, experience-ui-bundle-agentforce-client-generate, experience-ui-bundle-file-upload-generate, experience-ui-bundle-deploy, experience-ui-bundle-site-generate, experience-ui-bundle-custom-app-generate
---

# Building a UI Bundle App

## Overview

Build a complete, deployable Salesforce React UI bundle application from a natural language description by orchestrating specialized UI bundle skills in correct dependency order. Each skill **MUST** be explicitly loaded before executing its phase.

## When to Use This Skill

**Use when:**

- User requests a "React app", "UI bundle", "web app", or "full-stack app" on Salesforce
- User says "build an app", "create an application" and the context implies a non-LWC based frontend (e.g. React)
- The work produces a complete UI bundle with scaffolding, features, data access, and UI -- not a single component in isolation

**Examples that should trigger this skill:**

- "Build a React app for managing customer cases with Salesforce data"
- "Create a UI bundle for an employee directory with search and navigation"
- "I need a full-stack React app with authentication, data tables, and file uploads"
- "Build a coffee shop ordering app on Salesforce"

**Do NOT use when:**

- Creating a single page or component (use `experience-ui-bundle-frontend-generate`)
- Only installing a feature (use `experience-ui-bundle-features-generate`)
- Only setting up data access (use `experience-ui-bundle-salesforce-data-access`)
- Only deploying an existing app (use `experience-ui-bundle-deploy`)
- Building a Lightning Experience app with custom objects and metadata (use `platform-lightning-app-coordinate`)
- Troubleshooting or debugging an existing UI bundle

---

## Dependency Graph & Build Order

### Phase 1: Scaffolding (Foundation)

```text
UI Bundle scaffold (sf template generate ui-bundle)
    v
Install dependencies (npm install)
    v
Bundle metadata (uibundle-meta.xml, ui-bundle.json)
    v
CSP Trusted Sites (if external domains needed)
```

Creates the UI bundle directory structure, meta XML, and optional routing/headers config. All subsequent phases require the scaffold to exist.

### Phase 2: Features (Optional)

```text
Search project code (src/) for existing implementations
    v
Install dependencies (npm install)
    v
Search, describe, and install features (auth, shadcn, search, navigation, GraphQL)
    v
Resolve conflicts (two-pass: --on-conflict error, then --conflict-resolution)
    v
Integrate __example__ files into target files, then delete them
```

Installs pre-built, tested feature packages. Skip if the app requires no pre-built features. Always check for an existing feature before building from scratch. Features provide the foundation that UI components build on top of.

### Phase 3: Data Access (Backend Wiring)

```text
Ground every entity/field against the org (per experience-ui-bundle-salesforce-data-access)
    v
Generate queries/mutations FROM the verified names (never from guessed fields)
    v
Generate types (npm run graphql:codegen) and wire into components
    v
Validate and test (npx eslint, ask user before testing mutations)
```

Sets up the data layer using the **`@salesforce/platform-sdk`** Data SDK (`createDataSDK().graphql`).
GraphQL is preferred for record operations; REST for Connect, Apex, or UI API endpoints. **The
`experience-ui-bundle-salesforce-data-access` skill owns the grounding + authoring workflow — load it and follow
it; do not substitute a local-schema grep or guessed field names.** Grounding happens against the
**live org**, so it does not require a local `schema.graphql` to be present.

### Phase 4: UI (Frontend)

```text
Layout, navigation, header, and footer (appLayout.tsx)
    v
Pages (routed views)
    v
Components (widgets, forms, tables)
```

Builds the React UI. References the data layer from Phase 3 and the features from Phase 2. Must replace all boilerplate and placeholder content.

### Phase 5: Integrations (Optional)

```text
Agentforce chat widget (if requested)
File upload API (if requested)
```

These are independent and can be executed in parallel if both are needed.

### Phase 6: Deployment

```text
Org authentication
    v
Pre-deploy UI bundle build (npm install + npm run build)
    v
Deploy metadata
    v
Post-deploy configuration (permissions, profiles, named credentials, connected apps, custom settings, flow activation)
    v
Import data (if data plan exists)
    v
Fetch GraphQL schema and run codegen
*(Re-fetches schema from the deployed org -- required because the remote schema may differ from the local one used in Phase 3)*
    v
Final UI bundle build (rebuilds with the deployed schema)
```

Follows the canonical 7-step deployment sequence. Must deploy metadata before fetching schema. Must assign permissions before schema fetch.

### Phase 7: Hosting Target

Choose **one** of the following based on the app's audience:

#### Phase 7a: Experience Site (External)

```text
Resolve site properties (siteName, appDevName, etc.)
    v
Generate site metadata (Network, CustomSite, DigitalExperience)
    v
Deploy site infrastructure
```

Creates the Digital Experience site that hosts the UI bundle. Use when the user wants a public-facing or authenticated site URL for external users.

#### Phase 7b: Custom Application (Internal)

```text
Resolve app properties (appName, appNamespace, appLabel)
    v
Generate CustomApplication metadata (applications/*.app-meta.xml)
    v
Add <target>CustomApplication</target> to .uibundle-meta.xml
    v
Deploy custom application
```

Creates a Custom Application entry in the Lightning App Launcher. Use when the app is for internal users accessing it within Lightning Experience.

---

## Execution Workflow

### STEP 1: Requirements Analysis & Planning

**Actions:**

1. Parse the user's natural language request
2. Identify the app name and purpose
3. Extract pages and navigation structure
4. Identify data entities and Salesforce objects needed
5. Detect feature requirements (authentication, search, file upload, chat)
6. Determine if an Experience Site is needed
7. Identify external domains for CSP registration

> **The plan MUST contain an explicit grounding step before any query authoring.** Do not list
> guessed object/field names as settled facts and defer verification to codegen. The data-access
> portion of the plan must read: "verify these entities/fields against the org (via
> `experience-ui-bundle-salesforce-data-access`), then author queries from the verified names." A plan that
> authors queries first and codegens later is the failure mode that produces guessed fields and
> hand-stubbed types — do not emit it.

**Output: Build Plan**

```text
UI Bundle App Build Plan: [App Name]

SCAFFOLDING:
- App name: [PascalCase name]
- Routing: [SPA rewrites, trailing slash config]
- External domains: [domains needing CSP registration]

FEATURES:
- [list of features to install: auth, shadcn, search, navigation, etc.]

DATA ACCESS:
- Objects: [Salesforce objects to query/mutate]
- Grounding: [verify each object + its fields against the org via experience-ui-bundle-salesforce-data-access BEFORE authoring — list the objects/fields to confirm, not assumed-correct names]
- Queries: [GraphQL queries to author FROM the verified names]
- REST endpoints: [only where GraphQL/uiapi genuinely cannot cover it — not as a fallback for fields that were hard to verify]

UI:
- Layout: [description of app shell/navigation]
- Pages: [list of pages with routes]
- Components: [key components per page]
- Design direction: [aesthetic/style intent]

INTEGRATIONS (if applicable):
- Agentforce chat: [yes/no, agent ID if known]
- File upload: [yes/no, record linking pattern]

DEPLOYMENT:
- Target org: [org alias if known]
- Hosting target: [Experience Site / Custom Application / none]

SKILL LOAD ORDER:
1. experience-ui-bundle-metadata-generate
2. experience-ui-bundle-features-generate (if features needed)
3. experience-ui-bundle-salesforce-data-access (if data access needed)
4. experience-ui-bundle-frontend-generate
5a. experience-ui-bundle-agentforce-client-generate (if chat requested)
5b. experience-ui-bundle-file-upload-generate (if file upload requested)
6. experience-ui-bundle-deploy
7a. experience-ui-bundle-site-generate (if Experience Site requested -- external users)
7b. experience-ui-bundle-custom-app-generate (if Custom Application requested -- internal users)
```

### STEP 2: Per-Phase Execution

Execute each phase sequentially. Complete all steps within a phase before moving to the next. For each phase:

| Step | What to do | Why |
|------|-----------|-----|
| **1. Load skill** | Invoke the skill (e.g., via the Skill tool) for this phase | Gives you the current rules, patterns, constraints, and implementation guides |
| **2. Execute** | Follow the loaded skill's workflow to generate code/config | The skill defines HOW to do the work correctly |
| **3. Verify** | Run lint and build from the UI bundle directory | Catch errors before moving to the next phase |
| **4. Checkpoint** | Confirm phase completion before proceeding | Ensures dependencies are satisfied for the next phase |

**Do NOT skip step 1 (loading the skill).** Even if you remember the skill's content, skills evolve. Always load the current version.

---

**Phase 1 -- Scaffolding**
- 1. Load skill: Invoke `experience-ui-bundle-metadata-generate`
- 2. Execute: Run `sf template generate ui-bundle`, install dependencies (`npm install`), configure meta XML, ui-bundle.json, and CSP trusted sites
- 3. Verify: Confirm directory structure and metadata files exist
- 4. Checkpoint: UI bundle scaffold is ready -- proceed to Phase 2

**Phase 2 -- Features** (skip if no pre-built features needed)
- 1. Load skill: Invoke `experience-ui-bundle-features-generate`
- 2. Execute: Install dependencies, search and install features, integrate example files
- 3. Verify: Run `npm run build` to confirm features integrate cleanly
- 4. Checkpoint: Features installed -- proceed to Phase 3

**Phase 3 -- Data Access** (skip if no Salesforce data needed)
- 1. Load skill: Invoke `experience-ui-bundle-salesforce-data-access`
- 2. Execute: **Ground entities/fields against the org first** (per the skill), then author queries/mutations **from the verified names**, run codegen, wire into components. Never guess fields or hand-edit generated types.
- 3. Verify: Run `npx eslint` on files with GraphQL queries
- 4. Checkpoint: Data layer ready -- proceed to Phase 4

**Phase 4 -- UI**
- 1. Load skill: Invoke `experience-ui-bundle-frontend-generate`
- 2. Execute: Build layout, pages, components, navigation. Replace all boilerplate.
- 3. Verify: Run lint and build -- 0 errors required
- 4. Checkpoint: UI complete -- proceed to Phase 5

**Phase 5 -- Integrations** (skip if not requested)
- 1. Load skill(s): Invoke `experience-ui-bundle-agentforce-client-generate` (5a) and/or `experience-ui-bundle-file-upload-generate` (5b). If both are needed, they are independent and can be executed in parallel.
- 2. Execute: Follow each skill's workflow to add the integration
- 3. Verify: Run lint and build
- 4. Checkpoint: Integrations complete -- proceed to Phase 6

**Phase 6 -- Deployment**
- 1. Load skill: Invoke `experience-ui-bundle-deploy`
- 2. Execute: Follow the 7-step deployment sequence (auth, build, deploy, permissions, data, schema, final build)
- 3. Verify: Confirm deployment succeeds and app is accessible
- 4. Checkpoint: App deployed -- proceed to Phase 7 if needed

**Phase 7a -- Experience Site** (skip if not requested or if Custom Application chosen)
- 1. Load skill: Invoke `experience-ui-bundle-site-generate`
- 2. Execute: Resolve properties, generate site metadata, deploy
- 3. Verify: Confirm site URL is accessible
- 4. Checkpoint: Site live -- build complete

**Phase 7b -- Custom Application** (skip if not requested or if Experience Site chosen)
- 1. Load skill: Invoke `experience-ui-bundle-custom-app-generate`
- 2. Execute: Resolve app properties, generate CustomApplication metadata, add CustomApplication target to meta XML
- 3. Verify: Confirm app appears in App Launcher
- 4. Checkpoint: App registered -- build complete

### STEP 3: Final Summary

After all phases complete, present a build summary:

```text
UI Bundle App Build Complete: [App Name]

PHASES COMPLETED:
[x] Phase 1: Scaffolding -- [app name] UI bundle created
[x] Phase 2: Features -- [list of features installed, or "skipped"]
[x] Phase 3: Data Access -- [list of entities wired up]
[x] Phase 4: UI -- [count] pages, [count] components
[x] Phase 5: Integrations -- [list or "none"]
[x] Phase 6: Deployment -- deployed to [org]
[x] Phase 7: Hosting Target -- [Experience Site URL / Custom Application name / "skipped"]

FILES GENERATED:
[list key files and their paths]

NEXT STEPS:
[any manual steps the user should take]
```

---

## Validation

Before presenting the build as complete, verify:

- [ ] **Scaffold exists**: UI bundle directory with valid meta XML and ui-bundle.json
- [ ] **Dependencies installed**: `node_modules/` exists and `package.json` has expected packages
- [ ] **Build passes**: `npm run build` produces `dist/` with no errors
- [ ] **Lint passes**: `npx eslint src/` reports 0 errors
- [ ] **No boilerplate**: All placeholder text, default titles, and template content has been replaced
- [ ] **Navigation works**: `appLayout.tsx` has real nav items matching created pages
- [ ] **Data layer wired**: Components use the `@salesforce/platform-sdk` Data SDK (`createDataSDK().graphql`), with all entities/fields grounded against the org — not guessed (if data access phase was executed)
- [ ] **CSP registered**: All external domains have CSP Trusted Site metadata (if applicable)

---

## Error Handling

### Category 1: Stop and Ask User

- App purpose is too vague to determine pages or data needs
- User wants features that conflict (e.g., "no authentication" + "show user-specific data")
- Target org is unknown and deployment is requested

### Category 2: Log Warning, Continue

- A feature install has minor conflicts (resolve and continue)
- Optional integration setup encounters non-blocking issues
- Build has non-error warnings

---

## Best Practices

### 1. Always Follow Phase Order

Never build UI before installing features. Never deploy before building. Dependencies are strict.

### 2. Replace All Boilerplate

Every generated app must feel purpose-built. Replace "React App" titles, "Vite + React" placeholders, and all default content with real app-specific text and branding.

### 3. Design with Intent

Follow the design thinking and frontend aesthetics guidance from `experience-ui-bundle-frontend-generate`. Every app should have a clear visual direction -- not generic defaults.
