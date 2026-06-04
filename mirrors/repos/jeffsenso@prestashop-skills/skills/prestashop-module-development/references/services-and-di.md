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

---

## Symfony Console Commands

### **CRITICAL: Commands must be registered in `config/admin/services.yml`**

Console commands run in the **admin kernel context**. They must be registered in `config/admin/services.yml`, **NOT** in `config/common.yml` or `config/front/services.yml`.

```yaml
# config/admin/services.yml
services:
  mymodule.command.my_command:
    class: Vendor\MyModule\Command\MyCommand
    arguments:
      - "@mymodule.service.my_service"
    tags:
      - { name: console.command, command: modulename:action }
```

**Why admin only?**
- Console commands are executed via `php bin/console`, which uses the admin kernel
- Commands registered in `common.yml` or `front/services.yml` will not be discovered by the console application
- Services needed by commands should be in `common.yml` (if shared) or `admin/services.yml` (if admin-specific)

### Command Naming Convention

Format: `modulename:action`

Examples:
- `wsautocartrules:create`
- `ws_keepdblight:cleandb`
- `mymodule:import`
- `mymodule:export-products`

**Rules:**
- Use module name as namespace (underscores allowed)
- Use colon `:` to separate namespace from action
- Action should be a descriptive verb or verb phrase
- Use hyphens for multi-word actions: `export-products`, not `exportProducts`

### Command Class Structure

```php
namespace Vendor\MyModule\Command;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

class MyCommand extends Command
{
    private MyService $myService;

    public function __construct(MyService $myService)
    {
        parent::__construct(); // CRITICAL: call parent constructor
        $this->myService = $myService;
    }

    protected function configure(): void
    {
        $this
            ->setDescription('Brief description of what the command does')
            ->addOption(
                'limit',
                'l',
                InputOption::VALUE_OPTIONAL,
                'Limit processing to N items (0 = unlimited)',
                10
            )
            ->addArgument(
                'type',
                InputArgument::OPTIONAL,
                'Type of items to process'
            );
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        
        $limit = (int) $input->getOption('limit');
        $type = $input->getArgument('type');
        
        $io->title('Processing Items');
        $io->text(sprintf('Limit: %d', $limit));
        
        try {
            $result = $this->myService->process($limit, $type);
            $io->success(sprintf('Processed %d items', $result));
            return 0; // Success
        } catch (\Exception $e) {
            $io->error($e->getMessage());
            return 1; // Failure
        }
    }
}
```

### Return Codes

**CRITICAL**: Return integer codes, **NOT** `Command::SUCCESS` or `Command::FAILURE` constants (not available in PrestaShop's Symfony version).

```php
// ✅ CORRECT
return 0; // Success
return 1; // Failure

// ❌ WRONG — constants not available
return Command::SUCCESS;  // Fatal error
return Command::FAILURE;  // Fatal error
```

### SymfonyStyle Output

Use `SymfonyStyle` for rich, formatted console output:

```php
$io = new SymfonyStyle($input, $output);

// Titles and sections
$io->title('Main Title');
$io->section('Section Title');

// Messages
$io->text('Simple text message');
$io->text(['Line 1', 'Line 2', 'Line 3']);

// Styled messages
$io->success('Operation completed successfully');
$io->error('An error occurred');
$io->warning('This is a warning');
$io->note('This is a note');

// Lists
$io->listing(['Item 1', 'Item 2', 'Item 3']);

// Tables
$io->table(
    ['ID', 'Name', 'Email'],
    [
        [1, 'John', 'john@example.com'],
        [2, 'Jane', 'jane@example.com'],
    ]
);

// Progress bar
$io->progressStart(100);
for ($i = 0; $i < 100; $i++) {
    // Process item
    $io->progressAdvance();
}
$io->progressFinish();

// Ask questions
$answer = $io->ask('What is your name?');
$confirmed = $io->confirm('Continue?', false);
$choice = $io->choice('Select option', ['A', 'B', 'C']);
```

### Input Options vs Arguments

**Options**: Named parameters with `--` prefix
```php
// Define
->addOption('limit', 'l', InputOption::VALUE_OPTIONAL, 'Limit', 10)

// Use
php bin/console mymodule:process --limit=50
php bin/console mymodule:process -l 50

// Access
$limit = (int) $input->getOption('limit');
```

**Arguments**: Positional parameters (no `--` prefix)
```php
// Define
->addArgument('filename', InputArgument::REQUIRED, 'Filename')

// Use
php bin/console mymodule:import products.csv

// Access
$filename = $input->getArgument('filename');
```

**Argument modes**:
- `InputArgument::REQUIRED` - Must be provided
- `InputArgument::OPTIONAL` - Optional (provide default in constructor)
- `InputArgument::IS_ARRAY` - Accept multiple values

**Option modes**:
- `InputOption::VALUE_NONE` - Boolean flag (presence = true)
- `InputOption::VALUE_REQUIRED` - Must have a value
- `InputOption::VALUE_OPTIONAL` - Optional value (provide default in constructor)
- `InputOption::VALUE_IS_ARRAY` - Accept multiple values

### Service Injection

Commands receive services via constructor injection:

```php
class MyCommand extends Command
{
    public function __construct(
        private MyService $myService,
        private AnotherService $anotherService
    ) {
        parent::__construct(); // CRITICAL: always call parent
    }
}
```

Service definition:
```yaml
mymodule.command.my_command:
  class: Vendor\MyModule\Command\MyCommand
  arguments:
    - "@mymodule.service.my_service"
    - "@mymodule.service.another_service"
  tags:
    - { name: console.command, command: mymodule:process }
```

### Best Practices

1. **Always inject services** - Never use static calls or `$this->get()`
2. **Use SymfonyStyle** - Provides consistent, rich output
3. **Add --limit option** - For commands processing many items
4. **Provide progress feedback** - Use progress bars or status messages
5. **Return proper exit codes** - 0 for success, 1 for failure
6. **Catch exceptions** - Wrap main logic in try/catch
7. **Validate input early** - Check arguments/options before processing
8. **Use descriptive names** - Both command name and option/argument names
9. **Add help text** - Use `setDescription()` and option/argument descriptions
10. **Test with --help** - Verify help output: `php bin/console mymodule:command --help`

### Common Patterns

**Processing with limit:**
```php
$limit = (int) $input->getOption('limit');
$items = $this->myService->getItems();

$itemsToProcess = $limit > 0 ? array_slice($items, 0, $limit) : $items;

$io->text(sprintf('Found %d items. Processing %d...', count($items), count($itemsToProcess)));

foreach ($itemsToProcess as $item) {
    // Process item
}
```

**Dry-run mode:**
```php
->addOption('dry-run', null, InputOption::VALUE_NONE, 'Simulate without making changes')

if ($input->getOption('dry-run')) {
    $io->note('DRY RUN MODE - No changes will be made');
}
```

**Verbose output:**
```php
if ($output->isVerbose()) {
    $io->text('Detailed debug information...');
}
```

### Example: Complete Command

```php
namespace Ws\AutoCartRules\Command;

use CartRule;
use Configuration;
use DateTime;
use Language;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Ws\AutoCartRules\Service\EligibleCustomerService;

class CreateAutoCartRulesCommand extends Command
{
    private EligibleCustomerService $eligibleCustomerService;

    public function __construct(EligibleCustomerService $eligibleCustomerService)
    {
        parent::__construct();
        $this->eligibleCustomerService = $eligibleCustomerService;
    }

    protected function configure(): void
    {
        $this
            ->setDescription('Create cart rules for eligible customers')
            ->addOption(
                'limit',
                'l',
                InputOption::VALUE_OPTIONAL,
                'Limit customers to process (0 = all)',
                5
            );
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);

        $reductionPercent = (float) Configuration::get('WSAUTOCARTRULES_REDUCTION_PERCENTAGE');
        $pricingLevel = (float) Configuration::get('WSAUTOCARTRULES_PRICING_LEVEL');
        $durationDays = (int) Configuration::get('WSAUTOCARTRULES_DURATION_DAYS');

        if ($reductionPercent <= 0 || $pricingLevel <= 0 || $durationDays <= 0) {
            $io->error('Invalid configuration');
            return 1;
        }

        $limit = (int) $input->getOption('limit');

        $io->title('Creating Auto Cart Rules');
        $io->text([
            sprintf('Reduction: %s%%', $reductionPercent),
            sprintf('Pricing Level: €%s', $pricingLevel),
            sprintf('Duration: %d days', $durationDays),
            sprintf('Limit: %s', $limit > 0 ? $limit : 'No limit'),
        ]);

        $customers = $this->eligibleCustomerService->getEligibleCustomers($pricingLevel);

        if (empty($customers)) {
            $io->warning('No eligible customers found');
            return 0;
        }

        $customersToProcess = $limit > 0 ? array_slice($customers, 0, $limit) : $customers;

        $created = 0;
        $failed = 0;

        foreach ($customersToProcess as $customer) {
            try {
                // Create cart rule logic here
                ++$created;
                $io->success(sprintf(
                    '[%d/%d] Created for %s %s',
                    $created + $failed,
                    count($customersToProcess),
                    $customer['firstname'],
                    $customer['lastname']
                ));
            } catch (\Exception $e) {
                ++$failed;
                $io->error($e->getMessage());
            }
        }

        $io->section('Summary');
        $io->text([
            sprintf('Total eligible: %d', count($customers)),
            sprintf('Processed: %d', count($customersToProcess)),
            sprintf('Created: %d', $created),
            sprintf('Failed: %d', $failed),
        ]);

        return $created > 0 ? 0 : 1;
    }
}
```

### References

- [Symfony Console Commands](https://symfony.com/doc/current/console.html)
- [SymfonyStyle](https://symfony.com/doc/current/console/style.html)
- PrestaShop core commands: `/src/PrestaShopBundle/Command/`
