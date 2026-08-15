---
name: testng-skill
description: "Writes Java TestNG classes with @Test groups, @DataProvider, testng.xml suites, parallel thread-count, ITestListener, and SoftAssert. Trigger on TestNG, Surefire suite XML, or dependsOnMethods. Not for pytest/conftest (pytest-skill) or JUnit-only trees."
version: 1.0.1
risk: unknown
source: https://github.com/LambdaTest/agent-skills/tree/main/testng-skill
source_repo: LambdaTest/agent-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/LambdaTest/agent-skills/blob/main/LICENSE
---

# TestNG Testing Skill

## Overview

This skill provides production-grade TestNG test generation patterns for Java projects. It covers groups, data providers, parallel execution, XML suite configuration, listeners, soft assertions, and lifecycle annotations. Use the core patterns below for everyday work; load the deep playbook reference when the task requires advanced configuration such as thread-safe drivers, factories, CI/CD integration, or reporting frameworks.

## When to Use

Use this skill when the user needs to generate or configure TestNG tests in Java. Trigger keywords and phrases:

- "TestNG"
- "@DataProvider"
- "testng.xml"
- "TestNG suite"
- "parallel tests Java"
- "groups" (in a Java testing context)
- "@Listeners", "ITestListener"
- "SoftAssert"
- "dependsOnMethods"
- "Surefire TestNG"

Do **not** use this skill for JUnit-only projects. If the user mentions JUnit without TestNG, defer to a JUnit skill.

## Prerequisites

1. **Java 8+** installed and on `PATH`. Verify:
   ```powershell
   java -version
   ```
2. **Maven 3.6+** installed and on `PATH`. Verify:
   ```powershell
   mvn -version
   ```
3. **TestNG dependency** in `pom.xml`:
   ```xml
   <dependency>
     <groupId>org.testng</groupId>
     <artifactId>testng</artifactId>
     <version>7.10.2</version>
     <scope>test</scope>
   </dependency>
   ```
4. **Maven Surefire Plugin** configured to use TestNG and point at the suite XML:
   ```xml
   <plugin>
     <groupId>org.apache.maven.plugins</groupId>
     <artifactId>maven-surefire-plugin</artifactId>
     <version>3.2.5</version>
     <configuration>
       <suiteXmlFiles>
         <suiteXmlFile>testng.xml</suiteXmlFile>
       </suiteXmlFiles>
     </configuration>
   </plugin>
   ```
5. On Windows (PowerShell), ensure line endings in `testng.xml` are LF or CRLF consistently; mixed endings can cause Surefire parsing errors.

## Procedure

### 1. Identify the test scenario

Determine which TestNG features the user needs:

| Need | Feature |
|------|---------|
| Run subsets of tests | Groups (`@Test(groups = "smoke")`) |
| Feed multiple data sets | `@DataProvider` |
| Run tests concurrently | Parallel execution in `testng.xml` |
| Configure multi-env suites | `testng.xml` suite XML |
| Capture failures, retries, screenshots | `@Listeners` + `ITestListener` |
| Collect multiple assertion failures | `SoftAssert` |
| Cross-browser matrix | `@Factory` (see playbook §5) |

### 2. Write the test class

Use the lifecycle annotation order as a mental model:

```
@BeforeSuite → @BeforeTest → @BeforeClass → @BeforeMethod → @Test → @AfterMethod → @AfterClass → @AfterTest → @AfterSuite
```

**Basic test with groups:**

```java
import org.testng.annotations.*;
import org.testng.Assert;

public class LoginTest {
    @BeforeMethod
    public void setUp() { /* setup */ }

    @Test(groups = "smoke")
    public void testLoginSuccess() {
        Assert.assertTrue(loginService.login("user@test.com", "password123"));
    }

    @Test(groups = "regression", dependsOnMethods = "testLoginSuccess")
    public void testAccessDashboard() {
        Assert.assertNotNull(dashboard.getContent());
    }

    @Test(expectedExceptions = AuthenticationException.class)
    public void testLoginInvalidPassword() {
        loginService.login("user@test.com", "wrong");
    }

    @AfterMethod
    public void tearDown() { /* cleanup */ }
}
```

### 3. Add data providers when test data is reusable

```java
@DataProvider(name = "loginData")
public Object[][] loginData() {
    return new Object[][] {
        {"admin@test.com", "admin123", true},
        {"user@test.com", "password", true},
        {"invalid@test.com", "wrong", false},
    };
}

@Test(dataProvider = "loginData")
public void testLogin(String email, String password, boolean expected) {
    Assert.assertEquals(loginService.login(email, password), expected);
}
```

For advanced data providers (Excel, JSON, CSV, parallel, cross-class), load **`references/playbook.md` §4**.

### 4. Create the `testng.xml` suite file

```xml
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Regression" parallel="tests" thread-count="5">
  <test name="Smoke">
    <groups><run><include name="smoke"/></run></groups>
    <classes><class name="tests.LoginTest"/></classes>
  </test>
  <test name="Full">
    <groups><run><include name="regression"/><exclude name="flaky"/></run></groups>
    <packages><package name="tests.*"/></packages>
  </test>
</suite>
```

### 5. Configure parallel execution

Choose the granularity:

```xml
<suite parallel="methods" thread-count="5">   <!-- Method level -->
<suite parallel="classes" thread-count="5">    <!-- Class level -->
<suite parallel="tests" thread-count="5">      <!-- Test level -->
```

For thread-safe driver patterns (`ThreadLocal`, `ConfigReader`), load **`references/playbook.md` §3**.

### 6. Use soft assertions for multi-check scenarios

```java
SoftAssert soft = new SoftAssert();
soft.assertEquals(user.getName(), "Alice");
soft.assertEquals(user.getAge(), 25);
soft.assertTrue(user.isActive());
soft.assertAll();  // Reports all failures at once
```

### 7. Add listeners for production-grade reporting

```java
public class TestListener implements ITestListener {
    @Override public void onTestFailure(ITestResult result) {
        System.out.println("Failed: " + result.getName());
        // Take screenshot, log, etc.
    }
}

@Listeners(TestListener.class)
public class LoginTest { /* ... */ }
```

For production listener suites (retry analyzers, screenshot capture, timing), load **`references/playbook.md` §6**.

### 8. Run the tests

| Task | Command (PowerShell) |
|------|---------------------|
| Run suite | `mvn test -DsuiteXmlFile=testng.xml` |
| Run group | `mvn test -Dgroups=smoke` |
| Run single class | `mvn test -Dtest=LoginTest` |
| Run single method | `mvn test -Dtest=LoginTest#testLoginSuccess` |

### 9. Check reports

Default TestNG HTML report:

```
test-output\index.html
```

Open in a browser:
```powershell
Start-Process test-output\index.html
```

For Allure or ExtentReports integration, load **`references/playbook.md` §10**.

## Pitfalls

### Hard rules — do not violate

1. **Never use `dependsOnMethods` everywhere.** Cascading failures make debugging impossible. Prefer independent tests; use `dependsOnGroups` sparingly for true ordering dependencies.
2. **Never omit groups.** Without `@Test(groups = "...")` you cannot run subsets via `-Dgroups`. Always assign at least one group.
3. **Never hard-code test data inside test methods when a data provider is appropriate.** Use `@DataProvider` for reusable, maintainable data sets.
4. **Never rely on `priority` ordering as a substitute for independent tests.** Priority-based ordering is fragile and breaks when tests are added or removed.
5. **Never assume thread safety in parallel mode.** When `parallel="methods"` or higher, shared state (e.g., a static `WebDriver`) will cause race conditions. Use `ThreadLocal` per-thread drivers.
6. **Never mix line endings in `testng.xml` on Windows.** Ensure consistent LF or CRLF; mixed endings can cause Surefire XML parsing failures.

### Anti-patterns quick reference

| Bad | Good | Why |
|-----|------|-----|
| `dependsOnMethods` everywhere | Independent tests | Cascading failures |
| No groups | `@Test(groups = "smoke")` | Can't run subsets |
| Hard-coded test data | `@DataProvider` | Reusable |
| Priority ordering | Independent tests | Fragile |
| Shared static driver in parallel | `ThreadLocal<WebDriver>` | Race conditions |
| `Assert` after every check in long method | `SoftAssert.assertAll()` at end | Only first failure reported |

### Common debugging problems

For the full 12-problem debugging quick-reference, load **`references/playbook.md` §12**.

## Verification

After generating or modifying TestNG tests, verify with these checkable steps:

1. **Compile the project:**
   ```powershell
   mvn compile test-compile
   ```
   Expected: `BUILD SUCCESS`

2. **Run the suite and confirm tests execute:**
   ```powershell
   mvn test -DsuiteXmlFile=testng.xml
   ```
   Expected: `BUILD SUCCESS` with `Tests run: N, Failures: 0, Errors: 0, Skipped: 0`

3. **Run a specific group to confirm group filtering works:**
   ```powershell
   mvn test -Dgroups=smoke
   ```
   Expected: only tests annotated `@Test(groups = "smoke")` execute.

4. **Verify the HTML report was generated:**
   ```powershell
   Test-Path test-output\index.html
   ```
   Expected: `True`

5. **Verify parallel execution by checking thread count in logs** — TestNG logs thread pool usage when `parallel` is set. Confirm `thread-count` matches the suite XML value.

6. **Verify data provider invocation count** — a test using `@DataProvider` with 3 data rows should show `Tests run: 3` for that single method.

## References

The following reference file contains deep patterns beyond the core skill:

| File | When to Load |
|------|-------------|
| `references/playbook.md` | When the task requires advanced configuration: Maven/Surefire setup, multi-env suite XML, `ThreadLocal` drivers, Excel/JSON/CSV data providers, `@Factory` cross-browser matrix, production listeners (retry, screenshot, timing), Page Object integration, mixed parallel strategies, Allure/ExtentReports, CI/CD (GitHub Actions, Jenkins), or the 12-problem debugging guide. |

### Playbook section index

| § | Section | Focus |
|---|---------|-------|
| 1 | Project Setup & Configuration | Maven + Surefire config |
| 2 | Suite XML Configuration | Multi-env, parallel, groups |
| 3 | BaseTest & Thread-Safe Driver | ThreadLocal, ConfigReader |
| 4 | Data Providers (Advanced) | Excel, JSON, CSV, parallel, cross-class |
| 5 | Factory Pattern | Cross-browser matrix |
| 6 | Listeners (Production Suite) | Retry, screenshot, timing |
| 7 | Soft Assertions & Dependencies | Groups, method deps |
| 8 | Page Object Integration | PageFactory, fluent POs |
| 9 | Parallel Execution Strategies | Method/class/test/mixed |
| 10 | Reporting Integration | Allure, ExtentReports |
| 11 | CI/CD Integration | GitHub Actions, Jenkins |
| 12 | Debugging Quick-Reference | 12 common problems |
| 13 | Best Practices Checklist | 14 items |

## Limitations

- Use this skill only when the task clearly matches TestNG testing in Java and the local project context supports it.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- This skill does not cover TestNG for Kotlin or non-JVM languages.

## Related Skills

- **junit-skill** — JUnit 5 testing patterns (use when the project uses JUnit, not TestNG).
- **maven-skill** — Maven build lifecycle and plugin configuration (use when configuring Surefire/Failsafe beyond TestNG defaults).
- **selenium-skill** — Selenium WebDriver patterns (use alongside this skill for browser automation tests with TestNG).
