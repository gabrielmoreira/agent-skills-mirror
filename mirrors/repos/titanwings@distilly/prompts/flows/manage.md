# Manage Generated Skills

Resolve every `tools/...` path against `{distilly_skill_root}` (see `SKILL.md`). `{character}` is `colleague`, `relationship` or `celebrity`; confirm it with the user before rolling back or deleting.

List the skills of one family:
```bash
python3 "{distilly_skill_root}/tools/skill_writer.py" --action list --character {character} --base-dir ./skills/{character}
```

Roll back a specific skill version:
```bash
python3 "{distilly_skill_root}/tools/version_manager.py" --action rollback --character {character} --slug {slug} --version {version} --base-dir ./skills/{character}
```

Delete a specific skill:
```bash
rm -rf skills/{character}/{slug}
```
