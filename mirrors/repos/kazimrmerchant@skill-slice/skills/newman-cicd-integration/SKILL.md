---
name: newman-cicd-integration
description: "Generates CI pipeline YAML/Groovy that installs Newman, runs Postman collections with JUnit/HTML reporters, and publishes artifacts on GitHub Actions, GitLab CI, Jenkins, Azure DevOps, or CircleCI. Use when moving Newman/Postman API tests into CI. Not for authoring Postman collections, local newman run without a pipeline, or Playwright/browser E2E."
version: 1.0.1
risk: unknown
source: https://github.com/LambdaTest/agent-skills/tree/main/api-skill/newman/newman-cicd-helper
source_repo: LambdaTest/agent-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/LambdaTest/agent-skills/blob/main/LICENSE
---

# Newman CI/CD Integration Generator

## Overview

This skill generates complete, copy-paste-ready CI/CD pipeline configurations that install Newman and run Postman collections as part of automated builds. It supports GitHub Actions, GitLab CI, Jenkins (Declarative Pipeline), Azure DevOps, and CircleCI. Each generated config includes Newman installation, test execution with JUnit and HTML reporters, artifact publishing, and secret injection patterns specific to the target platform.

## When to Use

Use this skill when the user needs to:

- Run Newman in a CI pipeline for automated API testing
- Integrate Postman collections into automated builds
- Set up API tests in GitHub Actions, GitLab CI, Jenkins, Azure DevOps, or CircleCI
- Generate pipeline configs that publish Newman test results to CI dashboards
- Migrate manual Newman runs into a CI/CD workflow

**Trigger keywords:** Newman CI, Newman pipeline, Postman CI/CD, API testing pipeline, Newman GitHub Actions, Newman GitLab, Newman Jenkins, Newman Azure DevOps, Newman CircleCI, automated API tests, Postman collection automation.

## Prerequisites

1. **Node.js 18+** available in the CI runner image (or installable via the platform's setup action/task).
2. **Newman** installed globally (`npm install -g newman`).
3. **newman-reporter-htmlextra** installed globally (`npm install -g newman-reporter-htmlextra`) if HTML reports are needed.
4. **Postman collection JSON file** stored in the repository (e.g., `./collections/my-api.json`) or accessible via a Postman API URL.
5. **Environment JSON file** stored in the repository (e.g., `./environments/staging.json`) with non-secret values. Sensitive values must be injected via CI secrets — never committed to the repo.
6. **CI secrets configured** on the target platform for any credentials the collection requires (e.g., `API_KEY`, `BASE_URL`).

### Recommended repository structure

```
/
├── collections/
│   └── my-api.json
├── environments/
│   ├── staging.json
│   └── prod.json
└── results/         ← gitignored, created by Newman at runtime
```

Add `results/` to `.gitignore`:

```gitignore
results/
```

## Procedure

### Step 1 — Collect requirements from the user

Before generating any config, confirm the following with the user:

1. **CI platform** — GitHub Actions, GitLab CI, Jenkins, Azure DevOps, CircleCI, or Bitbucket?
2. **Collection source** — local file in the repo, or Postman API URL?
3. **Environment** — local env file in the repo, or env vars injected entirely by CI secrets?
4. **Reporters needed** — JUnit XML (for CI test results panel), HTML report, or both?
5. **Node.js version** preference (default: 18).
6. **Trigger** — on every push, pull request, schedule, or after deploy?
7. **Fail build on test failure?** — almost always yes; confirm.

### Step 2 — Select the platform template

Choose the matching template below and tailor the exact syntax for the user's CI platform. Use the correct secret/variable injection syntax for that platform. Include artifact publishing steps so test results appear in the CI UI. Add comments explaining which secrets need to be configured.

---

### GitHub Actions

```yaml
name: API Tests

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  api-tests:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install Newman
        run: |
          npm install -g newman
          npm install -g newman-reporter-htmlextra

      - name: Run API tests
        run: |
          newman run ./collections/my-api.json \
            -e ./environments/staging.json \
            -r cli,junit,htmlextra \
            --reporter-junit-export ./results/junit.xml \
            --reporter-htmlextra-export ./results/report.html \
            --reporter-htmlextra-title "API Test Results"
        env:
          BASE_URL: ${{ secrets.BASE_URL }}
          API_KEY: ${{ secrets.API_KEY }}

      - name: Publish test results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Newman API Tests
          path: results/junit.xml
          reporter: java-junit

      - name: Upload HTML report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: api-test-report
          path: results/report.html
```

**Secrets to configure:** `Settings > Secrets and Variables > Actions` — set `BASE_URL` and `API_KEY`.

---

### GitLab CI

```yaml
stages:
  - test

api-tests:
  stage: test
  image: node:18-alpine
  before_script:
    - npm install -g newman newman-reporter-htmlextra
  script:
    - |
      newman run ./collections/my-api.json \
        -e ./environments/staging.json \
        --env-var "BASE_URL=$BASE_URL" \
        --env-var "API_KEY=$API_KEY" \
        -r cli,junit,htmlextra \
        --reporter-junit-export results/junit.xml \
        --reporter-htmlextra-export results/report.html
  artifacts:
    when: always
    reports:
      junit: results/junit.xml
    paths:
      - results/report.html
    expire_in: 7 days
  variables:
    BASE_URL: $BASE_URL   # Set in GitLab CI/CD > Variables
    API_KEY: $API_KEY
```

**Secrets to configure:** `Settings > CI/CD > Variables` — set `BASE_URL` and `API_KEY` as masked variables.

---

### Jenkins (Declarative Pipeline)

```groovy
pipeline {
  agent any

  tools {
    nodejs 'NodeJS-18'   // Configure in Global Tool Configuration
  }

  stages {
    stage('Install Newman') {
      steps {
        sh 'npm install -g newman newman-reporter-htmlextra'
      }
    }

    stage('Run API Tests') {
      steps {
        sh '''
          newman run ./collections/my-api.json \
            -e ./environments/staging.json \
            -r cli,junit,htmlextra \
            --reporter-junit-export results/junit.xml \
            --reporter-htmlextra-export results/report.html \
            --reporter-htmlextra-title "API Tests - ${BUILD_NUMBER}"
        '''
      }
    }
  }

  post {
    always {
      junit 'results/junit.xml'
      publishHTML([
        allowMissing: false,
        alwaysLinkToLastBuild: true,
        keepAll: true,
        reportDir: 'results',
        reportFiles: 'report.html',
        reportName: 'Newman API Test Report'
      ])
    }
  }
}
```

**Secrets to configure:** `Manage Jenkins > Credentials` — store `API_KEY` and reference via `withCredentials([...])` if needed. Ensure the HTML Publisher plugin is installed for `publishHTML`.

---

### Azure DevOps

```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: NodeTool@0
    inputs:
      versionSpec: '18.x'
    displayName: 'Set up Node.js'

  - script: |
      npm install -g newman newman-reporter-htmlextra
    displayName: 'Install Newman'

  - script: |
      newman run ./collections/my-api.json \
        -e ./environments/staging.json \
        --env-var "API_KEY=$(API_KEY)" \
        -r cli,junit,htmlextra \
        --reporter-junit-export $(System.DefaultWorkingDirectory)/results/junit.xml \
        --reporter-htmlextra-export $(System.DefaultWorkingDirectory)/results/report.html
    displayName: 'Run API Tests'
    env:
      API_KEY: $(API_KEY)   # Set in Pipeline > Variables

  - task: PublishTestResults@2
    condition: always()
    inputs:
      testResultsFormat: 'JUnit'
      testResultsFiles: 'results/junit.xml'
      testRunTitle: 'Newman API Tests'

  - task: PublishBuildArtifacts@1
    condition: always()
    inputs:
      PathtoPublish: 'results/report.html'
      ArtifactName: 'api-test-report'
```

**Secrets to configure:** `Pipelines > Variables` — set `API_KEY` as a secret variable.

---

### CircleCI

```yaml
version: 2.1

jobs:
  api-tests:
    docker:
      - image: cimg/node:18.0
    steps:
      - checkout
      - run:
          name: Install Newman
          command: npm install -g newman newman-reporter-htmlextra
      - run:
          name: Run API Tests
          command: |
            mkdir -p results
            newman run ./collections/my-api.json \
              -e ./environments/staging.json \
              --env-var "API_KEY=$API_KEY" \
              -r cli,junit,htmlextra \
              --reporter-junit-export results/junit.xml \
              --reporter-htmlextra-export results/report.html
      - store_test_results:
          path: results
      - store_artifacts:
          path: results/report.html

workflows:
  test:
    jobs:
      - api-tests
```

**Secrets to configure:** `Project Settings > Environment Variables` — set `API_KEY`.

### Step 3 — Apply best practices to the generated config

1. **Never hardcode credentials.** Always inject sensitive values as CI environment variables/secrets. Reference in Newman via `--env-var "KEY=$SECRET_NAME"` or pre-set in the environment file.
2. **Store collection and environment files in the repo** (without secrets). Inject sensitive values via CI vars.
3. **Always use `if: always()` / `when: always` / `condition: always()` / `artifacts: when: always`** so test result artifacts are published even when Newman exits with a failure code.
4. **Exit codes:** Newman exits with code `1` if any tests fail — this automatically fails the pipeline step. Use `--bail` if you want to stop on the first failure rather than running all tests.
5. **Add comments** to the generated config explaining which secrets need to be configured and where.

### Step 4 — Deliver the config and offer follow-up

Once the Newman CI/CD config is delivered, ask the user:

> "Would you like me to generate Postman Test Cases for these commands? (yes/no)"

- If **yes**: Check if the `postman-testcase-generator` skill is available in the installed skills list.
  - If available: Read and follow the instructions in the `postman-testcase-generator` skill. Use the CI/CD command output above as the input.
  - If not available: Inform the user: "It looks like the postman-testcase-generator skill isn't installed. You can install it and re-run."
- If **no**: End the task here.

## Pitfalls

- **Hardcoded secrets in env files:** Never commit API keys, tokens, or passwords to the repository. Use CI platform secrets and inject via `--env-var`. Environment JSON files in the repo should contain only non-sensitive configuration (e.g., variable names with placeholder values).
- **Missing `if: always()` on artifact publishing:** If the publish step only runs on success, you lose test results exactly when tests fail — the time you need them most. Always set the publish/upload step to run unconditionally.
- **Jenkins `publishHTML` requires HTML Publisher plugin:** If the plugin is not installed, the `publishHTML` step will fail. Verify the plugin is installed before using that step.
- **Jenkins `tools { nodejs 'NodeJS-18' }` requires pre-configuration:** The NodeJS tool must be configured in `Global Tool Configuration` with the exact name `NodeJS-18` (or update the name in the pipeline to match).
- **GitLab `node:18-alpine` may lack build tools:** If `newman-reporter-htmlextra` fails to install on Alpine, switch to `node:18` (full Debian image) or install build dependencies first.
- **CircleCI `store_test_results` expects a directory:** The `path` should point to the directory containing `junit.xml`, not the file itself.
- **Azure DevOps `$(System.DefaultWorkingDirectory)` path:** Always use this variable for output paths so the PublishTestResults and PublishBuildArtifacts tasks can find the files regardless of agent OS.
- **Newman exit code 1 on test failure:** This is expected behavior and will fail the pipeline step. Do not wrap the Newman command in logic that suppresses the exit code unless you intentionally want the build to pass despite test failures.
- **`--bail` changes behavior:** Using `--bail` stops execution on the first failure. Only add it if the user explicitly wants early termination; otherwise omit it so all tests run and the full report is generated.
- **Windows local testing (PowerShell):** When testing Newman locally on a Windows host before pushing to CI, use PowerShell backtick line continuation or run the command on a single line. The backslash (`\`) line continuation in the CI configs above is for Linux runners only.

## Verification

After generating and applying a config, verify correctness with these checks:

1. **Validate YAML syntax (for YAML-based platforms):**

   ```powershell
   # GitHub Actions / GitLab CI / Azure DevOps / CircleCI
   # Use a local YAML linter or the platform's built-in validator
   npx --yes yaml-lint .github/workflows/api-tests.yml
   ```

   For GitHub Actions specifically, use `actionlint`:

   ```powershell
   # Install actionlint (Windows PowerShell via scoop)
   scoop install actionlint
   actionlint .github/workflows/api-tests.yml
   ```

2. **Test Newman locally before pushing:**

   ```powershell
   npm install -g newman newman-reporter-htmlextra
   mkdir results
   newman run ./collections/my-api.json -e ./environments/staging.json -r cli,junit,htmlextra --reporter-junit-export ./results/junit.xml --reporter-htmlextra-export ./results/report.html
   ```

   Expected: Newman runs all requests, prints test results to console, and creates `results/junit.xml` and `results/report.html`. Exit code is `0` if all tests pass, `1` if any fail.

3. **Verify JUnit XML is well-formed:**

   ```powershell
   # Quick check that the XML file exists and is parseable
   [xml]$xml = Get-Content ./results/junit.xml
   $xml.testsuites.testsuite | Format-Table name, tests, failures, errors
   ```

4. **Verify CI secrets are referenced, not hardcoded:**

   ```powershell
   # Search the generated config for any literal API keys or tokens
   Select-String -Path .github/workflows/api-tests.yml -Pattern "YOUR_KEY|sk-|Bearer " -AllMatches
   ```

   Expected: No matches for real key patterns. Only placeholder references like `${{ secrets.API_KEY }}` should appear.

5. **After pushing, check the CI pipeline:**

   - Confirm the pipeline triggers on the expected event (push/PR/schedule).
   - Confirm the Newman step runs and produces test output.
   - Confirm the test results appear in the CI UI (GitHub Actions test reporter, GitLab merge request, Jenkins test results, Azure DevOps Tests tab, CircleCI Test Insights).
   - Confirm the HTML report artifact is downloadable.

## Related skills

- **postman-testcase-generator** — Generate Postman test cases for API endpoints. Offered as a follow-up after delivering CI/CD configs.
- **newman-cli** — For local Newman execution patterns and CLI flag reference.

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
- Generated configs target Linux CI runners by default. For Windows-based runners, adjust path separators and line continuation characters accordingly.
