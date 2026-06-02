# AEM Content Localization & i18n

## Purpose
Implement multi-language content management including translation workflows, language copy management, i18n dictionaries, and locale-specific content delivery in AEM.

## When to Use (Triggers)
- User mentions "localization," "i18n," "translation," "language copy," or "multi-language"
- References to `/content/<site>/language-masters/`, i18n dictionaries, or locale codes
- Questions about translation connectors, translation memory, or language fallback
- Requests involving regional content variation or multi-locale site structure
- File paths containing locale identifiers (en, fr, de, ja) in content paths

## Core Capabilities
- Design multi-language site structures using language masters and copies
- Configure translation integration framework (TIF) with translation providers
- Implement i18n dictionaries for UI string translation
- Set up translation projects with human and machine translation workflows
- Configure locale detection and language switching for end users

## Domain Knowledge Required
### Technical Foundation
- AEM Translation Integration Framework (TIF) architecture
- Language copy vs. Live Copy vs. independent translation models
- Sling i18n ResourceBundleProvider and dictionary structure
- ICU message format and pluralization handling
- Locale detection: Accept-Language header, URL, cookie, geo-IP

### AEM-Specific Context
- Language Master pattern and language root configuration
- Translation projects in AEM Projects console
- Translation connectors (human, machine, hybrid)
- Translation memory and glossary management
- Multi-Site Manager (MSM) interaction with language copies
- Content Fragment translation and variation handling

## Implementation Approach
### Step 1: Language Architecture
Design the multi-language site structure.
- Define language master site and its role (source of truth)
- Plan language/locale hierarchy (language → country: en → en-us, en-gb)
- Determine translation model (language copy, MSM, or independent)
- Configure language roots with correct `jcr:language` properties

### Step 2: Translation Framework Configuration
Set up translation provider integration.
- Install and configure translation connector (Adobe Translation, custom TMS)
- Define translation rules (`translation_rules.xml`) for content inclusion/exclusion
- Configure translation workflow: human, machine, or hybrid approach
- Set up translation memory and glossary resources

### Step 3: i18n Dictionary Setup
Implement UI string externalization.
- Create Sling i18n dictionaries under `/apps/<project>/i18n/`
- Define dictionary structure with `mix:language` and `sling:basename`
- Externalize all UI strings from HTL templates using `${'key' @ i18n}`
- Handle pluralization and parameterized messages

### Step 4: Translation Workflow Execution
Manage the translation process end-to-end.
- Create translation projects from language master changes
- Configure translation scope (new content, updated content, or all)
- Implement review/approval workflow for translated content
- Handle translation delivery and import into AEM

### Step 5: Locale-Aware Delivery
Configure content serving based on user locale.
- Implement language detection and redirect logic
- Configure dispatcher URL mapping for locale-prefixed paths
- Set up language switcher component with available locales
- Handle fallback behavior for missing translations

## Quality Checklist
- [ ] All UI strings externalized — no hardcoded text in HTL templates
- [ ] Language copies maintain correct structure mapping to source
- [ ] Translation rules exclude non-translatable content (paths, codes)
- [ ] Translated content reviewed by native speakers before publication
- [ ] Locale detection works correctly across all entry points
- [ ] Fallback language configured for missing translations
- [ ] Right-to-left (RTL) layout supported for applicable locales
- [ ] Date, number, and currency formatting locale-aware

## Related Skills
- aem-msm-multi-site-manager (MSM with language copies)
- aem-content-strategy-architecture (content model for localization)
- aem-replication-publishing (publishing language-specific content)

## Example Use Cases
1. **Global Product Launch:** Translate 300 product pages from English into 12 languages with machine translation for initial draft, human review for customer-facing copy, and synchronized go-live across all markets.
2. **Legal Compliance Localization:** Implement region-specific legal disclaimers and privacy policies with strict translation accuracy requirements, legal team review workflow, and version tracking per locale.
3. **Mixed-Content Multilingual Site:** Build a platform where some content is fully translated, some is shared across locales (global media assets), and some is locale-exclusive (local events), with proper fallback behavior.

## Notes
- Language copies and Live Copies serve different purposes — language copies don't inherit content updates automatically
- AEM's translation framework supports incremental translation — only changed content is re-submitted
- i18n dictionaries are code artifacts (under `/apps/`) while translated content lives under `/content/`
- RTL languages (Arabic, Hebrew) require both content translation and CSS layout changes
