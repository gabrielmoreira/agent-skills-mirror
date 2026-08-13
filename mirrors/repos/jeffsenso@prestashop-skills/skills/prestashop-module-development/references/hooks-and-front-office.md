# Hooks & front office integration

## Registering hooks

Register hooks via the `Installer`:

```php
private array $hooks = ['displayHome', 'displayFooter', 'actionFrontControllerSetMedia'];
```

## **CRITICAL: Asset registration — Use `actionFrontControllerSetMedia`**

**MANDATORY**: For front-office CSS/JS registration, **ALWAYS use `actionFrontControllerSetMedia` hook**, **NEVER use `header` or `displayHeader`**:

```php
// ✅ CORRECT: Use actionFrontControllerSetMedia for front-office assets
public function hookActionFrontControllerSetMedia(): void
{
    $this->context->controller->registerStylesheet(
        'mymodule-front-css',
        'modules/' . $this->name . '/views/css/front.css',
        [
            'media' => 'all',
            'priority' => 200,
        ]
    );

    $this->context->controller->registerJavascript(
        'mymodule-front-js',
        'modules/' . $this->name . '/views/js/front.js',
        [
            'position' => 'bottom',
            'priority' => 200,
        ]
    );
}

// ❌ WRONG: DO NOT use header or displayHeader for assets
public function hookHeader() // WRONG!
{
    $this->context->controller->registerStylesheet(...);
}

public function hookDisplayHeader() // WRONG!
{
    $this->context->controller->addCSS(...);
}
```

**Why `actionFrontControllerSetMedia`?**
- ✅ Designed specifically for asset registration
- ✅ Executes at the correct point in the page lifecycle
- ✅ PrestaShop best practice and modern standard
- ✅ Better performance — assets are collected before page rendering
- ❌ `header`/`displayHeader` are display hooks meant for HTML output, not asset registration

## Hook method patterns

```php
// Render a Smarty template from a hook
public function hookDisplayProductAdditionalInfo($params)
{
    $this->smarty->assign([
        'product' => $params['product'],
        'module_setting' => Configuration::get('MYMODULE_SETTING'),
    ]);

    return $this->display(__FILE__, 'views/templates/hook/product_additional_info.tpl');
}
```

## Widget interface (front office data provider)

**CRITICAL**: When implementing `WidgetInterface`, **DO NOT define explicit hook methods** like `hookDisplayHome()` or `hookDisplayFooter()` that just call `renderWidget()`. PrestaShop automatically handles this for all registered hooks.

```php
use PrestaShop\PrestaShop\Core\Module\WidgetInterface;

class MyModule extends Module implements WidgetInterface
{
    // ✅ CORRECT: Only implement the two WidgetInterface methods
    public function renderWidget($hookName, array $configuration): string
    {
        if (!$this->isCached($this->getTemplatePath(), $this->getCacheId())) {
            $this->smarty->assign($this->getWidgetVariables($hookName, $configuration));
        }
        
        return $this->fetch($this->getTemplatePath(), $this->getCacheId());
    }

    public function getWidgetVariables($hookName, array $configuration): array
    {
        return [
            'items' => $this->getSomeData(),
            'script_url' => Configuration::get('MYMODULE_SCRIPT_URL', ''),
        ];
    }
    
    // ❌ WRONG: DO NOT create explicit hook methods for widgets
    // public function hookDisplayHome(array $params): string
    // {
    //     return $this->renderWidget('displayHome', $params); // PrestaShop does this automatically!
    // }
    
    // ❌ WRONG: DO NOT create explicit hook methods for widgets  
    // public function hookDisplayFooter(array $params): string
    // {
    //     return $this->renderWidget('displayFooter', $params); // PrestaShop does this automatically!
    // }
}
```

**Why this works**: When you implement `WidgetInterface` and register a display hook (e.g., `displayHome`, `displayFooter`, `displayProductAdditionalInfo`), PrestaShop **automatically calls `renderWidget($hookName, $configuration)` for that hook**. You don't need to create explicit `hook*()` methods.

**When to create explicit hook methods**: Only when you need hook-specific logic that differs from the standard widget rendering. For example:
- Different data for different hooks
- Hook-specific conditions
- Special handling for a particular hook

But for simple widget display, let PrestaShop handle it automatically.

## Passing Configuration values to JavaScript (Data-Attribute Pattern)

**Problem:** JavaScript needs access to user-configurable module settings (carousel speed, animation duration, API keys, etc.)

**Solution:** Configuration → PHP → Template data-attributes → JavaScript reads attributes

This is the **standard PrestaShop pattern** used by core modules (ps_imageslider, ps_featuredproducts, etc.):

### 1. Store configuration in Configuration table

```php
// src/Install/ConfigurationInstaller.php
public function install(): bool
{
    Configuration::updateValue('MYMODULE_SPEED', 5000);
    Configuration::updateValue('MYMODULE_PAUSE_ON_HOVER', true);
    return true;
}
```

### 2. Fetch and pass to template in getWidgetVariables()

```php
// Main module class
public function getWidgetVariables($hookName = null, array $configuration = []): array
{
    $vars = [];
    
    // Fetch your data (sliders, products, etc.)
    $vars['items'] = $this->get('mymodule.repository')->getItems();
    
    // Fetch configuration and pass to template
    $vars['mymodule_config'] = [
        'speed' => (int) Configuration::get('MYMODULE_SPEED', 5000),
        'pause' => Configuration::get('MYMODULE_PAUSE_ON_HOVER', true) ? 'hover' : '',
        'wrap' => 'true',
    ];
    
    return $vars;
}
```

### 3. Output as HTML data-attributes in template

```smarty
{* views/templates/hook/mywidget.tpl *}
<div class="mywidget-container" 
     data-interval="{$mymodule_config.speed}" 
     data-wrap="{$mymodule_config.wrap}" 
     data-pause="{$mymodule_config.pause}">
  {* Widget content *}
</div>
```

### 4. Read data-attributes in JavaScript

```javascript
// views/js/front.js
jQuery(document).ready(function ($) {
  $('.mywidget-container').each(function () {
    var $container = $(this);
    
    // Read configuration from data-attributes
    var interval = parseInt($container.data('interval')) || 5000;
    var pause = $container.data('pause') || 'hover';
    var wrap = $container.data('wrap') === 'true' || $container.data('wrap') === true;
    
    // Initialize with configuration
    $container.myPlugin({
      interval: interval,
      pause: pause,
      wrap: wrap
    });
  });
});
```

### Why this pattern?

- ✅ **Separation of concerns:** Configuration in PHP, presentation in template, behavior in JS
- ✅ **User-configurable:** Admin can change settings via back office without editing JS
- ✅ **Multiple instances:** Each widget instance can have different configs
- ✅ **PrestaShop standard:** Same pattern as ps_imageslider, ps_featuredproducts, ps_carousel
- ✅ **No AJAX needed:** Configuration available on page load
- ✅ **Cache-friendly:** Data-attributes cached with HTML

### Common mistakes to avoid

❌ **Hardcoding values in template:** `data-interval="5000"` (not configurable)  
✅ **Use template variable:** `data-interval="{$mymodule_config.speed}"`

❌ **Hardcoding in JavaScript:** `$container.carousel({interval: 5000})` (not configurable)  
✅ **Read from data-attributes:** `var interval = parseInt($container.data('interval')) || 5000;`

❌ **Not passing config in getWidgetVariables():** Template has no access to Configuration values  
✅ **Always include config array:** `$vars['mymodule_config'] = [...]`

❌ **Using global JavaScript variables:** `var MYMODULE_CONFIG = {speed: 5000};` (namespace pollution, hard to debug)  
✅ **Use data-attributes:** Scoped to each widget instance, no globals

## Back-office header hook (injecting JS vars)

Use `hookDisplayBackOfficeHeader` to inject JavaScript variables and assets only for the relevant controller:

```php
public function hookDisplayBackOfficeHeader()
{
    $controller = Tools::getValue('controller');
    if ($controller === 'AdminMymoduleMyentity') {
        Media::addJsDef([
            'myVar' => 'value',
        ]);
        $this->context->controller->addJS($this->_path . 'views/js/admin.js');
    }
}
```

## Resources

- [Hooks reference](https://devdocs.prestashop-project.org/9/modules/concepts/hooks/)
- [Widget interface](https://devdocs.prestashop-project.org/9/modules/concepts/widget/)
