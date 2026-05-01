# Global installation

This skill is already in a user-level skill directory:

- `~/.copilot/skills/playwright-vision-low-resource/`

Use in chat with:

- `/playwright-vision-low-resource mode=local-smoke scope=all`
- `/playwright-vision-low-resource mode=local-debug scope=mcp`
- `/playwright-vision-low-resource mode=remote-full scope=playwright`

Verification:

```bash
find ~/.copilot/skills/playwright-vision-low-resource -maxdepth 3 -type f | sort
~/.copilot/skills/playwright-vision-low-resource/scripts/preflight-playwright-mcp.sh || true
```
