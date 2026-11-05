# Changelog

All notable changes to this package are summarised in this file.
The full, per-file history of the skill is in
[`skills/prestashop-module-development/CHANGELOG.md`](skills/prestashop-module-development/CHANGELOG.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 2026-11-03

### Changed

- Grid JS: `scripts/grid.bundle.js` is now a generic init script on the core Grid components (PS 8.0+ / 9.x), copied with no edit; it replaces the broken webpack bundle template.

## 2026-10-06

### Changed

- Grid: sort / reset troubleshooting and grid ID verification for copied bundles (superseded on 2026-11-03).

## 2026-08-25

### Added

- `references/configuration-management.md` — YAML-based configuration management (single source of truth); modern Symfony router redirect in `getContent()`.

## 2026-08-12

### Changed

- Mandatory installer pattern, configuration page FormHandler with constructor DI, front-office media registration and Smarty translation rules.

## 2026-08-10

### Changed

- CategoryChoiceTreeType documentation embedded in the skill.

## 2026-06-03

### Added

- `references/cart-rules.md` — cart rules and vouchers; console commands; Order `LoggableInterface`.
- Skill `README.md` and `CHANGELOG.md`.

### Security

- PS9 core documentation clarified as static, pre-bundled files (security audit warning).

## 2026-06-01

### Changed

- Service visibility aligned with Symfony best practices (explicit `public: true` only where needed).

## 2026-05-28

### Added

- `references/theme-template-injection.md`, grid and translatable form JS templates in `scripts/`.

### Changed

- FixturesInstaller raw SQL rule, services wiring under `config/components/`.

## 2026-05-19

### Added

- Steering section in `SKILL.md`; `TranslatableType` documentation.

### Changed

- Skill made company-neutral (generic examples).

### Security

- Removed live external URLs (security scanner fixes).

## 2026-05-13

### Changed

- Front-office service access rules.

## 2026-05-07

### Added

- `ps9-core-ai/` — PrestaShop 9 core documentation.

## 2026-04-29

### Changed

- Translations and legacy context injection patterns.

## 2026-04-23

### Changed

- Forms and validation enrichment.

## 2026-04-15

### Added

- `references/` folder; `SKILL.md` refactored into a concise index.

## 2026-04-02

### Added

- Initial release of the `prestashop-module-development` skill.
