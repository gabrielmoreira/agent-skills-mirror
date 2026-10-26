# System Design & Modular Architecture SOP

## 1. Role Mandate & Core Standard
The System Architect / Lead Engineer owns the System Architecture Document. Per MetaGPT principles, high-level architectures must decompose systems into loosely coupled modules with explicit interfaces.

## 2. Mandatory Architecture Sections
1. **System Topology & Technology Stack:** Runtime choices, frameworks, and OS portability constraints.
2. **Modular Decomposition:** Nano-modular boundary definitions (1 File 1 Logic, 20-80 LOC).
3. **External Dependencies & Licensing:** FOSS compatibility (MIT, Apache-2.0, BSD) and CVE audits.
4. **Security Perimeter:** Threat containment, permission gates, and data sanitization boundaries.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE DELIVERABLES BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before creating or modifying deliverables, you MUST inspect the specific example blueprint:
`view_file` -> `skills/software_company_sop/example/02_system_architecture_design.md`
Adhere strictly to the structure and schema defined in this blueprint.
