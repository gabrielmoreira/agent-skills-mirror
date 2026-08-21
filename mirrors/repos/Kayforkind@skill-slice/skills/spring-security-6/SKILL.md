---
name: spring-security-6
version: 1.1.1
description: "Migrates Spring Security 5 on Boot 2 to Spring Security 6 on Boot 3: drop WebSecurityConfigurerAdapter, switch to EnableMethodSecurity, requestMatchers, lambda DSL, and javax-to-jakarta servlet. Use when converting an existing SS5 configuration. Not for greenfield Security 6 apps, versions before 5, or remaining on Boot 2/javax."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

Spring Security 6 (shipped with Spring Boot 3.x) is not a cosmetic rename. Three forces drive the migration, and knowing them lets you make good judgment calls when a mechanical rule does not fit your code:

1. **Jakarta EE namespace move.** When stewardship of Java EE passed from Oracle to the Eclipse Foundation, Oracle kept the `javax` trademark. The enterprise APIs were relocated from `javax.*` to `jakarta.*`. Spring Boot 3 baselines on Jakarta EE 9+, so every servlet, validation, and persistence import must move. There is no compatibility shim.
2. **From inheritance to composition.** The old `WebSecurityConfigurerAdapter` forced all security configuration into a single class hierarchy. The 6.x model publishes ordinary beans (`SecurityFilterChain`, `UserDetailsService`, `AuthenticationManager`), which you can define more than once, order explicitly, and test in isolation.
3. **From a builder chain to scoped lambdas.** The chained `.and()` DSL made it ambiguous which configurer a call applied to. Lambda DSL scopes each block to exactly one configurer, so the configuration reads top-to-bottom without hidden state. The `.and()` methods were removed in the 6.1 line, so this is required, not stylistic.

## When to Use

Use this skill when migrating a Java project from Spring Security 5 (Spring Boot 2.x) to Spring Security 6 (Spring Boot 3.x). Specifically use this when:

- Removing the deprecated `WebSecurityConfigurerAdapter`.
- Replacing `@EnableGlobalMethodSecurity` with `@EnableMethodSecurity`.
- Converting `antMatchers`, `mvcMatchers`, or `regexMatchers` to `requestMatchers`.
- Updating security configuration to the lambda DSL style.
- Updating servlet imports from `javax.servlet` to `jakarta.servlet`.
- Refactoring `AuthenticationManager` bean creation.
- Tightening configuration against current security defaults (stricter CSRF handling, explicit header policies, and updated OAuth2/OIDC flows).

**Do NOT use this skill when:**

- Setting up a brand-new Spring Security 6 project. Greenfield projects never had the legacy `WebSecurityConfigurerAdapter` or `.and()` chains — start from the current reference documentation instead.
- Migrating Spring Security versions prior to 5.0. The component-based model and lambda DSL assume configurer APIs that only stabilized in the 5.x line.
- You are not also upgrading to Spring Boot 3.x. The migration forces the `javax.*` → `jakarta.*` namespace change, and Spring Boot 2.x runs on the `javax` servlet API. Mixing the two namespaces produces `NoClassDefFoundError`/`ClassNotFoundException` at runtime because they are genuinely different types, not aliases.
- Do not reintroduce `antMatchers`, `mvcMatchers`, or `regexMatchers` in new code. They were removed (not merely deprecated) in Spring Security 6, so any new usage will fail to compile against the 6.x API.

## Prerequisites

- The project must already be on Spring Boot 3.x (or be upgrading to it simultaneously). Spring Security 6 requires the Jakarta EE 9+ namespace.
- A clean working tree in version control so every migration change is reviewable in a diff.
- Java 17 or higher (Spring Boot 3 minimum).
- For the OpenRewrite recipe path: Maven or Gradle build tooling must be functional.

## Procedure

### Step 1 — Remove WebSecurityConfigurerAdapter

Move from class extension to bean configuration: delete `extends WebSecurityConfigurerAdapter` and replace the overridden `configure(HttpSecurity http)` method with a `@Bean` method that returns a built `SecurityFilterChain`.

**Why:** The adapter is gone in 6.0. Returning a `SecurityFilterChain` bean lets the container own the lifecycle and lets you register multiple chains (for example one `@Order(1)` chain for `/api/**` and a default chain for the web UI) — something the single-adapter model made awkward. Because the chain is just a bean, it is also far easier to slice-test with `@WebMvcTest`.

**Key change:** Add `@Configuration` explicitly to the class. `@EnableWebSecurity` no longer implies `@Configuration` in Spring Security 6, so without it your `@Bean` methods are never processed and security silently falls back to defaults.

### Step 2 — Update method security

Replace `@EnableGlobalMethodSecurity` with `@EnableMethodSecurity`, and update the import:

```java
// BEFORE
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
@EnableGlobalMethodSecurity(prePostEnabled = true)

// AFTER  (prePostEnabled defaults to true and may be omitted)
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
@EnableMethodSecurity
```

**Why:** `@EnableGlobalMethodSecurity` sits on the legacy `AccessDecisionManager`/`AccessDecisionVoter` stack. `@EnableMethodSecurity` sits on the simplified `AuthorizationManager` API (introduced in 5.6), which supports meta-annotations and is easier to customize. It also enables `@PreAuthorize`/`@PostAuthorize` by default — `prePostEnabled` defaults to `true`, so the attribute is now optional.

**Important:** If you previously relied on `@Secured` or JSR-250 (`@RolesAllowed`), enable them explicitly with `securedEnabled = true` / `jsr250Enabled = true`; they are off by default under `@EnableMethodSecurity`.

### Step 3 — Convert to lambda DSL configuration

Convert chained methods and `.and()` calls to lambda-based configuration:

```java
// BEFORE
http
    .csrf().disable()
    .sessionManagement()
        .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
    .and()
    .authorizeRequests()
        .antMatchers("/api/public/**").permitAll()
        .anyRequest().authenticated();

// AFTER
http
    .csrf(csrf -> csrf.disable())
    .sessionManagement(session ->
        session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/api/public/**").permitAll()
        .anyRequest().authenticated()
    );
```

**Why:** Each lambda receives the specific configurer it configures, so the scope is explicit and there is no `.and()` back-navigation to reason about. The non-lambda overloads and `.and()` were removed in 6.1, so the lambda form is required to compile against current versions.

**Critical:** `.and()` cannot be text-replaced away with `sed`. It encodes structure, so removing it requires re-nesting calls into the correct lambdas — do this by hand or with OpenRewrite, not `sed`.

### Step 4 — Unify URL matching

Replace `antMatchers()`, `mvcMatchers()`, and `regexMatchers()` with `requestMatchers()`. Also rename the `authorizeRequests` entry point to `authorizeHttpRequests`.

```java
// BEFORE
.authorizeRequests()
    .antMatchers("/api/**").authenticated()
    .anyRequest().permitAll();

// AFTER
.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/**").authenticated()
    .anyRequest().permitAll()
);
```

**Why:** Maintaining three matcher methods was a recurring source of security bugs — the classic one being `antMatchers("/admin")` that failed to also cover `/admin/` or `/admin.html`, leaving a path unprotected. `requestMatchers()` is the single entry point and, when Spring MVC is on the classpath, applies `MvcRequestMatcher` semantics that match how the dispatcher actually resolves paths, closing that gap.

### Step 5 — Update exception handling and headers

Convert `.exceptionHandling()` and `.headers()` to their lambda equivalents, and take the opportunity to harden them:

```java
.exceptionHandling(ex -> ex
    .authenticationEntryPoint(authenticationEntryPoint))
.headers(headers -> headers
    .frameOptions(frame -> frame.sameOrigin())
    .contentSecurityPolicy(csp ->
        csp.policyDirectives("default-src 'self'; frame-ancestors 'self'")))
```

**Why:** Beyond the required lambda conversion, the defaults deserve a second look. An `authenticationEntryPoint` that echoes the raw exception message can disclose whether a username exists; disabling frame options entirely re-opens clickjacking. The lambda form is where you set safe, explicit policies.

### Step 6 — Update the servlet namespace

Change every `javax.servlet` import to `jakarta.servlet` (and likewise `javax.validation` → `jakarta.validation`, `javax.persistence` → `jakarta.persistence`).

```java
// BEFORE
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

// AFTER
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
```

**Why:** Spring Boot 3 ships the Jakarta servlet API. `javax.servlet.http.HttpServletResponse` and `jakarta.servlet.http.HttpServletResponse` are distinct, unrelated types — there is no bridge — so any remaining `javax` import fails to compile or, worse, fails at runtime if pulled in transitively.

### Step 7 — Refactor AuthenticationManager

Instead of overriding `authenticationManagerBean()`, inject `AuthenticationConfiguration` into a `@Bean` method and return `authConfig.getAuthenticationManager()`.

```java
// BEFORE (override on the adapter)
@Bean
@Override
public AuthenticationManager authenticationManagerBean() throws Exception {
    return super.authenticationManagerBean();
}

// AFTER (ask the AuthenticationConfiguration for the manager Spring built)
@Bean
public AuthenticationManager authenticationManager(
        AuthenticationConfiguration authConfig) throws Exception {
    Assert.notNull(authConfig, "AuthenticationConfiguration must not be null");
    return authConfig.getAuthenticationManager();
}
```

**Why:** `authenticationManagerBean()` was a hook on the adapter; with the adapter gone there is nothing to override. `AuthenticationConfiguration` hands you the `AuthenticationManager` that Spring assembles from your `UserDetailsService`/`AuthenticationProvider` beans. Many applications no longer need to expose it at all — only do so when something (such as a custom login filter) injects it directly.

**Note:** A single `UserDetailsService` bean is auto-detected and wired into the `AuthenticationManager` automatically, so the old `AuthenticationManagerBuilder` configuration is usually redundant and can be deleted.

## Examples

### Minimal migration — Before (Spring Security 5 / Spring Boot 2)

```java
package com.example.security.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Autowired
    private UserDetailsService userDetailsService;

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.userDetailsService(userDetailsService)
            .passwordEncoder(passwordEncoder());
    }

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeRequests()
                .antMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated();
    }

    @Bean
    @Override
    public AuthenticationManager authenticationManagerBean() throws Exception {
        return super.authenticationManagerBean();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### Minimal migration — After (Spring Security 6 / Spring Boot 3)

```java
package com.example.security.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.util.Assert;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        Assert.notNull(http, "HttpSecurity must not be null");
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }

    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration authConfig) throws Exception {
        Assert.notNull(authConfig, "AuthenticationConfiguration must not be null");
        return authConfig.getAuthenticationManager();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public UserDetailsService userDetailsService(PasswordEncoder passwordEncoder) {
        Assert.notNull(passwordEncoder, "PasswordEncoder must not be null");
        UserDetails serviceAccount = User.withUsername("service")
            .password(passwordEncoder.encode("replace-with-an-injected-secret"))
            .roles("SERVICE")
            .build();
        return new InMemoryUserDetailsManager(serviceAccount);
    }
}
```

### Hardened SecurityFilterChain with custom entry point, headers, and filter

```java
package com.example.security.config;

import com.example.security.web.CorrelationIdFilter;
import com.example.security.web.RestAuthenticationEntryPoint;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.util.Assert;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class ApiSecurityConfig {

    private final RestAuthenticationEntryPoint authenticationEntryPoint;
    private final CorrelationIdFilter correlationIdFilter;

    public ApiSecurityConfig(RestAuthenticationEntryPoint authenticationEntryPoint,
                             CorrelationIdFilter correlationIdFilter) {
        Assert.notNull(authenticationEntryPoint, "RestAuthenticationEntryPoint must not be null");
        Assert.notNull(correlationIdFilter, "CorrelationIdFilter must not be null");
        this.authenticationEntryPoint = authenticationEntryPoint;
        this.correlationIdFilter = correlationIdFilter;
    }

    @Bean
    public SecurityFilterChain apiSecurityFilterChain(HttpSecurity http) throws Exception {
        Assert.notNull(http, "HttpSecurity must not be null");
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(authenticationEntryPoint))
            .headers(headers -> headers
                .frameOptions(frame -> frame.sameOrigin())
                .contentSecurityPolicy(csp ->
                    csp.policyDirectives("default-src 'self'; frame-ancestors 'self'")))
            .addFilterBefore(correlationIdFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }
}
```

### Safe RestAuthenticationEntryPoint

Returns a stable, non-revealing JSON body and logs the real reason server-side. Uses constructor injection, validates its dependency, and writes a fully typed response body.

```java
package com.example.security.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;
import org.springframework.util.Assert;

import java.io.IOException;
import java.time.Instant;
import java.util.Map;

@Component
public class RestAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private static final Logger log = LoggerFactory.getLogger(RestAuthenticationEntryPoint.class);

    private final ObjectMapper objectMapper;

    public RestAuthenticationEntryPoint(ObjectMapper objectMapper) {
        Assert.notNull(objectMapper, "ObjectMapper must not be null");
        this.objectMapper = objectMapper;
    }

    @Override
    public void commence(HttpServletRequest request,
                         HttpServletResponse response,
                         AuthenticationException authException) throws IOException {
        log.warn("Unauthorized request to {}: {}",
            request.getRequestURI(), authException.getMessage());

        response.setStatus(HttpStatus.UNAUTHORIZED.value());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);

        Map<String, Object> body = Map.of(
            "timestamp", Instant.now().toString(),
            "status", HttpStatus.UNAUTHORIZED.value(),
            "error", "Unauthorized",
            "message", "Authentication required",
            "path", request.getRequestURI()
        );

        response.getWriter().write(objectMapper.writeValueAsString(body));
    }
}
```

### CorrelationIdFilter (jakarta.servlet)

Demonstrates the `javax.servlet` → `jakarta.servlet` move. Cleans up thread-bound `MDC` state in a `finally` block so a pooled request thread never leaks a stale correlation id.

```java
package com.example.security.web;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

@Component
public class CorrelationIdFilter extends OncePerRequestFilter {

    private static final String HEADER = "X-Correlation-Id";
    private static final String MDC_KEY = "correlationId";

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request,
                                    @NonNull HttpServletResponse response,
                                    @NonNull FilterChain filterChain)
            throws ServletException, IOException {

        String correlationId = request.getHeader(HEADER);
        if (!StringUtils.hasText(correlationId)) {
            correlationId = UUID.randomUUID().toString();
        }

        MDC.put(MDC_KEY, correlationId);
        response.setHeader(HEADER, correlationId);
        try {
            filterChain.doFilter(request, response);
        } finally {
            MDC.remove(MDC_KEY);
        }
    }
}
```

## Pitfalls

1. **`@Configuration` is no longer implied by `@EnableWebSecurity`.** Add `@Configuration` explicitly, otherwise your `SecurityFilterChain` `@Bean` methods are never processed and security silently falls back to defaults.
2. **`.and()` cannot be text-replaced away.** It encodes structure, so removing it requires re-nesting calls into the correct lambdas — do this by hand or with OpenRewrite, not `sed`.
3. **Use `AuthenticationConfiguration`, not `authenticationManagerBean()`.** The override no longer exists; injecting `AuthenticationConfiguration` returns the manager Spring already assembled from your beans.
4. **`UserDetailsService` is auto-detected.** A single `UserDetailsService` bean is wired into the `AuthenticationManager` automatically, so the old `AuthenticationManagerBuilder` configuration is usually redundant and can be deleted.
5. **`@EnableMethodSecurity` enables `@PreAuthorize`/`@PostAuthorize` by default.** If you previously relied on `@Secured` or JSR-250 (`@RolesAllowed`), enable them explicitly with `securedEnabled = true` / `jsr250Enabled = true`; they are off by default.
6. **CSRF is enabled by default.** That is correct for browser/session flows. For a stateless token API you must disable it *deliberately* (as shown) or supply a `CookieCsrfTokenRepository` — but do not blindly copy `csrf.disable()` into a cookie-session app, because that re-opens CSRF.
7. **`antMatchers`, `mvcMatchers`, and `regexMatchers` were removed, not deprecated.** Any new usage will fail to compile against the 6.x API. Never reintroduce them.
8. **`javax` and `jakarta` are distinct, unrelated types.** There is no bridge. Any remaining `javax` import fails to compile or fails at runtime if pulled in transitively.
9. **Searching for `.and()` is noisy.** A bare `grep -rn "\.and()"` matches `java.util.function.Predicate`, Stream/Collector composition, QueryDSL, and Mockito. Scope the search to your security package and review matches by hand.

## Verification

### Mechanical first pass with sed (renames only)

These `sed` replacements handle the *renames* only. They cannot perform the structural lambda conversion (wrapping each configurer in a lambda such as `csrf -> csrf.disable()`, removing `.and()`, and building the `SecurityFilterChain` with `http.build()`), because that requires understanding Java syntax, not just text. Run them as a starting point, then convert the DSL by hand.

> **Portability note:** These use GNU `sed -i` (no backup suffix). On BSD/macOS `sed`, use `sed -i ''`. Always run them on a clean working tree so the diff is reviewable, and never on generated or vendored sources.

**Bash / WSL:**
```bash
# Replace the annotation, then its import line.
find . -name "*.java" -type f -exec sed -i 's/@EnableGlobalMethodSecurity/@EnableMethodSecurity/g' {} +
find . -name "*.java" -type f -exec sed -i 's/EnableGlobalMethodSecurity/EnableMethodSecurity/g' {} +

# Unify the matcher methods.
find . -name "*.java" -type f -exec sed -i 's/\.antMatchers(/.requestMatchers(/g' {} +
find . -name "*.java" -type f -exec sed -i 's/\.mvcMatchers(/.requestMatchers(/g' {} +
find . -name "*.java" -type f -exec sed -i 's/\.regexMatchers(/.requestMatchers(/g' {} +

# Rename the authorize entry point.
find . -name "*.java" -type f -exec sed -i 's/\.authorizeRequests(/.authorizeHttpRequests(/g' {} +

# Move the servlet (and related Jakarta) namespaces.
find . -name "*.java" -type f -exec sed -i 's/javax\.servlet/jakarta.servlet/g' {} +
find . -name "*.java" -type f -exec sed -i 's/javax\.validation/jakarta.validation/g' {} +
find . -name "*.java" -type f -exec sed -i 's/javax\.persistence/jakarta.persistence/g' {} +
```

**PowerShell (Windows host primary):**
```powershell
# Replace the annotation and its import.
Get-ChildItem -Recurse -Filter *.java | ForEach-Object {
    (Get-Content $_.FullName) -replace '@EnableGlobalMethodSecurity', '@EnableMethodSecurity' -replace 'EnableGlobalMethodSecurity', 'EnableMethodSecurity' | Set-Content $_.FullName
}

# Unify the matcher methods.
Get-ChildItem -Recurse -Filter *.java | ForEach-Object {
    (Get-Content $_.FullName) -replace '\.antMatchers\(', '.requestMatchers(' -replace '\.mvcMatchers\(', '.requestMatchers(' -replace '\.regexMatchers\(', '.requestMatchers(' | Set-Content $_.FullName
}

# Rename the authorize entry point.
Get-ChildItem -Recurse -Filter *.java | ForEach-Object {
    (Get-Content $_.FullName) -replace '\.authorizeRequests\(', '.authorizeHttpRequests(' | Set-Content $_.FullName
}

# Move the Jakarta namespaces.
Get-ChildItem -Recurse -Filter *.java | ForEach-Object {
    (Get-Content $_.FullName) -replace 'javax\.servlet', 'jakarta.servlet' -replace 'javax\.validation', 'jakarta.validation' -replace 'javax\.persistence', 'jakarta.persistence' | Set-Content $_.FullName
}
```

### Prefer OpenRewrite for anything non-trivial

The Spring team publishes an OpenRewrite recipe that performs this migration with real type awareness — including the lambda DSL conversion that `sed` cannot do. It is far safer on a large codebase:

```bash
# Maven
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.activeRecipes=org.openrewrite.java.spring.security6.UpgradeSpringSecurity_6_0 \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-spring:RELEASE
```

### Verification checklist

- [ ] The project compiles against the Spring Boot 3 / Spring Security 6 BOM.
- [ ] The test suite passes with no `ClassNotFoundException`/`NoClassDefFoundError` for `javax.servlet` (a remaining `javax` import is the usual cause).
- [ ] Each `SecurityFilterChain` bean returns `http.build()` and no class still `extends WebSecurityConfigurerAdapter`.
- [ ] Stateless API chains either disable CSRF deliberately *or* use a token repository; cookie/session chains keep CSRF enabled.

### Confirm no deprecated patterns remain

**Bash / WSL (these should return no results):**
```bash
grep -rn "WebSecurityConfigurerAdapter" --include="*.java" .
grep -rn "@EnableGlobalMethodSecurity" --include="*.java" .
grep -rn "\.antMatchers(" --include="*.java" .
grep -rn "\.mvcMatchers(" --include="*.java" .
grep -rn "\.regexMatchers(" --include="*.java" .
grep -rn "\.authorizeRequests(" --include="*.java" .
grep -rn "javax\.servlet" --include="*.java" .
```

**PowerShell (Windows host primary — these should return no results):**
```powershell
Select-String -Path "*.java" -Recurse -Pattern "WebSecurityConfigurerAdapter"
Select-String -Path "*.java" -Recurse -Pattern "@EnableGlobalMethodSecurity"
Select-String -Path "*.java" -Recurse -Pattern "\.antMatchers\("
Select-String -Path "*.java" -Recurse -Pattern "\.mvcMatchers\("
Select-String -Path "*.java" -Recurse -Pattern "\.regexMatchers\("
Select-String -Path "*.java" -Recurse -Pattern "\.authorizeRequests\("
Select-String -Path "*.java" -Recurse -Pattern "javax\.servlet"
```

### Confirm the new patterns are present

**Bash / WSL (these should return results):**
```bash
grep -rn "@EnableMethodSecurity" --include="*.java" .
grep -rn "SecurityFilterChain" --include="*.java" .
grep -rn "\.requestMatchers(" --include="*.java" .
grep -rn "\.authorizeHttpRequests(" --include="*.java" .
```

**PowerShell (Windows host primary — these should return results):**
```powershell
Select-String -Path "*.java" -Recurse -Pattern "@EnableMethodSecurity"
Select-String -Path "*.java" -Recurse -Pattern "SecurityFilterChain"
Select-String -Path "*.java" -Recurse -Pattern "\.requestMatchers\("
Select-String -Path "*.java" -Recurse -Pattern "\.authorizeHttpRequests\("
```

> **Caveat on searching for `.and()`:** a bare `grep -rn "\.and()"` is noisy because `.and()` is also used by `java.util.function.Predicate`, Stream/Collector composition, QueryDSL, and Mockito. Do not treat every hit as a security-config leftover. Scope the search to your security package, e.g. `grep -rn "\.and()" --include="*.java" src/main/java/com/example/security`, and review matches by hand. In PowerShell: `Select-String -Path "src\main\java\com\example\security\*.java" -Recurse -Pattern "\.and\(\)"`.

## Related skills

- `spring-boot-3-migration`
- `jakarta-ee-migration`
- `spring-data-jpa-migration`
