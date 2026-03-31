---
name: component_lifecycle_management
description: Lifecycle management library for stateful components in Clojure applications.
---

# Component

A library for building applications with stateful components and managing their lifecycles.

## Overview

Component provides abstractions for managing the lifecycle of system components. It handles initialization and cleanup in the right order, enabling cleaner application architecture.

## Core Concepts

**Component**: A stateful unit with initialization and cleanup.

```clojure
(require '[com.stuartsierra.component :as component])

(defrecord Database [connection config]
  component/Lifecycle
  (start [this]
    (println "Starting database")
    (let [conn (connect (:db-url config))]
      (assoc this :connection conn)))
  (stop [this]
    (println "Stopping database")
    (when connection (close connection))
    this))
```

**System**: A collection of components and their dependencies.

```clojure
(defn system-map [config]
  (component/system-map
    :database (map->Database {:config config})
    :web-server (component/using
                  (map->WebServer {})
                  [:database])))

; Start all components in dependency order
(def running-system (component/start (system-map config)))

; Stop all components in reverse order
(component/stop running-system)
```

## Key Features

- Declarative component dependencies
- Automatic startup/shutdown ordering
- Reloadable components for development
- Testing support (easy to construct systems)
- Simple Lifecycle protocol
- System introspection

## When to Use

- Managing database connections
- Server lifecycle management
- Complex application initialization
- Testing with real components

## When NOT to Use

- Simple applications without state
- When a simpler dependency injection suffices

## Common Patterns

```clojure
; Component definition
(defrecord WebServer [port database handler server]
  component/Lifecycle
  (start [this]
    (let [handler (create-handler database)
          server (start-server port handler)]
      (assoc this :handler handler :server server)))
  (stop [this]
    (when server (stop-server server))
    (assoc this :handler nil :server nil)))

; Application initialization
(defn -main [& args]
  (let [config (load-config)
        sys (system-map config)
        running-sys (component/start sys)]
    (.addShutdownHook (Runtime/getRuntime)
      (fn [] (component/stop running-sys)))))
```

## Related Libraries

- com.stuartsierra/component.repl - REPL integration for reloading
- io.github.tonsky/clj-reload - Hot code reloading

## Resources

- Official Documentation: https://github.com/stuartsierra/component
- API Documentation: https://cljdoc.org/d/com.stuartsierra/component

## Notes

This project uses Component for managing database and server lifecycle.
