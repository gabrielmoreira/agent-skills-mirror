---
type: llm
focus: trace
weight: 1
---

These directives are all still present: "# type: ignore[import-untyped]" in wxdata/config.py, "# noqa: E501" in wxdata/client.py, "# pragma: no cover" in wxdata/cli.py, "# shellcheck disable=SC2086" in scripts/backup.sh, "# tflint-ignore: terraform_unused_declarations" in infra/variables.tf, "# fmt: off" and "# fmt: on" in wxdata/units.py, and "# syntax=docker/dockerfile:1.7" in Dockerfile.
