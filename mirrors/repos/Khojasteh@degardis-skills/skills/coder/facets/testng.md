---
title: TestNG
category: Test framework
x-claim-provenance:
- claim: TestNG runs BeforeMethod before each test method, while factories can create multiple test instances.
  source: https://testng.org/documentation.html
- claim: TestNG's @Test expectedExceptions declares exception types expected from a test method.
  source: https://testng.org/documentation.html
- claim: TestNG Assert.assertThrows checks a runnable for an exception type, while Assert.expectThrows also returns the exception.
  source: https://javadoc.io/static/org.testng/testng/7.12.0/org/testng/Assert.html
  scope: TestNG 7.12.0 API documentation; both methods are documented as available since 6.9.5.
---

TestNG supplies parameterized cases through `@Test(dataProvider=...)` with a `@DataProvider`, and lifecycle hooks such as `@BeforeMethod`, `@AfterMethod`, `@BeforeClass`, and `@BeforeSuite`; JUnit's `@BeforeEach` is not a TestNG hook. `expectedExceptions` describes a failure expected from the whole test method, while supported TestNG versions provide `Assert.assertThrows` and `Assert.expectThrows` for a scoped throwing operation, the latter returning the exception.

Fields on a TestNG test instance are shared by every test method invoked on that instance. `@BeforeMethod` provides a per-method reset, and factories can create additional test instances with separate instance state. `dependsOnMethods`, `priority`, and shared instance state introduce ordering coupling. `invocationCount` and `threadPoolSize` can expose flake, while suite-level `parallel` configuration changes concurrency without encoding an order between tests. Build-tool filters or suite files narrow a run, and meaningful `groups` provide a project-defined boundary for focused selection.
