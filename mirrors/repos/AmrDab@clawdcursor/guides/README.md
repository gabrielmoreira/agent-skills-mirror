# Clawd Cursor App Guides — moved

> **The JSON guides are now at `src/llm/knowledge/guides/`.** This directory used to hold contributor-submitted guides at the repo root, but nothing in the live code path loaded them. In v0.9.0 they were migrated into the bundled package so the loader at `src/llm/knowledge/loader.ts` actually finds them.

## Where to add a new guide

1. Create `src/llm/knowledge/guides/{app-key}.json` — use the lowercase **app key** (not the process name), e.g. `notepad.json`, `mspaint.json`, `vscode.json`. The key is what `detectApp()` returns from `src/llm/knowledge/domain-map.ts` for that app.
2. If your app isn't covered by `DOMAIN_MAP` (web URLs) or `TITLE_FALLBACKS` (process names / window titles) yet, add a row in `domain-map.ts` so `detectApp()` resolves to your key.
3. Build (`npm run build`) — `postbuild.ts` copies the JSONs into `dist/llm/knowledge/guides/` for the shipped binary.

## Guide format

App guides are LLM context, not deterministic scripts. The loader injects them into the agent's system prompt so the model has the right keyboard shortcuts, workflow shapes, and known failure modes at decision time. The agent still reasons — guides just feed it richer data than "look at the screen and improvise."

```json
{
  "app": "Microsoft Excel",
  "processNames": ["EXCEL", "excel"],
  "domainHints": ["sheets.google.com"],
  "shortcuts": {
    "new_workbook": "Ctrl+N",
    "save": "Ctrl+S"
  },
  "workflows": {
    "create_table": "Click cell A1. Type headers with Tab between columns. Enter for next row.",
    "save_as": "Press Ctrl+Shift+S. Navigate to folder. Type filename. Click Save."
  },
  "layout": {
    "ribbon": "Top toolbar with tabs (Home, Insert, Page Layout, etc.)",
    "workspace": "Grid of cells below the ribbon — this is where you type data"
  },
  "tips": [
    "Tab moves right, Enter moves down. Shift+Tab moves left.",
    "For simple tables, type directly into cells. Don't use Insert > Table."
  ]
}
```

Two workflow shapes are supported:

- **Prose string** (this README's example): a single sentence per workflow. Reads naturally for the LLM, no execution semantics.
- **Structured step array** (see `gmail.json`, `outlook.json`): list of typed steps (`pressKey`, `wait`, `typeAtFocus`, `verify`). The LLM still reads them as context; a future template-runner could execute them deterministically.

Pick whichever fits the app. Both ship and load the same way.

## Contributing

1. Add `src/llm/knowledge/guides/{key}.json`
2. If the app isn't title-/domain-detectable yet, add a row in `domain-map.ts`
3. PR
