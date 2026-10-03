---
title: Laravel
category: Framework and library
x-claim-provenance:
- claim: Once the configuration has been cached with config:cache, the .env file is not loaded during requests or Artisan commands, so the env function returns only external, system-level environment variables and should be called only from configuration files.
  source: https://laravel.com/docs/configuration
  scope: Laravel 13.x documentation, read 2026-09.
- claim: A queued job that accepts an Eloquent model serializes only the model identifier, and the queue system re-retrieves the full model and its loaded relationships from the database when the job is handled; a job dispatched within a database transaction may be processed before the transaction commits unless the connection's after_commit option or the job's afterCommit method defers dispatch until open parent transactions commit.
  source: https://laravel.com/docs/queues
  scope: Laravel 13.x documentation, read 2026-09.
- claim: Laravel 11 introduced a new default application structure with fewer service providers, middleware, and configuration files, and the upgrade guide does not recommend that Laravel 10 applications migrate their structure, because Laravel 11 also supports the Laravel 10 structure.
  source: https://laravel.com/docs/11.x/upgrade
---

The configured Laravel and PHP versions, service providers, container bindings, middleware, authentication guards, queues, cache, database, filesystem, scheduler, and deployment process define the Laravel environment. Route and middleware order, binding scope, validation, authorization policies, Eloquent and transaction behavior, events and listeners, queued-job ownership, serialization, migrations, and configuration caching are behavioral contracts.

Configuration caching changes what code reads. Once `config:cache` has run, Laravel no longer loads `.env`, so `env()` called anywhere outside the configuration files returns only variables set in the real environment, or its default, in a cached production deployment while it works in development.

Queued work has timing of its own. A job that receives an Eloquent model serializes only the model's identifier and reloads the model and its loaded relationships from the database when a worker handles it, so the job sees the row as it is then rather than as it was at dispatch. A job dispatched inside a database transaction can run before that transaction commits, and so before its rows exist, unless the connection's `after_commit` option or the job's `afterCommit` defers dispatch until the commit. Behavior runs through provider boot order, container resolution, middleware, model binding, validation, guards and policies, Eloquent scopes and relationships, transactions, events, observers, queued jobs, retries, scheduling, cache, and termination hooks. Characteristic failure modes are lazy-loaded queries, mass assignment, tenant scoping, jobs serialized with stale state, side effects repeated on retry, and configuration that differs after caching.

Upgrades follow crossed-version requirements, and compatibility has to be settled for sessions, password hashes, cache keys, queued payloads, stored models, public storage, and third-party packages. Application-skeleton and starter-kit files are project source rather than package-manager output, so their destination-version changes are reconciled explicitly against the language minimum and installed first-party packages; Laravel 11's slimmer default structure, for example, is not something its upgrade guide expects a Laravel 10 application to adopt, since Laravel 11 also supports the older structure.

Code is also referenced indirectly, through:

- route and event caches and package discovery
- string class references, morph maps, casts, and model observers
- queue names and configuration and environment keys
- migrations, Blade templates, and commands

Evidence comes from the narrowest container, HTTP, queue, command, or database boundary that preserves the behavior, with application state, database transactions, cache, filesystem, clock, queues, and events isolated between cases. Behavioral evidence covers allowed and denied authorization, validation, query shape, transaction rollback, migration paths, job retry and idempotency, serialization, scheduler ownership, and cleanup. Configured production caches and worker modes change resolution and are runtime evidence where they apply, and a change must preserve public routes, stored data, queue compatibility, and deployment order unless altering them is part of its requested outcome.
