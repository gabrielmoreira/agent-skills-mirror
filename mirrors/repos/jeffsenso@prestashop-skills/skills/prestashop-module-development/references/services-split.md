# Services split & components architecture

## Services split: common.yml vs admin services.yml

PrestaShop is **not fully migrated** — front office runs a legacy light container, admin runs the full Symfony bundle kernel.

### How PrestaShop loads module service files

| File | Loaded by |
|------|----------|
| `config/services.yml` | **Admin** kernel only (via `PrestaShopBundle::build()`) |
| `config/admin/services.yml` | **Admin** kernel only, in addition to `config/services.yml` |
| `config/front/services.yml` | **Front-office** kernel only (via `Adapter\ContainerBuilder`) |

**`config/services.yml`** is an admin-kernel-only entry point loaded by `PrestaShopBundle::build()` via `LoadServicesFromModulesPass()` (no container name = empty = `config/services.yml`). It is **NOT** loaded by the front kernel.

**`config/front/services.yml`** is the front-kernel entry point, loaded by `Adapter\ContainerBuilder` via `LoadServicesFromModulesPass('front')`. It must import `../common.yml`. This is what makes repository services available in front-office hooks.

> ⚠️ **Front services must be in `config/front/services.yml`**, not `config/services.yml`. Putting repository services only in `config/services.yml` means the front kernel never sees them and `$this->get()` calls in `getWidgetVariables()` will silently return null.

**`config/common.yml`** — imported by both `config/front/services.yml` and `config/admin/services.yml`:
- Imports `components/repository/*.yml` only
- No inline service definitions
- No dependency on any `PrestaShop\` class

**`config/admin/services.yml`** — admin only, loaded in addition to `config/services.yml`:
- Imports `../common.yml` (self-contained; safe to re-import — Symfony deduplicates)
- Then imports all admin-only component globs
- Manager, grid factories, form types, controllers, any `PrestaShopBundle\` dep

> ⚠️ **Path trap**: in `config/admin/services.yml`, the path to common is `../common.yml` (not `common.yml`). Using `common.yml` resolves relative to `config/admin/` and fails with a FileLocator error.

**Rule**: A service goes in `common.yml` only if ALL its dependencies are Doctrine-level (not `PrestaShopBundle`). If any dependency is `@prestashop.*` or a `PrestaShopBundle\` class, it belongs in admin-only services.

## Components split (mandatory for all modules)

Always split admin services into component files under `config/components/`. Never put more than one concern in a single flat `services.yml`. Use this structure:

```
config/
  common.yml                              # imports: components/repository/*.yml only
  admin/
    services.yml                          # imports: common.yml + all components/* globs
  front/
    services.yml                          # imports: common.yml only
  components/
    index.php                             # PS security redirect
    repository/
      index.php
      repository.yml                      # Doctrine factory services only
    manager/
      index.php
      manager.yml                         # Manager class (PrestaShopBundle deps)
    form/
      index.php
      <feature>_form.yml                  # DataConfiguration, DataProvider, FormType, Handler
    grid/
      index.php
      <entity>_grid.yml                   # GridDefinitionFactory, QueryBuilder, DataFactory, GridFactory, PositionDefinition, twig.loader.filesystem
    controller/
      index.php
      controllers.yml                     # All FrameworkBundleAdminController services
```

**`config/services.yml`** pattern (admin kernel only, optional):
```yaml
# Admin kernel only — loaded by PrestaShopBundle in addition to config/admin/services.yml.
imports:
    - { resource: "common.yml" }
```

**`config/front/services.yml`** pattern (front kernel only, **required for front-office hooks**):
```yaml
# Front-office only — loaded by Adapter\ContainerBuilder (config/front/services.yml).
imports:
    - { resource: "../common.yml" }
```

**`config/common.yml`** pattern:
```yaml
# Loaded by both kernels (via config/front/services.yml and config/admin/services.yml) — Doctrine-only services.
imports:
    - { resource: "components/repository/*.yml" }
```

**`config/admin/services.yml`** pattern:
```yaml
# Admin-only — loaded by admin kernel IN ADDITION to config/services.yml.
# ../common.yml is re-imported for self-containment; Symfony deduplicates safely.
imports:
    - { resource: ../common.yml }        # ← must be ../common.yml, NOT common.yml
    - { resource: "../components/manager/*.yml" }
    - { resource: "../components/form/*.yml" }
    - { resource: "../components/grid/*.yml" }
    - { resource: "../components/controller/*.yml" }
```

**`config/components/repository/repository.yml`** pattern:
```yaml
# Front+Admin — repository services (no PrestaShopBundle dependencies).
# Only mark public: true on services accessed via $this->get() from the module class.
# All other services remain private (omit public:).
services:
    mymodule.repository.my_repository:
        class: Vendor\MyModule\Repository\MyRepository
        public: true                             # ← accessed via $this->get() in module class
```

> ⚠️ **`public: true` is required only for services accessed via `$this->get()`** from the module class or a controller. Declare it explicitly on each such service definition — avoid `_defaults: public: true` as a blanket default: it is against Symfony best practices (services should be private unless explicitly needed) and causes a fatal error in PrestaShop's Symfony version when combined with `parent:` services.

Rules:
- Each component `.yml` starts with a comment header naming the concern and kernel scope
- Every component folder must contain an `index.php` PS security redirect file
- Add a new sub-folder (never a new inline block) when a new concern is introduced
- `config/front/services.yml` imports only `common.yml` — never add admin-only services there
- **Never point `config/services.yml` at `admin/services.yml`** — doing so loads admin-only services (e.g. `PrestaShopBundle` controller decorators) into the front kernel and breaks container compilation silently
