---
name: atomic-framework-plugins
description: "Use when working on Atomic plugin architecture: the Plugin base class, PluginManager bootstrap, plugin routes, plugin helpers, user plugins, and built-in integrations (Monopay, WordPress, WooCommerce, RSS Reader)."
argument-hint: "Plugin register, boot, activate, PluginManager, plugin helpers, Monopay, WordPress plugin"
user-invocable: true
---

# Atomic Framework Plugins

## When to Use
- Creating or editing a plugin (register, boot, activate, deactivate lifecycle).
- Adding routes or migrations scoped to a plugin.
- Using plugin helpers (`plugin_manager`, `get_plugin`, `has_plugin`, etc.).
- Working on built-in integrations: Monopay, WordPress, WooCommerce, RSS Reader.

## Engine Files
`engine/Atomic/App/Plugin.php`, `engine/Atomic/App/PluginManager.php`, `engine/Atomic/Plugins/*`

## Reference Docs
`docs/plugins.md`, `docs/plugins/monopay.md`, `docs/plugins/wordpress.md`, `docs/plugins/woocommerce.md`, `docs/plugins/rss-reader.md`

---

## Plugin Abstract Class

All plugins extend `Engine\Atomic\App\Plugin`.

```php
namespace App\Plugins\Newsletter;

use Engine\Atomic\App\Plugin;

final class NewsletterPlugin extends Plugin
{
    public function get_name(): string
    {
        return 'Newsletter';
    }

    // Called once on first activation
    public function activate(): void
    {
        // run migrations, seed data
    }

    // Called on deactivation
    public function deactivate(): void
    {
        // cleanup
    }

    // Called on every bootstrap (register services, bindings)
    public function register(): void
    {
        add_filter('the_footer', [$this, 'add_signup_form']);
    }

    // Called after all plugins are registered
    public function boot(): void
    {
        // attach routes, enqueue assets
    }

    public function get_migrations_path(): string
    {
        return __DIR__ . '/Migrations';
    }
}
```

## PluginManager Bootstrap Order

```
1. App::register_core_plugins()
       reads config/providers.php['plugins']
       instantiates each plugin class

2. App::register_plugins()
       PluginManager::load_user_plugins()  <- scans USER_PLUGINS dir for plugin.php
       PluginManager::register_all()       <- calls ->register() on all
       PluginManager::boot_all()           <- calls ->boot() on all

3. After boot_all(): each plugin's routes/ dir is scanned and loaded
```

## Registering Core Plugins

```php
// config/providers.php
return [
    'plugins' => [
        App\Plugins\Newsletter\NewsletterPlugin::class,
    ],
];
```

## User Plugins (External)

```
USER_PLUGINS/
  my-plugin/
    plugin.php          <- must instantiate the plugin class
    routes/web.php
    Migrations/install_my_plugin.php
```

## Plugin Helpers

```php
$pm = plugin_manager();                // PluginManager instance
$p  = get_plugin('Newsletter');        // plugin instance or null
$ok = has_plugin('Newsletter');        // bool
enable_plugin('Newsletter');
disable_plugin('Newsletter');
```

## Plugin Migrations

```bash
php atomic migrations/publish newsletter  # copy plugin migrations
php atomic migrations/migrate
```

## Plugin Dependencies

Plugins can declare load-order dependencies. `PluginManager` boots dependencies before the declaring plugin:

```php
final class GoogleAnalytics extends Plugin
{
    protected array $dependencies = ['Google'];  // Google boots first

    public function get_name(): string { return 'GoogleAnalytics'; }
    // ...
}
```

## Built-in Integrations

### Monopay
`engine/Atomic/Plugins/Monopay/`

```php
use Engine\Atomic\Plugins\Monopay\Api;

$api = new Api($token, $baseUrl);

$api->create_invoice($data);                        // array
$api->get_invoice_status($invoiceId);               // array
$api->cancel_invoice($invoiceId, $options);         // array
$api->remove_invoice($invoiceId);                   // array
$api->finalize_hold($invoiceId, $amount, $items);   // array (hold finalization)
$api->get_public_key();                             // array
$api->verify_signature($publicKey, $xSign, $body);  // bool
```

| File | Purpose |
|---|---|
| `Api.php` | Monopay API client |
| `Order.php` | Order model |
| `WebhookHandler.php` | Webhook verification and dispatch |
| `Models/Payment.php`, `Models/PaymentHistory.php` | DB models |
| `Migrations/` | DB schema |
| `routes/cli.php` | CLI commands |
| `Enums/PaymentStatus.php`, `Enums/MonopayHook.php` | Status and hook enums |

### WordPress
`engine/Atomic/Plugins/WordPress.php`

```php
use Engine\Atomic\Plugins\WordPress;

// Retrieve via PluginManager
$wp = get_plugin('WordPress');  // WordPress plugin instance

$wp->connect('https://mysite.com', $apiKey, $apiSecret);  // chain
$posts      = $wp->get_posts(1, 100, ['status' => 'publish']);  // array
$post       = $wp->get_post($id);
$all        = $wp->get_all_posts(['status' => 'publish']);       // iterates pages
$categories = $wp->get_categories();
$tags       = $wp->get_tags();
$media      = $wp->get_media();
```

### WooCommerce
`engine/Atomic/Plugins/WooCommerce.php`

```php
$wc = get_plugin('WooCommerce');

$wc->connect('https://mysite.com', $key, $secret);
$products    = $wc->get_products(1, 100);
$product     = $wc->get_product($id);
$all         = $wc->get_all_products();
$categories  = $wc->get_categories();
$all_cats    = $wc->get_all_categories();
$parsed      = $wc->parse_product($raw);         // normalize raw WC product

// Orders
$order   = $wc->create_order($orderData);
$updated = $wc->update_order($orderId, $data);
$order   = $wc->get_order($orderId);
$wc->update_order_status($orderId, 'completed');
$wc->apply_coupon($orderId, 'SUMMER20');
```

### RSS Reader
`engine/Atomic/Plugins/RssReader.php`

```php
$rss = get_plugin('RssReader');

// Named feed registry
$rss->add_feed('tech', 'https://example.com/feed.xml');
$items = $rss->read_feed('tech', 10, ['title', 'link']);  // ?count, ?tags

// One-off read by URL
$items = $rss->read('https://example.com/feed.xml', 5);
// Each item: ['title', 'link', 'description', 'pubDate', ...]
```

### GlobusStudio
`engine/Atomic/Plugins/GlobusStudio.php`

```php
$gs = get_plugin('GlobusStudio');

// Currency rates (from GlobusStudio API)
$rates  = $gs->get_currencies('USD');               // base currency
$rate   = $gs->find_rate('USD', 'UAH', $rates);     // ?float
$result = $gs->convert_amount(100.0, 'USD', 'UAH', $rates);  // array

// QR code generation
$qr = $gs->get_qr('https://example.com', 'png', 5); // array

// Global helpers (when plugin is active)
$rates  = gs_get_currencies('USD');
$rate   = gs_find_rate('USD', 'UAH', $rates);
$result = gs_convert_amount(100.0, 'USD', 'UAH');
$qr     = gs_get_qr('https://example.com', 'png', 5);
```

### Google / GoogleAnalytics
`engine/Atomic/Plugins/Google.php`, `engine/Atomic/Plugins/GoogleAnalytics.php`

```php
// GoogleAnalytics depends on Google (boots first via $dependencies)
final class GoogleAnalytics extends Plugin
{
    protected array $dependencies = ['Google'];
    protected function get_name(): string { return 'GoogleAnalytics'; }
    // register/boot handled internally
}
```

See `docs/plugins/monopay.md`.

### WordPress
`Engine\Atomic\Plugins\WordPress` -- WP REST API client, post/category import. See `docs/plugins/wordpress.md`.

### WooCommerce
`Engine\Atomic\Plugins\WooCommerce` -- order/product sync from WC REST API. See `docs/plugins/woocommerce.md`.

### RSS Reader
`Engine\Atomic\Plugins\RssReader` -- feed fetch, parse, and persist. See `docs/plugins/rss-reader.md`.

### Google
Sets up Google OAuth foundation. Sets `PLUGIN.Google.*` hive keys. Required by `GoogleAnalytics`.

### GoogleAnalytics
Depends on `Google` plugin (`dependencies = ['Google']`). Sets `PLUGIN.GoogleAnalytics.*` hive keys.

### GlobusStudio

Currency rates API.

```php
$gs  = get_plugin('GlobusStudio');
$res = $gs->get_currencies('USD', 'json');
// $res = [
//   'ok'   => true,
//   'data' => [
//     [
//       'currency_code_a' => 'USD',
//       'currency_code_b' => 'UAH',
//       'rate_buy'        => 39.50,
//       'rate_sell'       => 40.10,
//       'rate_cross'      => 0.00,
//     ], ...
//   ],
// ];

has_plugin('GlobusStudio');
```

## Guardrails
- Never call heavy initialization in `register()` -- it runs on every request for all plugins.
- `activate()` and `deactivate()` are one-time operations; guard against running twice.
- Plugin routes are available only after `boot_all()` completes.
- Keep plugins isolated; communicate through hooks or events, not direct coupling.
