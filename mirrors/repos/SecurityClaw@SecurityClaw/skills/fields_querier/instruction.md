---
schedule_interval_seconds: null
skill: FieldsQuerier
description: >
  Reads the local field-schema catalog (data/fields_rag.json) and answers
  questions about available field names, types, and examples. Use this
  BEFORE opensearch_querier when you need exact field names for a query.
---

# FieldsQuerier

## Purpose
This skill answers field-schema questions from a local JSON catalog built by
`fields_baseliner`.  It does **not** query OpenSearch or any remote system —
responses are purely from the local file.

## When to Use
- "What field holds the source IP?"
- "Which field stores byte counts?"
- "What fields contain alert signatures?"
- "What fields are available for country filtering?"
- Any schema-discovery question needed before crafting an OpenSearch query.

## Output
Returns an answer listing exact field names (to use verbatim in OpenSearch
queries), their types, and example values, plus a structured `field_mappings`
dict for downstream query builders.

## Rules
- Use ONLY the catalog. Do not invent field names.
- List ALL candidate fields that match the concept, not just one.
- Show example values from the catalog for concreteness.
- Be brief: aim for 3-10 lines per answer.
