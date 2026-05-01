# Legacy code conversion patterns

## Static calls (Context, Configuration, Language)

**Legacy** (do not use in services/controllers):
```php
$context = Context::getContext();
$langId = $context->language->id;
$shopId = $context->shop->id;
$translator = $context->getTranslator();
Configuration::updateValue('MY_KEY', 'value');
$value = Configuration::get('MY_KEY');
```

**Modern** — use service injection:
```yaml
# config/services.yml
mymodule.service.my_service:
  class: 'Vendor\MyModule\Service\MyService'
  arguments:
    $context: "@=service('prestashop.adapter.legacy.context').getContext()"
    $translator: '@translator'
    $configuration: '@prestashop.adapter.legacy.configuration'
```

```php
public function __construct(
    private readonly Context $context,
    private readonly TranslatorInterface $translator,
    private readonly Configuration $configuration
) {}

public function doSomething(): void
{
    $langId = $this->context->language->id;
    $shopId = $this->context->shop->id;
    $message = $this->translator->trans('key', [], 'Modules.Mymodule.Admin');
    $this->configuration->set('MY_KEY', 'value');
}
```

Read `references/services-and-di.md` for complete list of injection patterns.

## Configuration page

**Legacy** (do not use):
```php
public function getContent()
{
    $output = '';
    if (Tools::isSubmit('submit')) {
        // Process form manually
        Configuration::updateValue('MY_SETTING', Tools::getValue('my_setting'));
        $output .= $this->displayConfirmation($this->l('Settings updated'));
    }
    return $output . $this->displayForm();
}

private function displayForm()
{
    $helper = new HelperForm();
    // ... HelperForm setup ...
}
```

**Modern** — use Symfony form components. Read `references/configuration-page.md`.

## Database access

**Legacy**:
```php
Db::getInstance()->execute('INSERT INTO `' . _DB_PREFIX_ . 'my_table` ...');
$rows = Db::getInstance(_PS_USE_SQL_SLAVE_)->executeS('SELECT ...');
```

**Modern** — use Doctrine entities and repositories. Read `references/database-and-entities.md`.

For simple read queries in modules that do not use Doctrine ORM, `Db::getInstance()` is still acceptable; just always sanitize inputs (cast with `(int)`, escape with `pSQL()`).

## Admin controllers

**Legacy** — extends `AdminController` or `ModuleAdminController`:
```php
class AdminMyModuleController extends ModuleAdminController
{
    public function __construct()
    {
        $this->table = 'my_table';
        $this->className = 'MyEntityObjectModel';
        // ...
    }
}
```

**Modern** — Symfony controller extending `FrameworkBundleAdminController`, routed via `config/routes.yml`. Read `references/configuration-page.md` for the full pattern.

## Position management

**Legacy** — jQuery UI sortable (`addJqueryUI('ui.sortable')`) + custom admin.js:
```js
$('#my-list').sortable({
    update: function() { $.post(ajaxPositionUrl, { ... }); }
});
```

**Modern** — use the PS Grid `PositionColumn` and the pre-built Grid JS bundle. Read `references/grid-system.md`.

## ObjectModel vs Doctrine

ObjectModel can be retained for simple entities that do not need repository queries or Grid integration. When adding a list page, migrate to Doctrine DBAL queries in a `QueryBuilder` class (Grid system pattern).

## Hook registration

**Legacy**:
```php
$this->registerHook('displayHeader');
// Inline in install() method
```

**Modern** — registered via `Installer::registerHooks()`. Read `references/module-class-and-installer.md`.
