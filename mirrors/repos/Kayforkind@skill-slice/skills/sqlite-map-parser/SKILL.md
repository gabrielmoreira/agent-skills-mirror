---
name: sqlite-map-parser
version: 1.1.1
description: "Reads unknown SQLite and GeoPackage files via sqlite_master and PRAGMA, then emits batched JSON or GeoJSON under a read-only URI. Use when the schema is undocumented, map tiles need JSON, or GPKG geometry must be decoded. Do not use for PostgreSQL/MySQL engines, live writes, SQLCipher-locked files, or a single known-column lookup."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# SQLite to Structured JSON

Parse SQLite databases by exploring the schema first and only then extracting
rows into structured JSON. The ordering matters: schema before data. If you
guess table and column names, the first unfamiliar database you receive will
break your queries. By grounding every query in what `sqlite_master` and the
`pragma_*` table-valued functions actually report, the same workflow survives
schemas you have never seen.

Throughout this document the running example is a map database with three
tables — `map_tiles` (one row per tile), `tile_metadata` (a single descriptive
row), and `tile_attributes` (extra columns keyed back to a tile `id`). Wherever
you see those names, substitute your own; the patterns do not depend on them.

## When to Use

Reach for this skill when you are handed a `.sqlite` / `.db` / `.gpkg` file and
need to turn it into JSON without already knowing its layout.

- **Unknown or undocumented schemas.** You inspect the catalog first, so every
  later query is grounded in columns that exist instead of columns you hoped
  would exist.
- **Map / grid / tile extraction.** A row-per-entity table maps cleanly to a
  JSON array of objects; the `map_tiles` example is just one instance of that.
- **Relationship discovery.** Primary keys, foreign keys, and indexes tell you
  how to join tables correctly rather than duplicating data or producing
  mismatched records.
- **Spatial data (GeoPackage, vector tiles).** GeoPackage is ordinary SQLite
  plus conventions, so the same read-only extraction applies once geometry is
  decoded.
- **Debugging and sampling.** Counting rows, sampling values, and checking for
  NULLs is far cheaper than loading an entire database into memory blind.

### When NOT to use this skill

- **The file is not SQLite** (PostgreSQL, MySQL, SQL Server). The PRAGMA
  introspection and `sqlite_master` queries are SQLite-specific and will error
  on other engines — use a driver built for that engine instead.
- **You need live, transactional querying.** Every connection here opens
  read-only for a one-shot export. If you must react to ongoing writes, query
  the live system directly so you are not reasoning from a stale snapshot.
- **The schema is already well known and you need one value.** Full exploration
  is overhead you do not need; a single targeted query is simpler.
- **You need to write or migrate data.** The `mode=ro` URI is deliberate so an
  extraction can never corrupt the source. Reach for a migration tool when you
  actually intend to modify the database.
- **The database is encrypted** (SQLCipher and similar). Open it with the
  correct key first; the stock `sqlite3` driver cannot read encrypted pages and
  will report the file as "not a database".
- **Extracted data is subject to privacy rules (GDPR and similar).** Add a
  redaction step before writing JSON, because exported data leaves SQLite's
  access controls entirely and is hard to recall.

## Prerequisites

- **Python 3.10+** — required for `X | Y` union types and built-in generics
  such as `list[str]` and `dict[str, int]`.
- **SQLite 3.35.0+** — required for `RETURNING`, full `ALTER TABLE`, and
  window-function behavior the patterns assume. The version that matters is the
  one bundled with your interpreter — check `sqlite3.sqlite_version`, not the
  Python version.
- **SpatiaLite extension** (`mod_spatialite`) — required only for GeoPackage
  geometry decoding (Example 1). Not needed for plain SQLite extraction.
- **Windows host (PowerShell).** All path examples use Windows-style paths
  (e.g. `~\data\map.sqlite`). On PowerShell, use backtick
  (`` ` ``) as line continuation, not backslash.

## Procedure

### Step 1: Explore the schema

Start by learning what exists. Each query below answers a specific question, and
the comment explains why you ask it.

#### 1.1 List the user tables

```sql
-- Exclude the sqlite_% tables: those are SQLite's own bookkeeping (for example
-- sqlite_sequence, sqlite_stat1, and sqlite_autoindex_* indexes) and are never
-- part of the data you want to export.
SELECT name
FROM sqlite_master
WHERE type = 'table'
  AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

#### 1.2 Inspect a table's columns

```sql
-- pragma_table_info exposes the declared type, NOT NULL flag, default value,
-- and primary-key position for each column. Those four facts are what let you
-- decide how to type each field when you emit JSON.
SELECT cid, name, type, "notnull", dflt_value, pk
FROM pragma_table_info('map_tiles')
ORDER BY pk DESC, cid;

-- For generated or hidden columns, use pragma_table_xinfo instead: it adds a
-- "hidden" column that pragma_table_info does not report.
SELECT cid, name, type, "notnull", dflt_value, pk, hidden
FROM pragma_table_xinfo('map_tiles')
ORDER BY pk DESC, cid;

-- The original CREATE statement is the ground truth for anything PRAGMA does
-- not surface: CHECK constraints, WITHOUT ROWID, partial-unique definitions.
SELECT sql
FROM sqlite_master
WHERE name = 'map_tiles'
  AND type IN ('table', 'view');
```

#### 1.3 Find primary keys, unique keys, and indexes

```sql
-- Primary-key columns. pk > 0 also gives their order within a composite key,
-- which you need to reconstruct the key correctly.
SELECT name, type, "notnull", pk
FROM pragma_table_info('map_tiles')
WHERE pk > 0
ORDER BY pk;

-- Every index on the table. "unique" tells you whether the index enforces a
-- constraint (and is therefore safe to treat as an identity) or merely speeds
-- up reads; "partial" warns that the index does not cover all rows.
SELECT name, "unique", partial, origin
FROM pragma_index_list('map_tiles');

-- Columns inside one index, with sort direction and collation. Use
-- pragma_index_xinfo (not pragma_index_info) because only the x-variant returns
-- "desc", "coll", and "key".
SELECT seqno, cid, name, "desc", coll, key
FROM pragma_index_xinfo('idx_map_tiles_xy');
```

### Step 2: Understand relationships

#### 2.1 Read declared foreign keys

```sql
-- Foreign keys tell you the real join keys instead of forcing you to infer them
-- from column names. "on_update" / "on_delete" also reveal cascade behavior,
-- which matters if you later reason about referential integrity in the JSON.
SELECT id, seq, "table", "from", "to", on_update, on_delete, match
FROM pragma_foreign_key_list('tile_attributes');
```

#### 2.2 Spatial metadata (GeoPackage)

```sql
-- GeoPackage advertises its feature/tile tables and their geometry columns in
-- two metadata tables. Read these first so you know which user table holds
-- geometry and what the geometry column is actually called (it is often not
-- literally "geometry").
SELECT table_name, data_type, identifier, srs_id
FROM gpkg_contents;

SELECT table_name, column_name, geometry_type_name, srs_id
FROM gpkg_geometry_columns;
```

#### 2.3 Joining related tables safely

```sql
-- Prefer explicit JOINs and bound parameters. USING (id) is shorthand for
-- ON t.id = a.id and only works when both tables name the column "id". The
-- BETWEEN ? AND ? keeps the row range out of the SQL text, so a caller can
-- never turn the range into an injection.
SELECT t.id, t.x, t.y, t.terrain, a.elevation, a.biome
FROM map_tiles AS t
LEFT JOIN tile_attributes AS a USING (id)
WHERE t.id BETWEEN ? AND ?
ORDER BY t.id;
```

### Step 3: Extract and transform

The design choices below all serve one goal: make failures loud and typed
instead of silent and stringly. The connection is opened read-only so an
extraction can never mutate the source; dynamic identifiers are validated
because parameter binding cannot substitute table or column names; and errors
are raised as a single custom exception rather than returned as `{"error": message}`
dicts, so callers cannot accidentally treat a failure as data.

#### 3.1 Shared types and helpers

```python
from __future__ import annotations

import base64
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import TypeAlias, TypedDict, cast

# SQLite stores every value as one of five storage classes. bytes covers BLOB;
# everything else is text, integer, real, or NULL.
SQLiteValue: TypeAlias = str | int | float | bytes | None
Row: TypeAlias = dict[str, SQLiteValue]

# A fully JSON-serializable value, defined recursively. Used for decoded
# geometry and other nested structures that are not flat SQLite scalars.
JSONValue: TypeAlias = (
    str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]
)

# Plain SQL identifiers we are willing to interpolate into a statement. Anything
# outside this pattern is rejected before it reaches the database.
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class SQLiteParseError(RuntimeError):
    """Raised when a database cannot be opened, validated, or parsed.

    A single exception type lets callers wrap extraction in one ``except`` block
    while still receiving an actionable message, instead of inspecting the
    string contents of an error dict.
    """


def _quote_identifier(name: str) -> str:
    """Validate and double-quote a SQL identifier.

    Parameter binding (``?``) substitutes *values* only, never table or column
    names, so any dynamic identifier must be validated explicitly to prevent SQL
    injection. We reject anything that is not a plain identifier, then escape
    embedded double quotes defensively before quoting.
    """
    if not isinstance(name, str) or not _IDENTIFIER_RE.fullmatch(name):
        raise ValueError(f"Refusing to use unsafe SQL identifier: {name!r}")
    return '"' + name.replace('"', '""') + '"'


def _row_to_dict(row: sqlite3.Row) -> Row:
    """Convert a ``sqlite3.Row`` into a typed dict.

    The stdlib types ``sqlite3.Row`` values as ``Any`` because the C layer is
    dynamic. We cast once, here, at that single boundary so the rest of the code
    stays strictly typed and no ``Any`` leaks into a public signature.
    """
    return cast(Row, {key: row[key] for key in row.keys()})


def _to_json_value(value: SQLiteValue) -> JSONValue:
    """Coerce a raw SQLite value into something ``json.dumps`` accepts.

    BLOBs are the only non-serializable storage class, so we surface them as
    base64 text rather than letting ``json.dumps`` raise at the very end of an
    otherwise successful extraction.
    """
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    return value


def _list_tables(cursor: sqlite3.Cursor) -> set[str]:
    """Return user table names, excluding SQLite's internal bookkeeping tables."""
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return {str(row[0]) for row in cursor.fetchall()}
```

#### 3.2 Parse a database into a JSON-serializable structure

```python
class ParsedDatabase(TypedDict):
    """Result of a successful extraction. Both fields are always present."""

    metadata: Row
    items: list[Row]


def parse_sqlite_to_json(
    db_path: str | Path,
    *,
    main_table: str,
    id_column: str = "id",
    metadata_table: str | None = None,
    related_table: str | None = None,
    batch_size: int = 1000,
) -> ParsedDatabase:
    """Parse a SQLite database into a metadata mapping plus an items list.

    Args:
        db_path: Path to the database file. Validated to exist before opening.
        main_table: The table whose rows become the JSON ``items`` array.
        id_column: Column used to key rows so a related table can be merged in.
        metadata_table: Optional single-row table merged into ``metadata``.
        related_table: Optional table whose columns are merged onto matching
            ``items`` by ``id_column``.
        batch_size: Rows fetched per round trip. Bounded extraction keeps memory
            flat on large tables instead of materializing every row at once.

    Returns:
        A :class:`ParsedDatabase` on success.

    Raises:
        SQLiteParseError: The file is missing, the required table is absent, the
            id column is missing, or the driver reports any SQLite error.
        ValueError: ``batch_size`` is not positive, or an identifier is unsafe.
    """
    path = Path(db_path)
    if not path.is_file():
        raise SQLiteParseError(f"Database file not found: {path}")
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size!r}")

    # Validate every identifier up front so a bad name fails before we open a
    # connection rather than midway through extraction.
    main_sql = _quote_identifier(main_table)
    id_sql = _quote_identifier(id_column)

    try:
        # closing() guarantees the connection is closed even if validation below
        # raises. This also avoids the classic bug of referencing `conn` in a
        # finally block when the connect() call itself failed.
        with closing(sqlite3.connect(f"file:{path}?mode=ro", uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            # trusted_schema=OFF stops schema-defined functions and views from
            # executing attacker-controlled SQL while we read the catalog.
            conn.execute("PRAGMA trusted_schema = OFF")
            cursor = conn.cursor()

            tables = _list_tables(cursor)
            if main_table not in tables:
                raise SQLiteParseError(
                    f"Required table {main_table!r} not present; "
                    f"available tables: {sorted(tables)}"
                )

            metadata: Row = {}
            if metadata_table is not None and metadata_table in tables:
                cursor.execute(
                    f"SELECT * FROM {_quote_identifier(metadata_table)} LIMIT 1"
                )
                first = cursor.fetchone()
                if first is not None:
                    metadata = _row_to_dict(first)

            # Key rows by id so a related table can be merged in O(1) per row.
            data: dict[SQLiteValue, Row] = {}
            cursor.execute(f"SELECT * FROM {main_sql} ORDER BY {id_sql}")
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                for raw in batch:
                    record = _row_to_dict(raw)
                    if id_column not in record:
                        raise SQLiteParseError(
                            f"Column {id_column!r} missing from {main_table!r}; "
                            f"columns present: {sorted(record)}"
                        )
                    data[record[id_column]] = record

            if related_table is not None and related_table in tables:
                cursor.execute(f"SELECT * FROM {_quote_identifier(related_table)}")
                for raw in cursor:
                    related = _row_to_dict(raw)
                    key = related.get(id_column)
                    target = data.get(key)
                    if target is not None:
                        for column, value in related.items():
                            if column != id_column:
                                target[column] = value

            return {"metadata": metadata, "items": list(data.values())}

    except sqlite3.Error as exc:
        # Wrap every driver error in our type so callers handle one exception
        # and still see the originating file and message.
        raise SQLiteParseError(f"Failed to parse {path}: {exc}") from exc
```

#### 3.3 Probe optional tables without masking real errors

```python
def safe_query(
    cursor: sqlite3.Cursor,
    query: str,
    params: tuple[SQLiteValue, ...] = (),
) -> list[sqlite3.Row]:
    """Run a parameterized query, treating a missing table as empty results.

    Feature tables come and go across schema versions, so a missing table is an
    expected, recoverable condition when probing optional data. We translate
    *only* that specific ``OperationalError`` into an empty list and re-raise
    everything else (corruption, locked database, syntax errors) so genuine
    problems are never silently swallowed.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            return []
        raise
```

### Step 4: Output as structured JSON

The JSON shapes below are the serialized form of the TypedDicts above. The
GeoJSON `FeatureCollection` corresponds to `extract_geopackage`'s return type;
the array form corresponds to `parse_sqlite_to_json`'s `items`.

**GeoJSON FeatureCollection** (one feature per spatial row):

```json
{
  "type": "FeatureCollection",
  "metadata": {
    "table_name": "map_tiles",
    "data_type": "features",
    "srs_id": 4326
  },
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [10, 20] },
      "properties": { "id": 1, "terrain": "grass", "elevation": 120 }
    }
  ]
}
```

**Flat array with a documented contract** (one object per row):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "metadata": { "created": "2026-03-15T12:00:00Z", "map": "overworld" },
  "items": {
    "type": "array",
    "items": {
      "type": "object",
      "required": ["x", "y"],
      "properties": {
        "x": { "type": "integer", "minimum": 0 },
        "y": { "type": "integer", "minimum": 0 },
        "terrain": { "type": "string" }
      }
    }
  }
}
```

## Examples

### Example 1: GeoPackage feature extraction

GeoPackage stores geometry as a custom binary envelope, so decoding it to
GeoJSON requires the SpatiaLite extension (`mod_spatialite`). The function below
verifies the file really is a GeoPackage, loads the extension defensively (and
re-locks extension loading immediately after), and validates the feature-table
and geometry-column names — both of which come from *data* in `gpkg_contents`,
not from code — before interpolating them into a query.

```python
class GeoJSONFeature(TypedDict):
    type: str
    geometry: JSONValue
    properties: dict[str, JSONValue]


class FeatureCollection(TypedDict):
    type: str
    metadata: Row
    features: list[GeoJSONFeature]


# ASCII 'GPKG' as a big-endian integer; the value GeoPackage writes into the
# SQLite header's application_id field.
_GPKG_APPLICATION_ID = 0x47504B47


def extract_geopackage(db_path: str | Path) -> FeatureCollection:
    """Extract one GeoPackage feature table as a GeoJSON FeatureCollection.

    Raises:
        SQLiteParseError: The file is missing, is not a GeoPackage, SpatiaLite
            cannot be loaded, or the driver reports any SQLite error.
    """
    path = Path(db_path)
    if not path.is_file():
        raise SQLiteParseError(f"Database file not found: {path}")

    try:
        with closing(sqlite3.connect(f"file:{path}?mode=ro", uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA trusted_schema = OFF")
            cursor = conn.cursor()

            # Verify this is actually a GeoPackage by checking the application_id
            # in the SQLite header.
            app_id = cursor.execute("PRAGMA application_id").fetchone()[0]
            if app_id != _GPKG_APPLICATION_ID:
                raise SQLiteParseError(
                    f"Not a GeoPackage (application_id=0x{app_id:08X}, "
                    f"expected 0x{_GPKG_APPLICATION_ID:08X})"
                )

            # Load SpatiaLite defensively: enable extension loading, load it,
            # then immediately disable extension loading again.
            try:
                conn.enable_load_extension(True)
                conn.load_extension("mod_spatialite")
            except (AttributeError, sqlite3.OperationalError) as exc:
                raise SQLiteParseError(
                    "GeoPackage geometry decoding requires the SpatiaLite "
                    f"extension (mod_spatialite); it could not be loaded: {exc}"
                ) from exc
            finally:
                try:
                    conn.enable_load_extension(False)
                except AttributeError:
                    pass

            contents_row = cursor.execute(
                "SELECT * FROM gpkg_contents WHERE data_type = 'features' LIMIT 1"
            ).fetchone()
            if contents_row is None:
                raise SQLiteParseError("No feature tables found in gpkg_contents")
            contents = _row_to_dict(contents_row)

            table_name = contents.get("table_name")
            if not isinstance(table_name, str):
                raise SQLiteParseError(
                    "gpkg_contents.table_name is missing or not text"
                )
            feature_sql = _quote_identifier(table_name)

            # The geometry column is declared in metadata; do not assume it is
            # literally named "geometry".
            geom_row = cursor.execute(
                "SELECT column_name FROM gpkg_geometry_columns WHERE table_name = ?",
                (table_name,),
            ).fetchone()
            geometry_column = geom_row["column_name"] if geom_row is not None else None
            if not isinstance(geometry_column, str) or not _IDENTIFIER_RE.fullmatch(
                geometry_column
            ):
                raise SQLiteParseError(
                    f"Invalid or missing geometry column: {geometry_column!r}"
                )
            geometry_sql = _quote_identifier(geometry_column)

            features: list[GeoJSONFeature] = []
            cursor.execute(
                f"SELECT *, ST_AsGeoJSON({geometry_sql}) AS __geojson "
                f"FROM {feature_sql}"
            )
            for raw in cursor:
                record = _row_to_dict(raw)
                raw_geometry = record.pop("__geojson", None)
                geometry: JSONValue = (
                    json.loads(raw_geometry)
                    if isinstance(raw_geometry, str)
                    else None
                )
                # Drop the raw geometry blob; the decoded form lives in geometry.
                record.pop(geometry_column, None)
                properties: dict[str, JSONValue] = {
                    key: _to_json_value(value) for key, value in record.items()
                }
                features.append(
                    {
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": properties,
                    }
                )

            return {
                "type": "FeatureCollection",
                "metadata": contents,
                "features": features,
            }

    except sqlite3.Error as exc:
        raise SQLiteParseError(f"Failed to read GeoPackage {path}: {exc}") from exc
```

### Example 2: Hierarchical extraction with a recursive CTE

A self-referential `categories` table (each row points at its `parent_id`) is an
adjacency-list tree, and a recursive CTE is the natural way to flatten it with a
computed depth. The risk is a malformed or cyclic `parent_id` chain, which would
otherwise recurse forever, so the query carries an explicit depth cap. As with
every example here, the connection is read-only because this is pure extraction.

```python
class CategoryNode(TypedDict):
    id: int
    parent_id: int | None
    name: str
    depth: int


def extract_hierarchical(
    db_path: str | Path,
    *,
    max_depth: int = 100,
) -> dict[str, list[CategoryNode]]:
    """Flatten a self-referential ``categories`` table, deepest path bounded.

    Args:
        db_path: Path to the database file.
        max_depth: Hard ceiling on recursion depth. Guards against cyclic
            parent_id data that would otherwise loop indefinitely.

    Raises:
        SQLiteParseError: The file is missing or a SQLite error occurs.
        ValueError: ``max_depth`` is not positive.
    """
    path = Path(db_path)
    if not path.is_file():
        raise SQLiteParseError(f"Database file not found: {path}")
    if max_depth <= 0:
        raise ValueError(f"max_depth must be positive, got {max_depth!r}")

    try:
        with closing(sqlite3.connect(f"file:{path}?mode=ro", uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA trusted_schema = OFF")
            cursor = conn.cursor()

            # The WHERE h.depth < ? in the recursive term is the cycle guard:
            # the bound parameter keeps the limit out of the SQL string.
            cursor.execute(
                """
                WITH RECURSIVE hierarchy(id, parent_id, name, depth) AS (
                    SELECT id, parent_id, name, 0 AS depth
                    FROM categories
                    WHERE parent_id IS NULL

                    UNION ALL

                    SELECT c.id, c.parent_id, c.name, h.depth + 1
                    FROM categories AS c
                    JOIN hierarchy AS h ON c.parent_id = h.id
                    WHERE h.depth < ?
                )
                SELECT id, parent_id, name, depth
                FROM hierarchy
                ORDER BY depth, id
                """,
                (max_depth,),
            )

            categories: list[CategoryNode] = []
            for raw in cursor:
                parent_raw = raw["parent_id"]
                categories.append(
                    {
                        "id": int(raw["id"]),
                        "parent_id": int(parent_raw) if parent_raw is not None else None,
                        "name": str(raw["name"]),
                        "depth": int(raw["depth"]),
                    }
                )

            return {"categories": categories}

    except sqlite3.Error as exc:
        raise SQLiteParseError(
            f"Failed to extract hierarchy from {path}: {exc}"
        ) from exc
```

## Common schema patterns

### Spatial data
- **GeoPackage tables** (`gpkg_*`) describe which user tables hold geometry and
  in which spatial reference system, so always read them before the data.
- **Vector tiles** store MVT-encoded blobs; decode them with a dedicated MVT
  library rather than treating the blob as text.
- **R\*Tree spatial indexes** accelerate bounding-box queries but are virtual
  tables — query them through their module, not as ordinary rows.

### Hierarchical data
- **Self-referential `parent_id` columns** model trees in a single table and are
  best traversed with a recursive CTE (see Example 2).
- **JSON columns** hold flexible attributes; pull them out with `json_extract`
  rather than parsing strings in Python where you can avoid it.
- **UUID text keys** are common in modern schemas; treat keys as opaque strings
  rather than assuming integer ids.

### Performance
- **`fetchmany` over `fetchall`** keeps memory flat on large tables.
- **WAL mode** means a `-wal` sidecar file may hold the newest committed data;
  open the main database normally and SQLite reconciles it for you.
- **Covering indexes** let a query be answered from the index alone — worth
  checking with `EXPLAIN QUERY PLAN` when an export is slow.

## Pitfalls

- **Never use `fetchall` on large tables.** It materializes every row in memory
  at once. Use `fetchmany(batch_size)` in a loop to keep RSS flat.
- **Never interpolate unvalidated identifiers into SQL.** Parameter binding
  (`?`) substitutes *values* only, never table or column names. Always pass
  dynamic identifiers through `_quote_identifier` first.
- **Never open without `mode=ro`.** The read-only URI is deliberate so an
  extraction can never mutate or corrupt the source database.
- **Never skip `PRAGMA trusted_schema = OFF`.** Without it, schema-defined
  functions and views can execute attacker-controlled SQL while you read the
  catalog.
- **Never assume the geometry column is named `geometry`.** GeoPackage declares
  the column name in `gpkg_geometry_columns`; always read it from metadata.
- **Never assume `parent_id` chains are acyclic.** Always pass a `max_depth`
  bound to recursive CTEs to prevent infinite loops on malformed data.
- **Never swallow `OperationalError` broadly.** Only translate "no such table"
  to an empty list in `safe_query`; re-raise everything else (corruption, locked
  database, syntax errors) so genuine problems surface.
- **Never treat BLOBs as text.** BLOBs are the only non-serializable storage
  class; encode them as base64 before emitting JSON.
- **Never assume SQLite version.** Check `sqlite3.sqlite_version >= "3.35.0"`;
  older builds lack `RETURNING`, full `ALTER TABLE`, and some window functions.
- **Encrypted databases (SQLCipher) will report "not a database".** The stock
  `sqlite3` driver cannot read encrypted pages. Open with the correct key first.
- **WAL sidecar files.** A `-wal` file may hold the newest committed data; open
  the main database normally and SQLite reconciles it automatically.
- **Privacy/GDPR.** Exported data leaves SQLite's access controls entirely.
  Add a redaction step before writing JSON if the data is subject to privacy
  rules.

## Verification

Each item names what to check and why it matters; treat the list as a smoke test
before trusting an extraction in production.

1. **Driver version.** Confirm `sqlite3.sqlite_version >= "3.35.0"`:

   ```python
   python -c "import sqlite3; print(sqlite3.sqlite_version)"
   ```

   The patterns assume features older builds lack.

2. **Read-only URIs work.** Verify a `file:<path>?mode=ro` connection opens and
   that a write attempt is rejected — proof the source cannot be mutated:

   ```python
   python -c "import sqlite3; c=sqlite3.connect('file:test.db?mode=ro',uri=True); c.execute('CREATE TABLE x(id)')"
   # Expected: sqlite3.OperationalError: attempt to write a readonly database
   ```

3. **`trusted_schema = OFF` is non-breaking.** Confirm normal reads still
   succeed with the hardening pragma enabled.

4. **GeoPackage path.** Run `extract_geopackage` against a real `.gpkg` and
   confirm the `application_id` check and SpatiaLite load behave correctly.

5. **Recursive CTE bound.** Feed `extract_hierarchical` cyclic data and confirm
   it terminates at `max_depth` instead of hanging.

6. **Memory on large tables.** Watch RSS while extracting a large table to
   confirm `fetchmany` keeps it flat:

   ```powershell
   # In a separate PowerShell window while extraction runs:
   Get-Process python | Select-Object Id, WorkingSet64
   ```

7. **Corruption handling.** Point the parser at a truncated file and confirm it
   raises `SQLiteParseError` with a useful message, not a bare traceback.

8. **Read-only filesystem.** Run against a file on a read-only mount to confirm
   the read-only connection still opens.

9. **JSON validity.** Validate emitted JSON against the draft 2020-12 shapes
   above, including base64-encoded BLOB fields:

   ```python
   python -c "import json; json.load(open('output.json')); print('valid')"
   ```

10. **Identifier rejection.** Pass a malicious `main_table` (e.g.
    `"t; DROP TABLE x"`) and confirm `_quote_identifier` raises `ValueError`:

    ```python
    python -c "from skill import _quote_identifier; _quote_identifier('t; DROP TABLE x')"
    # Expected: ValueError: Refusing to use unsafe SQL identifier: 't; DROP TABLE x'
    ```

## Related skills

- **json-transformer-v2** — chain after extraction to reshape or stream JSON.
- **geopackage-analyzer** — deeper spatial analysis once geometry is decoded.
- **sqlite-forensics** — recovery and analysis of deleted or corrupted data.
- **schema-diff-tool** — compare two database schema versions.
