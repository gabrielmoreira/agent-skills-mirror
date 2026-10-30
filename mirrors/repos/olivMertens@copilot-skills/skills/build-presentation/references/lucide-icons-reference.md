# Lucide Icons Reference

Quick reference for the most useful Lucide outline icons (ISC license, free, no attribution required).
**Source:** <https://lucide.dev>

## How to use in your HTML deck

1. Browse <https://lucide.dev> or search below for the icon name you need
2. Copy the SVG path data from this reference or from lucide.dev
3. Embed in your HTML slide as an inline `<svg>` element:

```html
<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
  <!-- Paste the path data here -->
  <path d="M12 2a10 10 0 1 0 20 0"/>
</svg>
```

The CSS class `.icon` handles:
- Sizing: 2.1cqw (about 27px at 1280px slide width)
- Stroke: 1.7px width with round caps and joins
- Color: inherits `var(--azure)` or `var(--amber)` from container
- Never uses fill; outline only

## Concepts & workflow

| Concept | Icon name | SVG path | Use case |
|---------|-----------|----------|----------|
| **Data/Storage** | `Database` | `<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/>` | Database, storage, record |
| | `Server` | `<rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6" y1="6" y2="18"/>` | Backend system, compute |
| **Process** | `Workflow` | `<rect width="8" height="8" x="3" y="3" rx="2" ry="2"/><path d="M7 11h10a2 2 0 0 1 2 2v.5"/><rect width="8" height="8" x="13" y="13" rx="2" ry="2"/>` | Orchestration, pipeline |
| **AI/Agent** | `Bot` | `<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><path d="M9 11a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><circle cx="12" cy="19" r="2"/>` | Agent, AI actor |
| **Communication** | `MessageSquare` | `<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>` | Conversational channel |
| | `MessageCircle` | `<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12c0 1.6.406 3.109 1.121 4.424L2 22l6.59-1.121A10 10 0 0 0 12 22z"/>` | Chat, messaging |
| **Security/Control** | `ShieldCheck` | `<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>` | Governance, approved |
| | `KeyRound` | `<path d="M2.586 13.314A4.172 4.172 0 0 0 2 15.673v2.03a1 1 0 0 0 1 1h1"/><path d="M16 6a4 4 0 1 1-8 0 4 4 0 0 1 8 0z"/><circle cx="12" cy="10" r="2"/>` | Access, authentication |
| **Search/Discovery** | `FileSearch` | `<path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><circle cx="11.5" cy="14.5" r="2.5"/>` | Search, find, evidence |
| | `Search` | `<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>` | Search, lookup |
| **Audit/Time** | `History` | `<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>` | Audit trail, timeline |
| | `Clock` | `<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 15 15"/>` | Time, duration, schedule |
| **Validation/Check** | `UserCheck` | `<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><path d="m15 9 2 2 4-4"/>` | Human review, approval |
| | `CheckCircle2` | `<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>` | Confirmed, done |
| **Action/Energy** | `Zap` | `<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>` | Action, power, energy |
| | `Cog` | `<circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M4.22 19.78l4.24-4.24m4.24-4.24l4.24-4.24"/>` | Settings, config, system |
| **Status/Trend** | `TrendingUp` | `<polyline points="23 6 13.5 15.5 8.5 10.5 1 17"/><polyline points="17 6 23 6 23 12"/>` | Growth, success, positive |
| | `AlertCircle` | `<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>` | Warning, alert, risk |
| **Connection** | `GitBranch` | `<line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>` | Branch, fork, split |
| | `Link2` | `<path d="M9 17H7a5 5 0 0 1 0-10h2"/><path d="M15 7h2a5 5 0 0 1 0 10h-2"/>` | Link, connection, dependency |

## Decorative/UI elements

| Element | Icon name | SVG path | Use case |
|---------|-----------|----------|----------|
| **Navigation** | `ArrowRight` | `<path d="M5 12h14M12 5l7 7-7 7"/>` | Next, forward, direction |
| | `ArrowLeft` | `<path d="M19 12H5m7-7-7 7 7 7"/>` | Previous, back |
| | `ChevronRight` | `<polyline points="9 18 15 12 9 6"/>` | Collapse/expand, disclosure |
| | `Home` | `<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>` | Home, start |
| **Display** | `Maximize2` | `<polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" x2="3" y1="3" y2="21"/>` | Fullscreen, expand |
| | `X` | `<line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/>` | Close, dismiss |
| | `Menu` | `<line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="18" y2="18"/>` | Menu, hamburger |
| **Media** | `Play` | `<polygon points="5 3 19 12 5 21 5 3"/>` | Play, start, next |
| | `Pause` | `<rect width="4" height="16" x="6" y="4"/><rect width="4" height="16" x="14" y="4"/>` | Pause, stop |
| | `Volume2` | `<polygon points="11 5 6 9 2 9 2 15 6 15 11 19V5"/><path d="M15.54 8.46a6.5 6.5 0 0 1 0 9.07"/>` | Volume, audio, mute |

## Special notes

- **Accessibility:** Use `aria-hidden="true"` on purely decorative icons. For meaningful diagrams, add a `<title>` or use `aria-label`.
- **Color:** Icons inherit stroke color from their container or CSS class. Use `--azure` (main), `--amber` (contrast/governance), `--success` (confirmed).
- **Sizing:** The `.icon` class scales responsively with `cqw` units on the slide. At 1280px width, `.icon` is ~27px.
- **Offline:** No CDN call needed. Copy the SVG path and embed inline for offline-first delivery.
- **License:** ISC (free, commercial use OK, no attribution required). But always credit Lucide in your project if publicly shared.

## Getting more icons

For additional icons beyond this reference:
1. Visit <https://lucide.dev>
2. Use the search box to find the concept (e.g., "upload", "download", "settings")
3. Click to copy the SVG path data
4. Paste into your HTML with `viewBox="0 0 24 24"` and stroke styles

**Tips for icon selection:**
- Prefer single words that describe the concept (not emoji)
- Use consistent style within a deck (all outline, no filled)
- Keep labels alongside icons; never rely on icon alone for meaning
