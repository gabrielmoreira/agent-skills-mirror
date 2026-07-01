---
name: atomic-framework-queue-scheduler-telemetry
description: "Use when working on Atomic queue (push jobs, workers, drivers, applications), scheduler (cron-style tasks, frequencies, overlap protection), or the telemetry diagnostics panel."
argument-hint: "Queue jobs, push, worker, scheduler, cron, without_overlapping, telemetry panel, /telemetry routes"
user-invocable: true
---

# Atomic Framework Queue, Scheduler, and Telemetry

## When to Use
- Pushing jobs to the queue or building job handlers.
- Configuring cron-style scheduled tasks.
- Inspecting job status, retrying failed jobs, or using the queue monitor.
- Using the telemetry diagnostics panel at `/telemetry`.

## Engine Files
`engine/Atomic/Queue/*`, `engine/Atomic/Scheduler/*`, `engine/Atomic/Telemetry/*`

## Reference Docs
`docs/queue.md`, `docs/scheduler.md`, `docs/telemetry.md`, `docs/applications.md`, `docs/log.md`

---

## Queue - Pushing Jobs

`Engine\Atomic\Queue\Managers\Manager`

```php
use Engine\Atomic\Queue\Managers\Manager;

$queue = new Manager('default');

// Basic push (named params)
$queue->push(
    [App\Jobs\SendEmail::class, 'handle'],
    ['email' => 'user@example.com', 'subject' => 'Hello']
);

// Positional params
$queue->push(
    [App\Jobs\SendEmail::class, 'handle'],
    ['user@example.com', 'Hello']
);

// With options
$queue->push(
    [App\Jobs\SendEmail::class, 'handle'],
    ['email' => 'user@example.com'],
    [
        'delay'        => 60,    // seconds before processing
        'priority'     => 1,     // lower = sooner
        'timeout'      => 30,
        'max_attempts' => 3,
        'retry_delay'  => 10,
        'ttl'          => 3600,
    ]
);
```

`push()` signature: `push(array $payload, array $data = [], array $options = [], string $uuid = ''): bool`

Handler rules:
- Format: `[ClassName::class, 'method']`
- Named `$data` keys are matched to handler parameter names via reflection.
- Indexed `$data` values are passed positionally.

### Job Handler Shape

```php
namespace App\Jobs;

final class SendEmail
{
    public function handle(string $email, string $subject): void
    {
        // do work
        // if exception thrown: job is marked failed
    }
}
```

### Runtime Methods

```php
$queue->pop_batch();
$queue->process_job($job);
$queue->release($job, $delaySeconds);
$queue->mark_failed($job, $exception);
$queue->mark_completed($job);
$queue->retry();
$queue->retry_by_uuid('job-uuid');
$queue->delete_job('job-uuid');
```

### Drivers

| Driver | Class | Config |
|---|---|---|
| Database | `Queue\Drivers\DB` | `DB_CONFIG.*` |
| Redis | `Queue\Drivers\Redis` | `REDIS.*` |

### CLI Commands

```bash
php atomic queue/worker default    # start worker for 'default' queue
php atomic queue/monitor           # inspect all queues
php atomic queue/retry             # retry all failed jobs
php atomic queue/retry <uuid>      # retry specific job
php atomic queue/delete <uuid>     # delete a job
php atomic queue/db                # show queue DB stats

# Test jobs
php atomic queue/test success
php atomic queue/test failure
php atomic queue/test timeout
php atomic queue/test/monitor      # seed test jobs for monitor
```

### Built-in Queue Applications

`Engine\Atomic\Queue\Applications\*` -- pre-built job handlers. Run directly or push via `Manager->push()`:

```php
// Push to queue (recommended for async)
$queue = new Manager('default');
$queue->push([ImageOptimizer::class, 'optimize'], ['source' => '/img.jpg', 'destination' => '/opt.jpg']);

// Or run synchronously (direct call)
use Engine\Atomic\Queue\Applications\ImageOptimizer;
use Engine\Atomic\Queue\Applications\ImageThumbnail;
use Engine\Atomic\Queue\Applications\MailSender;
use Engine\Atomic\Queue\Applications\MailChecker;
use Engine\Atomic\Queue\Applications\PageCache;
use Engine\Atomic\Queue\Applications\PluginSync;
use Engine\Atomic\Queue\Applications\SystemLogs;

// Image optimization (jpeg, png, webp, avif, svg)
$optimizer = new ImageOptimizer();
$optimizer->optimize(['source' => '/path/img.jpg', 'destination' => '/path/opt.jpg']);

// Thumbnail generation; modes: 'thumbnail', 'small', 'medium', 'large'
$thumb = new ImageThumbnail();
$thumb->generate(['source' => '/img.jpg', 'destination' => '/thumb.jpg', 'mode' => 'medium']);

// Mail sending (uses Mailer under the hood)
$sender = new MailSender();
$sender->send(['to' => 'user@example.com', 'subject' => 'Hello', 'body' => $html]);
$sender->send_test(['to' => 'test@example.com']);  // test delivery

// Mail deliverability checker
$checker = new MailChecker();
$checker->check(['domain' => 'example.com', 'selector' => 'default']);

// Page cache (generate, purge, preload)
$cache = new PageCache();
$cache->generate(['url' => '/products/1', 'ttl' => 3600]);
$cache->purge(['url' => '/products/1']);
$cache->preload(['urls' => ['/products/1', '/products/2']]);

// Plugin sync (sync, fetch updates, apply updates, notify)
$sync = new PluginSync();
$sync->sync(['plugin' => 'monopay']);
$sync->sync_test(['plugin' => 'monopay']);          // test sync without applying
$sync->fetch_updates(['plugin' => 'monopay']);
$sync->apply_updates(['plugin' => 'monopay', 'version' => '1.2.0']);
$sync->notify(['plugin' => 'monopay', 'message' => 'Updated']);

// System logs management
$logs = new SystemLogs();
$logs->archive(['before' => '2025-01-01', 'channel' => 'atomic']);
$logs->delete(['before' => '2024-01-01']);
$logs->export(['channel' => 'error', 'format' => 'csv']);
```

All job handlers receive `array $params` and return `bool`.

---

## Scheduler

`Engine\Atomic\Scheduler\Scheduler` - schedule file: `routes/schedule.php`.

```php
use Engine\Atomic\Scheduler\Scheduler;

$scheduler = Scheduler::instance();

// Closure task
$scheduler->call(function () {
    echo "cleanup\n";
})->daily_at('03:00')->description('Cleanup old logs');

// Class method (string)
$scheduler->call('App\\Tasks\\CacheWarmer->handle')
    ->hourly()
    ->without_overlapping()     // uses Mutex internally
    ->description('Warm cache');

// Shell command
$scheduler->exec('php atomic queue/monitor')
    ->every_five_minutes();

// Class, method, args
$scheduler->job(App\Tasks\Report::class, 'handle', ['daily']);
```

### Frequency Methods (ManagesFrequencies)

```
every_minute()         every_two_minutes()    every_five_minutes()
every_ten_minutes()    every_fifteen_minutes() every_thirty_minutes()
hourly()               hourly_at(15)          every_two_hours()
daily()                daily_at('02:30')      twice_daily(1, 13)
weekly()               weekly_on(1, '08:00')  monthly()
monthly_on(15, '10:00') quarterly()           yearly()
cron('*/5 * * * *')

// Day filters
weekdays() weekends() mondays() tuesdays() ... sundays()
timezone('Europe/Kyiv')
```

### Event Controls

```php
$scheduler->call($task)
    ->when(fn() => app_env() === 'production')
    ->skip(fn() => false)
    ->before(fn($event) => Log::info('starting'))
    ->after(fn($event) => Log::info('done'))
    ->on_success(fn($event) => null)
    ->on_failure(fn($e) => Log::error($e->getMessage()))
    ->without_overlapping(60);  // 60s mutex TTL
```

### CLI Commands

```bash
php atomic schedule/run      # run all due tasks once
php atomic schedule/work     # loop forever
php atomic schedule/work 30  # loop every 30s
php atomic schedule/list     # list all registered tasks
php atomic schedule/test     # test-run without executing
```

---

## Telemetry Panel

Diagnostics served at `/telemetry`. Sanitized through `Core\Redactor` before display.

| Route | Purpose |
|---|---|
| `GET /telemetry` | Queue job list (filterable by status, UUID, date) |
| `GET /telemetry/events/@driver/@job_uuid` | Job event timeline |
| `GET /telemetry/dashboard` | PHP/framework/DB runtime snapshot |
| `GET /telemetry/hive` | Sanitized F3 hive dump |
| `GET /telemetry/logs` | Paginated log output (`?channel=auth&date=2025-01-01`) |
| `GET /telemetry/log-channels` | Available channels and dates |
| `GET /telemetry/log-stat` | File line count + mtime |
| `GET /telemetry/dumps/@dump_id` | JSON dump by UUID |

Production config: set `TELEMETRY_ADMIN_ONLY=true`.

Dumps are created by `Log::dump()` and `Log::dump_hive()` only when debug mode is active.

## Guardrails
- Job handlers must be deterministic and idempotent (they can be retried).
- Never throw uncaught exceptions directly inside a handler - wrap in try/catch and let the queue mark the job failed.
- Scheduler tasks that must not run in parallel must use `without_overlapping()`.
- Never expose the telemetry panel publicly - always set `TELEMETRY_ADMIN_ONLY=true` in production.
