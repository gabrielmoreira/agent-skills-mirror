# Main module class & installer pattern

## **MANDATORY: Module install/uninstall pattern**

**CRITICAL**: Always use this EXACT pattern for `install()` and `uninstall()` methods:

```php
public function install(): bool
{
    if (!parent::install()) {
        return false;
    }

    return $this->getInstaller()->install($this);
}

public function uninstall(): bool
{
    return $this->getInstaller()->uninstall() && parent::uninstall();
}

private function getInstaller(): Installer
{
    return new Installer();
}
```

**Why this order matters**:
- ✅ **install()**: `parent::install()` FIRST with explicit check, THEN delegate to Installer
- ✅ **uninstall()**: Installer FIRST, THEN `parent::uninstall()` — use `&&` chaining in return
- ❌ **NEVER** use `return parent::install() && $installer->install($this)` — if parent fails, installer doesn't run and you get no error details

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

class MyModule extends Module
{
    public function __construct()
    {
        $this->name = 'mymodule';
        $this->tab = 'front_office_features';
        $this->version = '1.0.0';
        $this->author = 'Your Name';
        $this->need_instance = 0;
        $this->ps_versions_compliancy = ['min' => '8.0.0', 'max' => _PS_VERSION_];
        $this->bootstrap = true;

        parent::__construct();

        $this->displayName = $this->trans('My Module', 'Modules.Mymodule.Admin');
        $this->description = $this->trans('Module description', 'Modules.Mymodule.Admin');
    }

    public function isUsingNewTranslationSystem(): bool
    {
        return true;
    }

    public function install(): bool
    {
        if (!parent::install()) {
            return false;
        }

        return $this->getInstaller()->install($this);
    }

    public function uninstall(): bool
    {
        return $this->getInstaller()->uninstall() && parent::uninstall();
    }

    public function getContent(): string
    {
        $route = $this->get('router')->generate('mymodule_configuration');

        Tools::redirectAdmin($route);

        return '';
    }

    private function getInstaller(): Installer
    {
        return new Installer();
    }
}
```

## **MANDATORY: Tab management pattern**

**CRITICAL**: Always define tabs as a structured class property array. NEVER use `getTabs()` method in the module class.

```php
namespace Vendor\MyModule\Install;

class Installer
{
    /** @var array<int, string> */
    private array $hooks = [
        'displayHome',
        'actionFrontControllerSetMedia',
    ];

    private string $groupTabName = 'AdminMyCompanyGroup';  // Replace with your company group tab name

    /** @var array<int, array<string, mixed>> */
    private array $tabs = [
        [
            'name' => 'mymodule',                              // Module name (lowercase)
            'class_name' => 'AdminMymoduleConfiguration',       // Tab class name
            'label' => 'My Module Configuration',               // Display label (all languages)
            'parent_class_name' => 'AdminMyCompanyGroup',       // Parent tab class name
            'visible' => true,                                  // true = visible in sidebar, false = hidden (routing only)
        ],
    ];

    public function install(\Module $module): bool
    {
        return $this->registerHooks($module)
            && $this->installTabs()
            && $this->installConfiguration();
    }

    public function uninstall(): bool
    {
        return $this->uninstallTabs()
            && $this->uninstallConfiguration();
    }

    private function registerHooks(\Module $module): bool
    {
        return $module->registerHook($this->hooks);
    }

    private function installTabs(): bool
    {
        if (!empty($this->tabs)) {
            $groupTabIsInstalled = (int) \Tab::getIdFromClassName($this->groupTabName);
            if (!$groupTabIsInstalled === false) {
                $parentTab = [
                    'name' => 'WebSenso',                      // Replace with your company name
                    'label' => 'WebSenso',                     // Replace with your company label
                    'class_name' => $this->groupTabName,
                    'visible' => true,
                    'parent_class_name' => 'CONFIGURE',
                ];
                array_unshift($this->tabs, $parentTab);
            }
        }

        foreach ($this->tabs as $data) {
            $tab = new \Tab();
            $tab->active = true;
            $tab->module = $data['name'];
            $tab->class_name = $data['class_name'];
            $tab->enabled = $data['visible'] ?? true;
            $tab->position = \Tab::getNewLastPosition($data['parent_class_name']);
            $tab->id_parent = (int) \Tab::getIdFromClassName($data['parent_class_name']);
            foreach (\Language::getLanguages() as $lang) {
                $tab->name[$lang['id_lang']] = $data['label'];
            }
            $tab->icon = 'mouse';
            if ($tab->save() === false) {
                return false;
            }
        }

        return true;
    }

    private function uninstallTabs(): bool
    {
        foreach ($this->tabs as $data) {
            $idTab = (int) \Tab::getIdFromClassName($data['class_name']);
            if ($idTab) {
                $tab = new \Tab($idTab);
                $tab->delete();
            }
        }

        return true;
    }

    private function installConfiguration(): bool
    {
        return \Configuration::updateValue('MYMODULE_SETTING', '');
    }

    private function uninstallConfiguration(): bool
    {
        return \Configuration::deleteByName('MYMODULE_SETTING');
    }
}
```

**Key points**:
- ✅ **Hooks as class property array**: `private array $hooks = [...]`
- ✅ **Tabs as class property array**: `private array $tabs = [...]` with structured data
- ✅ **Auto-install parent group tab**: Check if group tab exists, if not, prepend it to tabs array
- ✅ **No sub-classes**: All install logic in one Installer class
- ✅ **Direct Configuration calls**: No ConfigurationInstaller wrapper
- ✅ **Tab structure**: `name`, `class_name`, `label`, `parent_class_name`, `visible`
- ❌ **NEVER use `getTabs()` in module class** — all tab management in Installer

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
