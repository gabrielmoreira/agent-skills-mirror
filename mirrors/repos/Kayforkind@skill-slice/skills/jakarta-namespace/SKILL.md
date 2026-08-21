---
name: jakarta-namespace
version: 1.1.1
description: "Rewrites Java EE specification types from javax.* onto jakarta.* in sources, Maven/Gradle coordinates, and web.xml/persistence.xml namespaces for Spring Boot 3 and Jakarta EE 9+. Trigger on package javax does not exist, javax.persistence, or javax.servlet after a Boot 3 bump. Never rewrite JDK packages such as javax.sql or javax.crypto; not for Android androidx."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Use this skill when:
- Upgrading to Spring Boot 3.x (or newer versions like 3.2.x, 3.3.x) and encountering `package javax.xxx does not exist` compilation errors.
- Migrating `javax.persistence`, `javax.validation`, `javax.servlet`, `javax.websocket`, `javax.jms`, `javax.json`, `javax.xml.ws`, `javax.jws`, `javax.security.enterprise`, `javax.interceptor`, `javax.inject`, `javax.ejb`, `javax.ws.rs`, `javax.enterprise.context`, `javax.transaction`, `javax.annotation`, `javax.mail`, `javax.xml.bind`, or `javax.activation` imports.
- Fixing compilation errors after the transition from Java EE to Jakarta EE.
- Projects targeting Servlet 6.0, JPA 3.1, or Bean Validation 3.0 specifications.

**Trigger keywords**: `jakarta`, `javax`, `namespace migration`, `Spring Boot 3`, `Jakarta EE`, `javax.persistence`, `javax.validation`, `javax.servlet`, `package javax does not exist`.

## Do Not Use

Do **NOT** use this skill for JDK packages. These are part of the Java 17+ JDK itself, not part of Java EE, and their `javax` namespace is maintained by the JDK. Attempting to migrate these will cause compilation errors or runtime issues:

| Package | Status |
|---|---|
| `javax.sql.*` | JDK — do not migrate |
| `javax.crypto.*` | JDK — do not migrate |
| `javax.naming.*` | JDK — do not migrate |
| `javax.xml.*` | JDK — do not migrate (but `javax.xml.bind` and `javax.xml.ws` DO migrate) |
| `javax.management.*` | JDK — do not migrate |
| `javax.security.*` | JDK — do not migrate (but `javax.security.enterprise` DOES migrate) |
| `javax.net.*` | JDK — do not migrate |
| `javax.sound.*` | JDK — do not migrate |
| `javax.swing.*` | JDK — do not migrate |
| `javax.imageio.*` | JDK — do not migrate |
| `javax.print.*` | JDK — do not migrate |
| `javax.rmi.*` | JDK — do not migrate |
| `javax.script.*` | JDK — do not migrate |
| `javax.smartcardio.*` | JDK — do not migrate |
| `javax.tools.*` | JDK — do not migrate |
| `javax.transaction.xa` | JDK internal — do not migrate (but `javax.transaction` the JTA API DOES migrate to `jakarta.transaction`) |
| `javax.activation` (JDK internal) | JDK internal — do not migrate (but the standalone `javax.activation` API DOES migrate to `jakarta.activation`) |

**Warning — `javax.annotation.*`**: Be particularly careful. While `javax.annotation.PostConstruct` and `javax.annotation.PreDestroy` are part of the Common Annotations specification (which moved to `jakarta.annotation.*`), other `javax.annotation` classes might still be present in the JDK or third-party libraries that haven't fully migrated. Always verify the specific class after migration.

## Prerequisites

- Java 17+ installed and on `PATH`.
- Build tool (Maven 3.6+ or Gradle 7+) installed.
- Git repository in a clean, committed state (for rollback safety).
- PowerShell 5.1+ (Windows host, primary) or bash (Linux/macOS).

## Procedure

### Step 1 — Backup Your Project

Before performing any large-scale find-and-replace, ensure you have a clean commit or backup.

```powershell
# Windows PowerShell — verify clean git state
git status --porcelain
# If clean, create a migration branch
git checkout -b jakarta-namespace-migration
```

```bash
# Linux/macOS
git status --porcelain
git checkout -b jakarta-namespace-migration
```

### Step 2 — Identify Packages to Migrate

Scan your codebase for `javax.*` imports that belong to Jakarta EE specifications (not JDK packages):

```powershell
# Windows PowerShell — list all javax.* imports in Java files
Get-ChildItem -Recurse -Filter *.java | Select-String -Pattern "import javax\." | ForEach-Object { $_.Line.Trim() } | Sort-Object -Unique
```

```bash
# Linux/macOS
grep -rh "import javax\." --include="*.java" . | sed 's/^[[:space:]]*//' | sort -u
```

Review the output against the **Do Not Use** table above. Only migrate packages that are part of Jakarta EE specifications.

### Step 3 — Batch Replace Imports

#### Windows PowerShell (Primary Host)

Run these from your project's root directory. Each command targets a specific Jakarta EE package.

```powershell
# Define the list of package prefixes to migrate
$packages = @(
    "javax.persistence",
    "javax.validation",
    "javax.servlet",
    "javax.annotation",
    "javax.transaction",
    "javax.websocket",
    "javax.jms",
    "javax.json",
    "javax.xml.ws",
    "javax.jws",
    "javax.security.enterprise",
    "javax.interceptor",
    "javax.inject",
    "javax.ejb",
    "javax.ws.rs",
    "javax.enterprise",
    "javax.mail",
    "javax.xml.bind",
    "javax.activation"
)

# Apply replacements across all .java files
foreach ($pkg in $packages) {
    $jakartaPkg = $pkg -replace "^javax\.", "jakarta."
    Get-ChildItem -Recurse -Filter *..java | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        if ($content -match [regex]::Escape("import $pkg")) {
            $newContent = $content -replace ("import " + [regex]::Escape($pkg)), ("import " + $jakartaPkg)
            Set-Content -Path $_.FullName -Value $newContent -NoNewline
            Write-Host "Migrated: $($_.Name) — $pkg -> $jakartaPkg"
        }
    }
}
```

#### Linux/macOS (sed)

```bash
# IMPORTANT: On macOS, sed -i requires an empty string argument: sed -i ''
# On Linux, use: sed -i (no extra argument)

# Migrate JPA imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.persistence/import jakarta.persistence/g' {} +

# Migrate Validation imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.validation/import jakarta.validation/g' {} +

# Migrate Servlet imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.servlet/import jakarta.servlet/g' {} +

# Migrate Annotation imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.annotation/import jakarta.annotation/g' {} +

# Migrate Transaction imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.transaction/import jakarta.transaction/g' {} +

# Migrate WebSocket imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.websocket/import jakarta.websocket/g' {} +

# Migrate JMS imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.jms/import jakarta.jms/g' {} +

# Migrate JSON-B/JSON-P imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.json/import jakarta.json/g' {} +

# Migrate JAX-WS imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.xml\.ws/import jakarta.xml.ws/g' {} +

# Migrate JAX-RS (REST) imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.ws\.rs/import jakarta.ws.rs/g' {} +

# Migrate CDI imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.enterprise/import jakarta.enterprise/g' {} +

# Migrate EJB imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.ejb/import jakarta.ejb/g' {} +

# Migrate Inject imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.inject/import jakarta.inject/g' {} +

# Migrate Mail imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.mail/import jakarta.mail/g' {} +

# Migrate JAXB imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.xml\.bind/import jakarta.xml.bind/g' {} +

# Migrate Activation imports
find . -type f -name "*.java" -exec sed -i 's/import javax\.activation/import jakarta.activation/g' {} +
```

> **macOS note**: Replace `sed -i` with `sed -i ''` (empty string after `-i`).

### Step 4 — Update Fully-Qualified References in Code

The sed/PowerShell commands above only target `import` statements. If your code uses fully-qualified class names inline (e.g., `javax.servlet.http.HttpServlet` in class declarations or method signatures), you must also replace those:

```powershell
# Windows PowerShell — replace fully-qualified javax references (not just imports)
$packages = @("javax.persistence","javax.validation","javax.servlet","javax.annotation","javax.transaction","javax.websocket","javax.jms","javax.json","javax.xml.ws","javax.jws","javax.security.enterprise","javax.interceptor","javax.inject","javax.ejb","javax.ws.rs","javax.enterprise","javax.mail","javax.xml.bind","javax.activation")
foreach ($pkg in $packages) {
    $jakartaPkg = $pkg -replace "^javax\.", "jakarta."
    Get-ChildItem -Recurse -Filter *.java | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        if ($content -match [regex]::Escape($pkg)) {
            $newContent = $content -replace ([regex]::Escape($pkg)), $jakartaPkg
            Set-Content -Path $_.FullName -Value $newContent -NoNewline
        }
    }
}
```

### Step 5 — Update Build Dependencies

Update your `pom.xml` or `build.gradle` to use Jakarta EE 9+ compatible dependencies.

**For Spring Boot 3.x**: The parent POM handles this automatically. Ensure your `<parent>` is set to Spring Boot 3.x:

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.0</version>
</parent>
```

**For direct Jakarta EE dependencies** (non-Spring Boot), update versions manually:

```xml
<!-- JPA 3.1 -->
<dependency>
    <groupId>jakarta.persistence</groupId>
    <artifactId>jakarta.persistence-api</artifactId>
    <version>3.1.0</version>
</dependency>

<!-- Servlet 6.0 -->
<dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
    <scope>provided</scope>
</dependency>

<!-- Bean Validation 3.0 -->
<dependency>
    <groupId>jakarta.validation</groupId>
    <artifactId>jakarta.validation-api</artifactId>
    <version>3.0.0</version>
</dependency>
```

**Gradle equivalent**:

```groovy
implementation 'jakarta.persistence:jakarta.persistence-api:3.1.0'
compileOnly 'jakarta.servlet:jakarta.servlet-api:6.0.0'
implementation 'jakarta.validation:jakarta.validation-api:3.0.0'
```

### Step 6 — Update Non-Java Configuration Files

Some XML descriptors and properties files also reference `javax` namespaces:

| File Type | What to Change |
|---|---|
| `web.xml` | `http://xmlns.jcp.org/xml/ns/javaee` → `https://jakarta.ee/xml/ns/jakartaee`; update `version` to 6.0 |
| `beans.xml` | Update XSD to `https://jakarta.ee/xml/ns/jakartaee/beans_4.0.xsd` |
| `persistence.xml` | Update XSD namespace to `jakarta.persistence` |
| `validation.xml` | Update XSD to `jakarta.validation` namespace |

## Examples

### Entity Migration (JPA)

```java
// BEFORE (Spring Boot 2.x / Java EE 8) — WILL NOT COMPILE in Spring Boot 3.x+
import javax.persistence.Entity;
import javax.persistence.Table;
import javax.persistence.Id;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Column;
import javax.persistence.Version;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Version
    private Long version;
}

// AFTER (Spring Boot 3.x+ / Jakarta EE 9+) — REQUIRED
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Column;
import jakarta.persistence.Version;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Version
    private Long version;
}
```

### Validation Migration

```java
// BEFORE (Java EE 8)
import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;

// AFTER (Jakarta EE 9+)
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
```

### Servlet Migration

```java
// BEFORE (Java EE 8)
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;

@WebServlet("/old-hello")
public class OldHelloServlet extends javax.servlet.http.HttpServlet {
    // ...
}

// AFTER (Jakarta EE 9+)
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;

@WebServlet("/new-hello")
public class NewHelloServlet extends jakarta.servlet.http.HttpServlet {
    // ...
}
```

## Pitfalls

1. **Migrating JDK packages by mistake**: Packages like `javax.sql.*`, `javax.crypto.*`, `javax.naming.*`, `javax.xml.*` (except `xml.bind` and `xml.ws`), `javax.management.*`, `javax.net.*`, `javax.swing.*` are JDK packages and must NOT be migrated. Always cross-reference against the Do Not Use table.

2. **`javax.annotation.*` ambiguity**: `@PostConstruct` and `@PreDestroy` move to `jakarta.annotation.*`, but other `javax.annotation` classes (e.g., `javax.annotation.Nonnull` from JSR-305) are third-party and should NOT be blindly migrated. Verify each class after replacement.

3. **`javax.transaction.xa` vs `javax.transaction`**: The JTA API `javax.transaction` migrates to `jakarta.transaction`, but the JDK's internal `javax.transaction.xa` does NOT migrate. A blanket `javax.transaction` → `jakarta.transaction` replacement could break XA-related code if it references JDK-internal classes.

4. **Fully-qualified class names in code body**: The sed/PowerShell import-only replacement misses fully-qualified references like `extends javax.servlet.http.HttpServlet` or `throws javax.servlet.ServletException`. Run Step 4 to catch these.

5. **Third-party libraries not yet migrated**: Some libraries may still depend on `javax.*` namespaces. If a dependency hasn't released a Jakarta-compatible version, you may need a compatibility layer (e.g., Eclipse Transformer) or wait for the library to catch up.

6. **XML descriptor files**: `web.xml`, `beans.xml`, `persistence.xml`, and `validation.xml` have their own namespace URIs that must be updated separately. Missing these can cause runtime deployment failures even when Java code compiles.

7. **macOS `sed -i` syntax**: On macOS, `sed -i` requires an empty backup extension argument (`sed -i ''`). Using `sed -i` without it will fail. On Linux, `sed -i` works without the extra argument.

8. **PowerShell file encoding**: `Set-Content` may change file encoding. If your project uses UTF-8 without BOM, add `-Encoding UTF8NoBOM` (PowerShell 6+) or use `[System.IO.File]::WriteAllText()` to preserve encoding.

## Verification

### Verify No Old `javax` Imports Remain (Jakarta EE packages)

These commands should return **NO results** after a successful migration.

```powershell
# Windows PowerShell — check for remaining Jakarta EE javax imports
$jakartaPackages = "persistence|validation|servlet|annotation|transaction|websocket|jms|json|xml\.ws|jws|security\.enterprise|interceptor|inject|ejb|ws\.rs|enterprise|mail|xml\.bind|activation"
Get-ChildItem -Recurse -Filter *.java | Select-String -Pattern "import javax\.($jakartaPackages)"
# Expected: no output (empty result)
```

```bash
# Linux/macOS — comprehensive check
grep -r "import javax\." --include="*.java" . | grep -E "(persistence|validation|servlet|annotation|transaction|websocket|jms|json|xml\.ws|jws|security\.enterprise|interceptor|inject|ejb|ws\.rs|enterprise|mail|xml\.bind|activation)"
# Expected: no output (empty result)
```

### Verify `jakarta` Imports Are Present

These commands **MUST** return results showing your migrated classes.

```powershell
# Windows PowerShell
Get-ChildItem -Recurse -Filter *.java | Select-String -Pattern "import jakarta\." | Select-Object -First 20
```

```bash
# Linux/macOS
grep -r "import jakarta\." --include="*.java" . | head -20
```

### Verify Project Compiles

```powershell
# Maven
mvn clean compile
# Expected: BUILD SUCCESS

# Gradle
.\gradlew clean build
# Expected: BUILD SUCCESSFUL
```

```bash
# Maven
mvn clean compile

# Gradle
./gradlew clean build
```

### Verification Checklist

- [ ] Project compiles successfully without any `package javax.xxx does not exist` errors.
- [ ] No `javax.*` imports remain for Jakarta EE specifications (verification commands return empty).
- [ ] All `jakarta.*` imports are correctly resolved.
- [ ] All unit tests and integration tests pass.
- [ ] Application starts up and runs correctly in a Jakarta EE 9+ compatible environment.
- [ ] Dependency configs (`pom.xml` / `build.gradle`) updated to Jakarta EE 9+ compatible versions.
- [ ] XML descriptors (`web.xml`, `beans.xml`, `persistence.xml`, `validation.xml`) updated to Jakarta namespaces.
- [ ] No JDK packages (e.g., `javax.sql`, `javax.crypto`, `javax.naming`) were accidentally migrated.

## Related Skills

- **Spring Boot 3.x Migration**: Essential for any Spring Boot application upgrade as it mandates Jakarta EE 9+.
- **Java EE to Jakarta EE Migration**: The fundamental shift in enterprise Java.
- **Package Migration**: General skill for updating package namespaces.
- **Dependency Management Update**: Updating `pom.xml` or `build.gradle` for Jakarta EE compatible libraries.
