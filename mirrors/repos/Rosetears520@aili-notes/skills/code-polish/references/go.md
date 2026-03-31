# Go high-risk refactors (add to "avoid" set)

- Error-check order changes (which error occurs first is observable)
- `defer` timing or location changes; early-return refactors that move/skip defers
- `range` variable capture issues (closures); address-of loop variable mistakes
- `nil` interface vs typed-nil behavior changes; `map` iteration order reliance
