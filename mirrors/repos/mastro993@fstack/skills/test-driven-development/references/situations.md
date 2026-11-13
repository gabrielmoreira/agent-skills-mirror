# Situations

Read the parts that match the work.

## Bug fix

1. Write a test with the input from the report and the expected result, at the lowest level that reproduces it. It goes red with the wrong result the report describes.
2. Fix the code; run the whole suite.
3. An existing test that asserts the buggy result pins the bug: correct its expected value in the same red and name it in the report. When it then covers the same behavior as the new test, keep the one with the reported input.
4. The same mistake nearby (the other branch, a sibling function) is a new list item, not a silent extra fix.

One regression test per bug, in the unit's existing test file.

## Untested code

Before changing code without tests:

- **Characterization tests**: assert what the code does now, even when it looks wrong, for the part the change touches.
- **Seams**: break a dependency on the clock, database, or network through a parameter, an injected module, or a function argument.
- **Sprout**: write the new behavior test-first in a new function and call it from the old code. **Wrap**: give the old name to a new function that calls the renamed original plus the new behavior.

## A feature across layers

The double loop: one failing acceptance test for the main path as a user sees it, then unit cycles for each piece until it goes green. Edge cases live at the unit level only. With nothing running end to end yet, build the walking skeleton first: the thinnest slice that boots and runs one test in CI.

## UI components

Drive them through what the user perceives with Testing Library or the platform's equivalent: query by role and accessible name, then label, then text; interact with user events; assert visible text and enabled, disabled, present, or gone. Double only navigation, network, and native modules. Test hooks through a component, or `renderHook` for a reusable one. Assert the specific thing rather than snapshot a whole tree.

## Third-party libraries and services

Wrap them in an adapter in your domain's words, test the adapter against the real thing or its emulator, and double the adapter elsewhere. When unsure how the library behaves, a **learning test** settles it; keep it only when your code relies on that behavior.

## Invariants and wide input spaces

A rule that holds for every input (parsers, encoders, dates, money) fits one property-based test (fast-check, Hypothesis, proptest, jqwik) in place of a long list of examples, plus a few hand-picked boundary rows so a reader sees the rule.

## State stores

Dispatch actions and assert on state or selectors, with fakes for the store's adapters, rather than stepping through a saga's internal effects.
