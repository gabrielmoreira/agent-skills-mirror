---
name: nrepl_network_repl_server
description: |
  Network REPL protocol for remote Clojure code evaluation and interactive development.
  Use when building IDE integrations, remote debugging, editor REPL connections, embedding
  REPL servers in applications, or when the user mentions nREPL, network REPL, remote REPL,
  CIDER, Calva, editor integration, REPL server, or networked evaluation.
---

# nREPL

A Clojure network REPL that provides a server and client, along with common APIs for IDEs and tools that need to evaluate Clojure code in remote environments.

## Quick Start

Start an nREPL server and connect from any client:

```clojure
;; Start server (programmatically)
(require '[nrepl.server :refer [start-server stop-server]])
(defonce server (start-server :port 7888))
;; => #'user/server

;; Or via command line
;; clj -M:nrepl -m nrepl.cmdline --port 7888
;; lein repl :headless :port 7888

;; Connect from another process
(require '[nrepl.core :as nrepl])
(with-open [conn (nrepl/connect :port 7888)]
  (-> (nrepl/client conn 1000)
      (nrepl/message {:op "eval" :code "(+ 1 2 3)"})
      nrepl/response-values))
;; => [6]

;; Stop server
(stop-server server)
```

**Key benefits:**
- Network-based REPL for remote development
- Foundation for editor integrations (CIDER, Calva, Cursive)
- Middleware-based extensibility
- Supports multiple concurrent sessions
- Transport abstraction (bencode, tty, custom)

## Core Concepts

### Message-Based Protocol

nREPL is fundamentally message-oriented and asynchronous. Clients send request messages and receive response messages:

```clojure
;; Request message
{:op "eval"
 :code "(+ 1 2 3)"
 :session "abc-123"
 :id "msg-456"}

;; Response messages
{:value "6"
 :session "abc-123"
 :id "msg-456"}

{:status ["done"]
 :session "abc-123"
 :id "msg-456"}
```

**Key properties:**
- Messages are maps with keyword keys
- `:op` specifies the operation
- `:session` identifies the evaluation context
- `:id` correlates requests with responses
- Multiple responses possible per request

### Transports

Transports implement the communication protocol. nREPL includes:

```clojure
;; Bencode transport (default, binary)
(nrepl/connect :port 7888)
;; Uses nrepl.transport/bencode

;; TTY transport (telnet-compatible, text)
(require '[nrepl.server :refer [start-server]])
(start-server 
  :port 7888
  :transport-fn #(nrepl.transport/tty % {}))

;; Connect via telnet
;; telnet localhost 7888
```

**Available transports:**
- `bencode` - Default, efficient binary format
- `tty` - Text-based for telnet/netcat
- Custom transports can be implemented

### Middleware

Middleware compose to create the server's handler. They can intercept and modify messages:

```clojure
(require '[nrepl.server :refer [default-handler]])

;; Start with default middleware
(def handler (default-handler))

;; Or add custom middleware
(defn logging-middleware [handler]
  (fn [{:keys [op] :as msg}]
    (println "Operation:" op)
    (handler msg)))

(def custom-handler 
  (default-handler #'logging-middleware))

(start-server :port 7888 :handler custom-handler)
```

**Default middleware provides:**
- Code evaluation (`eval`)
- Session management
- Interrupts
- Code loading (`load-file`)
- Completion
- Documentation lookup
- stdin handling

### Sessions

Sessions provide isolated evaluation contexts:

```clojure
(require '[nrepl.core :as nrepl])

(with-open [conn (nrepl/connect :port 7888)]
  (let [client (nrepl/client conn 1000)]
    ;; Create a new session
    (def session-id (nrepl/new-session client))
    
    ;; Use session-specific client
    (let [sess-client (nrepl/client-session client :session session-id)]
      ;; Evaluations share state within session
      (sess-client {:op "eval" :code "(def x 42)"})
      (-> (sess-client {:op "eval" :code "x"})
          nrepl/response-values))
    ;; => [42]
    
    ;; x doesn't exist in other sessions
    (-> (client {:op "eval" :code "x"})
        nrepl/response-values)))
;; => Exception: Unable to resolve symbol: x
```

## Common Workflows

### Workflow 1: Starting a Server

**Via Command Line (Clojure CLI):**

```clojure
;; Add to ~/.clojure/deps.edn
{:aliases 
 {:nrepl 
  {:extra-deps {nrepl/nrepl {:mvn/version "1.3.0"}}}}}

;; Start server
;; clj -M:nrepl -m nrepl.cmdline --port 7888
;; clj -M:nrepl -m nrepl.cmdline --socket /tmp/nrepl.sock  ;; Unix socket
```

**Via Leiningen:**

```clojure
;; Start with REPL-y client
;; lein repl

;; Start headless
;; lein repl :headless :port 7888
;; lein repl :headless :socket /tmp/nrepl.sock
```

**Programmatically (Embedding):**

```clojure
(require '[nrepl.server :refer [start-server stop-server]])

;; Basic server
(defonce server (start-server :port 7888))

;; Bind to specific address
(defonce server (start-server 
                  :bind "172.18.0.5" 
                  :port 4001))

;; Unix domain socket (more secure)
(defonce server (start-server 
                  :socket "/some/where/safe/nrepl"))

;; With custom handler
(defonce server (start-server 
                  :port 7888
                  :handler (default-handler #'my.middleware/wrap-something)))

;; Stop server
(stop-server server)
```

### Workflow 2: Connecting as a Client

```clojure
(require '[nrepl.core :as nrepl])

;; TCP connection
(with-open [conn (nrepl/connect :port 7888)]
  (let [client (nrepl/client conn 1000)]  ;; 1000ms timeout
    ;; Send message, get responses
    (-> (client {:op "eval" :code "(+ 1 2 3)"})
        nrepl/response-values)))
;; => [6]

;; Unix socket connection
(with-open [conn (nrepl/connect :socket "/tmp/nrepl.sock")]
  (let [client (nrepl/client conn 1000)]
    (nrepl/response-values 
      (client {:op "eval" :code "(range 5)"}))))
;; => [(0 1 2 3 4)]

;; Process full response messages
(with-open [conn (nrepl/connect :port 7888)]
  (let [client (nrepl/client conn 1000)]
    (doall (client {:op "eval" :code "(println \"Hello\")"}))))
;; => ({:out "Hello\n" :session "..." :id "..."}
;;     {:ns "user" :value "nil" :session "..." :id "..."}
;;     {:status ["done"] :session "..." :id "..."})
```

### Workflow 3: Using Sessions

```clojure
(require '[nrepl.core :as nrepl])

(with-open [conn (nrepl/connect :port 7888)]
  (let [client (nrepl/client conn 1000)
        session-id (nrepl/new-session client)]
    
    ;; Create session-specific client
    (let [sess (nrepl/client-session client :session session-id)]
      ;; State is preserved within session
      (sess {:op "eval" :code "(def x 100)"})
      (sess {:op "eval" :code "(def y 200)"})
      (nrepl/response-values 
        (sess {:op "eval" :code "(+ x y)"})))
    ;; => [300]
    
    ;; Clone existing session
    (let [cloned-id (nrepl/new-session client :clone session-id)
          cloned (nrepl/client-session client :session cloned-id)]
      ;; Cloned session has same state
      (nrepl/response-values 
        (cloned {:op "eval" :code "x"})))))
;; => [100]
```

### Workflow 4: Custom Middleware

```clojure
(require '[nrepl.middleware :refer [set-descriptor!]]
         '[nrepl.server :refer [default-handler start-server]]
         '[nrepl.transport :as transport])

;; Define middleware
(defn timing-middleware [handler]
  (fn [{:keys [op transport] :as msg}]
    (let [start (System/currentTimeMillis)
          result (handler msg)
          elapsed (- (System/currentTimeMillis) start)]
      (when (= op "eval")
        (transport/send transport 
          {:timing elapsed 
           :session (:session msg)
           :id (:id msg)}))
      result)))

;; Add descriptor (optional, for documentation)
(set-descriptor! #'timing-middleware
  {:expects #{"eval"}
   :handles {}})

;; Use middleware
(def handler (default-handler #'timing-middleware))
(start-server :port 7888 :handler handler)
```

### Workflow 5: Loading Files

```clojure
(require '[nrepl.core :as nrepl]
         '[clojure.java.io :as io])

(with-open [conn (nrepl/connect :port 7888)]
  (let [client (nrepl/client conn 5000)
        file-content (slurp "src/my_app/core.clj")
        file-path "src/my_app/core.clj"]
    
    ;; Load file
    (-> (client {:op "load-file" 
                 :file file-content
                 :file-path file-path
                 :file-name "core.clj"})
        nrepl/combine-responses)))
;; => {:status #{:done}, :ns "my-app.core", ...}
```

### Workflow 6: Interrupting Evaluation

```clojure
(require '[nrepl.core :as nrepl])

(with-open [conn (nrepl/connect :port 7888)]
  (let [client (nrepl/client conn 1000)
        sess-id (nrepl/new-session client)
        sess (nrepl/client-session client :session sess-id)]
    
    ;; Start long-running evaluation
    (future
      (sess {:op "eval" :code "(Thread/sleep 60000)"}))
    
    ;; Wait a bit
    (Thread/sleep 100)
    
    ;; Send interrupt
    (client {:op "interrupt" :session sess-id})))
;; Long evaluation will be interrupted
```

### Workflow 7: Embedding in Java Applications

```java
import clojure.java.api.Clojure;
import clojure.lang.IFn;

public class App {
    public static void main(String[] args) {
        // Require nREPL
        IFn require = Clojure.var("clojure.core", "require");
        require.invoke(Clojure.read("nrepl.server"));
        
        // Start server
        IFn start = Clojure.var("nrepl.server", "start-server");
        int port = 7888;
        Object server = start.invoke(
            Clojure.read(":port"), 
            Clojure.read(Integer.toString(port)));
        
        System.out.println("nREPL server started on port " + port);
        
        // Stop server later
        // IFn stop = Clojure.var("nrepl.server", "stop-server");
        // stop.invoke(server);
    }
}
```

### Workflow 8: Configuration Files

**Global configuration** (`~/.nrepl/nrepl.edn`):

```clojure
{:bind "localhost"
 :transport nrepl.transport/bencode
 :middleware [some.ns/my-middleware]}
```

**Project configuration** (`.nrepl.edn` in project root):

```clojure
{:port 12345
 :bind "localhost"
 :handler some.ns/custom-handler}
```

**Dynamic variable defaults**:

```clojure
;; In ~/.nrepl/nrepl.edn
{:dynamic-vars {clojure.core/*warn-on-reflection* true
                clojure.core/*print-length* 100}}
```

## When to Use Each Approach

**Use TCP sockets when:**
- Connecting from remote machines
- Standard editor integration
- Need network transparency
- Traditional REPL workflow

**Use Unix domain sockets when:**
- Local development only
- Enhanced security (no network exposure)
- Better performance (no routing overhead)
- POSIX-based access control

**Use embedded server when:**
- Deploying applications to production
- Need runtime debugging capability
- Dynamic code patching required
- Remote monitoring and introspection

**Use command-line start when:**
- Interactive development
- Quick REPL sessions
- Editor integration
- Standard tooling workflows

## Best Practices

**DO:**
- Use Unix sockets for local development (more secure)
- Bind to `localhost` when using TCP ports
- Use sessions to isolate evaluation contexts
- Stop servers properly with `stop-server`
- Add authentication for production deployments
- Use timeouts on client connections
- Configure middleware via deps.edn or project.clj
- Use `:port 0` to auto-select available port
- Leverage configuration files for consistent setup

**DON'T:**
- Expose nREPL on public networks without authentication
- Share sessions between different clients carelessly
- Bind to `0.0.0.0` without understanding security implications
- Forget to handle connection errors
- Use blocking operations in middleware
- Ignore session cleanup
- Hard-code ports in production
- Skip timeout configuration on clients

## Common Issues

### Issue: "Connection Refused"

**Problem:** Cannot connect to nREPL server

```clojure
;; Connection fails
(nrepl/connect :port 7888)
;; => java.net.ConnectException: Connection refused
```

**Solution:** Check server is running and port/host are correct

```clojure
;; Verify server is running
;; lsof -i :7888
;; netstat -an | grep 7888

;; Check host binding
(start-server :bind "127.0.0.1" :port 7888)  ;; Local only
(start-server :bind "0.0.0.0" :port 7888)    ;; All interfaces (dangerous!)

;; Check firewall rules if remote connection
```

### Issue: "Evaluation Timeout"

**Problem:** Operations take too long and timeout

```clojure
(with-open [conn (nrepl/connect :port 7888)]
  (let [client (nrepl/client conn 1000)]  ;; 1 second timeout
    (client {:op "eval" :code "(Thread/sleep 5000)"})))
;; => Timeout waiting for response
```

**Solution:** Increase timeout or use async evaluation

```clojure
;; Increase timeout
(let [client (nrepl/client conn 10000)]  ;; 10 seconds
  (client {:op "eval" :code "(Thread/sleep 5000)"}))

;; Or use async (no timeout on response-seq)
(let [responses (nrepl/response-seq conn)]
  ;; Process responses as they arrive
  (doseq [resp responses]
    (println resp)))
```

### Issue: "Session State Lost"

**Problem:** Definitions disappear between evaluations

```clojure
(let [client (nrepl/client conn 1000)]
  (client {:op "eval" :code "(def x 42)"})
  (nrepl/response-values 
    (client {:op "eval" :code "x"})))
;; => Exception: Unable to resolve symbol: x
```

**Solution:** Use session-specific client

```clojure
;; Create and use a session
(let [client (nrepl/client conn 1000)
      session-id (nrepl/new-session client)
      sess (nrepl/client-session client :session session-id)]
  ;; Now state persists
  (sess {:op "eval" :code "(def x 42)"})
  (nrepl/response-values 
    (sess {:op "eval" :code "x"})))
;; => [42]
```

### Issue: "Unknown Op"

**Problem:** Operation not supported by server

```clojure
(client {:op "custom-operation" :arg "value"})
;; => {:status ["unknown-op" "done"], ...}
```

**Solution:** Ensure required middleware is loaded

```clojure
;; Check available ops
(-> (client {:op "describe"})
    nrepl/combine-responses
    :ops
    keys)

;; Add middleware that provides the op
(def handler (default-handler #'my.middleware/custom-op))
(start-server :port 7888 :handler handler)
```

### Issue: "Permission Denied" (Unix Sockets)

**Problem:** Cannot connect to Unix socket

```clojure
(nrepl/connect :socket "/tmp/nrepl.sock")
;; => java.io.IOException: Permission denied
```

**Solution:** Check socket file permissions and parent directory

```bash
# Make directory accessible
mkdir -m 700 /tmp/safe-nrepl

# Start server there
# clj -M:nrepl -m nrepl.cmdline --socket /tmp/safe-nrepl/socket

# Connect
(nrepl/connect :socket "/tmp/safe-nrepl/socket")
```

## Advanced Topics

### Built-in Operations

nREPL's default middleware provides many operations beyond `eval`:

- `describe` - List available operations and versions
- `eval` - Evaluate code
- `load-file` - Load and evaluate a file
- `interrupt` - Interrupt running evaluation
- `stdin` - Provide input to *in*
- `clone` - Clone session
- `close` - Close session
- `ls-sessions` - List active sessions
- `completions` - Code completion
- `lookup` - Symbol lookup/documentation

See [nREPL's ops documentation](https://nrepl.org/nrepl/ops.html) for complete list.

### TLS/SSL Support

```clojure
;; Start TLS server
(start-server 
  :port 7888
  :tls? true
  :tls-keys-file "path/to/keystore.jks")

;; Connect with TLS
(with-open [conn (nrepl/connect 
                   :port 7888
                   :tls-keys-file "path/to/keystore.jks")]
  (let [client (nrepl/client conn 1000)]
    (nrepl/response-values 
      (client {:op "eval" :code "(+ 1 2)"}))))
```

### Custom Transports

Implement `nrepl.transport/Transport` protocol for custom communication channels (HTTP, WebSockets, message queues, etc.).

## Resources

- Official Documentation: https://nrepl.org
- API Docs: https://cljdoc.org/d/nrepl/nrepl/CURRENT
- GitHub: https://github.com/nrepl/nrepl
- Building Middleware: https://nrepl.org/nrepl/building_middleware.html
- Building Servers: https://nrepl.org/nrepl/building_servers.html
- Building Clients: https://nrepl.org/nrepl/building_clients.html

## Editor Integration

- **CIDER** (Emacs): https://docs.cider.mx/
- **Calva** (VSCode): https://calva.io/
- **Cursive** (IntelliJ): https://cursive-ide.com/
- **vim-fireplace** (Vim): https://github.com/tpope/vim-fireplace
- **Conjure** (Neovim): https://github.com/Olical/conjure

## Summary

nREPL is the foundation of Clojure's networked REPL ecosystem:

- **Message-based** - Asynchronous request/response protocol
- **Extensible** - Middleware architecture for custom functionality
- **Session-based** - Isolated evaluation contexts
- **Transport-agnostic** - Bencode, TTY, or custom transports
- **Editor-friendly** - Powers CIDER, Calva, Cursive, and more
- **Embeddable** - Add REPL server to any application
- **Secure options** - Unix sockets, TLS, localhost binding

Use nREPL for remote development, editor integration, production debugging, and any scenario requiring networked access to a Clojure runtime.
