---
name: install-codex-pet
description: Install shared Codex pet packages into Omnibot with the official codex-pets npm CLI. Use when the user asks to add, install, download, import, or sync a pet by slug or collection, especially requests containing commands such as "npx codex-pets add".
---

# Install Codex Pet

Install pets into Omnibot's selectable pet directory while preserving the
official Codex package format.

## Workflow

1. Extract the lowercase pet slug or collection slug from the request. Do not
   guess when no slug is present.
2. Confirm `node`, `npm`, and `npx` are available. If they are missing, report
   that the embedded Alpine runtime needs its base packages installed.
3. Point the official CLI at Omnibot's Codex-compatible pet root, then run the
   requested command:

```sh
export CODEX_HOME=/workspace/.omnibot
npx --yes codex-pets add claude-pixel
```

For a collection:

```sh
export CODEX_HOME=/workspace/.omnibot
npx --yes codex-pets add-collection cats
```

4. Validate each installed pet:

```sh
sh /workspace/.omnibot/skills/install-codex-pet/scripts/validate_codex_pet.sh claude-pixel
```

5. Report the installed display name and
   `/workspace/.omnibot/pets/<pet-id>/`. The appearance page discovers the
   package automatically; do not copy it into another pet directory.

## Rules

- Keep `CODEX_HOME=/workspace/.omnibot` for every `codex-pets` command. The
  package defaults to `/root/.codex`, which the Omnibot appearance scanner does
  not use.
- Use the npm CLI directly. Do not generate replacement art, rewrite the
  downloaded manifest, or hand-build a package.
- Accept only lowercase slugs made from letters, digits, and hyphens.
- Treat command failures, missing `pet.json`, missing `spritesheet.webp`, an id
  mismatch, or an unexpected `spritesheetPath` as installation failures.
- Never expose credentials or add API keys to commands. `CODEX_PETS_API_BASE`
  may be used only when the user explicitly provides a trusted alternate
  service.
