---
applyTo: "dashboard/**"
---

# Dashboard Development Instructions

## Stack

- **HTML**: Semantic, accessible, no framework
- **CSS**: Vanilla CSS, mobile-first responsive
- **JS**: Alpine.js for reactive state, plain `<script>` tags for logic (global scope)
- **No build step**: Files served as-is

## Patterns

- Dashboard state in `app.js` via `dashboardApp()` Alpine component
- Each monitor module exports pure render/check functions (global scope)
- Config stored in localStorage via `config-panel.js`
- Health checks return `{ status, message, timestamp }` objects

## File Size

≤100 lines per file. Split modules by concern:
- `health-check.js` — Ollama/OpenClaw connectivity
- `quota-tracker.js` — Free-tier API quota monitoring
- `device-monitor.js` — Tailscale mesh device status

## Styling

- CSS custom properties for theming (dark mode default)
- Grid/flexbox for layout
- Status colors: green (#3fb950), yellow (#d29922), red (#f85149), blue (#58a6ff)
