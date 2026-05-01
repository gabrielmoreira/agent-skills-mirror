# Output Contracts

Every GitHub ops skill report must include:

1. Scope and mode/phase
2. Checks/findings with pass/fail/partial
3. Ordered actions with owner/executor + objective verification gate
4. Decision (`apply|defer|NO_CHANGE`)
5. Missing evidence list

For plan/feature-sensitive flows, also include capability status from `github-capability-resolver`:

- `available-now`
- `available-with-config-change`
- `available-with-plan-upgrade`
- `not-supported`

## Canonical schema

```text
<SKILL_REPORT>
scope: <repo|org|enterprise>
mode: <...>
policy_profile: <strict|standard|light>

checks:
- id: <id>
	result: <pass|fail|partial>
	observation: <what was observed>
	verification: <objective pass condition>

actions:
1) priority: <P1|P2|P3>
	 owner_or_executor: <role|skill>
	 change: <specific action>
	 verification: <objective pass condition>

decision:
- <apply|defer|NO_CHANGE>

missing_evidence:
- <none or required artifacts>
```

No skill may claim merge/release/closeout success without objective verification evidence.
