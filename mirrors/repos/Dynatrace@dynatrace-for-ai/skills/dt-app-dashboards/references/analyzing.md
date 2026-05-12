# Dashboard Analysis & Information Extraction

## Two Main Workflows

1. **Look into dashboard** — read global context, then tiles top-to-bottom
2. **Search for something** — find specific content by keyword

---

## Workflow 1: Read Dashboard

### Global Context

```bash
# Metadata overview
jq '{version: .content.version, tiles: (.content.tiles | length),
  variables: (.content.variables | length)}' dashboard.json

# Variables (filters available to user)
jq '.content.variables[] | {key, type, input, defaultValue}' dashboard.json
```

### Tiles Top-to-Bottom

```bash
# Sorted by position
jq '. as $r | .content.layouts | to_entries | sort_by(.value.y, .value.x) |
  map({id: .key, y: .value.y, tile: $r.content.tiles[.key]})' dashboard.json

# Specific tile details
jq --arg id "4" '.content.tiles[$id] | {title, query, visualization,
  visualizationSettings}' dashboard.json
```

Per tile, extract: **title** (what it shows), **query** (DQL), **visualization**
(chart type), **thresholds** (color interpretation), **content** (markdown text).

---

## Workflow 2: Search

```bash
# Search tile titles
jq --arg k "error" '.content.tiles | to_entries |
  map(select(.value.title // "" | ascii_downcase | contains($k)))' dashboard.json

# Search queries
jq --arg p "fetch logs" '.content.tiles | to_entries |
  map(select(.value.query // "" | contains($p)))' dashboard.json
```

---

## Executing Queries from Dashboard

1. **Extract query** with title, visualization, and thresholds for context
2. **Check for variables** (`$VarName` references)
3. **Resolve variables**: if `type=="query"`, execute the variable's `input`
   query to get valid values; if `type=="text"`, use `defaultValue`
4. **Substitute** variable values into the query
5. **Execute** and interpret results based on visualization type and thresholds

---

## Purpose Identification

Analyze tile titles and data sources to infer dashboard purpose:
- "Request Rate", "Error Count", "Response Time" → Service Health (RED)
- "CPU Usage", "Memory Usage" → Infrastructure Monitoring
- "SLI", "Error Budget" → SLO Tracking
- Single values with thresholds → Executive / KPI dashboard

```bash
# Data sources used
jq -r '.content.tiles[].query | select(. != null)' dashboard.json |
  grep -oE 'fetch \w+' | sort | uniq -c
```
