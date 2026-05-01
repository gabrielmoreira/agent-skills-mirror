# Connector Capability Matrix

| Source | Landing | Capability Tags | Risk Class | Secret Profile | Decision Class | Reviewed Head | Explicit Reject |
|---|---|---|---|---|---|---|---|
| `awesome-mcp-servers` | `catalog_only` | `discovery`, `metadata`, `ranking`, `catalog_sync` | `medium` | `none` | `metadata-only` | `ed1aa4fbeb0006e9c2be7594b494910a948d83ae` | implicit auto install / route takeover / execution owner |
| `composio` | `provider_contract` | `tool_binding`, `oauth_boundary`, `app_catalog`, `read_action`, `write_action` | `medium` | `connector_admission` | `admit` | `3d284eef2e48b4c3e8ce84ad1f866bdb4d204056` | second orchestrator / provider takeover |
| `activepieces` | `workflow_reference` | `workflow_templates`, `piece_metadata`, `automation_reference`, `trigger_action`, `write_action` | `medium` | `connector_admission` | `admit` | `e1bd2772affc271f69b502b07cfa22e57eb2b757` | background execution owner / provider takeover |
| `awesome-claude-skills-composio` | `reference_only_pattern_bank` | `connector_skills`, `app_actions`, `examples` | `low` | `none` | `reference-only` | `27904475d1270d8395acf07691966267d5abda2d` | direct runtime loading |
