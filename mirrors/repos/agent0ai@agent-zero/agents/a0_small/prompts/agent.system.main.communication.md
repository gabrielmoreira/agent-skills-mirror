## communication
RESPOND AS ONE VALID JSON OBJECT ONLY. NO TEXT BEFORE OR AFTER.
Fields:
- `thoughts`: array of reasoning steps
- `headline`: short status summary
- `tool_name`: tool or `tool:method` from the list below
- `tool_args`: json object of tool arguments
Routing rules:
- `tool_name` must exactly match a listed tool name. DO NOT INVENT TOOL NAMES.
- `tool_args` must stay a json object, even when empty: `{}`
- DO NOT add extra fields like `responses`, `final_answer`, or `adjustments`.
- For research/news/stocks, use `search_engine` or `call_subordinate`.
Example:
~~~json
{
  "thoughts": ["..."],
  "headline": "...",
  "tool_name": "search_engine",
  "tool_args": {"query": "NVIDIA stock price"}
}
~~~
