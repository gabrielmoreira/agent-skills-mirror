---
name: codox_documentation_generator
description: Documentation generator for Clojure libraries.
---

# Codox

A Clojure documentation generator that creates static HTML documentation from your source code.

## Overview

Codox automatically generates HTML documentation from docstrings and metadata in your Clojure code, creating searchable API references.

## Core Concepts

**Generating Documentation**: Create docs from code.

```clojure
; In deps.edn:
; :codox {:extra-deps {codox/codox {:mvn/version "0.10.8"}}
;         :metadata {:doc/format :markdown}
;         :exec-fn codox.main/generate-docs
;         :exec-args {:source-paths ["src"]}}

; In terminal:
; clojure -X:codox
```

**Docstrings**: Documentation from code comments.

```clojure
(defn add
  "Adds two numbers together.
   
   Args:
     a: First number
     b: Second number
   
   Returns:
     Sum of a and b
   
   Examples:
     (add 1 2)
     ; => 3"
  [a b]
  (+ a b))
```

## Key Features

- Automatic API documentation
- Markdown support in docstrings
- Function signatures
- Example code
- Searchable HTML
- Customizable output
- Handles namespaces

## When to Use

- Creating library documentation
- Generating API references
- Sharing code with others
- Maintaining technical documentation

## When NOT to Use

- Application code documentation (use README)

## Common Patterns

```clojure
; Library namespace with documentation
(ns ^{:doc "User management module
           
           This namespace handles all user-related operations
           including creation, deletion, and updates."}
    my.lib.users
  (:require [my.lib.database :as db]))

(defn create-user
  "Creates a new user in the system.
   
   This function validates input and stores the user in the database.
   
   Parameters:
     name - User's full name (string)
     email - User's email address (string)
   
   Returns:
     A map with :id, :name, :email, :created-at
   
   Throws:
     IllegalArgumentException if name or email is invalid
   
   Example:
     (create-user \"Alice\" \"alice@example.com\")
     ; => {:id 1, :name \"Alice\", :email \"alice@example.com\", :created-at ...}"
  [name email]
  (db/insert-user {:name name :email email}))
```

## Related Libraries

- hiccup/hiccup - HTML generation

## Resources

- Official Documentation: https://github.com/weavejester/codox
- API Documentation: https://cljdoc.org/d/codox/codox

## Notes

This project uses Codox for generating documentation from source code docstrings.
