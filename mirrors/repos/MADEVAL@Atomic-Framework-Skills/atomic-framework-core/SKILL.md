---
name: atomic-framework-core
description: "Use when working on Atomic Core: bootstrap, config loading, App class, request/response helpers, routing, middleware, logging channels, error handling, Prefly checks, DB connections, migrations, crypto, guard roles, ID generation, upload, filesystem, and all route-loader behavior."
argument-hint: "Core bootstrap, config, middleware, logging, routing, crypto, migrations"
user-invocable: true
---

# Atomic Framework Core

## When to Use
- Writing or changing bootstrap, config, or request lifecycle behavior.
- Adding/modifying middleware, routes, or error handling.
- Using logging, crypto, guard, ID, upload, or filesystem utilities.
- Running or writing migrations, seeders, or DB connection management.

## Engine Files
`engine/Atomic/Core/` - App, CacheManager, Config/*, ConnectionManager, Crypto, ErrorHandler, ExceptionHandlerRegistrar, Filesystem, Guard, ID, Log, LogChannel, Methods, Middleware/*, Migrations, Prefly, Redactor, Request, Response, RouteLoader, Routes/*, Seeder, Traits/Singleton, Upload, Database/Migrations/*

## Reference Docs
`docs/atomic_core.md`, `docs/atomic_methods.md`, `docs/config.md`, `docs/request.md`, `docs/prefly.md`, `docs/errorhandler.md`, `docs/log.md`, `docs/middleware.md`, `docs/security.md`, `docs/database.md`, `docs/migrations.md`

---

## Config Loading

```php
use Engine\Atomic\Core\Config\ConfigLoader;
use Engine\Atomic\Core\Config\PhpConfigLoader;

// Environment-file mode (.env)
$f3 = \Base::instance();
ConfigLoader::init($f3, realpath(__DIR__ . '/../.env'));

// PHP config files mode
(new PhpConfigLoader($f3))->load();
```

Config values land in the F3 hive and are read by all subsystems via `$f3->get('DB_CONFIG.host')`, `$f3->get('REDIS')`, etc.

## App Bootstrap

```php
use Engine\Atomic\Core\App;

$app = App::instance($f3);
$app->prefly()
    ->register_logger()
    ->register_exception_handler()
    ->register_locales()
    ->register_middleware()
    ->register_routes()
    ->register_core_plugins()
    ->register_plugins()
    ->init_session()
    ->open_connections()
    ->register_user_provider();

$f3->run();
```

## Routing

```php
$app->route('GET /dashboard', 'App\\Http\\Controllers\\Dashboard->index', ['auth']);
$app->route('GET /posts/@id', 'App\\Http\\Controllers\\Posts->show', 60); // TTL
$app->route('GET /admin', 'App\\Http\\Admin->index', ['auth', 'role:admin']);
```

## Middleware

```php
// app/Http/Middleware/RequireAuth.php
use Engine\Atomic\Core\Middleware\MiddlewareInterface;

final class RequireAuth implements MiddlewareInterface
{
    public function handle(\Base $atomic): bool
    {
        if (!is_authenticated()) {
            $atomic->reroute('/login');
            return false; // stops controller
        }
        return true;
    }
}
```

```php
// config/middleware.php
return [
    'auth'     => App\Http\Middleware\RequireAuth::class,
    'role'     => App\Http\Middleware\RequireRole::class,
];
```

## Logging

```php
use Engine\Atomic\Core\Log;
use Engine\Atomic\Enums\LogChannel;
use Engine\Atomic\Enums\LogLevel;

// Default channel (atomic.log)
Log::error('Payment failed for order #' . $id);
Log::warning('Rate limit exceeded');
Log::info('User logged in');
Log::debug('Query params: ' . json_encode($params));

// Named channel
Log::channel('auth')->warning('Failed login attempt');
Log::channel('auth')->info('User authenticated');
Log::channel(LogChannel::QUEUE_WORKER)->error('Job failed');

// JSON dumps (only in DEBUG_MODE)
Log::dump('cart_data', ['items' => $items]);  // saved to DUMPS dir
Log::dump_hive();                              // snapshot entire F3 hive

// Custom channel registration (in bootstrap/plugins)
Log::add_channel('payments', storage_path('logs/payments.log'), LogLevel::INFO);
Log::channel('payments')->info('Invoice created');

// Retrieve channel names
$channels = Log::get_channel_names();  // ['atomic', 'error', 'auth', ...]
```

All PSR-3 methods take only `string $msg`. Embed context in the string itself.

Built-in channels: `atomic` (default), `error`, `auth`, `queue_worker`, `queue_monitor`.

## Guard (Authorization)

```php
use Engine\Atomic\Core\Guard;
use Engine\Atomic\Enums\Role;

if (!Guard::is_authenticated()) {
    \Base::instance()->reroute('/login');
}

if (!Guard::has_role(Role::ADMIN)) {
    \Base::instance()->error(403, 'Forbidden');
}

// All Guard methods:
Guard::is_authenticated();                              // bool
Guard::is_guest();                                      // bool
Guard::has_role(Role::ADMIN);                           // bool
Guard::has_role('admin');                               // accepts string or BackedEnum
Guard::has_any_role([Role::ADMIN, Role::SELLER]);        // bool
Guard::lacks_role(Role::SELLER);                        // bool (!has_role)
Guard::lacks_any_role([Role::SELLER, Role::BUYER]);      // bool
```

Note: `has_role()` requires the user to implement `HasRolesInterface`. When no user is authenticated, all `has_*` / `lacks_*` return appropriate defaults.

## Crypto (sodium_crypto_secretbox)

```php
use Engine\Atomic\Core\Crypto;

// APP_ENCRYPTION_KEY must be set in config
$crypto = new Crypto();
$cipher = $crypto->encrypt('sensitive payload');
$plain  = $crypto->decrypt((string)$cipher);

// Key generation
$key = Crypto::generate_key();
```

Returns `false` on empty input, invalid base64, or tampered ciphertext.

## DB Connections

```php
use Engine\Atomic\Core\ConnectionManager;

$cm = ConnectionManager::instance();
$db = $cm->get_db();               // MySQL via Cortex
$redis = $cm->get_redis(false);    // false = optional
$memcached = $cm->get_memcached(false);

$cm->open_all();
$cm->close();  // release all
```

## Migrations

```bash
php atomic migrations/init
php atomic migrations/create create_users_table
php atomic migrations/migrate
php atomic migrations/rollback
php atomic migrations/rollback 3
php atomic migrations/status
php atomic migrations/publish <plugin-name>
```

```php
// Migration file shape
return [
    'up' => function () {
        $db = ConnectionManager::instance()->get_db();
        $schema = new \DB\Cortex\Schema\Schema($db);
        // e.g. $schema->createTable('posts', [...])
    },
    'down' => function () {
        // rollback DDL
    },
];
```

## Request Helpers (Methods + helpers.php)

```php
is_home();                      // current path is /
is_page('/account');            // exact or wildcard
is_page(['/account', '/account/*']);
is_section('blog');             // /blog and /blog/*
is_ssl(); is_ajax(); is_mobile(); is_404(); is_telegram();
is_botblocker(); is_gs();
current_path();                 // path without locale prefix
url_segments();                 // ['seller', 'page']
get_segment(0);                 // 'seller'
get_year();                     // '2025'
get_copyright_years(2020);      // '2020 - 2025'
get_date('d.m.Y');              // '28.04.2025'
get_copy();                     // '©'
get_encoding();                 // charset string (e.g. 'UTF-8')
get_error_trace();              // formatted error trace for current request

// Error handling
format_error_trace($code, $text, $trace);  // format_error_trace(int, string, string): string
```

### Methods Class (low-level request context)

`Engine\Atomic\Core\Methods` (aliased `AM`) provides additional request context not exposed as global helpers:

```php
use Engine\Atomic\Core\Methods;

$am = Methods::instance();

$am->get_public_url();              // app domain, e.g. 'https://example.com'
$am->get_current_url();             // full current URL (REALM)
$am->get_current_route();           // matched route pattern (PATTERN)
$am->get_current_method();          // HTTP verb: 'GET', 'POST', ...
$am->get_user_ip();                 // client IP address
$am->get_user_agent();              // User-Agent string
$am->get_user_language();           // Accept-Language value
$am->get_is_debug();                // bool (DEBUG_MODE)
$am->get_user_device(true);         // device type string (true = high accuracy)
$am->list_routes();                 // array of all registered routes
$am->get_public_dir();              // filesystem path to public/uploads
```

## Upload

`Engine\Atomic\Core\Upload` -- file upload and access token management. Paths follow `public/uploads/{user_id}/{user_uuid}/{project_uuid}/` structure.

```php
use Engine\Atomic\Core\Upload;

$up = Upload::instance();

// Upload a user file (expects $_FILES['file'] entry)
$result = $up->upload_user_file($userId, $userUuid, $projectId, $projectUuid, $_FILES['file']);
// Returns: ['ok'=>bool, 'filename'=>string, 'url'=>string, 'path'=>string, ...]

// File info
$info = $up->get_file_info($userId, $userUuid, $projectId, $projectUuid, 'photo.jpg');
$info = $up->get_file_info($userId, $userUuid, $projectId, $projectUuid, 'photo.jpg', 'optimized');

// Delete
$up->delete_file($userId, $userUuid, $projectId, $projectUuid, 'photo.jpg');  // bool
$up->delete_project_files($userId, $userUuid, $projectId, $projectUuid);      // bool
$up->delete_user_files($userId, $userUuid);                                   // bool

// Download from URL
$result = $up->download_user_image($userId, $userUuid, $projectId, $projectUuid, $url, 'image.jpg');
$result = $up->download_system_file('filename.jpg');

// Paths
$up->get_upload_path();          // public/uploads/
$up->get_user_upload_path();     // public/uploads/{user_uuid}/
$up->get_system_upload_path();   // storage/app/public/

// Access tokens (for protected file routes)
$token = $up->generate_access_token($id, $uuid, $length);
$valid = $up->verify_access_token($token, $uuid);           // bool
$up->store_access_token($uuid, $filename, $token);
$up->get_stored_access_token($uuid, $filename);             // string|false
$up->create_and_store_access_token($id, $uuid, $filename);  // string
$up->get_or_create_user_token($userId, $userUuid);          // persistent user token
$up->get_or_create_project_token($projectId, $projectUuid); // persistent project token
```

## HTTP Client Helpers

```php
$res = remote_get('https://api.example.com/users', [
    'query'   => ['page' => 1],
    'headers' => ['Authorization' => 'Bearer '.$token],
    'timeout' => 5,
    'retries' => 2,
]);
if ($res['ok']) {
    $data = json_decode($res['body'], true);
}

// POST JSON
$res = remote_post('https://api.example.com/posts', json_encode($payload), [
    'headers' => ['Content-Type' => 'application/json'],
    'raw'     => true,
]);

// PUT, HEAD
$res = remote_put('https://api.example.com/posts/1', json_encode($payload));
$res = remote_head('https://example.com/file.pdf');
```

Return shape: `['ok'=>bool, 'status'=>int, 'headers'=>array, 'body'=>string, 'error'=>string, 'cached'=>bool, 'url'=>string]`

## Response Helpers

```php
// Global helpers (from helpers.php)
send_json(['user' => $user]);                           // 200
send_json(['user' => $user], 201);
send_json_error('Unauthorized', 401);
send_json_error('Validation failed', 422, ['field' => 'email']);
send_json_success(['id' => $id]);                       // {"success":true,"id":...}
send_json_success([], 201);

// Pass terminate=false to not call exit
send_json($data, 200, false);

// Low-level
json_response($data, 200);
$str = atomic_json_encode($data);  // UTF-8, unescaped slashes/unicode

// Via class
use Engine\Atomic\Core\Response;
Response::instance()->send_json($data, 200);
```

## ID

`Engine\Atomic\Core\ID` -- UUID and token utilities.

```php
use Engine\Atomic\Core\ID;

// UUID v4
$uuid = ID::uuid_v4();                          // e.g. '550e8400-...'
$ok   = ID::is_valid_uuid_v4($uuid);            // bool
$bin  = ID::uuid_v4_to_bytes($uuid);            // binary string (16 bytes)
$b64  = ID::uuid_v4_to_bytes_json($uuid);       // base64 of binary
$uuid = ID::bytes_to_uuid_v4($bin);
$uuid = ID::bytes_to_uuid_v4_json($b64);

// Random IDs
$hex = ID::generate_unique_id(16);              // 32 hex chars
$b64 = ID::generate_unique_id_json(16);         // base64

// HMAC access tokens (requires APP_KEY)
$token = ID::generate_access_token($userId, $uuid, 12);
$valid = ID::verify_access_token($token, $uuid);  // bool
$id    = ID::extract_id_from_token($token);      // string|null

// URL-safe base64
$enc = ID::base64_url_encode($data);
$dec = ID::base64_url_decode($enc);
```

## Filesystem

`Engine\Atomic\Core\Filesystem` -- file and directory operations.

```php
use Engine\Atomic\Core\Filesystem;

$fs = Filesystem::instance();

// Files
$fs->copy($src, $dst);              // bool
$fs->move($src, $dst);              // bool
$fs->delete('/path/to/file.txt');   // bool
$fs->read('/path/to/file.txt');     // string|false
$fs->write('/path/to/file.txt', $data, append: false);  // int|false
$fs->exists('/path');
$fs->is_file('/path/to/file');
$fs->rename('/old', '/new');        // bool
$fs->filesize('/file');
$fs->created_time('/file');         // int (unix)
$fs->modified_time('/file');
$fs->count_lines('/file');          // int|false

// Read from end (for log pagination)
$lines = $fs->read_lines_from_end('/path/app.log', $offset, $limit);

// Directories
$fs->make_dir('/path', 0755, recursive: true);
$fs->remove_dir('/path', recursive: true);
$fs->copy_dir('/src', '/dst');      // bool
$files = $fs->list_files('/dir/', levels: 100, exclusions: ['.git']);
$tmp = $fs->get_temp_dir();         // TEMP hive key value

// Archives
$fs->unzip_file('/archive.zip', '/extract/to');         // bool
$fs->zip_files(['/a.txt', '/b.txt'], '/archive.zip');   // bool
```

## Seeder

`Engine\Atomic\Core\Seeder` -- run seed files.

```php
use Engine\Atomic\Core\Seeder;

Seeder::run('/path/to/seeds/seed_posts.php');
```

Seed file shape:
```php
// database/seeds/seed_posts.php
return [
    'run' => function () {
        $post = new \App\Models\Post();
        $post->title = 'Sample post';
        $post->save();
    },
];
```

## Prefly Checks

`App::prefly()` validates PHP ≥ 8.1, required extensions (json, session, mbstring, fileinfo, pdo, pdo_mysql, curl), and that `storage/` + `storage/logs/` are writable. On failure: CLI exits 1, web returns HTTP 500/503.

## Error Handling

`ExceptionHandlerRegistrar::register($atomic)` sets `ONERROR` in the F3 hive.

Behavior: reads `ERROR.*` hive keys → formats trace → dumps hive (debug only) → responds:
- API/AJAX (`/api/*`, `AJAX` truthy, or `Accept: application/json`): JSON `{"error": {...}}`
- Web: renders `ErrorPages` theme layout (e.g. `layout/404.atom.php`)
- CLI: writes structured error to stderr

Trigger manually: `\Base::instance()->error(404, 'Not found')`

## Error Pages

`Engine\Atomic\App\Error` -- controller that renders themed error pages. Registered in `routes/web.error.php`.

Handled HTTP status codes: **400, 401, 403, 404, 405, 408, 429, 500, 502, 503**

Each method sets `PAGE.title`, `PAGE.color`, and renders the corresponding template from the `ErrorPages` theme:

```
resources/views/layout/400.atom.php
resources/views/layout/404.atom.php
... (same pattern for each code)
resources/views/layout/500.atom.php  // also sets ERROR.formatted_trace
```

To trigger programmatically:
```php
\Base::instance()->error(404, 'Post not found');
\Base::instance()->error(403, 'Forbidden');
```

## Redactor

`Engine\Atomic\Core\Redactor` -- sanitizes sensitive data before logging or display. Used automatically by the telemetry panel.

```php
use Engine\Atomic\Core\Redactor;

// Strip home path from all strings (auto-called with hive in telemetry)
Redactor::set_home_path('/var/www/myapp');
Redactor::init_from_hive(\Base::instance());  // reads HOME or ROOT from hive

// Sanitize any value (replaces passwords, keys, tokens with [MASKED])
$safe = Redactor::redact($anyValue);          // works on strings, arrays, objects

// Sanitize a single string
$safe = Redactor::redact_string($sensitiveString);
```

`Redactor::MASKED` constant: `'[MASKED]'`

## Guardrails
- Core changes are wide-impact. Keep them minimal and well-tested.
- Never bypass middleware or route loader.
- Always verify that `APP_ENCRYPTION_KEY` is properly set before using `Crypto`.
- Keep sensitive values out of logs - the Redactor sanitizes diagnostic output but not application log calls.
