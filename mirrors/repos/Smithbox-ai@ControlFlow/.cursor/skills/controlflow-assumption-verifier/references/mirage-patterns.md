# Mirage Pattern Catalog

Use these patterns when checking whether a plan is grounded in repository reality.

## Presence Mirages

1. **Phantom API**: a function, hook, or method is referenced but does not exist as claimed.
2. **Version Mismatch**: the plan assumes library behavior that the installed version may not support.
3. **Pattern Mismatch**: the plan assumes conventions that conflict with the codebase.
4. **Missing Dependency**: the plan depends on a library or tool that is not present.
5. **File Path Hallucination**: the plan names files or directories that are not there.
6. **Schema Mismatch**: the plan describes a data shape that conflicts with the actual schema.
7. **Integration Fantasy**: the plan assumes systems connect in ways the repository does not show.
8. **Scope Creep**: the plan includes tasks not traceable to the request.
9. **Test Infrastructure Mismatch**: the plan assumes the wrong test framework or pattern.
10. **Concurrency Blindness**: the plan ignores shared mutable state or collision risk in parallel work.

## Absence Mirages

1. **11. Missing Error Path**: the plan only covers the happy path.
2. **12. Missing Validation**: unsafe or unchecked input paths are ignored.
3. **13. Missing Edge Case**: empty, null, zero, boundary, or fallback behavior is omitted.
4. **14. Missing Requirement**: the request implies behavior that no phase actually delivers.
5. **15. Missing Cleanup**: resources or temporary state are created but never cleaned up.
6. **16. Missing Migration**: schema or contract changes appear without migration or rollback planning.
7. **17. Missing Security Boundary**: sensitive operations lack explicit access or safety boundaries.
