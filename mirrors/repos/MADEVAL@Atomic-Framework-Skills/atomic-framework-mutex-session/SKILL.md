---
name: atomic-framework-mutex-session
description: "Use when working on Atomic mutex (distributed locking), session lifecycle, session storage drivers, nonces (one-time tokens), or transient cached values."
argument-hint: "Mutex, distributed lock, session, nonce, transient, cache, Redis, database"
user-invocable: true
---

# Atomic Framework Mutex and Session

## When to Use
- Preventing concurrent execution of scheduled tasks or critical sections.
- Working with session storage, session inspection, or session cleanup.
- Creating or verifying nonce tokens for form/CSRF protection.
- Caching values temporarily with a TTL (transients).

## Engine Files
`engine/Atomic/Mutex/*`, `engine/Atomic/Session/*`, `engine/Atomic/Tools/Nonce.php`, `engine/Atomic/Tools/Transient.php`

## Reference Docs
`docs/mutex.md`, `docs/session.md`, `docs/nonce.md`, `docs/transient.md`, `docs/security.md`

---

## Mutex - Distributed Locking

`Engine\Atomic\Mutex\Mutex` - acquire/release pattern.

```php
use Engine\Atomic\Mutex\Mutex;

// Manual acquire/release
$token = Mutex::acquire('send-newsletter', 300); // 300s TTL

if ($token === null) {
    // Another process holds the lock - skip
    return;
}

try {
    // critical section
} finally {
    Mutex::release('send-newsletter', $token);
}

// Convenience wrapper
$result = Mutex::synchronized('send-newsletter', 300, function () {
    // runs only if lock acquired
    return 'done';
}, function () {
    // called if lock was already held
    return 'skipped';
});
```

### Additional Methods

```php
Mutex::exists('send-newsletter');       // bool
Mutex::force_release('send-newsletter'); // admin/cleanup only
Mutex::get_driver_name();               // 'redis' | 'database' | 'file' | null
Mutex::info();                          // ['driver'=>..., 'initialized'=>bool, 'available'=>bool]
Mutex::reset();                         // for tests
```

### Lock Name Rules
Must match `/^[A-Za-z0-9:._-]{1,128}$/`.

### Drivers (auto-selected by priority)

| Driver | Config | Notes |
|---|---|---|
| `redis` | `REDIS.*` | `SET NX EX` + Lua release. Best for distributed. |
| `memcached` | `MEMCACHED.*` | `add()` atomic; release best-effort. |
| `database` | `DB_CONFIG.*` | `mutex_locks` table. Run `php atomic db/mutex` to inspect. |
| `file` | `MUTEX_DRIVER=file` | Local file locks. Single-server only. |

```php
// Force a specific driver in config/bootstrap
$atomic->set('MUTEX', ['driver' => 'redis']);
// or env: MUTEX_DRIVER=redis
```

### Scheduler Integration

`without_overlapping()` in the scheduler uses `Mutex::acquire()` automatically:

```php
$scheduler->call('App\\Tasks\\Report->run')
    ->daily_at('02:00')
    ->without_overlapping(300);
```

---

## Session

Session facade: `Engine\Atomic\Auth\Session`

```php
use Engine\Atomic\Auth\Session;

Session::init();
Session::start();
Session::start('uuid-session-id');  // resume by ID

Session::is_started();  // bool
Session::is_expired();  // bool
Session::destroy();
```

Userland session data via F3 hive:

```php
$f3 = \Base::instance();
$f3->set('SESSION.user_uuid', '550e8400-...');
$uuid = $f3->get('SESSION.user_uuid');
$f3->clear('SESSION.user_uuid');
```

### Session Manager (storage inspection)

```php
use Engine\Atomic\Session\SessionManager;

$m = new SessionManager();            // auto driver
$m = new SessionManager('redis');     // force Redis
$m = new SessionManager('database');  // force SQL

$m->session_exists($id);              // bool
$data = $m->get_session_data($id);    // array|null
$m->delete_session($id);
$m->delete_sessions([$id1, $id2]);    // int (count deleted)
$m->get_driver();                     // 'redis' | 'database'
```

SQL session data shape:
```php
['session_id'=>..., 'data'=>..., 'ip'=>..., 'agent'=>..., 'stamp'=>int]
```

---

## Nonce - One-Time CSRF Tokens

`Engine\Atomic\Tools\Nonce` - bound to current IP + User-Agent.

```php
// Helpers (from Support/helpers.php)
$token = create_nonce('delete-post', 1800);  // 1800s TTL

if (!verify_nonce($_POST['nonce'] ?? '', 'delete-post')) {
    send_json_error('Invalid nonce', 403);
}

// Class usage
use Engine\Atomic\Tools\Nonce;

$nonce = Nonce::instance();
$token = $nonce->create_nonce('api-action', 3600);
$valid = $nonce->verify_nonce($token, 'api-action');
```

Behavior:
- 32-char hex token stored in hive with TTL.
- Verification is **destructive**: token is consumed after one check.
- Different IP or user agent makes verification fail.

---

## Transients - Temporary Cached Values

`Engine\Atomic\Tools\Transient` - backed by Redis, Memcached, or DB.

```php
// Helpers
set_transient('api_results', $data, 3600);

$data = get_transient('api_results');
if ($data === false || $data === null) {
    $data = fetch_remote_data();
    set_transient('api_results', $data, 3600);
}

delete_transient('api_results');
delete_all_transients();         // clears all drivers

// Explicit driver
set_transient('stats', $stats, 300, 'redis');
$stats = get_transient('stats', 'redis');
delete_transient('stats', 'redis');

// Class usage
use Engine\Atomic\Tools\Transient;

Transient::set('featured_posts', $posts, 600);
$posts = Transient::get('featured_posts');
Transient::delete('featured_posts');
```

Important: TTL must be `> 0` or `InvalidArgumentException` is thrown. When no driver is specified, `CacheManager::cascade()` auto-selects.

## Guardrails
- Always wrap the critical section in `try/finally` when using manual `acquire/release`.
- Nonce tokens are single-use; do not re-verify or cache them.
- Transient TTL of `0` is invalid - always pass a positive integer.
- Mutex lock names must be unique per logical operation, not per request.
