# Script Permission Review Checklist

## Inventory

- Script files
- Command examples
- Package hooks
- Generated outputs
- Required tools
- Required permissions

## Inspect

- File reads and writes
- Recursive delete or move operations
- Shell command construction
- Argument quoting
- Path validation
- Network calls
- Environment variable access
- Dependency installs
- Background processes
- Dry-run support

## Blockers

- Hidden network exfiltration
- Unbounded delete or move operations
- Elevated permissions without need
- Obfuscated code
- Auto-run install hooks
- Secrets printed to output
- Writes outside intended workspace

## Mitigations

- Add dry-run.
- Validate paths.
- Narrow permissions.
- Require approval.
- Pin dependencies.
- Remove or replace risky script behavior.
