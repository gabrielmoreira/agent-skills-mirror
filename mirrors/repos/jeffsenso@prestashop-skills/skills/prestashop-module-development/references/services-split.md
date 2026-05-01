# Services split & components architecture

## Services split: common.yml vs admin services.yml

PrestaShop is **not fully migrated** — front office runs a legacy light container, admin runs the full Symfony bundle kernel.

**`config/common.yml`** — loaded in BOTH front and admin:
- Imports `components/repository/*.yml` only
- No inline service definitions
- No dependency on any `PrestaShop\` class

**`config/admin/services.yml`** — admin only, imports common.yml + all component globs:
- Manager (uses `LangRepository` from `PrestaShopBundle\Entity\Repository`, `EntityManagerInterface`)
- Grid factories, query builders, data factories
- Form types, data configurations, handlers
- Symfony controllers (`FrameworkBundleAdminController`)
- Any service that depends on a `prestashop.*` or `PrestaShopBundle\` service

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

**`config/common.yml`** pattern:
```yaml
# Loaded by BOTH front and admin kernels — Doctrine-only services.
imports:
  - { resource: "components/repository/*.yml" }
```

**`config/admin/services.yml`** pattern:
```yaml
imports:
  - { resource: ../common.yml }
  - { resource: "../components/manager/*.yml" }
  - { resource: "../components/form/*.yml" }
  - { resource: "../components/grid/*.yml" }
  - { resource: "../components/controller/*.yml" }
```

Rules:
- Each component `.yml` starts with a comment header naming the concern and kernel scope
- Every component folder must contain an `index.php` PS security redirect file
- Add a new sub-folder (never a new inline block) when a new concern is introduced
- `config/front/services.yml` imports only `common.yml` — never add admin-only services there
