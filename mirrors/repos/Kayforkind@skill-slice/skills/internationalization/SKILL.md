---
name: internationalization
description: "Plans multi-locale sites: language-plus-region codes, subfolder vs subdomain vs ccTLD URLs, reciprocal hreflang with self-canonicals, translation workflow, and currency/date/RTL adaptation. Use when adding locales, hreflang, or region-specific formats. Never force Accept-Language redirects; not for iOS .strings catalogs or App Store screenshot locales."
version: 1.0.1
---

## When to Use

- Adding the first non-English (or non-default) language to a site.
- Adding additional locales to an existing internationalized site.
- Choosing URL structure for languages (subfolders vs subdomains vs ccTLDs).
- Implementing hreflang tags and canonical strategies.
- Designing translation workflow and content mirroring strategies.
- Handling currency, date, time, and number formats.
- Designing or fixing layout for RTL (Right-to-Left) languages.
- Auditing an internationalization rollout that is underperforming.

## Prerequisites

Before starting, gather or confirm the following inputs:
- The locales in scope (language + region, e.g., `en-US`, `de-DE`, `fr-CA`).
- Business reason per locale (priority, audience size).
- Existing site architecture and CMS capabilities.
- Translation resources (in-house, agency, AI-assisted, community).
- Content volume and update frequency.

## Procedure

### 1. Decide Which Locales
Do not add languages just because you can. Each locale has an ongoing maintenance cost.
- **Audience research:** Where are visitors and prospects located?
- **Business priority:** Which markets are growth targets?
- **Content readiness:** Do you have the resources to maintain it?
- **Legal:** Do regulations require localization (GDPR, accessibility laws)?

### 2. Pick URL Structure
How locales are reflected in URLs. For most sites, subfolders are the default. Subdomains or ccTLDs only when there's a specific reason (legal, infrastructure, or brand).

| Pattern | Example | When to Use |
|---|---|---|
| ccTLD | example.de, example.fr | Strong country focus, distinct legal entities, willing to maintain separate domains |
| Subdomain | de.example.com, fr.example.com | Logical separation, willing to host separately, common for large sites |
| Subfolder | example.com/de/, example.com/fr/ | SEO equity unified, simplest to manage, default for most |
| URL parameter | example.com?lang=de | Avoid; weak SEO signal |

**Decide:**
- Language only (`/de/`) or language plus region (`/de-de/`, `/de-at/`, `/de-ch/`)?
- Default locale: at the apex (`example.com`) or in a folder (`example.com/en/`)?
  - *Note:* Default-locale-at-apex is common but causes hreflang complexity (the apex needs an `x-default` and the canonical for the default language).

### 3. Pick Content Structure
How content is organized across locales.
- **Pattern A: Mirror.** Every page in every locale. The translation IS the page. Suitable for marketing sites with controlled content.
- **Pattern B: Subset.** Some content in all locales, some only in select locales. Common for product pages (only available products), blog (some posts translated), or regulatory differences.
- **Pattern C: Local.** Each locale has its own content largely independent of other locales. Common for media or community sites.

*Most marketing sites are A. Most large sites end up at B by necessity. C is for sites with strong regional editorial.*

### 4. Set up hreflang and Canonicals
Implement before launching the second locale, even if it's just one extra page.

**hreflang** specifies the language and optional region for each version.
```html
<link rel="alternate" hreflang="en-US" href="https://example.com/en-us/page">
<link rel="alternate" hreflang="en-GB" href="https://example.com/en-gb/page">
<link rel="alternate" hreflang="de-DE" href="https://example.com/de-de/page">
<link rel="alternate" hreflang="x-default" href="https://example.com/en-us/page">
```

**Rules:**
- Every page lists every translated equivalent (including itself).
- Pages must reciprocate (page A says page B is its German version; page B says page A is its English version).
- `x-default` is the fallback for users in unspecified regions.
- Each page has its own canonical pointing to itself (not to the default language).
- hreflang can be in the HTML head, in HTTP headers, or in the XML sitemap. Sitemap is best for large sites; HTML head is fine for small.

### 5. Set up Translation Workflow
How content gets translated, kept fresh, and quality-controlled.
1. **Source content authored** in the source language.
2. **Translation requested** through a TMS (translation management system) or spreadsheet.
3. **Translation produced** with translation memory (avoids retranslating reused phrases).
4. **Review** by a second translator or in-region staff.
5. **Localization** beyond translation (currency, units, examples, cultural references).
6. **Publishing** in the destination locale.
7. **Update propagation** when source content changes.

*The TMS pays off above ~10K words of total content. Below that, spreadsheets and disciplined naming are fine.*

### 6. Localize Beyond Translation
For each locale, adapt the experience:
- **Currency:** Display in the local currency where applicable (EUR for European locales, JPY for Japanese). Don't show USD to French users.
- **Numbers:** Thousand separators and decimals differ (`1,000.50` in en-US is `1.000,50` in de-DE).
- **Dates and times:** Format and order vary. Use a date formatting library that respects locale.
- **Names and addresses:** Field order and required components differ. Use country-aware address forms.
- **Phone numbers:** E.164 international format universally; display formatting per locale.
- **Units:** Metric vs imperial.
- **RTL languages:** Arabic, Hebrew, Persian, Urdu. Layout flips. Use CSS logical properties (`margin-inline-start` instead of `margin-left`).
- **Cultural sensitivity:** Avoid hand gestures in product imagery. Avoid country-specific references unless localized.

### 7. Implement Language Switcher
- Prominent in the header or footer.
- Shows the current locale clearly.
- Lists all available locales in their own language ("Deutsch" not "German").
- Persists the choice (cookie or local storage).
- Doesn't auto-redirect based on browser; suggests instead.
- Try to land the user on the same page in the new locale, not the homepage.

### 8. Test
- Each locale renders correctly.
- hreflang links are valid (use a checker).
- Canonicals are self-referential per page.
- Currency and dates are correct.
- RTL layout is correct (for RTL locales).
- Language switcher works and persists.
- Search-engine perspective: each locale is crawlable and indexable.

### 9. Launch and Monitor
Per locale, monitor:
- Indexing rate.
- Traffic from intended geographies.
- Engagement metrics in the locale.
- Translation freshness (when did source content change without translation update?).

### 10. Maintain
- Translation update cadence (when source changes, when translations follow).
- Quarterly review of locale performance.
- Sunset locales that aren't viable (better than maintaining a dead locale poorly). Redirect old URLs to the closest equivalent in another supported language.

## Pitfalls

- **Auto-redirect based on browser language:** User is in Germany, prefers English. Site forces German. Suggest, don't redirect.
- **Single canonical to default language:** Search engines can't index the translations. Self-canonical per page.
- **Reciprocal hreflang missing:** German page lists English as its translation, English page doesn't list German. Search engines treat the relationship as unconfirmed.
- **hreflang language without region when region matters:** `hreflang="es"` is fine if there's one Spanish version. If you have es-ES (Spain) and es-MX (Mexico), use both with regions.
- **Auto-translated content treated as final:** Machine translation is an acceptable starting point. Human review is necessary for any user-facing content.
- **Currency baked into copy:** "$99/month" in body text breaks for European users. Use templated currency that adapts.
- **Hardcoded date formats:** "January 5, 2024" in code. Doesn't adapt. Use a date formatting library.
- **Field labels left in source language:** Translated body, untranslated form labels. Translate UI strings as part of localization.
- **Untranslated error messages:** User submits a form, gets an error in English on a French page. Translate UI states.
- **Untranslated emails:** Site is in French; transactional emails are English. Translate emails to match.
- **Forgotten locales in CMS:** Editors forget to update one locale. Drift. Use a TMS or workflow that surfaces drift.
- **Locale switcher that doesn't work mid-flow:** User is on the German checkout, switches to French, lands on French homepage. Try to land on the same page in the new locale.
- **RTL layouts that don't actually flip:** Margin and padding hardcoded for LTR. Use CSS logical properties.
- **Sunset language without redirect:** Discontinuing French; old French URLs 404. Redirect to the closest equivalent in another supported language.

## Verification

To verify the internationalization rollout:
1. **Crawl the site:** Use a crawler (e.g., Screaming Frog) to verify all hreflang tags are present, reciprocated, and valid.
2. **Check canonicals:** Ensure every locale page has a self-referential canonical.
3. **Visual check:** Manually verify currency, dates, and numbers render correctly per locale.
4. **RTL check:** If supporting RTL, verify layout flips correctly and no hardcoded LTR margins/paddings exist.
5. **Switcher test:** Change languages and verify the user lands on the equivalent page and the choice persists on reload.
6. **Search Console:** Check indexing status for each locale-specific URL pattern.

## Per-locale extras

Cover URL pattern, content mirroring, UX (switcher, RTL), formats (currency, dates, numbers), and legal copy in Procedure steps 2–7. This folder does not ship a separate locale checklist file. Official hreflang: https://developers.google.com/search/docs/specialty/international/localized-versions
