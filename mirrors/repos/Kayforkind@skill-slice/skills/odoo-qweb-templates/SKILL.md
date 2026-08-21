---
name: odoo-qweb-templates
description: "Writes server-side Odoo QWeb: `ir.actions.report` records, `t-foreach`/`t-field`/`t-if`, `t-out` versus `t-esc`, and `web.external_layout` PDF shells. Trigger when a Print menu report or QWeb email fails to render. Not for Kanban/Form JavaScript QWeb widgets. Never route stock valuation or warehouse routes here."
version: 1.0.1
risk: safe
source: self
---

# Odoo QWeb Templates

## Overview

QWeb is Odoo's primary server-side templating engine, used for PDF reports, website pages, and email templates. This skill generates correct, well-structured QWeb XML with proper directives, translation support, and report action bindings. It covers server-side QWeb only (not the JavaScript QWeb engine used in Kanban/Form widgets).

## When to Use

- Creating a custom PDF report (invoice, delivery slip, certificate, patient card).
- Building a QWeb email template triggered by workflow actions.
- Designing Odoo website pages with dynamic content.
- Debugging QWeb rendering errors (`t-if`, `t-foreach`, `t-field` issues).
- Binding an `ir.actions.report` record to a QWeb template.
- Migrating `t-esc` to `t-out` for Odoo 15+ upgrades.

## Prerequisites

- Odoo module development environment (Odoo 14+ recommended; directives differ between versions).
- Basic familiarity with XML data files and Odoo module structure (`__manifest__.py`, `reports/` directory).
- For PDF rendering: `wkhtmltopdf` installed and configured in Odoo system parameters.
- For testing: access to an Odoo instance with the target module installed or upgradeable.

Directive syntax, layout wrappers (`web.html_container`, `web.external_layout`, `web.internal_layout`), and email vs report variable scope (`object` vs `docs`) are in this file. Validate XML with the well-formedness check in Verification before upgrading the module.

## Procedure

### 1. Identify the Report or Template Requirements

Determine the following before generating any code:

- **Target model** (e.g., `hospital.patient`, `sale.order`).
- **Report type**: `qweb-pdf` (most common), `qweb-html`, or email template.
- **Odoo version**: affects directive choices (`t-out` for 15+, `t-esc` for 14 and below).
- **Fields to display** and any conditional logic needed.
- **Layout**: `web.external_layout` for customer-facing PDFs (includes company header/footer/logo), `web.internal_layout` for internal documents.

### 2. Create the Report Action Record

Place this in your module's data file (typically `reports/report_patient_card.xml` or similar):

```xml
<record id="action_report_patient_card" model="ir.actions.report">
    <field name="name">Patient Card</field>
    <field name="model">hospital.patient</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">hospital_management.report_patient_card</field>
    <field name="binding_model_id" ref="model_hospital_patient"/>
</record>
```

Key fields:
- `report_name` must match the template `id` prefixed with the module name: `module_name.template_id`.
- `binding_model_id` makes the report appear in the Print menu of the target model's views.
- `report_type` is `qweb-pdf` for PDF output or `qweb-html` for HTML.

### 3. Create the QWeb Template

Place the template in the same data file or a separate template file:

```xml
<template id="report_patient_card">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Patient Card</h2>
                    <table class="table table-bordered">
                        <tr>
                            <td><strong>Name:</strong></td>
                            <td><t t-field="doc.name"/></td>
                        </tr>
                        <tr>
                            <td><strong>Doctor:</strong></td>
                            <td><t t-field="doc.doctor_id.name"/></td>
                        </tr>
                        <tr>
                            <td><strong>Status:</strong></td>
                            <td><t t-field="doc.state"/></td>
                        </tr>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```

### 4. Register the Data File in `__manifest__.py`

```python
{
    'name': 'Hospital Management',
    'version': '17.0.1.0.0',
    'depends': ['web'],
    'data': [
        'reports/report_patient_card.xml',
    ],
}
```

### 5. Upgrade the Module

On Windows (PowerShell), upgrade the module from the Odoo shell or command line:

```powershell
# From the Odoo installation directory
python odoo-bin -c odoo.conf -d your_database -u hospital_management --stop-after-init
```

Or from the Odoo web UI: Apps → Update Apps List → upgrade the module.

### 6. Test the Report

1. Navigate to the target model's list or form view.
2. Select one or more records.
3. Click **Print** → **Patient Card** (the report name from the action record).
4. Verify the PDF renders correctly with company header/footer.

### 7. Debugging Broken Templates

If a template fails to render:

1. **Check Odoo logs** for QWeb compilation errors (usually syntax or undefined variable).
2. **Validate XML** — ensure the file is well-formed:
   ```powershell
   # If python is available
   python -c "import xml.dom.minidom; xml.dom.minidom.parse('reports/report_patient_card.xml'); print('XML is well-formed')"
   ```
3. **Common fixes**:
   - Missing `t-as` on `t-foreach` — add `t-as="doc"` or appropriate alias.
   - Using `t-esc` where HTML output is intended — switch to `t-out` (Odoo 15+) or restructure.
   - Referencing `docs` in an email template — email templates use `object`, not `docs`.
   - Field not displaying — ensure the field exists on the model and the record has a value.

## Examples

### Example 1: Conditional Rendering with `t-if`

```xml
<!-- Show a warning block only if the patient is not confirmed -->
<t t-if="doc.state == 'draft'">
    <div class="alert alert-warning">
        <strong>Warning:</strong> This patient has not been confirmed yet.
    </div>
</t>
```

### Example 2: Iterating Over a One2many Field

```xml
<!-- Display all appointments for a patient -->
<t t-foreach="doc.appointment_ids" t-as="apt">
    <tr>
        <td><t t-field="apt.date"/></td>
        <td><t t-field="apt.doctor_id.name"/></td>
        <td><t t-field="apt.state"/></td>
    </tr>
</t>
```

### Example 3: Safe HTML Output (Odoo 15+)

```xml
<!-- t-out renders HTML without escaping; use for trusted content only -->
<t t-out="doc.description_html"/>
```

For Odoo 14 and below, `t-esc` HTML-escapes output (prints tags as raw text). Use `t-raw` for unescaped output on Odoo 14, but be aware of XSS risks.

### Example 4: Report with `_get_report_values` Helper

Python model method to pre-compute values:

```python
from odoo import models


class PatientCardReport(models.AbstractModel):
    _name = 'report.hospital_management.report_patient_card'
    _description = 'Patient Card Report'

    def _get_report_values(self, docids):
        docs = self.env['hospital.patient'].browse(docids)
        return {
            'docs': docs,
            'is_confirmed': lambda doc: doc.state != 'draft',
        }
```

Then in the template:

```xml
<t t-if="is_confirmed(doc)">
    <span class="badge badge-success">Confirmed</span>
</t>
```

## Pitfalls

- **Missing `t-as` on `t-foreach`**: Without `t-as="doc"`, you cannot access the current record inside the loop body. This is the most common QWeb error.
- **Using `t-esc` for HTML content**: `t-esc` HTML-escapes output, printing tags as raw text. Use `t-out` (Odoo 15+) for safe HTML rendering of trusted content. On Odoo 14, use `t-raw` with caution.
- **Email template variable scope**: Email QWeb templates use `object` (the single record), not `docs` (the recordset). Mixing these causes silent rendering failures.
- **Raw Python in QWeb**: Do not embed complex Python expressions in QWeb attributes. Compute values in the model or in a `_get_report_values()` helper method. QWeb is for presentation, not business logic.
- **Forgetting `web.html_container`**: Without `t-call="web.html_container"`, the PDF will lack proper HTML document structure and may render as a blank or broken page.
- **Template ID mismatch**: The `report_name` field in the action record must exactly match `module_name.template_id`. A mismatch results in "template not found" errors.
- **Not upgrading the module**: After adding or modifying report XML, the module must be upgraded for changes to take effect. Simply restarting Odoo is not sufficient.
- **`t-field` on non-field values**: `t-field` only works on actual model field records. For computed or derived strings, use `t-out` or `t-esc`.
- **Translation strings inline**: Use `_lt()` (lazy translation) for translatable string literals inside Python report helpers, not inline `t-esc` with hardcoded strings.

## Verification

### Verify XML Well-Formedness

```powershell
python -c "import xml.dom.minidom; xml.dom.minidom.parse('reports/report_patient_card.xml'); print('XML is well-formed')"
```

Expected output:
```
XML is well-formed
```

### Verify Module Upgrade Succeeds

```powershell
python odoo-bin -c odoo.conf -d your_database -u hospital_management --stop-after-init
```

Check Odoo logs for errors. A successful upgrade shows no traceback and the module loads cleanly.

### Verify Report Action Exists

In the Odoo web UI or shell:

```python
# Odoo shell
env['ir.actions.report'].search([('report_name', '=', 'hospital_management.report_patient_card')]).name
```

Expected output:
```
'Patient Card'
```

### Verify Template Renders

1. Open a record of the target model in Odoo.
2. Click **Print** → **Patient Card**.
3. Confirm the PDF downloads and displays:
   - Company header and footer appear (from `web.external_layout`).
   - All `t-field` values render with proper formatting.
   - Conditional blocks (`t-if`) show or hide correctly based on record state.
   - Loop blocks (`t-foreach`) iterate over all related records.

### Verify No QWeb Compilation Errors in Logs

After triggering the report, check the Odoo log file for any `qweb` or `ValueError` entries:

```powershell
# On Windows, tail the log file (adjust path to your Odoo log location)
Get-Content -Path "C:\odoo\odoo.log" -Tail 50 | Select-String "qweb|ValueError|template"
```

No matches (or only INFO-level entries) indicates clean compilation.

## Limitations

- Does not cover **website controller routing** for dynamic QWeb pages — that requires Python `http.route` knowledge and controller classes.
- **Email template** QWeb has different variable scope than report QWeb (`object` vs `docs`) — this skill primarily focuses on PDF reports; keep email templates on `object`, not `docs`.
- QWeb JavaScript (used in Kanban/Form widgets) is a different engine; this skill covers **server-side QWeb only**.
- Does not cover **wkhtmltopdf configuration** for PDF rendering issues (page size, margins, header/footer overlap, missing CSS).
- Does not cover **multi-company report layouts** or company-specific template overrides via `ir.actions.report` inheritance.

## Related Skills

- `odoo-module-structure` — for module scaffolding, `__manifest__.py`, and data file registration.
- `odoo-models-orm` — for model methods, `_get_report_values()`, and field definitions.
- `odoo-views-xml` — for form/list/kanban views that include Print menu bindings.
