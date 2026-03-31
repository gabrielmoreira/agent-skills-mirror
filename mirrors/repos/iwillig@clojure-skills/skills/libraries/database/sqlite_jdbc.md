---
name: sqlite_jdbc_database_driver
description: JDBC driver for SQLite database access.
---

# SQLite JDBC

JDBC driver for SQLite, enabling Java/Clojure applications to work with SQLite databases.

## Overview

org.xerial/sqlite-jdbc is a JDBC driver that provides seamless integration between Java applications and SQLite databases. It includes a native SQLite library, requiring no external dependencies.

## Core Concepts

**Driver Loading**: SQLite JDBC is automatically loaded by next.jdbc.

```clojure
(require '[next.jdbc :as jdbc])

; SQLite connection
(def db {:dbtype "sqlite" :dbname "mydb.db"})
(def conn (jdbc/get-connection db))
```

**Database File**: SQLite stores data in a single file.

```clojure
; Connection to file-based database
{:dbtype "sqlite" :dbname "data/myapp.db"}

; In-memory database
{:dbtype "sqlite" :dbname ":memory:"}
```

## Key Features

- Pure Java implementation
- Embedded database in a file
- No server required
- ACID transactions
- Full SQL support
- Lightweight and fast for small to medium databases

## When to Use

- Development and testing
- Desktop applications
- Small to medium databases
- Applications requiring minimal deployment
- Local data persistence

## When NOT to Use

- High-concurrency multi-user systems
- Very large databases (terabytes)
- Complex distributed transactions

## Common Patterns

```clojure
; Development configuration
(def dev-db {:dbtype "sqlite" :dbname "dev/dev.db"})

; Test configuration with in-memory database
(def test-db {:dbtype "sqlite" :dbname ":memory:"})

; With next.jdbc and HoneySQL
(require '[next.jdbc :as jdbc]
         '[honey.sql :as sql])

(def query (sql/format {:select [:*] :from [:users]}))
(jdbc/execute! (jdbc/get-connection dev-db) query)
```

## Related Libraries

- com.github.seancorfield/next.jdbc - Use SQLite with next.jdbc
- com.github.seancorfield/honeysql - Build queries for SQLite

## Resources

- Official Documentation: https://github.com/xerial/sqlite-jdbc
- SQLite Documentation: https://www.sqlite.org/

## Notes

This project uses SQLite JDBC with next.jdbc for local persistent storage in development and testing.
