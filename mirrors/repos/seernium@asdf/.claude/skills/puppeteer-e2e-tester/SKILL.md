# Skill: Headless E2E Browser Test Synthesis

Creates automated user flow validations running in headless browser environments via Puppeteer.

## Steps
1. Design test script files targeting user journeys under `src/__e2e__/`
2. Configure automated steps: navigate screens, populate inputs, trigger actions
3. Add assertion checkpoints using accessible roles or `data-testid` attributes

## Template
- See `e2e-test-template.ts` — Login flow E2E test with Puppeteer + Vitest