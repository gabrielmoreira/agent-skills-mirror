---
name: atomic-framework-data
description: "Use when working on Atomic data layer: Model, Validator, cache drivers, Codes, Enums, Exceptions hierarchy, file exports (PDF/XLS/CSV), and Support helpers."
argument-hint: "Model, validation, cache, enums, exceptions, PDF/XLS/CSV export"
user-invocable: true
---

# Atomic Framework Data

## When to Use
- Creating or editing models (Cortex ORM).
- Adding validation rules, handling validation errors.
- Using or extending cache (DB, Memcached), transient values, or code enums.
- Throwing or catching domain-specific exceptions.
- Generating PDF, XLS, or CSV files.
- Using or adding global helper functions.

## Engine Files
`engine/Atomic/App/Model.php`, `engine/Atomic/Validator/*`, `engine/Atomic/Cache/*`, `engine/Atomic/Codes/Code.php`, `engine/Atomic/Enums/*`, `engine/Atomic/Exceptions/*`, `engine/Atomic/Files/*`, `engine/Atomic/Support/helpers.php`

## Reference Docs
`docs/model.md`, `docs/atomic_pdf.md`, `docs/atomic_xls.md`, `docs/database.md`, `docs/errorhandler.md`, `docs/transient.md`, `docs/security.md`

---

## Model

`Engine\Atomic\App\Model` extends F3 Cortex ORM.

```php
use Engine\Atomic\App\Model;

final class Post extends Model
{
    protected $table = 'posts';          // auto-prefixed with DB_CONFIG.ATOMIC_DB_PREFIX

    protected $fieldConf = [
        'title' => ['type' => 'VARCHAR256', 'nullable' => false],
        'body'  => ['type' => 'TEXT',       'nullable' => true],
    ];
}

// Save with built-in validation
$post = new Post();
$post->title = 'Hello';

if (!$post->save()) {
    [$code, $vars] = $post->get_last_err_data();
    // or:
    $code = $post->get_last_err_code();
    $vars = $post->get_last_err_vars();
}
```

### Bulk update

```php
$post->update_property(['status = ?', 'draft'], 'status', 'published');
```

### Validation hook

Override `before_validate()` for pre-validation transforms.

## Validator

`Engine\Atomic\Validator\Validator` runs on `save()`.
`Engine\Atomic\Validator\ValidatorModelTrait` adds validation to any model.

Validation rules come from `Enums\Rule` (PHP 8.1 backed enum).

## Enums

### Role (`Enums\Role`)

```php
use Engine\Atomic\Enums\Role;

Role::ADMIN->value     // 'admin'
Role::SELLER->value    // 'seller'
Role::BUYER->value     // 'buyer'
Role::MODERATOR->value // 'moderator'
Role::SUPPORT->value   // 'support'

Role::all();                    // ['admin', 'seller', 'buyer', 'moderator', 'support']
Role::is_valid('admin');        // bool

// In Guard checks:
Guard::has_role(Role::ADMIN);
has_role(Role::SELLER);
```

### Currency (`Enums\Currency`)

```php
use Engine\Atomic\Enums\Currency;

Currency::USD->value;       // 'USD'
Currency::EUR->value;       // 'EUR'
Currency::UAH->value;       // 'UAH'
Currency::RUB->value;       // 'RUB'

Currency::USD->symbol();        // '$'
Currency::EUR->symbol();        // '€'
Currency::UAH->symbol();        // '₴'

Currency::USD->display_name();  // 'US Dollar'
Currency::USD->to_array();      // ['value'=>'USD', 'symbol'=>'$', 'display_name'=>'US Dollar']
Currency::get_available();      // [Currency::USD, Currency::EUR, ...]
```

### Language (`Enums\Language`)

```php
use Engine\Atomic\Enums\Language;

Language::EN->value;            // 'en'
Language::UK->value;            // 'uk'
Language::RU->value;            // 'ru'
// also: ES, FR, DE, IT, PT, NL, PL

Language::EN->display_name();   // 'English'
Language::UK->display_name();   // 'Українська'
Language::get_all();            // ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru', 'uk']
```

### LogLevel / LogChannel

```php
use Engine\Atomic\Enums\LogLevel;
use Engine\Atomic\Enums\LogChannel;

// LogLevel (PSR-3 levels)
LogLevel::EMERGENCY; LogLevel::ALERT; LogLevel::CRITICAL;
LogLevel::ERROR; LogLevel::WARNING; LogLevel::NOTICE;
LogLevel::INFO; LogLevel::DEBUG;
LogLevel::ERROR->to_int();  // 3 (lower = more severe)

// LogChannel (named log files)
LogChannel::ERROR;         // error.log
LogChannel::AUTH;          // auth.log
LogChannel::QUEUE_WORKER;  // queue_worker.log
LogChannel::QUEUE_MONITOR; // queue_monitor.log
```

### Rule (`Enums\Rule`)

Validation rules used in `fieldConf['rules']` arrays. All cases are backed strings.

```php
use Engine\Atomic\Enums\Rule;

// Full enum (backed string enum):
Rule::UUID_V4           // 'uuid_v4'   -- valid UUID v4
Rule::EMAIL             // 'email'     -- valid email address
Rule::URL               // 'url'       -- valid URL
Rule::ENUM              // 'enum'      -- value in fieldConf['enum'] array
Rule::REGEX             // 'regex'     -- matches fieldConf['pattern']
Rule::CALLBACK          // 'callback'  -- fieldConf['callback'] callable returns bool
Rule::NUM_MIN           // 'num_min'   -- numeric >= fieldConf['min']
Rule::NUM_MAX           // 'num_max'   -- numeric <= fieldConf['max']
Rule::STR_MIN           // 'str_min'   -- byte length >= fieldConf['min']
Rule::STR_MAX           // 'str_max'   -- byte length <= fieldConf['max']
Rule::MB_MIN            // 'mb_min'    -- UTF-8 char count >= fieldConf['min']
Rule::MB_MAX            // 'mb_max'    -- UTF-8 char count <= fieldConf['max']
Rule::PASSWORD_ENTROPY  // 'password_entropy' -- entropy >= fieldConf['min_entropy'] (default 18.0)
```

Usage in `fieldConf`:

```php
protected $fieldConf = [
    'email' => [
        'type'     => 'VARCHAR256',
        'required' => true,
        'rules'    => [Rule::EMAIL],
    ],
    'slug' => [
        'type'    => 'VARCHAR128',
        'rules'   => [Rule::REGEX],
        'pattern' => '/^[a-z0-9-]+$/',
    ],
    'password' => [
        'type'           => 'VARCHAR256',
        'rules'          => [Rule::MB_MIN, Rule::PASSWORD_ENTROPY],
        'min'            => 8,
        'min_entropy'    => 20.0,   // optional, default 18.0
    ],
    'status' => [
        'type'   => 'VARCHAR128',
        'rules'  => [Rule::ENUM],
        'enum'   => ['draft', 'published', 'archived'],
    ],
    'user_uuid' => [
        'type'  => 'VARCHAR128',
        'rules' => [Rule::UUID_V4],
    ],
];
```

`required`, `nullable`, and `unique` are **not** Rule cases -- they are plain `fieldConf` keys (booleans).

## Exceptions

Hierarchy: `AtomicException` → domain exceptions.

```
AtomicException
  AuthenticationException
  ConfigurationException
  FileProcessingException
    ImportException              // extends FileProcessingException
  InsufficientStockException
  NotFoundException
  PaymentException
  ValidationException
```

Always throw the most specific exception. Catch at the controller or middleware boundary.

```php
use Engine\Atomic\Exceptions\NotFoundException;
use Engine\Atomic\Exceptions\ValidationException;
use Engine\Atomic\Exceptions\PaymentException;

throw new NotFoundException('Product not found');
throw new ValidationException('Invalid email format');
throw new PaymentException('Payment gateway timeout');
```

## Codes (`Codes\Code`)

`Engine\Atomic\Codes\Code` -- string constants returned by the validator and used in API responses.

```php
use Engine\Atomic\Codes\Code;

// Generic HTTP-style codes
Code::SUCCESS           // '200'
Code::BAD_REQUEST       // '400'
Code::UNAUTHORIZED      // '401'
Code::FORBIDDEN         // '403'
Code::RATE_LIMIT        // '429'
Code::NONCE_INVALID     // '440'
Code::SERVER_ERROR      // '500'
Code::SERVICE_UNAVAILABLE // '503'

// OAuth-specific codes
Code::OAUTH_TOKEN_ERROR             // '450'
Code::OAUTH_USER_DATA_ERROR         // '451'
Code::OAUTH_ACCOUNT_ALREADY_LINKED  // '452'
Code::OAUTH_NOT_CONFIGURED          // '453'
Code::OAUTH_INVALID_STATE           // '454'
```

Convention: models define field-level error constants following the pattern:
`Code::{MODEL}_{FIELD}_{SUFFIX}`, e.g. `Code::USER_EMAIL_REQUIRED`, `Code::USER_EMAIL_FORMAT`.
The validator auto-resolves these from field name and model class name.

## Cache Drivers and CacheManager

`Engine\Atomic\Core\CacheManager` -- factory for all cache backends.

```php
use Engine\Atomic\Core\CacheManager;

$cm = CacheManager::instance();

// Get a specific driver (returns F3 \Cache-compatible instance)
$redis     = $cm->redis();           // uses REDIS.* hive config
$db        = $cm->db();              // uses DB connection
$memcached = $cm->memcached();       // uses MEMCACHED.* hive config

// Custom Redis config (bypasses shared instance)
$cache = $cm->redis([
    'server'   => '127.0.0.1',
    'port'     => 6379,
    'password' => 'secret',
]);

// Auto-select: tries redis → memcached → db in order
$best = $cm->cascade();

// Use like F3 \Cache:
$best->set('key', $data, 3600);
$val = $best->get('key');
$best->clear('key');
```

Config constants for ImageOptimizer (used by built-in queue applications):
- `ATOMIC_JPEG_QUALITY` (default 85)
- `ATOMIC_PNG_COMPRESSION_LEVEL` (default 6)
- `ATOMIC_WEBP_QUALITY` (default 85)
- `ATOMIC_AVIF_QUALITY` (default 50)

`Engine\Atomic\Cache\DB` and `Engine\Atomic\Cache\Memcached` are the low-level drivers used by `CacheManager`.

## File Export

### PDF

Use `Engine\Atomic\Files\PDF` (TCPDF wrapper). See `docs/atomic_pdf.md` for full API.

### XLS

Use `Engine\Atomic\Files\XLS` (PhpSpreadsheet wrapper). See `docs/atomic_xls.md`.

### CSV

`Engine\Atomic\Files\CSV` for comma-separated exports.

Font data for PDF lives in `engine/Atomic/Files/fonts/` (DejaVu Sans included).

## Support Helpers

All global PHP functions used across the codebase are defined in `engine/Atomic/Support/helpers.php`.

Examples:
```php
plugin_manager();           // Engine\Atomic\App\PluginManager instance
get_plugin('Monopay');      // plugin instance or null
has_plugin('Google');       // bool
enable_plugin('name');
disable_plugin('name');

ai_connector('sk-...');     // AIConnector singleton

// request helpers
is_home(); is_page('/x'); is_ajax(); is_ssl(); is_mobile();
current_path(); url_segments(); get_segment(0);

// mail
mail_to('a@b.com')->set_html('<h1>Hi</h1>')->send('Subject');
mail_send('a@b.com', 'Subject', $html);

// theme
get_head(); get_header(); get_footer(); get_section('hero');

// transient
set_transient('key', $val, 3600);
get_transient('key');
delete_transient('key');

// nonce
create_nonce('delete-post', 1800);
verify_nonce($_POST['nonce'] ?? '', 'delete-post');
```

## Guardrails
- Use the most specific `Exception` subclass; never throw a bare `\Exception` for domain errors.
- Model validation runs automatically on `save()`; do not bypass it by calling raw ORM methods.
- Table names are auto-prefixed; do not hardcode full table names in queries.
