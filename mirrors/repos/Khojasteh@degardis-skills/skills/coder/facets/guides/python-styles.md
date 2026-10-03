---
title: Python docstring contracts and styles
applicability:
- When a docstring is among what the work produces or assesses
x-claim-provenance:
- claim: A docstring is a string literal that is the first statement of a module, function, class, or method, and a multi-line docstring has a summary line, a blank line, and then a fuller description.
  source: https://peps.python.org/pep-0257/
- claim: Sphinx's Napoleon extension parses NumPy and Google style docstrings and converts them to reStructuredText before Sphinx parses them.
  source: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
- claim: doctest finds text that looks like interactive Python sessions and executes it to verify that it works exactly as shown.
  source: https://docs.python.org/3/library/doctest.html
---

The project's configured docstring parser and generator determine the syntax they recognize, while the owning package or module establishes the local style convention. Google-style sections, NumPy-style sections, reStructuredText field lists, and other parser conventions are not interchangeable merely because a human can understand them; an unsupported form can render as ordinary prose. The opening summary and spacing also inherit the project's adopted PEP 257 convention.

Annotations remain the owner of types they already state, so duplicated type prose adds no independent contract, and an annotation is code rather than documentation. Generator and yield sections describe yielded values according to the configured parser, while an async function's documented result is the consumer-visible awaited result. Call-time failure and failure during awaiting or iteration remain distinct when the reader observes them differently.

Module documentation placement, public-surface coverage, and property or generated-field documentation depend on where the configured tool actually reads them; some configurations require module documentation as the first statement. When doctest collection is configured, a `>>>` example becomes executable evidence, whereas a non-doctest code block can remain purely illustrative.
