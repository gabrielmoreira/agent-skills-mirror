# Sensitivity Labels remediate Guide

Diagnostic workflow for Microsoft Purview sensitivity label issues in Microsoft Fabric Power BI.

## Table of Contents

- [Common Symptoms and Quick Fixes](#common-symptoms-and-quick-fixes)
- [Enabling Sensitivity Labels](#enabling-sensitivity-labels)
- [Applying Labels](#applying-labels)
- [PBIX File Issues](#pbix-file-issues)
- [Export and Download Issues](#export-and-download-issues)
- [Label Inheritance](#label-inheritance)
- [REST API Label Management](#rest-api-label-management)
- [Sovereign Cloud Support](#sovereign-cloud-support)

## Common Symptoms and Quick Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Can't enable labels on tenant | Missing Azure Information Protection license | Acquire AIP license |
| Can't enable labels | Labels not migrated to Purview version | Migrate in Purview admin center |
| Can't apply labels | Missing Pro/PPU license | Upgrade user license |
| Label is greyed out | Insufficient usage rights for that label | Contact label creator or M365 admin |
| Sensitivity button greyed (Desktop) | Missing license or security group membership | Check tenant settings |
| Can't open protected PBIX | Desktop version < December 2020, or free license | Update Desktop, upgrade license |
| Export fails for protected file | PBIX > 6 GB with protected label | Reduce file size or remove label |
| Can't publish via service principal | Protected labels block SP publishing | Remove label before SP publish |
| Label doesn't protect exported file | Export via unsupported path | Block unsupported export paths in admin |

## Enabling Sensitivity Labels

### Tenant Configuration Steps

1. Go to **Fabric Admin Portal** → **Tenant Settings**
2. Find **Information Protection** section
3. Expand **Allow users to apply sensitivity labels for content**
4. Enable the toggle
5. Configure scope:
   - **Entire organization** (default) or
   - **Specific security groups** (recommended for rollout)
6. Optionally exclude groups via **Except specific security groups**
7. Click **Apply**

### Prerequisites for Labels

- Sensitivity labels must be defined in Microsoft Purview Information Protection
- Labels must be migrated to the Purview version supported by Fabric
- Users must have both:
  - Pro or Premium Per User (PPU) license
  - Create and Edit permissions on the item
  - Membership in the security group allowed to apply labels

## Applying Labels

### Label Is Greyed Out

Check these conditions in order:

1. **License**: User needs Pro or PPU license
2. **Security group**: User must be in the group enabled in tenant settings
3. **Usage rights**: User may lack rights to change the specific label
4. **Label policy**: The label must be in the user's label policy

If the label was applied by someone else and you can't change it, contact the original label creator or your M365 security administrator to request the necessary usage rights.

### Label Doesn't Protect Exported Content

Sensitivity labels and file encryption protect data **only** when leaving Power BI via supported export paths:

- Supported: Excel, PowerPoint, PDF, PBIX
- Unsupported: Other export methods (data leaks unprotected)

**Admin action**: Block unsupported export paths via Power BI export and sharing settings in the admin portal.

## PBIX File Issues

### Can't Open Protected PBIX

| Condition | Resolution |
|-----------|------------|
| Desktop version < December 2020 | Update Power BI Desktop |
| User has free license | Upgrade to Pro or PPU |
| User lacks Full Control/Export rights | Request rights from label creator |
| Power BI Report Server Desktop | Not supported — use standard Desktop |
| File > 6 GB with protected label | Reduce size below 6 GB threshold |

### Can't Publish Protected PBIX via Service Principal

Publishing a protected PBIX via APIs with a service principal is **not supported**. Workaround:

1. Remove the sensitivity label from the PBIX
2. Publish via service principal
3. Reapply the label in the Power BI service

### Can't Save Labeled PBIX (Offline)

When internet connectivity is lost, encryption-related operations may fail. Return online and retry. Use additional encryption (BitLocker, NTFS encryption) as backup protection.

### Lost Access to PBIX (No One Has Rights)

If the only person with usage rights leaves the organization:

1. Use the Power BI Admin REST APIs:
   - `Set Labels as Admin` API to change the label
   - `Remove Labels as Admin` API to remove the label
2. Only Fabric administrators can run these APIs
3. Requires `Tenant.ReadWrite.All` scope

## Export and Download Issues

### PBIX Download Shows "Insufficient Permissions"

In the Power BI service, sensitivity labels do **not** affect content access — access is based solely on workspace/item permissions. However, in Power BI Desktop, labels with encryption settings **do** restrict who can open the file.

This means: a user can view a report in the service but get blocked when downloading the PBIX if they lack the label's usage rights.

### Refresh Failures with Labeled Files

| Scenario | Result |
|----------|--------|
| Protected Live Connect PBIX (OneDrive/SharePoint) | Refresh fails — neither content nor label updates |
| Labeled unprotected Live Connect PBIX | Content updates but label does not |
| New label applied (owner lacks usage rights) | Refresh fails |
| Owner's OneDrive/SharePoint token expired | Refresh fails |

## Label Inheritance

### Labels Not Inherited from Data Sources

Check all conditions:

1. Source data must be labeled with Purview sensitivity labels
2. Label scope must include "Files and emails" and "Azure Purview assets"
3. Sensitivity labels must be enabled in Power BI
4. Tenant setting "Apply sensitivity labels from data sources" must be enabled
5. All label application conditions must be met
6. Only supported in V2 workspaces (not classic)
7. Only supported with Import mode (not Live Connection or DirectQuery)
8. Not supported through gateways or Azure VNet

## REST API Label Management

### Can't Set/Remove Labels via Admin APIs

Check these requirements:

1. Caller must be a Fabric administrator
2. Admin user (and delegated user if provided) must have sufficient usage rights
3. For `setLabels`: the label must be in the admin's label policy
4. Rate limit: 25 requests/hour, up to 2000 artifacts per request
5. Required scope: `Tenant.ReadWrite.All`

## Sovereign Cloud Support

| Cloud | Supported |
|-------|-----------|
| US Government (GCC) | ✅ |
| US Government (GCC High) | ✅ |
| US Government (DoD) | ✅ |
| China | ✅ (requires additional config) |

For China: Enable rights management and add the Microsoft Purview Information Protection Sync Service service principal.

## Unsupported Scenarios

- Template apps: Sensitivity labels are removed on install and lost on update
- B2B and multi-tenant scenarios
- Workbooks (labels only supported on dashboards, reports, semantic models, dataflows, paginated reports)
- "Shared with me" view does not display labels (but labels persist on exports)
