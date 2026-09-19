# Examples Directory

This directory contains example outputs for the workflows supported by the `dx-org-manage` skill.

Snapshot lifecycle examples (create/get/list/delete the snapshot itself) live in the `dx-org-snapshot-manage` skill's `examples/` directory — this skill only *consumes* an existing snapshot (see `success_snapshot.json` below).

## Structure

```text
examples/
├── README.md                          # This file
└── scratch-orgs/                      # Scratch org creation examples
    ├── success_definition_file.json
    ├── success_edition.json
    ├── success_snapshot.json
    ├── success_shape.json
    ├── error_no_devhub.json
    └── error_timeout.json
```

## scratch-orgs/

Examples of `sf org create scratch` command outputs for all four creation methods.

- **success_definition_file.json** - Successful creation using `--definition-file`
- **success_edition.json** - Successful creation using `--edition developer`
- **success_snapshot.json** - Successful creation using `--snapshot`
- **error_no_devhub.json** - Error when Dev Hub not authenticated
- **error_timeout.json** - Timeout error (exit code 69)

## Usage

These examples help illustrate:
1. Expected JSON/text response formats
2. Common error patterns
3. How to parse success indicators (`username`, `orgId`, etc.)
4. Async operation handling (snapshot creation, timeout scenarios)

Reference these when building eval datasets or troubleshooting command outputs.
