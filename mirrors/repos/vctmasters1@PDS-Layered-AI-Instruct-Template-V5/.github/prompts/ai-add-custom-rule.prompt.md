---
mode: agent
description: Interactive builder for custom compliance rules
---

# /ai-add-custom-rule — Add Custom Compliance Rule

Add a new custom compliance rule to your project in interactive mode.

## What is a Custom Rule?

Custom rules let your project enforce standards beyond the AI-INSTRUCT framework. Examples:

- **Python docstrings**: Enforce module docstrings in specific directories
- **API organization**: Require route files to be in a specific location
- **Security checks**: Scan for hardcoded secrets or credentials
- **Type hints**: Encourage or require type annotations
- **Custom patterns**: Any project-specific convention

## Quick Start

```powershell
python .ai/engine/add_custom_rule.py
```

Or let the AI guide you:

> "I want to add a rule that [your requirement]"

The prompt will:
1. Show available rule templates
2. Let you customize the rule
3. Show YAML preview
4. Save to `.ai/compliance-rules.yaml`

## Example: Enforce API Route Organization

```
1. Select rule type: api_organization
2. Rule ID: api_routes_in_correct_location
3. Description: All API routes must be in api/routes/ directory
4. Severity: error
5. Review preview
6. Save
```

Result: `.ai/compliance-rules.yaml` now has your rule. Run Phase 1 analyzer to check for violations.

## Available Templates

### 1. Python Docstrings
- **Pattern**: `all_python_files_must_have_module_docstring`
- **Checks**: Every `.py` file starts with a docstring
- **Customizable**: paths, exclude patterns, severity

### 2. API Organization
- **Pattern**: `api_routes_must_be_in_api_routes_dir`
- **Checks**: Route/endpoint files in correct location
- **Severity**: error (prevents misorganization)

### 3. Hardcoded Secrets
- **Pattern**: `no_hardcoded_secrets_in_code`
- **Checks**: Regex scan for `api_key=`, `password=`, `token=`, etc.
- **Customizable**: file extensions, severity
- **Use**: Pre-commit security gate

### 4. Type Hints
- **Pattern**: `python_functions_must_have_type_hints`
- **Checks**: Python functions have `->` return type
- **Severity**: warning (optional enforcement)
- **Customizable**: paths to enforce in

### 5. Custom
- **Pattern**: You define it
- **Use**: For your own regex or validation logic

## Workflow

### Step 1: Add Rule

```powershell
python .ai/engine/add_custom_rule.py
```

Walk through the prompts. Your rule is saved to `.ai/compliance-rules.yaml`.

### Step 2: Test Rule

Run the analyzer to check for violations:

```powershell
pwsh .github/debug/import-project.ps1 -Phase analyze -ProjectPath .
```

Your custom rule violations will appear in the report.

### Step 3: Integrate (Optional)

Import tool can check custom rules alongside standard violations:

```powershell
pwsh .github/debug/import-project.ps1 -Phase fix -ProjectPath . -Mode auto
```

## Example `.ai/compliance-rules.yaml`

Your custom rules go in `.ai/compliance-rules.yaml` (gitignored, created on first use).

Here's an example of what it looks like once you add rules:

```yaml
rules:
  no_db_hardcodes:
    enabled: true
    pattern: "no_hardcoded_secrets_in_code"
    description: "Prevent database credentials in code"
    severity: "error"
    scan_extensions: [".py", ".js"]

  api_routes_organized:
    enabled: true
    pattern: "api_routes_must_be_in_api_routes_dir"
    description: "Keep all routes in api/routes/"
    severity: "error"

  py_docstrings:
    enabled: false
    pattern: "all_python_files_must_have_module_docstring"
    description: "All modules should have docstrings"
    severity: "warning"
    paths: ["src/"]
```

## Troubleshooting

**Rule not running**: Check `enabled: true` in YAML.

**False positives**: Adjust regex patterns or `exclude` list.

**Can't find violations**: Run analyzer with `-ProjectPath .` and check output.

## See Also

- [.ai/compliance-rules.example.yaml](../../.ai/compliance-rules.example.yaml) — Template for custom rules
- [.ai/engine/custom_rules_validator.py](../../.ai/engine/custom_rules_validator.py) — How rules are validated
- `/ai-onboard` (import path) — Integrate rules into project adoption workflow
