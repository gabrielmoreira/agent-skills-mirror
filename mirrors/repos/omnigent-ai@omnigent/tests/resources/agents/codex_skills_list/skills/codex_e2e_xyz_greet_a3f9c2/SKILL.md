---
name: codex_e2e_xyz_greet_a3f9c2
description: Test greeter — codex skills e2e. The unique suffix a3f9c2 appears in the skill name so a string match in the agent's output proves codex loaded this skill.
---

# Codex E2E Greet (a3f9c2)

This is a fixture skill for `tests/e2e/test_codex_skills_filter_e2e.py`. The skill body itself does not matter — the test asserts on whether the SKILL name (`codex_e2e_xyz_greet_a3f9c2`) appears in the agent's enumerated-skills response.
