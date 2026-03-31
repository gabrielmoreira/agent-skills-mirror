---
name: clojure_mcp_light_nrepl_cli
description: |
  Command-line nREPL evaluation tool with automatic delimiter repair for Claude Code integration.
  Use when evaluating Clojure code via nREPL from command line, REPL-driven development workflows,
  Claude Code Clojure integration, or when the user mentions clj-nrepl-eval, nREPL CLI, command-line
  REPL evaluation, automatic delimiter fixing, or Claude Code hooks for Clojure.
---

# clojure-mcp-light

A minimal CLI tooling suite for Clojure development with Claude Code providing automatic delimiter fixing and nREPL command-line evaluation.

## Quick Start

Install via bbin and start using immediately:

```bash
# Install both tools via bbin
bbin install https://github.com/bhauman/clojure-mcp-light.git --tag v0.2.0

bbin install https://github.com/bhauman/clojure-mcp-light.git --tag v0.2.0 \
  --as clj-nrepl-eval \
  --main-opts '["-m" "clojure-mcp-light.nrepl-eval"]'

# Discover running nREPL servers
clj-nrepl-eval --discover-ports

# Evaluate Clojure code via nREPL
clj-nrepl-eval -p 7889 "(+ 1 2 3)"
# => 6

# Automatic delimiter repair
clj-nrepl-eval -p 7889 "(+ 1 2 3"
# => 6  (automatically fixed missing delimiter)

# Check connected sessions
clj-nrepl-eval --connected-ports
```

**Key benefits:**
- Instant nREPL evaluation from command line
- Automatic delimiter repair before evaluation
- Persistent sessions across invocations
- Server discovery (finds .nrepl-port files and running processes)
- Connection tracking (remembers which servers you've used)
- Intelligent backend selection (parinfer-rust or parinferish)
- No MCP server needed (works with standard Claude Code tools)

## Core Concepts

### Command-Line nREPL Client

`clj-nrepl-eval` is a babashka-based CLI tool that communicates with nREPL servers using the bencode protocol:

```bash
# Evaluate code with automatic delimiter repair
clj-nrepl-eval -p 7889 "(+ 1 2 3)"

# Automatic delimiter fixing before evaluation
clj-nrepl-eval -p 7889 "(defn add [x y] (+ x y"
# Automatically repairs to: (defn add [x y] (+ x y))

# Pipe code via stdin
echo "(println \"Hello\")" | clj-nrepl-eval -p 7889

# Multi-line code via heredoc
clj-nrepl-eval -p 7889 <<'EOF'
(def x 10)
(def y 20)
(+ x y)
EOF
```

**How it works:**
- Detects delimiter errors using edamame parser
- Repairs delimiters with parinfer-rust (if available) or parinferish
- Sends repaired code to nREPL server via bencode protocol
- Handles timeouts and interrupts
- Maintains persistent sessions per host:port

### Automatic Delimiter Repair

Both tools use intelligent delimiter fixing:

```clojure
;; Before repair (missing closing delimiter)
(defn broken [x]
  (let [result (* x 2]
    result))

;; After automatic repair
(defn broken [x]
  (let [result (* x 2)]
    result))
```

**Repair backends:**
- **parinfer-rust** - Preferred when available (faster, battle-tested)
- **parinferish** - Pure Clojure fallback (no external dependencies)

The tool automatically selects the best available backend.

### Session Persistence

Sessions persist across command invocations:

```bash
# Define a var in one invocation
clj-nrepl-eval -p 7889 "(def x 42)"

# Use it in another invocation (same session)
clj-nrepl-eval -p 7889 "(* x 2)"
# => 84

# Reset session if needed
clj-nrepl-eval -p 7889 --reset-session
```

**Session files stored in:**
- `~/.clojure-mcp-light/sessions/`
- Separate file per host:port combination
- Cleaned up when nREPL server restarts

### Server Discovery

Find running nREPL servers without guessing ports:

```bash
# Discover servers in current directory
clj-nrepl-eval --discover-ports
# Discovered nREPL servers in current directory (/path/to/project):
#   localhost:7889 (bb)
#   localhost:55077 (clj)
#
# Total: 2 servers in current directory

# Check previously connected sessions
clj-nrepl-eval --connected-ports
# Active nREPL connections:
#   127.0.0.1:7889 (session: abc123...)
#
# Total: 1 active connection
```

**Discovery methods:**
- Reads `.nrepl-port` files in current directory
- Scans running JVM processes for nREPL servers
- Checks Babashka nREPL processes

## Common Workflows

### Workflow 1: Basic REPL-Driven Development

Start a server and evaluate code from command line:

```bash
# 1. Start an nREPL server
# Using Clojure CLI
clj -Sdeps '{:deps {nrepl/nrepl {:mvn/version "1.3.0"}}}' -M -m nrepl.cmdline

# Using Babashka
bb nrepl-server 7889

# Using Leiningen
lein repl :headless

# 2. Discover the server
clj-nrepl-eval --discover-ports

# 3. Evaluate code
clj-nrepl-eval -p 7889 "(+ 1 2 3)"
# => 6

# 4. Build up state incrementally
clj-nrepl-eval -p 7889 "(defn add [x y] (+ x y))"
clj-nrepl-eval -p 7889 "(add 10 20)"
# => 30

# 5. Load and test a namespace
clj-nrepl-eval -p 7889 "(require '[my.app.core :as core])"
clj-nrepl-eval -p 7889 "(core/my-function test-data)"
```

### Workflow 2: Working with Delimiter Errors

Let the tool automatically fix common delimiter mistakes:

```bash
# Missing closing paren
clj-nrepl-eval -p 7889 "(defn add [x y] (+ x y"
# Automatically fixed to: (defn add [x y] (+ x y))
# => #'user/add

# Mismatched delimiters
clj-nrepl-eval -p 7889 "[1 2 3)"
# Automatically fixed to: [1 2 3]
# => [1 2 3]

# Nested delimiter errors
clj-nrepl-eval -p 7889 "(let [x 10
                              y (+ x 5
                          (println y))"
# Automatically repaired and evaluated

# Check what was fixed (if logging enabled)
clj-nrepl-eval -p 7889 --log-level debug "(defn broken [x] (+ x 1"
```

### Workflow 3: Multi-Line Code Evaluation

Handle complex multi-line expressions:

```bash
# Using heredoc
clj-nrepl-eval -p 7889 <<'EOF'
(defn factorial [n]
  (if (<= n 1)
    1
    (* n (factorial (dec n)))))

(factorial 5)
EOF
# => 120

# From a file
cat src/my_app/core.clj | clj-nrepl-eval -p 7889

# With delimiter repair
clj-nrepl-eval -p 7889 <<'EOF'
(defn broken [x]
  (let [result (* x 2]
    result))
EOF
# Automatically fixed before evaluation
```

### Workflow 4: Session Management

Control evaluation context across invocations:

```bash
# Build up state in session
clj-nrepl-eval -p 7889 "(def config {:host \"localhost\" :port 8080})"
clj-nrepl-eval -p 7889 "(def db-conn (connect-db config))"
clj-nrepl-eval -p 7889 "(query db-conn \"SELECT * FROM users\")"

# Check active sessions
clj-nrepl-eval --connected-ports
# Active nREPL connections:
#   127.0.0.1:7889 (session: abc123...)

# Reset if state becomes corrupted
clj-nrepl-eval -p 7889 --reset-session

# Continue with fresh session
clj-nrepl-eval -p 7889 "(def x 1)"
```

### Workflow 5: Timeout Handling

Configure timeouts for long-running operations:

```bash
# Default timeout (120 seconds)
clj-nrepl-eval -p 7889 "(Thread/sleep 5000)"
# Completes normally

# Custom timeout (5 seconds)
clj-nrepl-eval -p 7889 --timeout 5000 "(Thread/sleep 10000)"
# ERROR: Timeout after 5000ms

# For interactive operations
clj-nrepl-eval -p 7889 --timeout 300000 "(run-comprehensive-tests)"
# 5 minute timeout for test suite
```

### Workflow 6: Working Across Multiple Projects

Manage connections to different nREPL servers:

```bash
# In project A
cd ~/projects/project-a
clj-nrepl-eval --discover-ports
# localhost:7889 (bb)

clj-nrepl-eval -p 7889 "(require '[project-a.core :as a])"
clj-nrepl-eval -p 7889 "(a/process-data data)"

# Switch to project B
cd ~/projects/project-b
clj-nrepl-eval --discover-ports
# localhost:7890 (clj)

clj-nrepl-eval -p 7890 "(require '[project-b.core :as b])"
clj-nrepl-eval -p 7890 "(b/analyze-results)"

# Check all active connections
clj-nrepl-eval --connected-ports
# Active nREPL connections:
#   127.0.0.1:7889 (session: abc123...)
#   127.0.0.1:7890 (session: xyz789...)
```

### Workflow 7: Claude Code Integration Pattern

Use clj-nrepl-eval as part of Claude Code workflows:

```markdown
# User: "Can you test if the add function works?"

# Agent uses clj-nrepl-eval to test interactively:

1. Load the namespace:
```bash
clj-nrepl-eval -p 7889 "(require '[my.app.math :reload] :as math)"
```

2. Test the function:
```bash
clj-nrepl-eval -p 7889 "(math/add 2 3)"
# => 5
```

3. Test edge cases:
```bash
clj-nrepl-eval -p 7889 "(math/add 0 0)"
# => 0

clj-nrepl-eval -p 7889 "(math/add -5 10)"
# => 5

clj-nrepl-eval -p 7889 "(math/add nil 5)"
# => NullPointerException (expected, now we know to add validation)
```

4. Report findings back to user with recommendations
```

## When to Use clj-nrepl-eval

**Use clj-nrepl-eval when:**
- Evaluating Clojure code from command line in Claude Code
- Testing functions interactively without opening an editor
- Building REPL-driven development workflows
- Need automatic delimiter repair before evaluation
- Working with multiple nREPL servers across projects
- Scripting Clojure evaluations in shell scripts
- Quick experimentation with code snippets
- Verifying code changes immediately after edits

**Use other tools when:**
- Need full IDE integration → Use CIDER, Calva, or Cursive
- Want comprehensive MCP server features → Use ClojureMCP
- Need more than evaluation → Use clojure-lsp for refactoring, formatting, etc.
- Writing long-form code → Use proper editor with REPL integration

## Best Practices

**DO:**
- Use `--discover-ports` to find nREPL servers automatically
- Check `--connected-ports` to see active sessions
- Reset sessions with `--reset-session` when state is unclear
- Use appropriate timeouts for long operations
- Leverage automatic delimiter repair for quick fixes
- Test code incrementally (small expressions first)
- Build up state in sessions for complex workflows
- Use heredocs for multi-line code blocks

**DON'T:**
- Hard-code ports (use discovery instead)
- Assume sessions persist forever (nREPL restart clears them)
- Skip delimiter repair validation (check if code makes sense)
- Use very short timeouts for complex operations
- Evaluate untrusted code without sandboxing
- Forget to reload namespaces after file changes
- Mix unrelated state in the same session
- Ignore evaluation errors

## Common Issues

### Issue: "Connection Refused"

**Problem:** Cannot connect to nREPL server

```bash
clj-nrepl-eval -p 7888 "(+ 1 2 3)"
# Error: Connection refused
```

**Solution:** Check if server is running and port is correct

```bash
# 1. Verify no server is running
clj-nrepl-eval --discover-ports
# No servers found

# 2. Start a server
bb nrepl-server 7889

# 3. Verify discovery
clj-nrepl-eval --discover-ports
# localhost:7889 (bb)

# 4. Try again with correct port
clj-nrepl-eval -p 7889 "(+ 1 2 3)"
# => 6
```

### Issue: "Timeout Waiting for Response"

**Problem:** Evaluation times out

```bash
clj-nrepl-eval -p 7889 "(Thread/sleep 150000)"
# ERROR: Timeout after 120000ms
```

**Solution:** Increase timeout for long operations

```bash
# Use longer timeout (in milliseconds)
clj-nrepl-eval -p 7889 --timeout 180000 "(Thread/sleep 150000)"
# Completes successfully

# Or use dedicated timeout for specific operations
clj-nrepl-eval -p 7889 --timeout 600000 "(run-comprehensive-test-suite)"
```

### Issue: "Undefined Var After Definition"

**Problem:** Vars defined in one invocation not found in next

```bash
clj-nrepl-eval -p 7889 "(def x 42)"
clj-nrepl-eval -p 7889 "x"
# Error: Unable to resolve symbol: x
```

**Solution:** This usually means different sessions or server restart

```bash
# Check if you have active session
clj-nrepl-eval --connected-ports
# Active nREPL connections: (none)

# Session was lost (server restarted)
# Redefine vars:
clj-nrepl-eval -p 7889 "(def x 42)"
clj-nrepl-eval -p 7889 "x"
# => 42

# Or use same invocation
clj-nrepl-eval -p 7889 "(do (def x 42) x)"
# => 42
```

### Issue: "Delimiter Repair Not Working"

**Problem:** Code still has delimiter errors after repair

```bash
clj-nrepl-eval -p 7889 "((("
# Still shows delimiter error
```

**Solution:** Some errors can't be automatically repaired

```bash
# Repair works for balanced but mismatched delimiters
clj-nrepl-eval -p 7889 "[1 2 3)"  # Fixed to [1 2 3]

# Repair works for missing closing delimiters
clj-nrepl-eval -p 7889 "(+ 1 2"   # Fixed to (+ 1 2)

# But can't repair meaningless expressions
clj-nrepl-eval -p 7889 "((("      # Too ambiguous

# Write valid Clojure expressions for best results
clj-nrepl-eval -p 7889 "(+ 1 2 3"  # This repairs successfully
```

### Issue: "Wrong Host or Port"

**Problem:** Trying to connect to wrong server

```bash
clj-nrepl-eval -p 7888 "(+ 1 2)"
# Connection refused (wrong port)
```

**Solution:** Use discovery to find correct port

```bash
# Find running servers
clj-nrepl-eval --discover-ports
# Discovered nREPL servers in current directory:
#   localhost:7889 (bb)

# Use discovered port
clj-nrepl-eval -p 7889 "(+ 1 2)"
# => 3

# For remote hosts, specify explicitly
clj-nrepl-eval --host 192.168.1.100 --port 7889 "(+ 1 2)"
```

### Issue: "Session State Confusion"

**Problem:** Session has unexpected state from previous work

```bash
clj-nrepl-eval -p 7889 "(def x 100)"
# Later...
clj-nrepl-eval -p 7889 "x"
# => 100 (but you expected fresh session)
```

**Solution:** Reset session when starting new work

```bash
# Reset to clean state
clj-nrepl-eval -p 7889 --reset-session

# Verify x is undefined
clj-nrepl-eval -p 7889 "x"
# Error: Unable to resolve symbol: x

# Start fresh
clj-nrepl-eval -p 7889 "(def x 1)"
```

## Advanced Topics

### Parinfer Backend Selection

The tool automatically selects the best delimiter repair backend:

```bash
# With parinfer-rust installed (preferred)
which parinfer-rust
# /usr/local/bin/parinfer-rust

# Falls back to parinferish if parinfer-rust not available
# Both provide equivalent functionality for delimiter repair
```

**Installing parinfer-rust (optional but recommended):**

```bash
# macOS via Homebrew
brew install parinfer-rust

# Or from source
# https://github.com/eraserhd/parinfer-rust
```

### Custom nREPL Middleware

clj-nrepl-eval works with any nREPL server, including those with custom middleware:

```bash
# Start server with custom middleware
clj -M:dev:nrepl -m nrepl.cmdline \
  --middleware '[my.middleware/wrap-custom]'

# Evaluate code normally
clj-nrepl-eval -p 7889 "(+ 1 2)"
# Custom middleware sees and processes the request
```

### Scripting with clj-nrepl-eval

Use in shell scripts for automation:

```bash
#!/bin/bash
# Script: run-tests.sh

# Start nREPL if not running
if ! clj-nrepl-eval --discover-ports | grep -q "7889"; then
  echo "Starting nREPL..."
  bb nrepl-server 7889 &
  sleep 2
fi

# Load test namespace
clj-nrepl-eval -p 7889 "(require '[my.app.test-runner :reload])"

# Run tests
clj-nrepl-eval -p 7889 "(my.app.test-runner/run-all-tests)"

# Exit with test status
exit $?
```

### Integration with Other Tools

Combine with other command-line tools:

```bash
# Format code, then evaluate
cat src/core.clj | cljfmt | clj-nrepl-eval -p 7889

# Generate test data and evaluate
echo '(range 10)' | clj-nrepl-eval -p 7889 | jq '.value'

# Evaluate multiple expressions from file
while read -r expr; do
  clj-nrepl-eval -p 7889 "$expr"
done < expressions.txt
```

## Resources

- GitHub Repository: https://github.com/bhauman/clojure-mcp-light
- nREPL Documentation: https://nrepl.org
- parinfer-rust: https://github.com/eraserhd/parinfer-rust
- parinferish: https://github.com/oakmac/parinferish
- Babashka: https://babashka.org
- bbin: https://github.com/babashka/bbin

## Related Tools

- **ClojureMCP** - Full MCP server with comprehensive Clojure tooling
- **nREPL** - The underlying network REPL protocol
- **CIDER** - Emacs integration with nREPL
- **Calva** - VSCode integration with nREPL
- **Cursive** - IntelliJ integration with nREPL

## Summary

clojure-mcp-light provides minimal, focused CLI tooling for Clojure development:

1. **clj-nrepl-eval** - Command-line nREPL client with automatic delimiter repair
2. **clj-paren-repair-claude-hook** - Claude Code hook for delimiter fixing (optional)

**Core features:**
- Instant nREPL evaluation from command line
- Automatic delimiter repair (parinfer-rust or parinferish)
- Persistent sessions across invocations
- Server discovery and connection tracking
- Timeout handling and interrupt support
- Multi-line code support (pipe, heredoc)
- No MCP server required

**Best for:**
- REPL-driven development from command line
- Claude Code Clojure integration
- Quick code experimentation
- Testing code after edits
- Shell script automation
- Multi-project workflows

Use clj-nrepl-eval when you need instant Clojure evaluation without opening an editor, especially in Claude Code workflows where automatic delimiter repair prevents common LLM-generated syntax errors.
