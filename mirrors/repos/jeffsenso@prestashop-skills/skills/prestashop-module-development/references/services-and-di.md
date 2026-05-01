# Services & dependency injection

## **CRITICAL: Avoid legacy static calls**

❌ **DO NOT USE** legacy static accessor patterns in modern services/controllers:

```php
// ❌ WRONG - avoid these patterns
$context = Context::getContext();
$langId = Language::getLanguageByLocale($locale);
$translator = Context::getContext()->getTranslator();
```

✅ **DO USE** service injection instead:

```yaml
# In config/services.yml or config/admin/services.yml
mymodule.service.my_service:
  class: 'Vendor\MyModule\Service\MyService'
  arguments:
    # Inject entire Context object
    $context: "@=service('prestashop.adapter.legacy.context').getContext()"
    # Or inject specific context properties
    $languageId: "@=service('prestashop.adapter.legacy.context').getContext().language.id"
    $shopId: "@=service('prestashop.adapter.legacy.context').getContext().shop.id"
    # Inject translator
    $translator: '@translator'
```

```php
// Then in your service constructor:
public function __construct(
    private readonly Context $context,
    private readonly TranslatorInterface $translator
) {}

// Use injected dependencies instead of static calls:
$langId = $this->context->language->id;
$message = $this->translator->trans('key.translation', [], 'Modules.Mymodule.Admin');
```

### Common service injection patterns

| Legacy static call | Service injection pattern |
|---|---|
| `Context::getContext()` | `$context: "@=service('prestashop.adapter.legacy.context').getContext()"` |
| `Context::getContext()->language->id` | `$languageId: "@=service('prestashop.adapter.legacy.context').getContext().language.id"` |
| `Context::getContext()->shop->id` | `$shopId: "@=service('prestashop.adapter.legacy.context').getContext().shop.id"` |
| `Context::getContext()->getTranslator()` | `$translator: '@translator'` |
| `Language::getLanguage($id)` | Inject `@prestashop.core.admin.lang.repository` and call `->findOneById($id)` |
| `Configuration::get('KEY')` | `$config: '@prestashop.adapter.legacy.configuration'` → `$config->get('KEY')` |

**Why avoid static calls?**
- Breaks dependency injection principles
- Makes testing impossible (cannot mock)
- Hides dependencies (not visible in constructor)
- Violates SOLID principles
- PrestaShop is moving away from static patterns in modern code

## Defining services in `config/services.yml`

```yaml
services:
  _defaults:
    public: true

  mymodule.service.my_service:
    class: 'Vendor\MyModule\Service\MyService'
    arguments:
      - '@doctrine.orm.entity_manager'
      - '@prestashop.core.admin.lang.repository'
      $context: "@=service('prestashop.adapter.legacy.context').getContext()"
      $translator: '@translator'

  mymodule.service.another_service:
    class: 'Vendor\MyModule\Service\AnotherService'
    arguments:
      - '@mymodule.service.my_service'
```

## Accessing services in module controllers

Controllers extending `FrameworkBundleAdminController` can use `$this->get('service.id')`:

```php
$myService = $this->get('mymodule.service.my_service');
```

> **Note**: `$this->get()` is available in Symfony controllers. In non-controller classes, inject the service via the constructor (prefer constructor injection).

## Accessing services from the module class (`mymodule.php`)

```php
$router = $this->get('router');
// or via static accessor:
$container = \PrestaShop\PrestaShop\Adapter\SymfonyContainer::getInstance();
$router = $container->get('router');
```

## Commonly used PS core services

| Service ID | Purpose |
|---|---|
| `router` | Generate URLs |
| `prestashop.adapter.legacy.configuration` | Read/write PS `Configuration` table |
| `prestashop.adapter.shop.context` | Shop context info |
| `prestashop.adapter.legacy.context` | Legacy `Context` object |
| `prestashop.core.hook.dispatcher` | Dispatch hooks |
| `form.factory` | Create Symfony forms |
| `doctrine.dbal.default_connection` | Raw DBAL queries |
| `prestashop.bundle.grid.response_builder` | Grid search redirects |
| `prestashop.core.grid.filter.form_factory` | Grid filter forms |

## Expression Language in services.yml

Use `@=` for computed arguments:

```yaml
arguments:
  - "@=service('prestashop.adapter.shop.context').getContextListShopID()[0]"
  - "@=service('prestashop.adapter.legacy.context').getContext().language.id"
```

## Resources

- [Symfony DI documentation](https://symfony.com/doc/current/service_container.html)
- [PS service container](https://devdocs.prestashop-project.org/9/development/architecture/dependency-injection/)
