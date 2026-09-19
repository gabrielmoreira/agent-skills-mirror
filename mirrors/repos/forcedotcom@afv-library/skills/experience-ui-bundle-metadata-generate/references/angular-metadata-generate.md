# Angular UI Bundle Scaffold

Reference for the **Angular** path of `experience-ui-bundle-metadata-generate`. Use this to scaffold the bundle, then return to the "After generation" steps in `SKILL.md`.

## Scaffold command

Always pass `--template angularbasic` to scaffold an Angular bundle:

```bash
# Run from SFDX project root. The CLI creates the bundle under
# force-app/main/default/uiBundles/<AppName>/ — verify this before continuing.
sf template generate ui-bundle -n CoffeeBoutique --template angularbasic
```

Pass `--output-dir` to generate at a different location. If you do, pass that same path to `verify-bundle-location.sh` in the verification step.

## What the scaffold produces

An Angular (TypeScript, standalone components) app under `force-app/main/default/uiBundles/<AppName>/`:

- **Entry HTML:** `src/index.html` (NOT the bundle root), mounting `<app-root>` and carrying a `<base href="/">`.
- **App entry:** `src/main.ts`; `src/app/app.ts` + `src/app/app.html`, `src/app/app.config.ts`, `src/app/app.routes.ts`; pages under `src/app/pages/`.
- **Build:** Angular CLI driven by `angular.json` with the `@angular-builders/custom-esbuild:application` builder. Salesforce integration (API-version substitution, org proxy, Live Preview / `SFDC_ENV` / base-href injection) is wired via the esbuild plugin + `middleware/` — no `vite.config.ts`.
- **Build output:** the builder's `outputPath.browser` is flattened to `dist/`, matching `ui-bundle.json` `outputDir: "dist"` — same as React.

## Default boilerplate to replace

Replace every stock string before shipping — searching for these is the fastest way to find them:

- `<title>MyAngularApp</title>` in `src/index.html` → a real product title.
- Default `<app-root>` welcome/landing markup in `src/app/app.html` and any placeholder page stubs under `src/app/pages/`.
- Placeholder navigation and empty routes (see `experience-ui-bundle-frontend-generate`).

## Notes

- **Dev-server port / CSP:** the Angular bundle's dev server is `sf-angular-serve` (the `package.json` `dev` script, provided by `@salesforce/angular-plugin-ui-bundle`), whose default port is `5173` — the same as React's Vite default — overridable with `SF_UIBUNDLE_PORT`. No Angular-specific CSP Trusted Site change is needed for local dev vs React.
- **Element/binding syntax:** Angular uses `<app-root>` and standalone components with native control flow (`@if` / `@for`) — not JSX. This only matters when authoring pages; the metadata and config files below are framework-neutral.
