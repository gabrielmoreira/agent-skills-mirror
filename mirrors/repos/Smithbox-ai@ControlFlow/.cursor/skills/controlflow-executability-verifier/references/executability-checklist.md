# Executability Checklist

Use this grid during the cold-start simulation in `controlflow-executability-verifier`.

## Per-Task 8-Point Checklist

| Dimension | Pass | Fail indicator |
| --- | --- | --- |
| `what_clear` | The task objective is stated with no ambiguity | Objective uses vague terms ("update", "fix", "improve") without a concrete target |
| `where_clear` | Exact file paths, modules, or components are identified | Phase says "relevant files" or relies on executor to guess locations |
| `how_clear` | The approach is described in enough detail for a fresh executor | Phase says "implement as appropriate" or similar placeholder |
| `inputs_defined` | All required inputs (data, config, environment, upstream artifacts) are named | Phase depends on an output from a prior phase that is not explicitly described |
| `outputs_defined` | The expected deliverables (files, symbols, passing tests) are described | Phase says only "code the feature" without saying what done looks like |
| `dependencies_met` | Every library, tool, or service the phase requires is listed and available | Phase imports a package not in the current dependency manifest |
| `verify_command_complete` | A runnable verification command is given (e.g., `npm test`, `cargo check`) | Phase says "run the tests" without specifying which command |
| `test_specifics_concrete` | Test names, files, or acceptance signals are explicit | Phase says "write tests" without naming the harness, file, or behavior |

## TDD Walk-Through Steps

For each simulated task, mentally execute this sequence and stop at the first real blocker:

1. `open_file` — can you locate the exact file? If the file does not exist, is there a create instruction?
2. `read_existing_code` — does the plan acknowledge the existing implementation? Does it say what to preserve or discard?
3. `write_test_red` — can a failing test be written from the phase description alone?
4. `run_test` — is there a runnable command to confirm the test fails?
5. `write_implementation_green` — can the implementation be written without guessing API names, signatures, or patterns not stated in the plan?
6. `run_test_again` — is the same verification command still valid after implementation?
7. `refactor` — does the plan flag refactoring scope or leave it implicit?

## Blocker Classification

| Class | Description | Outcome |
| --- | --- | --- |
| Hard blocker | Cannot proceed without undocumented external knowledge | `FAIL` |
| Soft blocker | Can make a reasonable guess but should not have to | `WARN` |
| Not a blocker | Clear enough to proceed | `PASS` |

## Stopping Rule

Stop at the **first hard blocker** in a task and record exactly why execution would stall. Do not continue past a hard blocker with assumed context.
