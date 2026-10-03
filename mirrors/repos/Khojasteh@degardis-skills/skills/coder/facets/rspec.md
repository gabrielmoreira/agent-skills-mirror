---
title: RSpec
category: Test framework
x-claim-provenance:
- claim: let defines a memoized helper that is lazily evaluated on first use and cached within one example but not across examples, while let! forces its invocation before each example.
  source: https://rspec.info/features/3-13/rspec-core/helper-methods/let/
  scope: RSpec 3.13.
- claim: Passed together with --seed, --bisect repeatedly runs subsets of the suite to isolate the minimal set of examples that reproduce the same failures.
  source: https://rspec.info/features/3-13/rspec-core/command-line/bisect/
  scope: RSpec 3.13.
- claim: --only-failures runs only examples that failed the last time they ran, --next-failure is shorthand for --only-failures --fail-fast --order defined, and both require config.example_status_persistence_file_path, without which --only-failures raises an error.
  source: https://rspec.info/features/3-13/rspec-core/command-line/only-failures/
  scope: RSpec 3.13.
---

RSpec examples are `it` blocks inside `describe` or `context`, with setup through `before` or `around` and an expected failure written as `expect { ... }.to raise_error(SpecificError, /message/)`. `let` defines lazy per-example state and avoids the wider mutable surface of an instance variable assigned in `before`, while `let!` performs its side effect eagerly, so eagerness is observable test behavior rather than a stylistic synonym. An implicit `subject` is useful only when it improves readability.

Isolation depends on the project's seams for time and collaborators, and shared `before(:all)` state or mutated constants can create interference between examples. `--order random` with the failing run's exact `--seed` reproduces order dependence, and `--bisect` can reduce that failure to a smaller interfering set. A run narrows by file and line, `-e`, or, where `example_status_persistence_file_path` is configured, `--only-failures` or `--next-failure`, while `--format progress` reduces output, `--fail-fast` stops after a failure, and `--dry-run` lists examples without executing them.
