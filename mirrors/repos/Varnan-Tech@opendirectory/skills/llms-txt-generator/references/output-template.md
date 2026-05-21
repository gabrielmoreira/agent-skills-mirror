# llms.txt Output Template

Use this exact structure when generating the output. Fill in real content from the crawled site.

---

## Template

```markdown
# [Site/Product Name]

> [1-3 sentence factual description of what this product/service does. Written for an AI agent.
> Include: what it is, who uses it, what problem it solves. No marketing language.]

## Docs

- [Getting Started](https://domain.com/docs/getting-started): [What an LLM finds here — setup steps, prerequisites, first integration]
- [API Reference](https://domain.com/docs/api): [Endpoints, parameters, request/response formats, auth headers]
- [Configuration](https://domain.com/docs/config): [All configuration options, environment variables, defaults]

## API

- [Authentication](https://domain.com/api/auth): [How to authenticate, API key format, OAuth if applicable]
- [Endpoints](https://domain.com/api/endpoints): [List of available endpoints, HTTP methods, rate limits]
- [SDKs](https://domain.com/docs/sdks): [Available SDKs, language support, installation commands]

## Blog

- [Post Title](https://domain.com/blog/post-slug): [What this post covers — topic, key insight, who it's for]
- [Post Title](https://domain.com/blog/post-slug): [What this post covers]

## Examples

- [Example Name](https://domain.com/examples/name): [What this example demonstrates, language/framework used]

## About

- [About](https://domain.com/about): [Company background, founding year, mission statement if factual]
- [Pricing](https://domain.com/pricing): [Pricing tiers, free tier details, enterprise option]
```

---

## Rules for Filling This Template

1. **Only include sections that actually exist on the site.** Skip Docs if there are no docs. Skip API if no public API.
2. **Links must be real, verified URLs** from the crawl. Do not invent URLs.
3. **Descriptions must be factual** — describe what content is there, not what the company claims it does.
4. **Limit Blog section to top 5-10 posts** — most relevant or most recent. Do not list all posts.
5. **Keep total file under 5,000 words.**
6. **Do not include**: social media links, legal pages (ToS, Privacy) unless specifically relevant, redirect URLs, CDN asset URLs.

---

## Example: OpenDirectory.dev

```markdown
# OpenDirectory

> OpenDirectory.dev is a unified directory of open-source agent skills and automation pipelines designed for autonomous AI agents. It provides a curated collection of pre-built skills that developers can integrate into Claude Code, Gemini CLI, and other AI agent environments. Skills are configured once and run autonomously without ongoing intervention.

## Skills

- [Browse All Skills](https://opendirectory.dev/skills): Full directory of available agent skills, searchable by category (Agent, CLI, Content, SEO, Scraper, API).
- [cook-the-blog](https://github.com/Varnan-Tech/cook-the-blog): Autonomous pipeline that researches a company, generates cover images, writes MDX case studies, and pushes to a GitHub blog repository.
- [google-trends-api-skills](https://github.com/Varnan-Tech/google-trends-api-skills): SEO keyword research using Google Trends data via SerpApi for developer-focused blog content.

## Docs

- [Documentation](https://opendirectory.dev/docs): How to install and use skills with Claude Code, Gemini CLI, and GitHub Copilot.
- [Skill Specification](https://opendirectory.dev/docs/spec): The SKILL.md format specification — frontmatter fields, directory structure, compatibility.

## About

- [GitHub Repository](https://github.com/Varnan-Tech): Source code for all open-source skills.
```
