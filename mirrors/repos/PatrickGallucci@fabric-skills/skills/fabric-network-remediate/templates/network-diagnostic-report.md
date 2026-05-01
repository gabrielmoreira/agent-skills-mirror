# Fabric Network Diagnostic Report

**Date**: {{DATE}}
**Analyst**: {{ANALYST_NAME}}
**Workspace ID**: {{WORKSPACE_ID}}
**Capacity SKU**: {{CAPACITY_SKU}}
**Region**: {{REGION}}

---

## Executive Summary

{{SUMMARY — Brief description of the issue, impact, and resolution status}}

## Environment Details

| Property | Value |
|----------|-------|
| Fabric Capacity SKU | {{CAPACITY_SKU}} |
| Workspace Region | {{REGION}} |
| Managed VNet Enabled | Yes / No |
| Private Link (Tenant) | Enabled / Disabled |
| Outbound Access Protection | Enabled / Disabled |
| Spark Runtime Version | {{RUNTIME_VERSION}} |
| Environment Attached | {{ENVIRONMENT_NAME}} |

## Diagnostic Results

### Endpoint Reachability

| Endpoint | Status | Latency | Notes |
|----------|--------|---------|-------|
| OneLake DFS API | PASS / FAIL | {{ms}} | |
| OneLake Blob API | PASS / FAIL | {{ms}} | |
| Power BI Service | PASS / FAIL | {{ms}} | |
| Entra ID Login | PASS / FAIL | {{ms}} | |
| Data Warehouse | PASS / FAIL | {{ms}} | |

### DNS Resolution

| FQDN | Resolved IP | Private/Public | Expected |
|------|-------------|----------------|----------|
| {{FQDN}} | {{IP}} | Private / Public | Private |

### Private Endpoint Status

| Endpoint Name | Target Resource | Status | FQDN |
|---------------|----------------|--------|------|
| {{NAME}} | {{RESOURCE}} | Approved / Pending / Failed | {{FQDN}} |

### Spark Session Startup

| Metric | Value | Expected |
|--------|-------|----------|
| Startup Time | {{seconds}} | {{expected based on config}} |
| Starter Pool Used | Yes / No | {{expected}} |
| Library Install Time | {{seconds}} | 30s - 5 min |
| Queue Position | {{position}} | N/A |

## Root Cause Analysis

{{ANALYSIS — Detailed description of what was found}}

## Recommendations

1. {{RECOMMENDATION_1}}
2. {{RECOMMENDATION_2}}
3. {{RECOMMENDATION_3}}

## Actions Taken

| # | Action | Status | Owner |
|---|--------|--------|-------|
| 1 | {{ACTION}} | Complete / In Progress / Planned | {{OWNER}} |

## Appendix

### Script Output

```json
{{PASTE Test-FabricNetworkHealth.ps1 JSON OUTPUT HERE}}
```

### References

- [Fabric Network Security Overview](https://learn.microsoft.com/en-us/fabric/security/security-overview)
- [Managed VNets](https://learn.microsoft.com/en-us/fabric/security/security-managed-vnets-fabric-overview)
- [Managed Private Endpoints](https://learn.microsoft.com/en-us/fabric/security/security-managed-private-endpoints-overview)
- [Fabric URL Allowlist](https://learn.microsoft.com/en-us/fabric/security/fabric-allow-list-urls)
- [Service Tags](https://learn.microsoft.com/en-us/fabric/security/security-service-tags)
- [Workspace Outbound Access Protection](https://learn.microsoft.com/en-us/fabric/security/workspace-outbound-access-protection-overview)
