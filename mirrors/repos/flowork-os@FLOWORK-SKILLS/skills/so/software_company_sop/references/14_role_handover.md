# Role Handover & Handoff Contract SOP

## 1. Role Mandate & Core Standard
All agents cross-communicating across phase boundaries must dispatch structured handover contracts. Passing unstructured chat, vague summaries, or unvalidated file paths is strictly prohibited.

## 2. Mandatory Handover Payload Schema
1. **Source & Destination Roles:** Explicit identifiers of sender and recipient nodes.
2. **Artifact Manifest:** Absolute list of created/modified file paths with checksums/line counts.
3. **Execution Instructions:** Exact next actions, parameter constraints, and barrier prerequisites.
4. **Validation Proof:** Exit code or verification signature certifying that the phase milestone passed.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE DELIVERABLES BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before creating or modifying deliverables, you MUST inspect the specific example blueprint:
`view_file` -> `skills/software_company_sop/example/14_handoff_contract_payload.json`
Adhere strictly to the structure and schema defined in this blueprint.
