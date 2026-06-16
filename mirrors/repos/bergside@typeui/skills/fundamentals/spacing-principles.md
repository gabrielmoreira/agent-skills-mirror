# Spacing Principles

> The reasoning layer for **whitespace, proximity, and rhythm** — how to choose gaps, padding, and margins when building sections, components, and full pages. Written so AI agents can generate, audit, or improve layout spacing regardless of framework or stack. Apply these principles **after** the active design system's spacing tokens and **alongside** `ui-principles.md` and `typography-principles.md`.

---

## 0. How agents must use this file

1. **Load and apply the design system first — always.** Spacing tokens, component padding specs, section rhythm, and container rules in the design-system files (e.g. `layout.md`, component modules) are the source of truth for **concrete pixel values**.
2. **Then apply these spacing principles** to decide *which* token belongs *where* — inner-group vs between-group, vertical vs horizontal, tight vs loose — when the brief or component spec is silent.
3. **Never contradict the design system.** If a principle here and a design-system token conflict, the design system wins. Flag the conflict for human review.
4. **Never invent arbitrary values.** Pick from the allowed scale (see §1). If the design system defines an 8px base unit, all spacing must be multiples of that base — which also satisfies a 4-point grid.

### Application order (mandatory)

```
1. Design system spacing tokens & component specs  →  ship these first
2. Spacing principles (this file)                 →  choose tier, direction, grouping
3. UI principles + typography principles          →  refine hierarchy, polish, edge cases
```

---

## 1. The spacing scale

### 4-point grid (universal math)

The **4-point spacing system** uses multiples of **4px** for every margin, padding, and gap: 4, 8, 12, 16, 20, 24, 32, 48, 64, 96…

Benefits:
- **Consistency** — one rhythm across pages, sections, and components
- **Developer speed** — finite set of values, predictable handoff
- **Visual hierarchy** — different multiples signal different levels of importance

### Map to your design system

Many design systems anchor on **8px** (or **16px**) as the primary step. That is compatible with the 4-point grid — 8, 16, 24, 32, 48, 96 are all valid 4-point values.

| Role | Typical values (4pt grid) | Example design-system mapping |
|---|---|---|
| **Micro** — icon↔label inside a control | 4px, 8px | Icon gap, badge icon margin |
| **Tight** — within a group | 8px, 12px | List item internals, label→field |
| **Default** — related siblings | 16px | Button groups, form fields in a stack, flex row gap |
| **Medium** — between subgroups | 24px, 32px | Card grid gap, card internal sections |
| **Loose** — between major groups | 48px, 64px | Section header → content |
| **Section** — page rhythm | 96px+ (desktop), 24px+ (mobile) | Section vertical padding |

**Rule:** use **at least three distinct spacing tiers** in every layout (small / medium / large). If every gap is the same, hierarchy collapses and users cannot scan the structure.

---

## 2. Core principle: proximity creates grouping

Spacing is the **primary** grouping tool — stronger than borders for most content.

- **Tight spacing** → "these belong together"
- **Loose spacing** → "this is a new group, section, or topic"

### Inner vs outer (non-negotiable)

> **Padding around a group must be larger than spacing within the group.**

When elements are wrapped in a container (card, toolbar, form section, icon cluster):

```
outer padding (group edge → first child)  >  inner gap (child ↔ child)
```

If inner and outer gaps are equal, the group does not read as a unit. This applies vertically **and** horizontally — including icon rows, button clusters, and nav utility bars.

### Start generous, then tighten

When spacing feels wrong, **do not** add the minimum gap and increment until it "works" — that produces cramped layouts.

**Preferred workflow:**
1. Start with **more** whitespace than you think you need
2. Remove space until the grouping still reads clearly
3. Verify three tiers (tight / default / loose) are visibly distinct

---

## 3. Vertical spacing

### 3.1 Typography rhythm

| Element | Line-height guidance | Notes |
|---|---|---|
| **Body copy** | ~1.5× font size | Comfortable reading; increase 2–3px if the typeface defaults feel tight |
| **Subheadings** | ~1.3× | Between body and display |
| **Headings / titles** | ~1.2× | Tighter — do not use body line-height on large headings |
| **Between paragraphs** | ≈ one body font-size | Use paragraph spacing, not blank lines / `<br>` stacks |

### Heading → paragraph spacing (non-negotiable)

- When a **heading is immediately followed by a paragraph** (lead copy, body text, or description block), the heading must have **32px margin-bottom**.
- Applies to every heading level (`h1`–`h6`), section titles, block titles, and card headings when the next element is paragraph text — not a list, form field, button, or image.
- Use **`margin-bottom: 32px`** on the heading (or the design-system token mapped to 32px). Do not use default browser heading margins, arbitrary values, or padding on the paragraph to fake the gap.
- **Implementation:** set margin-bottom on the heading, not margin-top on the paragraph — the heading owns the space to its content below.
- This 32px gap binds the heading to the copy that follows it. It must still be **looser than paragraph→paragraph** spacing only when body copy uses a smaller gap (typically 16px) — never equal or tighter than the gap between two body paragraphs.

**Heading-to-section** must remain **looser** than **heading-to-paragraph** (e.g. 32px heading→body vs 48–96px section rhythm). The heading belongs to the content below it, not the block above.

### 3.2 Lists

When a list item contains multiple lines or sub-elements (title + meta, label + value):

- Use **two spacing tiers** inside the item — tight between related lines, default between distinct data points
- Use **looser spacing** between list items than within an item
- Do not apply one uniform margin to every line — users cannot tell which data belongs together

### 3.3 Forms and inputs

The most common spacing failure: **equal gaps everywhere**.

```
❌  label ──16px── field ──16px── label ──16px── field
    (user cannot tell which label owns which field)

✅  label ──8px── field ──24px── label ──8px── field
    (tight label↔field = one unit; loose field↔next label = new unit)
```

| Relationship | Tier | Typical token |
|---|---|---|
| **Heading → paragraph** | **Fixed** | **32px margin-bottom on the heading** |
| Label → its input | **Tight** | 4–8px |
| Input → next label (or next field group) | **Loose** | 16–24px |
| Section title → first field | **Default–medium** | 16–32px |

Apply the same logic to search bars, filter rows, and settings panels. See also `ui-principles.md` §0.1 — *Icon inset on inputs must balance both sides*.

### 3.4 Sections and pages

| Relationship | Tier | Principle |
|---|---|---|
| **Heading → paragraph** | **Fixed** | **32px margin-bottom on the heading** |
| Heading → lead paragraph | Same as above | 32px — heading binds to copy below |
| Paragraph → paragraph | Default | ≈ body font-size (typically 16px) |
| Content block → content block | Medium | 24–32px |
| Section header area → section content | Medium–loose | 48–64px |
| Section → section | Section | Equal top/bottom padding per design system |

Sections must share **equal** vertical padding top and bottom — do not compress one edge to "save space."

---

## 4. Horizontal spacing

### 4.1 Inside components

| Pattern | Typical gap | Example |
|---|---|---|
| Icon ↔ label (button, link, input) | **8px** | "Talk to sales" + phone icon |
| Inline text + chevron (dropdown trigger) | **8px** | "Products ▾" |
| Horizontal padding in inputs/buttons | Often **≈ font size** | 16px padding at 16px type — easy to remember and scan |

Icon-to-edge and icon-to-text balance on inputs is defined in `ui-principles.md` — both gaps must match.

### 4.2 Between sibling components

| Pattern | Tier | Example |
|---|---|---|
| Related controls in one row | **Default (16px)** | Login + Sign up, picker + divider + link |
| Icon-only controls **within** a cluster | **Micro (4px)** | Theme + notification + menu toggle |
| Icon-only cluster ↔ text-labeled control | **Default (16px)** | Icon group → Logout link |
| Unrelated columns or regions | **Medium–loose** | Brand ↔ nav ↔ utilities |

### 4.3 Groups laid out horizontally

Same rule as vertical: **space within the group < space around the group.**

```
❌  [ icon 16px icon 16px icon ] 16px  Logout
    (icons feel disconnected; group boundary is weak)

✅  [ icon 4px icon 4px icon ] 16px  Logout
    (icons read as one utility cluster)
```

Cards in a row, social icons, toolbar actions, and nav utility bars all follow this pattern.

---

## 5. Margin vs padding

| Property | What it controls | Use for |
|---|---|---|
| **Padding** | Space **inside** an element's border | Breathing room around text/icons inside a button, card, or input |
| **Margin** | Space **outside** an element's border | Separating siblings, pushing a block away from neighbors |

**Rules:**
- Use **padding** to size a component's internal comfort — never rely on margin to fake internal spacing inside a bordered surface
- Use **margin** or **parent gap** (`flex-gap`, `grid-gap`) to separate siblings — prefer `gap` on flex/grid parents over chaining margins on children
- Collapsing margins cause surprises — in modern layouts, prefer **gap on the parent**

---

## 6. Spacing by surface type

### Cards

| Zone | Tier | Guidance |
|---|---|---|
| Card padding (edge → content) | Default–medium | 16–24px |
| Image → title | Tight–default | 12–16px |
| **Title → body paragraph** | **Fixed** | **32px margin-bottom on the title** |
| Body → footer / CTA | Default | 16px |
| Card ↔ card in a grid | Medium | 24–32px |

### Button rows

- Adjacent buttons: **same height and padding** — see `ui-principles.md` §0.1
- Gap between labeled buttons: **16px** (default tier)
- Gap between icon-only buttons in a cluster: **4px**
- Gap between icon cluster and labeled button: **16px**
- Buttons use the design-system **base size** — do not shrink buttons to match compact inputs

### Navigation bars

- Primary link lists: **24px** gap (32px from medium breakpoint up) unless the brief specifies otherwise
- Utility/action rows: apply inner vs outer and icon-group rules from §4
- See `prompts-pro/marketing-navbars.md` for variant-specific measurements

### Modals, drawers, sidebars

- Outer padding: default–medium (16–24px)
- Title → body: default (16–24px)
- Stacked form fields: follow §3.3 tier rules
- Footer action row: 16px between buttons; flush to modal padding on sides

---

## 7. Responsive spacing

- **Section padding** scales down on mobile — keep top and bottom **equal** at each breakpoint
- **Do not** proportionally shrink every gap on mobile — preserve tier **ratios** (tight still tighter than loose)
- **Touch targets** need adequate padding inside and **≥ 8px** between adjacent interactive targets
- Horizontal container padding may decrease on small screens — internal component spacing tiers stay the same

---

## 8. Agent rules — spacing

### DO

- **DO** pick every spacing value from the 4-point / design-system scale — no `13px`, `17px`, `22px`
- **DO** use **at least three tiers** (tight / default / loose) in every section and component
- **DO** keep **inner-group spacing tighter than between-group spacing**
- **DO** keep **group outer padding larger than inner gaps**
- **DO** apply **32px margin-bottom** on every heading immediately followed by a paragraph
- **DO** bind labels to their fields with tight spacing; separate field groups with loose spacing
- **DO** start with generous whitespace and remove until grouping still reads
- **DO** use `gap` on flex/grid parents for sibling spacing
- **DO** match heading line-height to role (tighter for large headings, looser for body)
- **DO** keep section vertical padding symmetric (top = bottom)

### DO NOT

- **DO NOT** use default browser heading margins instead of the 32px heading→paragraph gap
- **DO NOT** use equal spacing between every element on a page
- **DO NOT** use blank lines, `<br>` tags, or empty divs instead of defined paragraph/section spacing
- **DO NOT** give a list item one uniform margin for all internal lines when structure varies
- **DO NOT** space icon-only controls at 16px from each other when they form one cluster
- **DO NOT** override design-system section or container tokens with ad-hoc values
- **DO NOT** add borders or dividers when proximity already communicates the grouping

---

## 9. Quick audit checklist

Before shipping a section, component, or page:

1. **Scale** — Are all spacing values multiples of 4 (and of the design-system base)?
2. **Tiers** — Can you name the tight, default, and loose gaps used? Are they visibly different?
3. **Grouping** — Does every label sit closer to its field than to the next field?
4. **Headings** — Does every heading followed by a paragraph have **32px margin-bottom**?
5. **Clusters** — Are icon-only controls grouped at 4px with 16px to text-labeled neighbors?
6. **Containers** — Is card/toolbar padding ≥ internal sibling gaps?
7. **Sections** — Is heading→paragraph (32px) tighter than section→section?
8. **Symmetry** — Is section padding equal top and bottom at each breakpoint?
9. **Design system** — Do section, container, and component specs override anything you guessed?

---

## 10. Relationship to other standards

| File | Role |
|---|---|
| **Design system** (`layout.md`, component modules) | Concrete tokens — section padding, container width, component padding |
| **`spacing-principles.md` (this file)** | How to *choose* and *layer* spacing tiers for grouping and hierarchy |
| **`ui-principles.md`** | Non-negotiable control rules (inputs, buttons, badges), layout pillars, proximity |
| **`typography-principles.md`** | Type scale, heading rhythm, line-length — pairs with §3.1 here |

When in doubt: **token first, principle second, polish third.**
