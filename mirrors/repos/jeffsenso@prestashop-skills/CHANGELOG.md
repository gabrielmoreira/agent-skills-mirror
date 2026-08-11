# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 2026-08-10

### Changed

- `SKILL.md` — CategoryChoiceTreeType documentation now embedded directly in configuration page section instead of referencing external steering file; skill is now more self-contained for core features.

## 2026-05-28

### Added

- `references/theme-template-injection.md` — new reference for PS8 theme template injection using marker-based file patching; two-class design (`ThemeTemplateInjector` + `ThemeTemplateInstaller`); rules for install/uninstall safety and `scandir()` vs legacy `Theme::getThemes()`.
- `scripts/grid.bundle.js` — pre-built bundle template for grid JS; replaces the previously inlined bundle content in the reference.
- `scripts/translatable-form.bundle.js` — pre-built bundle template for forms using `TranslatableType`.

### Changed

- `SKILL.md` — service access rules clarified: front-office context uses plain `$this->get()` + null check; `ContainerFinder` is explicitly forbidden.
- `SKILL.md` — services architecture: root-level `config/services.yml` must not exist; only `config/admin/services.yml` and `config/front/services.yml` are needed.
- `SKILL.md` — FixturesInstaller rule updated: must use `Db::getInstance()` raw SQL — `SymfonyContainer::getInstance()` returns `null` in `pr:mo` console context, making all Doctrine ORM calls silently no-ops.
- `SKILL.md` — added rule: `Db::getValue()` appends `LIMIT 1` internally — never write it in the SQL string.
- `SKILL.md` — added rule: Lang entity property types must match DB column nullability; `TranslatableType` returns `null` for unfilled languages — always coerce to `''` in Manager for `NOT NULL` columns.
- `SKILL.md` — new section `5b) Theme template injection` pointing to the new reference file.
- `SKILL.md` — `FrameworkBundleAdminController::trans()` signature clarified: order is `trans($id, $domain, $parameters = [])`, not Symfony's standard order.
- `SKILL.md` — services wiring: all references to `config/services.yml` updated to `config/components/` sub-folders imported by `config/admin/services.yml`.
- `references/forms.md` — new `TranslatableType` section: per-language fields, mandatory locale-switcher JS bundle setup with copy/sed instructions, `DataConfiguration` per-lang storage pattern, and service `parent: form.type.translatable.aware` requirement.
- `references/grid-system.md` — JS bundle setup rewritten to reference external template file (`scripts/grid.bundle.js`) with copy/sed instructions; inlined bundle content removed; added asset path pitfall warning (exact module folder name required).
- `references/module-class-and-installer.md` — expanded with FixturesInstaller raw SQL pattern, guard pattern details, and fixture resolution.
- `references/services-and-di.md` — expanded with additional DI rules and patterns.
- `references/services-split.md` — root `config/services.yml` deprecation clarified; added rule: services using `parent:` do not inherit `_defaults: public: true` — always add `public: true` explicitly.
- `references/configuration-page.md` — minor addition.
- `references/debugging.md` — minor fix.

## 2026-05-19

### Added

- `SKILL.md` — new `## Steering` section: describes the steering layers system, load order, and conflict resolution rules so consumers can attach project-specific context files.

### Changed

- `SKILL.md` — company-specific rules (table prefix, admin tab group, namespace examples) replaced with generic placeholders; the skill is now company-neutral.
- `SKILL.md` — removed live URL from source attribution; replaced with a static note.
- `references/module-class-and-installer.md` — admin tab group and label examples made generic; added `// Replace with your own values` comments.
- `references/entity-doctrine.md` — table prefix, class name, and namespace examples made generic.
- `references/grid-system.md` — table name examples made generic.
- `references/module-structure.md` — namespace examples made generic.

### Security

- `SKILL.md` — removed live URL pointing to an external repository (static agent context URL, security scanner fix).
- `ps9-core-ai/Domain/Webservice/CONTEXT.md` — added static documentation-only disclaimer at top of file (security scanner fix).

## 2026-04-15

### Added

- `references/` folder with 15 domain-specific reference files (module structure, installer, configuration page, entities, grid, security, services split, translations, validation, debugging, and more).

### Changed

- `SKILL.md` — refactored from a monolithic file into a concise index; each step now delegates to a dedicated reference file. Added Grid system, services-split, and guard-pattern rules.

## 2026-04-02

### Added

- Initial release of the `prestashop-module-development` skill.
