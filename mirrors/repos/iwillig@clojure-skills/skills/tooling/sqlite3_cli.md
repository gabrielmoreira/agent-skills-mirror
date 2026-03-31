---
name: sqlite3_cli
description: |
  Command-line interface for SQLite databases with SQL execution, schema inspection, 
  data import/export, and multiple output formats. Use when working with SQLite databases 
  from the command line, debugging database issues, importing/exporting data, running 
  SQL queries interactively, or when the user mentions sqlite3, SQLite CLI, database 
  shell, SQL console, or database debugging.
---

# SQLite3 Command-Line Interface

The `sqlite3` command-line tool is the official CLI for SQLite databases. It provides an interactive shell for executing SQL, inspecting schemas, importing/exporting data, and debugging database issues.

## Quick Start

Basic SQLite3 usage patterns:

```bash
# Open a database (creates if doesn't exist)
sqlite3 mydata.db

# Execute SQL from command line
sqlite3 mydata.db "SELECT * FROM users;"

# Use in-memory database
sqlite3 :memory: "CREATE TABLE test (x INT); INSERT INTO test VALUES (1), (2); SELECT SUM(x) FROM test;"
# => 3

# Read SQL from file
sqlite3 mydata.db < schema.sql

# Pipe SQL commands
echo "SELECT * FROM users;" | sqlite3 mydata.db

# Multiple SQL statements
sqlite3 mydata.db <<'EOF'
CREATE TABLE users (id INT PRIMARY KEY, name TEXT);
INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob');
SELECT * FROM users;
EOF
```

**Key benefits:**
- **No setup required** - SQLite is embedded, no server needed
- **Multiple output formats** - CSV, JSON, markdown, HTML, and more
- **Interactive mode** - Full REPL with tab completion
- **Import/export** - CSV, SQL dump, backup/restore
- **Schema inspection** - View tables, indexes, triggers
- **Query planning** - EXPLAIN QUERY PLAN for optimization

## Core Concepts

### Database Files and Special Names

SQLite stores databases in single files:

```bash
# Create/open a file-based database
sqlite3 myapp.db

# Use in-memory database (lost on exit)
sqlite3 :memory:

# Read-only access
sqlite3 -readonly mydata.db

# Create only if doesn't exist
sqlite3 -ifexists mydata.db "SELECT 1;"
# Error: unable to open database file (if doesn't exist)
```

**File locations:**
- Current directory if relative path: `sqlite3 data.db`
- Absolute path: `sqlite3 /var/db/myapp.db`
- `:memory:` - Special in-memory database

### Interactive vs Command-Line Mode

Two primary modes of operation:

```bash
# Command-line mode: Execute and exit
sqlite3 mydata.db "SELECT COUNT(*) FROM users;"
# => 42

# Interactive mode: Opens a REPL
sqlite3 mydata.db
# sqlite> SELECT * FROM users LIMIT 5;
# sqlite> .quit

# Force interactive mode
sqlite3 -interactive mydata.db < script.sql
```

**When to use each:**
- **Command-line mode**: Scripts, automation, one-off queries
- **Interactive mode**: Exploring, debugging, complex workflows

### Dot Commands

SQLite's REPL has special commands starting with `.` (not SQL):

```bash
sqlite3 mydata.db
sqlite> .help              # Show all dot commands
sqlite> .tables            # List all tables
sqlite> .schema users      # Show CREATE statement for table
sqlite> .quit              # Exit the shell
```

**Important:** Dot commands are NOT SQL - they're shell commands.

## Command-Line Options

### Output Format Options

Control how query results are displayed:

```bash
# CSV output
sqlite3 -csv mydata.db "SELECT * FROM users;"
# id,name,email
# 1,Alice,alice@example.com
# 2,Bob,bob@example.com

# JSON output
sqlite3 -json mydata.db "SELECT * FROM users LIMIT 2;"
# [{"id":1,"name":"Alice","email":"alice@example.com"},
#  {"id":2,"name":"Bob","email":"bob@example.com"}]

# Markdown table
sqlite3 -markdown mydata.db "SELECT name, email FROM users;"
# | name  |        email        |
# |-------|---------------------|
# | Alice | alice@example.com   |
# | Bob   | bob@example.com     |

# HTML table
sqlite3 -html mydata.db "SELECT * FROM users LIMIT 3;"

# Column mode (good for terminals)
sqlite3 -column -header mydata.db "SELECT * FROM users;"
# id  name   email               
# --  -----  --------------------
# 1   Alice  alice@example.com   
# 2   Bob    bob@example.com     

# Box drawing characters
sqlite3 -box mydata.db "SELECT * FROM users LIMIT 3;"
# ┌────┬───────┬───────────────────┐
# │ id │ name  │       email       │
# ├────┼───────┼───────────────────┤
# │ 1  │ Alice │ alice@example.com │
# │ 2  │ Bob   │ bob@example.com   │
# └────┴───────┴───────────────────┘
```

**Available formats:**
- `list` (default): pipe-separated `value1|value2|value3`
- `csv`: comma-separated values
- `json`: JSON array of objects
- `markdown`: Markdown table
- `column`: Aligned columns
- `box`: Unicode box drawing
- `html`: HTML table
- `line`: One value per line with labels
- `tabs`: Tab-separated values
- `quote`: SQL-quoted strings

### Common Options

```bash
# Show column headers
sqlite3 -header mydata.db "SELECT * FROM users;"

# Echo SQL before executing (debugging)
sqlite3 -echo mydata.db "SELECT COUNT(*) FROM users;"
# SELECT COUNT(*) FROM users;
# 42

# Stop on first error (useful in scripts)
sqlite3 -bail mydata.db < script.sql

# Run command before entering interactive mode
sqlite3 -cmd ".mode column" -cmd ".headers on" mydata.db

# Initialize from file (e.g., set up environment)
cat > .sqliterc <<EOF
.mode column
.headers on
.timer on
EOF
sqlite3 -init .sqliterc mydata.db
```

## Interactive Mode (Dot Commands)

### Schema Inspection

View database structure:

```sql
-- List all tables
.tables
-- => users  orders  products

-- List tables matching pattern
.tables user%
-- => users  user_sessions

-- Show table schema
.schema users
-- => CREATE TABLE users (
--      id INTEGER PRIMARY KEY,
--      name TEXT NOT NULL,
--      email TEXT UNIQUE
--    );

-- Show all schemas
.fullschema

-- Show all indexes
.indexes
-- => sqlite_autoindex_users_1

-- Show indexes for specific table
.indexes users
```

### Database Information

```sql
-- Show database files
.databases
-- => main: /path/to/mydata.db

-- Database statistics
.dbinfo
-- => database page size:  4096
--    write format:        1
--    ...

-- Show current settings
.show
-- => echo: off
--    explain: auto
--    headers: on
--    mode: column
--    ...
```

### Output Control

Configure output formatting:

```sql
-- Change output mode
.mode csv
.mode json
.mode markdown
.mode column
.mode box

-- Show/hide headers
.headers on
.headers off

-- Set NULL display value
.nullvalue NULL
SELECT id, optional_field FROM users;
-- => 1|Alice
--    2|NULL

-- Set column separator (list mode)
.separator ","
.separator "\t"

-- Set output to file (next query only)
.once output.txt
SELECT * FROM users;

-- Send all output to file
.output results.txt
SELECT * FROM orders;
SELECT * FROM products;
.output stdout  -- Back to console
```

### Data Import/Export

#### Exporting Data

```sql
-- Dump entire database as SQL
.dump
-- => PRAGMA foreign_keys=OFF;
--    BEGIN TRANSACTION;
--    CREATE TABLE users (...);
--    INSERT INTO users VALUES (1, 'Alice', ...);
--    ...

-- Dump specific table
.dump users

-- Dump schema only (no data)
.schema

-- Export as CSV
.mode csv
.headers on
.once users.csv
SELECT * FROM users;

-- Export as JSON
.mode json
.once users.json
SELECT * FROM users;
```

#### Importing Data

```sql
-- Import CSV file
CREATE TABLE imported (name TEXT, age INT, city TEXT);
.mode csv
.import data.csv imported

-- Import with headers (skip first line)
-- Note: First line becomes data if no --skip option
-- For files with headers, create table with matching columns first

-- Import tab-separated values
.mode tabs
.import data.tsv imported

-- Read and execute SQL file
.read schema.sql
.read seed_data.sql
```

**CSV Import Gotchas:**
- Table must exist before import
- Column count must match
- First row treated as data (not headers) by default
- Use `.mode csv` before `.import`

### Backup and Restore

```sql
-- Backup database to file
.backup mybackup.db

-- Backup specific database (if using ATTACH)
.backup main mybackup.db

-- Restore from backup
.restore mybackup.db
```

**Difference from .dump:**
- `.backup` creates binary copy (fast, exact)
- `.dump` creates SQL script (portable, editable)

### Query Optimization

```sql
-- Show query execution plan
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'alice@example.com';
-- => QUERY PLAN
--    `--SEARCH users USING INDEX sqlite_autoindex_users_1 (email=?)

-- Enable automatic EXPLAIN
.eqp on
SELECT * FROM large_table WHERE indexed_col = 123;
-- Shows query plan before results

-- Detailed explain
.eqp full
```

### Other Useful Commands

```sql
-- Execute shell command
.shell ls -la
.shell pwd

-- Change working directory
.cd /path/to/data

-- Set timer (show query execution time)
.timer on
SELECT COUNT(*) FROM large_table;
-- => 42
--    Run Time: real 0.234 user 0.210000 sys 0.020000

-- Run integrity check
PRAGMA integrity_check;
```

## Common Workflows

### Exploring a New Database

```bash
sqlite3 unknown.db
```

```sql
-- What tables exist?
.tables

-- What's the schema?
.schema

-- Sample data from each table
SELECT * FROM users LIMIT 5;
SELECT * FROM orders LIMIT 5;

-- How many rows?
SELECT COUNT(*) FROM users;

-- What indexes exist?
.indexes

-- Any foreign keys?
PRAGMA foreign_key_list(orders);
```

### Creating and Populating a Database

```bash
# Create schema
sqlite3 myapp.db <<'EOF'
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
EOF

# Import data from CSV
cat > users.csv <<'EOF'
username,email
alice,alice@example.com
bob,bob@example.com
charlie,charlie@example.com
EOF

sqlite3 myapp.db <<'EOF'
.mode csv
.import users.csv users_temp

INSERT INTO users (username, email)
SELECT username, email FROM users_temp;

DROP TABLE users_temp;
EOF
```

### Debugging Performance Issues

```sql
-- Enable query plans and timing
.eqp on
.timer on

-- Check if indexes are being used
SELECT * FROM users WHERE email = 'alice@example.com';
-- QUERY PLAN
-- `--SEARCH users USING INDEX idx_users_email (email=?)

-- Identify slow queries
SELECT * FROM large_table WHERE unindexed_column = 'value';
-- Run Time: real 2.345 user 2.100000 sys 0.240000
-- QUERY PLAN
-- `--SCAN large_table  (no index!)

-- Create index to fix
CREATE INDEX idx_large_table_col ON large_table(unindexed_column);

-- Verify improvement
SELECT * FROM large_table WHERE unindexed_column = 'value';
-- Run Time: real 0.012 user 0.010000 sys 0.002000
```

### Exporting Data for Analysis

```bash
# Export as JSON for processing with jq
sqlite3 -json mydata.db "SELECT * FROM users;" | jq '.[] | .email'

# Export as CSV for spreadsheets
sqlite3 -csv -header mydata.db "SELECT * FROM sales_report;" > report.csv

# Export as Markdown for documentation
sqlite3 -markdown -header mydata.db "SELECT * FROM config;" > config.md

# Complex query to multiple formats
sqlite3 mydata.db <<'EOF'
.mode csv
.headers on
.once report.csv
SELECT u.username, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id
ORDER BY post_count DESC;

.mode json
.once report.json
SELECT u.username, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id
ORDER BY post_count DESC;
EOF
```

### Scripting with SQLite

```bash
#!/bin/bash
# Automated database maintenance script

DB="myapp.db"

# Check integrity
echo "Checking database integrity..."
sqlite3 "$DB" "PRAGMA integrity_check;" | grep -q "ok" || {
  echo "Database integrity check failed!"
  exit 1
}

# Backup
BACKUP="backups/$(date +%Y%m%d_%H%M%S).db"
mkdir -p backups
sqlite3 "$DB" ".backup '$BACKUP'"
echo "Backed up to $BACKUP"

# Clean old data
echo "Cleaning old records..."
sqlite3 "$DB" "DELETE FROM logs WHERE created_at < date('now', '-30 days');"

# Optimize
echo "Optimizing database..."
sqlite3 "$DB" "VACUUM;"
sqlite3 "$DB" "ANALYZE;"

echo "Maintenance complete."
```

## Best Practices

**DO:**
- Use `.mode column` and `.headers on` for interactive exploration
- Enable `.timer on` when optimizing queries
- Use `.eqp on` to verify indexes are being used
- Backup databases with `.backup` before major changes
- Use `:memory:` for testing and temporary work
- Check `.dbinfo` to understand database characteristics
- Use `.schema` to understand table structure before querying
- Export data with appropriate format (CSV for spreadsheets, JSON for code)

**DON'T:**
- Mix dot commands and SQL in scripts (separate them clearly)
- Forget to enable `.headers on` when exporting CSV
- Import CSVs without creating table first
- Ignore query plans for slow queries
- Use text comparison on `.dump` output (use `.backup` instead)
- Assume first CSV row is skipped (it's imported as data)
- Use interactive mode for automation (use command-line mode)

## Common Issues

### "Parse error: near line X"

SQL syntax error or mixing dot commands with SQL:

```bash
# Wrong - dot command in SQL script
sqlite3 mydata.db <<'EOF'
SELECT * FROM users;
.mode csv
SELECT * FROM orders;
EOF

# Right - separate dot commands from SQL
sqlite3 -csv mydata.db <<'EOF'
SELECT * FROM users;
EOF
```

### "Error: no such table"

Table doesn't exist or wrong database:

```bash
# Check what tables exist
sqlite3 mydata.db ".tables"

# Verify database file
sqlite3 mydata.db ".databases"

# Create table if missing
sqlite3 mydata.db "CREATE TABLE IF NOT EXISTS users (...);"
```

### CSV Import Issues

```bash
# Problem: Imported CSV has wrong data
# Cause: Mode not set to CSV

# Wrong
sqlite3 mydata.db ".import data.csv users"
# Imports with pipe separator (default mode)

# Right
sqlite3 mydata.db <<'EOF'
.mode csv
.import data.csv users
EOF
```

### "Database is locked"

Another process has the database open:

```bash
# Check for locks
lsof mydata.db

# Use read-only mode if only querying
sqlite3 -readonly mydata.db "SELECT * FROM users;"

# Set timeout for locks (milliseconds)
sqlite3 mydata.db <<'EOF'
.timeout 5000
-- Your SQL here
EOF
```

## Advanced Features

### Attaching Multiple Databases

```sql
-- Attach additional database
ATTACH DATABASE 'other.db' AS other;

-- Query across databases
SELECT u.name, o.total
FROM users u
JOIN other.orders o ON u.id = o.user_id;

-- Show attached databases
.databases
-- => main: /path/to/mydata.db
--    other: /path/to/other.db

-- Detach when done
DETACH DATABASE other;
```

### Working with JSON (SQLite 3.38+)

SQLite has built-in JSON functions:

```sql
-- Store JSON data
CREATE TABLE events (id INT, data JSON);
INSERT INTO events VALUES (1, '{"type":"login","user":"alice"}');

-- Extract JSON fields
SELECT id, json_extract(data, '$.type') as event_type FROM events;
-- => 1|login

-- Query JSON arrays
INSERT INTO events VALUES (2, '{"type":"order","items":["a","b","c"]}');
SELECT json_each.value 
FROM events, json_each(data, '$.items')
WHERE id = 2;
-- => a
--    b
--    c
```

### Configuration File (~/.sqliterc)

Create persistent settings:

```bash
cat > ~/.sqliterc <<'EOF'
-- SQLite initialization file
.mode column
.headers on
.timer on
.nullvalue NULL

-- Useful aliases (SQLite doesn't support these directly,
-- but you can use .read with files containing common queries)
EOF

# Now every sqlite3 session starts with these settings
sqlite3 mydata.db
# Already in column mode with headers and timer!
```

## Summary

The sqlite3 CLI is a powerful tool for database work:

**Key Commands:**
- `sqlite3 database.db` - Open database
- `sqlite3 :memory:` - Temporary database
- `.tables` - List tables
- `.schema TABLE` - Show structure
- `.mode FORMAT` - Set output format
- `.import FILE TABLE` - Import CSV
- `.dump` - Export as SQL
- `.backup FILE` - Binary backup
- `.eqp on` - Show query plans

**Common Patterns:**
```bash
# Query and output JSON
sqlite3 -json db.db "SELECT * FROM users;"

# Interactive exploration
sqlite3 db.db
sqlite> .mode column
sqlite> .headers on
sqlite> SELECT * FROM users LIMIT 10;

# Import CSV
sqlite3 db.db <<'EOF'
CREATE TABLE data (...);
.mode csv
.import data.csv data
EOF

# Backup
sqlite3 db.db ".backup backup.db"
```

Use sqlite3 CLI for database exploration, debugging, scripting, and data exchange. Its multiple output formats and rich command set make it invaluable for SQLite development.
