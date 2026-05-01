---
name: prestashop-module-development
description: "Complete PrestaShop module development workflow using modern architecture and best practices. Use when: creating new PrestaShop modules, updating legacy modules to modern code, implementing hooks and actions, setting up module configuration pages, adding front office features, handling database operations, implementing security measures, managing translations, or modernizing existing PrestaShop modules from legacy patterns to current standards."
---

# PrestaShop Module Development

## When to use

Use this skill for PrestaShop module development tasks such as:

- Creating new modules with modern architecture (Symfony controllers, services, entities)
- Refactoring legacy modules to use modern PrestaShop patterns
- Implementing hooks, actions, and event listeners
- Adding configuration pages (modern Symfony-form approach)
- Creating front office features and widgets
- Setting up database entities and migrations
- Implementing security measures (CSRF, input validation, SQL injection prevention)
- Adding multilingual support and translations
- Converting legacy code patterns (HelperForm, jQuery UI sortable, ObjectModel) to modern equivalents
- Building list pages with the PrestaShop Grid system (filters, pagination, toggle, drag-and-drop position)

## Inputs required

- PrestaShop version (target 8.x/9.x for modern development)
- Module scope and functionality requirements
- Existing module path (if updating legacy code)
- Database schema requirements (if applicable)
- Front office integration needs (hooks, widgets, pages)
- Configuration requirements (settings, admin interface)
- Multilingual requirements and supported languages

## Procedure

### 0) Project structure & namespace naming

Read: `references/module-structure.md`

Key rules:
- Derive PSR-4 namespace from the module name prefix — never use `PrestaShop\Module\`
- Use the [PrestaShop Module Generator](https://validator.prestashop.com/generator) to scaffold new modules

### 1) Main module class & installer

Read: `references/module-class-and-installer.md`

Key rules:
- Always `require_once __DIR__ . '/vendor/autoload.php';` after the `_PS_VERSION_` guard
- Never put hook registration, DB queries, or `Configuration::` calls directly in `install()` — delegate to `src/Install/Installer.php`
- **Do NOT add `getTabs()`** to the main module class — manage tabs entirely via `Installer::installTabs()` / `uninstallTabs()`
- Default parent tab is `Adminwswebsenso` (shared Websenso group); check existence before creating it
- `getContent()` must only redirect to the Symfony route, never render HTML
- **No SQL in the main module class** — all database access (including in hooks like `hookActionShopDataDuplication` and widget methods like `getWidgetVariables`) must be delegated to the Repository or Manager class via `$this->get('service.id')`
- **Always guard service access** — use `$this->has()` + null check in admin context; use try/catch + `instanceof` in front-office context (stale container can make `has()` return `true` while `get()` still throws). See `references/module-class-and-installer.md` → *Guard patterns* section.

### 2) Modern configuration pages

Read: `references/configuration-page.md`

Key rules:
- **Do NOT use `HelperForm`** — use Symfony form components + `FrameworkBundleAdminController`
- Four classes: `DataConfiguration`, `FormDataProvider`, `FormType`, `Controller`
- Wire everything in `config/services.yml` and `config/routes.yml`

### 3) Database operations & entities

Read: `references/database-and-entities.md`  
For translatable entities with Grid: read `references/entity-doctrine.md`

- **Always use Doctrine ORM** (Entity + LangEntity + Repository + Manager) for any entity that has a Grid list page or translatable fields
- ObjectModel is legacy — do not use in new or modernised modules
- **Entity class name = table name without `_DB_PREFIX_`** — PS adds the prefix globally; use `@ORM\Table()` with no `name=` parameter
- **All table names must start with `ws_`** — e.g. `ws_mymodule_items`, `ws_mymodule_items_lang` — to group Websenso tables together
- Do NOT create `MetadataListener` or Doctrine event listeners for table naming
- Always sanitize raw DBAL SQL: cast IDs with `(int)`, use bound parameters
- **No raw SQL (`Db::getInstance()`, `pSQL()`, `_DB_PREFIX_` string concatenation) outside Repository and Manager classes.** This applies everywhere: main module class, Installer, FixturesInstaller, hooks, widget methods. The only exception is `Installer` SQL schema queries (`CREATE TABLE`, `DROP TABLE`) which have no Repository equivalent.
- **FixturesInstaller must NOT call module-own services** — the module's services are not in the container at install time. Instantiate Manager directly using core Doctrine services. See `references/module-class-and-installer.md` → *FixturesInstaller — service resolution* section.

### Services split & components architecture

Read: `references/services-split.md`

Key rules:
- Repository services only in `config/common.yml` (Doctrine-level, no `PrestaShopBundle` deps)
- All `PrestaShopBundle`-dependent services go in `config/admin/services.yml`
- Always split into component sub-folders under `config/components/` — never one flat `services.yml`

### 4) Security (mandatory)

Read: `references/security.md`

- CSRF: handled by Symfony forms automatically; validate manually for raw AJAX endpoints
- SQL injection: `(int)` + `pSQL()` on every value, or use `DbQuery` builder
- File uploads: pass full `$_FILES`-compatible array (including `type`, `size`, `error`) to `ImageManager::validateUpload()`

### 5) Hooks & front office integration

Read: `references/hooks-and-front-office.md`

- Register hooks in `Installer`, not in `install()` directly
- Load assets only for the relevant controller in `hookDisplayBackOfficeHeader`
- Implement `WidgetInterface` for front office widgets

### 6) Translations

Read: `references/translations.md`

- Use `$this->trans('Text', [], 'Modules.Mymodule.Admin')` in PHP
- Use `'Text'|trans({}, 'Modules.Mymodule.Admin')` in Twig
- Declare `isUsingNewTranslationSystem(): true` in the module class

### 7) Legacy code conversion

Read: `references/legacy-conversion.md`

Common conversions: HelperForm → Symfony form, jQuery UI sortable → Grid PositionColumn, ModuleAdminController → FrameworkBundleAdminController.

### 8) Services & dependency injection

Read: `references/services-and-di.md`

**CRITICAL**: Never use legacy static calls in services/controllers:
- ❌ `Context::getContext()` — inject `$context: "@=service('prestashop.adapter.legacy.context').getContext()"` instead
- ❌ `Configuration::get()` / `updateValue()` — inject `@prestashop.adapter.legacy.configuration` instead
- ❌ `Context::getContext()->getTranslator()` — inject `@translator` instead

Key rules:
- Define services in `config/services.yml`
- Use `$this->get('service.id')` in Symfony controllers
- Use Expression Language (`@=`) for computed constructor arguments (context, language ID, shop ID)
- Always inject dependencies via constructor, never use static accessors

### 9) Grid system (list pages with drag-and-drop position)

Read: `references/grid-system.md`

Full pattern for building CRUD list pages with the PS Grid system:
- `GridDefinitionFactory` — columns (`PositionColumn`, `ToggleColumn`, `ActionColumn`), filters, row actions
- `QueryBuilder` — Doctrine DBAL query with sorting, pagination, and filters
- `Filters` — default sort/limit settings
- 5 service definitions in `services.yml` (factory, query, data, grid, position)
- 4 routes in `routes.yml` (index, search, toggle, update-position)
- 4 controller actions (`indexAction`, `searchAction`, `toggleStatus`, `updatePositionAction`)
- Pre-built JS bundle (copied from `ws-entity-grid-skeleton`, grid ID replaced via `sed`)

## Verification

- Module installs without PHP errors: `php bin/console pr:mo install mymodule`
- Configuration saves correctly with proper validation
- Front office features display and function properly
- Translations work in all configured languages

## Validation

> **AI agent rule — NEVER SKIP EITHER STEP**. Read `references/validation.md` for full instructions.

### Step 1 — lotr (run from the module root)

```bash
vendor/websenso/prestashop-module-devtools/bin/lotr
```

Expected: `🎉 All commands completed successfully! Executed: 6/6`

### Step 2 — Install test (run from the PS root)

```bash
php bin/console pr:mo install mymodule
```

Expected: `L'action Install sur le module … a réussi.`

## Failure modes / debugging

Read: `references/debugging.md`

Common failure areas:
- `references/debugging.md` — all symptom/cause/fix tables (install, config page, Grid, InputBag, ImageManager, lotr steps)

## Escalation

- [PrestaShop 9 Module Creation](https://devdocs.prestashop-project.org/9/modules/creation/)
- [Module Good Practices](https://devdocs.prestashop-project.org/9/modules/creation/good-practices/)
- [Official Example Modules](https://github.com/PrestaShop/example-modules)
- [demosymfonyform](https://github.com/PrestaShop/example-modules/tree/master/demosymfonyform) — canonical Symfony form config page
- [Module Validator](https://validator.prestashop.com/)
- [PrestaShop Developer Slack](https://www.prestashop-project.org/slack/)
