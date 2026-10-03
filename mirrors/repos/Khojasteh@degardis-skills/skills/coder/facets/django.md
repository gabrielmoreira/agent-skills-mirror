---
title: Django
category: Framework and library
x-claim-provenance:
- claim: A feature deprecated in feature release A.x keeps working with warnings in all A.x versions and is removed in B.0, or B.1 if deprecated in the last A.x feature release; the RemovedInDjangoXXWarning deprecation warnings are silent by default.
  source: https://docs.djangoproject.com/en/dev/internals/release-process/
- claim: An upgrade through more than one feature version is usually easier through each feature release incrementally, using its latest patch release and reading the release notes of each final release after the current version up to the target, after resolving deprecation warnings raised under the current version.
  source: https://docs.djangoproject.com/en/stable/howto/upgrade-version/
- claim: migrate --fake-initial skips an app's initial migration if tables with the names of all models its CreateModel operations create already exist, and does not check for matching schema beyond table names.
  source: https://docs.djangoproject.com/en/stable/ref/django-admin/
- claim: ATOMIC_REQUESTS wraps each view in a transaction that commits if the response is produced without problems and rolls back if the view raises; transaction.on_commit callbacks run after the open transaction commits, are discarded if it rolls back, and run immediately when no transaction is open.
  source: https://docs.djangoproject.com/en/stable/topics/db/transactions/
---

The configured Django, Python, database, server, installed applications, middleware, settings, and migration state decide which APIs and upgrade paths apply. URL routing, middleware order, authentication and permissions, forms or serializers, ORM evaluation, transaction boundaries, constraints, migrations, signals, caching, templates, static/media handling, and background jobs are contracts.

A feature deprecated in one release keeps working, with warnings that are silent by default, through the rest of that major series and is removed at the next major version, or one feature release later when it was deprecated in the series' last feature release. A removal is therefore announced in the release that deprecated it, and the destination release notes may not repeat it, which is why a multi-release upgrade moves through each intermediate feature release on its latest patch and reads every release's notes along the way. Upgrade compatibility also depends on the destination release requirements, on every deprecation in the releases crossed, and on continuity for sessions, signed cookies, password hashes, content-type and permission rows, cache keys, and third-party applications.

Failure timing differs across request, commit, signal, command, and background-task paths. With `ATOMIC_REQUESTS` each view runs in a transaction that rolls back if the view raises, and a callback registered with `transaction.on_commit` runs only after the enclosing transaction commits, is discarded if it rolls back, and runs immediately when no transaction is open, so the same code can send an email or enqueue a job at different moments depending on where it is called. Behavior also runs through queryset laziness, select/prefetch behavior, transactions, locking, validation, permissions, template escaping, redirects, cache invalidation, and cleanup.

Code is also referenced indirectly, so renaming or moving it can break:

- app labels, string model references, and URL names
- settings, admin registration, serializers, and templates
- task registrations
- migration dependencies and historical model state

Declared migration history and the real schema can diverge. `migrate --fake-initial` records an initial migration as applied whenever tables with the right names exist, without comparing their columns, and faked or introspected initial migrations and existing data can invalidate an account built from source alone, which makes the real schema boundary the evidence.

Behavioral evidence depends on the configured settings, database engine, middleware, installed applications, server entry point, and background runner, and hosted or database integration evidence is needed where request, transaction, migration, or template behavior decides the result. It distinguishes permissions, validation, query count, lost-update controls, constraints, migration forward and reverse behavior, signal effects, cache freshness, time zones, and cleanup. Deprecation warnings surfaced during upgrade checks are upgrade evidence, and performance evidence comes from warmed production settings rather than development instrumentation.
