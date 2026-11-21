# Iterating from Design Studio Annotations

Users annotate rendered HTML elements and regions in Design Studio (Comment pin, Region box, Pen markup) and click **Copy to Agent** to send an `<attached-preview-comments>` brief.

## Scoped revision loop

1. **Read current comments and revision:** call `openmotion_design_comments` (`action="list"`, `projectId`) and `openmotion_design_project` (`action="get"`, `projectId`).
2. **Read affected files:** call `openmotion_design_edit` (`action="read_file"`, `projectId`, `path`).
3. **Edit only the marked scope:** modify only the elements, styles, regions or slides identified in the open comments unless the user explicitly requested broader changes. Preserve unrelated sections, tokens and interactions.
4. **Save as a new version:** call `openmotion_design_edit` (`action="write"`, `projectId`, `expectedRevision`, `requestId`, `files`, `summary` citing the addressed comment IDs). On `VERSION_CONFLICT`, re-read the project and re-apply against the latest revision.
5. **Resolve addressed comments:** for each addressed comment, call `openmotion_design_comments` (`action="update"`, `projectId`, `commentId`, `status="resolved"`, `expectedCommentRevision`).
6. **Open the updated preview:** call `openmotion_design_project` (`action="open"`, `projectId`). The Design Studio editor polls project state and automatically refreshes the preview.

## Version history and rollback

- List snapshots with `openmotion_design_edit` (`action="list_versions"`, `projectId`).
- Roll back safely with `openmotion_design_edit` (`action="restore_version"`, `projectId`, `versionId`, `expectedRevision`, `requestId`). Restoring `v3` while on `v5` creates `v6` with `v3`'s bytes while preserving `v4` and `v5`.
