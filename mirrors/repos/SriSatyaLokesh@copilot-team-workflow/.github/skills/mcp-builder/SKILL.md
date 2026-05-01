---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

# MCP Server Development

Guide for creating high-quality MCP (Model Context Protocol) servers.

## Development Workflow

### Phase 1: Research and Planning

1. **Modern MCP Design**: Balance comprehensive API coverage with specialized workflow tools. Prioritize clear, action-oriented tool names (e.g., `github_create_issue`).
2. **Protocol Study**: Review the [specification overview](https://modelcontextprotocol.io/specification/draft.md) and transport mechanisms.
3. **Framework Selection**: 
   - **TypeScript (Recommended)**: Best SDK support and type safety.
   - **Python**: Good for specific library integrations.
4. **API Planning**: Identify endpoints, auth requirements, and data models for the target service.

### Phase 2: Implementation

1. **Setup Project**: Use language-specific templates.
2. **Core Infrastructure**: Implement API client, auth, and error handling helpers.
3. **Implement Tools**:
   - **Input Schema**: Use Zod (TS) or Pydantic (Python) with clear descriptions.
   - **Output Schema**: Define `outputSchema` for structured results.
   - **Annotations**: Set `readOnlyHint`, `destructiveHint`, etc.

### Phase 3: Review and Test

1. **Code Quality**: Ensure DRY principles and consistent error handling.
2. **Testing**:
   - Verify compilation/syntax.
   - Use the [MCP Inspector](https://npx @modelcontextprotocol/inspector).

### Phase 4: Evaluation

Create evaluations to test LLM effectiveness using the provided guide.

1. **Generate Questions**: Create 10 realistic, complex, verifiable questions.
2. **Verify Answers**: Manually solve and document correct answers.
3. **Format**: Use the [evaluation XML structure](reference/evaluation.md).

## Resources

- **Best Practices**: [📋 Core Guidelines](./reference/mcp_best_practices.md)
- **TypeScript SDK**: [⚡ TS Patterns](./reference/node_mcp_server.md)
- **Python SDK**: [🐍 Python Patterns](./reference/python_mcp_server.md)
- **Evaluations**: [✅ Evaluation Guide](./reference/evaluation.md)