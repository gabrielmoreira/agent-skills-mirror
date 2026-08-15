---
name: postman-newman-automation
description: "Emits Newman CLI invocations, PowerShell or bash runners, and Jenkins/GitHub Actions stages for exported Postman collections, including CSV iteration data and JUnit/htmlextra reporters. Trigger on newman, postman cli, collection CI, or data-driven API suites. Do not use for Postman GUI collection authoring, the Postman CLI binary, Bruno/Insomnia clients, or Pact contract tests."
version: 1.0.1
risk: unknown
source: https://github.com/LambdaTest/agent-skills/tree/main/api-skill/postman/postman-to-newman
source_repo: LambdaTest/agent-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/LambdaTest/agent-skills/blob/main/LICENSE
---

# Postman Newman Automation

## Overview

Newman is the command-line collection runner for Postman. This skill generates ready-to-run Newman CLI commands, reusable shell scripts, and Jenkins pipeline configurations for automated API test execution in local or CI/CD environments. It covers basic runs, data-driven iterations, environment variable overrides, reporter selection, and CI integration patterns.

## When to Use

Use this skill when the user needs to:

- **Run Postman collections from the command line** (local or CI)
- **Automate API test suites** with Newman
- **Integrate Postman tests into Jenkins** (declarative or scripted pipelines)
- **Generate Newman shell scripts** with exit-code handling and report archiving
- **Produce JUnit XML or HTML reports** for CI consumption
- **Run data-driven tests** using CSV or JSON iteration data
- **Override environment variables inline** without an environment file

Trigger keywords: *newman, postman cli, run postman collection, api test automation, jenkins postman, newman reporter, htmlextra, junit postman, postman ci/cd*

## Prerequisites

1. **Node.js ≥ 14** installed and on PATH.
2. **Newman installed globally:**
   ```powershell
   npm install -g newman
   ```
3. **Optional reporters** (install only if the user requests HTML or custom reports):
   ```powershell
   npm install -g newman-reporter-htmlextra
   ```
4. **Postman collection file** (exported JSON) or a Postman API UID with a valid API key.
5. **Environment file** (optional) — exported from Postman as JSON.
6. On **Windows (PowerShell)**, line continuations use backtick (`` ` ``) instead of backslash (`\`). All bash examples below are for CI/Linux runners; see the PowerShell note in Step 2 for local Windows execution.

## Procedure

### Step 1 — Gather Requirements

Ask or infer from context before generating any command:

| Parameter | Question | Example |
|---|---|---|
| Collection source | File path, URL, or Postman API UID? | `./collection.json` or UID `12345-abcde` |
| Environment | File path or inline variables? | `./environment.json` or `--env-var` |
| Reporter(s) | CLI only, HTML, JUnit XML, JSON? | `cli,htmlextra,junit` |
| Fail behavior | Stop on first failure or run all? | `--bail` or omit |
| Iterations | Single run or data-driven (CSV/JSON)? | `--iteration-data data.csv` |
| Target | Local shell, Jenkins, or both? | `run-tests.sh` or `Jenkinsfile` |

### Step 2 — Generate the Newman Command

#### Basic local run (Linux/macOS / CI runner)

```bash
newman run collection.json \
  --environment environment.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export reports/report.html \
  --bail
```

#### Basic local run (Windows PowerShell)

```powershell
newman run collection.json `
  --environment environment.json `
  --reporters cli,htmlextra `
  --reporter-htmlextra-export reports/report.html `
  --bail
```

> **Windows note:** Create the `reports` directory before running:
> ```powershell
> New-Item -ItemType Directory -Force -Path reports
> ```

#### Run from Postman API (by UID)

```bash
newman run "https://api.getpostman.com/collections/<UID>?apikey={{POSTMAN_API_KEY}}" \
  --environment environment.json \
  --reporters cli,junit \
  --reporter-junit-export results/junit.xml
```

Replace `<UID>` with the collection UID and `{{POSTMAN_API_KEY}}` with a valid Postman API key (e.g., `YOUR_POSTMAN_API_KEY`). Never hardcode live keys in committed files — use environment variables or CI secret injection.

#### Data-driven run (CSV)

```bash
newman run collection.json \
  --iteration-data test-data.csv \
  --iteration-count 5 \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export reports/data-driven-report.html
```

#### Inline environment variable overrides (no file needed)

```bash
newman run collection.json \
  --env-var "base_url=https://staging.api.example.com" \
  --env-var "token=YOUR_TOKEN" \
  --reporters cli
```

### Step 3 — Generate a Reusable Shell Script

Produce a `run-tests.sh` for Linux/CI runners:

```bash
#!/bin/bash
set -e

# Configuration
COLLECTION="./collection.json"
ENVIRONMENT="./environment.json"
REPORT_DIR="./reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Ensure report directory exists
mkdir -p "$REPORT_DIR"

echo "Running Newman collection: $COLLECTION"

newman run "$COLLECTION" \
  --environment "$ENVIRONMENT" \
  --reporters cli,htmlextra,junit \
  --reporter-htmlextra-export "$REPORT_DIR/report_$TIMESTAMP.html" \
  --reporter-junit-export "$REPORT_DIR/junit_$TIMESTAMP.xml" \
  --timeout-request 10000 \
  --bail

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ All tests passed."
else
  echo "❌ Tests failed. Check report: $REPORT_DIR/report_$TIMESTAMP.html"
  exit $EXIT_CODE
fi
```

For Windows PowerShell, generate a `run-tests.ps1` equivalent:

```powershell
$ErrorActionPreference = "Stop"

$Collection = ".\collection.json"
$Environment = ".\environment.json"
$ReportDir = ".\reports"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

Write-Host "Running Newman collection: $Collection"

newman run $Collection `
  --environment $Environment `
  --reporters cli,htmlextra,junit `
  --reporter-htmlextra-export "$ReportDir\report_$Timestamp.html" `
  --reporter-junit-export "$ReportDir\junit_$Timestamp.xml" `
  --timeout-request 10000 `
  --bail

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed."
} else {
    Write-Host "❌ Tests failed. Check report: $ReportDir\report_$Timestamp.html"
    exit $LASTEXITCODE
}
```

### Step 4 — Generate a Jenkins Pipeline

#### Declarative Jenkinsfile (preferred)

```groovy
pipeline {
  agent any

  environment {
    POSTMAN_ENV = credentials('postman-environment-file') // Jenkins credential ID
  }

  stages {
    stage('Install Newman') {
      steps {
        sh 'npm install -g newman newman-reporter-htmlextra'
      }
    }

    stage('Run API Tests') {
      steps {
        sh """
          newman run collection.json \
            --environment ${POSTMAN_ENV} \
            --reporters cli,htmlextra,junit \
            --reporter-htmlextra-export reports/report.html \
            --reporter-junit-export reports/junit.xml \
            --timeout-request 10000 \
            --bail
        """
      }
    }
  }

  post {
    always {
      publishHTML(target: [
        allowMissing: false,
        alwaysLinkToLastBuild: true,
        keepAll: true,
        reportDir: 'reports',
        reportFiles: 'report.html',
        reportName: 'Newman API Test Report'
      ])
      junit 'reports/junit.xml'
    }
    failure {
      echo 'API tests failed! Check the Newman report.'
    }
  }
}
```

#### Scripted Jenkinsfile (if declarative is not available)

```groovy
node {
  stage('Install Newman') {
    sh 'npm install -g newman newman-reporter-htmlextra'
  }

  stage('Run API Tests') {
    try {
      sh """
        newman run collection.json \
          --environment environment.json \
          --reporters cli,junit \
          --reporter-junit-export reports/junit.xml \
          --bail
      """
    } catch (err) {
      currentBuild.result = 'FAILURE'
      throw err
    } finally {
      junit 'reports/junit.xml'
    }
  }
}
```

#### Jenkins with inline environment variables (no credentials file)

```groovy
environment {
  BASE_URL = 'https://api.example.com'
  API_TOKEN = credentials('api-token-secret')
}

steps {
  sh """
    newman run collection.json \
      --env-var "base_url=${BASE_URL}" \
      --env-var "token=${API_TOKEN}" \
      --reporters cli,junit \
      --reporter-junit-export results/junit.xml
  """
}
```

### Step 5 — Select Reporters

| Reporter | Install | Flag | Output |
|---|---|---|---|
| `cli` | built-in | `--reporters cli` | Terminal output |
| `junit` | built-in | `--reporters junit` | JUnit XML (for Jenkins/GitHub Actions) |
| `htmlextra` | `npm i -g newman-reporter-htmlextra` | `--reporters htmlextra` | Rich HTML report |
| `json` | built-in | `--reporters json` | Raw JSON results |

Combine multiple reporters: `--reporters cli,htmlextra,junit`

### Step 6 — Deliver Output

Provide the following based on what the user needs:

1. **Newman command** — ready to paste in terminal (bash or PowerShell as appropriate)
2. **Shell script** (`run-tests.sh` or `run-tests.ps1`) — with exit-code handling
3. **Jenkinsfile** — declarative or scripted based on context
4. **Setup notes** — Node.js version requirement (≥14), npm install commands
5. **Report locations** — where output files will be written

### Common Flags Quick Reference

| Flag | Purpose |
|---|---|
| `--bail` | Stop run on first test failure |
| `--timeout-request 5000` | Per-request timeout in ms |
| `--delay-request 200` | Delay between requests in ms |
| `--iteration-count 3` | Run collection N times |
| `--folder "Folder Name"` | Run only a specific folder |
| `--env-var "k=v"` | Inline environment variable |
| `--suppress-exit-code` | Always exit 0 (don't fail CI) |
| `--verbose` | Show full request/response details |
| `--color off` | Disable color (useful for log files) |

## Pitfalls

1. **Missing report directory** — Newman does not create output directories. Always `mkdir -p reports` (Linux) or `New-Item -ItemType Directory -Force -Path reports` (PowerShell) before running.
2. **htmlextra not installed** — If `--reporters htmlextra` is used but `newman-reporter-htmlextra` is not installed globally, Newman will error. Install it first: `npm install -g newman-reporter-htmlextra`.
3. **Windows line continuation** — PowerShell uses backtick (`` ` ``), not backslash (`\`). Mixing these causes parse errors. Bash examples are for Linux/macOS/CI runners only.
4. **Postman API key exposure** — Never commit `apikey=` in a repository. Use environment variables (`POSTMAN_API_KEY`) or CI secret injection (Jenkins `credentials()`).
5. **`--bail` hides later failures** — When `--bail` is set, only the first failure is reported. Remove it if the user wants a full failure summary.
6. **`set -e` with exit-code capture** — In the shell script, `set -e` will exit before the `EXIT_CODE=$?` line if Newman fails. Either remove `set -e` or capture the exit code with `set +e` before the Newman call and `set -e` after.
7. **Node.js version too old** — Newman requires Node.js ≥ 14. Older versions will fail with cryptic module errors. Verify with `node --version`.
8. **Jenkins `publishHTML` plugin missing** — The `publishHTML` step requires the HTML Publisher plugin. If it is not installed, the pipeline will fail at the `post` block. Use `junit` alone as a fallback.
9. **CSV encoding** — Iteration data CSV files must be UTF-8 encoded. Excel may export as UTF-8 with BOM, which can cause parsing issues. Re-save as plain UTF-8 if errors occur.
10. **`--suppress-exit-code` in CI** — Using this flag means Newman always exits 0, so CI will never fail on test failures. Only use it when you want to collect reports without gating the build.

## Verification

After generating commands or scripts, verify correctness with these checks:

1. **Newman is installed and on PATH:**
   ```powershell
   newman --version
   ```
   Expected: a version number (e.g., `6.x.x`).

2. **htmlextra reporter is installed (if used):**
   ```powershell
   npm list -g newman-reporter-htmlextra
   ```
   Expected: the package listed with a version.

3. **Collection file is valid JSON:**
   ```powershell
   node -e "JSON.parse(require('fs').readFileSync('collection.json','utf8')); console.log('Valid JSON')"
   ```
   Expected: `Valid JSON`.

4. **Dry run — execute the generated command against a small or test collection:**
   ```bash
   newman run collection.json --reporters cli --bail
   ```
   Expected: summary table showing total/failures, exit code 0 if all pass.

5. **Report files were created:**
   ```powershell
   Test-Path reports/report.html
   Test-Path reports/junit.xml
   ```
   Expected: `True` for each.

6. **Jenkinsfile syntax validation (if pipeline generated):**
   Use Jenkins' Replay or `jenkinsfile-runner`, or validate via the Jenkins UI **Pipeline Syntax > Declarative Directive Generator**. At minimum, confirm Groovy compiles without syntax errors.

7. **Exit code reflects test results:**
   ```powershell
   newman run collection.json --reporters cli; echo "Exit code: $LASTEXITCODE"
   ```
   Expected: `0` when all tests pass, non-zero when failures exist (unless `--suppress-exit-code` is used).

## Related Skills

- **API Documentation** — After generating Newman automation, ask the user: *"Would you like me to generate API documentation for this collection?"* If yes and the API Documentation skill is installed, follow that skill's instructions using the collection as input. If not installed, inform the user they can install it and re-run.

## Limitations

- Use this skill only when the task clearly matches Newman/Postman CLI automation.
- Verify all generated commands, dependencies, credentials, and external service behavior before applying changes in production.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- No live secrets are included in this skill; all API keys and tokens are placeholders (e.g., `YOUR_POSTMAN_API_KEY`, `YOUR_TOKEN`).
