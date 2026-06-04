# Database Schema Naming Conventions

**Scope**: Workspace root (authoritative; may be extended hierarchically by modules)
**Purpose**: Establish naming conventions for database schema elements enabling automated discovery, documentation, and testing
**Convention**: Semantic names with clear prefixes: `tbl_` for tables, `col_` for columns, `idx_` for indices
**Last Updated**: 2026-06-02

---

## Contents

| Section | What's here |
|---|---|
| [Table Naming](#table-naming) | Conventions for table names |
| [Column Naming](#column-naming) | Conventions for column names |
| [Index Naming](#index-naming) | Conventions for database indices |
| [Constraint Naming](#constraint-naming) | Foreign keys, unique constraints |
| [Migration Naming](#migration-naming) | Migration file naming and versioning |
| [Timestamp & Standard Columns](#timestamp--standard-columns) | Required columns every table must have |
| [Type Conventions](#type-conventions) | UUID, ENUM, JSON handling |
| [Hierarchical Inheritance](#hierarchical-inheritance) | Module-level schema extensions |
| [Best Practices](#best-practices) | When and how to use the system |

---

## Table Naming

### Pattern: `tbl_{resource_name}`

**Rules:**
- Prefix: `tbl_` (two-letter prefix for searchability)
- Use singular noun: `tbl_user`, not `tbl_users`
- Snake case: `tbl_user_profile`, not `tbl_userProfile`
- Searchable: enables grep `grep tbl_user` to find all user tables

**Examples:**

| Resource | Table Name | Purpose |
|----------|-----------|---------|
| User account | `tbl_user` | Core user data |
| User profile | `tbl_user_profile` | Extended user attributes |
| Product | `tbl_product` | Product catalog |
| Order | `tbl_order` | Order records |
| Order item | `tbl_order_item` | Line items in orders |
| Payment | `tbl_payment` | Payment transactions |
| Invoice | `tbl_invoice` | Billing invoices |
| Session | `tbl_session` | User sessions |

---

## Column Naming

### Pattern: `col_{field_name}`

**Rules:**
- Use snake_case: `col_first_name`, not `col_firstName`
- Be explicit: `col_email_address`, not `col_email`
- Include unit in name if relevant: `col_created_at_utc`, `col_duration_seconds`
- Foreign keys: `col_{resource}_id`, not `col_{resource}_fk` (e.g., `col_user_id`)
- Boolean flags: `col_is_{state}` (e.g., `col_is_active`, `col_is_verified`)

**Standard Columns Every Table Must Have:**

| Column | Type | Purpose | Indexed |
|--------|------|---------|---------|
| `id` | UUID v7 / BIGINT | Primary key | ✅ (PRIMARY) |
| `col_created_at_utc` | TIMESTAMP | Creation timestamp | ✅ |
| `col_updated_at_utc` | TIMESTAMP | Last update timestamp | ✅ |
| `col_deleted_at_utc` | TIMESTAMP / NULL | Soft delete flag | ✅ |

**Column Type Reference:**

| Type | Usage | Example |
|------|-------|---------|
| `UUID` | Primary/foreign keys | `id`, `col_user_id` |
| `VARCHAR(255)` | Strings (email, name, etc.) | `col_email_address`, `col_first_name` |
| `TEXT` | Long text (descriptions, etc.) | `col_description`, `col_content` |
| `BOOLEAN` | True/false flags | `col_is_active`, `col_is_verified` |
| `INT` / `BIGINT` | Numbers | `col_quantity`, `col_score` |
| `DECIMAL(10, 2)` | Money/precise decimals | `col_price`, `col_balance` |
| `TIMESTAMP` | Timestamps (always UTC) | `col_created_at_utc`, `col_published_at_utc` |
| `JSONB` | Structured data (PostgreSQL) | `col_metadata`, `col_configuration` |
| `ENUM` | Fixed set of values | `col_status`, `col_role` |

---

## Index Naming

### Pattern: `idx_{table}_{column(s)}`

**Rules:**
- Prefix: `idx_` (searchable prefix)
- Include table name: `idx_tbl_order_col_user_id`
- Multiple columns: `idx_tbl_order_col_user_id_col_status`
- Composite indices: List columns in usage order

**Types:**

| Type | Pattern | Purpose | Example |
|------|---------|---------|---------|
| Primary Key | PRIMARY | Unique identifier | `PRIMARY KEY (id)` |
| Unique Index | `idx_unique_{table}_{column}` | Unique constraint | `idx_unique_tbl_user_col_email` |
| Foreign Key Index | `idx_fk_{table}_{column}` | FK lookup performance | `idx_fk_tbl_order_col_user_id` |
| Search Index | `idx_{table}_{column}` | Query performance | `idx_tbl_user_col_created_at` |
| Composite Index | `idx_{table}_{col1}_{col2}` | Multi-column queries | `idx_tbl_order_col_user_id_col_status` |

**When to Index:**

✅ **Always index:**
- Foreign key columns
- Columns used in WHERE clauses
- Columns used in ORDER BY
- Columns used in JOINs

❌ **Avoid over-indexing:**
- Columns with low cardinality (booleans, enums)
- Columns that are rarely queried
- Large columns (TEXT, JSONB) unless necessary

---

## Constraint Naming

### Foreign Key: `fk_{child_table}_{column}_{parent_table}`

```sql
ALTER TABLE tbl_order
ADD CONSTRAINT fk_tbl_order_col_user_id_tbl_user
FOREIGN KEY (col_user_id) REFERENCES tbl_user(id);
```

### Unique Constraint: `uq_{table}_{column}`

```sql
ALTER TABLE tbl_user
ADD CONSTRAINT uq_tbl_user_col_email UNIQUE (col_email_address);
```

### Check Constraint: `ck_{table}_{condition}`

```sql
ALTER TABLE tbl_product
ADD CONSTRAINT ck_tbl_product_col_price_positive CHECK (col_price > 0);
```

---

## Migration Naming

### Pattern: `YYYYMMDDHHMMSS_{kebab-case-description}.sql`

**Rules:**
- Timestamp: Use UTC timestamp to ensure global ordering
- Description: Describe the change in kebab-case
- Append-only: Never modify a committed migration
- Reversible: Every migration must have a corresponding `DOWN` statement

**Examples:**

```
migrations/
├── 20260601120000_create_tbl_user.sql
├── 20260601120100_create_tbl_user_profile.sql
├── 20260602081500_add_col_verification_token_to_tbl_user.sql
├── 20260602083000_create_idx_tbl_user_col_email.sql
├── 20260602090000_create_tbl_order.sql
└── 20260602090100_create_fk_tbl_order_col_user_id.sql
```

**Migration Template:**

```sql
-- UP: Create new table
CREATE TABLE tbl_user (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  col_email_address VARCHAR(255) NOT NULL,
  col_first_name VARCHAR(255),
  col_last_name VARCHAR(255),
  col_created_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  col_updated_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  col_deleted_at_utc TIMESTAMP NULL
);

CREATE INDEX idx_tbl_user_col_email ON tbl_user(col_email_address);
CREATE INDEX idx_tbl_user_col_created_at ON tbl_user(col_created_at_utc);

-- DOWN: Drop table
DROP TABLE IF EXISTS tbl_user CASCADE;
```

---

## Timestamp & Standard Columns

Every table must include these three columns:

```sql
id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
col_created_at_utc    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
col_updated_at_utc    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
col_deleted_at_utc    TIMESTAMP NULL DEFAULT NULL  -- Soft delete support
```

**Why:**
- `id`: Globally unique primary key (UUID v7 enables sharding)
- `col_created_at_utc`: Audit trail and sorting
- `col_updated_at_utc`: Track changes for sync/replication
- `col_deleted_at_utc`: Soft delete support without losing data

**Rules:**
- Always UTC: Never use local time
- `col_updated_at_utc` auto-updates on every write (database trigger or application)
- `col_deleted_at_utc` is NULL for active records; set to timestamp for deleted
- Never hard-delete; always soft-delete via `col_deleted_at_utc`

---

## Type Conventions

### UUID

```sql
col_user_id    UUID NOT NULL,  -- Always UUID for primary/foreign keys
col_session_id UUID NOT NULL
```

**Advantages:**
- Globally unique (no collisions across distributed systems)
- Supports sharding (not sequential like SERIAL)
- UUIDv7 includes timestamp (sortable)

### ENUM

```sql
-- Define enum type
CREATE TYPE enum_order_status AS ENUM ('pending', 'shipped', 'delivered', 'cancelled');

-- Use in table
CREATE TABLE tbl_order (
  id UUID PRIMARY KEY,
  col_status enum_order_status NOT NULL DEFAULT 'pending'
);

-- Query: SELECT * FROM tbl_order WHERE col_status = 'shipped';
```

### JSONB

```sql
-- Store structured data
CREATE TABLE tbl_user (
  id UUID PRIMARY KEY,
  col_metadata JSONB DEFAULT '{}',  -- Flexible attributes
  col_settings JSONB DEFAULT '{"theme": "light", "notifications": true}'
);

-- Query: SELECT * FROM tbl_user WHERE col_metadata->>'role' = 'admin';
```

---

## Hierarchical Inheritance

**Default behavior:** All schemas inherit the master naming convention above.

**Module-level override/extension:**
- Any module may create `.ai/database-schema.md` in its directory
- Module schemas extend the master table without duplicating
- To create a custom table pattern, add it to the module's `.ai/database-schema.md`:

```markdown
# Custom Tables for [Module]

| Table | Purpose | Columns |
|-------|---------|---------|
| `tbl_audit_log` | Audit trail | id, col_action, col_user_id, col_created_at_utc |
| `tbl_webhook_event` | Webhook events | id, col_event_type, col_payload, col_created_at_utc |
```

---

## Best Practices

### Do's

✅ **Do:**
- Use the `tbl_`, `col_`, `idx_` prefixes consistently
- Make table/column names searchable and grep-able
- Always include the three standard columns (id, created_at, updated_at)
- Use migrations for every schema change
- Version migrations with timestamps (UTC)
- Create indices on foreign keys and frequently queried columns
- Soft-delete using `col_deleted_at_utc`
- Use JSONB for flexible attributes (PostgreSQL)
- Document why an index exists (in migration comments)

### Don'ts

❌ **Don't:**
- Hard-delete data; always soft-delete
- Use `SERIAL`/`AUTO_INCREMENT` for primary keys (use UUID instead)
- Create indices on columns with low cardinality
- Name tables with plural forms (`tbl_users` → `tbl_user`)
- Use inconsistent timestamp formats or timezones (always UTC)
- Add indices without measuring impact (run EXPLAIN ANALYZE first)
- Create circular foreign key relationships
- Store passwords, tokens, or secrets in regular columns (use hashing or encrypted columns)

---

## Validation Rules

The schema validator checks:

1. **Naming consistency**: `tbl_` prefix for tables, `col_` prefix for columns
2. **Standard columns**: Every table has `id`, `created_at_utc`, `updated_at_utc`
3. **No hard deletes**: Deleted records use `col_deleted_at_utc`, not DROP TABLE
4. **Index coverage**: Foreign keys and frequently queried columns are indexed
5. **Migration audit**: All migrations are timestamped and reversible
6. **Type safety**: UUIDs used for PKs/FKs, not sequential integers

---

## Next Steps

1. Review this convention
2. Use `schema_generator.py` to create migrations
3. Run `schema_discovery.py` to find all tables/columns
4. Run `schema_validator.py` to check consistency

---

## References

- [Database Schema Generator](../db/schema_generator.py) — generates migrations from registry
- [Example: data-layer module](../.examples/data-layer/.ai/instruct.md) — reference migration discipline
