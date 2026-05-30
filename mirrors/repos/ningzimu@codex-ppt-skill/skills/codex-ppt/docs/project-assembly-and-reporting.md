# Project Assembly And Reporting

Read this before initializing the project directory, writing speaker notes, assembling the PPT, or sending the final report.

## Project Directory

Use this output structure:

```text
{base_dir}/{deck_name}/
├── origin_image/
│   ├── slide_01.png
│   ├── slide_02.png
│   └── ...
├── prompts/
│   ├── slide_01.json
│   └── ...
├── slide_jobs.json
├── slide_run_state.json
├── deck_spec.json
├── outline.md
├── speech.md
└── {deck_name}.pptx
```

If the user did not specify a destination, use the current working directory or the directory that contains the source file.

You may initialize the directory structure with:

```bash
~/.codex-ppt-skill/.venv/bin/python {skill_root}/scripts/assemble_ppt.py {base_dir} {deck_name}.pptx --init
```

## Quality Check And Repair

Before assembling the PPT, inspect every slide image. Check:

- Text is readable and not garbled.
- Slide content matches the outline.
- Title and key points are not truncated.
- Visual style is consistent across slides.
- No page number appears unless the user requested one.
- Important elements do not overlap.

If a slide has severe text or layout issues, regenerate it with a more constrained prompt. If a slide is mostly correct but has a localized issue, use the selected backend's edit capability when available. In CLI/API fallback mode, use `scripts/image_gen.py edit --image {slide_path} --prompt ... --out {new_slide_path}` and replace the final slide only after validating the edited output.

## Speaker Notes

Make sure `outline.md` reflects the final confirmed deck outline. Do not recreate it from scratch here.

Create `speech.md` with speaker notes. Keep it useful and concise: 1-3 short paragraphs per slide is usually enough.

Use headings that the assembly script can map back to slide numbers:

```markdown
## Slide 1: {Title}

{Speaker notes for slide 1}

## Slide 2: {Title}

{Speaker notes for slide 2}
```

## Assembly

Before running `scripts/assemble_ppt.py` or the CLI/API fallback scripts, make sure the shared runtime exists. If `~/.codex-ppt-skill/.venv/bin/python` is missing, or if importing script dependencies fails, create or refresh the environment:

```bash
python3 {skill_root}/scripts/codex_ppt_runtime.py bootstrap
```

This is an internal setup step for the skill. Do not ask the user to run these commands unless dependency installation fails and user approval or troubleshooting is required.

Run:

```bash
~/.codex-ppt-skill/.venv/bin/python {skill_root}/scripts/assemble_ppt.py {base_dir} {deck_name}.pptx --aspect-ratio 16:9
```

Important:

- `{base_dir}` is the parent directory of `{deck_name}/`.
- `{deck_name}.pptx` must match the project folder name.
- The script reads images from `{base_dir}/{deck_name}/origin_image/`.
- The script only reads final images named like `slide_01.png`, `slide_02.png`, etc.; drafts and sample files are ignored.
- Before running assembly, `slide_jobs.json` should show every generated slide as `recorded` and every approved sample slide as `accepted`. If any slide is `pending`, `dispatched`, or `blocked`, stop and report that state.
- If `{base_dir}/{deck_name}/speech.md` exists and uses `Slide N` headings, the script writes those notes into the corresponding PPT speaker notes.
- The script writes `{base_dir}/{deck_name}/{deck_name}.pptx`.

`assemble_ppt.py` supports `16:9` and `4:3`. Use `16:9` unless the user requests otherwise. `image_gen.py` loads `~/.codex-ppt-skill/.env` automatically for `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `CODEX_PPT_IMAGE_MODEL`. Run `python3 {skill_root}/scripts/codex_ppt_runtime.py doctor --check-api` when troubleshooting API access.

## Final Report

Report:

- Project directory
- PPT file path
- Slide image directory
- `outline.md` path
- `speech.md` path
- `slide_jobs.json` path
- Number of slides
- Confirm which image backend was used and that every non-sample slide result was recorded with `record_slide_result.py`.
- Confirm that speaker notes from `speech.md` were written into the PPT, if applicable
- Any slides that were regenerated, blocked, or still have known limitations

## Prompting Principles

- Keep one global visual style fixed across the deck.
- Vary slide composition by page role; style consistency does not mean repeating the same layout.
- Use `layout_blueprints` as candidate patterns, not mandatory templates.
- Generate one slide per image request.
- Prefer concrete visual direction over generic words like "beautiful" or "professional".
- For dense content, split across more slides instead of crowding one slide.
- Prioritize clarity over decoration.
