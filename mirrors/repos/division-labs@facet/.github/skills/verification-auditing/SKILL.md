---
name: verification-auditing
description: Rigorous technical verification comparing implementation code against theory via bidirectional verification obligations (anchor vectors, pseudo-oracles, relational metamorphic laws, and property fuzzing). Use when proving or validating technical implementations against specifications.
license: Apache-2.0
user-invocable: true
argument-hint: 'Implementation file or active specification to verify'
---

# Technical Verification & Auditing Skill

## Purpose
This skill rigorously verifies whether a production software implementation satisfies all formal specifications from `manifest.json` and obligations from `mapping.json`. It decouples verification from any single library (e.g. SymPy is optional, used only when closed-form algebra exists) by operating across Hughes's complete 4-predicate basis:
1. **`anchor`:** Pinned test vectors, boundary values, and known identities from the source literature.
2. **`reference_model` (ALGO Pseudo-Oracle):** Observational equivalence against a dead-simple, unoptimized literal reference model on small inputs (*Weyuker 1982*, *ALGO NeurIPS 2023*).
3. **`relational_law` (Metamorphic Invariants):** Multi-call identities ($f(T(x)) \sim g(f(x))$, round-trip `decode(encode(x)) == x`, idempotence, or conservation laws) requiring no closed-form oracle.
4. **`postcondition` (Hoare Contracts):** Randomized/adversarial property fuzzing of output bounds, dimensions, and deterministic rejection of invalid inputs.

## Required Context
* Active `Specification Manifest` (`manifest.json`) declaring `SPEC-k` claims and `verification_contract`.
* Active `Mapping Document` (`mapping.json`) declaring `public_interface` and `verification_obligations` (`OBL-j`).
* Target implementation file(s).

## Execution Protocol

### 1. Information-Barrier ("Clean-Room") Test Construction
Before inspecting the implementation's internal code, read `manifest.json` and the `public_interface` contract from `mapping.json`. Construct test fixtures solely from the interface signatures and the mathematical definitions.

### 2. Obligation-by-Obligation Verification
For every `OBL-j` in `mapping.json`:
- If `predicate_type == "anchor"`: Evaluate against closed-form expressions or pinned vectors based on [anchor_oracle_template.py](./anchor_oracle_template.py).
- If `predicate_type == "reference_model"`: Compare implementation output against a naive reference model based on [reference_model_template.py](./reference_model_template.py).
- If `predicate_type == "relational_law"`: Test metamorphic or algebraic invariants based on [relational_law_template.py](./relational_law_template.py).
- If `predicate_type == "postcondition"`: Run property fuzzing on bounds and error checks based on [hypothesis_template.py](./hypothesis_template.py).
- If symbolic algebra is available: Evaluate symbolic identity equivalence based on [sympy_template.py](./sympy_template.py).

*Tolerance & Suite Soundness Invariant:* Include `from __future__ import annotations`, a module docstring, and `-> None` return annotations on all test functions. For continuous arithmetic, compare using `math.isclose` or `np.allclose(..., rtol=rtol, atol=atol)` with `rtol`/`atol` from `manifest.json`—never use exact equality (`==`) on float outputs/time-step sums or Python built-in `max(np.abs(...))` on NumPy arrays. Include Hypothesis `@given` property fuzzing for `postcondition`/`relational_law` obligations and `pytest.raises` checks for `precondition_assertions`, and keep `VERIFICATION.md` strictly plain-ASCII (no decorative emojis).

### 3. Direct Atomic Reporting & Reflexion Failure Ledger (`Stage 4`)
- If all obligations pass: Persist the complete verification report directly to `VERIFICATION.md` via atomic `create(path="<absolute_cwd>/VERIFICATION.md", file_text="...")`, recording every `OBL-j` verdict, `SPEC-k` link, and tolerance check (`[CHECKPOINT: S4 -> C3]`). Never call `edit` on `VERIFICATION.md`.
- If any obligation fails: Persist `AUDIT_FEEDBACK.json` directly via atomic `create(path="<absolute_cwd>/AUDIT_FEEDBACK.json", file_text="...")` conforming to [audit_feedback_schema.json](./audit_feedback_schema.json), capturing the minimal counter-example, expected oracle output, actual output, violated invariant, and concrete diagnosis for `@Engineer`.

## Success Criteria
- 100% of `verification_obligations` (`OBL-j`) from `mapping.json` are tested and reported.
- Zero assertion errors, unhandled exceptions, or invariant violations on accepted code.
- Detailed, actionable counter-examples recorded if defects are discovered.
