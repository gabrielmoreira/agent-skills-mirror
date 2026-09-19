# React UI Bundle Features

Framework reference for the **React** path of `experience-ui-bundle-features-generate`. Read
this alongside the workflow spine in `SKILL.md`. The `@salesforce/ui-bundle-features` CLI
installs the React variant of each feature into a React/Vite UI bundle (`"react"` in the
bundle `package.json`, `.tsx` sources under `src/`).

## Example files

Features ship integration examples under `__examples__/` as **`.tsx`** files — often full,
working pages with concrete names (e.g. `AccountSearch.tsx`), not bare stubs. Integrate the
pattern into the target file named in `describe` output, then verify before deleting the
`__examples__/` dir.

## Files features may rewrite

React features commonly touch the app shell and routing:

- `src/appLayout.tsx` — the app layout/shell
- `src/routes.tsx` — route registration
- `src/App.tsx` — app entry (some features mount here)

These are the paths to expect as conflicts in the two-pass conflict flow; resolve them per
`SKILL.md` → *Conflict Handling* (the exact paths are whatever the CLI prints).

## Mount the feature's entry component

Mount the OOTB component the feature ships rather than hand-rolling a parallel one. For search,
mount the feature's `<Search>` component (JSX) on the search-results page:

```tsx
import { Search } from "./features/search";      // path per describe output
// ...
export default function SearchResults() {
  return <Search />;                              // do NOT hand-roll a results page
}
```

## Build & verify

Build command (run from the UI bundle dir):

```bash
npm run build
```

Worked grep for the *verify-before-delete* check (adjust the symbol to one from the example
you integrated — here the `SearchInput`/`useSearch` pattern integrated into a page):

```bash
grep -q "SearchInput\|useSearch" src/pages/*.tsx src/components/*.tsx 2>/dev/null || {
  echo "ERROR: Pattern from example not found in target files - integration incomplete"
  echo "Do NOT delete __examples__/ until the pattern is confirmed present"
  exit 1
}
```

Only `rm -rf __examples__/` after the build passes **and** this grep confirms the pattern is
present in the target.
