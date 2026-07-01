---
name: atomic-framework-tools-websockets
description: "Use when working on Atomic AI Connector (ai_connector), WebSocket servers (Workerman), Tools utilities (Telegram notifier, Nonce, Transient), or the AI client chain for completions, embeddings, and multi-provider setup."
argument-hint: "ai_connector, completion, chat_completion, embeddings, WebSocket server, Workerman, Telegram, Tools"
user-invocable: true
---

# Atomic Framework Tools and WebSockets

## When to Use
- Using or extending the AI Connector for LLM completions or embeddings.
- Building or modifying a Workerman-based WebSocket server.
- Sending Telegram messages or bot notifications.
- Working on Nonce or Transient utilities (see also `atomic-framework-mutex-session`).

## Engine Files
`engine/Atomic/Tools/*` (AIConnector, Nonce, Transient, Telegram), `engine/Atomic/WebSockets/*` (Server, Connection, Test)

## Reference Docs
`docs/ai_connector.md`, `docs/websockets.md`, `docs/telegram.md`, `docs/nonce.md`, `docs/transient.md`

---

## AI Connector

`Engine\Atomic\Tools\AIConnector` -- singleton per API key.

```php
use Engine\Atomic\Tools\AIConnector;

// Singleton per provider (default: openai)
$ai = AIConnector::instance($apiKey);                        // uses openai provider
$ai = AIConnector::instance($apiKey, 'groq');                // force groq provider
$ai = AIConnector::instance();                               // reads api_key from hive: ai.openai.api_key
```

### Text Completion

```php
$result = $ai->completion('Write a product description for blue sneakers');
```

### Chat Completion

```php
$messages = [
    ['role' => 'system', 'content' => 'You are a helpful assistant.'],
    ['role' => 'user',   'content' => 'Summarize this article...'],
];
$result = $ai->chat_completion($messages);
$result = $ai->chat_completion($messages, ['temperature' => 0.7, 'max_tokens' => 1024]);
```

### Embeddings

```php
$vector = $ai->create_embeddings('Text to embed');  // returns float[]
```

### Provider and Model Selection

```php
$ai->set_provider('openrouter')->set_model('google/gemini-2.5-flash');
$ai->set_provider('groq')->set_model('llama3-70b-8192');
$ai->set_provider('openai')->set_model('gpt-4o-mini');
$ai->set_provider('globus');
```

### Providers and Config Hive Keys

| Provider | Hive key | Default model |
|---|---|---|
| openai | `ai.openai.api_key` | `gpt-4o-mini` |
| groq | `ai.groq.api_key` | `llama3-8b-8192` |
| openrouter | `ai.openrouter.api_key` | `openai/gpt-4o-mini` |
| globus | `ai.globus.api_key`, `ai.globus.endpoint` | configured via endpoint |

```php
// config/tools.php or .env
$f3->set('ai.openai.api_key', $_ENV['OPENAI_API_KEY']);
```

---

## WebSocket Server

`Engine\Atomic\WebSockets\Server` -- abstract, Workerman-based.

```php
namespace App\WebSockets;

use Engine\Atomic\WebSockets\Server;
use Engine\Atomic\WebSockets\Connection;

final class ChatServer extends Server
{
    protected function setup(): void
    {
        // Subscribe to Redis pubsub channel (optional)
        $this->subscribe_to_channel('chat-events');
    }

    protected function on_connect(Connection $connection): void
    {
        $connection->send('Welcome! Your ID: ' . $connection->id());
    }

    protected function on_message(Connection $connection, string $data, int $op): void
    {
        // $op = 0x1 text, 0x2 binary
        $msg = json_decode($data, true);
        $connection->send(json_encode(['echo' => $msg]));
    }

    protected function on_disconnect(Connection $connection): void
    {
        // cleanup
    }
}
```

### Connection API

```php
$connection->id();       // unique ID
$connection->send($d);   // send string or binary
$connection->close();    // close with optional code/reason
```

### Redis Pubsub Bridge

Call `subscribe_to_channel('channel')` in `setup()`.
Expected Redis payload: `{"task_id": "...", "status": "done", "data": {}}`.
Server broadcasts matching messages to all connected clients.

### Running the Server

Workerman creates PID + log files named `workerman.<lowercased-classname>.*`.

There are no built-in `websockets/start|stop|status` CLI commands. Start the server by calling `->run()` from a custom CLI handler registered in `routes/cli.php`:

```php
// routes/cli.php
$atomic->route('GET /ws/start [cli]', 'App\CLI\Websockets->start');

// App/CLI/Websockets.php
final class Websockets {
    public function start(\Base $f3): void {
        (new \App\WebSockets\ChatServer())->run();
    }
}
```

---

## Telegram

```php
use Engine\Atomic\Tools\Telegram;

// Singleton (constructor is private)
$tg = Telegram::instance();                    // reads TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID from hive
$tg = Telegram::instance($token, $chatId);    // explicit credentials

// Send text message
$tg->send('Order shipped!');                             // to default chat_id
$tg->send('<b>Alert</b>', $chatId, ['parse_mode'=>'HTML']);

// Other methods
$tg->send_photo($photoUrl, ['caption' => 'Screenshot']);
$tg->send_document($fileUrl);
$tg->get_me();                                  // bot info
$tg->set_webhook($url);
$tg->delete_webhook();
$tg->verify_web_app_init_data($initData);      // array|false - Mini App auth
$tg->verify_login_widget($authData);           // array|false - Login Widget auth
$tg->create_invoice_link($data);               // Telegram Payments
$tg->answer_pre_checkout_query($id, true);
```

### Helpers (helpers.php)

```php
// Get/create singleton with optional override
$tg = telegram();                         // uses TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
$tg = telegram($token, $chatId);          // custom credentials

// Quick send
$res = telegram_send('Order created!');                    // to default TELEGRAM_CHAT_ID
$res = telegram_send('Alert!', '-100123456789');           // to specific chat
$res = telegram_send('*Bold*', null, ['parse_mode' => 'MarkdownV2']);
// $res = ['ok' => bool, 'result' => [...]]
```

Config: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` hive keys.

For Telegram login (bot widget verification), see `atomic-framework-app-auth` skill.

---

## Nonce and Transient

Full API documented in `atomic-framework-mutex-session` skill.

```php
create_nonce('delete-post', 1800);
verify_nonce($_POST['nonce'] ?? '', 'delete-post');

set_transient('key', $data, 3600);
get_transient('key');
delete_transient('key');
```

## Guardrails
- Store AI API keys in environment/config only; never hardcode them.
- WebSocket handlers must be stateless across reconnects; store state in Redis or DB.
- `subscribe_to_channel()` must be called inside `setup()` only.
- The Telegram Bot Token is sensitive; treat it like a password.
