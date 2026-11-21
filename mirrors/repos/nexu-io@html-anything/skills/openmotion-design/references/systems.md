# Design Systems, Skills and Craft Guides

OpenMotion bundles the Design Studio library under `library/design/` and exposes it through `openmotion_design_catalog`.

- **Design systems:** call `openmotion_design_catalog` (`action="list_design_systems"`, optional `q` or `category`), then `action="get_design_system"` with `id` to read `DESIGN.md` and `tokens.css`. Passing `designSystemId` to `openmotion_design_project` (`action="create"`) automatically writes `DESIGN.md` and `tokens.css` into the new project.
- **Starter templates:** call `action="list_templates"` (optional `scenario`, `q`) and pass `templateId` to `openmotion_design_project` (`action="create"`) to start from an existing HTML template.
- **Design Skills:** call `action="list_skills"` and `action="get_skill"` (`id`, optional `referencePath`) for specialized patterns (dashboards, editorial decks, typography, data visualization). When a library skill mentions legacy Open Design CLI commands (`od ...`), translate them to `openmotion_design_catalog`, `openmotion_design_project`, `openmotion_design_edit`, `openmotion_design_comments` or `openmotion_assets_use`.
- **Craft rules:** call `action="get_craft"` (no `id` to list; with `id` to read) for accessibility, typography hierarchy, color, animation discipline, form validation, state coverage and RTL guidance.
