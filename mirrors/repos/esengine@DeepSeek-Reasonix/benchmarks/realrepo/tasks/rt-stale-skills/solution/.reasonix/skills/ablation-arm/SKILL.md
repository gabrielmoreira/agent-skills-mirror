---
name: ablation-arm
description: Add a new switchable subsystem to the benchmark's ablation arms.
---

# Adding an ablation module

1. Declare the module as a `Module` constant in
   `internal/contract/ablation/ablation.go` beside the others.
2. Add it to `Modules()`, in the position arm names should list it; `Parse`
   and the `all` spec read that list, so nothing else registers it.
3. Arm names come from `Set.Arm()`; check that yours reads `no-<module>` and
   that `Set.String()` still round-trips through `Parse`.
4. Flag help needs no edit: `benchctl arm` builds it from `ModuleList()`.
5. Add the module's row to the README's ablation table.
6. Run `make check`.
