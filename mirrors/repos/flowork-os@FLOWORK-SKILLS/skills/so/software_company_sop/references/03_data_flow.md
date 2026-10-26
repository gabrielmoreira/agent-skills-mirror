# Data Flow & Sequential Interaction SOP

## 1. Role Mandate & Core Standard
The Lead Architect and Backend Engineer co-own the Data Flow Specification. Systems must model dynamic message and state sequences deterministically prior to implementation.

## 2. Mandatory Data Flow Requirements
1. **Sequence Modeling:** Explicit lifecycle transitions, request/response cycles, and event triggers.
2. **Error Recovery Trajectories:** Explicit handling of network timeouts, parse failures, and circuit breakers.
3. **State Mutation Boundary:** Zero ambient mutation; state updates must be atomic and reversible.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE DELIVERABLES BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before creating or modifying deliverables, you MUST inspect the specific example blueprint:
`view_file` -> `skills/software_company_sop/example/03_data_flow_sequence.md`
Adhere strictly to the structure and schema defined in this blueprint.
