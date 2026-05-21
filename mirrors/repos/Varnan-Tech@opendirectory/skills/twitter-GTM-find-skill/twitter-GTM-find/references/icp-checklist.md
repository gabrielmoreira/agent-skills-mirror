# Ideal Customer Profile (ICP) Checklist

When evaluating whether a scraped company meets our OpenClaw ICP, follow these strict guidelines.

## 1. Developer-First Product
**What qualifies:**
* API platforms, infrastructure tools, SDKs, dev utilities
* AI agents/automation for technical workflows
* DevOps, CI/CD, monitoring, analytics
* Code editors, Data infrastructure, LLM deployment platforms

**Auto-skip (NOT ICP):**
* Consumer apps, B2C SaaS
* HR tools, Recruiting agencies
* Pure Fintech or Healthcare software
* Traditional physical industries (Real estate, Automotive, Clinics)

## 2. Funding Evidence
**Minimum requirement:**
* $100K+ raised (verifiable via Crunchbase, YC, press, founder posts)

**Preferred:**
* $500K-$5M seed/Series A in the last 18 months
* Backed by Y Combinator (YC), a16z, Sequoia

**Skip if (NOT ICP):**
* Purely bootstrapped companies with zero external capital mentioned
* Service agencies with no product (even if they do tech/web3 marketing)
* No verifiable funding evidence found online

## Evaluation Process
1. Research the company's official website to determine the product type.
2. Search "[Company Name] funding Crunchbase Y Combinator" to find capital raised.
3. If they are a dev-first/infrastructure/AI tool AND have funding -> `isICP` is `true`.
4. If they fail EITHER criteria -> `isICP` is `false`.
