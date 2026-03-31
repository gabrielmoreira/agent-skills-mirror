---
name: uberdeps_uberjar_builder
description: Build tool for creating executable uberjar files.
---

# uberdeps

A simple tool for building uberjars (executable JAR files) from Clojure projects.

## Overview

uberdeps packages your application and all its dependencies into a single executable JAR file, making deployment straightforward.

## Core Concepts

**Building Uberjars**: Create executable JAR files.

```clojure
; In terminal:
; clojure -X:uberdeps

; In deps.edn:
; :uberdeps {:replace-deps {uberdeps/uberdeps {:mvn/version "1.4.0"}}
;            :replace-paths []
;            :main-opts ["-m" "uberdeps.uberjar"]}
```

**Configuration**: Customize build settings.

```clojure
; In uberdeps.edn or deps.edn:
{:aliases
 {:uberdeps {:main-opts ["-m" "uberdeps.uberjar"
                         "--alias" "myapp"
                         "--output" "target/myapp.jar"]}}}
```

## Key Features

- Simple uberjar building
- Manifest configuration
- Class path assembly
- Dependency inclusion
- Minimal configuration
- Fast builds

## When to Use

- Deployment of applications
- Distribution of standalone tools
- CI/CD builds
- Containerization

## When NOT to Use

- Development (regular CLI preferred)

## Common Patterns

```clojure
; In bb.edn:
; Build uberjar
; clojure -X:uberdeps

; Example deployment:
; 1. Build: clojure -X:uberdeps
; 2. Result: target/myapp.jar
; 3. Deploy: java -jar target/myapp.jar

; With main entry point in deps.edn:
; :main {:main-opts ["-m" "my.app.main"]}

; Build and execute:
; clojure -X:uberdeps
; java -jar target/myapp.jar arg1 arg2
```

## Related Libraries

- clojure/tools.build - Advanced build tool

## Resources

- Official Documentation: https://github.com/tonsky/uberdeps
- API Documentation: https://cljdoc.org/d/uberdeps/uberdeps

## Notes

This project uses uberdeps for building executable JAR files for distribution.
