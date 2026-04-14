### skills_tool
use skills only when relevant
workflow:
- `skills_tool:search`: find candidate skills by keywords or trigger phrases from the current task
- `skills_tool:list`: discover available skills
- `skills_tool:load`: load one skill by `skill_name`
after loading a skill, follow its instructions and use referenced files or scripts with other tools
reload a skill if its instructions are no longer in context
example:
~~~json
{
  "thoughts": ["The user's request sounds like a skill trigger phrase, so I should search first."],
  "headline": "Searching for relevant skill",
  "tool_name": "skills_tool:search",
  "tool_args": {
    "query": "set up a0 cli connector"
  }
}
~~~
