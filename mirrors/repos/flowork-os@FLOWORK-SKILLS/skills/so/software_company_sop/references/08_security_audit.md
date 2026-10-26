# Security Audit & Vulnerability Verification SOP

## 1. Role Mandate & Core Standard
The Security Auditor executes automated static and dynamic security audits. The auditor operates under radical zero-trust and must empirically scan codebases for vulnerabilities before any release approval.

## 2. Mandatory Audit Vectors
1. **SAST Code Antipatterns:** Detect command injection, path traversal, hardcoded secrets, unsafe regex (ReDoS), and unannotated unsafe blocks.
2. **SCA Dependency Audit:** Scan Cargo.lock, package.json, and requirements.txt against CVE and advisory databases.
3. **Runtime Permissions & Locks:** Ensure sanctity of `@lock` / `@frozen` blocks and verify tool execution sandboxes.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE DELIVERABLES BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before creating or modifying deliverables, you MUST inspect the specific example blueprint:
`view_file` -> `skills/software_company_sop/example/08_security_audit_report.md`
Adhere strictly to the structure and schema defined in this blueprint.
