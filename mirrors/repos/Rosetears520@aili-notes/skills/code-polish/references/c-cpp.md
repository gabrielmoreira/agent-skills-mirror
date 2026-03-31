# C/C++ high-risk refactors (add to "avoid" set)

- Object lifetime / move/copy timing changes; temporary lifetime and RAII side effects
- UB risk via subtle reordering; macro-dependent behavior; sequence points
- Iterator invalidation; pointer/reference stability; allocation/reallocation timing
