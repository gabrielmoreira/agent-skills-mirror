# Services & dependency injection

## **CRITICAL: `SymfonyContainer::getInstance()` is null in console context**

`PrestaShop\PrestaShop\Adapter\SymfonyContainer::getInstance()` relies on reading `global $kernel`.

**In the Symfony console context (`php bin/console pr:mo install mymodule`), `$kernel` is never set as a global variable.** The method always returns `null`. Any code that depends on it silently does nothing.

**NEVER use `SymfonyContainer::getInstance()` in install-time code** (FixturesInstaller, ThemeTemplateInstaller, Installer, etc.).

For data access at install time, use `Db::getInstance()` raw SQL. See `module-class-and-installer.md`.

For services at runtime (web request), use `$this->get('service.id')` from the module class or inject via constructor.

---

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
  mymodule.service.my_service:
    class: 'Vendor\MyModule\Service\MyService'
    public: true                             # ← only if accessed via $this->get() from module class
    arguments:
      - '@doctrine.orm.entity_manager'
      - '@prestashop.core.admin.lang.repository'
      $context: "@=service('prestashop.adapter.legacy.context').getContext()"
      $translator: '@translator'

  mymodule.service.another_service:          # private by default — injected via constructor only
    class: 'Vendor\MyModule\Service\AnotherService'
    arguments:
      - '@mymodule.service.my_service'
```

> **Why selective `public: true`?** Symfony best practices require services to be private unless accessed directly via `$container->get()`. A blanket `_defaults: public: true` is valid Symfony syntax but against best practices, and causes a fatal error in PrestaShop's Symfony version when combined with `parent:` services.

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

## PITFALL: `public` cannot be inherited from `_defaults` when `parent` is set

PrestaShop's Symfony version throws a fatal error if a service uses `parent:` and tries to inherit `public: true` from `_defaults`:

```
Attribute "public" on service "mymodule.form.type.foo" cannot be inherited from "_defaults"
when a "parent" is set.
```

This is one reason to avoid `_defaults: public: true` as a blanket default.

Form types registered via `parent: form.type.translatable.aware` do **not** need to be public — they are never fetched via `$this->get()`, only via the form factory. Leave them private (no `public:` at all).

If you have a rare case where a `parent:` service genuinely needs to be public, declare it explicitly on the service itself:

```yaml
# ❌ WRONG — public: true cannot be inherited from _defaults when parent is set
services:
  _defaults:
    public: true

  mymodule.form.type.foo:
    class: Vendor\MyModule\Form\FooType
    parent: "form.type.translatable.aware"   # ← triggers the error
    tags:
      - { name: form.type }

# ✅ CORRECT — don't use _defaults: public: true; only mark public if truly needed via $this->get()
services:
  mymodule.form.type.foo:
    class: Vendor\MyModule\Form\FooType
    parent: "form.type.translatable.aware"   # private by default — form types don't need public
    tags:
      - { name: form.type }

  mymodule.some.other.service:
    class: Vendor\MyModule\Service\SomeService
    public: true                             # ← only if accessed via $this->get() in module class
```


## PITFALL: `FrameworkBundleAdminController::trans()` has a non-standard argument order

The PS parent controller overrides Symfony's `trans()` with a **different signature**:

```php
// PrestaShop FrameworkBundleAdminController
protected function trans($key, $domain, array $parameters = [])
//                              ^^^^^^^ domain is 2nd, parameters 3rd
```

Symfony's standard `TranslatorInterface::trans()` is `trans($id, array $parameters, string $domain)` — the opposite order.

```php
// ❌ WRONG — Symfony order, throws TypeError at runtime
$this->trans('My label', [], 'Modules.Mymodule.Admin');

// ✅ CORRECT — PS FrameworkBundleAdminController order
$this->trans('My label', 'Modules.Mymodule.Admin', []);
```

This applies to **all** `$this->trans()` calls inside controllers that extend `FrameworkBundleAdminController`.
