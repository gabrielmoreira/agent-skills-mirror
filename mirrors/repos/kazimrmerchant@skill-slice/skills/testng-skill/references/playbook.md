# TestNG playbook

Load this file when `SKILL.md` points at a section: Surefire, multi-env XML, `ThreadLocal` drivers, advanced data providers, `@Factory`, production listeners, reporting, or CI. Patterns target TestNG 7.10.x and Maven Surefire 3.2.x. Official docs: `https://testng.org/` and `https://maven.apache.org/surefire/maven-surefire-plugin/examples/testng.html`.

This is **not** a pytest playbook. Python fixtures, `conftest.py`, and `@pytest.mark` belong in `pytest-skill`.

## §1 Project setup (Maven + Surefire)

```xml
<dependency>
  <groupId>org.testng</groupId>
  <artifactId>testng</artifactId>
  <version>7.10.2</version>
  <scope>test</scope>
</dependency>
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

Override the suite at the CLI: `mvn test -DsuiteXmlFile=suites/smoke.xml`. Group filter: `mvn test -Dgroups=smoke`. Single class: `mvn test -Dtest=LoginTest`. Keep `testng.xml` line endings consistent on Windows (mixed LF/CRLF breaks Surefire parsing).

Surefire 3.6+ can run TestNG through the JUnit Platform engine; this pack stays on suite-XML configuration unless the project already migrated.

## §2 Suite XML (multi-env, groups, parallel)

```xml
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Regression" parallel="tests" thread-count="5">
  <parameter name="env" value="staging"/>
  <test name="Smoke">
    <parameter name="browser" value="chrome"/>
    <groups><run><include name="smoke"/><exclude name="flaky"/></run></groups>
    <classes><class name="tests.LoginTest"/></classes>
  </test>
  <test name="Full">
    <packages><package name="tests.*"/></packages>
  </test>
</suite>
```

`parallel` values: `methods`, `classes`, `tests` (and `instances` when using factories). `thread-count` is the pool size. Parameters in XML are strings; complex objects go through `@DataProvider` (§4).

From TestNG 7.9, suite attributes `share-thread-pool-for-data-providers` and `use-global-thread-pool` need the 1.1 DTD if the IDE should autocomplete them.

## §3 BaseTest and thread-safe driver

`parallel="methods"` plus a static `WebDriver` races. One driver per thread:

```java
public final class DriverFactory {
    private static final ThreadLocal<WebDriver> DRIVERS = new ThreadLocal<>();
    public static void set(WebDriver driver) { DRIVERS.set(driver); }
    public static WebDriver get() { return DRIVERS.get(); }
    public static void unload() {
        WebDriver d = DRIVERS.get();
        if (d != null) d.quit();
        DRIVERS.remove();
    }
}

public class BaseTest {
    @BeforeMethod(alwaysRun = true)
    public void openBrowser(ITestContext ctx) {
        String browser = ctx.getCurrentXmlTest().getParameter("browser");
        DriverFactory.set(createDriver(browser));
    }
    @AfterMethod(alwaysRun = true)
    public void closeBrowser() { DriverFactory.unload(); }
}
```

Read env URLs from a `ConfigReader` (properties / env vars), never from literals in `@Test` methods. `singleThreaded = true` on a class pins that class to one thread when the suite is `parallel="methods"`.

## §4 Data providers (Excel / JSON / CSV, parallel, other class)

```java
@DataProvider(name = "loginData", parallel = true)
public Object[][] loginData() { /* rows */ }

@Test(dataProvider = "loginData")
public void testLogin(String email, String password, boolean expected) { }

@DataProvider(name = "fromCsv")
public Object[][] fromCsv() throws Exception {
    // parse CSV/JSON/Excel into Object[][]; never hard-code secrets
}

@Test(dataProvider = "fromCsv", dataProviderClass = LoginData.class)
public void testLoginExternal(String email, String password) { }
```

A provider on another class must be `static` (or the class must have a no-arg constructor) when `dataProviderClass` is set. Default parallel data-provider pool size is 10; raise it with `data-provider-thread-count` on `<suite>` or Surefire `<property><name>dataproviderthreadcount</name>`.

## §5 Factory (cross-browser matrix)

```java
public class BrowserFactory {
    @Factory
    public Object[] chromeAndFirefox() {
        return new Object[] { new LoginTest("chrome"), new LoginTest("firefox") };
    }
}
```

Each factory instance gets its own object; instance fields are safe across browsers. Combine with `parallel="instances"` when the matrix should run together. Do not also `@Factory` a class that already uses a process-wide static driver.

## §6 Listeners (retry, screenshot, timing)

```java
public class TestListener implements ITestListener {
    @Override public void onTestFailure(ITestResult result) {
        WebDriver d = DriverFactory.get();
        if (d instanceof TakesScreenshot ts) {
            File shot = ts.getScreenshotAs(OutputType.FILE);
            // copy next to test-output; do not swallow IOException
        }
    }
}
```

Wire with `@Listeners(TestListener.class)` or `<listeners><listener class-name="…"/></listeners>` in XML. `IAnnotationTransformer` **must** be declared in XML (too early for `@Listeners`).

Retry analyzer (failed → rerun, cap the count):

```java
public class Retry implements IRetryAnalyzer {
    private int n;
    public boolean retry(ITestResult result) { return n++ < 1; }
}
@Test(retryAnalyzer = Retry.class, groups = "flaky")
```

Retries hide flakes; log every retry and keep the group so CI can quarantine. `IInvokedMethodListener` is the hook for per-method timing.

Listener order (TestNG 7.10+): implement `ListenerComparator` and pass `-listenercomparator`.

## §7 Soft asserts and dependencies

`SoftAssert.assertAll()` reports every failure in the method. Forgetting `assertAll()` marks the test green. Prefer independent tests; `dependsOnMethods` cascades skips. `dependsOnGroups` is the less-brittle ordering tool. Do not use `priority=` as a substitute for isolation.

## §8 Page objects

```java
public class LoginPage {
    private final WebDriver driver;
    public LoginPage(WebDriver driver) {
        this.driver = driver;
        PageFactory.initElements(driver, this);
    }
    @FindBy(id = "email") private WebElement email;
    public LoginPage typeEmail(String value) { email.sendKeys(value); return this; }
}
```

Construct pages with `DriverFactory.get()`, not `new ChromeDriver()`. Fluent returns keep tests linear. Locators stay in the page class.

## §9 Parallel strategies

| `parallel` | What shares a thread | Typical use |
| --- | --- | --- |
| `methods` | Nothing (except `dependsOn*` order) | Independent unit-like tests; requires ThreadLocal |
| `classes` | Methods in one class | Classes that share mutable fixtures |
| `tests` | Everything inside one `<test>` | Multi-env XML blocks |
| `instances` | One `@Factory` instance | Browser matrix |

Mixed: smoke `<test>` with `parallel="classes"` and a slower UI `<test>` with `parallel="methods"`. Do not mix a static driver with `methods`. From 7.9, `use-global-thread-pool=true` shares one pool between regular methods and data-driven methods (`thread-count` sizes it).

## §10 Reporting (Allure / Extent)

Default HTML: `test-output/index.html`. Allure: add `allure-testng`, write results to `allure-results`, then `allure serve`. ExtentReports: implement `ITestListener` / `IReporter` and flush in `onFinish`. Attach screenshots from §6 into the report object, not only stdout.

## §11 CI/CD

GitHub Actions sketch: JDK 17, `mvn -B test -DsuiteXmlFile=testng.xml`, upload `test-output/` and Allure results as artifacts. Jenkins: Maven job with the same suite property; publish Surefire / Allure plugins. Fail the build on `Failures`/`Errors` ≠ 0; do not `-DskipTests` to go green.

## §12 Debugging (twelve frequent failures)

1. **0 tests run** — Surefire `suiteXmlFile` path wrong, or package name in XML does not match.
2. **Group filter empty** — method missing `@Test(groups=…)`; `-Dgroups` then selects nothing.
3. **`dependsOnMethods` skip storm** — one failure skips the chain; drop the dependency.
4. **Stale element / random browser** — static WebDriver under `parallel="methods"`; switch to ThreadLocal.
5. **Data provider `IllegalArgumentException`** — row arity ≠ test parameters.
6. **Provider method not found** — name mismatch, or `dataProviderClass` method not static.
7. **SoftAssert green** — missing `assertAll()`.
8. **XML parse error on Windows** — mixed line endings in `testng.xml`.
9. **IAnnotationTransformer ignored** — declared only with `@Listeners`; move to XML.
10. **Retry loops forever** — `IRetryAnalyzer` without a cap.
11. **Factory × parallel clash** — instance fields plus a process-wide driver.
12. **Allure empty** — adapter not on the test classpath, or results directory not uploaded.

## §13 Checklist

1. Every `@Test` has at least one group.
2. Tests are independent unless a real `dependsOnGroups` exists.
3. Data lives in `@DataProvider`, not literals (except tiny smoke values).
4. Parallel suites use ThreadLocal (or `singleThreaded`) for WebDriver.
5. `assertAll()` on every `SoftAssert`.
6. Listeners capture failure screenshots.
7. Retry is capped and grouped as flaky.
8. Suite XML line endings are uniform.
9. Surefire points at the intended suite file.
10. Reports are opened after `mvn test` (`test-output/index.html`).
11. CI uploads reports and fails on errors.
12. No secrets in XML parameters or provider tables.
13. JUnit-only modules are not forced through this chair (`junit-skill`).
14. Pytest trees are not rewritten as TestNG (`pytest-skill`).
