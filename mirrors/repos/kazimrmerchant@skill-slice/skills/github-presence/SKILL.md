---
name: github-presence
description: "Improves GitHub discoverability: README anatomy and badges, username profile README, topics, awesome-list submissions, FUNDING.yml, and traffic/star signals. Use for making a repo findable via README, topics, profile page, or awesome-list PRs. Not for Actions log debugging, PR merge mechanics, or application feature work."
version: 1.0.1
risk: unknown
source: https://github.com/jonathimer/devmarketing-skills/tree/main/skills/github-presence
source_repo: jonathimer/devmarketing-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/jonathimer/devmarketing-skills/blob/main/LICENSE
---

# GitHub Presence

## Overview

GitHub is where developers evaluate your project before trying it. This skill covers README optimization, profile READMEs, discoverability through topics and awesome lists, and using GitHub features for marketing. Treat your GitHub presence as the first technical evaluation a developer performs — optimize accordingly.

## When to Use

Use this skill when the user wants to optimize their GitHub profile, README, or project discoverability. Trigger phrases include:

- "GitHub README"
- "README optimization"
- "GitHub profile"
- "GitHub stars"
- "GitHub discoverability"
- "awesome lists"
- "GitHub marketing"

## Prerequisites

1. **Read `.agents/developer-audience-context.md` if it exists** — this file provides context about who evaluates the repository.
2. Audit your current GitHub presence (profile, pinned repos, READMEs) before making changes.
3. Confirm you have push access to the target repository or profile README repo.

## Procedure

### 1. Audit Current Presence

1. Open the target repository on GitHub.
2. Review the existing README for structure, badges, quick start, and license.
3. Check repository settings for topics (up to 20 allowed).
4. Review the profile README if one exists (repo named exactly after the username).
5. Check Insights → Traffic for current views, clones, and referrers.

### 2. README Structure

A great README follows this anatomy:

| Section | Purpose | Required? |
|---------|---------|-----------|
| **Logo/Banner** | Brand recognition, visual appeal | Recommended |
| **Badges** | Quick trust signals, status | Recommended |
| **One-liner** | What it does in one sentence | Required |
| **Hero example** | Immediate "what does it look like?" | Highly recommended |
| **Features** | Why use this over alternatives | Required |
| **Quick start** | Get running in < 2 minutes | Required |
| **Installation** | All installation methods | Required |
| **Usage** | Core usage examples | Required |
| **Documentation** | Link to full docs | Required |
| **Contributing** | How to contribute | Recommended |
| **License** | Legal clarity | Required |

### 3. Apply the README Template

Use this template as a starting point. Replace placeholders with project-specific content:

```markdown
<div align="center">
  <img src="logo.svg" alt="Project Name" width="200">
  <h1>Project Name</h1>
  <p><strong>One compelling sentence explaining what this does.</strong></p>

  <!-- Badges -->
  <a href="https://github.com/org/repo/actions"><img src="https://github.com/org/repo/workflows/CI/badge.svg" alt="CI"></a>
  <a href="https://www.npmjs.com/package/name"><img src="https://img.shields.io/npm/v/name.svg" alt="npm version"></a>
  <a href="https://github.com/org/repo/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://discord.gg/invite"><img src="https://img.shields.io/discord/123456789" alt="Discord"></a>

  <br>
  <br>

  <a href="https://docs.example.com">Documentation</a> •
  <a href="https://example.com">Website</a> •
  <a href="https://discord.gg/invite">Discord</a>
</div>

---

## Why Project Name?

- **Feature 1** — Brief explanation
- **Feature 2** — Brief explanation
- **Feature 3** — Brief explanation

## Quick Start

```bash
npm install project-name
```

```javascript
import { thing } from 'project-name';

const result = thing.doSomething();
console.log(result);
```

## Installation

### npm
```bash
npm install project-name
```

### yarn
```bash
yarn add project-name
```

### pnpm
```bash
pnpm add project-name
```

## Usage

### Basic Example

```javascript
// Code example with comments
```

### Advanced Example

```javascript
// More complex example
```

## Documentation

Full documentation available at [docs.example.com](https://docs.example.com)

- [Getting Started](https://docs.example.com/getting-started)
- [API Reference](https://docs.example.com/api)
- [Examples](https://docs.example.com/examples)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT © [Your Name](https://yoursite.com)
```

### 4. Add Trust Signal Badges

| Badge | What it shows | When to use |
|-------|--------------|-------------|
| CI/Build status | Code quality | Always |
| Version | Latest release | Always for packages |
| License | Legal clarity | Always |
| Downloads/installs | Adoption | When impressive |
| Coverage | Test quality | If > 70% |
| Security | Audit status | If you have it |

Community badges:

| Badge | Source | Purpose |
|-------|--------|---------|
| Discord members | shields.io | Show active community |
| GitHub stars | shields.io | Social proof |
| Contributors | shields.io | Open source health |
| Last commit | shields.io | Project activity |

Badge services:

| Service | URL | Best for |
|---------|-----|----------|
| Shields.io | shields.io | Most badges |
| Badgen | badgen.net | Fast, minimal |
| GitHub badges | Native | Actions, issues |

Badge examples:

```markdown
<!-- Build status -->
![CI](https://github.com/org/repo/workflows/CI/badge.svg)

<!-- npm version -->
[![npm](https://img.shields.io/npm/v/package-name.svg)](https://www.npmjs.com/package/package-name)

<!-- Downloads -->
[![Downloads](https://img.shields.io/npm/dm/package-name.svg)](https://www.npmjs.com/package/package-name)

<!-- License -->
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<!-- Discord -->
[![Discord](https://img.shields.io/discord/SERVER_ID?color=7289da&logo=discord&logoColor=white)](https://discord.gg/invite)

<!-- Stars -->
[![GitHub stars](https://img.shields.io/github/stars/org/repo?style=social)](https://github.com/org/repo)
```

### 5. Set Up or Update Profile README

1. Create a repository with your exact GitHub username (e.g., `github.com/yourname/yourname`).
2. Add a `README.md` file — it will display on your profile page.
3. Use this structure:

```markdown
# Hi, I'm [Name] 👋

[One sentence about what you do]

## What I'm Working On

- 🔭 Building [project] — [brief description]
- 🌱 Learning [technology]
- 💬 Ask me about [expertise areas]

## Projects

| Project | Description | Stars |
|---------|-------------|-------|
| [Project 1](https://github.com/yourname/project1) | Brief description | ![Stars](https://img.shields.io/github/stars/yourname/project1?style=social) |
| [Project 2](https://github.com/yourname/project2) | Brief description | ![Stars](https://img.shields.io/github/stars/yourname/project2?style=social) |

## Recent Blog Posts

<!-- BLOG-POST-LIST:START -->
<!-- Automated with GitHub Actions -->
<!-- BLOG-POST-LIST:END -->

## Connect

[![Twitter](https://img.shields.io/badge/-Twitter-1DA1F2?style=flat&logo=twitter&logoColor=white)](https://twitter.com/handle)
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/handle)

## GitHub Stats

![Your GitHub stats](https://github-readme-stats.vercel.app/api?username=yourusername&show_icons=true)
```

Profile README best practices:

| Do | Don't |
|----|-------|
| Keep it scannable | Write paragraphs |
| Show your best projects | List everything |
| Include current work | Let it get stale |
| Add contact methods | Make it hard to reach you |
| Show personality | Be generic |

### 6. Optimize Discoverability

#### GitHub Topics

Topics are how people find repositories. Add up to 20 via Repository settings → Topics.

| Topic strategy | Example |
|----------------|---------|
| Technology | `javascript`, `rust`, `python` |
| Framework | `react`, `nextjs`, `django` |
| Use case | `cli`, `api`, `testing` |
| Category | `developer-tools`, `devops` |
| Problem | `authentication`, `caching` |

#### Search Optimization

GitHub search considers, in order of impact:

1. **Repository name** — Include main keyword.
2. **Description** — 350 chars max, keyword-rich.
3. **README content** — Full text indexed.
4. **Topics** — Category matching.
5. **Language** — Auto-detected.

#### Awesome Lists

Getting on awesome lists drives traffic and credibility.

1. Find relevant awesome lists (search "awesome + [topic]").
2. Check list requirements (quality, activity, docs).
3. Ensure your project meets criteria.
4. Submit a PR following the list's guidelines.
5. Be patient — curation takes time.

Popular awesome lists for dev tools:

- `awesome-cli-apps`
- `awesome-selfhosted`
- `awesome-nodejs`
- `awesome-python`
- `awesome-go`
- `awesome-rust`
- `awesome-devops`

### 7. Automate with GitHub Actions

#### Automated README Updates (Blog Posts)

```yaml
# .github/workflows/readme-update.yml
name: Update README

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Example: Update blog post list
      - uses: gautamkrishnar/blog-post-workflow@master
        with:
          feed_list: "https://yourblog.com/feed"

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add -A
          git diff --quiet && git diff --staged --quiet || git commit -m "Update README"
          git push
```

#### Metrics and Stats

```yaml
# Auto-update GitHub stats image
- uses: lowlighter/metrics@latest
  with:
    token: ${{ secrets.METRICS_TOKEN }}
    filename: github-metrics.svg
```

#### Release Announcements

```yaml
# Tweet on new release
name: Release Announcement
on:
  release:
    types: [published]

jobs:
  announce:
    runs-on: ubuntu-latest
    steps:
      - name: Tweet
        uses: ethomson/send-tweet-action@v1
        with:
          status: "🚀 ${{ github.repository }} ${{ github.event.release.tag_name }} released! ${{ github.event.release.html_url }}"
          consumer-key: ${{ secrets.TWITTER_CONSUMER_KEY }}
          # ... other secrets
```

> **Never commit live secrets.** Use GitHub repository secrets (`Settings → Secrets and variables → Actions`) and reference them as `${{ secrets.YOUR_KEY }}`. Example placeholders above are not real credentials.

### 8. Set Up GitHub Sponsors

1. Join GitHub Sponsors at `github.com/sponsors`.
2. Create compelling tier descriptions.
3. Add a `.github/FUNDING.yml` file to repos:

```yaml
github: [yourusername]
patreon: yourpatreon
open_collective: yourproject
ko_fi: yourkofi
custom: ["https://buymeacoffee.com/you"]
```

Sponsor tiers that work:

| Tier | Price | Offer |
|------|-------|-------|
| **Supporter** | $5/mo | Thanks + name in README |
| **Backer** | $15/mo | Logo in README + Discord role |
| **Sponsor** | $50/mo | Priority support + feature voting |
| **Enterprise** | $200+/mo | Dedicated support + consultation |

### 9. Measure Success

Track these metrics via Repository → Insights → Traffic:

| Metric | What it tells you | Goal |
|--------|-------------------|------|
| Stars | Interest/bookmarks | Growth over time |
| Forks | Active usage | Quality > quantity |
| Clones | People trying it | Pre-install interest |
| Traffic | Profile/repo views | Awareness |
| Referrers | Where traffic comes from | Channel effectiveness |
| Contributors | Community health | Sustainable project |

### 10. Use Supporting Tools

| Tool | Use case |
|------|----------|
| **[Octolens](https://octolens.com)** | Monitor GitHub for mentions of your project, competitors, and relevant discussions. Get alerts when people talk about problems you solve. |
| **Shields.io** | Generate status badges |
| **GitHub Readme Stats** | Dynamic stats for profile |
| **Carbon** | Beautiful code screenshots |
| **readme.so** | README generator |
| **Metrics** | Advanced profile stats |

## Pitfalls

1. **Neglecting the README** — it is your landing page; a weak README kills adoption.
2. **Too many badges** — cluttered headers reduce scannability. Keep to 4–6 high-signal badges.
3. **Letting issues and PRs pile up unanswered** — signals an abandoned project.
4. **Missing license file** — legal ambiguity discourages adoption and contribution.
5. **Low-quality or broken images** — broken logo/banner links look unprofessional.
6. **Walls of text without structure** — developers scan, they don't read paragraphs.
7. **Missing contribution guidelines** — potential contributors bounce without a CONTRIBUTING.md.
8. **Stale profile README** — outdated "what I'm working on" sections signal inactivity.
9. **No topics set** — repositories without topics are nearly invisible in GitHub search.
10. **Submitting to awesome lists before meeting criteria** — rejected PRs waste time and burn goodwill with maintainers.
11. **Committing secrets to workflows** — always use GitHub repository secrets, never hardcode tokens or API keys.

## Verification

Run through this README audit checklist after making changes:

- [ ] Clear, keyword-rich name and description
- [ ] Badges show CI status, version, license
- [ ] One-liner explains what it does
- [ ] Quick start gets users running in < 2 min
- [ ] Code examples are copy-pasteable
- [ ] All links work and are HTTPS
- [ ] Images have alt text
- [ ] Mobile-readable formatting
- [ ] License file present
- [ ] Contributing guidelines exist
- [ ] Topics are set (up to 20)
- [ ] Social preview image uploaded (Repository → Settings → Social preview)

Checkable commands (PowerShell, Windows host):

```powershell
# Verify README exists and has key sections
Test-Path .\README.md
Select-String -Path .\README.md -Pattern "Quick Start","Installation","Usage","License" | Select-Object -ExpandProperty Line

# Verify LICENSE file exists
Test-Path .\LICENSE

# Verify CONTRIBUTING.md exists
Test-Path .\CONTRIBUTING.md

# Verify FUNDING.yml exists if sponsors are set up
Test-Path .\.github\FUNDING.yml

# Check for accidentally committed secrets (should return nothing)
Select-String -Path .\README.md -Pattern "YOUR_KEY","xoxb-","sk-" -AllMatches
```

On GitHub, verify:

1. Navigate to the repository page — README renders correctly with badges and images.
2. Check Repository → Insights → Traffic for view/clone data.
3. Confirm topics appear under the repo title.
4. Open the profile page — profile README renders if the username-matched repo exists.

## Related Skills

- `developer-audience-context` — Know who evaluates your repo
- `hacker-news-strategy` — HN users check GitHub before upvoting
- `reddit-engagement` — Redditors evaluate via GitHub
- `dev-to-hashnode` — Link from README to content

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
