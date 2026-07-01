---
name: atomic-framework-cli-entrypoint
description: "Project-level CLI entrypoint script: shebang, bootstrap and delegation to the framework command handler."
argument-hint: "entrypoint, shebang, php atomic, bootstrap/app.php, vendor/autoload.php"
user-invocable: true
---

# Atomic CLI Entrypoint

## When to Use
- When verifying or creating the project-level CLI stub file (the executable that dispatches console commands).
- When documenting how to run `php atomic` or execute the `atomic` file directly.

## Purpose
This file is the tiny, project-root executable that boots Composer autoload, loads the application bootstrap and delegates CLI control to the framework. 

## Recommended filename and location
Place the file in the project root as `atomic` (preferred) or `atomic.php`.
Make it executable (`chmod +x atomic`) so it can be run directly (`./atomic`).

## Entrypoint script (exact)
```php
#!/usr/bin/env php
<?php
define('ATOMIC_START', microtime(true));
require __DIR__.'/vendor/autoload.php';
global $argv;

$app = require_once __DIR__.'/bootstrap/app.php';
$status = $app->handle_command($argv);

exit($status);
```

## Notes
- `bootstrap/app.php` MUST return the application/container instance exposing `handle_command(array $argv): int`.
- Use `./atomic help` or `php atomic help` to list available commands.
- The script should be intentionally minimal: autoload, bootstrap, delegate, exit.

## Examples
- `./atomic help`
- `php atomic init`

## Troubleshooting
- If commands do not appear, verify `bootstrap/app.php` returns a valid application and `routes/cli.php` is loaded by the bootstrap.
- Ensure `vendor/autoload.php` exists (run `composer install`).
