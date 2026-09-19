# React UI Bundle Scaffold

Reference for the **React** path of `experience-ui-bundle-metadata-generate`. Use this to scaffold the bundle, then return to the "After generation" steps in `SKILL.md`.

## Scaffold command

Always pass `--template reactbasic` to scaffold a React/Vite bundle:

```bash
# Run from SFDX project root. The CLI creates the bundle under
# force-app/main/default/uiBundles/<AppName>/ — verify this before continuing.
sf template generate ui-bundle -n CoffeeBoutique --template reactbasic
```

Pass `--output-dir` to generate at a different location. If you do, pass that same path to `verify-bundle-location.sh` in the verification step.

## What the scaffold produces

A React + Vite (TypeScript) app under `force-app/main/default/uiBundles/<AppName>/`:

- **Entry HTML:** `index.html` at the bundle root, mounting `<div id="root">` and loading `src/app.tsx`.
- **App entry:** `src/app.tsx`; pages under `src/pages/`, components under `src/components/`.
- **Toolchain:** `vite.config.ts`, `package.json`, shadcn/ui primitives, Tailwind, GraphQL client + `codegen.yml`.
- **Build output:** `dist/` (matches `ui-bundle.json` `outputDir: "dist"`).

## Default boilerplate to replace

Replace every stock string before shipping — searching for these is the fastest way to find them:

- `<title>Welcome to React App</title>` in `index.html` → a real product title.
- Any "React App" / "Vite + React" placeholder copy and default hero/landing text.
- Placeholder navigation and empty page stubs (see `experience-ui-bundle-frontend-generate`).
