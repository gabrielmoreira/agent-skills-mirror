# Project Methodology: Specification-Driven Development

This project follows a specification-driven development methodology inspired by systems engineering.
The methodology decomposes high-level requirements into progressively more concrete engineering artifacts, maintains explicit traceability between those artifacts, and ensures that every implemented behavior can be verified through tests.
Project specifications are stored under the `specs/` directory.

## Specification Hierarchy

Project specifications are organized into three levels: `L1 / L2`
The `L1 / L2` specification hierarchy is the collaboration space between humans and assistant.
These levels represent a refinement hierarchy from abstract business intent to concrete implementation detail.

### L1 — User and Business Requirements

L1 contains high-level requirements from the user or business perspective.
L1 specifications are primarily human-authored or human-approved. Assistant may help clarify, organize, or detect inconsistencies in L1 documents, but they must not change the business meaning without human approval.
L1 specifications must follow the approved L1 requirement template. The template is required for L1 only. The template file at `/specs/templates/spec-l1-requirement.md`.
Typical L1 content defines business intent, user requirements, business workflows, system capabilities, functional requirements, non-functional requirements, and acceptance criteria at the product or system level.
L1 specifications answer the question: `What must the system do, and why?`

### L2 — Technical Requirements and High-Level Design

L2 refines L1 content into technical requirements and high-level design decisions.
L2 specifications are co-designed by humans and assistant. 
L2 specifications translate L1 content into technical requirements, system architecture, component boundaries, technical frameworks / programming languages selection, standards, API contracts, data models, infrastructure assumptions, and high-level implementation constraints and other technical decisions.
L2 specifications are free-form design documents.
L2 specifications answer the question: `How should the system be designed to satisfy the requirements?`

### Ownership Model

L1: Human-authored or human-approved. Assistant should not change without human approval.
L2: Human-assistant co-designed. Assistant may update when technical design changes or gaps are discovered.
Assistant may update L2 directly only for local technical clarifications that do not change public APIs, data models, security posture, infrastructure cost assumptions, or externally visible behavior.
If an L2 change affects architecture, component boundaries, API contracts, data compatibility, deployment assumptions, or security constraints, assistant must propose the change for human approval before implementation.

## Traceability

The project uses explicit traceability links between requirements, designs, implementations, and tests.
The primary traceability chain is: `L1 -> L2`
The design should keep as decoupled as possible.
Tests are verification artifacts and must be traceable to the specification artifacts they verify.
Coverage for L1 and L2 is usually derived transitively through the traceability chain: `L2 -> L1`.
If the unit test verifies an L2 design, and that L2 design is already L1, then the unit test contributes to L1 through the traceability matrix.
The recommended mapping is:
```
Integration Test → L2 Design
End-to-End Test → L1 Requirement
```

## Specification Status

Each specification document must include a status field:
- Draft
- Approved
- Implemented
- Deprecated

Approved and Implemented specifications are baselined artifacts.
Status transitions:
- Draft → Approved: Human approval required.
- Approved → Implemented: Assistant may update after the corresponding implementation and tests are completed.
- Approved / Implemented → Draft: Allowed only by opening a new revision for proposed changes. The previous Approved or Implemented revision must be retained as the historical baseline and remains the active implementation authority until the new revision is approved or implemented.
- Approved / Implemented → Deprecated: Human approval required unless explicitly part of an approved replacement.

Example:
```text
L2-DES-AUTH-003 Rev 1
Status: Implemented
Active Baseline: yes

L2-DES-AUTH-003 Rev 2
Status: Draft
Active Baseline: no
Supersedes: Rev 1 after approval
```

In this example, `Rev 1` remains the active implementation authority while `Rev 2` is still Draft. Existing implementation, tests, and traceability continue to reference `Rev 1`.
Assistant must not mark L1 or L2 specifications as Approved unless explicitly instructed by a human.
Assistant should implement only against the active Approved or Implemented revision unless explicitly instructed otherwise. Deprecated specifications must not be used as implementation authority.

Each specification document should include the following metadata:
- Artifact ID
- Revision
- Status
- Active Baseline
- Supersedes, if applicable
- Superseded-By, if applicable

## Folder Hierarchy

The hierarchy is organized as:
```
specs/
  L1/
  L2/
  traceability/
```

L1 and L2 may contain subdirectories grouped by domain, module, feature, or subsystem. Each specification item should be stored as a separate Markdown file. 
Each specification item should have a stable artifact identifier. If only one revision exists, the file name may include only the artifact identifier. If multiple revisions are retained, the file name should also include the revision number. Example:
If only one revision exists:
```text
specs/L1/business-flow/L1-REQ-AUTH-001-login.md
specs/L2/auth/L2-DES-AUTH-001-authentication-architecture.md
```
The artifact identifier remains stable across revisions. The revision marker belongs to the file name and document metadata, not to the artifact identifier.
The `traceability/` directory is the single source of truth for traceability relationships between specification artifacts, implementation files, and tests.
All specifications should use stable identifiers. Identifiers must be stable, unique within their scope, human-readable, and suitable for use in traceability matrices.
Recommended identifier format:
```
L1-REQ-<DOMAIN>-<NNN>
L2-DES-<DOMAIN>-<NNN>
```
Implementation artifacts are referenced by file path and symbol or module name.
Test artifacts are identified by their test location and test function path. Test type is recorded separately as Unit, Integration, or End-to-End.

Identifier meanings:
```
REQ = Requirement
DES = Design
```

## Traceability Matrix

Traceability relationships are maintained in dedicated files under: `specs/traceability/`, files:
```
specs/traceability/l1_to_l2.md
specs/traceability/verification.md
```

The standard relationship types are:
```
L1 → L2: refined-by
Test → Specification: verifies
```

Example:
```
# L1 to L2 Traceability Matrix

| Source ID | Source Path | Target ID | Target Path | Relationship | Rationale |
|---|---|---|---|---|---|
| L1-REQ-AUTH-001 | L1/business-flow/L1-REQ-AUTH-001-login.md | L2-DES-AUTH-001 | L2/auth/L2-DES-AUTH-001-authentication-architecture.md | refined-by | The authentication architecture refines the login requirement. |
```

```
# Verification Traceability Matrix

| Test Reference | Test Type | Test Location | Directly Verifies | Verified Revision | Derived Coverage | Notes |
|---|---|---|---|---:|---|---|
| auth::retry::tests::retries_transient_failure_three_times | Unit | crates/auth/src/retry.rs | L2-DES-AUTH-001 | 1 | L1-REQ-AUTH-001 | Verifies retry count and stop condition. |
```

The traceability matrices provide the foundation for requirement coverage analysis, test coverage analysis, impact analysis, change management, design review, implementation review, verification, and validation.


## Test Trace Comment

Tests should declare traceability metadata using structured comments immediately above the test function.
The preferred format is:
```rust
/// Trace: <SPEC-ID>[, <SPEC-ID>...]
/// Verifies: <short description of the behavior being verified>
#[test]
fn test_name() {
    ...
}
```
The `Trace` line is mandatory for tests that verify behavior derived from the specification hierarchy.
The `Verifies` line is recommended because it helps humans and assistant understand why the test exists.
A test may reference multiple specification artifacts when it verifies behavior that spans multiple requirements, design elements, or detailed behaviors.

## Guidance for Assistant

When adding or modifying behavior, Assistant must identify the relevant L1 / L2 specification artifacts first.
Non-behavioral changes such as formatting, lint-only edits, dead-code removal, internal refactors that preserve observable behavior, CI maintenance, and test utilities do not require new specification artifacts. When possible, such changes should reference the closest relevant existing specification. If no relevant specification exists, the change should be described as engineering maintenance in the implementation summary.
When adding or modifying tests, Assistant must identify the behavior being verified and attach traceability metadata to the test.
Assistant may update specification documents when implementation work reveals that the existing specification is incomplete, ambiguous, inconsistent, or insufficiently actionable. The assistant’s authority depends on the specification level.
The preferred workflow is:
```
1. Identify the relevant L1 / L2 artifacts.
2. If the L2 artifact is missing, ambiguous, incomplete, or inconsistent with implementation needs, update the L2 artifact before implementing code.
3. If the issue affects business meaning, externally visible behavior, or acceptance criteria, propose the corresponding L1 change for human approval before implementation.
4. Implement the behavior in the corresponding source file.
5. Add or update tests for the implemented behavior.
6. Add traceability metadata to the tests.
7. Update the traceability matrix if new artifacts or relationships are introduced.
8. Ensure that every implemented behavior is traceable to at least one specification artifact.
```
