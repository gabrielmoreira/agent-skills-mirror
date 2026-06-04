---
name: prestashop-module-development
description: "Complete PrestaShop module development workflow using modern architecture and best practices. Use when: creating new PrestaShop modules, updating legacy modules to modern code, implementing hooks and actions, setting up module configuration pages, adding front office features, handling database operations, implementing security measures, managing translations, creating cart rules and vouchers, building Symfony console commands, or modernizing existing PrestaShop modules from legacy patterns to current standards."
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
- Creating and managing PrestaShop cart rules (vouchers, discount codes, promotional codes)
- Implementing Symfony console commands for background tasks and batch operations

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
- If using a shared company group tab, check its existence before creating it — never unconditionally create it
- `getContent()` must only redirect to the Symfony route, never render HTML
- **No SQL in the main module class** — all database access (including in hooks like `hookActionShopDataDuplication` and widget methods like `getWidgetVariables`) must be delegated to the Repository or Manager class via `$this->get('service.id')`
- **Service access**: use `$this->has()` + null check in admin context; use plain `$this->get()` + null check in front-office context. **NEVER use `ContainerFinder`** — it is unnecessary. See `references/module-class-and-installer.md` → *Guard patterns* section.

### 2) Modern configuration pages

Read: `references/configuration-page.md`

Key rules:
- **Do NOT use `HelperForm`** — use Symfony form components + `FrameworkBundleAdminController`
- Four classes: `DataConfiguration`, `FormDataProvider`, `FormType`, `Controller`
- Wire everything in `config/components/` sub-folders (imported by `config/admin/services.yml`) and `config/routes.yml`

### 3) Database operations & entities

Read: `references/database-and-entities.md`  
For translatable entities with Grid: read `references/entity-doctrine.md`

- **Always use Doctrine ORM** (Entity + LangEntity + Repository + Manager) for any entity that has a Grid list page or translatable fields
- ObjectModel is legacy — do not use in new or modernised modules
- **Entity class name = table name without `_DB_PREFIX_`** — PS adds the prefix globally; use `@ORM\Table()` with no `name=` parameter
- Prefix table names with a consistent company or module prefix (e.g. `prefix_mymodule_items`, `prefix_mymodule_items_lang`) — to group tables together and avoid conflicts with PS core tables
- **Lang entity property types must match the DB column nullability**: columns declared `NOT NULL DEFAULT ''` use `string $field = ''`; columns declared `NULL` use `?string $field = null`
- **`TranslatableType` returns `null` for languages the user did not fill in** — in the Manager, always coerce null to `''` for `NOT NULL` string fields: `$row->setName((string) ($value ?? ''))`. Never pass the raw form value directly to a setter on a `NOT NULL` column
- Do NOT create `MetadataListener` or Doctrine event listeners for table naming
- Always sanitize raw DBAL SQL: cast IDs with `(int)`, use bound parameters
- **No raw SQL (`Db::getInstance()`, `pSQL()`, `_DB_PREFIX_` string concatenation) outside Repository and Manager classes.** This applies everywhere: main module class, Installer, FixturesInstaller, hooks, widget methods. The only exception is `Installer` SQL schema queries (`CREATE TABLE`, `DROP TABLE`) which have no Repository equivalent.
- **FixturesInstaller must use `Db::getInstance()` raw SQL** — `SymfonyContainer::getInstance()` returns `null` in the `pr:mo` Symfony console context (`global $kernel` is never set). All Doctrine ORM calls silently do nothing at install time. See `references/module-class-and-installer.md` → *FixturesInstaller* section.
- **`Db::getValue()` appends `LIMIT 1` internally** — never write `LIMIT 1` in the SQL string passed to it; causes a MariaDB syntax error.

### Services split & components architecture

Read: `references/services-split.md`

Key rules:
- **Do NOT create `config/services.yml`** — only `config/admin/services.yml` and `config/front/services.yml` are needed; a root-level `config/services.yml` is never required and should not exist
- `config/admin/services.yml` is loaded by admin kernel only — import `../common.yml` + admin components (never `common.yml` without the `../` prefix)
- Repository services only in `config/common.yml` components (Doctrine-level, no `PrestaShopBundle` deps)
- All `PrestaShopBundle`-dependent services go in `config/admin/services.yml`
- Always split into component sub-folders under `config/components/` — never one flat `services.yml`
- **Only services accessed via `$this->get('service.id')` need `public: true`** — declare it explicitly on each such service; all other services remain private (omit `public:`). Avoid `_defaults: public: true` as a blanket: it is against Symfony best practices and causes a fatal error in PrestaShop's Symfony version when combined with `parent:` services
- **Services that use `parent:` and need to be public must declare `public: true` explicitly on the service definition** — `public` cannot be inherited from `_defaults` when `parent` is set (PrestaShop's Symfony version enforces this)
- **Never point `config/services.yml` at `admin/services.yml`** — this loads admin-only services into the front kernel, breaking container compilation and making all `$this->get()` calls fail silently

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

### 5b) Theme template injection (widget call on install)

Read: `references/theme-template-injection.md`

- PS8 does not support theme overrides from modules — use marker-based file patching instead
- Two-class design: `ThemeTemplateInjector` (service, reusable) + `ThemeTemplateInstaller` (install orchestrator)
- **Never use `Theme::getThemes()`** in install context — legacy class, not autoloaded in Symfony console; use `scandir(_PS_ALL_THEMES_DIR_)` instead
- Wrap install/uninstall calls in try/catch returning `true` — theme injection must never block module install

### 6) Translations

Read: `references/translations.md`

- **`FrameworkBundleAdminController::trans()` signature is `trans($id, $domain, $parameters = [])` — NOT Symfony's order** — always call as `$this->trans('Text', 'Modules.Mymodule.Admin')` (never `$this->trans('Text', [], 'Domain')` — passing `[]` as domain and a string as `$parameters` causes a fatal type error)
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
- Define services in `config/components/` sub-folders (imported by `config/admin/services.yml`)
- Use `$this->get('service.id')` in Symfony controllers
- Use Expression Language (`@=`) for computed constructor arguments (context, language ID, shop ID)
- Always inject dependencies via constructor, never use static accessors

#### Symfony Console Commands

Read: `references/services-and-di.md` → *Symfony Console Commands* section

**CRITICAL**: Commands must be registered in `config/admin/services.yml` (NOT `common.yml` or `front/services.yml`):

```yaml
# config/admin/services.yml
mymodule.command.my_command:
  class: Vendor\MyModule\Command\MyCommand
  arguments: ["@mymodule.service.my_service"]
  tags:
    - { name: console.command, command: modulename:action }
```

Key rules:
- Command naming: `modulename:action` format (e.g., `wsautocartrules:create`, `ws_keepdblight:cleandb`)
- Return codes: `0` for success, `1` for failure (NOT `Command::SUCCESS`/`FAILURE` constants)
- Use `SymfonyStyle` for rich console output (tables, progress bars, styled messages)
- Add `--limit` options for batch operations to enable testing with small datasets
- Always inject services via constructor, never use static calls or `$this->get()`

### 9) Cart Rules & Vouchers

Read: `references/cart-rules.md`

Complete guide for creating and managing PrestaShop cart rules (discount vouchers) programmatically:

Key patterns:
- **Code generation**: Use character set `123456789ABCDEFGHIJKLMNPQRSTUVWXYZ` (no O/0 to avoid confusion, same as PrestaShop admin.js)
- **Uniqueness check**: Validate with `CartRule::getIdByCode($code)` before creation
- **Multilingual names**: Set `name` for all active languages via `Language::getLanguages(true)`
- **Customer restriction**: Use `$cartRule->id_customer` for customer-specific vouchers
- **Date range**: Both `date_from` and `date_to` required (format: `Y-m-d H:i:s`)
- **Reduction types**: `reduction_percent`, `reduction_amount`, `free_shipping`, or `gift_product`
- **Essential fields**: `quantity`, `quantity_per_user`, `priority`, `highlight`, `partial_use`, `active`
- **Restrictions**: All default to `false` (no restriction); set specific restrictions as needed

Common use cases documented:
- Customer-specific vouchers with percentage discount
- Auto-apply cart rules (no code required)
- Limited-time flash sales with highlight
- Free shipping vouchers
- Gift product vouchers

### 10) Grid system (list pages with drag-and-drop position)

Read: `references/grid-system.md`

Full pattern for building CRUD list pages with the PS Grid system:
- `GridDefinitionFactory` — columns (`PositionColumn`, `ToggleColumn`, `ActionColumn`), filters, row actions
- `QueryBuilder` — Doctrine DBAL query with sorting, pagination, and filters
- `Filters` — default sort/limit settings
- 5 service definitions in `config/components/grid/` (factory, query, data, grid, position) + 1 Twig FilesystemLoader
- **Twig FilesystemLoader path is `%kernel.project_dir%/modules/mymodule/views`** — `%kernel.project_dir%` is the PS root (parent of `app/`), so `modules/` is a direct child. Never use `%kernel.project_dir%/../modules/`
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

## PrestaShop 9 Core Documentation

The following files are bundled with this skill in the `ps9-core-ai/` directory.
Read them for deep understanding of PS9 core architecture, conventions, and patterns.

- **`ps9-core-ai/CONTEXT.md`** — Root AI context for the PS9 codebase: project-wide coding
  standards, architecture layers (Core/Adapter/Bundle/Legacy), CQRS pattern, branching
  policy, and the full index of domain and component contexts.
- **`ps9-core-ai/STRUCTURE.md`** — Architecture of the `.ai/` folder itself: how contexts,
  skills, and pointer files are organized and how AI tools discover them.

> **Note for skill maintainers**: These files are static snapshots from the official PrestaShop repository. To update them, skill maintainers can run `lotr --install` from a module directory. This is not a runtime operation — the files are pre-bundled and version-controlled with the skill.

## Steering

If your project or organisation defines a steering layer (layered context rules for coding standards, architecture conventions, and project-specific overrides), load the steering files before starting any task.

**Finding the resolver — search in this order:**

1. `steering/resolver.md` at the module root (custom installation)
2. `vendor/websenso/prestashop-module-devtools/steering/resolver.md` — canonical path when the devtools are installed as a Composer package (same package that provides `vendor/websenso/prestashop-module-devtools/bin/lotr`)
3. Any `vendor/*/*/steering/resolver.md` — scan all vendor subfolders for a `steering/resolver.md` file (use the first match found)

If none exists, skip steering silently and apply only the skill defaults.

Typical steering structure (paths relative to wherever the resolver is found):

```
steering/resolver.md                          ← load order and conflict rules
steering/company/                             ← organisation-wide standards
steering/languages/php/coding-standards.md    ← PHP conventions
steering/frameworks/prestashop/               ← PrestaShop-specific rules
```

Load steering files from lowest to highest priority (company → language → framework → project). Later layers override earlier ones.

## Escalation

- [PrestaShop 9 Module Creation](https://devdocs.prestashop-project.org/9/modules/creation/)
- [Module Good Practices](https://devdocs.prestashop-project.org/9/modules/creation/good-practices/)
- [Official Example Modules](https://github.com/PrestaShop/example-modules)
- [demosymfonyform](https://github.com/PrestaShop/example-modules/tree/master/demosymfonyform) — canonical Symfony form config page
- [Module Validator](https://validator.prestashop.com/)
- [PrestaShop Developer Slack](https://www.prestashop-project.org/slack/)
