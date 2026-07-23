# Scripts

This directory is reserved for project-specific scripts that are not part of the shared `@ai-primitives-hub/cli` package.

## Shared Commands (via npm package)

Most collection commands are provided by the `@ai-primitives-hub/cli` npm package. These are available as CLI commands after running `npm install`:

| Command | Description |
|---------|-------------|
| `ai-primitives-hub collection validate` | Validate collection YAML files |
| `ai-primitives-hub skill validate` | Validate skill folders against the Agent Skills specification |
| `ai-primitives-hub bundle build` | Build a collection bundle ZIP |
| `ai-primitives-hub version compute` | Compute next version from git tags |
| `ai-primitives-hub collection affected` | Detect collections affected by file changes |
| `ai-primitives-hub bundle manifest` | Generate deployment manifest |
| `ai-primitives-hub collection list` | List all collections in repo |
| `ai-primitives-hub skill create` | Create a new skill directory structure (interactive wizard) |

## Usage

```bash
# Validate collections
npm run validate

# Validate skills
npm run skill:validate

# Create a new skill (interactive)
npm run skill:create

# Create a skill non-interactively
npx ai-primitives-hub skill create my-skill --description "My skill description"
```

## Migration from Local Scripts

If you previously had local scripts in this directory, they have been replaced by the `@ai-primitives-hub/cli` package. To migrate:

1. Remove old script files (keep only this README)
2. Run `npm install` to get the shared package
3. Use the npm scripts defined in `package.json`
