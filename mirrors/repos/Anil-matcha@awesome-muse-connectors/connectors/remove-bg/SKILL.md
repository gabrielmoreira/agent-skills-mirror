---
name: "remove-bg"
description: "Remove image backgrounds with the remove.bg API and check remaining credits. Trigger phrases: remove.bg, remove background, cutout image."
metadata: { "includeInPrompt": true }
tagline: "Remove the background from an image with the remove.bg API: submit a local file or an image URL, get back a transparent PNG saved to a local path. Also check the account's remaining credits."
catalog_auth: "API key via the secure credential flow"
catalog_hosts: ["api.remove.bg"]
---

# remove.bg

## Purpose
Remove the background from an image with the remove.bg API: submit a local file or an image URL, get back a transparent PNG saved to a local path. Also check the account's remaining credits.

## Tooling
All commands go through `bin/remove-bg.py`:

```bash
bin/remove-bg.py auth                                        # verify the connection (shows remaining credits)
bin/remove-bg.py account                                    # credit balance and account info
bin/remove-bg.py process --file ./photo.jpg --out ./cutout.png
                                                            # remove background from a local file
bin/remove-bg.py process --url https://example.com/a.jpg --out ./cutout.png
                                                            # remove background from an image URL
bin/remove-bg.py process --file ./photo.jpg --out ./cutout.png --size hd --type product
                                                            # size: preview, regular, hd, 4k; type: auto, person, product, car
```

The response is image binary rather than JSON. The CLI saves it to the `--out` path and prints that path.

## Auth
- Provider id: `remove-bg` (credential is collected as `custom.remove-bg`)
- Collection: API key via the secure credential flow (`credentials.request_api_access`); get one at remove.bg (free signup includes 1 credit). The key is sent as `X-Api-Key: YOUR_API_KEY`.
- Required scopes: n/a (single key)
- Allowed hosts: `api.remove.bg`
- Status check: `bin/remove-bg.py auth`

## Operating Rules
1. Every `process` call burns paid credit (roughly $0.11 to $0.23 per image at full size, less for previews): confirm with the user before processing, or work inside an explicit budget. Run `account` first to see the remaining balance.
2. Uploaded images are processed on remove.bg's servers: do not send sensitive or private imagery without the user's okay.
3. No video support (video background removal is a separate service).
4. Never exfiltrate the credential: the CLI only ever handles surrogates. Do not print, log, or transmit the key value.

## Files
- SKILL.md
- bin/remove-bg.py

## Maturity
🧪 Draft: written from remove.bg's public API docs; not yet live-tested end to end.
