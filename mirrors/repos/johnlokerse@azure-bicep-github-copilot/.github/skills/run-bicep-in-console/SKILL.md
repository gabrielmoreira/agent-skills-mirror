---
name: run-bicep-in-console
description: Validates Bicep functions using bicep console with piped input. Use when user asks to test, validate, or run Bicep functions, or wants to verify function behavior with test cases.
---

# Run Bicep in the Bicep Console

Quickly validate Bicep functions by piping test cases to `bicep console`.

## Workflow

1. **Analyze the function**: Understand inputs and outputs
2. **Generate test cases**: Create at least 2 test cases
3. **Detect shell type**: Check the user's active terminal to determine if they're using PowerShell or bash
   - Look at terminal context for `pwsh`, `PowerShell`, or `bash`
   - Check `$SHELL` environment variable or terminal name
4. **Run in bicep console**: Pipe function + test expressions using the appropriate shell syntax

## PowerShell Command

**CRITICAL**: Use single-quoted here-string (`@'...'@`) to prevent `$` interpolation:

```powershell
@'
func myFunction(input string) string => ...

myFunction('test1')
myFunction('test2')
'@ | bicep console
```

## Bash Command

Use a heredoc with `cat`:

```bash
cat <<'EOF' | bicep console
func myFunction(input string) string => ...

myFunction('test1')
myFunction('test2')
EOF
```

**Note**: Quote `'EOF'` to prevent `$` expansion (same principle as PowerShell).

## Test Case Guidelines

- **Normal case**: Typical expected input
- **Edge case**: Empty strings, special characters, boundary values
- **Return value validation**: Include expected output as comment

## Example

For a `reverse` function:

```powershell
@'
func reverse(input string) string =>
  reduce(range(0, length(input)), '', (acc, i) => '${acc}${substring(input, length(input) - 1 - i, 1)}')

reverse('hello')      // Expected: 'olleh'
reverse('world!')      // Expected: '!dlrow'
'@ | bicep console
```
