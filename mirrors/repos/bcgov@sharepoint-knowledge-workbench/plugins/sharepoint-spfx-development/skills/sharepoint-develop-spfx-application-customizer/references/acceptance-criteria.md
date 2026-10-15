# Acceptance Criteria

- Skill slug: `sharepoint-develop-spfx-application-customizer`
- Target plugin: `sharepoint-spfx-development`
- Canonical PowerShell resides only in the plugin root `scripts` directory.
- The skill-local scripts are file-level symbolic links registered in `symlinks.json`.
- The workflow distinguishes package deployment, app installation, and custom-action registration.
- Registration is dry-run by default and writes only with `-Execute` and the confirmation token.
- Registration matches existing actions by stable name or component id; duplicate matches fail safely.
- A write is verified by re-querying the custom action.
- `-Remove` removes all matching actions and is safe when none exist.
- The skill covers placeholders, SPA navigation, disposal and untrusted-input handling.
- Positive and negative routing evals distinguish Application Customizers from web parts, command sets and form customizers.
