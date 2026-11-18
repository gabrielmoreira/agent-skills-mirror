# Facet: Engineering & Invariant Instructions

## 1. Tool Use & Failure Recovery Protocol
* **Parameter Ordering & Path Hygiene:** Always pass `"path"` (full absolute path) as the **first** argument in `create`, `edit`, and `view` calls; in `bash` commands, use workspace-relative paths (e.g. `./.venv/bin/python -m pytest verify_<slug>.py`) or double-quote paths containing spaces.
* **Atomic `create` vs. Surgical `edit` / `code_patch.py`:** Always use `create(path, file_text)` for specification/report artifacts (`SOURCE_OCR.md`, `RESEARCH.md`, `manifest.json`, `mapping.json`, `VERIFICATION.md`, `AUDIT_FEEDBACK.json`). For `*.py` modules (`<= 300` lines) or multi-function refactors, prefer atomic `create(path, file_text)` overwrites (backed by automatic rollback on `SyntaxError` and `ruff format`); for large files, use `edit(path, old_str, new_str)` or `code_patch.py`.
* **Targeted Search over Sequential Scans:** When locating functions, classes, imports, theoretical formulas, or test references, prefer fast, targeted `grep` and `glob` queries over broad directory scans.
* **Never Repeat Failing Tool Arguments:** If an `edit` tool call fails, never retry with identical strings. Immediately re-read the file with `view` to verify the actual file state and indentation.
* **Non-Interactive Execution:** When executing shell commands via `bash`, never invoke interactive pagers without non-interactive flags (e.g. `less -F`, `git --no-pager`).

## 2. Technical Code & Quantitative Type-Safety Standards
* **Strict Technical & Numerical Typing:** All technical and numerical implementations must include comprehensive type annotations using `from __future__ import annotations`, `typing`, and `numpy.typing` (`NDArray[np.float64]`). Never use unconstrained `Any`.
* **Explicit Precondition Assertions:** Algorithms and quantitative models must explicitly assert domain preconditions, dimensional shapes, and conservation bounds at function entry (e.g. `assert np.all(x > 0)`).
* **Tolerance & Equivalence Contracts:** Floating-point comparisons must never use exact equality (`==`). Always use `math.isclose` or `numpy.allclose` with documented tolerances (`rtol`, `atol`).

## 3. Literature Traceability & Canonical Citation Contract
* **Theory-Level Docstrings:** Every numerical function, class, state transition, and algorithmic implementation must cite the specific equation, theorem, RFC section, or page number from the source paper or specification in its docstring.
* **Inline Theoretical Annotations:** Complex control flows must include an inline comment mapping code to its theoretical expression (e.g. `# Implements Eq. (4.2): x_{n+1} = x_n - f(x)/f'(x)`).

## 4. State Persistence Invariant & Subagent Alignment
* **Disk-Anchored State:** Active concept parameters, stage gates, and verification contracts are permanently anchored in `.pipeline_state.json` and `manifest.json`. Always inspect these files on disk rather than relying on prior chat turns.
* **Runtime Tool Alignment:** Invoke exact runtime tool names in tool calls (`view`, `create`, `edit`, `grep`, `glob`, `web_fetch`, `bash`, `task`, `sql`) while keeping VS Code frontmatter `tools:` categories (`read`, `edit`, `execute`, `search`, `agent`, `web`, `todo`) in `.agent.md` headers.
* **Isolated Environment (`./.venv`):** Python execution and test commands must invoke `./.venv/bin/python`. Third-party dependencies are pinned in `requirements.txt`.
* **Local Model Lock-In:** Subagent delegations within this pipeline must strictly run on local Gemma models. Delegations must never specify cloud models or invoke built-in cloud agents.
* **Clean Root:** Upon verification sign-off (Stage 5), all run deliverables—verified production source code (`*.py`), `requirements.txt`, specification artifacts (`SOURCE_OCR.md`, `RESEARCH.md`, `manifest.json`, `mapping.json`, `VERIFICATION.md`), `verify_*.py` scripts, `hook_state_snapshot.json`, and `PROVENANCE.json`—are moved and sealed inside `specs/<concept_slug>/`, leaving the workspace root completely clean.
