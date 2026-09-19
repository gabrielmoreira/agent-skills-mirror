# REST API limitations and SF CLI dependencies

**Context:** Per Codey isolation policy, skills should be API-first with no CLI dependencies. Flow discovery and verification (Steps 1 & 7) were converted to REST APIs, but flow retrieval, validation, and deployment (Steps 2, 5, 6) still require the `sf` CLI due to format mismatches with available REST APIs.

## Converted to REST API

**Step 1 - Flow Discovery:** Uses Tooling API `GET /services/data/v67.0/tooling/query` instead of `sf data query`

**Step 7 - Flow Verification:** Uses Tooling API `GET /services/data/v67.0/tooling/query` instead of `sf data query`

**Form Attachment:** DynamicDataCapture SObject API `POST /services/data/vXX.0/sobjects/DynamicDataCapture` is available but not yet wired into the main workflow.

## Still requires SF CLI (documented gaps)

**Step 2 - Flow Retrieval:**
- Current: `sf project retrieve start --metadata "Flow:<name>"` returns Flow.Metadata XML
- REST alternative: Flow Builder Connect API `GET /flowbuilder/flow/{id}` returns JSON (not XML)
- **Gap:** Transformer expects XML input; JSON→XML conversion not yet built
- **Future work:** Build converter OR modify transformer to accept JSON

**Step 5 - Flow Validation:**
- Current: `sf project deploy start --dry-run` validates via Metadata API
- REST alternative: Flow Builder Connect API `POST /flowbuilder/flow/validate-flow` validates JSON
- **Gap:** Requires XML→JSON conversion + may miss Metadata API-specific errors
- **Future work:** Add conversion layer + test equivalence

**Step 6 - Flow Deployment:**
- Current: `sf project deploy start` + `deploy_flow.sh` (Metadata API + rollback snapshot)
- REST alternative: Flow Builder Connect API `POST /flowbuilder/flow/save` saves JSON
- **Gaps:**
  1. Requires XML→JSON conversion
  2. Unclear if `save` is equivalent to Metadata API deployment
  3. No built-in rollback snapshot (would need manual Tooling Query first)
  4. Activation is TOGGLE (not idempotent) - must query status first
  5. Approval for Codey usage not yet confirmed
- **Future work:** Investigate equivalence + build conversion + implement rollback

## Python scripts

The Python transformation scripts (`transform_flow.py`, `convert_to_dc_spec.py`, etc.) are also CLI-adjacent (invoked as local processes rather than via API) — converting them to a hosted service is tracked as separate future work and would require a microservice deployment.
