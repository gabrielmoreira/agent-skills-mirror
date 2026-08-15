---
name: playwright-java
version: 1.0.1
description: "Scaffolds and hardens Playwright Java E2E tests with Page Object Model, JUnit 5, ThreadLocal parallel browsers, Allure, and CI browser install. Use when writing Java page objects, fixing flake without Thread.sleep, or wiring Maven/Jenkins/GitHub Actions. Not for TypeScript Playwright, Chrome CDP research automation (chrome-browser-automation), or k6 load tests."
category: test-automation
risk: safe
source: community
date_added: 2026-06-16
tags: [playwright, java, e2e-testing, junit5, page-object-model, allure, selenium-alternative]
tools: [claude, cursor, antigravity]
---

# Playwright Java – Advanced Test Automation

## Overview

This skill produces production-quality, enterprise-grade Playwright Java test code. It enforces the Page Object Model (POM), strict locator strategies, thread-safe parallel execution, and full Allure reporting integration.

**Opinionated choices and their rationale:**

- **POM** keeps selectors and page interactions in one place, so a UI change touches one page object instead of every test that uses that screen.
- **`ThreadLocal` lifecycle** is required because a Playwright `Page` is not thread-safe; parallel tests that share a `Page` corrupt each other in ways that look like random flake.
- **Web-first assertions** (`assertThat(locator)`) auto-retry until a timeout, which removes the timing races that `Thread.sleep()` only papers over.

Targets **Java 17+** and **Playwright 1.44+**. Some examples use newer APIs: `Locator.ariaSnapshot()` requires **Playwright 1.49+**, so bump `playwright.version` to at least `1.49.0` in `pom.xml` if you use that API.

### Reference files — load on demand

| Topic | File | When to load |
|-------|------|--------------|
| Maven POM, ConfigReader, Docker/CI setup | `config.md` | When scaffolding a new project or configuring CI/Docker |
| Component pattern, dropdowns, uploads, waits | `page-objects.md` | When writing complex page objects or component-level interactions |
| Full assertion API, soft assertions, visual testing | `assertions.md` | When writing or debugging assertions, especially soft assertions or visual checks |
| Fixtures, test data factory, auth state, retry | `fixtures.md` | When setting up test data factories, auth state reuse, or retry logic |
| Drop-in base class templates | `templates/BaseTest.java`, `templates/BasePage.java` | When scaffolding — copy these as your starting base classes |

---

## When to Use

Reach for this skill whenever the task is browser-driven end-to-end testing in Java. Trigger keywords and situations:

- **Scaffolding a new project** — you need the directory layout, `pom.xml`, and base classes to agree from day one, because retrofitting parallelism and reporting later is painful.
- **Writing Page Objects or JUnit 5 test classes** — to keep selectors and assertions on the correct side of the POM boundary.
- **Cross-browser, parallel, or Allure questions** — these are exactly the areas where naive setups silently break (shared state, missing AspectJ agent, racy property toggles).
- **Fixing flaky tests** — usually the fix is replacing `Thread.sleep()` with a wait or a web-first assertion that polls for the real condition.
- **CI/CD setup** (GitHub Actions, Jenkins, Docker) — browsers must be installed with system dependencies and artifacts (traces, Allure results) must survive a failed job.
- **Hybrid API + UI tests** — when seeding state over HTTP is faster and less brittle than clicking through a setup wizard just to reach the assertion.
- **Mentions of** "POM pattern", "BrowserContext", "Playwright fixtures", "traces", "Allure", "storageState", or "Playwright Java".

---

## Prerequisites

- **Java 17+** installed and on `PATH`.
- **Maven 3.8+** installed (`mvn --version` must succeed).
- **Playwright browsers** installed: run `mvn exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install --with-deps"` after adding the Playwright dependency to `pom.xml`.
- **Allure CLI** installed for local report viewing (`allure --version`).
- On Windows (PowerShell, primary host): ensure `JAVA_HOME` and `MAVEN_HOME` environment variables are set. Use PowerShell-compatible path separators when running commands.

---

## Procedure

### Step 1: Decide the Approach

Pick the *lightest* pattern that still covers the risk you care about — extra machinery is extra surface area for flake.

| User Request | Approach | Why |
|---|---|---|
| New project from scratch | Full scaffold — see `config.md` | Lifecycle, reporting, and parallelism must be wired together or not at all. |
| Single feature test | POM page class + JUnit 5 test class | Keeps selectors reusable and the test focused on behaviour. |
| API + UI hybrid | `APIRequestContext` alongside `Page` | Seeding via HTTP is faster and avoids testing the create-UI you don't care about. |
| Cross-browser | Parameterized test with its own per-browser stack | A test that mutates global browser state mid-run is racy under parallelism. |
| Flaky test fix | Replace `sleep` with `waitFor` / `waitForResponse` / web-first assertion | These poll for the actual condition instead of guessing a duration. |
| CI integration | `playwright install --with-deps` in pipeline | CI images lack the OS libraries the browsers link against. |
| Parallel execution | `junit-platform.properties` + `ThreadLocal` | Isolates each test's browser stack so workers cannot interfere. |
| Rich reporting | Allure + Playwright trace + video recording | A per-test trace is the one artifact that explains a CI-only failure. |

**HARD RULE — Cross-browser:** Do *not* flip a system property inside the test body — by then the browser is already launched. Use parameterized tests with per-parameter browser stacks.

**HARD RULE — Hybrid tests:** Prefer the API for *arrange* and the UI only for *assert*, so the test fails for the reason you intended.

### Step 2: Scaffold the Project Structure

Use this layout when creating a new project. Each package has exactly one reason to change:

```
src/
├── test/
│   ├── java/com/company/tests/
│   │   ├── base/
│   │   │   ├── BaseTest.java         # thread-safe lifecycle (templates/BaseTest.java)
│   │   │   └── BasePage.java         # shared page helpers   (templates/BasePage.java)
│   │   ├── config/
│   │   │   └── ConfigReader.java     # single source of env/config truth
│   │   ├── model/
│   │   │   └── User.java             # immutable, self-validating test data
│   │   ├── pages/
│   │   │   ├── LoginPage.java
│   │   │   ├── DashboardPage.java
│   │   │   ├── OrdersPage.java
│   │   │   ├── ProductsPage.java
│   │   │   └── CheckoutPage.java
│   │   ├── tests/
│   │   │   └── LoginTest.java
│   │   └── utils/
│   │       ├── TestDataFactory.java
│   │       └── WaitUtils.java
│   └── resources/
│       ├── test.properties           # baseUrl, browser, timeouts (overridable by -D)
│       ├── junit-platform.properties # parallel execution knobs
│       └── testdata/users.json
└── pom.xml
```

**Why this shape:** `base/` owns the driver lifecycle, `pages/` owns selectors and actions, `tests/` owns assertions, and `config/`, `model/`, and `utils/` stay completely free of Playwright wiring. Because selectors never leak into test classes, a markup change is a one-file edit in `pages/`, not a find-and-replace across `tests/`.

1. Create the directory structure above.
2. Copy `templates/BaseTest.java` and `templates/BasePage.java` into `base/`.
3. Load `config.md` for the complete `pom.xml` with Playwright, JUnit 5, Allure, and AspectJ weaver dependencies.
4. Create `src/test/resources/test.properties` with `baseUrl`, `browser`, `headless`, and `defaultTimeout` entries.
5. Create `src/test/resources/junit-platform.properties` with parallel execution settings.

### Step 3: Set Up Thread-Safe BaseTest

A `Page` is single-threaded. JUnit runs parallel tests on a *shared* thread pool, so the only safe model is "one full `Playwright → Browser → BrowserContext → Page` stack per thread," held in `ThreadLocal`.

**Two critical details naive examples omit:**
1. Every resource must be closed even if a sibling close throws — use `closeQuietly()`.
2. Every `ThreadLocal` must be `remove()`d — otherwise a pooled thread hands the *next* test a closed `Page` and the OS slowly fills with orphaned browser processes.

```java
package com.company.tests.base;

import com.company.tests.config.ConfigReader;
import com.microsoft.playwright.*;
import io.qameta.allure.Allure;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.TestInfo;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Objects;

public abstract class BaseTest {

    private static final ThreadLocal<Playwright>     PLAYWRIGHT = new ThreadLocal<>();
    private static final ThreadLocal<Browser>        BROWSER    = new ThreadLocal<>();
    private static final ThreadLocal<BrowserContext> CONTEXT    = new ThreadLocal<>();
    private static final ThreadLocal<Page>           PAGE       = new ThreadLocal<>();

    protected Page page() {
        return Objects.requireNonNull(
            PAGE.get(), "Page is null — setUp() did not run or failed on this thread");
    }

    @BeforeEach
    void setUp() throws IOException {
        Files.createDirectories(Paths.get("target/traces"));
        Files.createDirectories(Paths.get("target/videos"));

        Playwright playwright = Playwright.create();
        PLAYWRIGHT.set(playwright);

        BrowserType.LaunchOptions launchOptions = new BrowserType.LaunchOptions()
            .setHeadless(ConfigReader.isHeadless())
            .setSlowMo(resolveSlowMo());

        Browser browser = resolveBrowser(playwright).launch(launchOptions);
        BROWSER.set(browser);

        BrowserContext context = browser.newContext(new Browser.NewContextOptions()
            .setViewportSize(1920, 1080)
            .setLocale("en-US")
            .setRecordVideoDir(Paths.get("target/videos")));
        context.setDefaultTimeout(ConfigReader.getDefaultTimeout());
        context.setDefaultNavigationTimeout(60_000);
        context.tracing().start(new Tracing.StartOptions()
            .setScreenshots(true)
            .setSnapshots(true)
            .setSources(true));
        CONTEXT.set(context);

        PAGE.set(context.newPage());
    }

    @AfterEach
    void tearDown(TestInfo testInfo) {
        attachScreenshot();
        stopTracing(testInfo);

        closeQuietly(PAGE.get());
        closeQuietly(CONTEXT.get());
        closeQuietly(BROWSER.get());
        closeQuietly(PLAYWRIGHT.get());

        PAGE.remove();
        CONTEXT.remove();
        BROWSER.remove();
        PLAYWRIGHT.remove();
    }

    private static int resolveSlowMo() {
        String raw = System.getProperty("slowMo", "0").trim();
        try {
            int slowMo = Integer.parseInt(raw);
            if (slowMo < 0) throw new NumberFormatException("must be non-negative");
            return slowMo;
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(
                "slowMo must be a non-negative integer, got: '" + raw + "'", e);
        }
    }

    private static BrowserType resolveBrowser(Playwright playwright) {
        Objects.requireNonNull(playwright, "playwright must not be null");
        String name = System.getProperty("browser", "chromium").trim().toLowerCase();
        return switch (name) {
            case "chromium", "chrome" -> playwright.chromium();
            case "firefox"            -> playwright.firefox();
            case "webkit", "safari"   -> playwright.webkit();
            default -> throw new IllegalArgumentException(
                "Unsupported browser '" + name + "'. Use chromium, firefox, or webkit.");
        };
    }

    private void attachScreenshot() {
        Page page = PAGE.get();
        if (page == null) return;
        try {
            byte[] png = page.screenshot(new Page.ScreenshotOptions().setFullPage(true));
            Allure.addAttachment(
                "Final Screenshot", "image/png", new ByteArrayInputStream(png), "png");
        } catch (PlaywrightException e) { /* non-fatal */ }
    }

    private void stopTracing(TestInfo testInfo) {
        BrowserContext context = CONTEXT.get();
        if (context == null) return;
        try {
            Path tracePath = Paths.get("target/traces", safeFileName(testInfo) + ".zip");
            context.tracing().stop(new Tracing.StopOptions().setPath(tracePath));
        } catch (PlaywrightException e) { /* non-fatal */ }
    }

    private static String safeFileName(TestInfo testInfo) {
        String name = testInfo.getDisplayName().replaceAll("[^a-zA-Z0-9._-]", "_");
        return name.length() > 80 ? name.substring(0, 80) : name;
    }

    private static void closeQuietly(AutoCloseable closeable) {
        if (closeable == null) return;
        try { closeable.close(); }
        catch (Exception e) { /* best-effort */ }
    }
}
```

### Step 4: Build the Model and Page Object Classes

**Test data should be impossible to construct in an invalid state.** A `record` with a validating compact constructor means a blank email fails at creation — at the factory, with a clear message — instead of surfacing 200 lines later as a confusing "element not found".

```java
package com.company.tests.model;

import java.util.Objects;

public record User(String email, String password, String firstName, String lastName, String role) {
    public User {
        Objects.requireNonNull(email, "email must not be null");
        Objects.requireNonNull(password, "password must not be null");
        Objects.requireNonNull(firstName, "firstName must not be null");
        Objects.requireNonNull(lastName, "lastName must not be null");
        Objects.requireNonNull(role, "role must not be null");
        if (email.isBlank())    throw new IllegalArgumentException("email must not be blank");
        if (password.isBlank()) throw new IllegalArgumentException("password must not be blank");
    }
}
```

**Page Object rules:**
- Declare every `Locator` as a `final` field set in the constructor. Locators are lazy (resolved at action time, not creation), so building them once keeps pages readable and prevents selector drift.
- Navigation methods **return the next Page Object**, encoding legal screen transitions in the type system: an illegal flow fails to compile.
- **HARD RULE:** Never instantiate `Playwright` inside a Page Object. Page Objects model pages; owning the driver lifecycle there breaks parallelism and leaks browsers.

```java
package com.company.tests.pages;

import com.company.tests.base.BasePage;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.WaitForSelectorState;

import java.util.Objects;
import java.util.regex.Pattern;

public final class LoginPage extends BasePage {

    private final Locator emailInput;
    private final Locator passwordInput;
    private final Locator loginButton;
    private final Locator errorMessage;

    public LoginPage(Page page) {
        super(Objects.requireNonNull(page, "page must not be null"));
        this.emailInput    = page.getByLabel("Email address");
        this.passwordInput = page.getByLabel("Password");
        this.loginButton   = page.getByRole(AriaRole.BUTTON,
                                 new Page.GetByRoleOptions().setName("Sign in"));
        this.errorMessage  = page.getByTestId("login-error");
    }

    @Override
    protected String getUrl() { return "/login"; }

    public DashboardPage loginAs(String email, String password) {
        submitCredentials(email, password);
        page.waitForURL(Pattern.compile(".*/dashboard"),
            new Page.WaitForURLOptions().setTimeout(15_000));
        return new DashboardPage(page);
    }

    public LoginPage loginExpectingError(String email, String password) {
        submitCredentials(email, password);
        errorMessage.waitFor(new Locator.WaitForOptions()
            .setState(WaitForSelectorState.VISIBLE)
            .setTimeout(10_000));
        return this;
    }

    public Locator errorBanner() { return errorMessage; }

    public String errorText() {
        errorMessage.waitFor(new Locator.WaitForOptions()
            .setState(WaitForSelectorState.VISIBLE)
            .setTimeout(10_000));
        return Objects.requireNonNullElse(errorMessage.textContent(), "").trim();
    }

    private void submitCredentials(String email, String password) {
        Objects.requireNonNull(email, "email must not be null");
        Objects.requireNonNull(password, "password must not be null");
        fill(emailInput, email);
        fill(passwordInput, password);
        click(loginButton);
    }
}
```

```java
package com.company.tests.pages;

import com.company.tests.base.BasePage;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import java.util.Objects;

public final class DashboardPage extends BasePage {
    private final Locator welcomeBanner;

    public DashboardPage(Page page) {
        super(Objects.requireNonNull(page, "page must not be null"));
        this.welcomeBanner = page.getByTestId("welcome-banner");
    }

    @Override
    protected String getUrl() { return "/dashboard"; }

    public Locator getWelcomeBanner() { return welcomeBanner; }
}
```

### Step 5: Write Tests with Allure Annotations

**Two assertion styles — choose deliberately:**

- **Web-first** `assertThat(locator)` (from `PlaywrightAssertions`) re-queries the DOM and retries until the timeout. Use it whenever you assert on live page state — it eliminates the race that `Thread.sleep()` tries to dodge.
- **`SoftAssertions`** (AssertJ) collects *all* failures before stopping, but it does **not** retry. Apply it only to plain values you have *already read* from the page; never wrap a live `Page`/`Locator` in it, or you lose auto-retry and get false flake.

```java
package com.company.tests.tests;

import com.company.tests.base.BaseTest;
import com.company.tests.model.User;
import com.company.tests.pages.DashboardPage;
import com.company.tests.pages.LoginPage;
import com.company.tests.utils.TestDataFactory;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import io.qameta.allure.Severity;
import io.qameta.allure.SeverityLevel;
import io.qameta.allure.junit5.AllureJunit5;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.assertj.core.api.SoftAssertions.assertSoftly;

@Epic("Authentication")
@Feature("Login")
@ExtendWith(AllureJunit5.class)
class LoginTest extends BaseTest {

    @Test
    @DisplayName("Valid user can log in and sees the dashboard welcome banner")
    @Severity(SeverityLevel.CRITICAL)
    void validUserCanLogin() {
        User user = TestDataFactory.validUser();

        LoginPage loginPage = new LoginPage(page());
        loginPage.navigate();

        DashboardPage dashboard = loginPage.loginAs(user.email(), user.password());

        // Web-first assertion: auto-retries until the banner is visible.
        assertThat(dashboard.getWelcomeBanner()).isVisible();
        assertThat(dashboard.getWelcomeBanner()).hasText("Welcome, " + user.firstName());
    }

    @Test
    @DisplayName("Invalid credentials show an error message")
    @Severity(SeverityLevel.NORMAL)
    void invalidCredentialsShowError() {
        LoginPage loginPage = new LoginPage(page());
        loginPage.navigate();

        loginPage.loginExpectingError("invalid@example.com", "wrong-password");

        // Expose Locator for web-first assertion — never read text into a String first.
        assertThat(loginPage.errorBanner()).isVisible();
        assertThat(loginPage.errorBanner()).containsText("Invalid");
    }
}
```

### Step 6: Configure Parallel Execution

Create `src/test/resources/junit-platform.properties`:

```properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=concurrent
junit.jupiter.execution.parallel.mode.classes.default=concurrent
junit.jupiter.execution.parallel.config.strategy=dynamic
junit.jupiter.execution.parallel.config.dynamic.factor=1.0
```

**HARD RULE:** Parallel execution is only safe with the `ThreadLocal` stack from Step 3. Never share a `Page` across threads.

### Step 7: Configure Allure Reporting

Load `config.md` for the exact `pom.xml` snippet. The critical piece is the AspectJ weaver agent in `maven-surefire-plugin`:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <argLine>
            -javaagent:"${settings.localRepository}/org/aspectj/aspectjweaver/1.9.22/aspectjweaver-1.9.22.jar"
        </argLine>
    </configuration>
</plugin>
```

**HARD RULE:** Without the AspectJ weaver agent in `<argLine>`, `@Step` annotations are never woven and the Allure report will be blank or missing steps.

### Step 8: Install Browsers and Run

```powershell
# Install Playwright browsers with system dependencies (Windows PowerShell)
mvn exec:java -e "-Dexec.mainClass=com.microsoft.playwright.CLI" "-Dexec.args=install --with-deps"

# Run all tests
mvn test

# Run a single test class
mvn test "-Dtest=LoginTest"

# Run with a specific browser
mvn test "-Dtest=LoginTest" "-Dbrowser=firefox"

# Run headed with slow motion for debugging
mvn test "-Dtest=LoginTest" "-Dheadless=false" "-DslowMo=500"

# Generate and serve Allure report
allure serve target/allure-results
```

### Step 9: CI/CD Setup

For CI pipelines (GitHub Actions, Jenkins, Docker):

1. Run `playwright install --with-deps` in the pipeline — CI images lack the OS libraries browsers link against.
2. Ensure `target/traces/`, `target/videos/`, and `target/allure-results/` are uploaded as artifacts on failure.
3. Use `--with-deps` only on Linux CI; on Windows/macOS CI, omit `--with-deps`.
4. Load `config.md` for complete Docker and CI YAML examples.

### Step 10: Auth State Reuse (storageState)

To skip UI login on every test:

1. Create an `AuthSetup` class that logs in once and saves `storageState` to `target/auth/user-state.json`.
2. In `BaseTest`, load the saved state when creating `BrowserContext`:

```java
BrowserContext context = browser.newContext(new Browser.NewContextOptions()
    .setStorageStatePath(Paths.get("target/auth/user-state.json")));
```

3. **HARD RULE:** If `storageState` is stale, tests redirect to login. Regenerate by re-running `AuthSetup` before the suite, or add a `@BeforeAll` that refreshes it when missing or expired. Load `fixtures.md` for the full auth state pattern.

---

## Pitfalls

- **Tests fail randomly in parallel mode.**
  *Fix:* Ensure every test builds its own `Playwright → Browser → BrowserContext → Page` chain via `ThreadLocal` and calls `.remove()` in `@AfterEach`. Never share a `Page` across threads — that is the root cause of "works alone, flakes in the suite".

- **`assertThat(locator).isVisible()` times out even though the element appears.**
  *Fix:* The default timeout is too low for this page. Raise it per assertion with `.setTimeout(10_000)`, or globally via `context.setDefaultTimeout()` in `BaseTest`.

- **`Thread.sleep(2000)` was added but tests are still flaky.**
  *Fix:* **HARD RULE: Never call `Thread.sleep()`.** Replace it with a condition-based wait — `page.waitForResponse("**/api/endpoint", () -> action())` or a web-first `assertThat(locator).hasText("Done")` — which polls until the state is actually reached.

- **The Playwright trace zip is empty or missing.**
  *Fix:* Confirm `tracing().start()` runs in `@BeforeEach` (before test actions) and `tracing().stop()` is in `@AfterEach` (per-test), not `@AfterAll`. A trace stopped after all tests captures nothing useful for an individual failure.

- **The Allure report is blank or missing steps.**
  *Fix:* Add the AspectJ weaver agent to the `maven-surefire-plugin` `<argLine>` in `pom.xml` — without it, `@Step` annotations are never woven. See `config.md` for the exact snippet.

- **The `storageState` auth file is stale and tests redirect to login.**
  *Fix:* Regenerate `target/auth/user-state.json` by re-running `AuthSetup` before the suite, or add a `@BeforeAll` that refreshes it when it is missing or older than the session lifetime.

- **Headless-mode flake that doesn't reproduce headed.**
  *Fix:* **HARD RULE:** Do not just set `headless=true` and move on. The default `chrome-headless-shell` renders with subtle layout differences from real Chrome; pin the channel to `chromium` (or the full `chrome` channel) so headless and headed runs agree.

- **XPath used where semantic locators exist.**
  *Fix:* **HARD RULE:** Do not use XPath for elements that expose `getByRole`/`getByLabel`/`getByTestId` handles. Semantic locators document intent and survive DOM restructuring, while XPath couples the test to incidental structure.

- **Missing inputs, credentials, or target environment.**
  *Fix:* **HARD RULE:** Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing. A confidently wrong assumption about the base URL, credentials, or target environment can point a destructive test at the wrong system.

---

## Verification

1. **Check `pom.xml` version floor:**
   ```powershell
   Select-String -Path pom.xml -Pattern "playwright.version" | ForEach-Object { $_.Line }
   ```
   Confirm `playwright.version` is `>= 1.49.0` (required for `ariaSnapshot()`; `1.44+` suffices otherwise).

2. **Run a sample test alone and in parallel:**
   ```powershell
   mvn test "-Dtest=LoginTest"
   mvn test
   ```
   Both must pass. If the single test passes but the suite flakes, the `ThreadLocal` stack is not correctly isolated.

3. **Verify trace artifacts exist:**
   ```powershell
   Get-ChildItem target/traces/*.zip | Measure-Object
   ```
   There should be one non-empty `.zip` per test run.

4. **Verify HAR files (if using HAR recording):**
   ```powershell
   Get-ChildItem target/har/*.har | ForEach-Object { "$($_.Name): $($_.Length) bytes" }
   ```
   Files must exist and be non-empty.

5. **Verify Allure report renders with steps:**
   ```powershell
   allure serve target/allure-results
   ```
   Confirm the report displays steps, screenshots, and video recordings. If steps are missing, the AspectJ agent is not wired up — recheck `maven-surefire-plugin` `<argLine>`.

6. **Verify no orphaned browser processes after teardown:**
   ```powershell
   Get-Process -Name "chrome","chromium","firefox" -ErrorAction SilentlyContinue | Measure-Object
   ```
   Count should be zero after the suite completes (indicates `ThreadLocal.remove()` and `closeQuietly()` are working).

---

## Related Skills

- `rest-assured-java` — Use for pure API test suites with no UI interaction.
- `selenium-java` — Legacy alternative; prefer Playwright for all new projects (auto-waiting, tracing, and a simpler parallel model).
- `allure-reporting` — Deep dive into Allure annotations, categories, and history trends.
- `testcontainers-java` — Use alongside this skill when tests need a live database or service.
- `github-actions-ci` — For building complete multi-browser matrix CI pipelines.
