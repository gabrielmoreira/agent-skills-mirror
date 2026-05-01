# Hooks & front office integration

## Registering hooks

Register hooks via the `Installer`:

```php
private array $hooks = ['displayHeader', 'displayFooter', 'displayProductAdditionalInfo'];
```

## Hook method patterns

```php
// Load CSS/JS only when needed
public function hookDisplayHeader($params)
{
    if ($this->context->controller instanceof ProductController) {
        $this->context->controller->addCSS($this->_path . 'views/css/front.css');
        $this->context->controller->addJS($this->_path . 'views/js/front.js');
    }
}

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

Implement `WidgetInterface` when the module exposes a widget to themes:

```php
use PrestaShop\PrestaShop\Core\Module\WidgetInterface;

class MyModule extends Module implements WidgetInterface
{
    public function renderWidget($hookName = null, array $configuration = []): string
    {
        if (!$this->isCached($this->templateFile, $this->getCacheId($hookName))) {
            $this->smarty->assign($this->getWidgetVariables($hookName, $configuration));
        }
        return $this->fetch($this->templateFile, $this->getCacheId($hookName));
    }

    public function getWidgetVariables($hookName = null, array $configuration = []): array
    {
        return [
            'items' => $this->getSomeData(),
        ];
    }
}
```

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
