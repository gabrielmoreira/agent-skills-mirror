# JS/TS high-risk refactors (add to "avoid" set)

- Adding/removing `await` or changing async boundaries (microtask/macrotask ordering)
- Truthy/nullish changes (`||` vs `??`); `==` vs `===` behavior shifts
- Object/field initialization order and enumerable property order assumptions
- Converting `function` declarations/expressions to arrow functions (changes `this`, `arguments`, `new`, `prototype`)
- Removing optional chaining (`?.`) or nullish coalescing (`??`) without type-checker proof (even if it looks redundant)
