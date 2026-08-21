---
name: redis-cli
description: "Operates Redis from redis-cli: GET/SET/hashes/lists, SCAN, latency/bigkeys, ACL, cluster, pub/sub, MONITOR. Use when querying or diagnosing a Redis instance from the command line. Not for application Redis clients (redis-py/ioredis), choosing Vercel/Upstash storage (vercel-storage), or Redis module/source development."
version: 1.0.1
risk: unknown
source: https://github.com/chaunsin/agent-skills/tree/master/skills/redis-cli
source_repo: chaunsin/agent-skills
source_type: community
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/chaunsin/agent-skills/blob/master/LICENSE
---

# redis-cli — Redis Command Line Interface

## Overview

`redis-cli` is the primary command-line tool for interacting with Redis. It supports two modes: **command-line execution** (run a command and exit) and **interactive mode** (a REPL with tab completion, history, and hints). It also provides special modes for monitoring, latency analysis, keyspace scanning, and data import/export.

**Official resources:** [Redis CLI Docs](https://redis.io/docs/latest/develop/tools/cli/) | [Commands](https://redis.io/commands/) | [Download](https://redis.io/downloads/)

## When to Use

Use this skill whenever the user mentions `redis-cli`, Redis CLI, or any task involving:

- Querying, inspecting, debugging, or managing Redis from the command line
- Key/value reads and writes (GET, SET, HGETALL, LRANGE, ZRANGE, etc.)
- SCAN or keyspace exploration (`--scan`, `SCAN`, `DBSIZE`)
- Latency diagnostics (`--latency`, `--latency-history`, `--intrinsic-latency`)
- Big keys and memory analysis (`--bigkeys`, `--memkeys`, `--keystats`)
- ACL management, client management, runtime configuration
- Cluster operations (`--cluster check`, `--cluster reshard`)
- Pub/Sub, Lua scripting, RDB backup, mass insertion
- Real-time monitoring (`--stat`, `MONITOR`)

## Prerequisites

1. **Check if redis-cli is installed:**

```bash
redis-cli --version
```

2. **Install options by platform:**

```bash
# macOS (Homebrew)
brew install redis

# Ubuntu / Debian
sudo apt install redis-tools

# CentOS / RHEL
sudo yum install redis

# Alpine
apk add redis

# Build from source (binary only)
make redis-cli
# Binary at: src/redis-cli

# Docker (no installation needed)
docker run -it --rm redis redis-cli -h <host> -p <port> PING
```

> **Windows host note:** On Windows, `redis-cli` may be available via WSL2, Docker Desktop, or a native Redis port. If running under PowerShell, pipe-based examples (`| wc -l`, `while read`) require adaptation — use WSL or Git Bash for shell pipelines, or use PowerShell equivalents (`Measure-Object`, `ForEach-Object`).

## Procedure

### Step 1 — Establish a Connection

```bash
# Basic connection (default: 127.0.0.1:6379)
redis-cli
redis-cli -h redis15.localnet.org -p 6390 PING

# With password — NEVER pass -a in production; use REDISCLI_AUTH env var
REDISCLI_AUTH=YOUR_PASSWORD redis-cli PING

# URI connection
redis-cli -u redis://user:password@host:port/dbnum PING

# TLS
redis-cli --tls --cacert /path/to/ca.crt -h redis.example.com PING

# Specific database
redis-cli -n 2 DBSIZE

# IPv4/IPv6 preference
redis-cli -4 PING   # prefer IPv4
redis-cli -6 PING   # prefer IPv6
```

### Step 2 — Choose Execution Mode

**Command-line mode** (execute one command and exit):

```bash
redis-cli INCR mycounter
redis-cli GET mykey
```

**Interactive mode** (REPL with tab completion and history):

```bash
redis-cli
127.0.0.1:6379> PING
PONG
127.0.0.1:6379> SELECT 2
OK
127.0.0.1:6379[2]> DBSIZE
(integer) 1
```

The prompt shows `host:port[db]`. Use `CONNECT <host> <port>` to switch instances interactively.

### Step 3 — Query Data by Type

**String operations** (O(1)):

```
GET key
SET key value [NX|XX] [EX sec|PX ms|KEEPTTL]
SET key value GET              # Set new, return old value
GETSET key newvalue            # [Prefer SET key value GET]
MGET key1 key2 ...
INCR key
INCRBY key 10
STRLEN key
GETRANGE key 0 50
```

**Hash operations**:

```
HGET key field                 # O(1)
HMGET key f1 f2                # O(N)
HGETALL key                    # O(N)
HKEYS key                      # O(N)
HLEN key                       # O(1)
HEXISTS key field              # O(1)
HSCAN key 0 [MATCH pat]        # O(1) per call
```

**List operations**:

```
LRANGE key 0 -1                # O(N)
LLEN key                       # O(1)
LINDEX key 0                   # O(N)
LPOS key value                 # O(N)
```

**Set operations**:

```
SMEMBERS key                   # O(N)
SCARD key                      # O(1)
SISMEMBER key member           # O(1)
SMISMEMBER key m1 m2           # O(N)
SSCAN key 0 [MATCH pat]        # O(1) per call
```

**Sorted Set operations**:

```
ZRANGE key 0 -1 [WITHSCORES]           # By index        O(log(N)+M)
ZRANGE key -inf +inf BYSCORE           # By score range  O(log(N)+M)
ZRANGE key [a [z BYLEX                 # By lexicographic O(log(N)+M)
ZCARD key                               # O(1)
ZSCORE key member                       # O(1)
ZRANK key member                        # O(log(N))
ZSCAN key 0 [MATCH pat]                 # O(1) per call
```

**Key inspection**:

```
EXISTS key [key ...]           # Returns count; O(N) for multi
TYPE key                       # string|list|set|zset|hash|stream  O(1)
TTL key                        # -1=none, -2=not exists  O(1)
PTTL key                       # Milliseconds            O(1)
MEMORY USAGE key [SAMPLES n]   # Bytes                   O(N)
OBJECT ENCODING key            # ziplist, hashtable, etc. O(1)
OBJECT IDLETIME key            # Seconds since last access O(1)
DBSIZE                         # Total keys in current DB  O(1)
RANDOMKEY                      # Random key               O(1)
```

### Step 4 — Scan Keys Safely (Production)

> **HARD RULE:** Never use `KEYS *` in production — it blocks the server. Always use `SCAN`.

```bash
# Built-in scan mode
redis-cli --scan
redis-cli --scan --pattern 'user:*'
redis-cli --scan --pattern '*:12345*'
redis-cli --scan --count 100

# Programmatic SCAN in interactive mode
SCAN 0 MATCH user:* COUNT 100
# Returns: 1) next_cursor  2) [keys...]
# Continue: SCAN <next_cursor> MATCH user:* COUNT 100
# Complete when cursor returns 0

# Count keys matching a pattern
redis-cli --scan --pattern 'session:*' | wc -l
```

SCAN guarantees: a full iteration (cursor 0 → cursor 0) always returns all elements that existed for the entire duration. Elements may appear multiple times — handle duplicates in your application.

### Step 5 — Inspect Server Health

```bash
# Real-time stats (updates every second; -i changes interval)
redis-cli --stat

# Server information by section
redis-cli INFO server
redis-cli INFO memory
redis-cli INFO keyspace
redis-cli INFO replication
redis-cli INFO all

# Key space analysis
redis-cli --bigkeys               # Largest keys by element count
redis-cli --memkeys               # Largest keys by memory usage
redis-cli --keystats              # Combined bigkeys + memkeys with distribution

# Latency analysis
redis-cli --latency               # Continuous latency sampling
redis-cli --latency-history       # Latency over time (15s windows)
redis-cli --latency-dist          # Latency spectrum visualization
redis-cli --intrinsic-latency 5   # System baseline (run on Redis host)
```

### Step 6 — Control Output Format

```bash
# Raw output (no type prefixes) — default when piping
redis-cli --raw GET mykey
redis-cli GET mykey > /tmp/output.txt    # auto raw mode

# Human-readable (force) when piping
redis-cli --no-raw GET mykey | cat

# CSV output
redis-cli --csv LRANGE mylist 0 -1

# JSON output (RESP3; use -2 for RESP2)
redis-cli --json HGETALL user:1

# Read last argument from stdin
cat /etc/services | redis-cli -x SET net_services

# Pipe commands from file
cat /tmp/commands.txt | redis-cli
```

### Step 7 — Repeat and Monitor Commands

```bash
# Run command N times
redis-cli -r 5 INCR counter

# Run with delay (seconds, supports decimals)
redis-cli -r -1 -i 1 INFO | grep rss_human    # infinite, every 1s

# Interactive: prefix with count
5 INCR mycounter    # runs 5 times
```

### Step 8 — Administer Server

```bash
# ACL management
redis-cli ACL LIST
redis-cli ACL SETUSER admin on >YOUR_PASSWORD ~* +@all
redis-cli ACL SETUSER readonly on >YOUR_PASSWORD ~* +@read
redis-cli ACL DELUSER username
redis-cli ACL DRYRUN username GET key
redis-cli ACL GENPASS

# Client management
redis-cli CLIENT LIST
redis-cli CLIENT KILL ADDR ip:port
redis-cli CLIENT PAUSE 5000 WRITE
redis-cli CLIENT SETNAME my-app

# Configuration
redis-cli CONFIG GET maxmemory
redis-cli CONFIG SET maxmemory 100mb
redis-cli CONFIG REWRITE
redis-cli CONFIG RESETSTAT

# Replication acknowledgment
redis-cli WAIT 2 5000              # Wait for 2 replicas (5s timeout)
redis-cli WAITAOF 1 1 5000         # Wait for AOF fsync (Redis 7.2+)

# Persistence
redis-cli BGSAVE
redis-cli BGREWRITEAOF
redis-cli LASTSAVE

# Replication
redis-cli REPLICAOF host port
redis-cli REPLICAOF NO ONE

# Server lifecycle
redis-cli SHUTDOWN SAVE
redis-cli SHUTDOWN NOSAVE

# Slow log
redis-cli SLOWLOG GET 10
redis-cli SLOWLOG LEN
redis-cli SLOWLOG RESET

# Cluster management
redis-cli --cluster check host:port
redis-cli --cluster reshard host:port
redis-cli -c -h cluster-node PING
```

## Common Workflows

### Explore an Unknown Database

```bash
# Step 1: Basic stats
redis-cli INFO keyspace
redis-cli DBSIZE

# Step 2: Find big keys and memory usage
redis-cli --bigkeys
redis-cli --memkeys

# Step 3: Sample keys and inspect types
redis-cli --scan | head -20
redis-cli TYPE <key>
redis-cli TTL <key>

# Step 4: Read data based on type
redis-cli HGETALL <hash_key>
redis-cli LRANGE <list_key> 0 -1
redis-cli ZRANGE <zset_key> 0 -1 WITHSCORES
```

### Monitor in Real Time

```bash
# Live server stats
redis-cli --stat -i 2

# Watch memory specifically
redis-cli -r -1 -i 5 INFO memory | grep used_memory_human

# Monitor all commands (caution: high overhead)
redis-cli MONITOR

# Continuous latency
redis-cli --latency-history -i 5
```

### Query Specific Key Patterns

```bash
# Count keys by pattern
redis-cli --scan --pattern 'session:*' | wc -l

# Find and inspect hash keys
redis-cli --scan --pattern 'user:*' | while read key; do
  echo "=== $key ==="
  redis-cli HGETALL "$key"
done

# Check TTL of matching keys
redis-cli --scan --pattern 'cache:*' | while read key; do
  redis-cli TTL "$key"
done
```

## Detailed Reference Files

Load these reference files from the `references/` directory when the task requires deeper detail beyond the quick reference above.

| File | Content | When to load |
|------|---------|-------------|
| `references/connection-and-options.md` | Full connection options, CLI flags, SSL/TLS, environment variables, interactive mode features (completion, history, preferences), RESP protocol versions | Configuring connections, setting up TLS, customizing CLI behavior |
| `references/data-query-commands.md` | Core data type commands: Strings, Hashes, Lists, Sets, Sorted Sets, Streams, Bitmaps, HyperLogLog, Geospatial, plus Key Operations, Database Operations, and Transactions | Looking up core command syntax, understanding command options and return values |
| `references/module-data-types.md` | Module data types: JSON (RedisJSON), Vector Sets (Redis 8.0+), Bloom Filter, Cuckoo Filter, Top-K, Count-Min Sketch, T-Digest, TimeSeries (TS.*), Full-Text Search / RediSearch (FT.*) | Working with Redis module data types, similarity search, probabilistic data structures, time series data, full-text search |
| `references/key-management.md` | SCAN family details (SCAN/SSCAN/HSCAN/ZSCAN), big keys analysis, key expiration (EXPIRE, TTL, PERSIST), keyspace patterns, mass insertion | Scanning databases, analyzing key distribution, managing key lifecycles |
| `references/inspection-and-monitoring.md` | INFO sections, MONITOR, --stat mode, latency tools, RDB backup, replica mode, LRU simulation | Monitoring Redis instances, debugging performance, creating backups |
| `references/advanced-features.md` | Lua scripting (--eval, --ldb), Pub/Sub mode, pipe mode, CSV/JSON output, string quoting and escaping, stdin input, remote RDB transfer, Cluster management | Running scripts, subscribing to channels, bulk data operations, managing Redis Cluster |
| `references/server-administration.md` | ACL management, client management, configuration, replication acknowledgment (WAIT/WAITAOF), persistence, replication setup, server lifecycle (SHUTDOWN/FAILOVER) | Managing users and permissions, controlling client connections, runtime configuration, ensuring write durability, persistence management |

## Pitfalls

> **HARD RULES — never violate these:**

1. **Never pass passwords via `-a` in production** — visible in shell history and process listings. Always use the `REDISCLI_AUTH` environment variable instead.
2. **Never use `KEYS *` on production databases** — it blocks the server. Always use `SCAN` or `--scan`.
3. **`MONITOR` logs all commands** including sensitive data — use cautiously, never for extended periods on production servers.
4. **`FLUSHALL` / `FLUSHDB` are irreversible** — always verify the target database first with `CLIENT LIST` or `INFO keyspace` before executing.
5. **`--rdb` transfer during write operations** may produce inconsistent snapshots on busy servers. Run during low-traffic windows or use `BGSAVE` first.
6. **SCAN may return duplicate keys** across iterations — deduplicate in your application logic.
7. **`CONFIG SET` at runtime is not persisted** — follow with `CONFIG REWRITE` to save to `redis.conf`, or changes are lost on restart.
8. **`SHUTDOWN NOSAVE` discards all in-memory data** — verify persistence status (`INFO persistence`, `LASTSAVE`) before using.
9. **Shell pipelines (`| wc -l`, `while read`) do not work natively in PowerShell** — use WSL, Git Bash, or PowerShell equivalents (`Measure-Object`, `ForEach-Object`).

## Verification

1. **Verify redis-cli is installed and responsive:**

```bash
redis-cli --version
redis-cli PING
# Expected: PONG
```

2. **Verify connection to a specific host/port:**

```bash
redis-cli -h <host> -p <port> PING
# Expected: PONG
```

3. **Verify database size and keyspace:**

```bash
redis-cli INFO keyspace
# Expected: db0:keys=N,expires=M,avg_ttl=...
redis-cli DBSIZE
# Expected: (integer) <key_count>
```

4. **Verify a key exists and check its type:**

```bash
redis-cli EXISTS mykey
# Expected: (integer) 1
redis-cli TYPE mykey
# Expected: string|list|set|zset|hash|stream
```

5. **Verify SCAN completes a full iteration:**

```bash
redis-cli --scan --pattern 'test:*' | wc -l
# Expected: integer count of matching keys
```

6. **Verify TLS connection works:**

```bash
redis-cli --tls --cacert /path/to/ca.crt -h redis.example.com PING
# Expected: PONG
```

7. **Verify ACL user permissions:**

```bash
redis-cli ACL DRYRUN myuser GET mykey
# Expected: OK
```

## External References

- [Redis CLI Documentation](https://redis.io/docs/latest/develop/tools/cli/)
- [Redis Commands](https://redis.io/commands/)
- [Redis Data Types](https://redis.io/docs/latest/develop/data-types/)
- [Redis Protocol Specification](https://redis.io/docs/latest/develop/reference/protocol-spec/)
- [Redis Mass Insertion](https://redis.io/docs/latest/develop/clients/patterns/bulk-loading/)
- [Redis Lua Debugger](https://redis.io/docs/latest/develop/programmability/lua-debugging/)

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
