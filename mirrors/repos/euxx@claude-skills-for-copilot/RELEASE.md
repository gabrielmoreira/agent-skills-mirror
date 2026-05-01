# Release Guide

## Steps to Release a New Version

1. Update `CHANGELOG.md`:
   - Add version entry: `## [X.Y.Z] - YYYY-MM-DD` with changes

2. Update version in `package.json`:

   ```bash
   # Edit package.json to set "version": "X.Y.Z"
   npm install  # sync package-lock.json
   ```

3. Verify packaging locally:

   ```bash
   npm run package
   ```

   Confirm the `.vsix` file is generated without errors. You may keep it for manual testing.

4. Commit and push:

   ```bash
   git add CHANGELOG.md package.json
   git commit -m "chore: update version to vX.Y.Z"
   git push origin main
   ```

5. Run the release workflow:

   ```bash
   gh workflow run release.yml
   ```

   This runs tests, packages the extension as `.vsix`, and creates a GitHub Release with the file attached.

   To overwrite an existing release for the same version:

   ```bash
   gh workflow run release.yml -f overwrite=true
   ```

6. Verify the release:

   ```bash
   gh release view vX.Y.Z
   ```

7. Update the release notes on GitHub to match `CHANGELOG.md`:

   Write the notes in Markdown format to a temp file, then pass it via `--notes-file`:

   ```bash
   gh release edit vX.Y.Z --notes-file /path/to/notes.md
   ```

   Notes format:

   ```markdown
   ## What's Changed

   ### Added/Changed/Fixed

   - Change 1
   - Change 2

   **Full Changelog**: https://github.com/PUBLISHER/extension-name/compare/vPREV...vX.Y.Z
   ```

   > `PUBLISHER` and `extension-name` come from the `publisher` and `name` fields in `package.json`.
