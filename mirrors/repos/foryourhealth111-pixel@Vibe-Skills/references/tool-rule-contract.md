# Tool Rule Contract

This document translates Letta-style tool rules into VCO-native governance language.

## Rule Types

| Contract Type | VCO Mapping |
|---|---|
| allow tool use | candidate provider/skill may be suggested |
| require confirmation | emit `confirm_required` or advisory confirmation question |
| forbid unsafe escalation | stay in advisory mode or fallback |
| budget-aware tool use | prefer lighter path / compaction / defer heavy context |

## Field Expectations

Conformance-oriented tool rules should expose `preferred_tool_classes` and `forbidden_tool_classes` so VCO can check whether policy vocabulary remains advisory rather than authoritative.

## Contract Constraints

1. Tool rules can constrain, but cannot replace VCO routing.
2. Tool rules can request confirmation, but cannot silently mutate authority.
3. Any contract that implies a second orchestrator is invalid in VCO.
