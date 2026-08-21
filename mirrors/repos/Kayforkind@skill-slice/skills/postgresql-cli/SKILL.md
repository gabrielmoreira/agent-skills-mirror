---
name: postgresql-cli
description: "Drives PostgreSQL's psql client: connections, \\d inspection, \\copy, scripting, pipeline mode, and \\watch. Use when the user mentions psql, backslash meta-commands, or SQL scripting from the terminal. Not for Neon egress/query-bloat diagnosis (neon-postgres-egress-optimizer) and not a Metabase BI setup (setup-metabase-instance)."
version: 1.0.1
---

# psql — PostgreSQL Interactive Terminal

psql is PostgreSQL's feature-rich interactive terminal. It lets you write and execute queries, inspect database objects, import/export data, script batch operations, and customize output formatting — all from the command line.

## When to Use

Use this skill when the user needs to:

- Connect to a PostgreSQL database from the command line
- Inspect database objects (tables, views, indexes, functions, roles, schemas)
- Import or export data using `\copy` or `COPY`
- Write and run SQL scripts with psql meta-commands
- Format query output (CSV, HTML, expanded, unaligned)
- Use pipeline mode, `\watch`, `\crosstabview`, or conditional scripting (`\if`)
- Troubleshoot connection issues, query plans, or lock contention
- Automate database tasks via `psql -c` or `psql -f`

Trigger keywords: `psql`, `postgresql cli`, `backslash commands`, `meta-commands`, `\d`, `\copy`, `\watch`, `\crosstabview`, `pgpass`, `pg_service.conf`, `ON_ERROR_STOP`, `FETCH_COUNT`.

## Prerequisites

Verify psql is installed and available:

```bash
psql --version
```

If not found, install PostgreSQL client tools:

```powershell
# Windows (PowerShell) — use the official installer or scoop/chocolatey
winget install PostgreSQL.PostgreSQL
# or
choco install postgresql
```

```bash
# macOS (Homebrew)
brew install libpq
brew link --force libpq

# Ubuntu / Debian
sudo apt install postgresql-client

# CentOS / RHEL
sudo yum install postgresql

# Alpine
apk add postgresql-client
```

The server package (`postgresql`) is not required — you only need the client to connect to a remote PostgreSQL instance.

## Procedure

### 1. Connect to a Database

**CLI flags (most explicit):**

```bash
psql -h host -p port -U user -d dbname
```

**Connection URI — WARNING: password in URI is visible in shell history and process listings. Prefer `~/.pgpass` for production:**

```bash
psql "postgresql://user:YOUR_PASSWORD@host:port/dbname"
```

**Environment variables (no flags needed):**

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=mydb
export PGUSER=postgres
# WARNING: PGPASSWORD is visible in process listings (e.g. `ps aux`).
#          Use ~/.pgpass in production instead.
export PGPASSWORD=YOUR_PASSWORD
psql
```

**`~/.pgpass` file (RECOMMENDED for passwords):**

```bash
# Format: hostname:port:database:username:password
touch ~/.pgpass && chmod 600 ~/.pgpass
# Then manually edit ~/.pgpass and add entries (avoids password in shell history):
# localhost:5432:mydb:postgres:YOUR_PASSWORD
psql -h localhost -U postgres -d mydb   # no password prompt
```

**Execute and exit (script mode):**

```bash
psql -f script.sql dbname                        # execute file then exit
psql -c "SELECT 1" dbname                        # run single command then exit
psql -1 -f migration.sql dbname                  # run in single transaction
```

**Service connection (reads from `pg_service.conf`):**

```bash
psql service=mydb_prod
```

**Reconnect within a session:**

```
\c dbname                                       # reconnect to different db
\c -reuse-previous=on sslmode=require           # change only sslmode
\c "host=newhost port=5432 dbname=mydb"         # conninfo string
```

**Connection precedence:** CLI flags > environment variables > `pg_service.conf` > defaults.
**Password precedence:** connection string/password flag > `PGPASSWORD` env > `~/.pgpass`. Use `~/.pgpass` instead of `PGPASSWORD` in production — `PGPASSWORD` is visible in process listings (`ps aux`).

**Key flags:** `-h` host, `-p` port, `-U` user, `-d` database, `-w` no password prompt, `-W` force password prompt, `-1` single transaction, `-f` execute file, `-c` execute command, `-t` tuples only, `-x` expanded, `-A` unaligned, `-E` echo hidden queries (`\d` internals), `-L` log file, `-X` skip `~/.psqlrc`.

On connection failure: interactive mode keeps the previous connection; script mode closes it and all subsequent database commands fail until the next successful `\c`.

### 2. Inspect Database Objects (\d family)

| Command | Shows |
|---|---|
| `\d` | All tables, views, materialized views, sequences, foreign tables (equiv. `\dtvmsE`) |
| `\dP` | Partitioned tables |
| `\dt` | Tables only |
| `\dv` | Views only |
| `\di` | Indexes only |
| `\ds` | Sequences only |
| `\dm` | Materialized views only |
| `\det` | Foreign tables (mnemonic: "external tables") |
| `\dT` | Data types |
| `\df` | Functions (modifiers: `a`=aggregate, `n`=normal, `p`=procedure, `t`=trigger, `w`=window) |
| `\da` | Aggregate functions |
| `\dn` | Schemas |
| `\du` / `\dg` | Roles |
| `\db` | Tablespaces |
| `\dc` | Conversions |
| `\dD` | Domains |
| `\dl` | Large objects (alias for `\lo_list`) |
| `\dF` | Text search configurations |
| `\dFd` | Text search dictionaries |
| `\dFp` | Text search parsers |
| `\dFt` | Text search templates |
| `\des` | Foreign servers |
| `\deu` | User mappings |
| `\dew` | Foreign-data wrappers |
| `\dp` | Privileges (GRANT/REVOKE) |
| `\drds` | Per-role and per-database configuration settings |
| `\l` | List databases (accepts pattern: `\l test*`) |
| `\dA` | Access methods |
| `\dAc` / `\dAf` / `\dAo` / `\dAp` | Operator classes, families, operators, support functions |
| `\dC` | Type casts |
| `\dconfig` | Server configuration parameters (`\dconfig *` for all, PostgreSQL 16+) |
| `\dd` | Object descriptions (comments) |
| `\ddp` | Default privileges |
| `\dL` | Procedural languages |
| `\do` | Operators (accepts arg type patterns) |
| `\dO` | Collations |
| `\dP[itn]` | Partitioned tables (`t`=tables, `i`=indexes, `n`=nested) |
| `\drg` | Granted role memberships |
| `\dRp` / `\dRs` | Replication publications / subscriptions |
| `\dX` | Extended statistics |
| `\dx` | Installed extensions |
| `\dy` | Event triggers |
| `\sf[+]` | Show function definition |
| `\sv[+]` | Show view definition |
| `\z` | Privileges (alias for `\dp`) |

**Modifiers** (append to most `\d` commands):

- `+` — extra info (size, description): `\dt+`, `\l+`, `\du+`
- `S` — include system objects: `\dtS`, `\dfS+`
- `x` — expanded display mode: `\dt+x` (note: `\dx` is a different command; `x` must follow `S` or `+`)

Provide a name for details: `\d table_name` shows columns, types, indexes, constraints, foreign keys.

**Pattern matching in `\d` commands:**

- `*` = any sequence of characters, `?` = single character
- `.` separates schema from object: `\dt public.*` or `\dt my_schema.users`
- `..` separates database.schema.object: `\dt mydb.public.*` (db must match current db)
- Double quotes stop case folding and wildcard expansion: `\dt "FOO"` matches `FOO` not `foo`
- `$` is matched literally (not regex anchor)
- Regex chars like `[0-9]` work: `\dt user[0-9]*` matches `user1`, `user2`
- No pattern: shows all objects visible in current `search_path` (not all objects in DB)
- Use `*.*` to see all objects in all schemas regardless of visibility

> **When to load references:** Load `references/meta-commands-inspection.md` when you need the full `\d` command reference, all modifiers, or pattern matching details for exploring database schema.

### 3. Execute Queries

| Command | Action |
|---|---|
| `;` | Execute the current query buffer |
| `\g` | Execute (like `;`, but can add options) |
| `\gx` | Execute with expanded output (forces `\x on`) |
| `\g filename` | Execute and send output to file |
| `\g \| command` | Execute and pipe output to shell command |
| `\g (format=csv footer=off) file` | Execute with one-shot formatting options |
| `\gdesc` | Describe result columns without executing |
| `\gset [prefix]` | Execute and store results in psql variables |
| `\gexec` | Execute each cell of result as a SQL command |
| `\crosstabview` | Display result as crosstab (pivot table) |
| `\watch` | Re-execute query periodically |
| `\bind [params...]` | Use extended query protocol with parameters. Works with `\g`, `\gx`, and `\gset` |
| `\bind_named stmt_name [params...]` | Bind named prepared statement |
| `\parse stmt_name` | Create prepared statement from current query buffer |
| `\close_prepared stmt_name` | Close a prepared statement |
| `\;` | Append semicolon to buffer without executing |

> **When to load references:** Load `references/meta-commands-core.md` when you need exact syntax or behavioral details for any backslash command, query buffer behavior, or argument parsing rules.

### 4. Import / Export Data

```sql
-- Server-side (requires superuser for file access, uses server filesystem)
COPY table TO '/path/file.csv' WITH (FORMAT csv, HEADER true);
COPY table FROM '/path/file.csv' WITH (FORMAT csv, HEADER true);

-- Client-side (runs with client permissions, no superuser needed) — PREFERRED
\copy table TO '/path/file.csv' WITH (FORMAT csv, HEADER true)
\copy table FROM '/path/file.csv' WITH (FORMAT csv, HEADER true)
\copy (SELECT ...) TO '/path/output.csv' WITH (FORMAT csv, HEADER true)

-- Advanced: specific columns, NULL handling, custom delimiter
\copy table (col1, col2) FROM 'data.csv' WITH (FORMAT csv, HEADER true, NULL 'N/A')
```

`\copy` is the go-to for day-to-day work — it uses the client's filesystem and permissions, not the server's.

**`\copy` syntax detail:**

```
-- FROM (import): sources are 'filename', program 'command', stdin, pstdin
\copy table FROM 'file.csv' WITH (FORMAT csv, HEADER true) [ WHERE condition ]

-- TO (export): destinations are 'filename', program 'command', stdout, pstdout
\copy table TO 'file.csv' WITH (FORMAT csv, HEADER true)
```

For `\copy ... FROM stdin`, data rows continue until a line containing only `\.` is read or EOF is reached. Use `pstdin`/`pstdout` to always read/write psql's actual stdin/stdout regardless of `\o` setting.

**WARNING:** The `program` option executes a shell command. If constructed from user input, it can lead to command injection. Never concatenate untrusted data into the `program` string.

**Tip:** `\copy` takes the entire rest of the line as arguments (no variable interpolation). When you need variable interpolation or multi-line queries, use SQL `COPY ... TO STDOUT` with `\g` instead:

```sql
-- This allows variable interpolation and multi-line queries
COPY (SELECT * FROM :table WHERE id > :min_id) TO STDOUT WITH (FORMAT csv, HEADER true) \g /tmp/output.csv
```

### 5. Format Output

```
\a                  Toggle aligned/unaligned output
\x                  Toggle expanded display (vertical vs table)
\t                  Toggle tuples only (no headers/footers)
\pset format FORMAT  Set output format: aligned, asciidoc, csv, html, latex, latex-longtable, troff-ms, unaligned, wrapped
\pset border N       Set border style (0-2; 3 for latex data-row lines)
\pset null STRING    Display NULL as STRING
\pset pager [off]    Control pager usage
\pset title 'TEXT'   Set table title
\pset recordsep SEP  Set record separator for unaligned mode
\pset fieldsep SEP   Set field separator for unaligned mode (default: |)
\pset footer [on|off] Toggle row count footer
\pset columns N      Set target width for wrapped format
\pset csv_fieldsep C  Set CSV field separator (default: comma)
\pset numericlocale [on|off]  Toggle locale-specific number formatting
\pset linestyle STYLE Set border style: ascii, old-ascii, unicode
\pset pager_min_lines N  Minimum lines before pager activates
\pset xheader_width MODE  Expanded header width: full, column, page, or N (PostgreSQL 17+)
\H                   Toggle HTML output (shortcut)
\C [title]           Set table title (shortcut for \pset title)
\f [string]          Set field separator (shortcut for \pset fieldsep)
\T table_options     Set HTML table attributes (shortcut for \pset tableattr)
```

> **When to load references:** Load `references/meta-commands-formatting.md` when the user needs to control output format, use pipeline mode, `\watch`, or `\crosstabview`.

### 6. Scripting & Control Flow

```
\i filename         Execute file (relative to current working directory)
\ir filename        Execute file (relative to the script being processed)
\o [filename]       Redirect query output to file (or pipe with |cmd)
\o                   Stop output redirection
\qecho TEXT          Output text to redirected output
\echo TEXT           Output text to stdout (-n suppresses trailing newline)
\warn TEXT           Output text to stderr
\! command           Execute shell command
\cd [dir]            Change working directory
\set NAME VALUE      Set psql variable
\unset NAME          Unset psql variable
\prompt [TEXT] NAME  Prompt user for variable value
\getenv psql_var env_var   Copy environment variable into psql variable
\setenv name [value]       Set or unset environment variable
\p                  Print current query buffer
\w filename         Write query buffer to file (or pipe with |cmd)
```

**Conditional execution:**

```
\if EXPR
  \echo 'true branch'
\else
  \echo 'false branch'
\endif

\elif EXPR           Else-if inside \if block
```

`\if` and `\elif` evaluate their argument as a boolean. Valid values (case-insensitive, unambiguous prefix matching): `true`, `false`, `1`, `0`, `on`, `off`, `yes`, `no`. Expressions that don't evaluate to true/false generate a warning and are treated as false. Variable references in skipped lines are NOT expanded.

**Variables in SQL:**

- `:'varname'` — quoted string value (escapes embedded quotes) — SAFER
- `:"varname"` — double-quoted identifier (properly escapes embedded double quotes)
- `:'varname'::type` — with cast
- `:varname` — unquoted — can break SQL — UNSAFE
- `:{?varname}` — tests existence, expands to TRUE/FALSE

> **When to load references:** Load `references/cli-options-and-variables.md` when configuring psql startup behavior, writing scripts that depend on variable state, or customizing prompts. Load `references/tips-workflows.md` when the user asks how to accomplish a specific task with psql.

### 7. Pipeline Mode (PostgreSQL 14+)

```
\startpipeline
  SELECT $1 \bind 42 \sendpipeline
  SELECT $1 \bind 100 \sendpipeline
  \getresults
\endpipeline
```

Pipeline mode sends multiple queries without waiting for each result, reducing round-trip latency. All queries use the extended query protocol.

**Pipeline commands:**

- `\startpipeline` — begin pipeline block
- `\endpipeline` — end pipeline block and process remaining results
- `\sendpipeline` — append current query buffer to pipeline without waiting
- `\syncpipeline` — send sync message without ending pipeline
- `\flushrequest` — request server flush without sync
- `\flush` — manually push unsent data to server
- `\getresults [N]` — read pending results (N=0 or omitted means all)

**Pipeline limitations:**

- `COPY` is not supported in pipeline mode
- Meta-commands like `\g`, `\gx`, `\gdesc` are not allowed inside a pipeline
- All queries use the extended query protocol
- Use `\bind`, `\bind_named`, `\parse`, `\close_prepared`, or `\sendpipeline` within pipelines
- A `%P` prompt variable shows pipeline status (`on`, `off`, or `abort`)

### 8. Large Objects

```
\lo_import filename [comment]   Import file as large object, returns OID
\lo_export loid filename        Export large object to file
\lo_list[x+]                    List all large objects
\lo_unlink loid                 Delete large object
```

Large object OIDs are persistent references. Always associate a human-readable comment on import. Use `\lo_list` to find OIDs.

### 9. Session Management

```
\c [dbname [user]]  Connect to database (or reconnect)
\conninfo           Display connection info (includes SSL info)
\encoding [ENC]     Set or show client encoding
\password [USER]    Change password (does NOT appear in command history or server log)
\q                   Quit psql. In a script file, only that script is terminated.
\r                   Reset (clear) the query buffer
\e                   Edit query buffer in external editor
\ef [FUNCNAME]       Edit function definition
\ev [VIEWNAME]       Edit view definition
\sf[+] FUNCNAME      Show function definition (read-only)
\sv[+] VIEWNAME      Show view definition (read-only)
\s [FILE]            Print command history (or save to file)
\restrict KEY        Enter restricted mode (only \unrestrict allowed)
\unrestrict KEY      Exit restricted mode
\timing [on|off]     Toggle query execution time display (milliseconds)
\errverbose          Repeat last error at maximum verbosity
\? [topic]           Help: commands, options, or variables
\h [command]         SQL syntax help (use * for all: \h *)
\copyright           Show PostgreSQL copyright
```

### 10. \watch Syntax

```
\watch [i[nterval]=SECONDS] [c[ount]=TIMES] [m[in_rows]=N]
```

Re-executes the current query buffer at the specified interval (default 2 seconds). Stops after `count` iterations or when the query returns fewer than `min_rows` rows. Useful for monitoring live queries or waiting for a condition to become true.

## When to Use What

| Scenario | Recommended Command |
|---|---|
| Quick table inspection | `\d table_name` |
| List all tables in schema | `\dt schema.*` |
| Check indexes on a table | `\di+ table_name*` or `\d table_name` |
| Export query to CSV | `\copy (SELECT ...) TO 'file.csv' WITH (FORMAT csv, HEADER)` |
| Import CSV into table | `\copy table FROM 'file.csv' WITH (FORMAT csv, HEADER)` |
| Run migration script | `psql -1 -f migration.sql dbname` |
| Watch a live query | `SELECT ... \watch 5` |
| Pivot query results | `SELECT ... \crosstabview` |
| Script with conditional logic | `\if :var ... \endif` |
| Batch-insert many rows | Use `\startpipeline` / `\endpipeline` |
| SQL syntax help | `\h CREATE TABLE` |
| psql command help | `\? commands` |
| Check query execution time | `\timing on` then run query |
| Debug error details | `\errverbose` |
| Handle large result sets | `\set FETCH_COUNT 1000` then run query |
| Auto-savepoint on errors | `\set ON_ERROR_ROLLBACK on` then use transactions |

## Pitfalls

### Security Risks

| Command | Risk | Mitigation |
|---|---|---|
| `\gexec` | Executes generated SQL without confirmation | Always inspect the generating query first by running it without `\gexec`; set `ON_ERROR_STOP on` |
| `\! command` | Arbitrary shell execution | No sandboxing; commands run with psql user's full privileges |
| `\copy ... program 'cmd'` | Shell command injection if filename comes from user input | Never concatenate untrusted input into the `program` string |
| `\deu+` | May display remote user passwords | Avoid using `\deu+` in shared/piped output; use `\deu` without `+` |
| `DELETE`/`UPDATE` without `WHERE` | Affects every row in the table | Always use `WHERE`; wrap in `BEGIN`/`ROLLBACK` to preview |
| `DROP DATABASE/TABLE` | Irreversible data loss | Verify you're on the correct database with `\conninfo` first |
| `PGPASSWORD` env var | Visible in process listings (`ps aux`) | Use `~/.pgpass` with `chmod 600` in production |
| Password in connection URI | Visible in shell history and process listings | Use `~/.pgpass` instead |

### Variable Interpolation Safety

psql variables are **plain text substitution**, not parameterized queries:

```sql
-- UNSAFE: if :name contains "Robert'); DROP TABLE users;--" it will execute the injection
SELECT * FROM users WHERE name = :'name';

-- SAFER: use \prompt for interactive input (user sees what they typed)
\prompt 'Enter name: ' search_name
SELECT * FROM users WHERE name = :'search_name';

-- SAFEST: use \bind for programmatic parameter passing (truly parameterized)
SELECT * FROM users WHERE name = $1;
\bind 'Robert' \g
```

The `:'varname'` form (quoted) is always safer than `:varname` (unquoted), because unquoted substitution can break SQL syntax or enable injection. Use `:"varname"` for identifiers (table/column names) — it properly escapes embedded double quotes.

### Comment Handling

psql handles two comment styles differently:

- **C-style block comments** (`/* ... */`): Passed to the server for processing and removal.
- **SQL-standard comments** (`--`): Removed by psql itself, before sending to the server.

This distinction matters when writing scripts that rely on comment behavior — only SQL-standard comments are stripped client-side.

### Version Compatibility

psql works best with servers of the same or an older major version. Backslash commands (especially `\d` family) may fail with newer server versions. When connecting to multiple server versions, use the newest available psql client. The `\d` commands generally work with servers back to version 9.2.

### Connection Failure Behavior

On connection failure: interactive mode keeps the previous connection; script mode closes it and all subsequent database commands fail until the next successful `\c`. Always check `\conninfo` before destructive operations.

> **When to load references:** Load `references/tips-advanced.md` for lock analysis, query plan inspection, `EXPLAIN`, `ECHO_HIDDEN`, `ON_ERROR_STOP` patterns, `search_path` safety, and common gotchas.

## Verification

### Verify psql is installed

```bash
psql --version
# Expected: psql (PostgreSQL) 16.x (or your installed version)
```

### Verify connection

```sql
\conninfo
-- Expected output:
-- You are connected to database "mydb" as user "postgres" on host "localhost" at port "5432".
-- SSL connection (protocol: TLSv1.3, ...)
```

### Verify database listing

```sql
\l
-- Expected: list of databases with Name, Owner, Encoding, Collate, Ctype, Access privileges
```

### Verify table inspection

```sql
\dt
-- Expected: list of tables in current search_path

\d table_name
-- Expected: columns, types, indexes, constraints, foreign keys for the table
```

### Verify script execution (single transaction)

```bash
psql -1 -f migration.sql dbname
# Expected: no errors, transaction committed. If any statement fails, all roll back.
```

### Verify data export

```sql
\copy (SELECT count(*) FROM users) TO 'check.csv' WITH (FORMAT csv)
-- Then verify file exists and has expected content
\! cat check.csv
```

### Verify query timing

```sql
\timing on
SELECT count(*) FROM users;
-- Expected: Time: X.XXX ms
```

## Reference Files

Load these reference files from the `references/` directory when deeper detail is needed:

| File | When to Load |
|---|---|
| `references/meta-commands-core.md` | Need exact syntax or behavioral details for any backslash command, query buffer behavior, argument parsing, connection management, `\copy` syntax, or scripting commands (`\if`, `\i`, `\o`, backquote expansion) |
| `references/meta-commands-inspection.md` | Exploring database schema; need full `\d` command reference, modifiers (`S`, `+`, `x`), or pattern matching rules |
| `references/meta-commands-formatting.md` | Need to control output format, use pipeline mode, `\watch`, `\crosstabview`, or session management (`\e`, `\ef`, `\ev`, `\timing`) |
| `references/cli-options-and-variables.md` | Configuring psql startup behavior, writing scripts that depend on variable state, customizing prompts, or using `~/.psqlrc` |
| `references/tips-workflows.md` | User asks how to accomplish a specific task with psql; practical workflows, scripting patterns, output control for automation |
| `references/tips-advanced.md` | Lock analysis, query plan inspection (`EXPLAIN`), `ECHO_HIDDEN`, safety best practices, `ON_ERROR_STOP`, transaction patterns, `search_path` safety, troubleshooting |

## External References

- [PostgreSQL Client Applications (psql)](https://www.postgresql.org/docs/current/app-psql.html)
- [Official PostgreSQL Documentation](https://www.postgresql.org/docs/current/index.html)
- [The SQL Language](https://www.postgresql.org/docs/current/sql.html)
- [SQL Syntax](https://www.postgresql.org/docs/current/sql-syntax.html)
- [SQL Commands](https://www.postgresql.org/docs/current/sql-commands.html)
- [PostgreSQL Wiki](https://wiki.postgresql.org/)

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- No live secrets are included in this skill; all passwords are shown as `YOUR_PASSWORD` placeholders.
