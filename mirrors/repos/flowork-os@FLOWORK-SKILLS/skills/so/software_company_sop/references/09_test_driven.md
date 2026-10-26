# Test-Driven Verification & Test Harness SOP

## 1. Role Mandate & Core Standard
The Quality Control (QC) Engineer leads verification, supported by Backend/Frontend engineers writing unit tests. All functionality must be backed by reproducible test harnesses executed against the real runtime environment.

## 2. Mandatory Verification Invariants
1. **Deterministic Execution:** Zero reliance on flaky network requests; mock external services only when necessary with high-fidelity fixtures.
2. **Boundary Testing:** Explicitly test edge cases: empty payloads, oversized payloads, non-ASCII characters, and negative numeric bounds.
3. **Automated Assertion:** Tests must assert exact state transitions and exit cleanly.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE DELIVERABLES BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before creating or modifying deliverables, you MUST inspect the specific example blueprint:
`view_file` -> `skills/software_company_sop/example/09_deterministic_test_harness.py`
Adhere strictly to the structure and schema defined in this blueprint.
