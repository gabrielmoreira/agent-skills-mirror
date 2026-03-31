---
name: honeysql_sql_query_builder
description: |
  Build SQL queries using Clojure data structures with HoneySQL. Use when building 
  dynamic SQL, composing queries programmatically, parameterized queries, SQL generation, 
  or when the user mentions SQL builder, HoneySQL, query composition, SQL DSL, or 
  data-driven queries.
---

# HoneySQL

A data-driven SQL query builder that converts Clojure data structures into SQL strings.

## Overview

HoneySQL allows you to build SQL queries programmatically using Clojure maps and vectors, making SQL composition type-safe and composable.

## Core Concepts

**Query Building**: Write SQL as Clojure data structures.

```clojure
(require '[honey.sql :as sql])

; SELECT query
(sql/format {:select [:id :name]
             :from [:users]
             :where [:= :active true]})
; => ["SELECT id, name FROM users WHERE active = ?" true]

; INSERT query
(sql/format {:insert-into :users
             :values [{:id 1 :name "Alice" :email "alice@example.com"}]})
; => ["INSERT INTO users (id, name, email) VALUES (?, ?, ?)" 1 "Alice" "alice@example.com"]
```

**Composability**: Build complex queries from simpler parts.

```clojure
(def base-query {:select [:*] :from [:users]})
(def with-filter (assoc base-query :where [:= :active true]))
(def with-order (assoc with-filter :order-by [[:name :asc]]))

(sql/format with-order)
```

## Key Features

- Data-driven query building
- Support for SELECT, INSERT, UPDATE, DELETE
- JOIN operations
- Subqueries
- Parameterized queries (SQL injection safe)
- Database-specific dialects
- CTE (Common Table Expressions)
- Aggregation functions

## When to Use

- Building dynamic SQL queries
- Complex queries with conditional clauses
- Query composition and reuse
- Parameterized query generation

## When NOT to Use

- Simple queries (raw SQL may be clearer)
- When you need an ORM (use an alternative)

## Common Patterns

```clojure
; With next.jdbc
(require '[next.jdbc :as jdbc])

(def query (sql/format {:select [:*]
                        :from [:users]
                        :where [:and
                                [:= :active true]
                                [:> :age 18]]}))
(jdbc/execute! conn query)

; Building conditional queries
(def user-id 1)
(sql/format {:select [:*]
             :from [:users]
             :where (if user-id
                      [:= :id user-id]
                      [:= :active true])})
```

## Related Libraries

- com.github.seancorfield/next.jdbc - Execute HoneySQL queries
- dev.weavejester/ragtime - Migrations

## Resources

- Official Documentation: https://github.com/seancorfield/honeysql
- API Documentation: https://cljdoc.org/d/seancorfield/honeysql

## Notes

This project uses HoneySQL with next.jdbc for building dynamic SQL queries safely.
