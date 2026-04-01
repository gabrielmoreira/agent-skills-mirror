from typing import Any, TYPE_CHECKING

from helpers.files import VariablesPlugin
from helpers import projects, subagents

if TYPE_CHECKING:
    from agent import Agent


class CallSubordinate(VariablesPlugin):
    def get_variables(
        self, file: str, backup_dirs: list[str] | None = None, **kwargs
    ) -> dict[str, Any]:
        agent: Agent | None = kwargs.get("_agent", None)
        project = projects.get_context_project_name(agent.context) if agent else None
        agents = subagents.get_available_agents_dict(project)
        if not agents:
            return {"agent_profiles": ""}

        lines: list[str] = []
        for name in sorted(agents.keys()):
            title = (agents[name].title or name).replace("\n", " ").strip()
            lines.append(f"- {name}: {title}")
        return {"agent_profiles": "\n".join(lines)}
