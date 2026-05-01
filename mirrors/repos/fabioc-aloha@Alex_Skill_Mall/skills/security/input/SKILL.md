---
type: skill
lifecycle: stable
inheritance: inheritable
name: input
description: Extract and resolve required CodeQL alert metadata from user input before remediation
tier: standard
applyTo: '**/*input*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Input Resolution — Instructions

> Scope: Resolve the required CodeQL alert metadata before remediation begins

---

## Objective

Extract the following values from the user input whenever they are available:

- OrganizationName
- ProjectName
- RepositoryName
- AlertFilePath
- QueryId
- LineNumber
- JobId
- AlertId
- AlertUrl

1. Some values may be missing. Use `cluster('1es').database('Liquid').CodeQL_Issues_Extended()` to look up missing metadata. Always resolve `OrganizationName`, `ProjectName`, and `RepositoryName` before proceeding. Make sure matching is case-insensitive.
2. Always set `IsDefaultBranch` to true and `State` to Active.
3. AlertId and AlertUrls are always unique.
4. JobId (aka CodeQLJobId) is not unique. One CodeQL job can contain multiple alerts or AlertIds.
5. Narrowing down search results. Start with orgName, projectName, repoName, then use alertFilePath, queryId, and lineNumber to further narrow down results.
6. Still, if you fail to get a unique match(es), report failure and exit.

## Relevant Lookup Schema

Use `CodeQL_Issues_Extended()` with at least the following fields:

| Column Name | Type | Description |
|---|---|---|
| Id | guid | AlertId. Unique identifier for the issue. |
| JobId | guid | CodeQLJobId. Unique identifier for the CodeQL analysis job that generated the alert. One CodeQL job can contain multiple alerts or `AlertId` values. |
| QueryId | string | CodeQL query identifier such as `cs/sql-injection`. |
| QueryName | string | Human-readable query name such as `KQL query built from user-controlled sources`. |
| RepoId | string | Repository identifier in the format `OrganizationName/ProjectName/RepositoryName`. |
| RepositoryUrl | string | URL of the repository where the issue is found. |
| AlertFilePath | string | File path relative to the repository root where the issue is found. |
| RevisionId | string | Git revision SHA of the analyzed commit. |

---

## Completion Checks

After resolving missing values, confirm that you have:

1. The CodeQL Job ID. If you cannot locate the alert later, assume the Job ID may be wrong and re-check it.
2. The alert information, or the full list of alerts to remediate.