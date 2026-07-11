# Fixtures Index

> **For human maintainers only.** This index requires a checkout of `enforce-o-matic-impl`. The agent should rely on [`templates.md`](templates.md), which reproduces the relevant XML shapes inline.

Quick lookup from "what I need" to "fixture that already does it".

All fixtures are under `enforce-o-matic-impl/test/func/filemetadata/<name>/`.

| If you need… | Fixture |
|---|---|
| Bare permit rule, no conditions | `baseSteelthread`, `steelthreadPayload` |
| Custom conjunction `(AND 1 2)` over UNLESS | `conjunctionExpressionSteelthread` |
| Tag check | `conditionTagValidSteelthread`, `conditionCustomTagValidDataMaskingSteelthread` |
| Classification check | `conditionClassificationValidClauseSteelthread`, `conditionClassificationValidDataMaskingSteelthread` |
| Dataspace / session dataspace | `conditionDataspaceValidSteelthread`, `conditionSessionDataspaceValidSteelthread` |
| Custom permission gate | `conditionAssignedPermPathValidSteelthread` |
| Plain RLS (record field = user ID) | `conditionRLSValidSteelthread` (1st condition), `conditionStandardIdRLSValidSteelthread` |
| RLS via PROJECTION join | `conditionRLSValidSteelthread` (2nd condition) |
| Scalar / plural SOQL principal (out-of-contract) | `conditionScalarAttributeValidSteelThread`, `conditionPluralAttributeValidSteelthread` |
| Hierarchy traversal | `conditionWithHierarchy` |
| Field masking transform | `conditionClassificationValidDataMaskingSteelthread`, `conditionInvalidDataMaskingSteelthread` (negative) |
| Field-scoped resource domain | `resourceDomainWithField` |
| Core standard object policy (Case) | `coreObjectCaseWithPolicy` (persistence-layer only; not a working IDENTIFIED_RECORD shape — see §8.4 of policy.md) |
| Extended steelthread (set referenced from sibling package) | `extendedSteelthread` |
| Negative: missing operator | `conditionMissingOperatorSteelthread` |
| Negative: missing path | `conditionMissingPathSteelthread` |
| Negative: invalid context path | `conditionInvalidContextPathSteelthread` |
| Negative: invalid data masking shape | `conditionInvalidDataMaskingSteelthread` |
| Negative: invalid payload | `invalidPayload` |
