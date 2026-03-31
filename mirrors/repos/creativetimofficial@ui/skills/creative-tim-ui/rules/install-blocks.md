# Installing Creative Tim UI Blocks

## Summary

Two CLI methods install blocks and all their shadcn/ui dependencies automatically.

## Method 1 — Creative Tim CLI (recommended)

```bash
npx @creative-tim/ui@latest add <block-name>
```

The package also exposes two named binaries you can use directly once installed globally:
```bash
npx creative-tim-ui add <block-name>
# or
npx creative-tim add <block-name>
```

### Examples

```bash
npx @creative-tim/ui@latest add hero-01
npx @creative-tim/ui@latest add ai-agent-activity-01
npx @creative-tim/ui@latest add agent-management-list-01
npx @creative-tim/ui@latest add pricing-01
npx @creative-tim/ui@latest add testimonials-03
```

### Initialize a new project

```bash
npx @creative-tim/ui@latest init
```

### What happens

1. Fetches `https://www.creative-tim.com/ui/r/<block-name>.json`
2. Copies the component source into your project
3. Runs `npx shadcn@latest add` for each `registryDependency` (button, card, badge, etc.)

## Method 2 — shadcn CLI

```bash
npx shadcn@latest add https://www.creative-tim.com/ui/r/<block-name>.json
```

### Examples

```bash
npx shadcn@latest add https://www.creative-tim.com/ui/r/hero-01.json
npx shadcn@latest add https://www.creative-tim.com/ui/r/ai-agent-activity-01.json
```

## Block Discovery

- Browse all blocks: https://www.creative-tim.com/ui
- AI-readable index: https://www.creative-tim.com/ui/llms.txt
- Latest blocks: https://www.creative-tim.com/ui/blocks/latest

Individual block JSON:
```
https://www.creative-tim.com/ui/r/<block-name>.json
```
