# Data Source Instructions: {{DATASOURCE_NAME}}

## General knowledge
The **{{DATASOURCE_NAME}}** contains {{DESCRIPTION_OF_DATA}}. It includes tables for
{{TABLE_CATEGORIES}}. Use this source for questions about {{USE_CASES}}.

## Table descriptions

### {{TABLE_1}}
{{TABLE_1_DESCRIPTION}}. Key columns:
- `{{COLUMN_1}}` ({{DATATYPE}}) — {{COLUMN_DESCRIPTION}}
- `{{COLUMN_2}}` ({{DATATYPE}}) — {{COLUMN_DESCRIPTION}}
- `{{COLUMN_3}}` ({{DATATYPE}}) — {{COLUMN_DESCRIPTION}}

### {{TABLE_2}}
{{TABLE_2_DESCRIPTION}}. Key columns:
- `{{COLUMN_1}}` ({{DATATYPE}}) — {{COLUMN_DESCRIPTION}}
- `{{COLUMN_2}}` ({{DATATYPE}}) — {{COLUMN_DESCRIPTION}}

### Relationships
- `{{TABLE_1}}.{{FK_COLUMN}}` → `{{TABLE_2}}.{{PK_COLUMN}}` ({{RELATIONSHIP_TYPE}})

## When asked about
- **{{TOPIC_A}}**: Use `{{TABLE_1}}` table, group by `{{GROUP_COLUMN}}`
- **{{TOPIC_B}}**: JOIN `{{TABLE_1}}` with `{{TABLE_2}}` on `{{JOIN_COLUMN}}`
- **{{TOPIC_C}}**: Filter `{{TABLE_1}}` WHERE `{{FILTER_COLUMN}}` = '{{FILTER_VALUE}}'
