---
id: paper_writing_skills_index
name: Paper Writing Skills Index
description: |
  Skills for scientific paper writing: CSS themes for HTML preview,
  pandoc conversion recipes, and writing best practices.
---

# Paper Writing Skills

Resources for the Paper Write Team's reporter and writer agents.

## CSS Themes

CSS themes control the visual appearance of the HTML preview generated from `paper.md`.
Reporter selects a theme based on `html_theme` in the triage output config.

| Theme | File | Look |
|---|---|---|
| `academic_minimal` | [academic_minimal.css](./themes/academic_minimal.css) | White background, navy headings, sans-serif, clean modern academic |
| `academic_latex` | [academic_latex.css](./themes/academic_latex.css) | Mimics LaTeX article class: Computer Modern fonts, paragraph indent, booktabs tables, theorem environments |

### How to use

Reporter copies the selected theme to the workdir:

```bash
cp {cwd}/.pantheon/skills/paper_writing/themes/{html_theme}.css {workdir}/themes/active_theme.css
```

Then passes it to pandoc:

```bash
pandoc paper.md --css {workdir}/themes/active_theme.css ...
```

### Custom themes

Users can add their own `.css` files to `.pantheon/skills/paper_writing/themes/`.
Set `html_theme: custom` and `custom_css_path: {absolute_path}` in the triage output config.
