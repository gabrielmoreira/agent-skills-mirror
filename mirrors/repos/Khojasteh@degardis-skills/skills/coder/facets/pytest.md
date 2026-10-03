---
title: pytest
category: Test framework
x-claim-provenance:
- claim: pytest -p no:NAME prevents the named plugin from loading or unregisters it.
  source: https://docs.pytest.org/en/stable/how-to/plugins.html
- claim: pytest gives an error for an asynchronous test function and prompts the user to install a plugin that can handle it.
  source: https://docs.pytest.org/en/stable/deprecations.html
- claim: --lf re-runs only the failures from the previous run, and when none are recorded --last-failed-no-failures all, the default, runs the full suite, while none only reports that and exits successfully.
  source: https://docs.pytest.org/en/stable/how-to/cache.html
  scope: pytest stable documentation, read 2026-09.
- claim: A run can select tests by node id such as path::Class::test[param] or by a -k expression matched case-insensitively against file, class, and function names.
  source: https://docs.pytest.org/en/stable/how-to/usage.html
---

Fixtures are pytest's native reusable setup mechanism. Module-level setup has wider reach, while the narrowest useful fixture scope in `conftest.py` limits state leakage into unrelated tests. `@pytest.mark.parametrize` with `ids` keeps cases identifiable; fixture scope, `tmp_path`, `monkeypatch`, and `caplog` support isolated state; `pytest.raises(..., match=...)` expresses expected failures; and coroutine execution follows the configured async plugin rather than a pytest-owned event loop.

Order randomization, repetition, and parallelism come from installed plugins rather than pytest core, for example `pytest-xdist`, `pytest-repeat`, and whichever randomizing plugin the project configures, and `-p no:<plugin>` can remove a plugin's influence for diagnosis. Snapshot and approval baselines are likewise plugin-defined, so the project-installed mechanism determines their semantics and any unused-baseline report. Pytest does not report an unused fixture, parameter set, or plugin-owned baseline when the last consuming test is deleted.

Node identifiers, or the name expression the installed runner supports, narrow a run, and the run reports its collected and deselected counts. `--lf` re-runs only recorded failures, and with none recorded it runs the whole suite unless `--last-failed-no-failures none` is set, while early-stop and output options are capabilities of the installed runner version.
