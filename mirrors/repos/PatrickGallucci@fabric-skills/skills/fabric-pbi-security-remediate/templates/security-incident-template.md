# Power BI Security Incident Report

## Incident Details

| Field | Value |
|-------|-------|
| **Date Reported** | YYYY-MM-DD |
| **Reported By** | |
| **Affected User(s)** | |
| **Workspace Name** | |
| **Workspace ID** | |
| **Affected Item(s)** | |
| **Severity** | [ ] Critical  [ ] High  [ ] Medium  [ ] Low |
| **Status** | [ ] Open  [ ] Investigating  [ ] Resolved  [ ] Closed |

## Symptom Description

<!-- Describe the exact error message or behavior the user is experiencing -->



## Classification

<!-- Check all that apply -->

- [ ] Workspace access denied
- [ ] Item not visible
- [ ] Data not visible (RLS issue)
- [ ] Visual shows error (OLS/CLS issue)
- [ ] Export/download blocked (sensitivity label)
- [ ] API/XMLA connection failure
- [ ] Service principal authentication error
- [ ] DirectLake fallback to DirectQuery
- [ ] Purview/DLP policy restriction
- [ ] Other: _______________

## Diagnostic Steps Performed

### 1. Workspace Role Check

- [ ] Verified user's workspace role
- User role: _______________
- Expected role: _______________

### 2. RLS/OLS Verification

- [ ] Tested using "Test as role" feature
- [ ] Checked role membership
- [ ] Verified DAX filter expressions
- [ ] Checked relationship filter directions
- Role(s) assigned: _______________

### 3. Sensitivity Label Check

- [ ] Verified label applied to item
- [ ] Checked user's label usage rights
- [ ] Verified tenant label settings
- Label name: _______________

### 4. Service Principal Check (if applicable)

- [ ] Verified tenant setting for SP API access
- [ ] Confirmed SP is in the correct security group
- [ ] Confirmed SP has workspace role
- SP Object ID: _______________
- SP Role: _______________

### 5. Governance Policy Check

- [ ] Checked Manage Permissions page for "No access"
- [ ] Reviewed recent Purview protection policy changes
- [ ] Reviewed recent DLP policy changes

## Root Cause

<!-- Describe the identified root cause -->



## Resolution

<!-- Describe the steps taken to resolve the issue -->



## Prevention

<!-- Describe any changes to prevent recurrence -->



## Diagnostic Script Output

```
<!-- Paste output from Get-PBISecurityDiagnostic.ps1 here -->

```

## Notes

<!-- Additional context, links to related incidents, etc. -->

