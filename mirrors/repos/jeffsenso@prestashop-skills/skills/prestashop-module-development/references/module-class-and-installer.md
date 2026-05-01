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

> **Rule**: Do NOT declare `getTabs()` in the main module class. This PS-native method has inconsistent lifecycle management and does not support the shared parent group tab (`Adminwswebsenso`) check.  
> **Always** handle tab creation/deletion in `Installer::installTabs()` / `uninstallTabs()`.

> **Rule**: **Never install the module configuration controller as a visible sidebar tab.** The configuration page is accessed via the module's "Configure" button in the Modules list (via `getContent()` redirect). The `AdminMymoduleConfiguration` tab must be installed with `visible: false` — it only exists to provide the `_legacy_link` routing target for the Symfony controller. Only CRUD/list controllers (e.g. `AdminMymoduleItems`) should appear in the sidebar.

The parent group tab `Adminwswebsenso` is shared across all Websenso modules. Install it only if it does not already exist.

```php
private string $groupTabName = 'Adminwswebsenso';

private array $tabs = [
    [
        // Hidden routing tab — required for _legacy_link routing, must NOT appear in sidebar
        'name'              => 'MyModule',
        'class_name'        => 'AdminMymoduleConfiguration',
        'label'             => 'My Module Configuration',
        'parent_class_name' => 'Adminwswebsenso',
        'visible'           => false,   // ← NEVER visible; accessed via module "Configure" button only
    ],
    [
        // Visible CRUD list tab
        'name'              => 'MyModule',
        'class_name'        => 'AdminMymoduleItems',
        'label'             => 'My Module Items',
        'parent_class_name' => 'Adminwswebsenso',
        'visible'           => true,
    ],
];

private function installTabs(): bool
{
    if (count($this->tabs) > 0) {
        $groupTabIsInstalled = \Tab::getIdFromClassName($this->groupTabName);
        if (!$groupTabIsInstalled) {
            $parentTab = [
                'name'              => 'WebSenso',
                'label'             => 'WebSenso',
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

class FixturesInstaller
{
    public function install(): void
    {
        // Insert default entities, sample content, etc.
    }
}
```

## FixturesInstaller — service resolution at install time

**CRITICAL**: Do NOT call `$module->get('mymodule.manager.entity_manager')` inside `FixturesInstaller::install()`. The module's own services are NOT in the compiled container at install time — the container was compiled before the module was registered as active.

Instead, resolve the two core Symfony services (always available) and instantiate the Manager directly:

```php
public function install(\Module $module): void
{
    $em = $module->get('doctrine.orm.default_entity_manager');        // always available
    $langRepo = $module->get('prestashop.core.admin.lang.repository'); // always available
    $itemRepo = $em->getRepository(MyEntity::class);
    $manager = new MyManager($itemRepo, $langRepo, $em);               // manual instantiation

    // Use \Language::getLanguages(false) for per-language arrays — core PS call, not our SQL
    foreach (\Language::getLanguages(false) as $lang) {
        // ...
    }
}
```

## Guard patterns — service access from the module class

### Admin context: `$this->has()` before `$this->get()`

```php
$service = $this->has('mymodule.service.id') ? $this->get('mymodule.service.id') : null;
if ($service === null) {
    return;
}
```

### Front office context: try/catch + instanceof (mandatory)

`$this->has()` can return `true` yet `$this->get()` still throw on a stale container. Always use this pattern in front-office hooks and widget methods:

```php
try {
    $repository = $this->get('mymodule.repository.my_repository');
} catch (Exception $e) {
    $repository = null;
}
if (!$repository instanceof \Ws\MyModule\Repository\MyRepository) {
    return [];
}
// safe to use $repository here
```

**Rule**: Repository services defined in `config/common.yml` are available in BOTH admin and front kernels. Manager and other admin-only services (in `config/admin/services.yml`) must NEVER be called from front-office hooks or widget methods.
