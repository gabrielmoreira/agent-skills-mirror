# HXL Setup Widgets — prop contracts and Education Cloud mapping

Five widgets give the setup workflow a visual spine. They hold NO logic: compute every field from live reads. Each is a visual aid, never a gate.

## Render call

The widgets live in the shared `hxl-setup-widgets` skill, so nothing is bundled here and nothing is deployed to the org. This file holds only the Education Cloud mapping. Render one with:

```text
display_widget(
  resourceType = "skill_widget",
  apiName = "hxl-setup-widgets/hxlSetup<Step>",
  props = { ... }
)
```

Pass props at the top level of `props` (no `attributes` wrapper). Generic prop rules are also in the `hxl-setup-widgets` skill; the mapping below is Education-specific.

**Fallback.** If `display_widget` is unavailable, the host does not paint MCP Apps widgets, or the call errors (including `widget not found in index`), continue in text for the rest of the session and say so once, in one line. Do not author a widget tree yourself.

## Shared rules

- **When it paints.** Only in hosts that mount MCP Apps widgets, and only where `display_widget` is enabled for the org. A non-mounting host (terminal) → error or text fallback. Continue in text; the numbered steps in SKILL.md are the source of truth. Never block setup on a widget.
- **Setup links are absolute.** `setupUrl` must be a full `https://` URL on the org's Setup host. A relative path resolves against the chat host, not the org. Build it as `<setup-host>/lightning/setup/<Page>/home`, where `<setup-host>` is the org host with its trailing `.salesforce.com` replaced by `.salesforce-setup.com` (e.g. `https://acme.my.salesforce.com` → `https://acme.my.salesforce-setup.com`). Take the org host from the origin of the `url` field in any headless-360 `dispatch`/`dispatch_readonly` response (the Phase 0 Organization query already returns it).
- **Gather first, render once.** Finish the step's reads, then render. Re-render only at the checkpoints below.
- **Nothing hard-coded.** Every status, label, and boolean comes from a read done this session. Never show `Verified` without a passing cold-verify.
- **Types.** `irreversible` and `enabled` are real booleans, not strings. Optional string fields you have nothing for are `""`, not omitted. A button renders only when `actionLabel` is non-empty, so verified/read-only rows pass `actionLabel: ""`.
- **`statusVariant`** values: `success`, `warning`, `error`, `info`, `default`.
- **`kind`** (Review/Apply items): `manual` → the widget draws its own fixed "Open Setup" link button that opens `setupUrl` in a new tab, so always set `setupUrl` and always set `actionLabel: ""` (a non-empty `actionLabel` adds a duplicate second button). Any other value (`action`, `toggle`) → the `actionLabel` button sends `message` back to the chat.
- **Button click = approval of that one item.** A `message` arrives as a user turn. Treat the click as the user's approval to run that item's write: do not ask again. Read first, write, then cold-verify. The row already shows its Irreversible badge, and the reply that accompanies the render states the one-way warning in plain text (a statement, not a question). A click approves only the item it names.
- Keep the text reply meaningful alongside each widget. Do not restate rows the widget already shows.

## Checkpoints

| Widget | `apiName` suffix | Call at |
|--------|-----------|---------|
| Intent | `hxlSetupIntent` | Phase 1 step 6 (domain choice) |
| Review | `hxlSetupReview` | After Phase 0 / 1 / 1.5 reads; again at step 15 (domain prerequisites); re-render after each enable |
| Plan | `hxlSetupPlan` | After step 20 selection, before the first write |
| Apply | `hxlSetupApply` | Step 21, re-rendered after each item's cold-verify |
| Verify | `hxlSetupVerify` | Step 22 summary |

## Intent — `hxlSetupIntent`

Props: `heading`, `subheading`, `options[]`.

| Option field | Rule |
|--------------|------|
| `name` | Domain name. |
| `description` | One-line "what it does" from `references/domain-features/<domain>.md`. |
| `requires` | Domain prerequisites, e.g. Student Management → `Requires Academic Operations`; else `""`. |
| `statusLabel` / `statusVariant` | `Enabled` / `success` when the domain toggle cold-reads `true`; else `Available` / `default`. Blocked by a missing prerequisite → `Blocked` / `warning`. |
| `actionLabel` / `actionVariant` | `Configure` / `primary`; `""` when already enabled and nothing to configure. |
| `message` | `Configure <Domain>`. |

Options: the six domains (Student Success, Recruitment & Admissions, Academic Operations, Alumni Relations, Student Management, Mentoring). Recruitment & Admissions has no master toggle; derive its status from its sub-feature settings and say so in `description`. Skip the widget if the user already named the domain.

## Review — `hxlSetupReview`

Props: `heading`, `subheading`, `checks[]`.

| Check field | Rule |
|-------------|------|
| `name` | Check name. |
| `description` | One-line what it does. |
| `requires` | Dependency, or `""`. |
| `kind` | `manual` (Setup UI only) or `action` (skill can do it). |
| `enabled` | `true` once verified. |
| `irreversible` | `true` for Education Cloud Foundation and Person Accounts. |
| `statusLabel` / `statusVariant` | `Verified` / `success`, `Pending` / `default`, or `Action needed` / `warning`. A manual step the user has not done is `Action needed`. |
| `actionLabel` | `""` when verified, check-only, or `kind: "manual"`; else `Enable`. |
| `message` | For `action` rows: `Enable <name>`. Else `""`. |
| `setupUrl` | For `manual` rows: absolute Setup URL (see "Setup links are absolute"). Else `""`. |

**Prerequisite review (after Phase 0/1/1.5 reads)** — eight rows, in order:

| # | Check | kind | Notes |
|---|-------|------|-------|
| 1 | Org Edition | `action` | Check-only: `actionLabel ""`. |
| 2 | Lightning Experience | `manual` | Setup → User Interface. |
| 3 | Education Cloud License | `action` | Check-only: `actionLabel ""`; not provisioned → contact account team. |
| 4 | Education Cloud Full Access | `manual` | Setup → Permission Sets. |
| 5 | Education Cloud Foundation | `action` | `irreversible: true`. |
| 6 | OmniStudio | `action` | Attempt API, else Setup → OmniStudio Settings. |
| 7 | Business Rules Engine | `manual` | Setup → Business Rules Engine. |
| 8 | Person Accounts | `manual` | `irreversible: true`; Setup → Account Settings. |

Heading `Education Cloud prerequisites`; `subheading` = org name and edition.

**Domain prerequisite review (step 15)** — same widget, one row per prerequisite the selected domain needs (Experience Cloud, Salesforce Scheduler, Fundraising, prior domain), per `references/domain-features/<domain>.md`. Heading `<Domain> prerequisites`.

## Plan — `hxlSetupPlan`

Read-only (no action buttons). Props: `heading`, `summary`, `planItems[]`.

| Plan item field | Rule |
|-----------------|------|
| `name` | Feature or domain being enabled. |
| `description` | One-line what it does. |
| `method` | `Metadata PUT (IndustriesSettings)`, `Invoke endpoint`, `Org preference PATCH`, `Data API create`, or `Manual (Setup UI)`. |
| `irreversible` | `true` for every one-way toggle. |
| `impact` | One line of what changes, e.g. `Activates student success objects and setup`. |

One item per pending write the user selected (domain toggle, chosen sub-features, chosen dependent features), in execution order. `summary` = count and how many are irreversible. Render it automatically; do not ask whether to show it. Plan has no buttons, so after rendering ask approve / reject / modify (authoring convention 4) unless the items are executed from Review/Apply button clicks.

## Apply — `hxlSetupApply`

Props: `heading`, `subheading`, `items[]`; item fields identical to Review `checks[]`.

Same items as the approved Plan, with live state: `Pending` / `default`, `Applied` / `success`, `Failed` / `error`, `Action needed` / `warning` (manual step outstanding). `Applied` only after that item's cold-verify passed. Manual rows carry `kind: "manual"`, `setupUrl`, and `actionLabel: ""`; API rows carry `kind: "action"` with a `message`. Re-render after each item completes.

## Verify — `hxlSetupVerify`

Read-only. Props: `heading`, `status`, `statusVariant`, `summary`, `results[]`.

| Result field | Rule |
|--------------|------|
| `name` | Feature. |
| `detail` | The re-read value, e.g. `IsStudentSuccessEnabled = true`. |
| `statusLabel` / `statusVariant` | `Verified` / `success`, `Failed` / `error`, or `Manual follow-up` / `warning`. |
| `method` | How it was enabled and verified: `API`, `UI`, or `OmniStudio`. |

`status` = `Complete` / `success` when every row is verified, else `Partial` / `warning`. `summary` = one line with counts. A feature appears as `Verified` only if both boxes in the Final Verification Checklist are checked (approval + cold-verify).
