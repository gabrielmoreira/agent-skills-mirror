# Configuration Management with YAML

## **MANDATORY: Configuration variables pattern**

**CRITICAL**: NEVER hardcode configuration keys or default values directly in code. Always use a YAML-based configuration system with:

1. **ConfigurationInstaller** for install/uninstall operations
2. **`/config_data` folder** with YAML files for keys & default values
3. **ConfigurationManager service** to read configuration (from database OR from YAML fallback)

### Why this pattern?

- ✅ **Single source of truth**: All configuration keys and defaults in one place (YAML)
- ✅ **Type safety**: Read configuration through a dedicated service with validation
- ✅ **Flexibility**: Can read from database (installed) or YAML (default values)
- ✅ **Maintainability**: Easy to add/modify configuration without touching multiple files
- ❌ **NEVER** use `Configuration::updateValue()` or `Configuration::get()` scattered across the codebase

## File structure

```
mymodule/
├── config_data/
│   ├── module.yml              # Module-level configuration
│   └── export_type.yml         # Optional: Additional config files
├── src/
│   ├── Configuration/
│   │   └── ConfigurationManager.php
│   └── Install/
│       └── ConfigurationInstaller.php
└── config/
    └── components/
        └── configuration/
            └── configuration_manager.yml   # Service definition
```

## `config_data/module.yml`

Define all configuration keys with their default values:

```yaml
configuration:
  install_admin_tabs: false           # Boolean config
  allowed_import: false              # Feature flags
  export_type: "marketplace"         # String config
  display_only_active_categories: false
  authorized_categories:             # Array config
    - "3213"
    - "3214"
  
# Examples and documentation can go here as YAML comments
# EXAMPLE FOR MARKETPLACE export
#  install_admin_tabs: false
#  allowed_import: false
#  export_type: "marketplace"
```

## `src/Install/ConfigurationInstaller.php`

**MANDATORY**: Use this exact pattern for installing/uninstalling configuration:

```php
<?php

declare(strict_types=1);

namespace Vendor\MyModule\Install;

use Configuration;

/**
 * Installs configuration variables
 */
class ConfigurationInstaller
{
    /**
     * Install configuration values
     *
     * @param array $configuration Associative array of config keys => values
     *
     * @return bool
     */
    public function install(array $configuration): bool
    {
        $res = true;
        foreach ($configuration as $key => $value) {
            // Handle arrays: serialize to comma-separated string
            if (is_array($value)) {
                $value = implode(',', $value);
            }
            $res &= (bool) \Configuration::updateValue($key, $value);
        }

        return (bool) $res;
    }

    /**
     * Uninstall configuration values
     *
     * @param array $configuration Associative array of config keys => values
     *
     * @return bool
     */
    public function uninstall(array $configuration): bool
    {
        $res = true;
        foreach ($configuration as $key => $value) {
            $res &= (bool) \Configuration::deleteByName($key);
        }

        return (bool) $res;
    }
}
```

## `src/Configuration/ConfigurationManager.php`

**MANDATORY**: Use this service to read configuration from database OR YAML:

```php
<?php

declare(strict_types=1);

namespace Vendor\MyModule\Configuration;

use Symfony\Component\Yaml\Yaml;

/**
 * Get module configuration from database or YAML files
 */
class ConfigurationManager
{
    private array $config;
    private ?array $exportTypes = null; // Optional: for multi-file configs

    public function __construct()
    {
        $configFilePath = _PS_MODULE_DIR_ . 'mymodule/config_data/module.yml';
        $this->config = Yaml::parseFile($configFilePath);
        
        // Optional: Load additional config files
        // $exportTypeFilePath = _PS_MODULE_DIR_ . 'mymodule/config_data/export_type.yml';
        // $this->exportTypes = Yaml::parseFile($exportTypeFilePath);
    }

    /**
     * Get configuration values (from database if installed, else from YAML)
     *
     * @return array
     *
     * @throws \Exception
     */
    public function getModuleConfiguration(): array
    {
        try {
            $configuration = $this->config['configuration'];
            if (!is_array($configuration)) {
                throw new \Exception('Configuration format error');
            }

            // Optional: Merge additional configuration from other YAML files
            // Example: dynamic service selection based on export_type
            /*
            $exportType = $configuration['export_type'] ?? null;
            if ($exportType && isset($this->exportTypes['export_type'][$exportType])) {
                $configuration['export_service'] = $this->exportTypes['export_type'][$exportType]['service'];
                $configuration['export_service_criteria'] = $this->exportTypes['export_type'][$exportType]['criteria'] ?? null;
            }
            */

            // Read from database (if installed) or use YAML defaults
            foreach ($configuration as $key => &$value) {
                $dbValue = \Configuration::get(strtoupper($key));
                if ($dbValue !== false) {
                    // Handle arrays: unserialize from comma-separated string
                    if (is_array($value)) {
                        $value = array_filter(array_map('trim', explode(',', $dbValue)));
                    } else {
                        $value = $dbValue;
                    }
                }
            }

            return $configuration;
        } catch (\Exception $e) {
            throw new \Exception('Module configuration loading error: ' . $e->getMessage());
        }
    }

    /**
     * Get a single configuration value by key
     *
     * @param string $key Configuration key (lowercase, as in YAML)
     * @param mixed $default Default value if not found
     *
     * @return mixed
     */
    public function get(string $key, $default = null)
    {
        $config = $this->getModuleConfiguration();

        return $config[$key] ?? $default;
    }
}
```

## `config/components/configuration/configuration_manager.yml`

Register the service:

```yaml
services:
  _defaults:
    public: true
    
  mymodule.configuration.configuration_manager:
    class: Vendor\MyModule\Configuration\ConfigurationManager
    public: true
```

Import this in `config/admin/services.yml`:

```yaml
imports:
  - { resource: '../components/configuration/configuration_manager.yml' }
```

## Using ConfigurationManager in the Installer

**Update `src/Install/Installer.php`:**

```php
<?php

declare(strict_types=1);

namespace Vendor\MyModule\Install;

use Vendor\MyModule\Configuration\ConfigurationManager;

class Installer
{
    private ConfigurationInstaller $configurationInstaller;
    private ConfigurationManager $configurationManager;

    public function __construct()
    {
        $this->configurationInstaller = new ConfigurationInstaller();
        $this->configurationManager = new ConfigurationManager();
    }

    public function install(\Module $module): bool
    {
        return $this->registerHooks($module)
            && $this->installTabs()
            && $this->installConfiguration();
    }

    private function installConfiguration(): bool
    {
        // Get default configuration from YAML
        $defaultConfig = $this->configurationManager->getModuleConfiguration();
        
        // Transform keys to uppercase for PrestaShop Configuration table
        $configToInstall = [];
        foreach ($defaultConfig as $key => $value) {
            $configToInstall[strtoupper($key)] = $value;
        }

        return $this->configurationInstaller->install($configToInstall);
    }

    public function uninstall(): bool
    {
        $config = $this->configurationManager->getModuleConfiguration();
        $configKeys = [];
        foreach (array_keys($config) as $key) {
            $configKeys[strtoupper($key)] = null;
        }

        return $this->uninstallTabs()
            && $this->configurationInstaller->uninstall($configKeys);
    }
}
```

## Using ConfigurationManager in Controllers

**✅ CORRECT — Inject via constructor**:

```php
<?php

declare(strict_types=1);

namespace Vendor\MyModule\Controller;

use Vendor\MyModule\Configuration\ConfigurationManager;
use PrestaShopBundle\Controller\Admin\FrameworkBundleAdminController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

class MyController extends FrameworkBundleAdminController
{
    private ConfigurationManager $configurationManager;

    public function __construct(ConfigurationManager $configurationManager)
    {
        $this->configurationManager = $configurationManager;
    }

    public function index(Request $request): Response
    {
        $config = $this->configurationManager->getModuleConfiguration();
        $isActiveImportFeature = (bool) ($config['allowed_import'] ?? false);
        
        // Or get a single value:
        $exportType = $this->configurationManager->get('export_type', 'marketplace');

        // ... use configuration
    }
}
```

**Register controller with dependency injection** in `config/components/configuration/services.yml`:

```yaml
  Vendor\MyModule\Controller\MyController:
    public: true
    arguments:
      - '@mymodule.configuration.configuration_manager'
    tags:
      - { name: controller.service_arguments }
```

## Using ConfigurationManager in Services

```php
<?php

namespace Vendor\MyModule\Service;

use Vendor\MyModule\Configuration\ConfigurationManager;

class ExportService
{
    private ConfigurationManager $configurationManager;

    public function __construct(ConfigurationManager $configurationManager)
    {
        $this->configurationManager = $configurationManager;
    }

    public function export(): void
    {
        $exportType = $this->configurationManager->get('export_type');
        $authorizedCategories = $this->configurationManager->get('authorized_categories', []);
        
        // ... use configuration
    }
}
```

## Benefits

1. **Single source of truth**: Configuration lives in YAML files
2. **Type-safe**: ConfigurationManager provides typed access
3. **Flexible**: Can read from database (when installed) or YAML (defaults)
4. **DRY**: No repeated `Configuration::get()` calls scattered everywhere
5. **Testable**: Easy to mock ConfigurationManager in tests
6. **Documented**: YAML files serve as documentation of available settings

## Anti-patterns (NEVER do this)

❌ **WRONG — Direct Configuration::get() calls everywhere**:

```php
// ❌ WRONG: Scattered Configuration calls
$exportType = Configuration::get('MYMODULE_EXPORT_TYPE');
$allowedImport = Configuration::get('MYMODULE_ALLOWED_IMPORT');
// Problem: Hardcoded keys, no defaults, no type safety, no single source of truth
```

❌ **WRONG — Hardcoded defaults in code**:

```php
// ❌ WRONG: Defaults hardcoded in code
$exportType = Configuration::get('MYMODULE_EXPORT_TYPE') ?: 'marketplace';
// Problem: Defaults should be in YAML, not scattered across PHP files
```

❌ **WRONG — Configuration::updateValue() in install() method**:

```php
// ❌ WRONG: Direct calls in install()
public function install(): bool
{
    Configuration::updateValue('MYMODULE_EXPORT_TYPE', 'marketplace');
    Configuration::updateValue('MYMODULE_ALLOWED_IMPORT', false);
    // Problem: Should delegate to ConfigurationInstaller + read from YAML
}
```

## Summary

**Always use this three-part pattern**:

1. **`config_data/module.yml`**: Define all keys and defaults
2. **`ConfigurationInstaller`**: Install/uninstall configuration (using YAML data)
3. **`ConfigurationManager` service**: Read configuration (database or YAML fallback)

**Never**:
- ❌ Use `Configuration::get()`/`updateValue()` directly in business logic
- ❌ Hardcode configuration keys or defaults in PHP code
- ❌ Skip the YAML file and define defaults in code
