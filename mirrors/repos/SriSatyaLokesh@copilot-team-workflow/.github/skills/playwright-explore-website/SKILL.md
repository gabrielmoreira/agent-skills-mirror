---
name: playwright-explore-website
description: "Use when a developer wants to understand what to test on a website before writing tests — when they say 'explore the website', 'what should I test?', 'check what flows exist on this URL', 'analyze the UI for test coverage', or when given a URL and asked to plan browser tests. Uses Playwright MCP to navigate and interact with 3–5 core features, documents UI locators, user interactions, and expected outcomes, then proposes concrete test cases. Auto-loads when website exploration, test planning, UI review, or discovering testable flows is mentioned."
---

# Website Exploration for Testing

Your goal is to explore the website and identify key functionalities to test.

## Specific Instructions

1. Navigate to the provided URL using the Playwright MCP Server. If no URL is provided, ask the user to provide one.
2. Identify and interact with 3-5 core features or user flows.
3. Document the user interactions, relevant UI elements (and their locators), and the expected outcomes.
4. Close the browser context upon completion.
5. Provide a concise summary of your findings.
6. Propose and generate test cases based on the exploration.