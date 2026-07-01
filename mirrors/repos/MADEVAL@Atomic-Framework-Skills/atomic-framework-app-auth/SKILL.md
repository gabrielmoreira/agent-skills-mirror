---
name: atomic-framework-app-auth
description: "Use when working on Atomic App layer (Controller, Model, Page, Storage, PluginManager), Auth flows (Auth, GoogleAuth, TelegramAuth, adapters, services), Session (SessionManager, drivers), and app-level models (Meta, Options, MutexLock)."
argument-hint: "Controllers, models, page, storage, login, OAuth, session, user provider"
user-invocable: true
---

# Atomic Framework App and Auth

## When to Use
- Writing controllers, page controllers, or app models.
- Implementing login, logout, Google OAuth, or Telegram login.
- Checking auth state, roles, or session lifetime.
- Working with app-level storage, system state, or plugin wiring.

## Engine Files
`engine/Atomic/App/*`, `engine/Atomic/Auth/*` (Auth, GoogleAuth, TelegramAuth, Adapters/*, Interfaces/*, Services/*)

## Reference Docs
`docs/applications.md`, `docs/model.md`, `docs/session.md`, `docs/telegram.md`, `docs/security.md`, `docs/transient.md`

---

## Controller

```php
namespace App\Http\Controllers;

use Engine\Atomic\App\Controller;

final class Posts extends Controller
{
    public function index(\Base $f3): void
    {
        $posts = (new \App\Models\Post())->find();
        $f3->set('posts', $posts);
        echo \Template::instance()->render('posts/index.htm');
    }

    public function store(\Base $f3): void
    {
        $post = new \App\Models\Post();
        $post->title = $f3->get('POST.title');

        if (!$post->save()) {
            [$code, $vars] = $post->get_last_err_data();
            send_json_error('Validation failed', 422, ['code' => $code]);
            return;
        }

        send_json(['id' => $post->id]);
    }
}
```

## Page Controller

`Engine\Atomic\App\Page` is used for rendering theme-based pages (head, body, title, meta).

## Model (App\Model)

See `atomic-framework-data` skill for full Model API.

```php
use Engine\Atomic\App\Model;

final class Post extends Model
{
    protected $table = 'posts';
    protected $fieldConf = [
        'title' => ['type' => 'VARCHAR256', 'nullable' => false],
    ];
}
```

## App Models

- `Engine\Atomic\App\Models\Options` -- app-wide key-value store (global config at `APP_UUID` scope)
- `Engine\Atomic\App\Models\Meta` -- per-entity metadata keyed by UUID + key
- `Engine\Atomic\App\Models\MutexLock` -- DB-backed mutex lock records

### Options (global app config)

```php
use Engine\Atomic\App\Models\Options;

Options::set_option('site_name', 'My Store');
Options::set_option('session_ttl', '3600', ttl: 86400); // with TTL (seconds); 0 = no expiry
$name = Options::get_option('site_name');          // mixed|false (returns $default if not found)
$name = Options::get_option('site_name', 'Shop');  // with default
Options::delete_option('site_name');

// has_option: returns [timestamp, ttl] or false; populates $val by reference
$result = Options::has_option('site_name', $val);
if ($result !== false) {
    [$ts, $ttl] = $result;   // $val contains the stored value
}

// Pattern queries (LIKE, e.g. 'cache_%')
$map = Options::get_option_like('cache_%');         // ['cache_posts' => '...', ...]
Options::delete_option_like('temp_%');              // bool

// Global helpers
add_option('site_name', 'My Store');
update_option('site_name', 'New Name');
$name = get_option('site_name', 'Default');
delete_option('site_name');
```

### Meta (per-entity metadata)

```php
use Engine\Atomic\App\Models\Meta;

Meta::set_meta($userUuid, 'profile_pic', '/avatars/1.jpg');
$pic = Meta::get_meta($userUuid, 'profile_pic');
$ok  = Meta::has_meta($userUuid, 'profile_pic');  // bool
Meta::delete_meta($userUuid, 'profile_pic');

// Pattern match (LIKE)
$all = Meta::get_meta_like($userUuid, 'upload_%');   // array|false
Meta::delete_meta_like($userUuid, 'upload_%');       // bool

// Global helpers
add_meta($uuid, 'key', 'value');
update_meta($uuid, 'key', 'value');
$val = get_meta($uuid, 'key');
delete_meta($uuid, 'key');
```

### Storage (abstract base)

`Engine\Atomic\App\Storage` is the base class for `Options` and `Meta`. It provides `_set`, `_get`, `_has`, `_delete`, `_get_like`, `_delete_like` as protected static methods keyed by `uuid + key`. Extend it to build custom per-entity stores.

## Page (CMS Model)

`Engine\Atomic\App\Page` extends `Model` and provides a rich pre-configured field set for CMS-style content:

```php
namespace App\Models;

use Engine\Atomic\App\Page;

final class Article extends Page
{
    protected $table = 'articles';

    // Optionally declare relations
    protected static function category_model(): ?string
    {
        return Category::class;    // auto-adds belongs-to-one 'category'
    }

    protected static function author_model(): ?string
    {
        return \App\Models\User::class;  // auto-adds belongs-to-one 'author'
    }
}
```

Built-in fields (pre-configured, no need to declare):

| Field | Type | Notes |
|---|---|---|
| `route` | VARCHAR256 | custom URL |
| `template` | VARCHAR256 | template file name |
| `title` | VARCHAR256 | required, min 3 chars |
| `slug` | VARCHAR256 | unique, required |
| `subtitle` | VARCHAR256 | optional |
| `excerpt` | TEXT | optional |
| `content` | LONGTEXT | optional |
| `content_type` | VARCHAR128 | default 'page' |
| `category` | INT | FK -- auto-wired from `category_model()` |
| `main_image` | VARCHAR256 | optional |
| `thumbnail` | VARCHAR256 | optional |
| `gallery` | LONGTEXT | JSON array |
| `attributes` | LONGTEXT | JSON |
| `custom_fields` | LONGTEXT | JSON |
| `seo_title` | VARCHAR256 | optional |
| `seo_description` | VARCHAR512 | optional |
| `og_title` | VARCHAR256 | optional |
| `og_description` | VARCHAR512 | optional |
| `og_image` | VARCHAR256 | optional |
| `is_published` | BOOL | default 0 |
| `publish_at` | DATETIME | optional |
| `expires_at` | DATETIME | optional |
| `author` | INT | FK -- auto-wired from `author_model()` |
| `views` | INT | view counter |

## User Role Helpers

```php
// Auth helpers
atomic_get_current_user();              // ?AuthenticatableInterface
is_authenticated();                     // bool
is_guest();                             // bool
has_role(Role::ADMIN);                  // bool
has_role('admin');                      // accepts string or BackedEnum
has_any_role([Role::ADMIN, Role::SELLER]);  // bool (any of)

// Short-hand role checkers (from helpers.php)
is_admin();
is_seller();
is_buyer();
is_support();
// Note: no is_moderator() helper exists; use has_role(Role::MODERATOR) directly

// Impersonation (admin acting as another user)
is_impersonating();    // bool
get_real_admin();      // ?AuthenticatableInterface
```

## Auth Facade

`Engine\Atomic\Auth\Auth` is the main auth entry point.

```php
use Engine\Atomic\Auth\Auth;

$auth = Auth::instance();
$user = $auth->get_current_user();      // ?AuthenticatableInterface
$auth->logout();

// Login by ID (bypass credentials -- for impersonation or trusted flows)
$auth->login_by_id('user-uuid');

// Login with secret key (e.g. API key auth)
$user = $auth->login_with_secret(['email' => 'a@b.com'], $secret);

// Rate limiting (returns false if limit exceeded)
$ok = $auth->check_rate_limit(['email' => 'a@b.com'], 'register');

// Impersonation
$auth->impersonate_user('target-user-uuid');  // bool
$auth->stop_impersonation();                  // bool
$auth->is_impersonating();                    // bool
$auth->get_real_admin();                      // ?AuthenticatableInterface
```

## Session Facade

```php
use Engine\Atomic\Auth\Session;

Session::init();
Session::start();
Session::start('550e8400-e29b-41d4-a716-446655440000'); // resume by ID

if (Session::is_started()) { /* ... */ }
if (Session::is_expired()) { /* ... */ }
Session::destroy();
```

Session data lives in the F3 hive:

```php
$f3 = \Base::instance();
$f3->set('SESSION.user_uuid', '550e...');
$uuid = $f3->get('SESSION.user_uuid');
$f3->clear('SESSION.user_uuid');
```

## Session Manager (Storage Inspection)

```php
use Engine\Atomic\Session\SessionManager;

$manager = new SessionManager();           // auto-selects driver
$redis   = new SessionManager('redis');
$sql     = new SessionManager('database');

$exists = $manager->session_exists($session_id);
$data   = $manager->get_session_data($session_id);
$manager->delete_session($session_id);
$manager->delete_sessions([$id1, $id2]);
```

Drivers: `database` (SQL via `SqlSessionTrait`) or `redis` (via `RedisSessionTrait`).

## Google Auth

`Engine\Atomic\Auth\GoogleAuth` + `GoogleAuthService` + `GoogleClientAdapter`.

```php
use Engine\Atomic\Auth\GoogleAuth;
use Engine\Atomic\Auth\Interfaces\OAuthUserResolverInterface;

$google = GoogleAuth::instance();

if (!$google->is_configured()) {
    throw new \RuntimeException('Google OAuth not configured');
}

// Step 1: redirect to Google
$loginUrl = $google->get_login_url();
\Base::instance()->reroute($loginUrl);

// Step 2: handle callback (routes/web.php)
// $google->set_user_resolver(new MyUserResolver());
$redirectUrl = $google->handle_callback($code, $state);  // ?string
// Returns redirect URL or null on failure
```

Required config keys (in `.env` / `config/auth.php`): `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_CALLBACK_URL`.

## Telegram Auth

`Engine\Atomic\Auth\TelegramAuth` + `TelegramAuthService` + `TelegramClientAdapter`.

```php
use Engine\Atomic\Auth\TelegramAuth;

$tg = TelegramAuth::instance();

if (!$tg->is_configured()) {
    throw new \RuntimeException('Telegram auth not configured');
}

// Render Telegram Login Widget -- get HTML attributes
$attrs = $tg->get_widget_attributes(
    size: 'large',          // 'small', 'medium', 'large'
    request_access: false,  // request write access
    use_avatar: true,
    corner_radius: 12,
);
// $attrs = ['data-telegram-login' => '...', 'data-size' => 'large', ...]

// Verify and handle callback (POST with auth data from widget)
$authData = $_POST; // or from JSON body
$verified = $tg->verify_auth_data($authData); // array|false
if ($verified !== false) {
    $redirectUrl = $tg->handle_callback($verified); // ?string
}

// Meta
$tg->get_bot_username();    // string
$tg->get_callback_url();    // string
```

Required config keys: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CALLBACK_URL`.

## Auth Interfaces

| Interface | Purpose |
|---|---|
| `AuthenticatableInterface` | User model contract |
| `AuthSessionInterface` | Session-based auth contract |
| `HasRolesInterface` | Role-check contract (`Guard::has_role()`) |
| `LoginInterface` | Login action contract |
| `OAuthUserResolverInterface` | OAuth user upsert contract |
| `UserProviderInterface` | Resolve user from session/token |

## Guardrails
- Never store passwords in session or plaintext. Use `BcryptHasherAdapter`.
- Always check `HasRolesInterface` before calling `Guard::has_role()`.
- Use `Session::destroy()` on logout, not raw `session_destroy()`.
- Keep adapters thin; business logic belongs in services.
