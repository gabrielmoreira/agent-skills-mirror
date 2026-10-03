---
title: Rails
category: Framework and library
x-claim-provenance:
- claim: The Rails upgrade guide recommends moving one minor version at a time to make good use of deprecation warnings; bin/rails app:update creates config/initializers/new_framework_defaults_X_Y.rb, whose new defaults can be enabled gradually across deployments before config.load_defaults is updated.
  source: https://guides.rubyonrails.org/upgrading_ruby_on_rails.html
- claim: Rails autoloads with Zeitwerk, which requires file names to match the constants they define with directories acting as namespaces; production eager-loads the application on boot, and bin/rails zeitwerk:check validates the project structure.
  source: https://guides.rubyonrails.org/autoloading_and_reloading_constants.html
- claim: A job enqueued inside a database transaction without enqueue_after_transaction_commit or an after_commit callback may run before the data it needs is visible to other connections, or be enqueued even if the transaction rolls back; enqueue_after_transaction_commit defers enqueuing until the surrounding transaction commits.
  source: https://guides.rubyonrails.org/active_job_basics.html
  scope: Rails 8.1 guide, read 2026-09.
---

The configured Rails and Ruby versions, database adapters, autoloading mode, middleware, authentication, jobs, cache, storage, mail, and deployment process decide which APIs apply. Route and controller behavior, parameter filtering, validation and authorization, Active Record transaction and locking boundaries, callbacks, jobs and retries, serialization, migrations, and configuration ownership are behavioral contracts.

Upgrades follow crossed-release requirements one minor version at a time, so that each version's deprecation warnings surface before a later version removes what they warned about, and compatibility has to be settled for sessions and signed data, password hashes, cache entries, queued payloads, stored attachments, schemas, routes, and third-party gems. Application-skeleton files and generated new-default proposals are project source. `bin/rails app:update` writes a `new_framework_defaults` initializer whose settings can be enabled one at a time across deployments, so each proposed initializer and middleware change is reconciled on its own, and advancing `config.load_defaults` is an explicit compatibility decision.

Constant loading follows file names. Zeitwerk expects each file to define the constant its path names, with directories as namespaces, and production eager-loads the whole application at boot, so a misnamed file that development never loaded can fail only at production startup. A job enqueued inside a transaction can run before its data is visible to other connections, or be enqueued even though the transaction rolls back, unless enqueuing is deferred to the commit or moved into an `after_commit` callback. Behavior runs through middleware, routing, filters, strong parameters, policies, model validation, callbacks, association loading, transactions, after-commit work, jobs, retries, mail, cache, storage, and shutdown.

Code is also referenced indirectly, through:

- route helpers and names and autoload constants
- polymorphic types, serialized columns, and STI names
- callbacks, observers, and job queues
- templates, translations, credentials, and initializers
- migrations and generated schema state

Characteristic failure modes are N+1 queries, callbacks hiding side effects, tenant scope loss, jobs carrying stale records, repeated effects on retry, unsafe parameter assignment, and migrations whose code no longer matches historical behavior.

Evidence comes from the narrowest model, request, job, mail, command, or database boundary that preserves the framework behavior, with database, cache, jobs, clock, filesystem, mail, and global configuration isolated between cases. Behavioral evidence covers routes, validation, allowed and denied authorization, query count, locks and transactions, callbacks, job idempotency, serialization, migration forward and reverse paths, and cleanup. Production eager loading and relevant asset or deployment configuration are runtime evidence when constant loading, initialization, or build output matters.
