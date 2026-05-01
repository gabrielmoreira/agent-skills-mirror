# Project Instructions
- Writing: keep user's voice, conversational, stick closely to what user said without making things up, but fix small grammar mistakes
- After adding or renaming tips, run `node scripts/generate-toc.js` to update the table of contents
- `~/.claude/CLAUDE.md` is symlinked to `GLOBAL-CLAUDE.md` in this repo
- When committing changes to the plugin (skills, plugin.json, etc.), bump the patch version in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. Don't bump for non-plugin changes like system prompt patches.
- Git tags/releases (e.g. `v0.25.1`) and plugin versions (e.g. `0.14.9`) are separate. The git tag follows the repo release progression and is bumped for any change. The plugin version is only in `plugin.json` and `marketplace.json`.

## Installing a specific native binary version

Native binaries are on GCS, not GitHub releases. To install a specific version:

1. Fetch the manifest: `curl -sL "https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/{VERSION}/manifest.json"`
2. Download the binary (use a safeclaw container): `.../claude-code-releases/{VERSION}/{PLATFORM}/claude` where PLATFORM is `darwin-arm64`, `linux-arm64`, etc.
3. Verify SHA256 checksum against the manifest
4. Place at `~/.local/share/claude/versions/{VERSION}` and `chmod 755`
5. Update symlink: `ln -sf ~/.local/share/claude/versions/{VERSION} ~/.local/bin/claude`
6. Patch with `bash system-prompt/{VERSION}/patch-native.sh`
