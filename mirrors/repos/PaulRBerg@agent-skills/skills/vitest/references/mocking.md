# Mocking

> Mock boundaries and own their cleanup; prefer dependency injection when it keeps the production interface simpler.

- `vi.mock` is hoisted. Keep it at file scope; put handles used by its factory in `vi.hoisted`. Its specifier must be
  identical to the production `import` specifier, and it cannot mock `require()`.
- Create a fresh result from every stateful mock factory per test. Keep one-off module wiring in that file; share only
  repository-conventional factories.
- Install fake timers before code schedules work. Use async advancement when callbacks schedule promises, and always
  restore real timers. Do not combine fake timers with uncontrolled real waits.
- Restore owned spies, timers, environment stubs, and replaced global property descriptors in local cleanup.
  `vi.restoreAllMocks()` restores `vi.spyOn` implementations but neither clears their history nor restores automocks;
  reset or reconfigure automocked exports explicitly.

See the installed version's [Vi API](https://vitest.dev/api/vi) for factory, timer, and stub semantics.
