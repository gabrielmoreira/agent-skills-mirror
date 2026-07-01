---
name: atomic-framework-theme
description: "Use when working on Atomic themes: Theme boot sequence, partials (head/header/footer/sidebar/section), THEME.* hive keys, theme.json, Assets, Head, OpenGraph, Schema, Redactor, and template rendering."
argument-hint: "Theme, head, header, footer, sidebar, section, theme.json, THEME hive, assets, OpenGraph"
user-invocable: true
---

# Atomic Framework Theme

## When to Use
- Creating or modifying a theme and its layout.
- Rendering theme partials (head, header, footer, sidebar, section) from controllers or hooks.
- Reading or writing theme config from `theme.json`.
- Working with page meta (title, description, OG tags, JSON-LD schema).
- Registering or enqueueing CSS/JS assets.

## Engine Files
`engine/Atomic/Theme/*` (Theme, Head, Assets, AssetManager, OpenGraph, Schema, Redactor)

## Reference Docs
`docs/theme.md`, `docs/head.md`, `docs/assets.md`, `docs/opengraph.md`, `docs/template.md`, `docs/redactor.md`

---

## Theme Boot Sequence

When `App::register_routes()` resolves a non-CLI, non-API request:

1. `Theme::instance('default')` -- reads `THEME.envname` or defaults to `'default'`.
2. Resolves theme directory: `public/themes/{name}/`.
3. Loads `public/themes/{name}/functions.atom.php` if it exists.
4. Reads `public/themes/{name}/theme.json` and maps each key to `THEME.{KEY}` in the hive.
5. Sets built-in hive keys: `THEME._file`, `THEME._dir`, `THEME._url`, `THEME._theme`, `THEME._url_public`.
6. Enqueues `ENQ_UI_FIX` (auto-fix meta viewport, charset) when configured.

```php
use Engine\Atomic\Theme\Theme;

$theme = Theme::instance('shop-theme');

// Force reset (tests or multi-theme per request)
Theme::reset();
```

## THEME Hive Keys

```php
$f3 = \Base::instance();

// Built-in
$f3->get('THEME._dir');        // absolute path to theme dir
$f3->get('THEME._url');        // public URL to theme dir
$f3->get('THEME._theme');      // theme name
$f3->get('THEME._url_public'); // URL to public/uploads/
$f3->get('THEME._file');       // path to functions.atom.php

// Custom from theme.json (example)
$f3->get('THEME.color_primary');  // '#FF0000'
$f3->get('THEME.supports_dark');  // true
```

### theme.json Shape

```json
{
    "color_primary": "#FF0000",
    "supports_dark": true,
    "sidebar": "left"
}
```

All keys become `THEME.<key>` in the hive automatically.

## Rendering Partials

```php
use Engine\Atomic\Theme\Theme;

Theme::get_head();
Theme::get_header();
Theme::get_footer();
Theme::get_sidebar();
Theme::get_section('hero');
Theme::get_section('hero', ['title' => 'Welcome']);

// Global helpers (Support/helpers.php)
get_head(); get_header(); get_footer(); get_sidebar();
get_section('hero'); get_section('hero', $data);

// Include relative to active theme dir
Theme::include('inc/hooks.php');
```

## Theme Directory Layout

```
public/themes/default/
  functions.atom.php
  theme.json
  layout/
    head.atom.php
    header.atom.php
    footer.atom.php
    sidebar.atom.php
    404.atom.php
  sections/hero.atom.php
  pages/home.atom.php
  assets/css/ assets/js/
```

## Head

`Engine\Atomic\Theme\Head` outputs HTML tags. Page metadata is set via the F3 hive **before** rendering:

```php
// Set via F3 hive in controller
$f3 = \Base::instance();
$f3->set('PAGE.title', 'Product Name');      // used by get_title()
$f3->set('APP_NAME', 'My Store');            // appended by get_title()
$f3->set('FAVICON', '/images/favicon.ico');  // used by get_favicon()

// Output helpers (echo HTML tags)
get_favicon();
get_title(' | ');              // <title>Product Name | My Store</title>
get_iconset('/icons');         // apple-touch-icon, favicon-32, etc.
get_manifest();                // <link rel="manifest">
get_canonical_link();          // <link rel="canonical"> (auto from current URL)
get_preconnect('google');      // preset: 'google', 'fonts', 'cloudflare', 'bootstrap'
get_preload_links();
get_analytics('gtag', 'G-XXXXXXX');          // Google Analytics
get_analytics('yandex', '12345678');         // Yandex.Metrika
get_analytics('ga4', 'G-XXXXXXX');           // GA4
get_schema('organization', ['name' => 'My Store', 'url' => 'https://example.com']);

// Add dynamically before render
add_preconnect('https://fonts.googleapis.com', crossorigin: true);
add_preload('/fonts/inter.woff2', 'font', 'font/woff2', crossorigin: true);
```

## Assets

```php
use Engine\Atomic\Theme\Assets;

Assets::enqueue_style('app', '/themes/default/assets/css/app.css');
Assets::enqueue_script('app', '/themes/default/assets/js/app.js', defer: true);
Assets::dequeue_style('unwanted');
```

### Full Asset Pipeline (helpers.php)

```php
// Styles
enqueue_style('app', '/themes/default/css/app.css', [], '1.0.0');
enqueue_style('print', '/css/print.css', [], null, 'print');
dequeue_style('vendor-style');
add_inline_style('app', 'body { margin: 0; }');

// Scripts (in_footer=true by default)
enqueue_script('app', '/themes/default/js/app.js', ['jquery'], '1.0.0');
enqueue_script('gtm',  '/js/gtm.js', [], null, false, ['async' => true]);
set_script_attrs('app', ['defer' => true]);
dequeue_script('vendor-script');
add_inline_script('app', 'console.log("loaded")', 'footer');

// Pass PHP data to JS
localize_script('app', [
    'apiUrl'  => '/api/v1',
    'nonce'   => create_nonce('api'),
], 'AppConfig');
// Result: var AppConfig = {...}; injected before the script tag

// Output in templates
print_styles();           // <link> tags -- call in <head>
print_scripts('header');  // <script> tags before </head>
print_scripts('footer');  // <script> tags before </body>
```

### Preset Assets

```php
enqueue_jquery();       // jQuery from preset CDN
enqueue_bootstrap();    // Bootstrap CSS + JS
enqueue_w3();           // W3.CSS
enqueue_fa();           // Font Awesome
enqueue_modernizr();
enqueue_font('Roboto'); // Google Fonts
```

## OpenGraph

```php
use Engine\Atomic\Theme\OpenGraph;

OpenGraph::instance()
    ->set_title('Product Name')
    ->set_description('Product description')
    ->set_image('https://example.com/img.jpg')
    ->set_type('product');
```

### Helpers (helpers.php)

```php
// Output all <meta property="og:*"> and <meta name="twitter:*"> tags:
get_opengraph([
    'title'       => 'Page Title',
    'description' => 'Description.',
    'image'       => 'https://example.com/og.jpg',
    'url'         => 'https://example.com/page',
    'type'        => 'article',
]);

get_twitter_card([
    'title'       => 'Page Title',
    'description' => 'Description.',
    'image'       => 'https://example.com/card.jpg',
    'card'        => 'summary_large_image',
]);
```

## Theme URL and Color Helpers

```php
get_theme_uri();         // URL to active theme folder
get_theme_dir();         // Filesystem path to active theme
get_public_uri();        // URL to public/uploads
get_public_dir();        // Filesystem path to public/uploads

get_color();             // current theme accent color
set_color('#3B82F6');    // set and persist accent color

get_custom_head();       // renders custom_head partial
```

## JSON-LD Schema

`Engine\Atomic\Theme\Schema` generates structured data from built-in templates.
Use the `get_schema()` helper -- it calls `Schema::instance()->generate()` and outputs a `<script type="application/ld+json">` tag.

```php
// Available types: 'organization', 'product', 'article', 'breadcrumb', 'website'

// Organization
get_schema('organization', [
    'name'             => 'ACME Corp',
    'url'              => 'https://example.com',
    'logo'             => 'https://example.com/logo.png',
    'description'      => 'We sell widgets.',
    'phone'            => '+1-800-WIDGETS',
    'email'            => 'info@example.com',
    'address.street'   => '123 Main St',
    'address.city'     => 'Springfield',
    'address.region'   => 'IL',
    'address.postal'   => '62701',
    'address.country'  => 'US',
]);

// Product
get_schema('product', [
    'name'            => 'Widget Pro',
    'image'           => 'https://example.com/widget.jpg',
    'description'     => 'Best widget.',
    'sku'             => 'WGT-001',
    'brand'           => 'ACME',
    'url'             => 'https://example.com/widget-pro',
    'currency'        => 'USD',
    'price'           => '49.99',
    'availability'    => 'https://schema.org/InStock',
    'priceValidUntil' => '2025-12-31',
]);

// Article
get_schema('article', [
    'title'           => 'How to Build a Widget',
    'image'           => 'https://example.com/article.jpg',
    'published'       => '2025-01-15',
    'modified'        => '2025-04-01',
    'author'          => 'Jane Doe',
    'publisher'       => 'ACME Corp',
    'publisher.logo'  => 'https://example.com/logo.png',
    'description'     => 'A step-by-step guide.',
]);

// Breadcrumb (item list)
get_schema('breadcrumb', [
    ['name' => 'Home', 'url' => 'https://example.com'],
    ['name' => 'Blog', 'url' => 'https://example.com/blog'],
    ['name' => 'Article', 'url' => 'https://example.com/blog/article'],
]);

// Website with SearchAction
get_schema('website');   // auto-fills name and url from APP_NAME / DOMAIN

// Direct class usage (returns array, does not echo)
$data = Schema::instance()->generate('product', [...]);
echo '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_UNICODE) . '</script>';
```

Unfilled template placeholders are removed from output automatically.

## Guardrails
- Always boot the theme before calling `get_head()` or `get_header()`.
- `Theme::include()` expects paths relative to the theme dir, not absolute paths.
- Keep `functions.atom.php` for hook/filter registration only.
- `THEME.*` keys are read-only after boot; do not mutate them at request time.
