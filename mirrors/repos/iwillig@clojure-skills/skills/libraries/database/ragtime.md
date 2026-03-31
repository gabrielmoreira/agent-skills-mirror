---
name: ragtime_database_migrations
description: Database migration library for managing schema changes.
---

# Ragtime

A simple, schema migration library for Clojure with support for various databases.

## Overview

Ragtime manages database schema migrations, allowing you to version and track changes to your database structure in code.

## Core Concepts

**Migrations**: SQL or Clojure-based schema changes.

```clojure
(require '[ragtime.core :as ragtime])
(require '[ragtime.strategies :as strategies])

; Migrations are typically stored in files or defined as data
; Example migration file: resources/migrations/001-create-users.sql
; CREATE TABLE users (
;   id INTEGER PRIMARY KEY,
;   name TEXT NOT NULL,
;   email TEXT NOT NULL
; );
```

**Database Tracking**: Ragtime tracks which migrations have been applied.

```clojure
(def config {:datastore (ragtime.sql.files/files-datastore "resources/migrations")
             :migrations (ragtime.sql.files/load-files "resources/migrations")})

; Apply pending migrations
(ragtime/migrate config)

; Rollback migrations
(ragtime/rollback config)
```

## Key Features

- File-based migrations
- Clojure-based migrations
- Up and down migrations
- Multiple database support
- Migration history tracking
- Simple, focused API

## When to Use

- Managing database schema versions
- Coordinating schema changes across environments
- Ensuring consistent database state
- Deploying applications with schema changes

## When NOT to Use

- For application data seeds (use separate tools)
- For real-time schema modifications

## Common Patterns

```clojure
; Typical migration file structure
; resources/migrations/001-initial-schema.sql
; CREATE TABLE users (id SERIAL PRIMARY KEY, ...);
; CREATE TABLE posts (id SERIAL PRIMARY KEY, ...);

; resources/migrations/002-add-timestamps.sql
; ALTER TABLE users ADD COLUMN created_at TIMESTAMP;
; ALTER TABLE posts ADD COLUMN created_at TIMESTAMP;

; In your application
(defn migrate-database [datasource]
  (let [config {:datastore (ragtime.sql.files/files-datastore "resources/migrations")
                :migrations (ragtime.sql.files/load-files "resources/migrations")}]
    (ragtime/migrate config)))
```

## Related Libraries

- com.github.seancorfield/next.jdbc - Execute migrations
- dev.weavejester/ragtime.next-jdbc - Next.jdbc integration

## Resources

- Official Documentation: https://github.com/weavejester/ragtime
- API Documentation: https://cljdoc.org/d/weavejester/ragtime

## Notes

This project uses Ragtime for managing SQLite schema migrations in resources/migrations/.
