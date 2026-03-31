---
name: next_jdbc_database_access
description: |
  Modern JDBC wrapper for SQL database access in Clojure. Use when querying databases, 
  executing SQL, database transactions, connection pooling, or when the user mentions 
  JDBC, database access, SQL queries, next.jdbc, relational databases, or database 
  connections.
---

# next.jdbc

A modern, friendly Clojure wrapper around JDBC for database access.

## Overview

next.jdbc provides a simpler, more idiomatic API for working with relational databases compared to raw JDBC. It handles connection management, statement execution, and result set conversion.

## Core Concepts

**Connections**: Manage database connections with a connection map.

```clojure
(require '[next.jdbc :as jdbc])

(def db {:dbtype "sqlite" :dbname "database.db"})
(def conn (jdbc/get-connection db))
```

**Queries**: Execute SQL queries and retrieve results.

```clojure
; Query returns rows as maps
(jdbc/execute! conn ["SELECT * FROM users WHERE id = ?" 1])
; => [{:id 1, :name "Alice", :email "alice@example.com"}]
```

**Transactions**: Execute multiple statements atomically.

```clojure
(jdbc/with-transaction [tx conn]
  (jdbc/execute! tx ["INSERT INTO users VALUES (?, ?, ?)" 2 "Bob" "bob@example.com"])
  (jdbc/execute! tx ["UPDATE users SET active = true WHERE id = ?" 2]))
```

## Key Features

- Connection pooling support
- Parameterized queries (prevent SQL injection)
- Result set as maps or vectors
- Transaction support
- Prepared statements
- Metadata inspection
- Column name formatting options

## When to Use

- Querying and updating relational databases
- Building data access layers
- Running migrations (with ragtime)
- Working with SQL directly

## When NOT to Use

- For complex object-relational mapping (consider Datomic)
- When you need high-level query builders (use HoneySQL)

## Common Patterns

```clojure
; Using HoneySQL with next.jdbc
(require '[honey.sql :as sql])

(def query (sql/format {:select [:*] :from [:users] :where [:= :id 1]}))
(jdbc/execute! conn query)

; Connection pooling
(require '[next.jdbc.connection :as connection])
(def datasource (connection/->PooledDataSource
                  {:dbtype "sqlite" :dbname "database.db"}))
```

## Related Libraries

- metosin/honeysql - SQL query builder
- dev.weavejester/ragtime - Database migrations
- org.xerial/sqlite-jdbc - SQLite driver

## Resources

- Official Documentation: https://github.com/seancorfield/next.jdbc
- API Documentation: https://cljdoc.org/d/seancorfield/next.jdbc

## Notes

This project uses next.jdbc with SQLite for local data persistence.
