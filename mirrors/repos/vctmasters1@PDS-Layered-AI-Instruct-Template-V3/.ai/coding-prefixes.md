# Element Naming Prefixes — Test & Discovery Registry

**Scope**: Workspace root (authoritative; may be extended hierarchically by modules)
**Purpose**: Establish naming conventions that enable automated discovery, test generation, and metadata-driven validation across **both UI elements and code elements**
**Convention**: All prefixes are **2 letters** (lowercase) followed by underscore: `{prefix}_`
**Last Updated**: 2026-06-03

---

## Contents

| Section | What's here |
|---|---|
| [GUI Element Prefixes](#gui-element-prefixes) | Prefixes for UI elements (buttons, inputs, modals, etc.) |
| [Code Element Prefixes](#code-element-prefixes) | Prefixes for code-side identifiers (endpoints, events, jobs, flags, states, metrics) |
| [Hierarchical Inheritance](#hierarchical-inheritance) | How modules extend or override prefixes |
| [Validation & Discovery](#validation--discovery) | How the validation engine finds and tests prefixed elements |
| [Best Practices](#best-practices) | When and how to use prefixes |

---

## GUI Element Prefixes

The following table is the **canonical registry** for UI element prefixes. Prefixes are designed to support automated test discovery, CLI searching (`grep "_{prefix}_"`), and code generation.

| Prefix | Element Type | Example | Notes |
|--------|---|---|---|
| `bu_` | Button | `bu_submit`, `bu_cancel` | Action triggers; primary interaction points |
| `tg_` | Toggle | `tg_darkmode`, `tg_notifications` | Boolean switches; state controls |
| `in_` | Input field | `in_email`, `in_searchbox` | Text input, number, email, etc. |
| `cb_` | Checkbox | `cb_accept_terms`, `cb_subscribe` | Multi-select option |
| `rd_` | Radio button | `rd_gender_male`, `rd_option_a` | Single-select from group |
| `sw_` | Switch/Toggle control | `sw_feature_flag`, `sw_advanced` | Binary state control (distinct from `tg_` for semantic clarity) |
| `sl_` | Slider/Range input | `sl_volume`, `sl_price_range` | Continuous value selection |
| `dd_` | Dropdown/Select | `dd_country`, `dd_sort_by` | Discrete option list |
| `md_` | Modal dialog | `md_confirm`, `md_settings` | Full-screen overlay; focused interaction |
| `dl_` | Dialog (lighter) | `dl_alert`, `dl_tooltip_info` | Lighter overlay; non-blocking or dismissible |
| `fd_` | Form/Fieldset | `fd_login_form`, `fd_account_section` | Grouped form controls; logical sections |
| `tb_` | Table | `tb_users`, `tb_transactions` | Data grids; tabular display |
| `cr_` | Card | `cr_product`, `cr_user_profile` | Contained content unit |
| `mn_` | Menu | `mn_main`, `mn_context` | Navigation or command lists |
| `sb_` | Sidebar | `sb_nav`, `sb_filters` | Side panel; typically collapsible |
| `hd_` | Header | `hd_main`, `hd_page_title` | Top section; title/branding area |
| `ft_` | Footer | `ft_main`, `ft_copyright` | Bottom section |
| `nd_` | Notification/Alert | `nd_error_msg`, `nd_success` | Status messages; toasts, alerts |
| `lk_` | Link/Anchor | `lk_homepage`, `lk_terms` | Navigation anchor; hyperlink |
| `ic_` | Icon | `ic_menu`, `ic_settings` | Symbolic visual element |
| `bd_` | Badge | `bd_count`, `bd_status_active` | Label/tag; small status indicator |
| `ld_` | Loading indicator | `ld_spinner`, `ld_skeleton` | Progress/busy state |
| `ov_` | Overlay | `ov_backdrop`, `ov_dimmer` | Visual masking layer |
| `pp_` | Popover/Popup | `pp_help`, `pp_date_picker` | Floating context menu or tooltip |
| `ac_` | Accordion | `ac_section_1`, `ac_faq` | Collapsible sections |
| `br_` | Breadcrumb | `br_navigation`, `br_path` | Navigation trail |
| `tt_` | Tooltip | `tt_help_icon`, `tt_info` | Hover/focus help text |
| `sp_` | Spinner | `sp_main_loader`, `sp_inline` | Animated loading indicator |
| `pd_` | Pagination | `pd_controls`, `pd_page_2` | Page navigation controls |
| `sr_` | Searchable result | `sr_item_1`, `sr_no_results` | Search result entry |
| `cm_` | Comment | `cm_thread_1`, `cm_reply_5` | Discussion/comment element |
| `rt_` | Rating | `rt_product_stars`, `rt_feedback` | Star/score rating input |
| `kb_` | Keyboard shortcut | `kb_save`, `kb_exit` | Keyboard-driven action (metadata for hotkeys) |

---

## Code Element Prefixes

Code-side identifiers that benefit from the same scan-and-test discipline as UI elements. Use these as constants, route IDs, event names, or symbol names — anywhere a tool, test, or audit needs to enumerate "all things of type X."

| Prefix | Element Type | Example | Notes |
|---|---|---|---|
| `ap_` | API route handler / endpoint identifier | `ap_login`, `ap_get_user`, `ap_list_orders` | Use as a constant or symbol attached to the handler. Discovery feeds OpenAPI / contract test generation. Distinct from the URL path. |
| `ev_` | Event (domain or telemetry) | `ev_user_signed_up`, `ev_payment_failed` | Emitted via event bus, telemetry, or domain log. Discovery feeds event catalog and consumer-side tests. |
| `mt_` | Metric / measurement | `mt_db_latency_ms`, `mt_login_success_total` | Counter, gauge, histogram. Discovery feeds dashboard and SLO audits. |
| `wk_` | Worker / background job | `wk_email_sender`, `wk_nightly_cleanup` | Long-running or scheduled task. Discovery feeds retry / idempotence / scheduling audits. |
| `fl_` | Feature flag | `fl_new_dashboard`, `fl_beta_search` | Discovery feeds rollout / cleanup audits (which flags are still referenced, which are stale). |
| `st_` | State machine state | `st_pending`, `st_approved`, `st_rejected` | Use within a state machine module. Discovery feeds transition coverage tests. |

**Note — code-element prefixes vs. agent-file namespaces.** The `ap_` / `ev_` / `mt_` / `wk_` / `fl_` / `st_` prefixes above apply to **identifiers inside code** (constants, symbols, route IDs, event names) so that discovery scans can enumerate "all things of type X." They do **not** apply to filenames that already encode their role through a `.<role>.md` suffix.

Agent files use a separate, project-scoped namespace pattern of the form `<project>-<namespace>-<role>.agent.md` — in this template, `pds-{pipe|man|meta}-<role>.agent.md` (e.g., `pds-pipe-super.agent.md`, `pds-man-naming.agent.md`, `pds-meta-router.agent.md`). That namespace lives in the *filename*, alongside the `.agent.md` role-suffix; it is unrelated to the two-letter code-element prefixes registered in this file. Do not mix the two systems.

---

## Hierarchical Inheritance

**Default behavior:** All modules inherit the master table above.

**Module-level override/extension:**
- Any module may create its own `.ai/coding-prefixes.md` in its directory
- Module prefixes override workspace prefixes if the same prefix is declared
- New prefixes in a module are **only valid within that module and its children**
- To extend the master table, create a new entry in the module's `.ai/coding-prefixes.md` with `[Module Override]` annotation

**Example module override** (`[module]/.ai/coding-prefixes.md`):

```markdown
# Module-Specific Prefixes

| Prefix | Element Type | Example | Module Note |
|--------|---|---|---|
| `cp_` | Custom component | `cp_analytics_widget` | [Module Override] |
```

---

## Validation & Discovery

### Scanning for prefixed elements

The validation engine (`validation/discovery.py` — see project structure) performs a **multi-stage scan**:

1. **Lexical discovery**: Search the codebase for regex pattern `[a-z]{2}_[a-zA-Z0-9_]*` in relevant file types
2. **Verification**: Match discovered identifiers against the active prefix table (workspace + module override)
3. **Location recording**: Map each element to file, line, column, and context
4. **Registry output**: Generate a `prefixes-found.json` report with:
   ```json
   {
     "timestamp": "2026-06-02T14:30:00Z",
     "scan_root": "/path/to/module",
     "elements": [
       {
         "id": "bu_submit",
         "prefix": "bu_",
         "type": "button",
         "file": "src/components/form.jsx",
         "line": 45,
         "column": 8,
         "context": "onClick={handleSubmit}"
       }
     ]
   }
   ```

### Test facility

The **generic test facility** reads the `prefixes-found.json` registry and applies strategy per element type:

- **Existence check** (all): confirm element is defined in the codebase
- **Accessibility checks** (buttons, inputs, etc.): verify aria labels, roles
- **Functional tests** (buttons, toggles, etc.): verify click handlers, state transitions (deferred to specialized test framework)
- **Visual regression** (cards, modals, etc.): capture and compare screenshots (deferred to visual testing tool)

---

## Best Practices

### When to use prefixes

✅ **Use prefixes for:**
- User-facing interactive elements (buttons, inputs, toggles)
- Major layout containers (modals, sidebars, cards)
- Elements that will be tested or queried programmatically
- Data attributes, element IDs, CSS classes

❌ **Avoid prefixes for:**
- Internal utility elements (wrappers, spacers with no semantic meaning)
- Elements that are never directly tested or queried
- Generic semantic HTML that needs no special identification

### Naming consistency

- Keep element names **lowercase** (after the prefix)
- Use **underscores to separate** words: `bu_submit_form`, not `buSubmitForm`
- Be **descriptive but concise**: `bu_delete_account` is better than `bu_btn`
- Avoid **ambiguous abbreviations**: `in_ph` is unclear; `in_phone` is clear

### Finding all prefixed elements

From the command line (PowerShell on Windows, bash on POSIX):

```powershell
# Find all button elements
Select-String -Path '*.jsx','*.tsx','*.js' -Pattern 'bu_\w+'

# Find all toggle elements
Select-String -Path '*.jsx','*.tsx','*.js' -Pattern 'tg_\w+'
```

Or run the validation script:
```bash
python validation/discovery.py --scan-root ./src --output prefixes-found.json
```

---

## References

- [File Naming Convention](conventions.md#file-naming) — canonical naming rules for files and identifiers
- [`validation/discovery.py`](../validation/discovery.py) — the scanner that consumes this registry
- `.ai/instruct.md` — project-wide authority (if this document is extended later)
