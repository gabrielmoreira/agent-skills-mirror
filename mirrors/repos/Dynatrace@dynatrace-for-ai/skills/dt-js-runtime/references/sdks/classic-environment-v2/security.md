# Security clients

Security problems, attacks, and Davis security advice. Import from `@dynatrace-sdk/client-classic-environment-v2`.

## `securityProblemsClient`

| Method | Purpose |
|---|---|
| `getSecurityProblems` | Query security problems (filterable, paginated). |
| `getSecurityProblem` | Get one security problem. |
| `getEventsForSecurityProblem` | List events for a security problem. |
| `getVulnerableFunctions` | List vulnerable functions for a security problem. |
| `muteSecurityProblem` / `unmuteSecurityProblem` | Mute/unmute a security problem. |
| `bulkMuteSecurityProblems` / `bulkUnmuteSecurityProblems` | Bulk mute/unmute security problems. |
| `getRemediationItems` / `getRemediationItem` | List / get remediation items. |
| `getRemediationProgressEntities` | Remediation progress entities. |
| `setRemediationItemMuteState` | Set a remediation item's mute state. |
| `bulkMuteRemediationItems` / `bulkUnmuteRemediationItems` | Bulk mute/unmute remediation items. |
| `trackingLinkBulkUpdateAndDelete` | Bulk update/delete tracking links. |

## `attacksClient`

| Method | Purpose |
|---|---|
| `getAttacks` | Query attacks (filterable, paginated). |
| `getAttack` | Get one attack by id. |

## `davisSecurityAdvisorClient`

| Method | Purpose |
|---|---|
| `getAdviceForSecurityProblems` | Get Davis AI remediation advice for security problems. |
