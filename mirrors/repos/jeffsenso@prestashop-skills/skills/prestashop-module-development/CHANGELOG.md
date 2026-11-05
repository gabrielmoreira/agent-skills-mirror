# Changelog

All notable changes to the PrestaShop Module Development skill — **full history**.
The package-level `CHANGELOG.md` (repository root) only summarises each release and points here.

Format: date-based releases (`YYYY-MM-DD`). Each entry lists the change type (Added, Changed, Deprecated,
Removed, Fixed, Security), the file or feature affected (**bold**), and what changed and why.

## [2026-11-03] - Grid JS: generic core-based init script (PS 8.0+ / 9.x)

### Changed
- **scripts/grid.bundle.js** - Replaced the minified webpack bundle with a short readable init script (same file name)
  - Uses the core `window.prestashop.component.Grid` and `GridExtensions` exposed by the back office theme — same API in PrestaShop 8.0.0, 8.1.0, 8.2.0 and 9.0.0 (checked in the core sources), tested live on 9.1.4
  - Copied as `views/js/{modulename}.bundle.js` with **no edit**: no grid ID, no `sed`; initialises every `.js-grid[data-grid-id]` of the page (multi-grid pages work)
  - Adds FiltersReset, FiltersSubmitButtonEnabler, Sorting, ReloadList, ExportToSqlManager, SubmitGridAction, LinkRowAction, SubmitRowAction, BulkActionCheckbox, SubmitBulkAction, AsyncToggleColumn, and PositionExtension only when the grid has a position column
  - Initialises in a jQuery ready callback (never `DOMContentLoaded`, which runs before the theme creates the components); `data-grid-initialized` guard against double inclusion; never adds `ColumnTogglingExtension` (double toggle requests)
- **references/grid-system.md** - "JS bundle setup" rewritten as "Grid JS setup" (extension table, init timing, upgrade path for old bundles); "How sort, search and reset actually work", diagnosis checklist, Twig `javascripts` block, gotchas and position drag-and-drop FAQ updated; grid-ID-in-bundle instructions removed
- **references/debugging.md** - Grid troubleshooting rows for script not loaded / not initialised, `DOMContentLoaded` timing, double toggle handlers, and old copied webpack bundles
- **references/legacy-conversion.md**, **SKILL.md**, **README.md** - Point to the generic grid script instead of the pre-built bundle

### Fixed
- The previous webpack template contained only 20 of its 22 modules: positional module indexes were shifted, so its private bootstrap never ran — delete row, reset search, refresh list, show SQL query, row links and bulk actions silently did nothing while sort still worked. A repaired 22-module version (2026-10-08, used by wsimageslider) was superseded by the core-based script. Modules that ship a copied bundle should overwrite their `views/js/*.bundle.js` with the new `scripts/grid.bundle.js` (file name and `<script>` tag unchanged).

## [2026-10-06] - Grid Sort / Reset Troubleshooting

### Changed
- **grid-system.md** - Documented why sort and reset silently do nothing
  - Grid ID verification step after the `sed` replacement (`grep -c` on `GRID_ID_PLACEHOLDER` and the real ID)
  - Bundles copied from another module keep that module's literal grid ID in the minified bootstrap — how to find and fix it
  - New section "How sort, search and reset actually work": private webpack bootstrap vs `$(document).ready` block, search as a plain form POST
  - Quick diagnosis checklist and new gotchas (`SortingExtension` with `ReorderPositionsButtonType`, `FiltersResetExtension`, `searchAction()` 3rd argument)
- **scripts/grid.bundle.js** - Minor fix
- *Superseded by 2026-11-03* (the webpack template itself was broken)


## [2026-08-25] - Configuration Management, Modern Config Route

### Added
- **configuration-management.md** - Mandatory YAML-based configuration pattern (single source of truth)
  - `config_data/module.yml` holds every configuration key and its default value
  - `ConfigurationInstaller` service for install/uninstall of configuration values
  - `ConfigurationManager` service to read configuration (database, YAML fallback)
  - Never call `Configuration::updateValue()` / `Configuration::get()` directly in business logic

### Changed
- **SKILL.md** - New section 1b "Configuration variable management"; `getContent()` must redirect with the Symfony router (`$this->get('router')->generate(...)` + `Tools::redirectAdmin()`)
- **module-class-and-installer.md** - Installer delegates configuration values to `ConfigurationInstaller`

## [2026-08-12] - Installer Pattern, Config Form DI, Front Media, Translations

### Added
- **configuration-page.md** - Mandatory FormHandler pattern with constructor dependency injection; why the controller's limited service locator requires DI instead of `$this->get()`
- **services-and-di.md** - Controller limited service locator section: controllers only reach core Symfony services via `$this->get()`; complete constructor DI pattern; controller registration (`public: true` + `controller.service_arguments` tag)
- **translations.md** - Front-office Smarty translations: use `{l}` directly in templates, never pass pre-translated strings from PHP (extraction, context, standard pattern)

### Changed
- **SKILL.md** - Mandatory installer pattern
  - `install()` calls `parent::install()` first with an explicit check, then delegates to the Installer
  - `uninstall()` calls the Installer first, then `parent::uninstall()` (`&&` chaining)
  - Hooks and tabs as class property arrays (`private array $hooks`, `private array $tabs`), parent group tab auto-installation, never `getTabs()` in the module class
- **SKILL.md** - Configuration page now 5 classes (FormHandler added) with constructor DI; FormType registration (`parent: 'form.type.translatable.aware'`, `form.type` tag)
- **SKILL.md** - Front-office CSS/JS: always `actionFrontControllerSetMedia` with `registerStylesheet()` / `registerJavascript()`, never `header` / `displayHeader`
- **SKILL.md** - `WidgetInterface`: no explicit `hookDisplayXxx()` methods, PrestaShop calls `renderWidget()`; Smarty `{l s='…' d='Modules.Modulename.Front'}` in templates
- **SKILL.md** - Skill file header fix (2026-08-11)
- **module-class-and-installer.md** - Complete rewrite around the mandatory install/uninstall pattern; tabs and hooks as structured class property arrays; all tab logic in the Installer
- **hooks-and-front-office.md** - Front-office media registration rules and `WidgetInterface` patterns

## [2026-08-10] - CategoryChoiceTreeType Self-Contained Documentation

### Changed
- **SKILL.md** - Embedded complete CategoryChoiceTreeType documentation directly in section 2
  - Removed external steering file reference for core feature documentation
  - Added comprehensive inline guidance: valid form options, template requirements, JavaScript initialization, form data handling, and common issues
  - Makes skill more self-contained and reduces dependency on external steering files
  - Documentation now includes all critical details: form theme declaration, JS bundle setup with `window.prestashop.component.ChoiceTree`, selector patterns, and troubleshooting table

## [2026-06-03] - Documentation Updates, Security Clarification

### Changed
- **SKILL.md** - Clarified PS9 Core Documentation section to address Snyk security audit warning
  - Emphasized that ps9-core-ai files are pre-bundled and static (not downloaded at runtime)
  - Reworded `lotr --install` reference as maintenance-only task for skill maintainers
  - Removed suggestion of runtime external dependency to resolve W012 MEDIUM security warning
- **README.md** - Created comprehensive skill overview
- **CHANGELOG.md** - Created complete change history

## [2026-06-03] - Cart Rules, Order LoggableInterface, Console Commands

### Added
- **cart-rules.md** - Complete reference for creating and managing PrestaShop cart rules (vouchers, discount codes)
  - Code generation patterns (character set, uniqueness validation)
  - Multilingual name handling
  - Customer-specific vouchers
  - Reduction types (percent, amount, free shipping, gift product)
  - Common use cases with examples
- **services-and-di.md** - Extended documentation
  - Symfony Console Commands section
  - Command registration in `config/admin/services.yml`
  - Command naming conventions (`modulename:action`)
  - Return code patterns (0/1, not `Command::SUCCESS`)
  - SymfonyStyle usage for rich console output
- **database-and-entities.md** - Order entity LoggableInterface implementation guide
  - 99 new lines documenting logable pattern for order tracking

### Changed
- Updated SKILL.md with new sections:
  - Section 8 extended with Console Commands subsection
  - Section 9 added for Cart Rules & Vouchers
  - Updated description to include console commands and cart rules

## [2026-06-01] - Service Visibility Best Practices

### Changed
- **services-and-di.md** - Aligned with Symfony best practices
  - Clarified explicit `public: true` declaration for services accessed via `$this->get()`
  - Removed `_defaults: public: true` anti-pattern
  - Added warning about `parent:` services requiring explicit `public: true`
- **services-split.md** - Updated service visibility patterns
  - Emphasized explicit `public:` declaration per service
  - Removed blanket `_defaults: public: true` recommendations
- **SKILL.md** - Updated Services split section with best practice guidance
- **configuration-page.md** - Removed `public: true` from private services
- **grid-system.md** - Fixed service visibility declarations

## [2026-05-28] - Fixtures, Theme Installer, Grid JS

### Added
- **theme-template-injection.md** - Complete guide for theme template modification
  - Two-class design pattern (ThemeTemplateInjector + ThemeTemplateInstaller)
  - Marker-based file patching for PS8
  - `scandir()` pattern instead of legacy `Theme::getThemes()`
  - Try/catch patterns to prevent install blocking
- **scripts/grid.bundle.js** - Pre-built JavaScript bundle for Grid functionality
  - Drag-and-drop position management
  - Ajax toggle handling

### Changed
- **module-class-and-installer.md** - Major enhancements
  - FixturesInstaller section documenting raw SQL requirement
  - Explanation of `SymfonyContainer::getInstance()` returning null in `pr:mo` context
  - Guard patterns for service access (`$this->has()` in admin, plain `$this->get()` in front)
  - Never use `ContainerFinder` clarification
- **services-and-di.md** - Added FixturesInstaller documentation
- **SKILL.md** - Added theme template injection section (5b)
- **grid-system.md** - Simplified Twig FilesystemLoader path documentation
- **debugging.md** - Minor updates

## [2026-05-19] - Translatable Forms, Path Fixes, Steering

### Added
- **forms.md** - Extended with translatable fields documentation (128 new lines)
  - `TranslatableType` usage patterns
  - Null coercion for `NOT NULL` fields
  - Multi-language form handling
- **scripts/translatable-form.bundle.js** - Pre-built JavaScript bundle for translatable forms

### Changed
- **SKILL.md** - Multiple improvements
  - Added resolver path case handling
  - Removed non-generic rules for broader applicability
  - Enhanced steering information for AI agents
  - Fixed false-positive warnings for sync & socket patterns
- **entity-doctrine.md** - Refactored for clarity (84 lines modified)
- **grid-system.md** - Path and pattern updates
- **module-class-and-installer.md** - Resolver path fixes
- **module-structure.md** - Namespace and path clarifications
- **ps9-core-ai/Domain/Webservice/CONTEXT.md** - Updated

## [2026-05-13] - Front Office Service Access

### Changed
- **services-split.md** - Major update (60 lines)
  - Documented service availability in front office context
  - Fixed service declaration patterns for front kernel
  - Never point `config/services.yml` at `admin/services.yml` rule
- **SKILL.md** - Updated services split section with front office guidance

## [2026-05-07] - PS9 Core Documentation Integration

### Added
- **ps9-core-ai/** - Complete PrestaShop 9 core documentation
  - CONTEXT.md - Core architecture overview
  - Component documentation (CQRS, Grid, Forms, etc.)
  - Skills for creating Behat tests, CQRS commands/queries
  - Over 100 files of official PS9 patterns and conventions

### Changed
- **SKILL.md** - Added PrestaShop 9 Core Documentation section
- Fixed ps9-core-ai file path reference

## [2026-04-29] - Translations & Legacy Context

### Changed
- **translations.md** - Enhanced translation patterns
- **SKILL.md** - Updated translations section
- **services-and-di.md** - Fixed legacy context service injection patterns
- Clarified `FrameworkBundleAdminController::trans()` signature differences

## [2026-04-23] - Forms & Validation Enrichment

### Changed
- **forms.md** - Added IntegerType field handling
- **SKILL.md** - Enriched form troubleshooting guidance
- **translations.md** - Extended translation patterns
- **debugging.md** - Added form-related failure modes

## [2026-04-15] - Structure Reorganization & Validation

### Changed
- Restructured skill with dedicated `references/` directory
- Moved all implementation guides to `references/*.md`
- **validation.md** - Updated validation tool installation instructions
- SKILL.md now serves as workflow overview pointing to references

## [2026-04-02] - Initial Release

### Added
- Initial release of the `prestashop-module-development` skill
