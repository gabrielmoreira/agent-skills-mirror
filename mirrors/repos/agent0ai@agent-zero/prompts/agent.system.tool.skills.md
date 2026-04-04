### skills_tool
use skills only when relevant
workflow:
- `skills_tool:list`: discover available skills
- `skills_tool:load`: load one skill by `skill_name`
after loading a skill, follow its instructions and use referenced files or scripts with other tools
reload a skill if its instructions are no longer in context
example:
~~~json
{
  "thoughts": ["A skill may already encode the workflow I need."],
  "headline": "Loading relevant skill",
  "tool_name": "skills_tool:load",
  "tool_args": {
    "skill_name": "playwright"
  }
}
~~~
