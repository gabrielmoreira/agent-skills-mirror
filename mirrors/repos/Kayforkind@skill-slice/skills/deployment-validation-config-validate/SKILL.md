---
name: deployment-validation-config-validate
version: 1.2.1
description: "Validates deploy-time config as a typed contract: Ajv JSON Schema 2020-12, environment policy (debug, HTTPS, password length, encryption-at-rest), and YAML/JSON/TOML/INI/.env drift plus secret-shape checks. Trigger on CI config gates or failing the build when production debug is enabled. Do not use for OPA/RBAC runtime policy. Never treat this folder as a shipped analyzer or validator file tree; helpers are inlined here."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Configuration Validation

Treat configuration as a *verified contract* rather than a loose collection of files: every value should have a declared shape, every environment should enforce its own safety policy, and every secret should be encrypted at rest. This skill builds that contract layer by layer — discovery, schema validation, environment policy, tests, runtime re-validation, versioned migrations, encryption, and generated docs.

## When to Use

- **Validating config before deploy.** A bad value (a `port` of `70000`, `debug: true` in production) should fail CI, not page someone at 2am. Schema + environment validation catches these deterministically.
- **Building CI/CD validation for YAML, JSON, TOML, INI, `.env`, or JS config files.** Each format parses to the same in-memory shape, so one schema can guard them all.
- **Enforcing environment-specific security and compliance rules.** Structural validity is not the same as "safe for production"; the environment validator encodes that gap.
- **You need a checklist or reference implementation.** The sections below are working, typed reference code you can adapt rather than rules to memorize.

**Do not use when:**

- The task is unrelated to configuration validation. Reach for a domain-appropriate skill instead.
- You actually need runtime *policy* enforcement (RBAC, quotas, network policy). This skill validates *shape and values*; it does not replace policy engines like OPA (Open Policy Agent). Use OPA when decisions depend on external state rather than the config file itself.
- Secrets are in plaintext config and you have no plan to encrypt or externalize them. This skill assumes secrets are either encrypted or pulled from a secret manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault).

## Prerequisites

- **Node.js 18+** with npm/pnpm for Ajv-based schema validation (TypeScript examples).
- **Python 3.10+** with `pyyaml` installed for the configuration analyzer and environment validator:
  ```powershell
  pip install pyyaml
  ```
- **Jest v30** (or compatible) for configuration testing:
  ```powershell
  npm install --save-dev jest @jest/globals ajv ajv-formats
  ```
- **Ajv 2020-12** (`ajv/dist/2020`) with `ajv-formats` for JSON Schema 2020-12 support.
- Windows host is primary. All shell commands assume **PowerShell**. Adjust path separators (`\` vs `/`) when running on WSL or Linux CI runners.

## Procedure

### Step 1 — Configuration Analysis (Discovery & Drift Detection)

**Why:** You cannot validate what you have not inventoried. Before writing a single schema, discover every config file, flag values that look like inlined secrets, and detect *drift* (a key present in `staging` but missing in `production` is one of the most common deploy-time surprises).

Copy the analyzer below into the application repo as a local helper (for example `config_analyzer.py`). The listing in this file is the canonical version.

```python
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


@dataclass(frozen=True)
class ConfigFile:
    path: str
    type: str          # "json" | "yaml" | "toml" | "ini" | "dotenv" | "javascript" | "unknown"
    environment: str   # "production" | "staging" | "development" | "test" | "local" | "default"


@dataclass(frozen=True)
class SecurityIssue:
    file: str
    type: str
    severity: str      # "high" | "medium" | "low"
    detail: str


@dataclass(frozen=True)
class ConsistencyIssue:
    files: List[str]
    type: str
    detail: str


@dataclass
class ProjectAnalysis:
    config_files: List[ConfigFile] = field(default_factory=list)
    security_issues: List[SecurityIssue] = field(default_factory=list)
    consistency_issues: List[ConsistencyIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ConfigurationAnalyzer:
    """Discovers config files and surfaces the highest-risk problems first."""

    IGNORE_DIRS = frozenset({"node_modules", ".git", "dist", "build", ".venv", "__pycache__", ".next"})

    # Key names that suggest a secret lives nearby.
    SECRET_PATTERNS: Dict[str, "re.Pattern[str]"] = {
        "api_key": re.compile(r"(api[_-]?key|apikey)", re.IGNORECASE),
        "password": re.compile(r"(secret|password|passwd)", re.IGNORECASE),
        "token": re.compile(r"(token|auth)", re.IGNORECASE),
        "aws": re.compile(r"(aws[_-]?access)", re.IGNORECASE),
    }

    # A value that looks like a real inlined secret rather than a reference or placeholder.
    # The negative lookahead skips ${VAR}, <PLACEHOLDER>, {{ template }}, ENV_VARS, process.env.*
    REAL_SECRET_VALUE = re.compile(
        r"""[:=]\s*['"]?(?!\$\{|<|\{\{|ENV|process\.env)[A-Za-z0-9/+_\-]{12,}['"]?"""
    )

    PLACEHOLDER_TOKENS = ("changeme", "example", "your_", "xxxx", "placeholder", "dummy", "redacted")

    def __init__(self, project_path: str) -> None:
        root = Path(project_path)
        if not root.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {project_path}")
        self.root = root

    def analyze_project(self) -> ProjectAnalysis:
        config_files = self._find_config_files()
        return ProjectAnalysis(
            config_files=config_files,
            security_issues=self._check_security_issues(config_files),
            consistency_issues=self._check_consistency(config_files),
            recommendations=self._build_recommendations(config_files),
        )

    def _find_config_files(self) -> List[ConfigFile]:
        patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.env*", "config.js", "config.*.js"]
        found: Dict[str, ConfigFile] = {}
        for pattern in patterns:
            for path in self.root.rglob(pattern):
                if not path.is_file() or self._should_ignore(path):
                    continue
                resolved = str(path)
                found[resolved] = ConfigFile(
                    path=resolved,
                    type=self._detect_config_type(path),
                    environment=self._detect_environment(path),
                )
        return sorted(found.values(), key=lambda c: c.path)

    def _should_ignore(self, path: Path) -> bool:
        return any(part in self.IGNORE_DIRS for part in path.parts)

    def _detect_config_type(self, path: Path) -> str:
        name = path.name.lower()
        if ".env" in name:
            return "dotenv"
        return {
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
            ".js": "javascript",
        }.get(path.suffix.lower(), "unknown")

    def _detect_environment(self, path: Path) -> str:
        name = path.name.lower()
        aliases = {"prod": "production", "stage": "staging", "dev": "development"}
        for token in ("production", "prod", "staging", "stage", "development", "dev", "test", "local"):
            if token in name:
                return aliases.get(token, token)
        return "default"

    def _check_security_issues(self, config_files: List[ConfigFile]) -> List[SecurityIssue]:
        issues: List[SecurityIssue] = []
        for config in config_files:
            try:
                content = Path(config.path).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for label, pattern in self.SECRET_PATTERNS.items():
                for match in pattern.finditer(content):
                    line = self._line_at(content, match.start())
                    if self._looks_like_real_secret(line):
                        issues.append(SecurityIssue(
                            file=config.path,
                            type=f"potential_{label}_secret",
                            severity="high",
                            detail=f"Possible inlined secret near: {line.strip()[:80]}",
                        ))
                        break
        return issues

    def _looks_like_real_secret(self, line: str) -> bool:
        lowered = line.lower()
        if any(token in lowered for token in self.PLACEHOLDER_TOKENS):
            return False
        return bool(self.REAL_SECRET_VALUE.search(line))

    @staticmethod
    def _line_at(content: str, index: int) -> str:
        start = content.rfind("\n", 0, index) + 1
        end = content.find("\n", index)
        return content[start:] if end == -1 else content[start:end]

    def _check_consistency(self, config_files: List[ConfigFile]) -> List[ConsistencyIssue]:
        issues: List[ConsistencyIssue] = []
        by_type: Dict[str, List[ConfigFile]] = {}
        for config in config_files:
            by_type.setdefault(config.type, []).append(config)

        for config_type, group in by_type.items():
            if len(group) < 2:
                continue
            key_sets: Dict[str, set[str]] = {}
            for config in group:
                keys = self._top_level_keys(Path(config.path))
                if keys is not None:
                    key_sets[config.path] = keys
            if len(key_sets) < 2:
                continue
            union: set[str] = set().union(*key_sets.values())
            for path, keys in key_sets.items():
                missing = union - keys
                if missing:
                    issues.append(ConsistencyIssue(
                        files=[path],
                        type="missing_keys",
                        detail=f"Missing keys present in sibling {config_type} configs: {sorted(missing)}",
                    ))
        return issues

    def _top_level_keys(self, path: Path) -> Optional[set[str]]:
        suffix = path.suffix.lower()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        try:
            if suffix == ".json":
                data: Any = json.loads(text)
            elif suffix in (".yaml", ".yml"):
                data = yaml.safe_load(text)
            else:
                return None
        except (json.JSONDecodeError, yaml.YAMLError):
            return None
        return set(data.keys()) if isinstance(data, dict) else None

    def _build_recommendations(self, config_files: List[ConfigFile]) -> List[str]:
        recommendations: List[str] = []
        if not config_files:
            recommendations.append("No configuration files found; confirm the project path is correct.")
            return recommendations
        if not any(c.type == "json" for c in config_files):
            recommendations.append("Commit JSON Schema files so configs can be validated automatically in CI.")
        if any(c.environment == "default" for c in config_files):
            recommendations.append(
                "Some configs are environment-agnostic; adopt a `*.production.yaml` naming scheme "
                "so environment intent is explicit and drift checks can pair files correctly."
            )
        recommendations.append("Run schema validation for every config file in CI before deployment.")
        return recommendations
```

**Run the analyzer on Windows (PowerShell):**

```powershell
python -c "from config_analyzer import ConfigurationAnalyzer; import json; r = ConfigurationAnalyzer('~\myproject').analyze_project(); print(json.dumps({'files': len(r.config_files), 'security': len(r.security_issues), 'consistency': len(r.consistency_issues)}, indent=2))"
```

### Step 2 — Schema Validation (JSON Schema 2020-12 with Ajv)

**Why:** A schema is the single source of truth for a config's shape. Define it once and validate every format against it. Three constructor choices matter:

- `strict: true` — makes a typo in the *schema* a hard error instead of a silent no-op.
- `coerceTypes: true` — turns the `"5432"` you get from an env var or `.env` parser into the number `5432`.
- `useDefaults: true` — fills in declared defaults so downstream code never sees `undefined`.

Typing the schema as `JSONSchemaType<DatabaseConfig>` means the schema and the TypeScript interface can never drift apart without a compile error.

Copy the validator class and schema types below into the application repo (for example `config-validator.ts` and `schemas.ts`). The listing in this file is canonical.

```typescript
import Ajv2020 from "ajv/dist/2020";
import type { DefinedError, JSONSchemaType, SchemaObject, ValidateFunction } from "ajv";
import addFormats from "ajv-formats";

export interface ValidationError {
  readonly path: string;     // JSON Pointer to the offending value, or "/" for the root
  readonly message: string;
  readonly keyword: string; // the failing JSON Schema keyword, e.g. "format" | "required"
}

export interface ValidationResult {
  readonly valid: boolean;
  readonly errors: readonly ValidationError[];
}

export class ConfigValidator {
  private readonly ajv: Ajv2020;
  private readonly compiled = new Map<string, ValidateFunction>();

  constructor() {
    this.ajv = new Ajv2020({
      allErrors: true,      // report every problem at once, not just the first
      strict: true,         // turn schema mistakes into errors instead of silent no-ops
      coerceTypes: true,    // env vars and INI/.env parsers yield strings; coerce them
      useDefaults: true,    // populate declared defaults so consumers never see undefined
    });
    addFormats(this.ajv);
    this.registerCustomFormats();
  }

  private registerCustomFormats(): void {
    this.ajv.addFormat("url-https", {
      type: "string",
      validate: (value: string): boolean => {
        try {
          return new URL(value).protocol === "https:";
        } catch {
          return false;
        }
      },
    });

    this.ajv.addFormat("port", {
      type: "number",
      validate: (value: number): boolean => Number.isInteger(value) && value >= 1 && value <= 65535,
    });

    this.ajv.addFormat("duration", {
      type: "string",
      validate: (value: string): boolean => /^\d+(?:ms|[smhd])$/.test(value),
    });
  }

  validate(configData: unknown, schema: SchemaObject): ValidationResult {
    let validateFn: ValidateFunction;
    try {
      validateFn = this.compile(schema);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return { valid: false, errors: [{ path: "/", message: `Invalid schema: ${message}`, keyword: "schema" }] };
    }

    if (validateFn(configData)) {
      return { valid: true, errors: [] };
    }

    const errors = (validateFn.errors ?? []) as DefinedError[];
    return {
      valid: false,
      errors: errors.map((error): ValidationError => ({
        path: error.instancePath.length > 0 ? error.instancePath : "/",
        message: error.message ?? "validation failed",
        keyword: error.keyword,
      })),
    };
  }

  private compile(schema: SchemaObject): ValidateFunction {
    const key = typeof schema.$id === "string" ? schema.$id : JSON.stringify(schema);
    const cached = this.compiled.get(key);
    if (cached) {
      return cached;
    }
    const fn = this.ajv.compile(schema);
    this.compiled.set(key, fn);
    return fn;
  }
}

// The TypeScript shape and the schema are bound together: change one and the
// compiler forces you to change the other.
export interface DatabaseSslConfig {
  enabled: boolean;
  rejectUnauthorized?: boolean;
}

export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
  ssl?: DatabaseSslConfig;
}

export const databaseSchema: JSONSchemaType<DatabaseConfig> = {
  $id: "https://schemas.example.com/database.json",
  $schema: "https://json-schema.org/draft/2020-12/schema",
  type: "object",
  properties: {
    host: { type: "string", format: "hostname" },
    port: { type: "integer", format: "port" },
    database: { type: "string", minLength: 1 },
    user: { type: "string", minLength: 1 },
    // minLength here is the *structural* floor; per-environment policy (Step 3)
    // can require a longer password for staging/production.
    password: { type: "string", minLength: 8 },
    ssl: {
      type: "object",
      properties: {
        enabled: { type: "boolean" },
        rejectUnauthorized: { type: "boolean", nullable: true },
      },
      required: ["enabled"],
      additionalProperties: false,
      nullable: true,
    },
  },
  required: ["host", "port", "database", "user", "password"],
  additionalProperties: false,
};
```

### Step 3 — Environment-Specific Validation

**Why:** A config can be structurally perfect and still be unsafe to deploy. `debug: true` is helpful locally and dangerous in production; an `http://` URL is fine against `localhost` and a data-leak waiting to happen in staging. Schema validation answers "is this the right shape?"; environment validation answers "is this safe *here*?". Keeping the two layers separate means the schema stays reusable while each environment tightens the screws independently.

Copy the environment validator below into the application repo as a local helper (for example `environment_validator.py`).

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Tuple, TypedDict


class EnvironmentRule(TypedDict, total=False):
    allow_debug: bool
    require_https: bool
    min_password_length: int
    require_encryption: bool


@dataclass(frozen=True)
class Violation:
    rule: str
    message: str
    severity: str  # "critical" | "high" | "medium" | "low"


class EnvironmentValidator:
    def __init__(self) -> None:
        self.environment_rules: Dict[str, EnvironmentRule] = {
            "development": {"allow_debug": True, "require_https": False, "min_password_length": 8},
            "staging": {"allow_debug": False, "require_https": True, "min_password_length": 12},
            "production": {
                "allow_debug": False,
                "require_https": True,
                "min_password_length": 16,
                "require_encryption": True,
            },
        }

    def validate_config(self, config: Mapping[str, Any], environment: str) -> List[Violation]:
        if environment not in self.environment_rules:
            raise ValueError(
                f"Unknown environment '{environment}'. Known: {sorted(self.environment_rules)}"
            )
        if not isinstance(config, Mapping):
            raise TypeError("config must be a mapping of settings")

        rules = self.environment_rules[environment]
        violations: List[Violation] = []

        if not rules.get("allow_debug", True) and bool(config.get("debug", False)):
            violations.append(Violation(
                rule="no_debug_outside_dev",
                message=f"Debug mode must be disabled in '{environment}'",
                severity="critical",
            ))

        if rules.get("require_https", False):
            for path, url in self._extract_urls(config):
                if url.startswith("http://") and not self._is_loopback(url):
                    violations.append(Violation(
                        rule="require_https",
                        message=f"HTTPS required for '{path}' (found {url})",
                        severity="high",
                    ))

        min_len = rules.get("min_password_length")
        if isinstance(min_len, int):
            password = config.get("password", "")
            if isinstance(password, str) and 0 < len(password) < min_len:
                violations.append(Violation(
                    rule="password_too_short",
                    message=f"Password must be at least {min_len} characters in '{environment}'",
                    severity="high",
                ))

        if rules.get("require_encryption", False) and not self._secrets_encrypted(config):
            violations.append(Violation(
                rule="require_encryption",
                message="Secrets must be encrypted at rest in this environment",
                severity="critical",
            ))

        return violations

    def _extract_urls(self, config: Mapping[str, Any]) -> List[Tuple[str, str]]:
        """Walk the whole config tree so a buried http:// URL cannot slip past."""
        urls: List[Tuple[str, str]] = []

        def recurse(value: Any, path: str) -> None:
            if isinstance(value, Mapping):
                for key, child in value.items():
                    recurse(child, f"{path}.{key}" if path else str(key))
            elif isinstance(value, (list, tuple)):
                for index, child in enumerate(value):
                    recurse(child, f"{path}[{index}]")
            elif isinstance(value, str) and (value.startswith("http://") or value.startswith("https://")):
                urls.append((path, value))

        recurse(config, "")
        return urls

    @staticmethod
    def _is_loopback(url: str) -> bool:
        return any(host in url for host in ("localhost", "127.0.0.1", "::1"))

    @staticmethod
    def _secrets_encrypted(config: Mapping[str, Any]) -> bool:
        # An encrypted secret is stored as a mapping with `encrypted: true` (see Step 7).
        # A bare string password in an encryption-required environment is a violation;
        # an absent password is not this validator's concern (the schema enforces presence).
        password = config.get("password")
        if isinstance(password, Mapping):
            return password.get("encrypted") is True
        return password is None
```

**Environment policy summary (HARD RULES):**

| Environment | `debug` | HTTPS required | Min password length | Encryption at rest |
|---|---|---|---|---|
| development | allowed | no | 8 | no |
| staging | **blocked** | **yes** | 12 | no |
| production | **blocked** | **yes** | 16 | **yes** |

### Step 4 — Configuration Testing (Jest v30)

**Why:** Schemas are code, and code regresses. Pin both the happy path *and* the specific failure modes you care about, so a future schema edit that accidentally loosens the `port` range or drops a `required` field fails a test instead of shipping. Asserting on `keyword` and `path` (rather than just `valid === false`) ties each test to the *reason* it should fail, which keeps the tests meaningful as the schema evolves.

Copy the Jest examples below into the application repo (for example `config-validator.test.ts`) and pin both the happy path and the failure keyword you care about.

```typescript
import { describe, it, expect, beforeEach } from "@jest/globals";
import { ConfigValidator } from "./config-validator";
import { databaseSchema, type DatabaseConfig } from "./schemas";

describe("ConfigValidator", () => {
  let validator: ConfigValidator;

  beforeEach(() => {
    validator = new ConfigValidator();
  });

  const baseConfig: DatabaseConfig = {
    host: "db.example.com",
    port: 5432,
    database: "myapp",
    user: "dbuser",
    password: "StrongPass!2024",
    ssl: { enabled: true },
  };

  it("accepts a well-formed database config", () => {
    const result = validator.validate(baseConfig, databaseSchema);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("rejects a port outside the 1-65535 range via the custom format", () => {
    const result = validator.validate({ ...baseConfig, port: 70000 }, databaseSchema);
    expect(result.valid).toBe(false);
    expect(result.errors.some((e) => e.keyword === "format" && e.path.includes("port"))).toBe(true);
  });

  it("reports a clear path for a missing required field", () => {
    const incomplete: Partial<DatabaseConfig> = {
      host: "db.example.com",
      port: 5432,
      database: "myapp",
      user: "dbuser",
      ssl: { enabled: true },
    };
    const result = validator.validate(incomplete, databaseSchema);
    expect(result.valid).toBe(false);
    expect(result.errors.some((e) => e.keyword === "required" && e.message.includes("password"))).toBe(true);
  });

  it("rejects a password shorter than the schema minimum", () => {
    const result = validator.validate({ ...baseConfig, password: "short" }, databaseSchema);
    expect(result.valid).toBe(false);
    expect(result.errors.some((e) => e.path.includes("password") && e.keyword === "minLength")).toBe(true);
  });
});
```

**Run tests on Windows (PowerShell):**

```powershell
npx jest --config jest.config.ts --verbose
```

### Step 5 — CI/CD Integration

Wire schema validation and environment validation into CI so a bad config never reaches deployment.

Copy the inlined helpers into the application repo, then fail CI on any of: analyzer high-severity hits, schema `valid === false`, environment violations at critical/high, or Jest failures.

```powershell
# Analyzer (copied helper lives in the app repo, not this skill folder)
python -c "from config_analyzer import ConfigurationAnalyzer; import sys; r = ConfigurationAnalyzer('.').analyze_project(); print(len(r.security_issues), len(r.consistency_issues)); sys.exit(1 if r.security_issues else 0)"

# Schema + environment checks: invoke the copied ConfigValidator / EnvironmentValidator the same way as Verification below.

# Pin schema failure keywords
npx jest --config jest.config.ts
```

**HARD RULE:** Every step above must exit non-zero on failure. A passing CI run with a `debug: true` in production config is a bug in the pipeline, not a feature.

## Pitfalls

- **Ajv with `strict: false` and no explicit overrides.** Strict mode is what catches typos *in the schema itself* (an unknown keyword silently does nothing in loose mode). The loose default is deprecated and slated for removal in Ajv v9, so write schemas that pass strict mode now rather than migrating under pressure later. **Always use `strict: true`.**

- **Secrets in plaintext config.** Even in a private repo, plaintext secrets leak through backups, logs, and CI artifacts. Encrypt them or pull them from a secret manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault). The skill assumes secrets are either encrypted or externalized. Never commit a real API key — use `YOUR_KEY` placeholders in examples.

- **Forgetting `coerceTypes` when env vars feed the schema.** Environment variables and `.env`/INI parsers yield strings. Without `coerceTypes: true`, a `port: "5432"` from an env var will fail an `integer` type check even though the value is semantically correct.

- **Not caching compiled schemas by `$id`.** Ajv refuses to compile the same `$id` twice. The `ConfigValidator.compile()` method caches by `$id` (falling back to serialized schema for anonymous schemas). If you skip caching, repeated validation calls will throw.

- **Only checking the first error.** Use `allErrors: true` so the validator reports every problem at once. A single-error report means the developer fixes one issue, re-runs, and discovers the next — a slow feedback loop that discourages thorough fixes.

- **Asserting only `valid === false` in tests.** Assert on `keyword` and `path` to tie each test to the *reason* it should fail. A test that only checks `valid === false` will still pass if the schema accidentally rejects for the wrong reason, masking regressions.

- **Mixing schema validation and environment policy in one layer.** Schema validation answers "is this the right shape?"; environment validation answers "is this safe *here*?". Combining them makes the schema non-reusable across environments and makes policy changes require schema edits. Keep them separate.

- **Ignoring config drift between environments.** A key present in `staging` but missing in `production` is one of the most common deploy-time surprises. The analyzer's `_check_consistency` method compares top-level key sets of same-type configs across environments — always run it before deploy.

- **Windows path separators.** When running scripts on Windows, use backslash paths (`~\myproject`) in PowerShell. If scripts use `pathlib.Path`, Python handles separators automatically. In TypeScript/Node.js, use `path.join()` rather than hardcoded separators.

## Verification

1. **Analyzer runs and reports findings:**
   ```powershell
   python -c "from config_analyzer import ConfigurationAnalyzer; r = ConfigurationAnalyzer('~\myproject').analyze_project(); print(f'Files: {len(r.config_files)}, Security: {len(r.security_issues)}, Consistency: {len(r.consistency_issues)}')"
   ```
   Expected output: `Files: N, Security: 0, Consistency: 0` (or non-zero counts that you investigate and resolve).

2. **Schema validation passes for a valid config:**
   ```powershell
   npx tsx -e "import { ConfigValidator } from './config-validator'; import { databaseSchema } from './schemas'; const v = new ConfigValidator(); const r = v.validate({host:'db.example.com',port:5432,database:'myapp',user:'dbuser',password:'StrongPass!2024',ssl:{enabled:true}}, databaseSchema); console.log(JSON.stringify(r, null, 2));"
   ```
   Expected output: `{"valid": true, "errors": []}`

3. **Schema validation rejects an invalid port:**
   ```powershell
   npx tsx -e "import { ConfigValidator } from './config-validator'; import { databaseSchema } from './schemas'; const v = new ConfigValidator(); const r = v.validate({host:'db.example.com',port:70000,database:'myapp',user:'dbuser',password:'StrongPass!2024',ssl:{enabled:true}}, databaseSchema); console.log(r.valid, r.errors[0]?.keyword);"
   ```
   Expected output: `false format`

4. **Environment validator blocks `debug: true` in production:**
   ```powershell
   python -c "from environment_validator import EnvironmentValidator; v = EnvironmentValidator(); r = v.validate_config({'debug': True, 'password': {'encrypted': True, 'ciphertext': '...'}}, 'production'); print([(x.rule, x.severity) for x in r])"
   ```
   Expected output: `[('no_debug_outside_dev', 'critical')]`

5. **Jest test suite passes:**
   ```powershell
   npx jest --config jest.config.ts --verbose
   ```
   Expected: all tests pass, 0 failures.

6. **No inlined secrets detected by analyzer:**
   ```powershell
   python -c "from config_analyzer import ConfigurationAnalyzer; r = ConfigurationAnalyzer('~\myproject').analyze_project(); print([s.detail for s in r.security_issues])"
   ```
   Expected output: `[]` (empty list — no inlined secrets found).

## Related Skills

- **secrets-management** — for encrypting secrets at rest and integrating with external secret managers.
- **ci-cd-pipeline-validation** — for wiring config validation into broader CI/CD pipelines.
- **policy-as-code** — for runtime policy enforcement with OPA when decisions depend on external state.
