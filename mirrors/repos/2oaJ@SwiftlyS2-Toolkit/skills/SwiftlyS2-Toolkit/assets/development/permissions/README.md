# Permissions Entry Notes

Official docs section:
- `Permissions`

Prioritize:
- `Core.Permission.PlayerHasPermission(...)`
- wildcard `*`
- `permissions.jsonc`
- permission groups / `__default`
- `AddSubPermission(parent, child)`

Common related scenarios:
- command permissions: `../commands/`
- menu visibility: `../menus/menu-template.cs.md`
- Shared API / cross-plugin capability tiering: `../shared-api/shared-interface-template.cs.md`
