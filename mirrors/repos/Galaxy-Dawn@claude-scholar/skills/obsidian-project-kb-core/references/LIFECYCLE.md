# Lifecycle Rules

## Project lifecycle

- `detach`: remove or disable repo binding, keep vault project content in place
- `archive`: move the entire project to `Research/_archived/{project-slug}-{date}/` and disable sync
- `purge`: permanently delete binding metadata and the vault project root

## Note lifecycle

- `archive`: move a canonical note into `Research/{project-slug}/Archive/`, repair links, update registry and index
- `rename`: rename or move a canonical note in place, repair links, update registry and index, and do not create archive history
- `purge`: permanently delete a canonical note, repair links, and record the removal in archive history when appropriate

## Defaults

- “remove project knowledge” means `archive`, not `purge`
- note archive history remains visible in `_system/registry.md`
- archived notes may still be referenced for historical context, but they are not active canonical notes
