---
name: "sql-query-builder"
description: "Build SQL queries for construction databases. Generate optimized SQL queries for construction data retrieval"
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🏷️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# SQL Query Builder

## Overview

Based on DDC methodology (Chapter 2.1), this skill builds SQL queries for construction databases, supporting common construction data patterns like cost tracking, schedule management, and resource allocation.

**Book Reference:** "Типы данных в строительстве" / "Data Types in Construction"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date

class QueryType(Enum):
    """Types of SQL queries"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    AGGREGATE = "aggregate"
    JOIN = "join"

class AggregateFunction(Enum):
    """SQL aggregate functions"""
    SUM = "SUM"
    AVG = "AVG"
    COUNT = "COUNT"
    MIN = "MIN"
    MAX = "MAX"
    GROUP_CONCAT = "GROUP_CONCAT"

class JoinType(Enum):
    """SQL join types"""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"

class ComparisonOperator(Enum):
    """Comparison operators"""
    EQ = "="
    NE = "<>"
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    LIKE = "LIKE"
    IN = "IN"
    BETWEEN = "BETWEEN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"

@dataclass
class WhereCondition:
    """SQL WHERE condition"""
    column: str
    operator: ComparisonOperator
    value: Any
    table_alias: Optional[str] = None

    def to_sql(self) -> str:
        col = f"{self.table_alias}.{self.column}" if self.table_alias else self.column

        if self.operator == ComparisonOperator.IS_NULL:
            return f"{col} IS NULL"
        elif self.operator == ComparisonOperator.IS_NOT_NULL:
            return f"{col} IS NOT NULL"
        elif self.operator == ComparisonOperator.IN:
            values = ", ".join(f"'{v}'" if isinstance(v, str) else str(v) for v in self.value)
            return f"{col} IN ({values})"
        elif self.operator == ComparisonOperator.BETWEEN:
            return f"{col} BETWEEN {self._format_value(self.value[0])} AND {self._format_value(self.value[1])}"
        elif self.operator == ComparisonOperator.LIKE:
            return f"{col} LIKE '{self.value}'"
        else:
            return f"{col} {self.operator.value} {self._format_value(self.value)}"

    def _format_value(self, value: Any) -> str:
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, (date, datetime)):
            return f"'{value.isoformat()}'"
        elif value is None:
            return "NULL"
        else:
            return str(value)

@dataclass
class JoinClause:
    """SQL JOIN clause"""
    table: str
    alias: str
    join_type: JoinType
    on_left: str
    on_right: str

    def to_sql(self) -> str:
        return f"{self.join_type.value} {self.table} {self.alias} ON {self.on_left} = {self.on_right}"

@dataclass
class SelectColumn:
    """Column selection with optional aggregate and alias"""
    column: str
    table_alias: Optional[str] = None
    aggregate: Optional[AggregateFunction] = None
    alias: Optional[str] = None

    def to_sql(self) -> str:
        col = f"{self.table_alias}.{self.column}" if self.table_alias else self.column

        if self.aggregate:
            col = f"{self.aggregate.value}({col})"

        if self.alias:
            col = f"{col} AS {self.alias}"

        return col

@dataclass
class OrderBy:
    """ORDER BY clause"""
    column: str
    descending: bool = False
    table_alias: Optional[str] = None

    def to_sql(self) -> str:
        col = f"{self.table_alias}.{self.column}" if self.table_alias else self.column
        direction = "DESC" if self.descending else "ASC"
        return f"{col} {direction}"


class ConstructionQueryBuilder:
    """
    Build SQL queries for construction databases.
    Based on DDC methodology Chapter 2.1.
    """

    def __init__(self, dialect: str = "postgresql"):
        self.dialect = dialect
        self.schemas = self._define_construction_schemas()

    def _define_construction_schemas(self) -> Dict[str, Dict]:
        """Define common construction database schemas"""
        return {
            "projects": {
                "columns": ["id", "name", "code", "status", "start_date", "end_date", "budget", "client_id"],
                "primary_key": "id"
            },
            "cost_items": {
                "columns": ["id", "project_id", "wbs_code", "description", "budgeted_cost", "actual_cost", "committed_cost"],
                "primary_key": "id",
                "foreign_keys": {"project_id": "projects.id"}
            },
            "activities": {
                "columns": ["id", "project_id", "name", "wbs_code", "start_date", "end_date", "duration", "status", "percent_complete"],
                "primary_key": "id",
                "foreign_keys": {"project_id": "projects.id"}
            },
            "resources": {
                "columns": ["id", "name", "type", "rate", "unit"],
                "primary_key": "id"
            },
            "resource_assignments": {
                "columns": ["id", "activity_id", "resource_id", "units", "cost"],
                "primary_key": "id",
                "foreign_keys": {"activity_id": "activities.id", "resource_id": "resources.id"}
            },
            "change_orders": {
                "columns": ["id", "project_id", "number", "description", "amount", "status", "submitted_date", "approved_date"],
                "primary_key": "id",
                "foreign_keys": {"project_id": "projects.id"}
            },
            "invoices": {
                "columns": ["id", "project_id", "number", "amount", "status", "invoice_date", "due_date", "paid_date"],
                "primary_key": "id",
                "foreign_keys": {"project_id": "projects.id"}
            },
            "materials": {
                "columns": ["id", "name", "category", "unit", "unit_cost"],
                "primary_key": "id"
            },
            "material_requisitions": {
                "columns": ["id", "project_id", "material_id", "quantity", "required_date", "status"],
                "primary_key": "id",
                "foreign_keys": {"project_id": "projects.id", "material_id": "materials.id"}
            },
            "daily_reports": {
                "columns": ["id", "project_id", "report_date", "weather", "temperature", "crew_count", "notes"],
                "primary_key": "id",
                "foreign_keys": {"project_id": "projects.id"}
            }
        }

    def select(
        self,
        table: str,
        columns: List[Union[str, SelectColumn]],
        conditions: Optional[List[WhereCondition]] = None,
        order_by: Optional[List[OrderBy]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> str:
        """Build a SELECT query"""
        # Format columns
        cols = []
        for col in columns:
            if isinstance(col, str):
                cols.append(col)
            else:
                cols.append(col.to_sql())

        query = f"SELECT {', '.join(cols)}\nFROM {table}"

        # WHERE clause
        if conditions:
            where_parts = [c.to_sql() for c in conditions]
            query += f"\nWHERE {' AND '.join(where_parts)}"

        # ORDER BY
        if order_by:
            order_parts = [o.to_sql() for o in order_by]
            query += f"\nORDER BY {', '.join(order_parts)}"

        # LIMIT/OFFSET
        if limit:
            query += f"\nLIMIT {limit}"
        if offset:
            query += f"\nOFFSET {offset}"

        return query + ";"

    def select_with_joins(
        self,
        main_table: str,
        main_alias: str,
        columns: List[SelectColumn],
        joins: List[JoinClause],
        conditions: Optional[List[WhereCondition]] = None,
        group_by: Optional[List[str]] = None,
        having: Optional[List[WhereCondition]] = None,
        order_by: Optional[List[OrderBy]] = None,
        limit: Optional[int] = None
    ) -> str:
        """Build a SELECT query with JOINs"""
        # Columns
        cols = [col.to_sql() for col in columns]
        query = f"SELECT {', '.join(cols)}\nFROM {main_table} {main_alias}"

        # JOINs
        for join in joins:
            query += f"\n{join.to_sql()}"

        # WHERE
        if conditions:
            where_parts = [c.to_sql() for c in conditions]
            query += f"\nWHERE {' AND '.join(where_parts)}"

        # GROUP BY
        if group_by:
            query += f"\nGROUP BY {', '.join(group_by)}"

        # HAVING
        if having:
            having_parts = [h.to_sql() for h in having]
            query += f"\nHAVING {' AND '.join(having_parts)}"

        # ORDER BY
        if order_by:
            order_parts = [o.to_sql() for o in order_by]
            query += f"\nORDER BY {', '.join(order_parts)}"

        # LIMIT
        if limit:
            query += f"\nLIMIT {limit}"

        return query + ";"

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> str:
        """Build an INSERT query"""
        columns = list(data.keys())
        values = []

        for v in data.values():
            if isinstance(v, str):
                values.append(f"'{v}'")
            elif isinstance(v, (date, datetime)):
                values.append(f"'{v.isoformat()}'")
            elif v is None:
                values.append("NULL")
            else:
                values.append(str(v))

        return f"INSERT INTO {table} ({', '.join(columns)})\nVALUES ({', '.join(values)});"

    def insert_many(
        self,
        table: str,
        columns: List[str],
        values: List[List[Any]]
    ) -> str:
        """Build a bulk INSERT query"""
        formatted_values = []

        for row in values:
            row_values = []
            for v in row:
                if isinstance(v, str):
                    row_values.append(f"'{v}'")
                elif isinstance(v, (date, datetime)):
                    row_values.append(f"'{v.isoformat()}'")
                elif v is None:
                    row_values.append("NULL")
                else:
                    row_values.append(str(v))
            formatted_values.append(f"({', '.join(row_values)})")

        return f"INSERT INTO {table} ({', '.join(columns)})\nVALUES\n{','.join(formatted_values)};"

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        conditions: List[WhereCondition]
    ) -> str:
        """Build an UPDATE query"""
        set_parts = []

        for col, val in data.items():
            if isinstance(val, str):
                set_parts.append(f"{col} = '{val}'")
            elif isinstance(val, (date, datetime)):
                set_parts.append(f"{col} = '{val.isoformat()}'")
            elif val is None:
                set_parts.append(f"{col} = NULL")
            else:
                set_parts.append(f"{col} = {val}")

        where_parts = [c.to_sql() for c in conditions]

        return f"UPDATE {table}\nSET {', '.join(set_parts)}\nWHERE {' AND '.join(where_parts)};"

    def delete(
        self,
        table: str,
        conditions: List[WhereCondition]
    ) -> str:
        """Build a DELETE query"""
        where_parts = [c.to_sql() for c in conditions]
        return f"DELETE FROM {table}\nWHERE {' AND '.join(where_parts)};"

    # Construction-specific query templates
    def project_cost_summary(self, project_id: int) -> str:
        """Generate project cost summary query"""
        return self.select_with_joins(
            main_table="cost_items",
            main_alias="ci",
            columns=[
                SelectColumn("wbs_code", "ci"),
                SelectColumn("description", "ci"),
                SelectColumn("budgeted_cost", "ci", AggregateFunction.SUM, "total_budget"),
                SelectColumn("actual_cost", "ci", AggregateFunction.SUM, "total_actual"),
                SelectColumn("committed_cost", "ci", AggregateFunction.SUM, "total_committed")
            ],
            joins=[
                JoinClause("projects", "p", JoinType.INNER, "p.id", "ci.project_id")
            ],
            conditions=[
                WhereCondition("project_id", ComparisonOperator.EQ, project_id, "ci")
            ],
            group_by=["ci.wbs_code", "ci.description"],
            order_by=[OrderBy("wbs_code", table_alias="ci")]
        )

    def schedule_progress(self, project_id: int) -> str:
        """Generate schedule progress query"""
        return self.select_with_joins(
            main_table="activities",
            main_alias="a",
            columns=[
                SelectColumn("wbs_code", "a"),
                SelectColumn("name", "a"),
                SelectColumn("start_date", "a"),
                SelectColumn("end_date", "a"),
                SelectColumn("percent_complete", "a"),
                SelectColumn("status", "a")
            ],
            joins=[
                JoinClause("projects", "p", JoinType.INNER, "p.id", "a.project_id")
            ],
            conditions=[
                WhereCondition("project_id", ComparisonOperator.EQ, project_id, "a"),
                WhereCondition("status", ComparisonOperator.NE, "Completed", "a")
            ],
            order_by=[
                OrderBy("start_date", table_alias="a"),
                OrderBy("wbs_code", table_alias="a")
            ]
        )

    def resource_utilization(self, project_id: int) -> str:
        """Generate resource utilization query"""
        return self.select_with_joins(
            main_table="resource_assignments",
            main_alias="ra",
            columns=[
                SelectColumn("name", "r", alias="resource_name"),
                SelectColumn("type", "r", alias="resource_type"),
                SelectColumn("units", "ra", AggregateFunction.SUM, "total_units"),
                SelectColumn("cost", "ra", AggregateFunction.SUM, "total_cost")
            ],
            joins=[
                JoinClause("resources", "r", JoinType.INNER, "r.id", "ra.resource_id"),
                JoinClause("activities", "a", JoinType.INNER, "a.id", "ra.activity_id")
            ],
            conditions=[
                WhereCondition("project_id", ComparisonOperator.EQ, project_id, "a")
            ],
            group_by=["r.name", "r.type"],
            order_by=[OrderBy("total_cost", descending=True)]
        )

    def change_order_summary(self, project_id: int) -> str:
        """Generate change order summary query"""
        return self.select(
            table="change_orders",
            columns=[
                SelectColumn("status", aggregate=AggregateFunction.COUNT, alias="count"),
                SelectColumn("amount", aggregate=AggregateFunction.SUM, alias="total_amount")
            ],
            conditions=[
                WhereCondition("project_id", ComparisonOperator.EQ, project_id)
            ]
        ).replace("SELECT", "SELECT status,")  # Add group by

    def cash_flow_projection(self, project_id: int) -> str:
        """Generate cash flow projection query"""
        return f"""
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) AS received,
    SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END) AS pending,
    SUM(amount) AS total
FROM invoices
WHERE project_id = {project_id}
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY month;
"""

    def material_requirements(self, project_id: int, from_date: date, to_date: date) -> str:
        """Generate material requirements query"""
        return self.select_with_joins(
            main_table="material_requisitions",
            main_alias="mr",
            columns=[
                SelectColumn("name", "m", alias="material_name"),
                SelectColumn("category", "m"),
                SelectColumn("quantity", "mr", AggregateFunction.SUM, "total_quantity"),
                SelectColumn("unit", "m"),
                SelectColumn("required_date", "mr", AggregateFunction.MIN, "earliest_need")
            ],
            joins=[
                JoinClause("materials", "m", JoinType.INNER, "m.id", "mr.material_id")
            ],
            conditions=[
                WhereCondition("project_id", ComparisonOperator.EQ, project_id, "mr"),
                WhereCondition("required_date", ComparisonOperator.BETWEEN, [from_date, to_date], "mr"),
                WhereCondition("status", ComparisonOperator.NE, "Cancelled", "mr")
            ],
            group_by=["m.name", "m.category", "m.unit"],
            order_by=[OrderBy("earliest_need")]
        )

    def daily_report_summary(self, project_id: int, month: str) -> str:
        """Generate daily report summary for a month"""
        return f"""
SELECT
    COUNT(*) AS total_reports,
    AVG(crew_count) AS avg_crew,
    COUNT(CASE WHEN weather = 'Rain' THEN 1 END) AS rain_days,
    COUNT(CASE WHEN weather = 'Clear' THEN 1 END) AS clear_days
FROM daily_reports
WHERE project_id = {project_id}
  AND TO_CHAR(report_date, 'YYYY-MM') = '{month}';
"""

    def generate_parameterized(
        self,
        query: str,
        params: Dict[str, Any]
    ) -> tuple:
        """Convert query to parameterized format"""
        param_list = []
        param_query = query

        for key, value in params.items():
            placeholder = f"${len(param_list) + 1}" if self.dialect == "postgresql" else "?"
            param_query = param_query.replace(f":{key}", placeholder)
            param_list.append(value)

        return param_query, param_list


class QueryOptimizer:
    """Optimize SQL queries for construction databases"""

    def suggest_indexes(self, queries: List[str]) -> List[str]:
        """Suggest indexes based on query patterns"""
        suggestions = []

        # Common construction query patterns
        patterns = {
            "project_id": "CREATE INDEX idx_{table}_project ON {table}(project_id);",
            "wbs_code": "CREATE INDEX idx_{table}_wbs ON {table}(wbs_code);",
            "status": "CREATE INDEX idx_{table}_status ON {table}(status);",
            "date": "CREATE INDEX idx_{table}_date ON {table}({date_col});"
        }

        for query in queries:
            query_lower = query.lower()

            # Detect table from FROM clause
            if "from " in query_lower:
                table = query_lower.split("from ")[1].split()[0]

                if "project_id" in query_lower:
                    suggestions.append(patterns["project_id"].format(table=table))
                if "wbs_code" in query_lower:
                    suggestions.append(patterns["wbs_code"].format(table=table))
                if "status" in query_lower:
                    suggestions.append(patterns["status"].format(table=table))

        return list(set(suggestions))

    def analyze_query(self, query: str) -> Dict:
        """Analyze query for optimization opportunities"""
        analysis = {
            "has_select_star": "*" in query and "SELECT *" in query.upper(),
            "has_indexes_hint": False,
            "join_count": query.upper().count("JOIN"),
            "subquery_count": query.upper().count("SELECT") - 1,
            "recommendations": []
        }

        if analysis["has_select_star"]:
            analysis["recommendations"].append(
                "Avoid SELECT * - specify only needed columns"
            )

        if analysis["join_count"] > 3:
            analysis["recommendations"].append(
                "Consider breaking down query with CTEs for readability"
            )

        if analysis["subquery_count"] > 0:
            analysis["recommendations"].append(
                "Consider replacing subqueries with JOINs where possible"
            )

        return analysis
```

## Common Use Cases

### Build Cost Summary Query

```python
builder = ConstructionQueryBuilder()

# Get project cost summary
query = builder.project_cost_summary(project_id=123)
print(query)
```

### Build Custom SELECT Query

```python
query = builder.select(
    table="activities",
    columns=[
        SelectColumn("name"),
        SelectColumn("status"),
        SelectColumn("percent_complete")
    ],
    conditions=[
        WhereCondition("project_id", ComparisonOperator.EQ, 123),
        WhereCondition("status", ComparisonOperator.IN, ["In Progress", "Delayed"])
    ],
    order_by=[OrderBy("percent_complete", descending=True)],
    limit=10
)
```

### Build JOIN Query

```python
query = builder.select_with_joins(
    main_table="invoices",
    main_alias="i",
    columns=[
        SelectColumn("name", "p", alias="project_name"),
        SelectColumn("number", "i", alias="invoice_no"),
        SelectColumn("amount", "i")
    ],
    joins=[
        JoinClause("projects", "p", JoinType.INNER, "p.id", "i.project_id")
    ],
    conditions=[
        WhereCondition("status", ComparisonOperator.EQ, "pending", "i")
    ]
)
```

### Insert and Update Data

```python
# Insert new cost item
insert_query = builder.insert(
    table="cost_items",
    data={
        "project_id": 123,
        "wbs_code": "03.01.01",
        "description": "Concrete Foundation",
        "budgeted_cost": 50000,
        "actual_cost": 0
    }
)

# Update progress
update_query = builder.update(
    table="activities",
    data={"percent_complete": 75, "status": "In Progress"},
    conditions=[
        WhereCondition("id", ComparisonOperator.EQ, 456)
    ]
)
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `ConstructionQueryBuilder` | Main query builder |
| `WhereCondition` | WHERE clause conditions |
| `JoinClause` | JOIN definitions |
| `SelectColumn` | Column with aggregate/alias |
| `OrderBy` | ORDER BY clause |
| `QueryOptimizer` | Query optimization suggestions |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 2.1
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [data-type-classifier](../data-type-classifier/SKILL.md) to identify data types
- Use [etl-pipeline](../../Chapter-4.2/etl-pipeline/SKILL.md) for data integration
- Use [kpi-dashboard](../../Chapter-4.1/kpi-dashboard/SKILL.md) for visualization
