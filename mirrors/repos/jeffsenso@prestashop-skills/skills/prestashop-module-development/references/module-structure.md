# Module structure & namespace naming

## Namespace naming convention

Derive the PSR-4 namespace from the module name:

- The module name prefix (first 2 letters before the real words) becomes the **top-level vendor namespace**
- The remaining real words become **sub-namespaces** in CamelCase (detect word boundaries)
- **Never** use the generic `PrestaShop\Module\` vendor prefix — it is reserved for PrestaShop core modules

Examples:
- `mycofeature` → prefix `My`, word `Cofeature` → `My\Cofeature`
- `mycompanycoolfeature` → prefix `My`, words `Company`, `Cool`, `Feature` → `My\CompanyCoolFeature`
- `mycoapp` → prefix `My`, word `Coapp` → `My\Coapp`

This applies to `composer.json` `autoload.psr-4`, PHP `namespace` declarations, and `config/services.yml` FQCNs.

**`composer.json` autoload**:
```json
"autoload": {
  "psr-4": { "Vendor\\MyModule\\": "src/" }
}
```

## Standard directory structure

```
mymodule/
├── config/
│   ├── services.yml          # Service definitions
│   └── routes.yml            # Symfony route definitions
├── src/
│   ├── Controller/           # Symfony controllers
│   │   └── Admin/
│   ├── Form/                 # Symfony form types + data providers
│   ├── Grid/                 # Grid system (list pages)
│   │   ├── Definition/Factory/
│   │   ├── Filters/
│   │   └── Query/
│   ├── Install/              # Installer classes
│   └── Service/             # Business logic services
├── controllers/              # Legacy controllers (avoid in new code)
├── views/
│   ├── templates/
│   │   ├── admin/           # Admin Twig templates
│   │   ├── front/           # Front office templates
│   │   └── hook/            # Hook Smarty/Twig templates
│   ├── css/
│   ├── js/
│   └── img/
├── upload/                   # User-uploaded files (images, documents, etc.)
├── translations/
├── upgrade/                  # Module upgrade scripts
├── vendor/                  # Composer dependencies
├── config.xml               # Cached module properties
├── logo.png                 # 140x140px module icon
└── mymodule.php             # Main module class
```

## Helpful resources

- [PrestaShop Module Generator](https://validator.prestashop.com/generator) — scaffolding for new modules
- [Module good practices](https://devdocs.prestashop-project.org/9/modules/creation/good-practices/)

---

## Upload directory rules

User-uploaded files (images, documents, downloads) **must** be stored in a dedicated directory at the **module root** — never inside `views/`.

```
mymodule/
├── upload/          # ✅ CORRECT — user-uploaded files here
├── views/
│   ├── templates/   # Twig templates only
│   └── img/         # Static module assets only (not user uploads)
```

**Why not `views/`?** The `views/` tree is for Twig templates and static assets bundled with the module. Mixing user uploads into `views/` makes it impossible to distinguish module source files from user data, complicates backups, and can expose template paths to user-controlled filenames.

For Twig namespace overrides (`@PrestaShop` namespace registration via `services.yml`), you will add `views/PrestaShop/` as a path — this is only for template files, never for uploaded content.
