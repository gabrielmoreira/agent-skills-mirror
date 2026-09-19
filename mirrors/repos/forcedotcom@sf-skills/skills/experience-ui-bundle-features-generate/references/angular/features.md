# Angular UI Bundle Features

Framework reference for the **Angular** path of `experience-ui-bundle-features-generate`. Read
this alongside the workflow spine in `SKILL.md`. The `@salesforce/ui-bundle-features` CLI
installs the Angular variant of each feature into an Angular UI bundle (an `angular.json` at/
above the bundle, `@angular/core` in `package.json`, standalone components as `.ts` + `.html`
pairs under `src/app/`).

## Example files

Features ship integration examples under `__examples__/` as Angular sources — a standalone
component is a **`.ts`** class + its **`.html`** template (e.g. `account-search.ts` +
`account-search.html`), often full working pages, not bare stubs. Integrate the pattern into
the target named in `describe` output, then verify before deleting the `__examples__/` dir.

> Do not assume file names or a `.component` infix — Angular UI bundle starters name
> components without it (`home.ts`, not `home.component.ts`). The `describe` `Copy Operations`
> destination and the copied-in source are the version-matched truth for what was installed.

## Files features may rewrite

Angular features commonly touch app wiring:

- `src/app/app.routes.ts` — route registration (route-based features add routes here)
- `src/app/app.ts` + `src/app/app.html` — root component and its template
- the app-layout component under `src/app/components/layout/` — the shell some features mount into

These are the paths to expect as conflicts in the two-pass conflict flow; resolve them per
`SKILL.md` → *Conflict Handling* (the exact paths are whatever the CLI prints).

## Mount the feature's entry component

Mount the OOTB component the feature ships rather than hand-rolling a parallel one. Angular
mounts by **selector** (in a template) or by **route** (lazy-loaded standalone component) —
use whichever `describe`/README specifies. For search mounted on a results page template:

```html
<!-- search-results.html — use the feature's selector; do NOT hand-roll a results page -->
<sf-search />
```

Or as a route in `src/app/app.routes.ts`:

```ts
export const routes: Routes = [
  { path: "search", loadComponent: () =>
      import("./features/search/search").then((m) => m.Search) },  // path per describe output
];
```

Import the feature's standalone component into whichever component's `imports:` array hosts it.

## Build & verify

Build command (run from the UI bundle dir):

```bash
npm run build
```

Worked grep for the *verify-before-delete* check — Angular splits usage across `.ts` (selector
registration, service imports, route entry) and `.html` (the mounted selector). Adjust the
symbol to one from the example you integrated:

```bash
grep -rq "sf-search\|SearchService" src/app --include='*.ts' --include='*.html' 2>/dev/null || {
  echo "ERROR: Pattern from example not found in target files - integration incomplete"
  echo "Do NOT delete __examples__/ until the pattern is confirmed present"
  exit 1
}
```

Only `rm -rf __examples__/` after the build passes **and** this grep confirms the pattern is
present in the target.
