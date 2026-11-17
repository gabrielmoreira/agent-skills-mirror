---
name: formal-mapping
description: Translates abstract quantitative formulas, mathematical concepts, and Specification Manifests into unambiguous computational structures, data types, preconditions, public interfaces, and verification obligations. Use when translating theoretical models into algorithm designs.
license: Apache-2.0
user-invocable: false
---

# Formal Mapping & Computational Discretization Skill

## Purpose
This skill bridges quantitative theory, continuous mathematics, and formal specifications into concrete computational models. It translates abstract symbols, domains, and operations from a `Specification Manifest` (`manifest.json`) into exact data types, assertions, public interface contracts, and traceable verification obligations conforming to [mapping_schema.json](./mapping_schema.json).

## Required Context
* Path to the active `Specification Manifest` JSON (`manifest.json`).
* Target programming language and numerical libraries (e.g., Python 3.11+, NumPy, SciPy).

## Execution Workflow
1. **Gatekeeper Verification:**
   * Verify that all definitions in `manifest.json` have verified `grounding_evidence`. Reject ungrounded claims.
2. **Public Interface Specification (`public_interface`):**
   * Define the explicit module contract: `target_module` and `entrypoints` (function names, typed parameters, and return types) to enable clean-room auditing before code is written.
3. **Symbolic Discretization:**
   * Map continuous theoretical domains ($\mathbb{R}$, $\mathbb{C}$, $\mathbb{R}^{m \times n}$) to specific computational types (`float64`, `complex128`, `NDArray[np.float64]`, dataclasses, structs).
   * Define executable precondition assertions for every domain restriction (e.g., $x \in (0, \infty) \rightarrow$ `assert np.all(x > 0.0)`).
4. **Verification Obligations Derivation (`verification_obligations`):**
   * Lower each specification claim (`SPEC-k`) into one or more `verification_obligations` (`OBL-j`) drawn from Hughes's complete 4-predicate basis:
     - `anchor`: Pinned test vectors, boundary values, and known identities.
     - `reference_model`: Observational equivalence against a naive, transparent reference model on small domains.
     - `relational_law`: Multi-call metamorphic or algebraic relations ($f(T(x)) \sim g(f(x))$, round-trip, conservation).
     - `postcondition`: Property fuzzing of output bounds, shapes, and error rejection.
   * Provide `anchor_test_cases` for fast Stage 3 implementer smoke-testing.
5. **Operator Realization:**
   * Translate mathematical operations (summations, gradients, matrix products, convolutions, state transitions) into idiomatic, vectorized code constructs.
6. **Conditioning & Stability:**
   * Note potential numerical instability (division by zero, loss of significance, ill-conditioned matrices) in the `assumptions` block.
7. **Interface-Obligation Consistency & Atomic Persistence (`mapping.json`):**
   * Verify that every input parameter key referenced in `anchor_test_cases` and `verification_obligations[*].inputs` is explicitly declared in `public_interface.entrypoints[*].parameters`.
   * Persist `mapping.json` (conforming to [mapping_schema.json](./mapping_schema.json), with optional `suggested_packages`) directly via `create(path="<absolute_path>", file_text="...")` (passing `"path"` first) in `Stage 2` (`@Formalist`). Concrete `requirements.txt` packaging is owned by `@Engineer` in `Stage 3`.

## Success Criteria
* Every symbol and variable from the Manifest has a corresponding computational type mapping.
* The `public_interface` contract is fully specified with module name, entrypoints, parameters, and return types.
* Every specification claim (`SPEC-k`) is covered by at least one `verification_obligation` (`OBL-j`).
* Preconditions are specified as executable Python assertion strings.
