---
name: deduplicate-bicep-parameters
description: Checks user-supplied Bicep parameter files for duplicate values, moves safe shared parameters into `base.bicepparam`, and adds `extends` inheritance. Use when asked to find, check, deduplicate, consolidate, or share values across `.bicepparam` files.
---

# Deduplicate Bicep parameter files

Check user-supplied `*.bicepparam` files for duplicate parameter values, move safe shared values to `base.bicepparam`, and make the supplied files inherit from it with `extends`.

## Scope

- Process only the parameter files explicitly supplied by the user.
- If no files were supplied, ask the user to provide them.
- Do not search for or modify other `*.bicepparam` files.

## Workflow

1. Read every supplied file completely.
2. Build each file before editing:

   ```bash
   bicep build-params <file> --outfile <temporary-file>
   ```

3. Stop if any file does not build.
4. Compare parameters by name, resolved value, and value type.
   - Sort object keys recursively before comparison.
   - Preserve array order.
5. Report every duplicate value and the files containing it.
6. Move eligible shared assignments to `base.bicepparam`.
7. Add an `extends` statement to each supplied file.
8. Build all supplied files again and confirm their resolved parameters are unchanged.

## Selecting base values

A parameter can be moved only when:

- It exists in every supplied file.
- At least two supplied files resolve it to the same value.
- One value is shared by all files or is the unique most common value.
- Its expression is self-contained and safe to evaluate from the base file.
- Moving it does not change any resolved parameter value.

Use the shared or unique most common value in the base file. Remove matching assignments from derived files and retain different values as explicit overrides.

Do not move a parameter when:

- The most common value is tied.
- It is missing from a supplied file.
- It uses local variables, imports, `externalInput`, or `getSecret`.
- A supplied file already extends a different base file.
- Moving it changes the compiled parameters.

## Base file

Create or update `base.bicepparam` next to the supplied files:

```bicep
using none

param location = 'westeurope'
```

If the supplied files are in different directories, ask where to place the shared base file.

When `base.bicepparam` already exists:

- Preserve its assignments and comments.
- Do not duplicate parameter assignments.
- Do not overwrite conflicting values; report the conflict instead.

## Derived files

Preserve each file's existing `using` statement and add one relative `extends` statement immediately after it:

```bicep
using './main.bicep'
extends './base.bicepparam'
```

Remove assignments equal to the base value. Keep environment-specific overrides and unrelated content unchanged.

## Validation

After editing:

- Run `bicep build-params --stdout` on each supplied file.
- Confirm each supplied file has exactly one valid `extends` statement.
- Confirm the base file contains `using none`.

## Result

Report:

| Parameter  | Duplicate value | Files                               | Action        |
| ---------- | --------------- | ----------------------------------- | ------------- |
| `location` | `"westeurope"`  | `dev.bicepparam`, `prod.bicepparam` | Moved to base |

Also list the created or updated base file, modified parameter files, retained overrides, excluded duplicates, and whether all before/after values matched.
