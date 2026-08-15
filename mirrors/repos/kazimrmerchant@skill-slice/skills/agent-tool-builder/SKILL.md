---
name: agent-tool-builder
description: "Specifies production agent tools: JSON Schema input_schema, MCP tools/list and tools/call, is_error envelopes, and batched parallel tool_result. Use for function-calling schemas or SDK tool runners. Never substitute this for prompt-only persona design or multi-agent orchestration without a callable schema."
version: 1.0.1
---

## Overview
Tools are how AI agents interact with the world. A well-designed tool is the difference between an agent that works and one that hallucinates, fails silently, or costs 10x more tokens than necessary. Tool descriptions are more important than tool implementations because the LLM never sees your code—it only sees the schema and description.

## When to Use
- User mentions or implies: agent tool, function calling, tool schema, tool design, mcp server, mcp tool, tool use, build tool for agent, define function, input_schema, tool_use, or tool_result.

## Prerequisites
- Familiarity with JSON Schema.
- Node.js or Python environment for MCP server or tool runner implementation.
- API keys for external services (if tools call external APIs). Use `YOUR_KEY` placeholders; never commit live secrets.

## Procedure

### 1. Design the Tool Schema
Aim for fewer than 20 tools per agent to avoid confusion. Every tool needs a comprehensive description.

1.  **Write a detailed description.** The description should explain what the tool does, when to use it, what it returns, and what it does NOT do.
    ```json
    {
      "name": "get_stock_price",
      "description": "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. Returns the latest trade price in USD. Use when the user asks about current or recent stock prices. Does NOT provide historical data, company info, or predictions.",
      "input_schema": {
        "type": "object",
        "properties": {
          "ticker": {
            "type": "string",
            "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
          }
        },
        "required": ["ticker"]
      }
    }
    ```
2.  **Describe every parameter.** Include what it is, the expected format, an example value, and edge cases.
    ```json
    {
      "location": {
        "type": "string",
        "description": "City and state/country. Format: 'City, State' for US (e.g., 'San Francisco, CA') or 'City, Country' for international (e.g., 'Tokyo, Japan'). Do not use ZIP codes or coordinates."
      }
    }
    ```
3.  **Use enums to constrain values.**
    ```json
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "description": "Task priority level"
    }
    ```
4.  **Explicitly define required fields and strict mode.**
    ```json
    {
      "type": "object",
      "properties": { "query": {} },
      "required": ["query"],
      "additionalProperties": false
    }
    ```
5.  **Add input examples for complex tools.** Use realistic data, show minimal and full specification patterns, and keep it to 1-5 examples.
    ```json
    "input_examples": [
      {
        "title": "Team Standup",
        "start_time": "2024-03-15T09:00:00Z",
        "duration_minutes": 30,
        "attendees": ["alice@company.com"]
      }
    ]
    ```

### 2. Implement Error Handling
Silent failures poison agents. Return strings, not objects.

1.  **Return informative errors.** Include error type, a helpful message, and suggestions.
    ```json
    {
      "error": true,
      "error_type": "not_found",
      "message": "Location 'Atlantis' not found. Please provide a real city name like 'San Francisco, CA'.",
      "suggestions": ["San Francisco, CA", "Los Angeles, CA"]
    }
    ```
2.  **Use the `is_error` flag in tool results.**
    ```json
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "Error: Location 'Atlantis' not found.",
      "is_error": true
    }
    ```
3.  **Handle all error categories:** Input validation, external service errors (rate limits, timeouts), business logic errors (not found, permission denied), and internal errors.

### 3. Build MCP Tools (Optional)
Use MCP for reusable, cross-platform tools.

1.  **Define the tool list and schema.**
    ```typescript
    server.setRequestHandler("tools/list", async () => ({
      tools: [{
        name: "get_weather",
        description: "Get current weather for a location.",
        inputSchema: {
          type: "object",
          properties: {
            location: { type: "string", description: "City and state, e.g. 'San Francisco, CA'" }
          },
          required: ["location"]
        }
      }]
    }));
    ```
2.  **Handle tool calls and errors.**
    ```typescript
    server.setRequestHandler("tools/call", async (request) => {
      const { name, arguments: args } = request.params;
      if (name === "get_weather") {
        try {
          const weather = await fetchWeather(args.location);
          return { content: [{ type: "text", text: JSON.stringify(weather) }] };
        } catch (error) {
          return { content: [{ type: "text", text: `Error: ${error.message}` }], isError: true };
        }
      }
      throw new Error(`Unknown tool: ${name}`);
    });
    ```

### 4. Use Tool Runners (Optional)
SDK tool runners handle the tool call loop automatically.

1.  **Define tools with decorators (Python).**
    ```python
    @beta_tool
    def get_weather(location: str, unit: str = "fahrenheit") -> str:
        '''Get the current weather in a given location.
        Args:
            location: The city and state, e.g. San Francisco, CA
            unit: Temperature unit, either 'celsius' or 'fahrenheit'
        '''
        return json.dumps({"temperature": "72°F", "conditions": "Sunny"})
    ```
2.  **Run the tool loop.**
    ```python
    runner = client.beta.messages.tool_runner(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=[get_weather],
        messages=[{"role": "user", "content": "What's the weather in Paris?"}]
    )
    final = runner.until_done()
    ```

### 5. Handle Parallel Tool Execution
Claude can call multiple tools in one response. Execute them in parallel and return ALL results in a SINGLE user message.

1.  **Execute tools in parallel.**
    ```python
    async def execute_tools_parallel(tool_uses):
        tasks = [execute_tool(t) for t in tool_uses]
        return await asyncio.gather(*tasks)
    ```
2.  **Return all results together.**
    ```python
    tool_results = [
        {"type": "tool_result", "tool_use_id": "toolu_01", "content": "72°F, Sunny"},
        {"type": "tool_result", "tool_use_id": "toolu_02", "content": "45°F, Cloudy"}
    ]
    messages.append({"role": "user", "content": tool_results})
    ```

## Pitfalls
- **Vague descriptions:** Tool descriptions under 100 characters cause hallucination. Always detail when to use, parameters, and return values.
- **Missing parameter descriptions:** Every parameter needs a description, format, and example.
- **Silent failures:** Tools without `try/except` blocks and `is_error` flags poison the agent context.
- **Returning objects instead of strings:** LLMs process text. Always return `json.dumps()` or `JSON.stringify()`.
- **Separate messages for parallel results:** Returning parallel tool results in separate messages breaks the execution pattern. Always batch them into one message.
- **Too many tools:** More than 20 tools causes confusion. Consolidate or split agents.
- **String concatenation in SQL:** Never concatenate user input into SQL. Use parameterized queries.
- **Missing timeouts:** External API calls without timeouts can hang the agent. Always add a timeout parameter.

## Verification
1.  **Check description length:** Ensure tool descriptions are at least 100 characters and explain when to use the tool.
2.  **Check parameter descriptions:** Verify every parameter in `input_schema` has a `description` field.
3.  **Check required fields:** Ensure `required` array is explicitly defined in the schema.
4.  **Check error handling:** Verify tool functions have `try/except` blocks and return `is_error: true` on failure.
5.  **Check return types:** Ensure tools return strings, not dict/object.
6.  **Check input validation:** Verify LLM-provided inputs are validated before execution.
7.  **Check MCP schema:** Ensure all MCP tools have an `inputSchema` defined.

## Related Skills
- `multi-agent-orchestration`: For coordinating multiple tools across agents.
- `agent-memory-systems`: For persistent memory between tool calls.
- `api-designer`: For underlying API design.
- `prompt-engineering`: For LLM prompting techniques.
