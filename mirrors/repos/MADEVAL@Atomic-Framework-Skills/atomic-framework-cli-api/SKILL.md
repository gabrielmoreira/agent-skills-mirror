---
name: atomic-framework-cli-api
description: "Use when working on Atomic CLI commands, API entrypoints, console input/output, scaffolders, init flows, migrations/queue/scheduler CLI subcommands, or command-facing bootstrap logic."
argument-hint: "CLI commands, php atomic, API routes, scaffolding, console output"
user-invocable: true
---

# Atomic Framework CLI and API

## When to Use
- Running or building `php atomic` commands.
- Registering new CLI routes or command handlers.
- Working on API entrypoints or API-only request handling.
- Building or modifying init/scaffold flows.

## Engine Files
`engine/Atomic/CLI/*` (CLI, Capabilities, Console/*, DB, File, Init, Init/*, Migrations, Queue, Scheduler, Seeder, Style), `engine/Atomic/API/*` (Api)

## Reference Docs
`docs/cli.md`, `docs/database.md`, `docs/migrations.md`, `docs/queue.md`, `docs/scheduler.md`

---

## Running Commands

```bash
# Framework built-in commands
php atomic help
php atomic version
php atomic routes           # list all registered routes
php atomic classes          # list loaded classes
php atomic custom-hive      # dump custom hive keys (note: hyphen, not underscore)
php atomic cache/clear      # reset F3 cache
php atomic redis/clear      # delete all atomic.* Redis keys

php atomic migrations/init
php atomic migrations/create create_posts_table
php atomic migrations/migrate
php atomic migrations/rollback
php atomic migrations/status
php atomic migrations/publish monopay

php atomic queue/worker default
php atomic queue/monitor
php atomic queue/retry
php atomic queue/retry <job_uuid>
php atomic queue/delete <job_uuid>

php atomic schedule/run
php atomic schedule/work
php atomic schedule/work 30
php atomic schedule/list
php atomic schedule/test
php atomic schedule/help       # list scheduled tasks with cron expression

php atomic db/tables
php atomic db/truncate <table_name>
php atomic db/truncate/queue   # truncate jobs queue table
php atomic db/sessions
php atomic db/users
php atomic db/pages
php atomic db/storage
php atomic db/mutex
php atomic db/queue            # create queue DB table (migration)

php atomic logs/rotate         # rotate log files

# File conversion (requires source file, output file)
php atomic file/csv2pdf input.csv output.pdf
php atomic file/xls2pdf input.xls output.pdf

# Seeding bundled data
php atomic seed/users
php atomic seed/roles
php atomic seed/pages

# Test queue jobs
php atomic queue/test success
php atomic queue/test failure
php atomic queue/test timeout
php atomic queue/test/monitor      # seed test jobs for monitor

# Init and key generation
php atomic init
php atomic init/key
php atomic init/guide
```

## CLI Entry Point

`App::handle_command($argv)` normalizes `schedule:run` → `/schedule/run` and dispatches through the F3 router.

CLI routes live in `routes/cli.php`:

```php
// routes/cli.php
$app->route('GET /my-command', 'App\\CLI\\MyHandler->run');
```

See [atomic-framework-cli-entrypoint/SKILL.md](atomic-framework-cli-entrypoint/SKILL.md) for the recommended project-level CLI stub (`atomic`) with shebang and bootstrap example.

## CLI Command Handler Pattern

```php
namespace App\CLI;

final class SendReport
{
    public function run(\Base $f3, array $params): void
    {
        // $f3->get('SERVER.argv') for raw args
        $output = new \Engine\Atomic\CLI\Console\Output();
        $output->line('Sending report...');
        // ... do work
        exit(0);
    }
}
```

## Console Output

`Engine\Atomic\CLI\Console\Output` - write to stdout/stderr.
`Engine\Atomic\CLI\Console\Input` - read from stdin.

```php
$output = new \Engine\Atomic\CLI\Console\Output();
$output->line('Processing...');
$output->error('Something went wrong');

$input = new \Engine\Atomic\CLI\Console\Input();
$value = $input->ask('Enter name: ');
```

## Style (ANSI Colors)

`Engine\Atomic\CLI\Style` -- ANSI color helpers; auto-disabled when the terminal does not support colors (`Capabilities::supports_colors()`).

```php
use Engine\Atomic\CLI\Style;

echo Style::green('Done!') . PHP_EOL;
echo Style::red('Error!') . PHP_EOL;
echo Style::yellow('Warning') . PHP_EOL;
echo Style::cyan('Info') . PHP_EOL;
echo Style::bold('Important') . PHP_EOL;

// Pre-formatted labels
echo Style::success_label() . ' Job complete' . PHP_EOL;  // [OK]
echo Style::error_label()   . ' Failed'        . PHP_EOL;  // [ERROR]
echo Style::warning_label() . ' Deprecated'    . PHP_EOL;  // [WARNING]

// Bold variant
echo Style::green('Success', bold: true) . PHP_EOL;
```

## Init and Scaffold

`Engine\Atomic\CLI\Init` dispatches to:
- `InitInstaller` - sets up a fresh project (config, directories, composer packages)
- `InitScaffold` - generates boilerplate files (controllers, models, migrations)

```bash
php atomic init         # initial project setup + key generation
php atomic init/key     # regenerate application keys
php atomic init/guide   # print setup guide to console
```

## DB CLI Commands

`Engine\Atomic\CLI\DB` exposes database introspection and admin commands.

```bash
php atomic db/tables           # list all tables
php atomic db/truncate posts   # truncate a table
php atomic db/sessions         # show session table stats
php atomic db/storage          # show storage tables
php atomic db/mutex            # show mutex locks
```

## API Entrypoint

`Engine\Atomic\API\Api` is a **trait** (not a base class) for use in API controllers. It provides helpers for reading the request body and sending JSON responses.

```php
namespace App\Http\Controllers\API;

use Engine\Atomic\API\Api;

final class UserController
{
    use Api;

    public function show(\Base $f3, array $params): void
    {
        $uuid = $this->param('uuid');        // route param

        // body() reads POST/GET or JSON body depending on Content-Type
        $data = $this->body();               // array

        $user = User::find($uuid);
        if (!$user) {
            $this->fail('Not found', 404);   // JSON error response
            return;
        }

        $this->json(['user' => $user->cast()]);  // JSON success response
    }
}
```

**`Api` trait methods:**

| Method | Signature | Description |
|---|---|---|
| `json()` | `json(mixed $data, int $code = 200): void` | Send JSON response |
| `fail()` | `fail(string $msg, int $code = 400, array $extra = []): void` | Send JSON error |
| `body()` | `body(): array` | Parse request body (JSON, POST, or GET) |
| `param()` | `param(string $key, mixed $default = null): mixed` | Get route param from `PARAMS` |

Routes under `/api/*` are loaded from `routes/api.php`.

## Capabilities

`Engine\Atomic\CLI\Capabilities` registers what CLI commands the framework can handle. Check this when adding a new command family.

## Guardrails
- CLI controllers must call `exit(0)` or `exit(1)` explicitly.
- API controllers must always return JSON - never HTML.
- Keep scaffold-generated files minimal and idiomatic.
