# Troubleshooting — Skill Manager for Copilot

## Common Issues

### Skills not appearing in sidebar
- Run `Skills: Pull All` from the command palette
- Check that at least one repo is configured in `skillManager.repos`
- Verify the repo has the correct structure: `skills/<name>/SKILL.md`

### "Clone failed" error when adding a repo
- Check the URL is correct (HTTPS or SSH)
- For private repos, ensure Git credentials are configured
- Try cloning manually: `git clone <url>` to verify access

### Skills not updating on pull
- If you edited the local copy, the extension preserves your changes (depends on `localEditStrategy`)
- Set `"skillManager.localEditStrategy": "overwrite"` to always accept repo updates
- Or set to `"ask"` to be prompted each time

### Push Feedback fails
- The repo may not allow push from your account
- Ensure you have write access or fork the repo first
- Check network connectivity — the status bar shows connection errors

### Disabled skill won't re-enable
- Right-click the skill in sidebar → `Enable Skill`
- Or manually rename `SKILL.md.disabled` back to `SKILL.md`

### Status bar shows "error"
- Usually a network issue during sync
- Run `Skills: Status` for details
- Run `Skills: Pull All` to retry

## Reset Extension State

If things are completely broken:

1. Delete the cache: remove the `.skill-manager-cache/` folder in the VS Code global storage
2. Delete local skills: remove `.github/skills/` from your workspace
3. Restart VS Code
4. Re-add your repos and pull again
