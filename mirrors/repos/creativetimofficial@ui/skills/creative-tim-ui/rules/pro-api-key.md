# PRO Blocks & API Key Setup

## Summary

PRO blocks require a Creative Tim API key. Get yours at https://www.creative-tim.com/ui/dashboard → **API Keys** section.

API key format: `pk_live_` prefix (e.g. `pk_live_a09e7677...`)

## Authentication Methods

### Method 1 — Environment Variable (recommended for development)

```bash
# macOS/Linux
export CREATIVE_TIM_UI_API_KEY=pk_live_your_key

# Inline (one-off)
CREATIVE_TIM_UI_API_KEY=pk_live_your_key npx @creative-tim/ui@latest add <block>

# .env.local (Next.js / Vite) — never commit this file
CREATIVE_TIM_UI_API_KEY=pk_live_xxxxxxxxxxxxxxxx
```

Then install normally — the CLI picks up the env var automatically:
```bash
npx @creative-tim/ui@latest add <pro-block-name>
```

Or pass it explicitly:
```bash
npx @creative-tim/ui@latest add <pro-block-name> --api-key $CREATIVE_TIM_UI_API_KEY
```

### Method 2 — components.json (recommended for teams / CI/CD)

Add a `registries` entry to `components.json`:

```json
{
  "registries": {
    "@creative-tim": {
      "url": "https://www.creative-tim.com/ui/r/{name}.json",
      "headers": {
        "Authorization": "Bearer ${CREATIVE_TIM_UI_API_KEY}"
      }
    }
  }
}
```

Team members each set `CREATIVE_TIM_UI_API_KEY` in their own shell / CI secrets.

### Method 3 — shadcn CLI

The same `components.json` config above works with the shadcn CLI:
```bash
npx shadcn@latest add https://www.creative-tim.com/ui/r/<pro-block>.json
```

## Detecting PRO Blocks

PRO blocks are marked on the website. In registry JSON they include `"pro": true`.
