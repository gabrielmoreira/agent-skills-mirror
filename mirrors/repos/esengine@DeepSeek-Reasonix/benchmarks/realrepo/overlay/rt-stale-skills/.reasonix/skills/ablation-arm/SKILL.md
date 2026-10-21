---
name: ablation-arm
description: Add a new switchable subsystem to the benchmark's ablation arms.
---

# Adding an ablation module

1. Declare the module in `internal/ablation/modules.go` beside the others.
2. Register it in `AllModules()` so `ParseSpec` accepts it.
3. Arm names come from `Set.Name()`; check that yours reads `without-<module>`.
4. Add the module to the flag help text in `cmd/bench/flags.go`.
5. Run `make test`.
