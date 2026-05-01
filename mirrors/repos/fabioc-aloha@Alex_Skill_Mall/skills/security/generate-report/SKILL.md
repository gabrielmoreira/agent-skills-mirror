---
type: skill
lifecycle: stable
inheritance: inheritable
name: generate-report
description: >
tier: standard
applyTo: '**/*generate*,**/*report*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Generate Tenant Isolation Violation Report

Generate an interactive, self-contained HTML dashboard that displays all SFI-TI3.2.2 tenant
isolation violations for a given service, org, or alias. The report opens in the default browser
and includes filtering, sorting, color-coded severity, TSG links, and S360 deep links.

---

## Trigger detection

Activate when the user says:
- "generate report" / "create dashboard" / "show violations report"
- "HTML report" / "violation dashboard" / "export violations"
- "tenant isolation report" / "create violation report"
- "generate TI report" / "show tenant isolation dashboard"
- "build HTML dashboard" / "S360 TI report"
- "generate SFI-TI3.2.2 report" / "export tenant isolation violations"

---

## Step 1 — Accept violation data

The input is structured violation data from the `fetch-violations` skill, typically passed
by the `violation-triager` skill. Each violation object is a **normalized flat record**
derived from the MCP response (flattened from `CustomDimensions` and `S360Dimensions`):

```
Title                    — Violation type (one of 9 titles, see Step 2)
TargetId                 — S360 target ID (service-level)
AppId                    — Application GUID (from CustomDimensions; empty for connector items)
AppDisplayName           — App name (from CustomDimensions; empty for connector items)
AppHomeTenantId          — Home tenant GUID
cloudType                — "Public", "Fairfax", "Mooncake"
SLAState                 — "OnTime" or "OutOfSla"
CurrentDueDate           — Current due date
CurrentETA               — ETA set by action owner
ActionOwnerAlias         — Action owner alias (from S360Dimensions)
ADOWorkItemHTMLUrl       — ADO work item link (from S360Dimensions)
URL                      — TSG / remediation link
KpiActionItemId          — Unique action item identifier
```

> The `remediationCategory`, `severity`, and `tsgLink` fields are **derived** by the
> skill at classification time (Step 2), not from the MCP response.

If no violation data is provided (or the array is empty), respond:

> "No violation data provided. Please run `fetch-violations` first to retrieve violations,
> then pass the results to this skill."

---

## Step 2 — Classify violations for display

For each violation, compute three derived fields:

### Remediation Category

Map `ViolationTitle` to a remediation category:

| ViolationTitle | Remediation Category |
|---|---|
| `AAD Entra Apps in Prod Tenants using certificates in Non-Prod Tenant` | Cert Rehoming |
| `AAD Entra Apps cloud mismatches with Cert Cloud` | Cert Rehoming |
| `AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud auth scenarios` | FIC Setup |
| `AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud 1P scenarios` | FIC Setup |
| `1pApp certs Tenant mismatches the Tenant of the Security Group` | SG Update |
| `AAD Entra apps with cross-tenant violations` | Cross-Tenant |
| `Connector domain OWNER should not use shared subjectName for authentication across tenant` | Connector |
| `Connector domain CONSUMER should not use shared subjectName for authentication across tenant` | Connector |
| `1P App with invalid security group` | SG Update |

### Severity Color

Determine severity based on remediation complexity:

- **Green** (Autofix eligible): Violations where an automated SG update can resolve them
  - `1P App with invalid security group`
- **Yellow** (Guidance available): Violations with clear TSG guidance but requiring manual owner action
  - `AAD Entra Apps in Prod Tenants using certificates in Non-Prod Tenant`
  - `AAD Entra Apps cloud mismatches with Cert Cloud`
  - `AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud auth scenarios`
  - `AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud 1P scenarios`
  - `1pApp certs Tenant mismatches the Tenant of the Security Group` — requires a follow-up SG-vs-cert decision
- **Red** (Complex remediation): Multi-step or cross-team coordination required
  - `AAD Entra apps with cross-tenant violations`
  - `Connector domain OWNER should not use shared subjectName for authentication across tenant`
  - `Connector domain CONSUMER should not use shared subjectName for authentication across tenant`

### TSG Link

Map `ViolationTitle` to the correct aka.ms troubleshooting guide:

| ViolationTitle | TSG Link |
|---|---|
| `AAD Entra Apps in Prod Tenants using certificates in Non-Prod Tenant` | `https://aka.ms/entraQ4` |
| `AAD Entra Apps cloud mismatches with Cert Cloud` | `https://aka.ms/entraQ5` |
| `AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud auth scenarios` | `https://aka.ms/entraQ5` |
| `AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud 1P scenarios` | `https://aka.ms/entraQ5` |
| `1pApp certs Tenant mismatches the Tenant of the Security Group` | `https://aka.ms/entraQ6` |
| `AAD Entra apps with cross-tenant violations` | `https://aka.ms/entraQ7` |
| `Connector domain OWNER should not use shared subjectName for authentication across tenant` | `https://aka.ms/entraQ8` |
| `Connector domain CONSUMER should not use shared subjectName for authentication across tenant` | `https://aka.ms/entraQ8` |
| `1P App with invalid security group` | `https://aka.ms/entraQ9` |

Store the classified results as `violations[]` with added fields:
`remediationCategory`, `severity` (green/yellow/red), `tsgLink`.

**Compute summary:**
```
total           = violations.length
autofixCount    = count where severity == 'green'
guidanceCount   = count where severity == 'yellow'
complexCount    = count where severity == 'red'
uniqueApps      = distinct AppId count
```

---

## Step 3 — Generate the HTML report

Write a complete, self-contained HTML file to:
`.\s360-ti322-report-{YYYYMMDD}-{HHmmss}.html`

The violations array must be serialized as JSON and embedded as a JS variable.

Use these placeholder substitutions:

```
{TARGET_LABEL}        → filter description (alias/service/org) or "All"
{GENERATED}           → current datetime ISO string
{VIOLATIONS_JSON}     → JSON.stringify(violations) — each item contains all original
                         fields plus remediationCategory, severity, tsgLink
{TOTAL}               → total
{AUTOFIX_COUNT}       → autofixCount
{GUIDANCE_COUNT}      → guidanceCount
{COMPLEX_COUNT}       → complexCount
{UNIQUE_APPS}         → uniqueApps
```

---

### HTML template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SFI-TI 3.2.2 Tenant Isolation — Violation Report</title>
<style>
/* ===== CSS Reset & Variables ===== */
:root {
  --bg: #f4f6f9;
  --surface: #ffffff;
  --surface2: #f0f2f5;
  --border: #dfe3ea;
  --header-bg: #1b2a4a;
  --header-text: #ffffff;
  --text: #1e293b;
  --muted: #64748b;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --green: #16a34a;
  --green-bg: rgba(22,163,74,.08);
  --green-border: rgba(22,163,74,.25);
  --yellow: #ca8a04;
  --yellow-bg: rgba(202,138,4,.08);
  --yellow-border: rgba(202,138,4,.25);
  --red: #dc2626;
  --red-bg: rgba(220,38,38,.08);
  --red-border: rgba(220,38,38,.25);
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  font-size: 14px;
  line-height: 1.5;
}

/* ===== Header ===== */
.header {
  background: var(--header-bg);
  color: var(--header-text);
  padding: 24px 32px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}
.header h1 {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.header .meta {
  font-size: .82rem;
  opacity: .75;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.header .meta span { white-space: nowrap; }

/* ===== Main container ===== */
.container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px 32px;
}

/* ===== Summary Cards ===== */
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow);
  transition: transform .15s, box-shadow .15s;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,.1);
}
.card .num {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
}
.card .label {
  color: var(--muted);
  font-size: .75rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  margin-top: 4px;
}
.card.total .num    { color: var(--accent); }
.card.green .num    { color: var(--green); }
.card.yellow .num   { color: var(--yellow); }
.card.red .num      { color: var(--red); }
.card.services .num { color: var(--muted); }

/* Card left-border accents */
.card.green  { border-left: 4px solid var(--green); }
.card.yellow { border-left: 4px solid var(--yellow); }
.card.red    { border-left: 4px solid var(--red); }
.card.total  { border-left: 4px solid var(--accent); }

/* ===== Filters Bar ===== */
.filters {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  box-shadow: var(--shadow);
}
.filters label {
  font-size: .78rem;
  color: var(--muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.filters select,
.filters input[type="text"] {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 6px;
  padding: 7px 12px;
  font-size: .83rem;
  font-family: var(--font);
  outline: none;
  transition: border-color .15s;
}
.filters select:focus,
.filters input[type="text"]:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(59,130,246,.15);
}
.filters input[type="text"] { width: 240px; }
.filter-count {
  margin-left: auto;
  font-size: .82rem;
  color: var(--muted);
  font-weight: 600;
}

/* ===== Table ===== */
.tbl-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.tbl-scroll {
  overflow-x: auto;
  max-height: 75vh;
  overflow-y: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: .83rem;
}
thead { position: sticky; top: 0; z-index: 10; }
th {
  background: var(--header-bg);
  color: var(--header-text);
  font-weight: 600;
  text-align: left;
  padding: 10px 14px;
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  border-bottom: 2px solid rgba(255,255,255,.1);
}
th:hover { background: #243558; }
th .sort-arrow { margin-left: 4px; font-size: .65rem; opacity: .5; }
th.sorted .sort-arrow { opacity: 1; }

td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}
tr:last-child td { border-bottom: none; }
tr.hidden { display: none; }
tr:not(.hidden):hover td { background: rgba(59,130,246,.03); }

/* Severity row tinting */
tr.severity-green td  { border-left-color: var(--green); }
tr.severity-yellow td { border-left-color: var(--yellow); }
tr.severity-red td    { border-left-color: var(--red); }
tr.severity-green td:first-child  { box-shadow: inset 4px 0 0 var(--green); }
tr.severity-yellow td:first-child { box-shadow: inset 4px 0 0 var(--yellow); }
tr.severity-red td:first-child    { box-shadow: inset 4px 0 0 var(--red); }

/* ===== Badges & Dots ===== */
.severity-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  vertical-align: middle;
}
.dot-green  { background: var(--green); }
.dot-yellow { background: var(--yellow); }
.dot-red    { background: var(--red); }

.badge {
  display: inline-block;
  border-radius: 12px;
  padding: 2px 10px;
  font-size: .72rem;
  font-weight: 600;
  white-space: nowrap;
}
.badge-green  { background: var(--green-bg);  color: var(--green);  border: 1px solid var(--green-border); }
.badge-yellow { background: var(--yellow-bg); color: var(--yellow); border: 1px solid var(--yellow-border); }
.badge-red    { background: var(--red-bg);    color: var(--red);    border: 1px solid var(--red-border); }
.badge-1p     { background: rgba(59,130,246,.1); color: var(--accent); border: 1px solid rgba(59,130,246,.25); }
.badge-3p     { background: rgba(100,116,139,.1); color: var(--muted); border: 1px solid rgba(100,116,139,.25); }

/* ===== Links ===== */
a.tsg-link,
a.s360-link {
  color: var(--accent);
  text-decoration: none;
  font-size: .78rem;
  font-weight: 500;
  white-space: nowrap;
}
a.tsg-link:hover,
a.s360-link:hover { text-decoration: underline; }

/* ===== Violation title ===== */
.violation-title {
  font-size: .78rem;
  max-width: 260px;
  line-height: 1.35;
  word-wrap: break-word;
}
.app-name { font-weight: 600; }
.cloud-tag {
  display: inline-block;
  font-size: .7rem;
  color: var(--muted);
  background: var(--surface2);
  border-radius: 4px;
  padding: 1px 6px;
}
.state-text {
  font-size: .78rem;
  line-height: 1.35;
  max-width: 200px;
  word-wrap: break-word;
}

/* ===== Empty state ===== */
#empty-state {
  display: none;
  text-align: center;
  padding: 48px 20px;
  color: var(--muted);
  font-size: .95rem;
}

/* ===== Footer ===== */
.footer {
  color: var(--muted);
  font-size: .72rem;
  margin-top: 32px;
  text-align: center;
  padding-bottom: 20px;
}

/* ===== Print styles ===== */
@media print {
  body { background: #fff; font-size: 11px; }
  .header { background: #1b2a4a !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .filters { display: none; }
  .tbl-scroll { max-height: none; overflow: visible; }
  .card { break-inside: avoid; }
  tr.hidden { display: none !important; }
  a { color: var(--accent) !important; }
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .header { padding: 16px; }
  .container { padding: 16px; }
  .cards { grid-template-columns: repeat(2, 1fr); }
  .filters input[type="text"] { width: 100%; }
}
</style>
</head>
<body>

<!-- ===== Header ===== -->
<div class="header">
  <div>
    <h1>🛡️ SFI-TI 3.2.2 Tenant Isolation — Violation Report</h1>
    <div class="meta">
      <span>Target: <strong>{TARGET_LABEL}</strong></span>
      <span>Generated: {GENERATED}</span>
      <span id="violation-counter"></span>
    </div>
  </div>
</div>

<!-- ===== Main Content ===== -->
<div class="container">

  <!-- Summary Cards -->
  <div class="cards">
    <div class="card total">
      <div class="num">{TOTAL}</div>
      <div class="label">Total Violations</div>
    </div>
    <div class="card green">
      <div class="num">{AUTOFIX_COUNT}</div>
      <div class="label">✅ Autofix Eligible</div>
    </div>
    <div class="card yellow">
      <div class="num">{GUIDANCE_COUNT}</div>
      <div class="label">⚠️ Guidance Available</div>
    </div>
    <div class="card red">
      <div class="num">{COMPLEX_COUNT}</div>
      <div class="label">🔴 Complex Remediation</div>
    </div>
    <div class="card services">
      <div class="num">{UNIQUE_APPS}</div>
      <div class="label">Unique Apps</div>
    </div>
  </div>

  <!-- Filters Bar -->
  <div class="filters">
    <label for="search">Search:</label>
    <input id="search" type="text" placeholder="🔍 Search apps, violations, owners…" oninput="applyFilters()">

    <label for="filter-violation">Violation:</label>
    <select id="filter-violation" onchange="applyFilters()">
      <option value="">All Violations</option>
    </select>

    <label for="filter-cloud">Cloud:</label>
    <select id="filter-cloud" onchange="applyFilters()">
      <option value="">All Clouds</option>
    </select>

    <label for="filter-category">Category:</label>
    <select id="filter-category" onchange="applyFilters()">
      <option value="">All Categories</option>
    </select>

    <label for="filter-severity">Severity:</label>
    <select id="filter-severity" onchange="applyFilters()">
      <option value="">All</option>
      <option value="green">✅ Autofix</option>
      <option value="yellow">⚠️ Guidance</option>
      <option value="red">🔴 Complex</option>
    </select>

    <span class="filter-count" id="filter-count"></span>
  </div>

  <!-- Violations Table -->
  <div class="tbl-wrap">
    <div class="tbl-scroll">
      <table id="main-table">
        <thead>
          <tr>
            <th data-col="appName" onclick="sortTable('appName')">
              App Name <span class="sort-arrow">▲▼</span>
            </th>
            <th data-col="violationTitle" onclick="sortTable('violationTitle')">
              Violation <span class="sort-arrow">▲▼</span>
            </th>
            <th data-col="cloud" onclick="sortTable('cloud')">
              Cloud <span class="sort-arrow">▲▼</span>
            </th>
            <th data-col="owner" onclick="sortTable('owner')">
              Owner <span class="sort-arrow">▲▼</span>
            </th>
            <th data-col="sla" onclick="sortTable('sla')">
              SLA <span class="sort-arrow">▲▼</span>
            </th>
            <th data-col="eta" onclick="sortTable('eta')">
              ETA <span class="sort-arrow">▲▼</span>
            </th>
            <th data-col="category" onclick="sortTable('category')">
              Category <span class="sort-arrow">▲▼</span>
            </th>
            <th>TSG</th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
      <div id="empty-state">No violations match your current filters.</div>
    </div>
  </div>

</div>

<div class="footer">
  SFI-TI 3.2.2 Tenant Isolation Violation Report · Generated by GitHub Copilot CLI · {GENERATED}
</div>

<script>
// ===================================================================
//  DATA — injected by the skill at generation time
// ===================================================================
const VIOLATIONS = {VIOLATIONS_JSON};

// ===================================================================
//  CLASSIFICATION HELPERS
// ===================================================================

// Severity sort order for table sorting
const SEVERITY_ORDER = { red: 0, yellow: 1, green: 2 };

// Severity label map
const SEVERITY_LABELS = {
  green:  'Autofix',
  yellow: 'Guidance',
  red:    'Complex'
};

// ===================================================================
//  UTILITY FUNCTIONS
// ===================================================================

function escHtml(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function truncate(s, max) {
  if (!s) return '';
  return s.length > max ? s.substring(0, max) + '…' : s;
}

function severityDotHtml(sev) {
  return '<span class="severity-dot dot-' + sev + '" title="' + (SEVERITY_LABELS[sev] || sev) + '"></span>';
}

function severityBadgeHtml(sev) {
  const label = SEVERITY_LABELS[sev] || sev;
  return '<span class="badge badge-' + sev + '">' + escHtml(label) + '</span>';
}

function appTypeBadgeHtml(type) {
  const cls = (type || '').toUpperCase() === '1P' ? 'badge-1p' : 'badge-3p';
  return '<span class="badge ' + cls + '">' + escHtml(type || '—') + '</span>';
}

// ===================================================================
//  POPULATE FILTER DROPDOWNS
// ===================================================================

// Violation titles
const violationTitles = [...new Set(VIOLATIONS.map(v => v.Title || v.ViolationTitle))].filter(Boolean).sort();
const violationSelect = document.getElementById('filter-violation');
violationTitles.forEach(t => {
  const o = document.createElement('option');
  o.value = t;
  o.textContent = truncate(t, 70);
  violationSelect.appendChild(o);
});

// Clouds
const clouds = [...new Set(VIOLATIONS.map(v => v.cloudType || v.AppCloudType))].filter(Boolean).sort();
const cloudSelect = document.getElementById('filter-cloud');
clouds.forEach(c => {
  const o = document.createElement('option');
  o.value = c;
  o.textContent = c;
  cloudSelect.appendChild(o);
});

// Remediation categories
const categories = [...new Set(VIOLATIONS.map(v => v.remediationCategory))].filter(Boolean).sort();
const categorySelect = document.getElementById('filter-category');
categories.forEach(c => {
  const o = document.createElement('option');
  o.value = c;
  o.textContent = c;
  categorySelect.appendChild(o);
});

// ===================================================================
//  RENDER TABLE ROWS
// ===================================================================

const tbody = document.getElementById('tbody');

VIOLATIONS.forEach((v, idx) => {
  const tr = document.createElement('tr');
  tr.dataset.idx           = idx;
  tr.dataset.violation      = v.Title || v.ViolationTitle || '';
  tr.dataset.cloud          = v.cloudType || v.AppCloudType || '';
  tr.dataset.category       = v.remediationCategory || '';
  tr.dataset.severity       = v.severity || '';
  tr.dataset.sortSeverity   = String(SEVERITY_ORDER[v.severity || 'yellow'] ?? 99);
  tr.dataset.search         = [
    v.AppDisplayName, v.AppId, v.Title || v.ViolationTitle,
    v.cloudType || v.AppCloudType, v.ActionOwnerAlias,
    v.SLAState, v.TargetId, v.remediationCategory
  ].join(' ').toLowerCase();

  // Severity-based row class
  tr.className = 'severity-' + (v.severity || 'yellow');

  // Sort-friendly data attributes
  tr.dataset.sortAppname    = (v.AppDisplayName || '').toLowerCase();
  tr.dataset.sortViolation = (v.Title || v.ViolationTitle || '').toLowerCase();
  tr.dataset.sortCloud     = (v.cloudType || v.AppCloudType || '').toLowerCase();
  tr.dataset.sortOwner     = (v.ActionOwnerAlias || '').toLowerCase();
  tr.dataset.sortSla       = (v.SLAState || '').toLowerCase();
  tr.dataset.sortEta       = (v.CurrentETA || '').toLowerCase();
  tr.dataset.sortCategory  = (v.remediationCategory || '').toLowerCase();

  tr.innerHTML = [
    // App Name
    '<td><div class="app-name">' + escHtml(v.AppDisplayName) + '</div>'
      + '<div style="font-size:.72rem;color:var(--muted)">'
      + escHtml(v.AppId || v.TargetId || '')
      + '</div></td>',

    // Violation Title
    '<td><div class="violation-title">' + escHtml(truncate(v.Title || v.ViolationTitle, 80)) + '</div></td>',

    // Cloud
    '<td><span class="cloud-tag">' + escHtml(v.cloudType || v.AppCloudType || '—') + '</span></td>',

    // Owner
    '<td><div class="state-text">' + escHtml(v.ActionOwnerAlias || '—') + '</div></td>',

    // SLA
    '<td><div class="state-text">' + escHtml(v.SLAState || '—') + '</div></td>',

    // ETA
    '<td><div class="state-text">' + escHtml(v.CurrentETA || '—') + '</div></td>',

    // Remediation Category
    '<td>' + severityBadgeHtml(v.severity) + '<div style="margin-top:3px;font-size:.75rem;color:var(--muted)">'
      + escHtml(v.remediationCategory || '') + '</div></td>',

    // TSG Link
    '<td>' + (v.tsgLink
      ? '<a class="tsg-link" href="' + escHtml(v.tsgLink) + '" target="_blank" rel="noopener">TSG ↗</a>'
      : '<span style="color:var(--muted)">—</span>') + '</td>'

  ].join('');

  tbody.appendChild(tr);
});

// ===================================================================
//  FILTERING
// ===================================================================

function applyFilters() {
  const q         = document.getElementById('search').value.toLowerCase();
  const violation = document.getElementById('filter-violation').value;
  const cloud     = document.getElementById('filter-cloud').value;
  const category  = document.getElementById('filter-category').value;
  const severity  = document.getElementById('filter-severity').value;

  let visible = 0;
  const rows = tbody.querySelectorAll('tr');

  rows.forEach(tr => {
    const matchSearch    = !q         || tr.dataset.search.includes(q);
    const matchViolation = !violation || tr.dataset.violation === violation;
    const matchCloud     = !cloud     || tr.dataset.cloud === cloud;
    const matchCategory  = !category  || tr.dataset.category === category;
    const matchSeverity  = !severity  || tr.dataset.severity === severity;

    const show = matchSearch && matchViolation && matchCloud && matchCategory && matchSeverity;
    tr.classList.toggle('hidden', !show);
    if (show) visible++;
  });

  document.getElementById('filter-count').textContent =
    visible + ' of ' + VIOLATIONS.length + ' violations';
  document.getElementById('empty-state').style.display =
    visible === 0 ? 'block' : 'none';
}

// Initialize filter count
applyFilters();

// ===================================================================
//  TABLE SORTING
// ===================================================================

let currentSort = { col: null, asc: true };

function sortTable(col) {
  const rows = Array.from(tbody.querySelectorAll('tr'));

  // Toggle direction if same column
  if (currentSort.col === col) {
    currentSort.asc = !currentSort.asc;
  } else {
    currentSort.col = col;
    currentSort.asc = true;
  }

  const dataAttr = 'sort' + col.charAt(0).toUpperCase() + col.slice(1);
  const dir = currentSort.asc ? 1 : -1;

  rows.sort((a, b) => {
    const va = a.dataset[dataAttr] || '';
    const vb = b.dataset[dataAttr] || '';
    if (va < vb) return -1 * dir;
    if (va > vb) return  1 * dir;
    return 0;
  });

  // Re-append sorted rows
  rows.forEach(r => tbody.appendChild(r));

  // Update sort arrow indicators
  document.querySelectorAll('th').forEach(th => th.classList.remove('sorted'));
  const activeTh = document.querySelector('th[data-col="' + col + '"]');
  if (activeTh) {
    activeTh.classList.add('sorted');
    const arrow = activeTh.querySelector('.sort-arrow');
    if (arrow) arrow.textContent = currentSort.asc ? '▲' : '▼';
  }
}

// Default sort: severity (red first), then app name
sortTable('severity');

// ===================================================================
//  VIOLATION COUNTER in header
// ===================================================================
document.getElementById('violation-counter').textContent =
  VIOLATIONS.length + ' violation' + (VIOLATIONS.length !== 1 ? 's' : '') + ' found';
</script>
</body>
</html>
```

---

## Step 4 — Save the report

Save the generated HTML file using a timestamped filename:

```powershell
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = ".\s360-ti322-report-$timestamp.html"
# ... write the HTML content to $reportPath ...
Set-Content -Path $reportPath -Value $htmlContent -Encoding UTF8
```

Then open in the default browser:

```powershell
Start-Process $reportPath
```

Report the full path to the user:
> "Report saved to: **{reportPath}**"

---

## Step 5 — Summary output

After generating the file and opening the browser, print a text summary:

```
📊 Generated: s360-ti322-report-{timestamp}.html
Total violations: {total}
  ✅ Autofix eligible: {autofixCount} (SG update scenarios)
  ⚠️  Guidance available: {guidanceCount} (cert rehoming, FIC setup)
  🔴 Complex remediation: {complexCount} (FIC/cross-tenant/connector)
Unique apps: {uniqueApps}
```

If 3+ violations are in the "red" (complex) category, list the top 3:
```
🚨 Most complex violations:
1. [{AppDisplayName}] {ViolationTitle} — {ActionOwnerAlias}
2. ...
3. ...
```

---

## Error handling

| Scenario | Response |
|---|---|
| No violation data provided | "No violation data. Run `fetch-violations` first." |
| Empty violations array | "No violations found for this target. Fully compliant 🎉" |
| File write failure | Report the error and suggest an alternate path |
| Unknown ViolationTitle | Classify as yellow severity, category "Unknown", no TSG link |

---

## Classification reference

Full mapping table for quick lookup during generation:

| ViolationTitle | Category | Severity | TSG |
|---|---|---|---|
| AAD Entra Apps in Prod Tenants using certificates in Non-Prod Tenant | Cert Rehoming | yellow | aka.ms/entraQ4 |
| AAD Entra Apps cloud mismatches with Cert Cloud | Cert Rehoming | yellow | aka.ms/entraQ5 |
| AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud auth scenarios | FIC Setup | yellow | aka.ms/entraQ5 |
| AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud 1P scenarios | FIC Setup | yellow | aka.ms/entraQ5 |
| 1pApp certs Tenant mismatches the Tenant of the Security Group | SG / Cert Decision | yellow | aka.ms/entraQ6 |
| AAD Entra apps with cross-tenant violations | Cross-Tenant | red | aka.ms/entraQ7 |
| Connector domain OWNER should not use shared subjectName for authentication across tenant | Connector | red | aka.ms/entraQ8 |
| Connector domain CONSUMER should not use shared subjectName for authentication across tenant | Connector | red | aka.ms/entraQ8 |
| 1P App with invalid security group | SG Update | green | aka.ms/entraQ9 |

---

## Key tools used

| Tool | MCP | Purpose |
|------|-----|---------|
| PowerShell (`Set-Content`, `Start-Process`) | — | Write HTML file, open browser |
| `fetch-violations` skill (upstream) | `s360-breeze` | Provides violation data input |
