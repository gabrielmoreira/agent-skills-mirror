# Main module class & installer pattern

## Main module file (`mymodule.php`)

> **Rule**: Never put `Configuration::updateValue/deleteByName`, hook registration, or DB queries directly in `install()`/`uninstall()`. Delegate entirely to an `Installer` class from `src/Install/`.

> **Critical**: Always `require_once __DIR__ . '/vendor/autoload.php';` after the `_PS_VERSION_` guard. Without it, namespaced classes will not be found when PrestaShop loads the module.

```php
<?php
if (!defined('_PS_VERSION_')) {
    exit;
}

require_once __DIR__ . '/vendor/autoload.php';

use Vendor\MyModule\Install\Installer;
use PrestaShop\PrestaShop\Adapter\SymfonyContainer;

class MyModule extends Module
{
    public function __construct()
    {
        $this->name = 'mymodule';
        $this->tab = 'front_office_features';
        $this->version = '1.0.0';
        $this->author = 'Your Name';
        $this->need_instance = 0;
        $this->ps_versions_compliancy = ['min' => '1.7.8.0', 'max' => _PS_VERSION_];
        $this->bootstrap = true;

        parent::__construct();

        $this->displayName = $this->trans('My Module', [], 'Modules.Mymodule.Admin');
        $this->description = $this->trans('Module description', [], 'Modules.Mymodule.Admin');
    }

    public function install(): bool
    {
        if (!parent::install()) {
            return false;
        }
        $installer = new Installer();
        return $installer->install($this);
    }

    public function uninstall(): bool
    {
        $installer = new Installer();
        return $installer->uninstall() && parent::uninstall();
    }

    // Do NOT add getTabs() — tabs are managed entirely by Installer::installTabs()
    // Only redirect getContent() — never render HTML
    public function getContent(): void
    {
        $router = SymfonyContainer::getInstance()->get('router');
        Tools::redirectAdmin($router->generate('mymodule_configuration'));
    }
}
```

## Tab management — always via Installer, never via getTabs()

> **Rule**: Do NOT declare `getTabs()` in the main module class. This PS-native method has inconsistent lifecycle management and does not support a shared parent group tab check.  
> **Always** handle tab creation/deletion in `Installer::installTabs()` / `uninstallTabs()`.

> **Rule**: **Never install the module configuration controller as a visible sidebar tab.** The configuration page is accessed via the module's "Configure" button in the Modules list (via `getContent()` redirect). The `AdminMymoduleConfiguration` tab must be installed with `visible: false` — it only exists to provide the `_legacy_link` routing target for the Symfony controller. Only CRUD/list controllers (e.g. `AdminMymoduleItems`) should appear in the sidebar.

If your organisation uses a shared group tab for all its modules, check for its existence before creating it. The example below uses `AdminMyCompanyGroup` as the group tab name — replace with your own.

```php
// Replace 'AdminMyCompanyGroup' and 'My Company' with your own values.
private string $groupTabName = 'AdminMyCompanyGroup';

private array $tabs = [
    [
        // Hidden routing tab — required for _legacy_link routing, must NOT appear in sidebar
        'name'              => 'MyModule',
        'class_name'        => 'AdminMymoduleConfiguration',
        'label'             => 'My Module Configuration',
        'parent_class_name' => 'AdminMyCompanyGroup',
        'visible'           => false,   // ← NEVER visible; accessed via module "Configure" button only
    ],
    [
        // Visible CRUD list tab
        'name'              => 'MyModule',
        'class_name'        => 'AdminMymoduleItems',
        'label'             => 'My Module Items',
        'parent_class_name' => 'AdminMyCompanyGroup',
        'visible'           => true,
    ],
];

private function installTabs(): bool
{
    if (count($this->tabs) > 0) {
        $groupTabIsInstalled = \Tab::getIdFromClassName($this->groupTabName);
        if (!$groupTabIsInstalled) {
            $parentTab = [
                'name'              => 'My Company',   // Replace with your company/group label
                'label'             => 'My Company',
                'class_name'        => $this->groupTabName,
                'visible'           => true,
                'parent_class_name' => 'CONFIGURE',
            ];
            array_unshift($this->tabs, $parentTab);
        }
    }

    foreach ($this->tabs as $data) {
        $tab = new \Tab();
        $tab->active     = true;
        $tab->module     = $data['name'];
        $tab->class_name = $data['class_name'];
        $tab->enabled    = $data['visible'] ?? true;    // false hides from sidebar but keeps routing
        $tab->position   = \Tab::getNewLastPosition($data['parent_class_name']);
        $tab->id_parent  = (int) \Tab::getIdFromClassName($data['parent_class_name']);
        foreach (\Language::getLanguages() as $lang) {
            $tab->name[$lang['id_lang']] = $data['label'];  // use label directly, no translator during install
        }
        $tab->icon = 'mouse';
        if (!$tab->save()) {
            return false;
        }
    }

    return true;
}

private function uninstallTabs(): bool
{
    foreach ($this->tabs as $data) {
        $id_tab = (int) \Tab::getIdFromClassName($data['class_name']);
        $tab = new \Tab($id_tab);
        $tab->delete();
    }

    return true;
}
```

Call both in `install()` / `uninstall()`:

```php
public function install(\Module $module): bool
{
    return $this->registerHooks($module)
        && $this->installDatabase()
        && $this->installTabs();
}

public function uninstall(): bool
{
    return $this->uninstallDatabase() && $this->uninstallTabs();
}
```

## Installer pattern (`src/Install/`)

Always split install logic into dedicated classes:

```
src/Install/
├── Installer.php              # orchestrates install/uninstall
├── ConfigurationInstaller.php # handles Configuration table values
├── FixturesInstaller.php      # (optional) inserts default/sample data
└── index.php                  # PS security guard
```

### `src/Install/Installer.php` — orchestrator

```php
namespace Vendor\MyModule\Install;

class Installer
{
    private array $hooks = ['displayHeader', 'displayFooter'];

    private ConfigurationInstaller $configurationInstaller;

    public function __construct()
    {
        $this->configurationInstaller = new ConfigurationInstaller();
    }

    public function install(\Module $module): bool
    {
        if (!$this->registerHooks($module)) {
            return false;
        }
        // if (!$this->installDatabase()) { return false; } // only if DB tables needed
        return $this->configurationInstaller->install();
    }

    public function uninstall(): bool
    {
        // $this->uninstallDatabase(); // only if DB tables exist
        return $this->configurationInstaller->uninstall();
    }

    private function registerHooks(\Module $module): bool
    {
        return (bool) $module->registerHook($this->hooks);
    }

    // Only add if module has DB tables:
    // private function installDatabase(): bool { return $this->executeQueries(SqlQueries::installQueries()); }
    // private function uninstallDatabase(): bool { return $this->executeQueries(SqlQueries::uninstallQueries()); }
    // private function executeQueries(array $queries): bool {
    //     foreach ($queries as $query) {
    //         if (!\Db::getInstance()->execute($query)) { return false; }
    //     }
    //     return true;
    // }
}
```

### `src/Install/ConfigurationInstaller.php` — installs config per shop context

```php
namespace Vendor\MyModule\Install;

use Configuration;
use Shop;

class ConfigurationInstaller
{
    public function install(): bool
    {
        $shops = Shop::getContextListShopID();
        $shopGroups = [];
        $res = true;

        foreach ($shops as $shopId) {
            $groupId = (int) Shop::getGroupFromShop($shopId, true);
            if (!in_array($groupId, $shopGroups)) {
                $shopGroups[] = $groupId;
            }
            $res &= (bool) Configuration::updateValue('MYMODULE_SETTING', 'default', false, $groupId, $shopId);
        }
        foreach ($shopGroups as $groupId) {
            $res &= (bool) Configuration::updateValue('MYMODULE_SETTING', 'default', false, $groupId);
        }
        $res &= (bool) Configuration::updateValue('MYMODULE_SETTING', 'default');

        return (bool) $res;
    }

    public function uninstall(): bool
    {
        return (bool) Configuration::deleteByName('MYMODULE_SETTING');
    }
}
```

### `src/Install/FixturesInstaller.php` — only create if default data is needed

```php
namespace Vendor\MyModule\Install;

use Db;

class FixturesInstaller
{
    public function install(): void
    {
        // Insert default data using Db::getInstance() — see FixturesInstaller section below
    }
}
```

## FixturesInstaller — MANDATORY: use `Db::getInstance()`, never Doctrine or SymfonyContainer

**`SymfonyContainer::getInstance()` returns `null` during `pr:mo` (Symfony console install).**

Root cause: `SymfonyContainer::getInstance()` reads `global $kernel`. In the Symfony console context used by `php bin/console pr:mo install mymodule`, `$kernel` is never set as a global, so the method always returns `null`. Any Doctrine ORM calls silently do nothing.

**`Db::getInstance()` is always available** — in web requests, console commands, and install hooks.

```php
namespace Vendor\MyModule\Install;

use Db;

class FixturesInstaller
{
    public function install(): void
    {
        $db = Db::getInstance();
        $prefix = _DB_PREFIX_;

        // Skip if already installed (idempotent)
        $existing = (int) $db->getValue("SELECT COUNT(*) FROM `{$prefix}mymodule_items`");
        if ($existing > 0) {
            return;
        }

        $langId = $this->resolveLangId($db, $prefix);
        if ($langId === 0) {
            return;
        }

        $now = date('Y-m-d H:i:s');
        $db->execute(
            "INSERT INTO `{$prefix}mymodule_items` (`active`, `position`, `date_add`, `date_upd`)
             VALUES (1, 0, '" . pSQL($now) . "', '" . pSQL($now) . "')"
        );

        $itemId = (int) $db->Insert_ID();
        if ($itemId === 0) {
            return;
        }

        $db->execute(
            "INSERT INTO `{$prefix}mymodule_items_lang` (`id_item`, `id_lang`, `name`)
             VALUES ({$itemId}, {$langId}, '" . pSQL('Default item') . "')"
        );
    }

    private function resolveLangId(Db $db, string $prefix): int
    {
        // NOTE: Db::getValue() automatically appends LIMIT 1 — never add it yourself
        $frId = (int) $db->getValue("SELECT `id_lang` FROM `{$prefix}lang` WHERE `iso_code` = 'fr'");
        if ($frId > 0) {
            return $frId;
        }
        return (int) $db->getValue("SELECT `id_lang` FROM `{$prefix}lang` ORDER BY `id_lang` ASC");
    }
}
```

> ⚠️ **`Db::getValue()` appends `LIMIT 1` internally** — never write `LIMIT 1` in the SQL string passed to `getValue()`. It results in a MariaDB syntax error.

## FixturesInstaller — legacy note (DO NOT USE)

~~Do NOT call `$module->get('mymodule.manager.entity_manager')` inside `FixturesInstaller::install()`. The module's own services are NOT in the compiled container at install time.~~

This was the previous guidance. The updated rule is simpler: **always use `Db::getInstance()` in FixturesInstaller**. It works in all contexts without any workarounds.

## ThemeTemplateInstaller — injecting widget calls into theme templates

If your module needs a `{widget}` call added to a theme template, use `ThemeTemplateInstaller` + `ThemeTemplateInjector`. See the dedicated reference: **`theme-template-injection.md`**.

## Guard patterns — service access from the module class

> ⚠️ **NEVER use `ContainerFinder`** — it is not needed and adds unnecessary complexity. `$this->get()` works in both admin and front-office contexts when services are registered in the correct config file.

### Admin context: `$this->has()` before `$this->get()`

```php
$service = $this->has('mymodule.service.id') ? $this->get('mymodule.service.id') : null;
if ($service === null) {
    return;
}
```

### Front office context: plain `$this->get()` + null check

Repository services are available via `$this->get()` in front-office hooks and widget methods, as long as they are registered in `config/front/services.yml` (directly or via import of `common.yml`).

```php
/** @var \Ws\MyModule\Repository\MyRepository|null $repository */
$repository = $this->get('mymodule.repository.my_repository');
if (!$repository) {
    return [];
}
// safe to use $repository here
```

If `$this->get()` returns `null` in front-office, the service is not in `config/front/services.yml` — fix the config, not the call site.

**Rule**: Repository services defined in `config/common.yml` (imported by `config/front/services.yml`) are available in both admin and front kernels. Manager and other admin-only services (in `config/admin/services.yml`) must NEVER be called from front-office hooks or widget methods.
