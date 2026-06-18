---
name: pi-e2e-xyz-greet-c4a8d5
description: Test greeter — pi skills e2e. The unique suffix c4a8d5 appears in the skill name so a string match in the agent's output proves Pi loaded this skill.
---

# Pi E2E Greet (c4a8d5)

This is a fixture skill for `tests/e2e/test_pi_skills_filter_e2e.py`. The skill body itself does not matter — the test asserts on whether the SKILL name (`pi-e2e-xyz-greet-c4a8d5`) appears in the agent's enumerated-skills response.
