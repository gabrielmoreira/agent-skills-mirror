# Evolve an Existing Skill

Resolve every `prompts/...` and `tools/...` path against `{distilly_skill_root}` (see `SKILL.md`).

## Append new material

When user provides new files or text:

1. Read new content with `prompts/flows/sources.md`
2. Resolve the base dir for the current family
3. `Read` existing `{resolved_base_dir}/{slug}/work.md` and `persona.md`
4. Use `prompts/{character}/merger.md` for incremental analysis
5. Archive current version (Bash):
   ```bash
   python3 "{distilly_skill_root}/tools/version_manager.py" \
     --action backup \
     --character {character} \
     --slug {slug} \
     --base-dir {resolved_base_dir}
   ```
6. Write work/persona delta into temporary patch files
7. Call:
   ```bash
   python3 "{distilly_skill_root}/tools/skill_writer.py" \
     --action update \
     --character {character} \
     --slug {slug} \
     --work-patch /tmp/distilly_{slug}_work_patch.md \
     --persona-patch /tmp/distilly_{slug}_persona_patch.md \
     --base-dir {resolved_base_dir}
   ```
8. If the current family is `celebrity`, run the quality check again after the update

## Correct from conversation

When user expresses "that's wrong" / "he should be":

1. Refer to `prompts/shared/correction_handler.md` to identify correction content
2. Determine if it belongs to Work (technical/workflow) or Persona (personality/communication)
3. If it belongs to Work:
   - Generate `/tmp/distilly_{slug}_work_patch.md`
   - The patch must be one or more replaceable `##` sections
   - Call:
     ```bash
     python3 "{distilly_skill_root}/tools/skill_writer.py" \
       --action update \
       --character {character} \
       --slug {slug} \
       --work-patch /tmp/distilly_{slug}_work_patch.md \
       --base-dir {resolved_base_dir}
     ```
4. If it belongs to Persona:
   - Write the correction record to `/tmp/distilly_{slug}_correction.json`
   - For a single correction, write `{scene, wrong, correct}`
   - For multiple persona corrections, write `{"persona_corrections": [{...}, {...}]}`
   - Call:
     ```bash
     python3 "{distilly_skill_root}/tools/skill_writer.py" \
       --action update \
       --character {character} \
       --slug {slug} \
       --correction-json /tmp/distilly_{slug}_correction.json \
       --base-dir {resolved_base_dir}
     ```
5. If the current family is `celebrity`, run the quality check again after the update
6. Do not hand-edit `work.md`, `persona.md`, `SKILL.md`, or `meta.json`; always update through `skill_writer.py`
