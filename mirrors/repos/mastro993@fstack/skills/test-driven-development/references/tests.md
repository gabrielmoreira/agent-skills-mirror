# Tests worth keeping

## Behavior, not implementation

A new behavior calls for a new test; a new method or class doesn't. Test through the public surface of a module (function, hook, component, use case, endpoint) and let private helpers be covered through it. Then the refactor step has a net that holds while structure changes: if renaming a private function or swapping a library breaks a test while users see no change, that test measures the wrong thing.

## Shape

- **Arrange, act, assert**: only the setup this behavior needs, one action, assertions about one behavior.
- **Deterministic**: the clock, random source, and HTTP client come in as parameters or injected dependencies.
- **Independent expected values**: a literal from the spec. A value computed the way the code computes it passes by construction:

```ts
const expected = items.reduce((sum, i) => sum + i.price, 0); // passes whatever the code does
expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15); // can disagree with the code
```

| Done when | If not |
| --- | --- |
| You saw it fail for the right reason | Break the code on purpose; watch it go red |
| It survives a pure refactor of the internals | Test through the public behavior |
| Its name explains the behavior; its failure says what broke | Rename; use a more specific matcher |
| No other test pins the same behavior | Merge or drop one |

## Doubles

Real objects inside your own code; doubles at the boundaries (network, storage, clock, OS, other services).

- **Wrap what you don't own**: a thin adapter you own around a third-party API, doubled elsewhere, with a few integration tests of its own.
- **Fakes for stateful dependencies**: an in-memory store doesn't encode call order the way a mock does.
- **Intercept the network** at the request level (MSW, `responses`, WireMock, `httptest`) rather than stubbing a fetch wrapper in every test.
- **Listen to the tests**: many mocks, mocks returning mocks, or a mocked value object is design feedback.

## Level

Pure logic: many fast unit tests. UI: mostly component tests through what the user perceives. End-to-end: a few critical journeys, outside the inner loop. Types and lint sit under all of them, so a test never re-checks what the compiler guarantees. Coverage is a flashlight, not a target.

## Smells

| Symptom | Cause | Fix |
| --- | --- | --- |
| A refactor breaks many tests | Coupled to internals or call order | Test public behavior; delete fine-grained duplicates |
| Huge arrange | Too many dependencies | Split responsibilities; builders for test data |
| Flaky | Real time, timers, network, shared state | Inject the clock, fake timers, intercept, reset state |
| Slow suite | Too much end-to-end, heavy setup | Push tests down to the cheapest level |
| Green but bugs ship | Weak assertions, testing mocks | Assert what the user sees; mutation testing |
| Long red | Steps too big | Revert; smaller test |
| Dozens of near-identical tests | One test per input | One table, one row per case |

## A cycle, start to finish

Credential status: `valid`, `expiring` (≤ 30 days left), or `expired`.

1. Red `valid when expiry is far in the future`; green by Fake It: `return 'valid'`.
2. Red `expired when expiry is in the past`; green: `expiry <= now ? 'expired' : 'valid'`.
3. `expired exactly now` passes at once but pins a decision: flip `<=` to `<`, see red, flip back.
4. Red `expiring when 30 days or fewer remain`; green: a second branch.
5. Refactor code (a named window constant) and tests, folding the examples into one table:

```ts
it.each([
  ['2027-06-01T00:00:00Z', 'valid'],
  ['2026-12-12T10:00:01Z', 'valid'],    // 30 days + 1 s
  ['2026-12-12T10:00:00Z', 'expiring'], // exactly 30 days
  ['2026-11-12T10:00:00Z', 'expired'],  // exactly now
] as const)('expiry %s -> %s', (iso, expected) => {
  expect(getCredentialStatus(new Date(iso), NOW)).toBe(expected);
});
```

The clock is a parameter, every boundary is a row, and the expected values came from the spec.
