---
name: spring-boot-migration
version: 1.1.1
description: "Migrates Spring Boot 2.x to 3.x: Java 17/21, parent BOM, javax.* to jakarta.* (not JDK javax.crypto/sql), JAXB cleanup, jjwt 0.12, OpenRewrite. Use when upgrading a Boot 2.7 app to Boot 3. Not for Boot 1.x, Boot 3 to 4 (Jackson 3 / Framework 7), apps stuck on Java 8, or non-Spring Boot projects."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

A Spring Boot 2.x to 3.x upgrade is not a routine version bump. Spring Boot 3 sits on top of
Spring Framework 6, which made two changes that ripple through an entire codebase:

1. **The Java baseline moved to 17.** Spring Framework 6 compiles against and uses Java 17 APIs,
   so there is no supported way to run Spring Boot 3 on Java 8 or 11.
2. **The Java EE `javax.*` namespace became the Jakarta EE `jakarta.*` namespace.** Jakarta EE 9
   relocated every `javax.*` package used by servlets, persistence, validation, and XML binding to
   `jakarta.*`. The packages are otherwise compatible, but the rename is a hard, compile-breaking
   change with no shim.

Understanding those two facts explains almost every individual step below. Most of the work is
mechanical, but the order matters: bump the platform first, then fix the namespace, then remove the
old dependencies that only existed to paper over gaps the new platform fills natively, and finally
update the few libraries (most notably the JWT library) whose own APIs changed at the same time.

## When to Use

Use this skill when you are doing any of the following, because each one is a symptom of the
2.x → 3.x jump:

- **Migrating a Spring Boot application from 2.x to 3.x** — the umbrella task this skill exists for.
- **Updating `pom.xml` versions** — the parent BOM version is what pulls in the entire Spring Boot 3
  dependency set, so it is the single change that triggers everything else.
- **Removing deprecated JAXB dependencies** — these `javax.xml.bind` artifacts actively conflict
  with the Jakarta namespace and cause `ClassNotFoundException`/`NoClassDefFoundError` at runtime if
  left in place.
- **Upgrading Java to 17 or 21** — required by the platform; 21 is the current LTS and gives you
  virtual threads and the latest GC improvements, which is why it is the recommended target.
- **Using OpenRewrite for automated migration** — the AST-aware recipe handles the bulk of the
  `javax` → `jakarta` rename far more safely than hand-editing or find/replace.
- **Migrating jjwt from 0.9.x to 0.12.x** — the JWT library's own API changed in the same era and
  requires coordinated dependency + calling-code changes.

### Do not use

Skip this skill in the following situations:

- **Non-Spring Boot applications** — none of the BOM, namespace, or starter guidance applies.
- **Migrating from Spring Boot 1.x** — there is no supported direct 1.x → 3.x path. Migrate
  1.x → 2.x first, stabilize, then use this skill for 2.x → 3.x.
- **Applications that must keep Java 8 compatibility** — Spring Boot 3 cannot run on Java 8. If a
  hard Java 8 constraint exists, stay on Spring Boot 2.7.x, which is the last line that supports
  Java 8/11.
- **Applications that depend on libraries with no Jakarta-compatible release** — if a critical
  dependency still ships only `javax.*` classes and has no `jakarta.*` build, migrating will break
  it at runtime. Confirm every major dependency has a Jakarta-ready version before you start.
- **Applications relying on features removed or significantly changed in Spring Boot 3** — for
  example, code built around the old `WebSecurityConfigurerAdapter` or `RestTemplate`-centric
  patterns needs design changes, not just a version bump. Plan that work separately (see
  "Related skills").

## Prerequisites

- **Source project must be on Spring Boot 2.7.x (latest patch).** The Spring team's guidance is to
  first move to the latest 2.7 patch, fix all deprecation warnings there, and only then jump to 3.x.
  Deprecations you clear on 2.7 become hard removals on 3.x, so clearing them first turns runtime
  surprises into compile-time ones you have already handled.
- **JDK 17 or 21 installed locally and available in CI.** A mismatch between the `pom.xml`
  `java.version` and the actual runtime JDK produces `UnsupportedClassVersionError` at runtime
  rather than a clear build failure.
- **Clean working tree.** Commit or stash all work before starting. The OpenRewrite `rewrite:run`
  goal modifies source files in place; a clean tree makes the transformation fully reversible.
- **All major third-party dependencies confirmed to have Jakarta-compatible releases.** Check each
  dependency's latest version for `jakarta.*` namespace support before beginning.

## Procedure

Work through the steps in order. Each step states what to change and *why* the change is required,
so you can adapt it to a project that does not look exactly like the examples.

### Step 1 — Update the Spring Boot parent version

Changing the parent BOM version is what swaps the whole managed dependency set from the 2.x line to
the 3.x line. Do this first, because every later step assumes the 3.x dependency management is in
effect.

```xml
<!-- Before: Spring Boot 2.7.x (the last 2.x line; final stop before 3.x) -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
    <relativePath/>
</parent>

<!-- After: Spring Boot 3.2.x -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
    <relativePath/>
</parent>
```

### Step 2 — Raise the Java baseline to 17 (or 21)

Spring Boot 3 will not start on anything below Java 17 because Spring Framework 6 is compiled for it.
Java 21 is the current LTS and the recommended target; choose 17 only if your build or deployment
infrastructure cannot yet provide 21.

```xml
<properties>
    <!-- Before: Java 8, expressed in the legacy "1.8" form -->
    <java.version>1.8</java.version>

    <!-- After: Java 21 (LTS). Use 17 if 21 is not yet available in your toolchain. -->
    <java.version>21</java.version>
</properties>
```

After changing this, verify your local JDK, CI image, and container base image all provide the
chosen version.

### Step 3 — Migrate the `javax.*` namespace to `jakarta.*`

This is the core breaking change of the whole migration. Jakarta EE 9 renamed the packages but kept
the class and method names, so the fix is almost always a one-to-one import swap. There is no
compatibility bridge: code that imports `javax.persistence.Entity` will not compile against Spring
Boot 3.

```java
// Before (Spring Boot 2.x) — Java EE namespace
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.validation.Valid;
import javax.validation.constraints.NotBlank;

// After (Spring Boot 3.x) — Jakarta EE namespace
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
```

**Critical exception:** not everything under `javax.*` moves. Core JDK packages such as
`javax.crypto.*`, `javax.sql.*`, and `javax.net.*` are part of the JDK itself, not Jakarta EE, and
must stay as `javax`. Only the Jakarta EE packages (persistence, servlet, validation, transaction,
annotation, mail, xml.bind, and similar) move to `jakarta`. This distinction is exactly why an
AST-aware tool like OpenRewrite is safer than a blind text replacement: it knows which `javax.*`
packages are Jakarta EE and which are JDK.

### Step 4 — Remove the deprecated JAXB and activation dependencies

These artifacts were commonly added to Spring Boot 2.x projects to restore XML binding on Java 9+,
where JAXB was removed from the JDK. They ship the old `javax.xml.bind` namespace, so on Spring Boot
3 they collide with the Jakarta runtime and cause classloading failures. **Remove them; do not
merely upgrade them.**

Dependencies to remove from `pom.xml`:

```xml
<!-- Old JAXB API — ships javax.xml.bind, conflicts with Jakarta. Remove. -->
<dependency>
    <groupId>javax.xml.bind</groupId>
    <artifactId>jaxb-api</artifactId>
</dependency>

<!-- Old JAXB implementation — pairs with the above. Remove. -->
<dependency>
    <groupId>com.sun.xml.bind</groupId>
    <artifactId>jaxb-impl</artifactId>
</dependency>

<dependency>
    <groupId>com.sun.xml.bind</groupId>
    <artifactId>jaxb-core</artifactId>
</dependency>

<!-- Old Java Activation Framework — superseded by jakarta.activation. Remove. -->
<dependency>
    <groupId>javax.activation</groupId>
    <artifactId>activation</artifactId>
</dependency>

<dependency>
    <groupId>javax.activation</groupId>
    <artifactId>javax.activation-api</artifactId>
</dependency>
```

If you genuinely need XML binding on Spring Boot 3 (e.g., a SOAP client or an explicit JAXB context),
add the Jakarta-namespace replacements. If nothing in your application uses JAXB, leave them out
entirely — adding them "just in case" reintroduces the exact kind of namespace coupling you just
removed.

```xml
<!-- Jakarta-namespace JAXB API and runtime -->
<dependency>
    <groupId>jakarta.xml.bind</groupId>
    <artifactId>jakarta.xml.bind-api</artifactId>
    <version>4.0.1</version>
</dependency>
<dependency>
    <groupId>org.glassfish.jaxb</groupId>
    <artifactId>jaxb-runtime</artifactId>
    <version>4.0.4</version>
    <scope>runtime</scope>
</dependency>
```

### Step 5 — Modernize the JWT (jjwt) integration

The widely used `io.jsonwebtoken:jjwt` library is a special case: its own API changed at roughly the
same time as the Spring Boot 3 era. The old `0.9.1` release was a single monolithic jar with a
fluent but loosely typed API (string keys, a `SignatureAlgorithm` enum, `setXxx` builder methods,
and Jackson bundled in). The `0.12.x` line splits into `jjwt-api`, `jjwt-impl`, and `jjwt-jackson`,
requires a real `javax.crypto.SecretKey`, and renames the builder methods. Migrating the dependency
without migrating the calling code will not compile.

#### Dependency change

```xml
<!-- Before: single jar, deprecated API -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt</artifactId>
    <version>0.9.1</version>
</dependency>

<!-- After: split modules. api is compile-scope; impl and jackson are runtime-only,
     which keeps the compile classpath limited to the public API surface. -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.3</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.3</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.3</version>
    <scope>runtime</scope>
</dependency>
```

#### Calling code: before (jjwt 0.9.1)

This is the typical 2.x-era token helper. Note the untyped string key, the deprecated
`SignatureAlgorithm` enum, the `setXxx` builders, and the absence of validation or error handling.

```java
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Date;

public class LegacyJwtUtil {

    private final String secret; // raw string key — weakly typed, no length guarantee

    public LegacyJwtUtil(String secret) {
        this.secret = secret;
    }

    public String generateToken(String username) {
        return Jwts.builder()
            .setSubject(username)
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + 86_400_000L))
            .signWith(SignatureAlgorithm.HS256, secret) // deprecated signature
            .compact();
    }

    public String extractUsername(String token) {
        Claims claims = Jwts.parser()
            .setSigningKey(secret)
            .parseClaimsJws(token)
            .getBody();
        return claims.getSubject();
    }
}
```

#### Calling code: after (jjwt 0.12.x), strictly typed and defensive

The 0.12.x version below uses an explicit `SecretKey` (never a raw string on the wire), validates
every input at the boundary, and contains parsing failures so callers get a clean
`true`/`false`/typed result instead of a leaking runtime exception.

```java
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.Objects;

@Service
public class JwtService {

    /** Minimum key length for HS256: the algorithm requires a key of at least 256 bits (32 bytes). */
    private static final int MIN_HS256_KEY_BYTES = 32;

    private final SecretKey signingKey;
    private final Duration tokenValidity;

    public JwtService(
            @Value("${security.jwt.secret}") String secret,
            @Value("${security.jwt.validity-hours:24}") long validityHours) {

        // Fail fast at construction. A weak or missing key is a security defect, not a runtime edge
        // case, so the application must refuse to start rather than mint forgeable tokens.
        Objects.requireNonNull(secret, "security.jwt.secret must be configured");
        byte[] keyBytes = secret.getBytes(StandardCharsets.UTF_8);
        if (keyBytes.length < MIN_HS256_KEY_BYTES) {
            throw new IllegalArgumentException(
                "security.jwt.secret must be at least " + MIN_HS256_KEY_BYTES
                    + " bytes for HS256, but was " + keyBytes.length + " bytes");
        }
        if (validityHours <= 0L) {
            throw new IllegalArgumentException(
                "security.jwt.validity-hours must be positive, but was " + validityHours);
        }

        this.signingKey = Keys.hmacShaKeyFor(keyBytes);
        this.tokenValidity = Duration.ofHours(validityHours);
    }

    /**
     * Issues a signed token for the given subject.
     *
     * @param subject the principal the token represents; must be non-null and non-blank
     * @return a compact, signed JWT string
     * @throws IllegalArgumentException if {@code subject} is null or blank
     */
    public String generateToken(String subject) {
        if (subject == null || subject.isBlank()) {
            throw new IllegalArgumentException("JWT subject must not be null or blank");
        }
        Instant now = Instant.now();
        return Jwts.builder()
            .subject(subject)
            .issuedAt(Date.from(now))
            .expiration(Date.from(now.plus(tokenValidity)))
            .signWith(signingKey, Jwts.SIG.HS256)
            .compact();
    }

    /**
     * Extracts the subject from a verified token.
     *
     * @param token a compact JWT string; must be non-null and non-blank
     * @return the token subject
     * @throws IllegalArgumentException if {@code token} is null or blank
     * @throws JwtException if the token is malformed, expired, or its signature does not verify
     */
    public String extractSubject(String token) {
        return parseClaims(token).getSubject();
    }

    /**
     * Validates a token against an expected subject without throwing on failure.
     *
     * @param token           the compact JWT string to check
     * @param expectedSubject the subject the token is expected to carry; must be non-null and non-blank
     * @return {@code true} only if the token verifies, is unexpired, and matches {@code expectedSubject}
     */
    public boolean isTokenValid(String token, String expectedSubject) {
        if (expectedSubject == null || expectedSubject.isBlank()) {
            throw new IllegalArgumentException("expectedSubject must not be null or blank");
        }
        try {
            Claims claims = parseClaims(token);
            Date expiration = claims.getExpiration();
            boolean unexpired = expiration != null && expiration.toInstant().isAfter(Instant.now());
            return unexpired && expectedSubject.equals(claims.getSubject());
        } catch (JwtException | IllegalArgumentException ex) {
            // Never trust a token we could not fully verify. Return false rather than propagate.
            return false;
        }
    }

    private Claims parseClaims(String token) {
        if (token == null || token.isBlank()) {
            throw new IllegalArgumentException("JWT token must not be null or blank");
        }
        Jws<Claims> jws = Jwts.parser()
            .verifyWith(signingKey)
            .build()
            .parseSignedClaims(token);
        return jws.getPayload();
    }
}
```

#### jjwt API rename mapping

Use this to migrate other call sites mechanically:

| jjwt 0.9.1 (old) | jjwt 0.12.x (new) |
|---|---|
| `Jwts.parser().setSigningKey(...)` | `Jwts.parser().verifyWith(SecretKey).build()` |
| `parseClaimsJws(token).getBody()` | `parseSignedClaims(token).getPayload()` |
| `.setSubject(...)` / `.setIssuedAt(...)` / `.setExpiration(...)` | `.subject(...)` / `.issuedAt(...)` / `.expiration(...)` |
| `signWith(SignatureAlgorithm.HS256, stringKey)` | `signWith(SecretKey, Jwts.SIG.HS256)` |

### Step 6 — Run OpenRewrite for automated migration (recommended)

OpenRewrite applies the namespace rename and many dependency/config changes as AST transformations,
so it correctly distinguishes JDK `javax.*` from Jakarta `javax.*` and avoids the over-matching that
text find/replace causes. **Prefer it over hand-editing for anything beyond a trivial project.**

Add the plugin to `pom.xml`:

```xml
<plugin>
    <groupId>org.openrewrite.maven</groupId>
    <artifactId>rewrite-maven-plugin</artifactId>
    <version>5.42.0</version>
    <configuration>
        <activeRecipes>
            <recipe>org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_2</recipe>
        </activeRecipes>
    </configuration>
    <dependencies>
        <dependency>
            <groupId>org.openrewrite.recipe</groupId>
            <artifactId>rewrite-spring</artifactId>
            <version>5.21.0</version>
        </dependency>
    </dependencies>
</plugin>
```

Run a dry run first so you can review the proposed diff before anything is written to disk. Apply
only once the dry-run patch looks correct:

```bash
# Generate a patch under target/rewrite/ WITHOUT modifying source — review this first.
mvn rewrite:dryRun

# Apply the transformations in place once the dry-run diff is approved.
mvn rewrite:run
```

**HARD RULE:** Check the plugin and `rewrite-spring` versions against the current releases before
running; the recipe set evolves, and an outdated recipe may miss newer changes. Commit (or stash)
your work beforehand so `rewrite:run` is fully reversible if you disagree with any transformation.

### Step 7 — Manual find/replace (fallback only)

If you cannot use OpenRewrite, you can nudge the most common version changes with a scripted
search/replace — but understand the risk: line-based regex over XML cannot see structure, so a loose
pattern can rewrite an unrelated `<version>` tag. **Always work on a committed tree and a backup so
the change is reversible.**

#### Windows / PowerShell (primary host)

```powershell
# Take a backup; the replacement edits in place and cannot be undone otherwise.
Copy-Item pom.xml pom.xml.bak

(Get-Content pom.xml -Raw) `
    -replace '<version>2\.7\.\d+</version>', '<version>3.2.0</version>' `
    -replace '<java\.version>(1\.8|8|11)</java\.version>', '<java.version>21</java.version>' |
    Set-Content pom.xml

# Review every change before trusting it.
Compare-Object (Get-Content pom.xml.bak) (Get-Content pom.xml)
```

#### Linux / macOS (sed)

```bash
# Take a backup; sed -i edits in place and cannot be undone otherwise.
cp pom.xml pom.xml.bak

# Update Spring Boot 2.7.x parent versions to 3.2.0.
sed -i 's#<version>2\.7\.[0-9]\+</version>#<version>3.2.0</version>#g' pom.xml

# Normalize the Java version property to 21 for the common legacy values.
sed -i 's#<java.version>1\.8</java.version>#<java.version>21</java.version>#g' pom.xml
sed -i 's#<java.version>8</java.version>#<java.version>21</java.version>#g' pom.xml
sed -i 's#<java.version>11</java.version>#<java.version>21</java.version>#g' pom.xml

# Review every change before trusting it.
diff -u pom.xml.bak pom.xml
```

## Pitfalls

- **Blind `javax.*` → `jakarta.*` text replacement breaks JDK packages.** `javax.crypto.*`,
  `javax.sql.*`, and `javax.net.*` are JDK packages, not Jakarta EE, and must stay as `javax`.
  Only persistence, servlet, validation, transaction, annotation, mail, xml.bind, and similar
  Jakarta EE packages move. This is why OpenRewrite (AST-aware) is strongly preferred over
  find/replace.

- **Leaving old JAXB dependencies in place causes runtime classloading failures.** The old
  `javax.xml.bind:jaxb-api` and `com.sun.xml.bind:jaxb-impl` artifacts ship `javax.xml.bind` classes
  that collide with the Jakarta runtime. Remove them entirely; do not upgrade them in place.

- **JDK version mismatch produces `UnsupportedClassVersionError` at runtime, not a build failure.**
  After setting `java.version` to 17 or 21, verify the local JDK, CI image, and container base image
  all match. A silent mismatch surfaces only at application startup.

- **Migrating jjwt dependency without updating calling code will not compile.** The 0.12.x API
  removes `SignatureAlgorithm`, renames `setXxx` builders to `xxx`, replaces `setSigningKey` with
  `verifyWith`, and requires a `SecretKey` object instead of a raw string. Both the `pom.xml` and
  every call site must change together.

- **Weak JWT keys silently accepted in jjwt 0.9.1.** The old API accepted any string as a signing
  key. The new `Keys.hmacShaKeyFor()` enforces a minimum 32-byte key for HS256. If your existing
  secret is shorter, the application will refuse to start — this is correct behavior, not a bug.

- **OpenRewrite `rewrite:run` modifies source files in place.** Always run `rewrite:dryRun` first
  and review the patch under `target/rewrite/`. Commit or stash before running `rewrite:run` so the
  transformation is reversible via `git checkout` or `git stash pop`.

- **Outdated OpenRewrite recipe versions miss newer changes.** The recipe set evolves with each
  release. Check `rewrite-maven-plugin` and `rewrite-spring` against current releases before
  running.

- **Skipping the 2.7.x stabilization step.** Deprecation warnings on 2.7.x become hard compile
  errors on 3.x. Clearing them first on 2.7.x turns runtime surprises into compile-time issues you
  have already handled.

- **Adding Jakarta JAXB dependencies "just in case."** If nothing in your application uses JAXB,
  do not add `jakarta.xml.bind` artifacts. Doing so reintroduces the namespace coupling you just
  removed.

## Verification

### Verification checklist

Each item maps to a specific failure mode from the steps above, so a failed check tells you which
step to revisit:

- [ ] Spring Boot parent version reads `3.x` (Step 1) — otherwise the 3.x dependency set is not active.
- [ ] `java.version` is `17` or `21` (Step 2) — and the build/runtime JDK actually matches it.
- [ ] No `javax.*` Jakarta EE imports remain (Step 3) — JDK `javax.crypto`/`javax.sql` are expected and fine.
- [ ] Old `javax.xml.bind` / `javax.activation` dependencies are gone (Step 4).
- [ ] The jjwt dependency is the split `0.12.x` modules and call sites use the new API (Step 5).
- [ ] The project compiles (`mvn clean compile`) — the fastest signal that namespace and API changes are complete.
- [ ] The full test suite passes (`mvn test`) — catches behavioral regressions a compile cannot.
- [ ] The application starts and a smoke test of the primary endpoints succeeds.

### Verification commands — Windows / PowerShell (primary host)

```powershell
# Parent version should show a 3.x line.
Select-String -Path pom.xml -Pattern 'spring-boot-starter-parent' -Context 0,2

# Java version should be 17 or 21.
Select-String -Path pom.xml -Pattern 'java\.version'

# Each of these should return NO matches once migration is complete.
Select-String -Path .\**\*.java, .\pom.xml -Pattern 'javax\.xml\.bind'
Select-String -Path pom.xml -Pattern 'jaxb-api'
Select-String -Path pom.xml -Pattern '<version>0\.9\.1</version>'   # old jjwt version must be gone

# Compile and test — the authoritative checks.
mvn clean compile
mvn test
```

### Verification commands — Linux / macOS

```bash
# Parent version should show a 3.x line.
grep -A2 "spring-boot-starter-parent" pom.xml | grep "version"

# Java version should be 17 or 21.
grep "java.version" pom.xml

# Each of these should return NO matches once migration is complete.
grep -R "javax.xml.bind" --include=*.java --include=pom.xml .
grep "jaxb-api" pom.xml
grep "<version>0\.9\.1</version>" pom.xml   # old jjwt version must be gone

# Compile and test — the authoritative checks.
mvn clean compile
mvn test
```

## Related skills

These cover the design-level changes that a version bump alone does not handle; reach for them when
the "Do not use" caveats apply:

- **Jakarta Namespace Migration** — deeper coverage of the `javax.*` → `jakarta.*` rename across
  persistence, servlet, and validation.
- **Spring Security 6 Migration** — the `WebSecurityConfigurerAdapter` removal and the move to the
  component-based, lambda-DSL `SecurityFilterChain`.
- **RestClient Migration** — replacing `RestTemplate` patterns with the Spring 6 `RestClient`.
- **Java 17/21 Migration** — language and JVM changes (records, sealed types, pattern matching,
  virtual threads) you can adopt once on the new baseline.
