---
title: PHPUnit
category: Test framework
x-claim-provenance:
- claim: PHPUnit 11 deprecated test metadata in doc-comment annotations, and PHPUnit 12 removed that support, so test metadata has to be expressed as attributes.
  source: https://phpunit.de/announcements/phpunit-12.html
  scope: PHPUnit 12 release announcement, 2025-02-07.
- claim: --order-by accepts strategies including random, defects, depends, duration, reverse, and size, --random-order-seed sets the seed used when running tests in random order, --filter, --group, and --stop-on-failure narrow or stop a run, and --process-isolation runs each test in a separate PHP process.
  source: https://docs.phpunit.de/en/12.0/textui.html
  scope: PHPUnit 12.0 documentation.
---

Which attributes, doc-comment metadata, configuration, and deprecations PHPUnit accepts depends on the installed major version and the surrounding project convention, not on an informal age label such as `modern`. Lifecycle, data-provider, grouping, process-isolation, mock, stub, and exception APIs likewise vary by the resolved version, and stable data-row names keep parameterized failures identifiable.

A configured random order and its recorded seed can reproduce order dependence. The interference behind it is leaked static, global, database, container, clock, or filesystem state. Selecting a class, method, group, or file depends on the syntax the installed runner supports.
