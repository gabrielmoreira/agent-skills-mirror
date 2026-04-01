# OpenAkita Setup Center

Desktop GUI and web configuration center for OpenAkita, built with Tauri 2.x + React 18.

## Tech Stack

- **UI**: React 18 + TypeScript (strict mode off)
- **Build**: Vite 6
- **Desktop Shell**: Tauri 2.x (Rust, in `src-tauri/`)
- **i18n**: i18next + react-i18next (en/zh)
- **Markdown**: react-markdown + remark-gfm + rehype-highlight

## Dev Commands

```bash
npm run dev          # Vite dev server (Tauri mode)
npm run dev:web      # Vite dev server (web-only mode, no Tauri)
npm run build        # Production build (Tauri)
npm run build:web    # Production build (web, output: dist-web/)
npm run tauri dev    # Full Tauri desktop app
```

## Project Structure

```
src/
  App.tsx             # Main app with routing, multi-agent toggle
  views/              # Page views (ChatView, AgentManagerView, MCPView, etc.)
  components/         # Shared UI components
  hooks/              # React hooks
  i18n/               # Internationalization (en.json, zh.json)
  platform/           # Platform abstraction layer (Tauri vs Web)
src-tauri/            # Rust backend for Tauri
  src/main.rs         # Tauri entry point
  tauri.conf.json     # Tauri config
dist-web/             # Web build output (bundled into pip package)
```

## Key Conventions

- **Platform abstraction**: Use `platform/` APIs for filesystem, dialogs, and process operations — never import `@tauri-apps/*` directly in views.
- **i18n keys**: All user-facing text must use `t('key')` from react-i18next. Add keys to both `en.json` and `zh.json`.
- **API calls**: Backend API is at `http://localhost:{port}/api/`. Port comes from Tauri env or defaults to 16185.
- **Web build**: `dist-web/` is committed and bundled into the Python pip package. Run `npm run build:web` after frontend changes.
- **No CSS framework**: Styles are plain CSS, component-scoped where possible.
