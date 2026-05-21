# Keyword Placement Guide

Detailed rules and examples for placing SEO keywords in blog content.

## Title (max 60 characters)

**Format**: `[Primary Keyword] — [Benefit/Number] [Year]`

**Good examples**:
- "Kubernetes Alternatives — 10 Best Options in 2026"
- "AI Code Review Tools — Complete Developer Guide"
- "Rust vs Go — Performance Comparison for Backend"

**Bad examples**:
- "Everything You Need to Know About Kubernetes" (no keyword focus)
- "Top Kubernetes Kubernetes Tools Kubernetes Guide" (stuffed)

## H1 Heading

Same as title or a slight variation. One H1 per page.

## H2 Headings (3-5 per article)

Source these from RELATED_TOPICS API results. Use natural language.

**Example**: If researching "kubernetes deployment", RELATED_TOPICS might return:
- "Container Orchestration" -> H2: Container Orchestration with Kubernetes
- "Docker" -> H2: Docker vs Kubernetes for Deployment
- "Helm" -> H2: Using Helm Charts for Kubernetes Deployment
- "CI/CD" -> H2: CI/CD Pipelines with Kubernetes

## H3 Headings (2-3 per H2 section)

Source from RELATED_QUERIES long-tail keywords. Prefer question format.

**Example**: Under "Container Orchestration with Kubernetes":
- H3: What Is Container Orchestration?
- H3: How Does Kubernetes Handle Container Scaling?

## First Paragraph

Include primary keyword within the first 100 words. Make it natural.

**Good**:
> Looking for the best **kubernetes deployment** strategies? As container adoption grows, understanding how to deploy applications on Kubernetes has become essential for modern engineering teams.

**Bad**:
> Kubernetes deployment is important. If you want kubernetes deployment, you need to learn about kubernetes deployment strategies for your kubernetes deployment needs.

## Body Content Density

**Primary keyword**: 1-2% of total word count
- 1500-word article = 15-30 natural mentions
- Spread evenly, not clustered

**Secondary keywords**: 0.5-1% each
- Use 2-4 secondary keywords throughout

**Semantic variations**: Use related terms naturally
- "kubernetes deployment" -> also use "k8s deploy", "deploying on kubernetes", "container deployment"

## Meta Description (150-160 characters)

Include primary keyword + 1-2 secondary keywords. Make it compelling.

**Good**:
> Learn kubernetes deployment best practices. Covers Helm charts, CI/CD pipelines, container orchestration, and scaling strategies for production.

**Bad**:
> This article is about kubernetes. Read to learn more about kubernetes deployment.

## Featured Snippet Optimization

For each long-tail H3 keyword:
1. Answer the question directly in 40-60 words immediately after the heading
2. Use bullet points or numbered lists
3. Provide a concise answer first, then expand

**Example**:
```markdown
### What Is Container Orchestration?

Container orchestration automates the deployment, scaling, networking,
and management of containerized applications across clusters of machines.
Tools like Kubernetes handle scheduling, load balancing, and self-healing,
allowing teams to manage thousands of containers efficiently.

In more detail, container orchestration solves several key challenges...
```
