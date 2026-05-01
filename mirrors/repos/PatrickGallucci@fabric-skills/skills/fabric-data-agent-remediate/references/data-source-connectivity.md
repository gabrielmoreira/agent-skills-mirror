# Data Source Connectivity

Troubleshoot issues connecting lakehouses, warehouses, Power BI semantic models, KQL databases, and ontologies to a Fabric Data Agent.

## General Data Source Rules

- Maximum 5 data sources per agent (any combination of supported types)
- Each data source must be added individually from the OneLake catalog
- User credentials are used for schema access and query execution
- Data sources must be in workspaces on the same capacity region as the agent

## Adding Data Sources

### First-Time Setup
When creating a new data agent, the OneLake catalog appears automatically. Select a data source and click **Add**. Repeat for each additional source.

### Adding More Sources Later
Navigate to **Explorer** (left pane) → click **+ Data source** → select from OneLake catalog.

### Removing a Data Source
Hover over the data source name in Explorer → click the three-dot menu → select **Remove**.

### Refreshing a Data Source
After schema changes (new tables, renamed columns), hover over the data source → three-dot menu → **Refresh**.

## Lakehouse Data Sources

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Tables not appearing | Tables not yet created or loaded | Ingest data into lakehouse tables first |
| CSV/JSON files not accessible | Agent reads tables only, not files | Load files into Delta tables via notebook, pipeline, or dataflow |
| Schema out of date | Recent table changes not reflected | Right-click data source → Refresh |
| 403 Forbidden | User lacks lakehouse access | Grant workspace Contributor or lakehouse Read permissions |
| Standalone files ignored | Known limitation | Convert files to lakehouse tables before adding as data source |

### Lakehouse-Specific Notes
- The agent queries **lakehouse tables** in the SQL analytics endpoint, not raw files.
- If data starts as CSV/JSON, use notebooks, pipelines, or dataflows to ingest into tables.
- OneLake shortcuts are supported as long as they expose as tables.

## Warehouse Data Sources

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Tables not selectable | User lacks warehouse access | Grant at least Read permissions on the warehouse |
| Wrong results from views | View logic not transparent to agent | Add instructions explaining view semantics or use base tables |
| Schema mismatch after DDL | Agent cache stale | Refresh the data source in Explorer |

### Warehouse-Specific Notes
- The agent generates T-SQL queries against the warehouse SQL endpoint.
- Stored procedures and functions are not invoked by the agent.
- Only read queries (SELECT) are generated.

## Power BI Semantic Model Data Sources

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Cannot add semantic model | XMLA endpoints disabled | Enable "Allow XMLA endpoints" in Tenant Settings → Integration |
| Model not visible in catalog | User lacks Read permission | Grant Read permission on the semantic model |
| Queries fail silently | Model not published or misconfigured | Verify model is published and accessible |
| Cannot add example queries | Known limitation | PBI semantic models do not support example query pairs currently |
| Write permission error | Incorrect assumption | Only Read permission is needed; Write is not required |

### XMLA Endpoint Checklist
1. Tenant Settings → Integration settings → "Allow XMLA endpoints and Analyze in Excel with on-premises datasets" → **Enabled**
2. Capacity must be Premium P1+ or Fabric F2+
3. Semantic model must be published (not just in development)
4. User needs Read permission on the specific semantic model

## KQL Database Data Sources

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Database not appearing | Wrong workspace or insufficient permissions | Verify KQL database workspace access |
| Queries return no data | Database empty or tables not populated | Confirm data exists in the target KQL tables |
| KQL syntax errors in examples | Example queries malformed | Validate all example KQL queries directly in KQL queryset |

### KQL-Specific Notes
- The agent generates KQL queries (Kusto Query Language).
- Example queries must use valid KQL syntax matching the database schema.
- Only read operations are supported.

## Ontology Data Sources

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Cannot find data agent item type | Required tenant settings not enabled | Enable all required tenant settings for both ontology and data agent |
| First queries fail | Agent initialization not complete | Wait a few minutes after creation, then retry |
| Aggregation queries incorrect | Known issue | Add instruction "Support group by in GQL" to agent instructions |
| Vague or generic results | Ontology not well-documented | Ensure entity and relationship names are meaningful |
| 403 Forbidden in preview | User lacks lakehouse access for bindings | Contact admin for lakehouse access |
| Preview graph won't load | Column mapping enabled on Delta tables | Column mapping is not supported; recreate tables without it |
| No entity instances shown | Data binding error | Confirm source tables exist with matching column names |

### Ontology-Specific Notes
- Only managed lakehouse tables are supported (not external tables).
- Changing table names after binding creation can break the connection.
- Graph refresh schedules contribute to capacity usage.

## Permissions Quick Reference

| Data Source Type | Minimum Permission Required |
|-----------------|---------------------------|
| Lakehouse | Workspace Contributor or lakehouse Read |
| Warehouse | Workspace Contributor or warehouse Read |
| Power BI Semantic Model | Read permission on the model |
| KQL Database | Workspace Contributor or database Read |
| Ontology | Workspace Contributor |
