---
name: sharepoint-scaffold-schema-definition
description: Scaffolds a declarative SiteSchemaDefinition JSON structure from scratch or input parameters without requiring a live tenant connection.
allowed-tools: Bash, Read, Write
examples:
  - "python scripts/schema_scaffold.py --label pilot-site --output schema.json"
---

# Scaffold Schema Definition

Use this skill to author, scaffold, or bootstrap a new SharePoint site schema definition (SiteSchemaDefinition JSON) locally before passing it to sharepoint-schema-reconciliation for diffing or sharepoint-provisioning for real PnP execution.

