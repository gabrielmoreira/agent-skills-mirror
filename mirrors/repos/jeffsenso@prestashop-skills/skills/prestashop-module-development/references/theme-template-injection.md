# Theme template injection

PrestaShop explicitly states: **"Overriding a theme from a module is NOT possible, and never will."**
A module cannot use `override/themes/` to alter theme `.tpl` files.

The only reliable approach for inserting a `{widget}` or any Smarty snippet into a theme template
is **programmatic file patching** on module install, with clean removal on uninstall.

---

## Architecture — two-class split

Split the responsibility into two classes so the file-level logic can be reused by:
- The install/uninstall process (`ThemeTemplateInstaller`)
- A future admin controller "re-install template" button (calls `ThemeTemplateInjector` directly via DI)

| Class | Location | Role |
|---|---|---|
| `ThemeTemplateInjector` | `src/Service/` | Stateless service. Handles **one** template file. Registered in `config/common.yml` as a public Symfony service. |
| `ThemeTemplateInstaller` | `src/Install/` | Orchestrator. Finds all theme template paths. Calls `ThemeTemplateInjector` for each. Called by `Installer`. |

---

## ThemeTemplateInjector

### Marker-based injection

Wrap the injected block in unique Smarty comment markers. This makes the operation:
- **Idempotent** — already-injected templates are skipped
- **Reversible** — `eject()` can find and remove the exact block
- **Safe** — markers cannot accidentally match user content

```smarty
{* mymodule:start *}
{widget name="mymodule" hook="productList" pos_loop=$smarty.foreach.listingproducts.index productClasses=$productClasses}
{* mymodule:end *}
```

### Handling pre-existing raw widget calls

Before injecting, **strip any raw (unmarked) widget call** already present in the file. A developer may have manually added the call before installing the module — without this step you'd end up with a duplicate.

Do this in **both** `inject()` and `eject()`.

```php
public const MARKER_START = '{* mymodule:start *}';
public const MARKER_END   = '{* mymodule:end *}';
private const WIDGET_RAW_PATTERN = '{widget name="mymodule"';

public function inject(string $templatePath): bool
{
    $content = \Tools::file_get_contents($templatePath);
    if ($content === false) { return false; }

    // Already injected — nothing to do
    if (strpos($content, self::MARKER_START) !== false) { return true; }

    // Remove any pre-existing raw (unmarked) widget call
    $lines = array_values(array_filter(
        explode("\n", $content),
        fn(string $l): bool => strpos($l, self::WIDGET_RAW_PATTERN) === false
    ));

    // Find injection point
    $insertAfterIndex = null;
    foreach ($lines as $i => $line) {
        if (strpos(ltrim($line), '{foreach name="listingproducts"') === 0) {
            $insertAfterIndex = $i;
            break;
        }
    }
    if ($insertAfterIndex === null) { return false; }

    $snippet = [
        '        ' . self::MARKER_START,
        '        {widget name="mymodule" hook="productList" pos_loop=$smarty.foreach.listingproducts.index productClasses=$productClasses}',
        '        ' . self::MARKER_END,
    ];
    array_splice($lines, $insertAfterIndex + 1, 0, $snippet);

    return file_put_contents($templatePath, implode("\n", $lines)) !== false;
}

public function eject(string $templatePath): bool
{
    $content = \Tools::file_get_contents($templatePath);
    if ($content === false) { return false; }
    if (strpos($content, self::MARKER_START) === false) { return true; }

    $filtered = [];
    $inside = false;
    foreach (explode("\n", $content) as $line) {
        if (strpos($line, self::MARKER_START) !== false) { $inside = true; continue; }
        if ($inside && strpos($line, self::MARKER_END) !== false) { $inside = false; continue; }
        // Also strip leftover raw widget calls
        if (!$inside && strpos($line, self::WIDGET_RAW_PATTERN) === false) {
            $filtered[] = $line;
        }
    }

    return file_put_contents($templatePath, implode("\n", $filtered)) !== false;
}
```

### PS Validator requirements

- Use **`\Tools::file_get_contents()`** not native `file_get_contents()` — the PS Validator enforces this
- `file_put_contents()` is allowed for writes

---

## ThemeTemplateInstaller — finding all theme template paths

### NEVER use `Theme::getThemes()`

`Theme` is a legacy PS class. It is not autoloaded in the **Symfony console context** (`php bin/console pr:mo install mymodule`). Calling it throws `Class "Theme" not found`.

### ALWAYS use `scandir(_PS_ALL_THEMES_DIR_)`

```php
use Vendor\MyModule\Service\ThemeTemplateInjector;

class ThemeTemplateInstaller
{
    private ThemeTemplateInjector $injector;

    public function __construct()
    {
        $this->injector = new ThemeTemplateInjector();
    }

    public function install(): void
    {
        foreach ($this->getTemplatePaths() as $path) {
            $this->injector->inject($path);
        }
    }

    public function uninstall(): void
    {
        foreach ($this->getTemplatePaths() as $path) {
            $this->injector->eject($path);
        }
    }

    /** @return array<string> */
    private function getTemplatePaths(): array
    {
        $paths = [];
        $themesDir = _PS_ALL_THEMES_DIR_;

        if (!is_dir($themesDir)) { return $paths; }

        $entries = scandir($themesDir);
        if ($entries === false) { return $paths; }

        foreach ($entries as $entry) {
            if ($entry === '.' || $entry === '..') { continue; }
            $dir = $themesDir . $entry;
            if (!is_dir($dir)) { continue; }
            $tplPath = $dir . DIRECTORY_SEPARATOR . ThemeTemplateInjector::TEMPLATE_RELATIVE_PATH;
            if (is_file($tplPath)) { $paths[] = $tplPath; }
        }

        return $paths;
    }
}
```

---

## Wiring into Installer

```php
// Installer::install()
return $this->registerHooks($module)
    && $this->installDatabase()
    && $this->installTabs()
    && $this->installFixtures()
    && $this->installThemeTemplates();

// Installer::uninstall()
return $this->uninstallTabs()
    && $this->uninstallThemeTemplates()
    && $this->uninstallDatabase();
```

Both `installThemeTemplates()` and `uninstallThemeTemplates()` **must catch all exceptions and return `true`** — theme template injection is optional and must never block a module install or uninstall.

```php
private function installThemeTemplates(): bool
{
    try {
        (new ThemeTemplateInstaller())->install();
    } catch (\Exception $e) {
        // optional — do not block install
    }
    return true;
}

private function uninstallThemeTemplates(): bool
{
    try {
        (new ThemeTemplateInstaller())->uninstall();
    } catch (\Exception $e) {
        // best-effort — do not block uninstall
    }
    return true;
}
```

---

## DI service registration

Register `ThemeTemplateInjector` in `config/common.yml` (not admin-only — a future front controller or admin controller may need it via DI):

```yaml
# config/common.yml
services:
  mymodule.service.theme_template_injector:
    class: Vendor\MyModule\Service\ThemeTemplateInjector
    public: true
```

### Future admin controller button

When adding a "Re-install template" button later, the controller simply does:

```php
$injector = $this->get('mymodule.service.theme_template_injector');
$injector->inject('/path/to/theme/templates/catalog/_partials/productlist.tpl');
```

The `isInjected()` method can be used to show the current status in the UI:

```php
$isInjected = $injector->isInjected($tplPath);
```

No new logic is needed in `ThemeTemplateInjector` — the service already exposes everything needed for a re-install button.
