---
name: email-template-developer
description: "Use this skill when working on email, SMS, or push notification templates — authoring Handlebars HTML email templates, understanding the backend template engine, visual testing with Playwright, or managing multi-tenant template deployment. Triggers on: body.hbs.html, subject.hbs.txt, Handlebars email templates, notification templates, email branding, _MASTER_TEMPLATE, template screenshots, Playwright visual regression, notification tenancy, template blob storage, EMAIL/SMS/PUSH channels, or cross-client HTML email compatibility."
---

# Email Template Developer

Author and maintain notification templates across the Handlebars template ecosystem. Covers template authoring conventions, HTML email constraints, visual testing, backend template processing, and multi-tenant deployment.

> **Scope**: Template authoring and backend template engine understanding. For general backend service work, use the `backend-developer` skill.

## Repositories

<!-- TODO: Replace with your actual repository locations -->
| Repo | Location | Purpose |
|---|---|---|
| Notification-Templates | <!-- TODO: Add location --> | Template authoring, Handlebars HTML, visual testing |
| Notification-Service | <!-- TODO: Add location --> | Backend notification service, template engine, tenant config |

## Template Directory Structure

```
Notification-Templates/
├── .github/
│   ├── instructions/
│   │   └── copilot.instructions.md     # HTML email development guidelines
│   └── prompts/
│       ├── create_new_template.prompt.md
│       ├── create_screenshots.prompt.md
│       └── validate_urls.prompt.md
├── Templates/
│   ├── EMAIL/
│   │   ├── _MASTER_TEMPLATE/           # Base for ALL new templates
│   │   │   ├── DE/body.hbs.html + subject.hbs.txt
│   │   │   ├── EN/body.hbs.html + subject.hbs.txt
│   │   │   ├── FR/body.hbs.html + subject.hbs.txt
│   │   │   └── IT/body.hbs.html + subject.hbs.txt
│   │   └── <TEMPLATE_NAME>/
│   │       ├── DE/body.hbs.html + subject.hbs.txt
│   │       ├── EN/body.hbs.html + subject.hbs.txt
│   │       ├── FR/body.hbs.html + subject.hbs.txt
│   │       └── IT/body.hbs.html + subject.hbs.txt
│   ├── SMS/
│   │   └── <TEMPLATE_NAME>/
│   │       └── <LANG>/body.hbs.txt
│   ├── PUSH/
│   │   └── <TEMPLATE_NAME>/
│   │       └── <LANG>/body.hbs.txt + title.hbs.txt
│   ├── DEFINITION/
│   │   ├── _MASTER_TEMPLATE.json
│   │   └── <TEMPLATE_NAME>.json
│   └── global_testdata.json            # Shared test data for all templates
├── package.json                         # Node.js: handlebars, playwright, pixelmatch
└── playwright.config.js                 # Chromium, 800x1200 viewport, threshold 0.2
```

## Golden Rules

1. **ALWAYS use `_MASTER_TEMPLATE` as base** for new email templates — never start from scratch.
2. **4 languages always**: DE, EN, FR, IT — every template must have all 4 language variants.
3. **No translations in `body.hbs.html`** — the HTML body structure is identical across languages. Only `subject.hbs.txt` differs per language.
4. **Preserve block comment anchors** — comments like `<!-- Content 1-spaltig -->`, `<!-- Address block -->` serve as structural markers and must be kept.
5. **Stay under ~100kB** per template to avoid Gmail truncation.

## Existing Copilot Prompts

The repo includes pre-built prompts in `/.github/prompts/` — use them instead of reinventing workflows:

| Prompt | Purpose |
|---|---|
| `/create_new_template` | Copy `_MASTER_TEMPLATE` → new template, set subjects per language |
| `/create_screenshots` | Replace placeholders with `global_testdata.json`, generate Playwright screenshots to `/.temp/` |
| `/validate_urls` | Check all template URLs per language, output CSV to `/.temp/URL_Validation_Results.csv` |

### Creating a New Template (Workflow)

1. Copy `/Templates/EMAIL/_MASTER_TEMPLATE/` → `/Templates/EMAIL/<NEW_NAME>/`
2. Copy `/Templates/DEFINITION/_MASTER_TEMPLATE.json` → `/Templates/DEFINITION/<NEW_NAME>.json`
3. Update subjects in each `subject.hbs.txt` per language
4. Update `<title>` tags in each `body.hbs.html`
5. Replace `_MASTER_TEMPLATE` references with the new template name
6. Modify HTML body content as needed (same structure across all languages)
7. Generate screenshots and validate

## HTML Email Constraints

### Cross-Client Compatibility

Target clients (last 24 months): **Apple Mail, Outlook (classic + new), Gmail, Yahoo Mail**.

| Constraint | Rule |
|---|---|
| Layout | Table-based responsive, `max-width: 620px` |
| Background | `background-color: #f4f4f4` outer wrapper |
| Buttons | Bulletproof (VML fallback for Outlook), min `44×44px` tap target |
| Contrast | WCAG AA minimum |
| Format detection | `x-ms-format-detection="none"` to suppress auto-linking |
| Outlook conditionals | `<!--[if mso]>` and `<!--[if !mso]><!--> ... <!--<![endif]-->` |
| Dark mode | `color-scheme: light dark`, `prefers-color-scheme` media query, neutral base palette |
| Validation | Audit against [Can I Email](https://www.caniemail.com/) before finalizing |

### Template HTML Structure

```html
<!-- Typical block structure (simplified) -->
<table role="presentation" width="100%" style="background-color: #f4f4f4;">
  <tr><td align="center">
    <table width="620" style="max-width: 620px;">
      <!-- Logo -->
      <!-- Content 1-spaltig -->
      <!-- Content 2-spaltig (optional) -->
      <!-- Address block -->
      <!-- Disclaimer -->
    </table>
  </td></tr>
</table>
```

### Size Optimization

Keep templates compact. Refactor verbose markup into block-based structure. Remove redundant inline styles by consolidating shared styles. Minimize whitespace in production templates.

## Brand Colors

<!-- TODO: Replace with your organization's brand colors -->
| Name | RGB | Hex |
|---|---|---|
| primary-red | `rgb(216, 32, 52)` | `#D82034` |
| anthrazit | `rgb(53, 53, 53)` | `#353535` |
| white | `rgb(255, 255, 255)` | `#FFFFFF` |
| light-grey | `rgb(244, 244, 244)` | `#F4F4F4` |
| warm-grey | `rgb(189, 183, 175)` | `#BDB7AF` |
| dark-warm-grey | `rgb(148, 142, 136)` | `#948E88` |
| sand | `rgb(233, 227, 218)` | `#E9E3DA` |
| burgundy | `rgb(147, 25, 66)` | `#931942` |
| midnight-blue | `rgb(31, 51, 84)` | `#1F3354` |
| forest-green | `rgb(81, 117, 95)` | `#51755F` |
| ocean-blue | `rgb(72, 122, 150)` | `#487A96` |
| petrol | `rgb(47, 107, 109)` | `#2F6B6D` |
| clay | `rgb(190, 135, 100)` | `#BE8764` |
| mauve | `rgb(162, 128, 148)` | `#A28094` |
| golden-yellow | `rgb(209, 168, 70)` | `#D1A846` |

## Handlebars Syntax

### Placeholders

```handlebars
{{ Salutation }}
{{ FirstName }}
{{ LastName }}
```

### Conditionals

```handlebars
{{#if DisplayDebugInfo}}
  <p>Debug: {{Environment}}-{{NotificationId}}</p>
  {{#if RobotSessionId}}Robot: {{RobotSessionId}}{{/if}}
{{/if}}
```

### Iteration

```handlebars
{{#each Docs}}
  <tr><td>{{Name}}</td><td>{{Date}}</td></tr>
{{/each}}
```

### Test Data

All placeholders map to keys in `Templates/global_testdata.json`. This file contains ~100+ fields including:
- `Salutation` (per-language variants: "Sehr geehrter Herr", "Dear Mr", "Cher Monsieur", "Gentile Signor")
- `FirstName`, `LastName`, personal data fields
- `Docs` array, `EV_Contracts`, `ThreeAStart` data
- `DisplayDebugInfo`, `Environment`, `NotificationId`, `RobotSessionId`

When creating screenshots, resolve placeholders with this test data. Handle language-specific overrides (e.g., Salutation changes per language).

## Visual Testing

### Playwright Screenshots

```bash
npm run screenshots    # Generate screenshots for all templates
npm test              # Run Playwright visual regression tests
npm run test:update   # Update baseline snapshots
npm run test:ui       # Interactive Playwright UI
npm run test:report   # View HTML report
```

- **Viewport**: 800×1200, Chromium only
- **Comparison**: `pixelmatch` with threshold `0.2`, binary mode
- **Output**: Screenshots saved to `/.temp/<TEMPLATE_NAME>_<LANG>.png`
- **Process**: Replace Handlebars placeholders with `global_testdata.json` data → render in Playwright → capture full-page screenshot

### Section Testing

Use [testi.at](https://testi.at/) for testing individual sections or new components before integrating them into a full template.

## Backend Template Engine

### File Name Constants (WellKnown.cs)

```
EMAIL:  body.hbs.html + subject.hbs.txt
SMS:    body.hbs.txt
PUSH:   body.hbs.txt + title.hbs.txt
```

Folder names: `EMAIL`, `SMS`, `PUSH`, `DEFINITION`

### Two Template Engines

| Engine | Type | When Used |
|---|---|---|
| **Handlebars** | File-based (Blob Storage) | Default for all channels and content types |
| **Render** | API-based | Email channel only, when `application` is specified and tenant has Render configured |

**Selection logic** (`TemplateEngineSelector`):
- Render: Email + non-null application + tenant has Render config → uses Render
- Handlebars: everything else (fallback for all channels)
- No cross-engine fallback — if the selected engine fails, the request fails

### Handlebars Processing Chain

```
Request → TemplateEngineSelector
  → TenantAwareTemplateResolver (resolve tenant config)
    → HandlebarsTemplateRepository (fetch from Azure Blob Storage)
      → HandlebarsCompiledTemplatesCache (memory cache: 24h absolute / 1h sliding)
        → HandlebarsContentParser.ParseAsync(tenantId, templateKey, data)
          → HandlebarsDotNet compilation + rendering
```

### Blob Storage Path

Templates stored at: `{channel}/{TEMPLATE_NAME}/{languageCode}/{fileName}`

Example: `EMAIL/ADDRESS_CHANGE_NOTIFICATION/DE/body.hbs.html`

### Backend Models

```csharp
// Core template types
record EmailTemplate(TemplateCompositeKey Id, string SubjectTemplate, string BodyTemplate);
record TemplateCompositeKey(string TemplateName, string LanguageCode);
record TemplateKey(string TemplateName, string LanguageCode, ChannelType ChannelType, ContentFieldType ContentFieldType);

// Enums
enum ChannelType { Email, Sms, Push }
enum ContentFieldType { Body, Subject }
```

## Multi-Tenant Architecture

### Tenants

<!-- TODO: Replace with your actual tenant configuration -->
| Tenant | ID | Default Lang | Supported Languages |
|---|---|---|---|
| TenantA | `tenanta` | de | de, fr, it, en |
| TenantB | `tenantb` | de | de, fr, it, en |
| TenantC | `tenantc` | de | de, fr, it, en |

Each tenant has:
- **Isolated blob storage** for templates (own container)
- **Own provider configuration** (SendGrid, Twilio, template engines)
- **Feature flags** controlling which channels are enabled

### Template Provider Configuration

```csharp
Templates = new TemplateProvidersConfiguration
{
    RenderDebugInfo = "Tenants:{TenantId}:ProvidersConfiguration:Templates:RenderDebugInfo",
    Handlebars = new HandlebarsTemplateProviderConfiguration
    {
        BlobStorage = new BlobStorageConfiguration
        {
            ConnectionString = "Tenants:{TenantId}:...:BlobStorage:ConnectionString",
            Url = "Tenants:{TenantId}:...:BlobStorage:Url",
            ContainerName = "templates"
        }
    },
    Render = new RenderTemplateProviderConfiguration  // Optional, Email-only
    {
        TenantName = "chid",
        Applications = []  // Empty = allow all
    }
}
```

### Template Deployment

1. **Create** templates in the Notification-Templates repo
2. **Test** with Playwright screenshots and `global_testdata.json`
3. **Upload** to tenant-specific Azure Blob Storage
4. **Verify** by sending test notifications in the tenant context

Deployment methods:
- Azure Storage Explorer (manual)
- CI/CD pipeline with Azure CLI
- Notification CLI tool (`notification-cli publish`)

### API Tenancy Requirements

All Notification API requests require:
- **Header**: `X-Tenant-Id: {tenant-id}`
- **OAuth scopes**: `api.notification.access` + `notification.tenant.{tenant-id}`

## SMS & Push Templates

### SMS Template Pattern

```handlebars
Your verification code is: {{Code}}
{{#if DisplayDebugInfo}}
{{Environment}}-{{NotificationId}}
{{#if RobotSessionId}}Robot:{{RobotSessionId}}{{/if}}
{{/if}}
```

### Push Template Pattern

- `title.hbs.txt` — notification title
- `body.hbs.txt` — notification body

Both use same Handlebars syntax as email templates, without HTML.

## Common Pitfalls

1. **Starting from scratch** instead of `_MASTER_TEMPLATE` — always copy the master.
2. **Translating body HTML** — the body structure is language-independent; only subjects differ.
3. **Missing a language** — every template needs DE, EN, FR, IT.
4. **Ignoring Outlook** — always test MSO conditional comments and VML button fallbacks.
5. **Gmail truncation** — keep total HTML under ~100kB.
6. **Forgetting debug info block** — include `{{#if DisplayDebugInfo}}` section for diagnostics.
7. **Wrong file names** — must be exactly `body.hbs.html` and `subject.hbs.txt` (backend `WellKnown.cs` constants).
8. **Missing test data keys** — verify all placeholders exist in `global_testdata.json` before generating screenshots.
