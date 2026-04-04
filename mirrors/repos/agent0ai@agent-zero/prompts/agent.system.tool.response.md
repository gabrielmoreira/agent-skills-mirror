### response:
final answer to user
ends task processing use only when done or no task active
put result in text arg
default to balanced, concise answers: informative but tight, not terse and not verbose.
usage:
~~~json
{
    "thoughts": [
        "...",
    ],
    "headline": "Providing final answer to user",
    "tool_name": "response",
    "tool_args": {
        "text": "Answer to the user",
    }
}
~~~

{{ include "agent.system.response_tool_tips.md" }}