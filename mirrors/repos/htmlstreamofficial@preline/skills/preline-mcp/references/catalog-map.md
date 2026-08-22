# Catalog Map - where intents and elements live

> Generated from the catalog (blocks.json, components.json, constants.ts). Regenerate with `node scripts/gen-catalog-map.mjs`.
> This is a **routing map**, not authority - always confirm exact slugs against live `blocks_categories` / `components_list` output before inserting.

Use during the **Discover** step (SKILL.md → Composite & Layout Requests): map an abstract intent to a blocks branch, and each named element to a component section.

---

## Blocks - intent ontology (for whole pages / regions / shells)

Abstract request ("a pricing page", "a login screen", "an admin shell", "a checkout flow")? Route to a branch, then `blocks_in_category({ mainSection, subSection, category })`. Whole app shells live under **Navigation & Layout → Sidebars & Shells**.

- **Marketing** - Hero, Banners & Landing Intros · Site Navigation & Headers · Trust & Social Proof · Content & Editorial · Pricing & Conversion · Website Foundations
- **Data Display** - Analytics & KPIs · Operational & Activity Views · Tables & Records
- **UI Components** - Menus & Selection · Actions, Status & Progress · Lists & Links
- **Forms** - Core Inputs & Layouts · Creation & Management · Filters & Refinement · Billing, Feedback & Conversion
- **Authentication** - Sign In & Account Access · Onboarding & Activation
- **Ecommerce** - Product Discovery · Product Detail & Purchase · Orders & Commerce Utilities
- **Communication** - Chat & Inbox · Calls & Media · Contacts & Presence
- **Productivity** - Calendars & Scheduling · Planning Boards
- **Blog & Articles** - Editorial Pages · Blog Discovery & Sections
- **Application Pages** - Workspaces & Admin · Profiles & Accounts
- **Billing & Payments** - Billing & Payments
- **Feedback & States** - Alerts & Recovery · Actions & Engagement · Consent & Compliance
- **Search & Command Palettes** - Search & Navigation · Actions & Shortcuts
- **Navigation & Layout** - Application Headers & Navigation · Sidebars & Shells · Title Bars & Footers · Blank, Error & Utility Layouts

---

## Components - section index (for individual elements)

Pass the section to keep the list small: `components_list({ section: "<slug>" })`. 📖 = has a `component_documentation` entry (JS API). Any interactive component still needs the Preline core script wired once.

**Form inputs & controls:** `input` · `input-group` · `input-number`📖 · `textarea` · `select` · `advanced-select`📖 · `combobox`📖 · `searchbox` · `checkbox` · `radio` · `switch` · `color-picker` · `range-slider` · `advanced-range-slider`📖 · `datepicker` · `advanced-datepicker`📖 · `time-picker` · `pin-input`📖 · `strong-password`📖 · `toggle-password`📖 · `file-input` · `file-upload`📖 · `file-uploading-progress-form`

**Menus & overlays:** `dropdown`📖 · `mega-menu` · `context-menu` · `modal` · `offcanvas` · `popover` · `tooltip`📖

**Navigation:** `navbar` · `navs` · `sidebar` · `breadcrumb` · `pagination` · `tabs`📖 · `stepper`📖 · `scrollspy`📖 · `tree-view`📖

**Feedback & status:** `alerts` · `toasts` · `toast-notifications` · `badge` · `progress` · `ratings` · `spinners` · `skeleton` · `legend-indicator`

**Data display:** `tables` · `datatables` · `charts` · `datamaps` · `maps` · `list-group` · `lists` · `timeline`

**Content & media:** `card` · `avatar` · `avatar-group` · `blockquote` · `images` · `carousel`📖 · `marquee` · `devices` · `chat-bubbles` · `text-editor` · `typography` · `static-icons`

**Actions & misc:** `buttons` · `button-group` · `links` · `dividers` · `kbd` · `clipboard` · `copy-markup`📖 · `toggle-count`📖 · `dark-mode` · `confetti` · `drag-and-drop` · `collapse`📖 · `accordion`📖

**Layout:** `container` · `grid` · `columns` · `layout-splitter`📖 · `custom-scrollbar`

