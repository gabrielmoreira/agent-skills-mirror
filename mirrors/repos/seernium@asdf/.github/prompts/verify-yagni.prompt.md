# /verify-yagni

Audits the codebase or a specific batch of changes to ensure zero speculative engineering (YAGNI compliance).

## Protocol
1. Scan the proposed or recently modified files for:
   - Unused interfaces or types created "for future use"
   - Placeholder methods, endpoints, or parameter options that are not used by the current UI/API flow
   - Configuration options or database columns that have no active consumers
2. For each identified redundant item, generate a clean suggestion to **prune/delete** it.
3. Hand off to `@planner` and `@code-reviewer` to verify that deleting the redundant blocks does not disrupt type safety or active code dependencies.
4. Remember: "The best code is no code." Less code means less surface area for bugs, performance drift, and technical debt.
