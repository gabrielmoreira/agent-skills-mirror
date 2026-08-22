# Composite & Layout Requests - Detailed Guide

How to handle any request bigger than a single component - multiple pieces, a region, a full page, an app shell, a wizard. Companion to `SKILL.md` → "Composite & Layout Requests".

The point: **the same five steps apply regardless of domain.** A dashboard shell, an ecommerce product page, a settings screen, a multi-step form, a marketing section, or "a card with X, Y and Z" all decompose the same way. Apply the method and let the catalog be the source of truth.

The mistake to avoid: firing `single_component` / `single_block` ad-hoc and stitching markup as you go. Plan the whole layout first; fetch and integrate one node at a time against that plan.

---

## The method

### 1. Lock cross-cutting constraints first
Resolve anything that applies to the **whole** result before any fetch, because it governs every fetch and edit:
- **Class system** - design tokens vs utilities. Drives `isUtilityBased` / `theme` on every call; keep it identical across the whole build.
- **Shared surfaces / color / spacing / density** - anything the request describes as uniform across regions.
- **Repeated element states** - pinned, selected, active, disabled, collapsed, aligned, icon-only, etc., noted against the element they modify (they change which variant you pick).

Deciding these once prevents inconsistent output halfway through.

### 2. Decompose into a tree
Containers → regions → leaf components. Write it down. Each leaf is one fetch; grouping leaves by region lets you integrate a region at a time. The shape of the method is identical whether the request is two nested elements or a fifty-element page.

### 3. Discover every node - never guess
- **Larger structures** (shells, navbars, headers, full sections, pages) → `blocks_categories()`. If a ready-made block already covers the structure, reuse it as the skeleton instead of hand-building.
- **Individual pieces** → `components_list({ section })`, then `single_component`.
- Resolve **each named element in the request** to a real slug from the tool output. The "Where things tend to live" table below is only a starting point for *which section to open* - the catalog is authoritative, so confirm against its output and never insert an unverified slug.

### 4. Assemble in order - one fetch + integrate at a time
1. **Outermost / skeleton first.** The shell or top container sets the shared surfaces and - importantly - the script/init placement anchors for everything inside it.
2. **Fill inward, region by region, leaf by leaf.** Integrate each fully (HTML, CSS in `<head>`, external scripts at the structural anchor, init before `</body>` - see Integration Rules) before fetching the next.
3. **Honor the locked constraints on every insert.** Keep the classes the MCP returns and change **text only** - except for the specific surfaces/colors/states the user explicitly asked to change.
4. **Plugins once for the page.** Interactive components share the Preline core script - add it and the init per the placement rules a single time; never duplicate the core script. For a plugin's JS API, events, or options, call `component_documentation`.

### 5. Verify
Re-read the request and check every named element, state, and constraint is present. Composite requests are easy to under-deliver; the checklist is the guard. Verify **against the request, not by auditing the generated code** - do not grep the project's CSS to confirm token classes exist, and do not run HTML/AST validators over the result (see SKILL.md → Integration Rules). The markup the MCP returned is valid by construction; the only open question is whether you placed every element the user asked for.

---

## Where things live

A request describes UI in plain language; you still discover the real slug. To route an abstract intent (a whole page/region/shell) to the right blocks branch, and each named element to the right component section, use the generated **[catalog-map.md](catalog-map.md)** - it lists the block intent ontology and all component sections grouped by purpose (JS-plugin marked). It's a starting-point map, not authority: always confirm the exact slug against live `blocks_categories` / `components_list` output before inserting.

---

## On surfaces and tokens

When the user wants semantic / design-token classes (not raw utilities), keep `isUtilityBased: false` and **preserve the token classes the MCP output already uses** - Preline returns semantic surface tokens, not hardcoded colors. Translate plain-language surface words to the matching tokens you see in the returned markup; do not substitute `bg-white` / `bg-gray-*` / hex, and do not invent token names.

Surface tokens you'll commonly see in the output (recognize and reuse them; exact names can vary by version - match what the catalog emits):

| Plain wording | Token family to look for |
|---|---|
| page background | `bg-background` |
| panel / "one gray part" shared by regions | a muted/secondary surface, e.g. `bg-muted` / `bg-secondary` |
| card / "layer" - white with borders | `bg-layer` + `border border-layer-line` (text `text-layer-foreground`) |
| inset / control surface | `bg-surface` |
| separators between regions | the matching `*-line` border token |

---

## Worked illustration (one shape of many)

The five steps are domain-agnostic. The same decomposition covers, for example:
- **App shell** - outer shell (shared surface) → navbar region(s) → sidebar region → content (distinct surface).
- **Product page** - gallery → details (title, price, variant pickers, actions) → tabs / reviews.
- **Settings page** - section nav → form sections → save bar.
- **Multi-step form** - stepper → step panels → footer actions.

A fuller pass for an app-shell request such as *"a navbar with a logo, a sidebar toggle, project / team / account dropdowns and dividers, links and a theme switcher; a left sidebar with search and links; navbar + sidebar as one gray panel, content as a white bordered layer; use theme-token classes":*

**1. Constraints (locked first):**
- "theme-token classes" → `isUtilityBased: false`, no theme passed - and the same setting on every later call.
- "navbar + sidebar one gray panel" → both regions share one muted/secondary surface token; no off-color seams.
- "content as a white bordered layer" → content region uses the layer surface tokens (`bg-layer` + border).

**2. Tree:**
```
shell (navbar + left sidebar = shared surface) + content (layer surface)
├─ navbar · left:  logo · sidebar-toggle · project-dropdown {★pinned A, ★pinned B, Add, Manage}
│                  · divider · team-dropdown {Add team, ✓selected "Marketing"}
├─ navbar · right: button(s) · text/icon links · divider
│                  · account-dropdown (avatar trigger) {Upgrade CTA, theme switch, icon links}
├─ sidebar (below navbar): search input · links · (bottom) icon links
└─ content: layer surface
```

**3. Discover (resolve every slug from output):**
1. `blocks_categories()` → look for an Application / Admin / Dashboard / Navigation shell that already pairs a navbar + sidebar + content. If one fits → `single_block(...)` → use as the skeleton.
2. If none fits, build the skeleton from the `navbar` + `sidebar` sections.
3. For each remaining leaf, `components_list({ section })` then `single_component` - sections per the orientation table (`dropdown`, `dividers`, `avatar`, `dark-mode`/`switch`, `input`/`searchbox`, `buttons`, `links`).

**4. Assemble (one fetch + integrate at a time):**
1. Skeleton → establishes the shared gray surface, the layer content container, and the script anchors.
2. Navbar-left leaves → navbar-right leaves → sidebar leaves, integrating each fully before the next.
3. Keep returned classes, edit **text only**; apply only the requested surface changes (shared gray shell, layer content). Set per-element states (pinned/selected) using the component's own selected/checkbox variant.
4. Wire plugin scripts/init **once** (sidebar toggle, dropdowns, theme switch all need the Preline core script - don't duplicate it). Use `component_documentation` for any plugin's JS API.

**5. Verify** against the request: every named element, every state (pinned, selected), and both surface rules (one gray shell, layer content) present.
