# Changelog

All notable changes to the PrestaShop Module Development skill.

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

## [2026-04-16] - Structure Reorganization & Validation

### Changed
- Restructured skill with dedicated `references/` directory
- Moved all implementation guides to `references/*.md`
- **validation.md** - Updated validation tool installation instructions
- SKILL.md now serves as workflow overview pointing to references

## Format

This changelog follows semantic versioning principles with date-based releases.
Each entry includes:
- **Date**: YYYY-MM-DD format
- **Type**: Added, Changed, Deprecated, Removed, Fixed, Security
- **Component**: File or feature affected
- **Description**: What changed and why
