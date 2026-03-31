# Spec-Engineer Skill

## Purpose

The Spec-Engineer skill is designed to turn vague or imprecise ideas into actionable, clear, and implementable software specifications. This skill provides a structured output format that delineates all necessary components of a software spec.

## How to Use

### Invocation

To use this skill, you can run the `/spec <your idea here>` command. This will generate a full specification with a detailed task breakdown and structure.

### Examples

To add a new feature or component, such as user authentication, you might invoke this skill as follows:

```
/spec Add user authentication with JWT and refresh tokens
```

This command will produce a structured specification with tasks from T1 to T6 (or more) each representing a unit of work.

## Output Format

The output follows a strict markdown format, focusing on clarity, testability, and completeness. See the prompt template in `~/.pi/agent/prompts/spec.md` for the detailed structure.

Here's a brief overview of the output format:

- **Overview**: Summary of the problem, beneficiaries and metrics for success
- **Business / User Value**: Justification for building now
- **Functional Requirements**: Prioritized list of features
- **Non-Functional Requirements & Constraints**: Performance, security, tech stack, style
- **Detailed Task Breakdown**: Small, verifiable tasks
- **Acceptance Criteria**: Testable outcomes
- **Edge Cases & Error Handling**: Important considerations
- **Out of Scope / Future Ideas**: Deferred items
- **Suggested File Structure / Naming**: Where to place new components

The skill aims to provide crisp, task-oriented specifications that help guide developers through implementation.
