# Services split & components architecture

## Services split: common.yml vs admin services.yml

PrestaShop is **not fully migrated** — front office runs a legacy light container, admin runs the full Symfony bundle kernel.

### How PrestaShop loads module service files

| File | Loaded by |
|------|----------|
| `config/services.yml` | **Both** front and admin kernels |
| `config/admin/services.yml` | Admin kernel **only**, in addition to `config/services.yml` |

**`config/services.yml`** is the main entry point for both kernels. It must import `common.yml` (and nothing admin-specific). This is what makes repository services available in front-office hooks.

**`config/common.yml`** — imported by `config/services.yml`, available in both kernels:
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

**`config/services.yml`** pattern (PS entry point — both kernels):
```yaml
# PS entry point — loaded by BOTH front and admin kernels.
imports:
    - { resource: "common.yml" }
```

**`config/common.yml`** pattern:
```yaml
# Loaded by BOTH front and admin kernels — Doctrine-only services.
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
# MANDATORY: _defaults public: true so $this->get('service.id') works in
# both front-office hooks and admin module class without container lookup failures.
services:
    _defaults:
        public: true

    mymodule.repository.my_repository:
        class: Vendor\MyModule\Repository\MyRepository
```

> ⚠️ **`public: true` is mandatory** for any service accessed via `$this->get()` from the module class. PrestaShop compiles services as private by default; a private service will cause `$this->get()` to throw or silently return null via the front-office try/catch guard. Always declare `_defaults: public: true` in every component yml.

Rules:
- Each component `.yml` starts with a comment header naming the concern and kernel scope
- Every component folder must contain an `index.php` PS security redirect file
- Add a new sub-folder (never a new inline block) when a new concern is introduced
- `config/front/services.yml` imports only `common.yml` — never add admin-only services there
- **Never point `config/services.yml` at `admin/services.yml`** — doing so loads admin-only services (e.g. `PrestaShopBundle` controller decorators) into the front kernel and breaks container compilation silently
