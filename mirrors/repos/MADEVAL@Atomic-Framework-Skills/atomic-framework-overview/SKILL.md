---
name: atomic-framework-overview
description: "Use when you need a high-level map of Atomic Framework, its Fat-Free Framework foundation, startup flow, module boundaries, boot sequence, routing conventions, and correct entry points before editing any engine or app code."
argument-hint: "Architecture, boot flow, module navigation, routing, hive"
user-invocable: true
---

# Atomic Framework Overview

## When to Use
- Starting work in any part of the framework for the first time.
- Tracing the bootstrap chain before editing engine code.
- Choosing which module owns a behavior.
- Understanding how Atomic wraps Fat-Free Framework (F3).

## Foundation
Atomic is a **modular PHP 8.1+ framework** built on top of **Fat-Free Framework** (`bcosca/fatfree-core ^3.9.1`).

- F3 owns: router, **hive** (global key-value store `$f3->get/set`), template engine, Cortex ORM.
- Atomic adds: config loading, middleware, plugin management, auth, queue, scheduler, telemetry, theme, and DX tooling on top of F3.
- Runtime state (config, session, DB connections, locale) lives in the F3 hive. Modules communicate through hive keys, not direct coupling.

## Bootstrap Chain

```
engine/index.php
  └─ bootstrap/app.php
       1. bootstrap/const.php  ← ATOMIC_LOADER, ATOMIC_DIR, ATOMIC_ENV, etc.
       2. ConfigLoader::init($f3, .env)  OR  (new PhpConfigLoader($f3))->load()
       3. App::instance($f3)
            ├─ prefly()                  ← PHP/extension checks, storage writability
            ├─ register_logger()
            ├─ register_exception_handler()
            ├─ register_locales()
            ├─ register_middleware()
            ├─ register_routes()
            ├─ register_core_plugins()
            ├─ register_plugins()
            ├─ init_session()
            ├─ open_connections()
            └─ register_user_provider()
       4. App\Event\Application::instance()->init()
       5. App\Hook\Application::instance()->init()
       6. $f3->run()
```

For CLI:
```bash
php atomic <command>   # e.g. php atomic schedule/run
# internally: App::instance()->handle_command($argv)
# normalizes "schedule:run" → "/schedule/run" then calls run()
```

## Module Map

```
engine/Atomic/
├── Core/         ← bootstrap, config, request/response, routing, middleware, crypto, log, guard
├── App/          ← Controller, Model, Page, Storage, PluginManager
├── Auth/         ← login flows, Google/Telegram OAuth, adapters, services
├── Session/      ← SessionManager, SQL + Redis session drivers
├── Queue/        ← job queue, workers, DB/Redis drivers, monitor, applications
├── Scheduler/    ← cron-style task scheduler + Mutex overlap protection
├── Telemetry/    ← diagnostics panel served at /telemetry
├── Theme/        ← Theme boot, Head, Assets, OpenGraph, Schema
├── Hook/         ← WordPress-style add_action/add_filter/do_action/apply_filters
├── Event/        ← dot-notation typed event bus (Event::instance()->on/emit)
├── Lang/         ← i18n, locale files, lang_url(), get_locale()
├── Mail/         ← SMTP wrapper: mail_to()->set_html()->send()
├── Mutex/        ← distributed locking: Mutex::acquire/release/synchronized
├── Plugins/      ← built-in integrations: Monopay, WordPress, WooCommerce, RSS...
├── Files/        ← PDF, XLS, CSV export
├── Cache/        ← DB and Memcached cache drivers
├── Tools/        ← Nonce, Transient, Telegram, AIConnector
├── Validator/    ← model-level validation via Validator + ValidatorModelTrait
├── WebSockets/   ← Workerman-based WebSocket server base class
├── Exceptions/   ← typed exception hierarchy (AtomicException, ...)
├── Enums/        ← PHP 8.1 backed enums: Role, Rule, Currency, Language, LogLevel
├── CLI/          ← console command layer: php atomic <cmd>
├── API/          ← API entrypoint wrapper
├── Codes/        ← Code constants
└── Support/      ← global helper functions (helpers.php)
```

## Routing Quick Reference

```php
// Basic
$app->route('GET /users', 'App\\Http\\Controllers\\Users->index');

// With middleware (array = MiddlewareStack; disables F3 route caching)
$app->route('GET /dashboard', 'App\\Http\\Controllers\\Dashboard->index', ['auth']);

// With TTL cache (seconds; no middleware)
$app->route('GET /posts/@id', 'App\\Http\\Controllers\\Posts->show', 60);

// Parameterized middleware
$app->route('GET /admin', 'App\\Http\\Controllers\\Admin->index', ['auth', 'role:admin']);
```

Route dispatch by request type:
| Path prefix | Route file loaded |
|---|---|
| CLI (`php atomic`) | `routes/cli.php` |
| `/api/*` | `routes/api.php` |
| `/telemetry/*` | `engine/.../Routes/telemetry.php` |
| everything else | `routes/web.php` |

Route files: `routes/web.php`, `routes/api.php`, `routes/cli.php`, `routes/schedule.php`.

## Key Skills to Load Next
| Task | Load skill |
|---|---|
| Config, request, middleware, logging | `atomic-framework-core` |
| Controllers, models, storage | `atomic-framework-app-auth` |
| Auth, session, OAuth | `atomic-framework-app-auth` |
| Queue, scheduler, telemetry | `atomic-framework-queue-scheduler-telemetry` |
| Theme, head, assets, OpenGraph | `atomic-framework-theme` |
| Hooks, events, mail, i18n | `atomic-framework-event-hook-lang-mail` |
| Mutex, session state, nonce, transient | `atomic-framework-mutex-session` |
| Plugins, integrations | `atomic-framework-plugins` |
| CLI commands, API | `atomic-framework-cli-api` |
| PDF/XLS, validation, cache, exceptions | `atomic-framework-data` |
| AI connector, WebSockets, tools | `atomic-framework-tools-websockets` |

## Guardrails
- Modules communicate through the F3 hive, not direct cross-module coupling.
- Always identify the owning module first. Never add a feature to the wrong module.
- Do not bypass `App::register_*()` lifecycle methods - they exist to wire the correct dependencies in order.
- Load the matching subsystem skill before making non-trivial changes.
