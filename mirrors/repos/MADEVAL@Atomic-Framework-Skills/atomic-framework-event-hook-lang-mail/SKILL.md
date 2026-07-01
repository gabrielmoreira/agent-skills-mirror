---
name: atomic-framework-event-hook-lang-mail
description: "Use when working on Atomic events (dot-notation typed event bus), hooks (WordPress-style add_action/add_filter), shortcodes, i18n localization, mail sending (Mailer, Notifier), or text-extensibility features."
argument-hint: "Events, hooks, filters, shortcodes, localization, lang_url, mail_to, notifier"
user-invocable: true
---

# Atomic Framework Event, Hook, Lang, and Mail

## When to Use
- Emitting or listening to application events.
- Registering WordPress-style actions or filters.
- Working with shortcodes.
- Adding translation strings or locale-aware URL generation.
- Sending SMTP emails or push notifications.

## Engine Files
`engine/Atomic/Event/*`, `engine/Atomic/Hook/*`, `engine/Atomic/Lang/*`, `engine/Atomic/Mail/*`

## Reference Docs
`docs/event.md`, `docs/hook.md`, `docs/i18n.md`, `docs/mailer.md`, `docs/notifier.md`, `docs/template.md`

---

## Events (typed dot-notation bus)

`Engine\Atomic\Event\Event` - backed by F3 hive.

```php
use Engine\Atomic\Event\Event;

$events = Event::instance();

// Register listener
$events->on('user.login', function ($user, array &$context, array $event) {
    // $event['name']    = 'user.login'
    // $event['key']     = current segment
    // $event['options'] = options passed at registration
    return $user;
});

// Listener with priority (lower = runs first) and options
$events->on('post.publish', function ($post, array &$context, array $event) {
    return $post;
}, 5, ['source' => 'admin']);

// Emit (stops propagation at first listener returning false)
$user = $events->emit('user.login', $user);

// broadcast() -- like emit() but visits ALL listeners regardless of false returns
$result = $events->broadcast('notification.sent', $payload);

// Stop propagation: return false from a listener (only stops emit, not broadcast)
$events->on('form.validate', function ($data) {
    return empty($data['email']) ? false : $data;
});
```

### Hierarchical Events

```php
// Listeners on 'user' receive all user.* events
$events->on('user', fn ($p) => $p);
$events->on('user.register', fn ($p) => $p);
$events->emit('user.register.success', $payload);  // walks up: user.register.success → user.register → user
```

### Object-Local Events

```php
$watcher = $events->watch($object);
$watcher->on('save', fn ($data) => $data);
$watcher->emit('save', ['id' => 1]);
$events->unwatch($object);
```

### Introspection

```php
$events->has('user.login');               // bool
$events->get_registered_events();         // all
$events->off('user.login');               // remove
```

### App Event Wiring

Application-level events are initialized in `app/Event/Application.php`:

```php
class Application
{
    public function init(): void
    {
        $events = Event::instance();
        $events->on('user.registered', [new UserWelcome(), 'handle']);
    }
}
```

---

## Hooks (WordPress-style actions & filters)

`Engine\Atomic\Hook\Hook` - thin wrapper over the Event bus.

```php
// Actions
// Tags accept string or UnitEnum (backed enum case)
enum HookTag: string { case INIT = 'init'; case USER_REGISTERED = 'user_registered'; }

add_action('init', function () {
    // runs at init hook
});

// UnitEnum tag (type-safe hooks)
add_action(HookTag::USER_REGISTERED, function ($userId, $data) {
    // $data['username']
}, 10, 2);

do_action('init');
do_action(HookTag::USER_REGISTERED, 123, ['username' => 'john']);

has_action('init');                          // bool
remove_action('init');                       // remove ALL callbacks on tag
remove_action('init', $specificCallback);    // remove ONE callback

// Filters
add_filter('the_content', function ($content) {
    return '<div class="wrap">' . $content . '</div>';
});

add_filter('price_label', function ($label, $currency) {
    return $label . ' ' . $currency;
}, 10, 2);

$content = apply_filters('the_content', '<p>Original</p>');
echo apply_filters('price_label', 'Price:', 'USD');

remove_filter('the_content');                // remove ALL
remove_filter('the_content', $myCallback);  // remove ONE
```

Note: pass `null` as callback to `remove_action()` / `remove_filter()` to clear ALL listeners on the tag. Pass a specific callable to remove only that one callback.

### App Hook Wiring

```php
// app/Hook/Application.php
class Application
{
    public function init(): void
    {
        add_filter('the_title', fn ($t) => strtoupper($t));
    }
}
```

### Shortcodes

`Engine\Atomic\Hook\Shortcode` provides a WordPress-style shortcode API. See the full API at the bottom of this skill (`## Shortcodes`).

---

## Localization (i18n)

`Engine\Atomic\Lang\I18n` - locale loading and translation.

```php
// Route with lang prefix
$app->route('GET /@lang/about', 'App\\Http\\Controllers\\Page->about');

// In controller
function about(\Base $f3, array $params): void
{
    $lang = $params['lang'] ?? get_locale();
}
```

### Helpers

```php
get_locale();                  // 'en', 'ru', ...
get_languages();               // ['en', 'uk', 'ru']
lang_url('/', 'uk');           // '/uk/'
lang_url('/login');            // '/en/login' for current locale
hreflang_links('/about');      // <link rel="alternate" hreflang="..."> tags
```

### Translation Functions

```php
// Translate by key (UI locale)
$label = __('btn.submit');                         // 'Submit'
$label = __('welcome', ['name' => 'John']);         // 'Hello, John!'
_e('btn.submit');                                   // echo

// With context
$label = _x('bank', 'financial context');           // disambiguate homonyms

// Plurals
$msg = _n('1 item', '%d items', $count, [$count]);

// Content locale (for bilingual content, set separately from UI locale)
content_locale('uk');          // set content locale
content_locale();              // get current content locale
$label = __c('btn.save');      // translate using content_locale()
_ec('btn.save');                // echo using content_locale()
$label = _xc('bank', 'financial');
$msg   = _nc('1 item', '%d items', $count, [$count]);

// Switch locale
set_locale('uk');
```

### Locale Files

Locales live in `engine/Atomic/Lang/locales/en.php`, `ru.php`, etc. as PHP arrays.

App translations go in the app-level locale directory configured by `LOCALES`.

---

## Mail

`Engine\Atomic\Mail\Mailer` - fluent SMTP wrapper.

```php
// Simple HTML email
mail_to('user@example.com', 'John Doe')
    ->set_html('<h1>Welcome!</h1>')
    ->send('Welcome');

// Text email
mail_to('user@example.com')
    ->set_text('Hello!')
    ->send('Hello');

// Quick send
mail_send('user@example.com', 'Subject', '<h1>Hi</h1>');
mail_send('user@example.com', 'Subject', 'Plain text', false);

// CC/BCC
mail_to('primary@example.com')
    ->add_cc('manager@example.com')
    ->add_bcc('archive@example.com')
    ->send('Report');

// Attachments
mail_to('client@example.com')
    ->attach('/path/to/report.pdf', 'Report.pdf')
    ->send('Documents');

// Custom sender
mail_to('user@example.com')
    ->set_from('noreply@example.com', 'System')
    ->send('Notification');

// Reply-To
mail_to('user@example.com')
    ->set_reply('support@example.com', 'Support')
    ->set_html('<p>Hello</p>')
    ->send('Hello');

// Custom header
mail_to('user@example.com')
    ->add_header('X-Campaign', 'welcome-2024')
    ->set_html('<p>Hi</p>')
    ->send('Hi');

// Mock (for testing)
$ok = mail_to('user@example.com')->set_html('<p>Test</p>')->send('Test', mock: true);
```

### Welcome Email Pattern

```php
mail_to($user->email, $user->name)
    ->set_html("
        <h1>Welcome, {$user->name}!</h1>
        <p><a href='" . lang_url('/activate/' . $user->token) . "'>Activate</a></p>
    ")
    ->send('Welcome to ' . get_option('site_name'));
```

## Notifier

`Engine\Atomic\Mail\Notifier` -- flash messages and notification queue.

```php
// Helpers
notify('Saved successfully!', 'success');
notify_success('Order created');
notify_info('Please check your email');
notify_warning('Stock is low');
notify_error('Payment failed');

// Read notifications (clears by default)
$all   = get_notifications();           // all
$errs  = get_notifications('error');    // filtered
$ok    = has_notifications('warning');  // bool
clear_notifications();                  // clear all
clear_notifications('error');

// Flash messages (survive exactly N requests, default 1)
set_flash('form_data', $_POST, 1);
$data = get_flash('form_data');         // reads + decrements lifetime
$data = peek_flash('form_data');        // reads without decrementing
$ok   = has_flash('form_data');         // bool
```

## Mail Deliverability Checks

`Engine\Atomic\Mail\MailerUtils` -- DNS validation helpers.

```php
// Helpers
$spf   = mail_check_spf('example.com');              // ['ok'=>bool, ...]
$dkim  = mail_check_dkim('example.com', 'default');  // ['ok'=>bool, ...]
$dmarc = mail_check_dmarc('example.com');            // ['ok'=>bool, ...]
$full  = mail_analyze('example.com', 'default');     // full deliverability report
```

## Shortcodes

```php
// Callback receives ($atts array, ?string $content)
add_shortcode('alert', function (array $atts, ?string $content): string {
    $type = $atts['type'] ?? 'info';
    return "<div class=\"alert alert-$type\">" . ($content ?? '') . "</div>";
});

$html = do_shortcode('[alert type="warning"]Low stock![/alert]');

// Self-closing (no content)
add_shortcode('icon', function (array $atts, ?string $content): string {
    return '<i class="icon-' . ($atts['name'] ?? '') . '"></i>';
});
$html = do_shortcode('[icon name="star"]');

remove_shortcode('alert');
```

The `do_shortcode()` helper wraps `Shortcode::instance()->do_shortcode($text)`.

## Guardrails
- Keep event and hook handlers small and single-purpose.
- Never call `do_action` inside a listener for the same action (infinite loop).
- Call `Mailer::reset()` (or `$mailer->reset()`) between sends in a loop to clear recipients and body.
- Keep locale files as plain arrays without side effects.
