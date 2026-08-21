---
name: jq
description: "Writes jq filters to query, reshape, aggregate, and pipeline JSON from APIs, CLIs, and logs. Use when parsing JSON, building jq one-liners, or explaining a jq expression. Not for in-memory DataFrames (pandas/polars), JSON Schema validation, or JavaScript Array.map as a jq substitute."
version: 1.0.1
category: development
risk: safe
source: community
date_added: "2026-03-28"
tags: [jq, json, shell, cli, data-transformation, bash]
tools: [claude, cursor, gemini]
---

# jq — JSON Querying and Transformation

## Overview

`jq` is the standard CLI tool for querying and reshaping JSON. This skill covers practical, expert-level usage: filtering deeply nested data, transforming structures, aggregating values, and composing `jq` into shell pipelines. Every example is copy-paste ready for real workflows.

## When to Use

- Parsing JSON output from APIs, CLI tools (AWS, GitHub, kubectl, docker), or log files
- Transforming JSON structure (rename keys, flatten arrays, group records)
- Building `jq` one-liners inside a bash script or PowerShell pipeline
- Explaining what a complex `jq` expression does
- Extracting specific fields from large JSON payloads for further processing

## Prerequisites

- `jq` installed and on `PATH`. Verify with `jq --version` (requires ≥ 1.6 for `walk`, `--stream` stability).
- On Windows (PowerShell, primary host): install via `winget install jqlang.jq` or `scoop install jq`. The binary is `jq.exe`; all filter syntax is identical across platforms.
- On Linux/macOS: `brew install jq` or `apt-get install jq`.
- Familiarity with JSON data types (object, array, string, number, boolean, null).

## Procedure

### 1. Basic Selection

```bash
# Extract a field
echo '{"name":"alice","age":30}' | jq '.name'
# "alice"

# Nested access
echo '{"user":{"email":"a@b.com"}}' | jq '.user.email'

# Array index
echo '[10, 20, 30]' | jq '.[1]'
# 20

# Array slice
echo '[1,2,3,4,5]' | jq '.[2:4]'
# [3, 4]

# All array elements
echo '[{"id":1},{"id":2}]' | jq '.[]'
```

PowerShell equivalent for the first example:
```powershell
'{"name":"alice","age":30}' | jq '.name'
```

### 2. Filtering with `select`

```bash
# Keep only matching elements
echo '[{"role":"admin"},{"role":"user"},{"role":"admin"}]' \
  | jq '[.[] | select(.role == "admin")]'

# Numeric comparison
curl -s https://api.github.com/repos/owner/repo/issues \
  | jq '[.[] | select(.comments > 5)]'

# Test a field exists and is non-null
jq '[.[] | select(.email != null)]'

# Combine conditions
jq '[.[] | select(.active == true and .score >= 80)]'
```

### 3. Mapping and Transformation

```bash
# Extract a field from every array element
echo '[{"name":"alice","age":30},{"name":"bob","age":25}]' \
  | jq '[.[] | .name]'
# ["alice", "bob"]

# Shorthand: map()
jq 'map(.name)'

# Build a new object per element
jq '[.[] | {user: .name, years: .age}]'

# Add a computed field
jq '[.[] | . + {senior: (.age > 28)}]'

# Rename keys
jq '[.[] | {username: .name, email_address: .email}]'
```

### 4. Aggregation and Reduce

```bash
# Sum all values
echo '[1, 2, 3, 4, 5]' | jq 'add'
# 15

# Sum a field across objects
jq '[.[].price] | add'

# Count elements
jq 'length'

# Max / min
jq 'max_by(.score)'
jq 'min_by(.created_at)'

# reduce: custom accumulator
echo '[1,2,3,4,5]' | jq 'reduce .[] as $x (0; . + $x)'
# 15

# Group by field
jq 'group_by(.department)'

# Count per group
jq 'group_by(.status) | map({status: .[0].status, count: length})'
```

### 5. String Interpolation and Formatting

```bash
# String interpolation
jq -r '.[] | "\(.name) is \(.age) years old"'

# Format as CSV (no header)
jq -r '.[] | [.name, .age, .email] | @csv'

# Format as TSV
jq -r '.[] | [.name, .score] | @tsv'

# URL-encode a value
jq -r '.query | @uri'

# Base64 encode
jq -r '.data | @base64'
```

### 6. Working with Keys and Paths

```bash
# List all top-level keys
jq 'keys'

# Check if key exists
jq 'has("email")'

# Delete a key
jq 'del(.password)'

# Delete nested keys from every element
jq '[.[] | del(.internal_id, .raw_payload)]'

# Recursive descent: find all values for a key anywhere in tree
jq '.. | .id? // empty'

# Get all leaf paths
jq '[paths(scalars)]'
```

### 7. Conditionals and Error Handling

```bash
# if-then-else
jq 'if .score >= 90 then "A" elif .score >= 80 then "B" else "C" end'

# Alternative operator: use fallback if null or false
jq '.nickname // .name'

# try-catch: skip errors instead of halting
jq '[.[] | try .nested.value catch null]'

# Suppress null output with // empty
jq '.[] | .optional_field // empty'
```

### 8. Practical Shell Integration

```bash
# Read from file
jq '.users' data.json

# Compact output (no whitespace) for further piping
jq -c '.[]' records.json | while IFS= read -r record; do
  echo "Processing: $record"
done

# Pass a shell variable into jq
STATUS="active"
jq --arg s "$STATUS" '[.[] | select(.status == $s)]'

# Pass a number
jq --argjson threshold 42 '[.[] | select(.value > $threshold)]'

# Slurp multiple JSON lines into an array
jq -s '.' records.ndjson

# Multiple files: slurp all into one array
jq -s 'add' file1.json file2.json

# Null-safe pipeline from a command
kubectl get pods -o json | jq '.items[] | {name: .metadata.name, status: .status.phase}'

# GitHub CLI: extract PR numbers
gh pr list --json number,title | jq -r '.[] | "\(.number)\t\(.title)"'

# AWS CLI: list running instance IDs
aws ec2 describe-instances \
  | jq -r '.Reservations[].Instances[] | select(.State.Name=="running") | .InstanceId'

# Docker: show container names and images
docker inspect $(docker ps -q) | jq -r '.[] | "\(.Name)\t\(.Config.Image)"'
```

PowerShell variable injection:
```powershell
$STATUS = "active"
jq --arg s $STATUS '[.[] | select(.status == $s)]'
```

### 9. Advanced Patterns

```bash
# Transpose an object of arrays to an array of objects
# Input: {"names":["a","b"],"scores":[10,20]}
jq '[.names, .scores] | transpose | map({name: .[0], score: .[1]})'

# Flatten one level
jq 'flatten(1)'

# Unique by field
jq 'unique_by(.email)'

# Sort, deduplicate and re-index
jq '[.[] | .name] | unique | sort'

# Walk: apply transformation to every node recursively
jq 'walk(if type == "string" then ascii_downcase else . end)'

# env: read environment variables inside jq
export API_KEY=secret
jq -n 'env.API_KEY'
```

### Best Practices

- Always use `-r` (raw output) when passing `jq` results to shell variables or other commands to strip JSON string quotes.
- Use `--arg` / `--argjson` to inject shell variables safely — never interpolate shell variables directly into filter strings.
- Prefer `map(f)` over `[.[] | f]` for readability.
- Use `-c` (compact) for newline-delimited JSON pipelines; omit it for human-readable debugging.
- Test filters interactively with `jq -n` and literal input before embedding in scripts.
- Use `empty` to drop unwanted elements rather than filtering to `null`.

### Security & Safety Notes

- `jq` is read-only by design — it cannot write files or execute commands.
- Avoid embedding untrusted JSON field values directly into shell commands; always quote or use `--arg`.
- Never put secrets directly in filter expressions; use `env` or `--arg` to pass them indirectly.

## Pitfalls

- **`jq` outputs `null` instead of the expected value.** Check for typos in key names; use `keys` to inspect actual field names. JSON is case-sensitive.

- **Numbers are quoted as strings in the output.** Use `--argjson` instead of `--arg` when injecting numeric values. `--arg` always creates a string.

- **Filter works in the terminal but fails in a script.** Ensure the filter string uses single quotes in the shell to prevent variable expansion. Use `jq '.field'` not `jq ".field"`. In PowerShell, use single quotes similarly: `jq '.field'`.

- **`add` returns `null` on an empty array.** Use `add // 0` or `add // ""` to provide a fallback default.

- **Streaming large files is slow.** Use `jq --stream` or switch to `jstream`/`gron` for very large files (>100 MB).

- **PowerShell mangles single-quoted jq filters with `$`.** PowerShell treats `$` inside double quotes as variable expansion but respects single quotes literally. Always wrap jq filters in single quotes in PowerShell: `jq '.[] | select(.price > $threshold)'` works correctly because single quotes prevent expansion.

- **`select(.field)` with `null` field throws a type error.** Guard with `select(.field != null and .field > 5)` or use `?` to suppress: `select(.field? > 5)`.

## Verification

1. **Verify jq is installed and working:**
   ```bash
   echo '{"test": true}' | jq '.test'
   # Expected output: true
   ```

2. **Verify version supports advanced functions:**
   ```bash
   jq --version
   # Expected: jq-1.6 or jq-1.7+
   ```

3. **Verify raw output mode strips quotes:**
   ```bash
   echo '{"name":"alice"}' | jq -r '.name'
   # Expected output: alice  (no quotes)
   ```

4. **Verify variable injection works:**
   ```bash
   STATUS="active"
   echo '[{"status":"active"},{"status":"inactive"}]' | jq --arg s "$STATUS" '[.[] | select(.status == $s)]'
   # Expected output: [{"status": "active"}]
   ```

5. **Verify `--argjson` for numeric injection:**
   ```bash
   echo '[{"value":10},{"value":50}]' | jq --argjson t 42 '[.[] | select(.value > $t)]'
   # Expected output: [{"value": 50}]
   ```

## Related Skills

- `bash-pro` — Wrapping jq calls in robust shell scripts
- `bash-linux` — General shell pipeline patterns
- `github-automation` — Using jq with GitHub CLI JSON output

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
