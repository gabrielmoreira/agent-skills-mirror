# ALL Consumer: General Policy

`consumer=ALL` selects the shared H360 policy contract. It does not apply Data Governance Policy Builder restrictions.

Keep the shared OLS, FLS, direct RLS, join RLS, Transform, condition, expression, and conjunction models reusable here. Apply base metadata, semantic, target-org reference, MDAPI, and runtime validation.

`ALL` does not mean unvalidated. Resolve resource domains, fields, joins, tags, classifications, permissions, and principal expressions before deployment. Reject `PLACEHOLDER` because it is internal-only. Do not reject `PLURAL_ATTRIBUTE` solely because the Data Governance UI cannot render it; require separate MDAPI/runtime evidence for any such policy.

RLS plus tag/classification conditions remain experimental until their combined metadata and runtime semantics are proven. Do not claim support from enum presence alone.
