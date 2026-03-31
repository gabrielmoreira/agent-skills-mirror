---
name: babashka_scripting
description: |
  Fast-starting Clojure scripting and task runner built on GraalVM native image. Use when 
  writing shell scripts, build automation, task runners, CLI tools, fast startup scripting, 
  or when the user mentions Babashka, bb, task runner, shell scripting, native Clojure, 
  GraalVM, fast REPL, or scripting automation.
---

# Babashka

A fast-starting Clojure interpreter for scripting built with GraalVM native image. Babashka (bb) provides instant startup time, making Clojure practical for shell scripts, build tasks, and CLI tools.

## Quick Start

Babashka scripts start instantly and can use most Clojure features:

```clojure
#!/usr/bin/env bb

;; Simple script - save as script.clj
(println "Hello from Babashka!")
(println "Arguments:" *command-line-args*)

;; Run it
;; bb script.clj arg1 arg2
;; => Hello from Babashka!
;; => Arguments: (arg1 arg2)

;; Or use shebang and make executable
;; chmod +x script.clj
;; ./script.clj arg1 arg2

;; One-liner evaluation
;; bb -e '(+ 1 2 3)'
;; => 6

;; Process piped input
;; echo '{"name": "Alice"}' | bb -e '(-> *input* slurp (json/parse-string true) :name)'
;; => Alice
```

**Key benefits:**
- **Instant startup** - ~10ms vs 1-2s for JVM Clojure
- **Native executable** - No JVM installation required
- **Task runner** - Built-in task system via bb.edn
- **Rich standard library** - Including shell, http, file system, JSON, YAML
- **Script-friendly** - Process args, stdin/stdout, exit codes
- **Pod system** - Extend with native binaries

## Core Concepts

### Fast Startup via GraalVM Native Image

Babashka is compiled to a native executable using GraalVM, eliminating JVM startup time:

```bash
# Compare startup times
time bb -e '(println "Ready")'
# ~0.01s

time clojure -M -e '(println "Ready")'
# ~1-2s
```

**Trade-offs:**
- Instant startup vs slower runtime performance
- Fixed set of classes vs dynamic classloading
- Lower memory usage vs smaller heap
- Perfect for scripts, not for long-running servers

### Built-in Libraries

Babashka includes many useful libraries by default:

```clojure
;; File system (babashka.fs)
(require '[babashka.fs :as fs])
(fs/list-dir ".")
(fs/glob "." "**/*.clj")
(fs/create-dirs "target/build")

;; Shell (babashka.process)
(require '[babashka.process :as p])
(-> (p/shell {:out :string} "git status --short")
    :out)

;; HTTP client (babashka.http-client)
(require '[babashka.http-client :as http])
(http/get "https://api.github.com/users/babashka")

;; JSON (cheshire)
(require '[cheshire.core :as json])
(json/parse-string "{\"name\": \"Alice\"}" true)

;; YAML (clj-commons/clj-yaml)
(require '[clj-yaml.core :as yaml])
(yaml/parse-string "name: Alice\nage: 30")

;; Data manipulation (medley)
(require '[medley.core :as m])
(m/map-vals inc {:a 1 :b 2})

;; And many more...
```

### Task System

Define reusable tasks in `bb.edn`:

```clojure
;; bb.edn
{:tasks
 {:requires ([babashka.fs :as fs])
  
  ;; Simple task
  clean
  {:doc "Remove build artifacts"
   :task (fs/delete-tree "target")}
  
  ;; Task with dependencies
  test
  {:doc "Run tests"
   :depends [clean]
   :task (shell "clojure -M:test")}
  
  ;; Task with parameters
  deploy
  {:doc "Deploy to environment"
   :task (let [env (or (first *command-line-args*) "dev")]
           (println "Deploying to" env)
           (shell (str "deploy-" env ".sh")))}}}

;; Run tasks
;; bb tasks                  # List available tasks
;; bb clean                  # Run clean task
;; bb test                   # Run test (which runs clean first)
;; bb deploy production      # Run with args
```

### Process Execution

Babashka provides excellent shell integration:

```clojure
(require '[babashka.process :as p])

;; Simple command
(p/shell "ls -la")
;; Output goes to stdout

;; Capture output
(-> (p/shell {:out :string} "git status --short")
    :out
    println)

;; Pipeline
(p/pipeline
  (p/process ["cat" "file.txt"])
  (p/process ["grep" "ERROR"])
  (p/process ["wc" "-l"]))

;; Handle errors
(let [result (p/shell {:continue true} "false")]
  (when-not (zero? (:exit result))
    (println "Command failed!")))
```

## Common Workflows

### Workflow 1: Writing Executable Scripts

```clojure
#!/usr/bin/env bb

;; Script: backup.clj
;; Usage: ./backup.clj source-dir backup-dir

(require '[babashka.fs :as fs]
         '[babashka.process :as p])

(defn backup [source dest]
  (println "Backing up" source "to" dest)
  
  ;; Create backup directory
  (fs/create-dirs dest)
  
  ;; Copy files
  (doseq [file (fs/glob source "**/*")]
    (when (fs/regular-file? file)
      (let [relative (fs/relativize source file)
            target (fs/path dest relative)]
        (fs/create-dirs (fs/parent target))
        (fs/copy file target {:replace-existing true}))))
  
  (println "Backup complete!"))

;; Parse arguments
(when (< (count *command-line-args*) 2)
  (println "Usage: backup.clj <source> <dest>")
  (System/exit 1))

(let [[source dest] *command-line-args*]
  (backup source dest))

;; Make it executable:
;; chmod +x backup.clj
;;
;; Run it:
;; ./backup.clj ~/docs ~/backups/docs
```

### Workflow 2: Creating a Task Runner

```clojure
;; bb.edn - Project task definitions
{:deps {medley/medley {:mvn/version "1.3.0"}
        io.github.paintparty/bling {:mvn/version "0.6.0"}}
 
 :paths ["src" "test"]
 
 :tasks
 {:requires ([babashka.fs :as fs]
             [babashka.process :as p]
             [bling.core :as bling])
  
  ;; Clean build artifacts
  clean
  {:doc "Remove target directory"
   :task (do
           (bling/callout {:type :info} 
                          (bling/bling [:bold "Cleaning..."]))
           (fs/delete-tree "target")
           (bling/callout {:type :success} "Clean complete"))}
  
  ;; Run tests
  test
  {:doc "Run tests with Kaocha"
   :task (do
           (bling/callout {:type :info} 
                          (bling/bling [:bold "Running tests..."]))
           (p/shell "clojure -M:test"))}
  
  ;; Lint code
  lint
  {:doc "Lint with clj-kondo"
   :task (p/shell "clojure -M:lint -m clj-kondo.main --lint src test")}
  
  ;; Format code
  fmt
  {:doc "Format code with cljstyle"
   :task (p/shell "clojure -M:format -m cljstyle.main fix src test")}
  
  ;; Check formatting
  fmt-check
  {:doc "Check code formatting"
   :task (p/shell "clojure -M:format -m cljstyle.main check src test")}
  
  ;; Run full CI pipeline
  ci
  {:doc "Run CI pipeline: clean, lint, test"
   :task (do
           (run 'clean)
           (run 'fmt-check)
           (run 'lint)
           (run 'test)
           (bling/callout {:type :success} 
                          (bling/bling [:bold "CI passed!"])))}
  
  ;; Start REPL
  repl
  {:doc "Start nREPL server on port 7889"
   :task (p/shell "clojure -M:nrepl")}
  
  ;; Build uberjar
  build
  {:doc "Build uberjar"
   :depends [clean test]
   :task (do
           (bling/callout {:type :info} "Building uberjar...")
           (p/shell "clojure -T:build uber")
           (bling/callout {:type :success} "Build complete!"))}}}

;; Usage:
;; bb tasks              # List all tasks
;; bb clean              # Run clean task
;; bb ci                 # Run full CI pipeline
;; bb build              # Build (runs clean and test first)
```

### Workflow 3: HTTP API Client Script

```clojure
#!/usr/bin/env bb

;; Script: github-info.clj
;; Usage: ./github-info.clj username

(require '[babashka.http-client :as http]
         '[cheshire.core :as json])

(defn get-user-info [username]
  (let [url (str "https://api.github.com/users/" username)
        response (http/get url {:headers {"User-Agent" "Babashka"}})]
    (when (= 200 (:status response))
      (json/parse-string (:body response) true))))

(defn get-repos [username]
  (let [url (str "https://api.github.com/users/" username "/repos")
        response (http/get url {:headers {"User-Agent" "Babashka"}})]
    (when (= 200 (:status response))
      (json/parse-string (:body response) true))))

(defn display-info [username]
  (if-let [user (get-user-info username)]
    (do
      (println "Name:" (:name user))
      (println "Bio:" (:bio user))
      (println "Public Repos:" (:public_repos user))
      (println "Followers:" (:followers user))
      
      (println "\nTop 5 Repos:")
      (doseq [repo (->> (get-repos username)
                        (sort-by :stargazers_count >)
                        (take 5))]
        (println (format "  ⭐ %d - %s" 
                         (:stargazers_count repo)
                         (:name repo)))))
    (println "User not found")))

;; Main
(when (empty? *command-line-args*)
  (println "Usage: github-info.clj <username>")
  (System/exit 1))

(display-info (first *command-line-args*))
```

### Workflow 4: File Processing Pipeline

```clojure
#!/usr/bin/env bb

;; Script: process-logs.clj
;; Process log files and generate report

(require '[babashka.fs :as fs]
         '[clojure.string :as str])

(defn parse-log-line [line]
  (when-let [[_ timestamp level message] 
             (re-matches #"\[(.*?)\] (\w+): (.*)" line)]
    {:timestamp timestamp
     :level (keyword (str/lower-case level))
     :message message}))

(defn analyze-logs [log-dir]
  (let [log-files (fs/glob log-dir "*.log")
        entries (->> log-files
                     (mapcat (comp str/split-lines slurp))
                     (keep parse-log-line))]
    
    {:total (count entries)
     :by-level (frequencies (map :level entries))
     :errors (->> entries
                  (filter #(= :error (:level %)))
                  (map :message)
                  (take 10))}))

(defn report [stats]
  (println "Log Analysis Report")
  (println "===================")
  (println "Total entries:" (:total stats))
  (println "\nBy level:")
  (doseq [[level count] (sort-by val > (:by-level stats))]
    (println (format "  %s: %d" (name level) count)))
  (println "\nRecent errors:")
  (doseq [error (:errors stats)]
    (println "  -" error)))

;; Main
(when (empty? *command-line-args*)
  (println "Usage: process-logs.clj <log-directory>")
  (System/exit 1))

(-> (first *command-line-args*)
    analyze-logs
    report)
```

### Workflow 5: Data Transformation Script

```clojure
#!/usr/bin/env bb

;; Script: transform-data.clj
;; Read JSON/YAML, transform, output JSON/YAML

(require '[cheshire.core :as json]
         '[clj-yaml.core :as yaml]
         '[clojure.string :as str]
         '[babashka.fs :as fs])

(defn read-file [path]
  (let [content (slurp path)
        ext (fs/extension path)]
    (case ext
      "json" (json/parse-string content true)
      "yaml" (yaml/parse-string content)
      "yml" (yaml/parse-string content)
      (throw (ex-info "Unsupported format" {:ext ext})))))

(defn write-file [path data]
  (let [ext (fs/extension path)]
    (case ext
      "json" (spit path (json/generate-string data {:pretty true}))
      "yaml" (spit path (yaml/generate-string data))
      "yml" (spit path (yaml/generate-string data))
      (throw (ex-info "Unsupported format" {:ext ext})))))

(defn transform [data]
  ;; Example: uppercase all string values
  (clojure.walk/postwalk
    (fn [x]
      (if (string? x)
        (str/upper-case x)
        x))
    data))

;; Main
(when (< (count *command-line-args*) 2)
  (println "Usage: transform-data.clj <input> <output>")
  (System/exit 1))

(let [[input output] *command-line-args*]
  (-> input
      read-file
      transform
      (write-file output))
  (println "Transformed" input "→" output))
```

### Workflow 6: Interactive Task with User Input

```clojure
#!/usr/bin/env bb

;; Script: interactive-setup.clj
;; Interactive project setup

(defn prompt [message]
  (print (str message " "))
  (flush)
  (read-line))

(defn confirm [message]
  (= "y" (prompt (str message " (y/n)?"))))

(defn setup-project []
  (println "Project Setup")
  (println "=============")
  
  (let [name (prompt "Project name:")
        desc (prompt "Description:")
        author (prompt "Author:")
        use-test? (confirm "Include test setup?")
        use-ci? (confirm "Include CI config?")]
    
    {:name name
     :description desc
     :author author
     :features {:test use-test?
                :ci use-ci?}}))

(defn create-files [config]
  (require '[babashka.fs :as fs])
  
  ;; Create project structure
  (fs/create-dirs (str (:name config) "/src"))
  
  (when (get-in config [:features :test])
    (fs/create-dirs (str (:name config) "/test")))
  
  (when (get-in config [:features :ci])
    (spit (str (:name config) "/.github/workflows/ci.yml")
          "name: CI\n..."))
  
  (println "\n✓ Project created:" (:name config)))

;; Main
(let [config (setup-project)]
  (when (confirm "\nCreate project files?")
    (create-files config)
    (println "Done!")))
```

### Workflow 7: Conditional Task Execution

```clojure
;; bb.edn with conditional tasks
{:tasks
 {:requires ([babashka.fs :as fs])
  
  ;; Check if files changed
  changed?
  {:task (let [src-files (fs/glob "src" "**/*.clj")
               target (fs/file "target/build.timestamp")
               last-build (when (fs/exists? target)
                            (fs/file-time->millis target))
               latest-src (when (seq src-files)
                            (apply max (map fs/file-time->millis src-files)))]
           (or (nil? last-build)
               (> latest-src last-build)))}
  
  ;; Build only if changed
  build
  {:doc "Build if source files changed"
   :task (if (-> (shell {:out :string :continue true} "bb changed?")
                 :out
                 str/trim
                 boolean)
           (do
             (println "Source changed, rebuilding...")
             (shell "clojure -T:build compile")
             (fs/create-dirs "target")
             (spit "target/build.timestamp" (System/currentTimeMillis)))
           (println "No changes, skipping build"))}}}
```

## When to Use Each Approach

**Use Babashka when:**
- Writing shell scripts that need Clojure
- Building task runners and build tools
- Creating CLI tools with fast startup
- Processing files and data transformations
- Quick automation scripts
- Replacing bash/python scripts with Clojure
- CI/CD scripts
- Git hooks

**Use JVM Clojure when:**
- Building long-running applications
- Need dynamic classloading
- Require libraries not compatible with bb
- Performance-critical computations
- Large heap requirements
- Web servers (use http-kit/Ring on JVM)

**Can use either:**
- Data processing pipelines (bb faster startup, JVM faster runtime)
- API clients (bb sufficient for most cases)
- Testing utilities (bb for fast feedback, JVM for comprehensive)

## Best Practices

**DO:**
- Use shebang `#!/usr/bin/env bb` for executable scripts
- Handle *command-line-args* explicitly
- Exit with proper codes (0 success, non-zero error)
- Use `babashka.process/shell` for external commands
- Leverage built-in libraries (fs, http-client, process)
- Define reusable tasks in bb.edn
- Use `:doc` strings in task definitions
- Handle errors with proper messages
- Make scripts portable (avoid platform-specific paths)

**DON'T:**
- Try to load incompatible libraries
- Expect same performance as JVM for CPU-intensive work
- Use dynamic classloading (not supported)
- Forget to handle missing arguments
- Ignore exit codes from shell commands
- Hard-code paths (use babashka.fs)
- Write overly complex scripts (consider JVM app instead)

## Common Issues

### Issue: "Class Not Found"

**Problem:** Trying to use a library not included in Babashka

```clojure
(require '[some.library :as lib])
;; => Could not find namespace: some.library
```

**Solution:** Check if library is compatible or use pods

```clojure
;; Check built-in libraries
;; bb -e "(keys (ns-publics 'clojure.core))"

;; Add compatible dependency to bb.edn
{:deps {medley/medley {:mvn/version "1.3.0"}}}

;; Or use a pod for native libraries
;; See: https://github.com/babashka/pods
```

### Issue: "Command Not Found in Shell"

**Problem:** Shell command fails to find executable

```clojure
(require '[babashka.process :as p])
(p/shell "my-tool")
;; => Error: Cannot run program "my-tool"
```

**Solution:** Use full path or check PATH

```clojure
;; Use full path
(p/shell "/usr/local/bin/my-tool")

;; Or check PATH
(p/shell {:extra-env {"PATH" (str (System/getenv "PATH") ":/custom/path")}}
         "my-tool")
```

### Issue: "Task Not Found"

**Problem:** bb.edn task not recognized

```clojure
;; bb.edn
{:tasks {test {:task (println "Testing")}}}

;; bb test
;; => Could not find task: test
```

**Solution:** Check bb.edn location and syntax

```bash
# bb.edn must be in current directory or parent
# Check it's valid EDN
bb -e '(clojure.edn/read-string (slurp "bb.edn"))'

# List available tasks
bb tasks
```

### Issue: "Slow Performance"

**Problem:** Script is slower than expected

```clojure
;; Intensive computation
(reduce + (range 10000000))
;; Takes longer than JVM Clojure
```

**Solution:** Babashka optimizes for startup, not runtime

```bash
# For CPU-intensive work, use JVM Clojure
clojure -M -e '(time (reduce + (range 10000000)))'

# Or keep bb for orchestration, delegate heavy work:
bb -e '(babashka.process/shell "clojure -M -m my.cpu-intensive-app")'
```

## Advanced Topics

### Pods System

Pods extend Babashka with native binaries:

```clojure
;; Load pod
(require '[babashka.pods :as pods])
(pods/load-pod 'org.babashka/postgresql "0.1.0")

;; Use pod
(require '[pod.babashka.postgresql :as pg])
(pg/execute! db-spec ["SELECT * FROM users"])
```

Available pods: https://github.com/babashka/pods

### Preloads

Load code before script execution:

```clojure
;; bb.edn
{:paths ["."]
 :tasks {:init (load-file "helpers.clj")}}

;; helpers.clj
(defn my-helper [x] (str x "!"))

;; Now available in all tasks
{:tasks
 {greet {:task (println (my-helper "Hello"))}}}
```

### Native Image Compilation

Compile your own bb scripts to native binaries:

```bash
# Using GraalVM native-image
# See: https://www.graalvm.org/latest/reference-manual/native-image/
```

### Socket REPL

Start a REPL server for debugging:

```bash
bb socket-repl 1666
# Connect with: rlwrap nc localhost 1666

bb nrepl-server 1667
# Connect from editors (CIDER, Calva, etc.)
```

## Resources

- Official Documentation: https://book.babashka.org
- GitHub: https://github.com/babashka/babashka
- Built-in libraries: https://book.babashka.org/#libraries
- Pods registry: https://github.com/babashka/pods
- Examples: https://github.com/babashka/babashka/tree/master/examples
- Task runner guide: https://book.babashka.org/#tasks
- API docs: https://babashka.org/doc/api

## Related Tools

- **Babashka.fs** - File system library (built-in)
- **Babashka.process** - Shell process library (built-in)
- **Babashka.cli** - Command-line parsing
- **Babashka.http-client** - HTTP client (built-in)
- **Scittle** - Babashka for the browser
- **Nbb** - Node.js-based Clojure scripting

## Summary

Babashka makes Clojure practical for scripting:

- **Instant startup** - ~10ms for shell scripts
- **Native binary** - No JVM required
- **Task runner** - Built-in task system
- **Rich stdlib** - fs, http, process, json, yaml, and more
- **Script-friendly** - Args, stdin/stdout, exit codes
- **Pod system** - Extend with native libraries

Use Babashka for shell scripts, build automation, CLI tools, and anywhere fast startup matters more than long-running performance.
