---
title: unittest
category: Test framework
description: Tests written with Python's standard-library unittest framework, whether its own runner or another one runs them.
x-claim-provenance:
- claim: patch() replaces the object a name points to, so the name used by the system under test is patched where it is looked up rather than where it is defined, and the patch is undone when the decorated function or with statement exits.
  source: https://docs.python.org/3/library/unittest.mock.html
- claim: Cleanup functions added with addCleanup are called even when setUp fails and tearDown is not called, subTest parameters are displayed whenever a subtest fails, and IsolatedAsyncioTestCase, added in Python 3.8, accepts coroutines as test functions.
  source: https://docs.python.org/3/library/unittest.html
- claim: The unittest command line provides -b to buffer the output of passing tests, -f to stop on the first error or failure, -k to select tests by pattern or substring, and discover -s and -t for the start and top-level directories, and it documents no option to shuffle or parallelize tests.
  source: https://docs.python.org/3/library/unittest.html
---

`unittest.mock.patch` replaces the name that the code under test resolves rather than the original definition, and its decorator and context-manager forms restore that patch automatically. Specific assertions such as `assertEqual`, `assertIs`, and `assertAlmostEqual` preserve the intended comparison better than wrapping the comparison in `assertTrue`. `setUp` and `tearDown` together with `addCleanup` provide cleanup that survives an earlier failure, `assertRaises` and `assertRaisesRegex` express expected failures as context managers, and `IsolatedAsyncioTestCase` provides coroutine-aware test cases. `subTest` carries keyword per-case context, which the standard-library runner displays for each failing subtest; another runner reports subtests only as far as it supports them.

Where the standard-library runner offers no seed, shuffle, repeat, or parallelism control, order dependence can be compared between an isolated test and its containing module, and adding another runner solely to obtain randomization would change the execution system being observed. `python -m unittest module.Class.test_method` runs a single test and `python -m unittest discover -s <start> -t <top>` discovers tests, while `-k` narrows by name, `-f` stops early, `-b` buffers the output of passing tests, and `-v` adds a line for every passing test.
