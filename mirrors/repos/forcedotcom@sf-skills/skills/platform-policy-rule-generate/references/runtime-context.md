# Runtime Context

Keep three version concepts separate:

- `MIN_API_VERSION`: static skill capability floor (`66.0` in the skill metadata).
- `ORG_API_VERSION`: target org's discovered maximum API version; use it for every API call, manifest, deploy, and retrieve.
- `EVIDENCE_API_VERSION`: historical version attached to retrieved examples; provenance only.

In normal author mode, resolve `ORG_API_VERSION` once from `/services/data`, verify it is at least `MIN_API_VERSION`, and carry it unchanged through the operation. Never copy an evidence version such as `69.0` into authored output unless the target org resolves to that version. Explicit evidence-recreation eval fixtures retain `{API_VERSION}` for harness substitution while recording API 69.0 as provenance in their instructions. Never modify `sfdx-project.json` to set an operation-specific version.
