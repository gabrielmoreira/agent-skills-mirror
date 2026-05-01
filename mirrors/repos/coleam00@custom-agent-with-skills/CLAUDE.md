# Custom Skill-Based Pydantic AI Agent Development Instructions

## Project Overview

Framework-agnostic skill system for AI agents that extracts the progressive disclosure pattern from Claude Skills and implements it as a native feature in Pydantic AI. This system enables developers to build AI agents with modular, reusable skills that load instructions and resources on-demand, eliminating context window constraints while maintaining type safety and testability.

**Key Innovation**: Unlike Claude Skills which are locked to the Claude ecosystem, this implementation makes advanced skill capabilities available to ANY AI agent framework. Demonstrates how to take successful patterns from proprietary systems and apply them to open frameworks.

## Core Principles

1. **FRAMEWORK AGNOSTIC**
   - Skills work with any AI framework, not just Claude
   - No vendor lock-in to Claude Desktop/Code
   - Portable skills across different agent implementations

2. **PROGRESSIVE DISCLOSURE IS KEY**
   - Level 1: Metadata in system prompt (~100 tokens/skill)
   - Level 2: Full instructions loaded via tool call
   - Level 3: Resources loaded via tool call only when referenced
   - Never consume unnecessary context

3. **TYPE SAFETY IS NON-NEGOTIABLE**
   - All functions, methods, and variables MUST have type annotations
   - Use Pydantic models for all data structures (skills, metadata)
   - No `Any` types without explicit justification
   - Pydantic Settings for configuration

4. **KISS** (Keep It Simple, Stupid)
   - Prefer simple, readable solutions over clever abstractions
   - Don't build fallback mechanisms unless absolutely necessary
   - Trust the progressive disclosure pattern - don't over-engineer

5. **YAGNI** (You Aren't Gonna Need It)
   - Don't build features until they're actually needed
   - MVP first, enhancements later
   - Focus on demonstrating the core pattern

6. **REFERENCE THE EXAMPLES FOLDER**
   - `examples/` contains production-quality MongoDB RAG agent
   - **DO NOT MODIFY** files in `examples/` - they are reference only
   - Copy patterns and code from examples, adapt for skills
   - Maintain same architecture and design patterns

**Architecture:**

```
custom-skill-agent/
├── src/                      # Skill-based agent implementation
│   ├── agent.py              # Pydantic AI agent with skills
│   ├── skill_loader.py       # Skill discovery and metadata
│   ├── skill_tools.py        # Progressive disclosure tools
│   ├── dependencies.py       # AgentDependencies with SkillLoader
│   ├── providers.py          # LLM provider configuration
│   ├── settings.py           # Pydantic Settings
│   ├── prompts.py            # Skill-aware system prompts
│   └── cli.py                # Rich-based CLI
├── skills/                   # Skill library
│   ├── weather/              # Simple skill demo
│   └── code_review/          # Advanced skill demo
├── examples/                 # MongoDB RAG reference (DO NOT MODIFY)
└── tests/                    # Test suite
```

---

## Documentation Style

**Use Google-style docstrings** for all functions, classes, and modules:

```python
async def load_skill(
    ctx: RunContext[AgentDependencies],
    skill_name: str
) -> str:
    """
    Load the full instructions for a skill (Level 2 progressive disclosure).

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to load

    Returns:
        Full skill instructions from SKILL.md

    Raises:
        ValueError: If skill not found
    """
```

---

## Development Workflow

**Setup environment:**
```bash
# Create virtual environment
python -m venv .venv

# Activate environment
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
# Or if using uv:
uv pip install -e .
```

**Run CLI agent:**
```bash
python -m src.cli
```

**Run tests:**
```bash
pytest tests/ -v
```

---

## Configuration Management

### Environment Variables

**ALL configuration in .env file:**
```bash
# LLM Provider
LLM_PROVIDER=openrouter
LLM_API_KEY=sk-or-v1-...
LLM_MODEL=anthropic/claude-sonnet-4.5
LLM_BASE_URL=https://openrouter.ai/api/v1

# Skills Configuration
SKILLS_DIR=skills

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
```

### Pydantic Settings

**Use Pydantic Settings for type-safe configuration:**
```python
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    skills_dir: Path = Field(default=Path("skills"))
    llm_api_key: str = Field(..., description="LLM provider API key")
    llm_model: str = Field(default="anthropic/claude-sonnet-4.5")
```

---

## Progressive Disclosure Pattern

### The Three Levels

**Level 1 - Metadata Discovery (Always Loaded)**
```yaml
# In system prompt - minimal tokens (~100 per skill)
---
name: weather
description: Get weather information for locations. Use when user asks about weather.
---
```

**Level 2 - Full Instructions (Loaded on Invocation)**
```python
# Agent decides skill is needed
agent.call_tool("load_skill", skill_name="weather")
# Returns: Full SKILL.md body with detailed instructions
```

**Level 3 - Resources (Loaded on Demand)**
```python
# Instructions reference a resource
"See references/api_reference.md for API documentation"

# Agent loads resource
agent.call_tool("read_skill_file",
    skill_name="weather",
    file_path="references/api_reference.md"
)
# Returns: Full API reference documentation
```

### Skill Directory Structure

**Every skill follows this pattern:**
```
skills/skill-name/
├── SKILL.md                 # YAML frontmatter + instructions
├── scripts/                 # Optional: Python/Bash scripts
│   └── helper.py
├── references/              # Optional: Documentation, guides
│   ├── api_reference.md
│   └── best_practices.md
└── assets/                  # Optional: Templates, data files
    └── template.txt
```

### SKILL.md Format

**Required structure:**
```markdown
---
name: skill-name
description: Brief description for agent discovery (1-2 sentences)
version: 1.0.0
author: Your Name
---

# Skill Name

Brief overview of what this skill does.

## When to Use

- Scenario 1
- Scenario 2
- Scenario 3

## Available Operations

1. Operation 1: Description
2. Operation 2: Description

## Instructions

Step-by-step instructions for using this skill...

## Resources

- `references/api_docs.md` - Detailed API documentation
- `scripts/helper.py` - Helper script for complex operations

## Examples

### Example 1: Simple Use Case
User asks: "What's the weather in NYC?"
Response: Call weather API, format response...

## Notes

Additional considerations or limitations.
```

---

## Skill Loader Implementation

### SkillLoader Class

**Core responsibilities:**
1. Scan `skills/` directory for skill folders
2. Parse YAML frontmatter from SKILL.md files
3. Maintain skill metadata registry
4. Generate system prompt section with skill metadata

**Key methods:**
```python
class SkillLoader:
    def discover_skills(self) -> List[SkillMetadata]:
        """Scan skills directory and extract metadata from all SKILL.md files."""

    def get_skill_metadata_prompt(self) -> str:
        """Generate system prompt section with all skill metadata."""

    def _parse_skill_metadata(self, skill_md: Path, skill_dir: Path) -> SkillMetadata:
        """Extract YAML frontmatter from SKILL.md."""
```

### SkillMetadata Model

**Pydantic model for type-safe metadata:**
```python
from pydantic import BaseModel
from pathlib import Path

class SkillMetadata(BaseModel):
    """Skill metadata from YAML frontmatter."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    skill_path: Path
```

---

## Skill Tools (Progressive Disclosure)

### Tool 1: load_skill (Level 2)

**Purpose**: Load full instructions when agent decides to use a skill

```python
async def load_skill(
    ctx: RunContext[AgentDependencies],
    skill_name: str
) -> str:
    """
    Load the full instructions for a skill.

    This implements Level 2 progressive disclosure - loading the full SKILL.md
    when the agent decides to use a skill.
    """
    skill_loader = ctx.deps.skill_loader

    if skill_name not in skill_loader.skills:
        return f"Error: Skill '{skill_name}' not found. Available: {list(skill_loader.skills.keys())}"

    skill = skill_loader.skills[skill_name]
    skill_md = skill.skill_path / "SKILL.md"

    # Read and return full content (minus frontmatter)
    content = skill_md.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()

    return content
```

### Tool 2: read_skill_file (Level 3)

**Purpose**: Load specific resource files when instructions reference them

```python
async def read_skill_file(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    file_path: str
) -> str:
    """
    Read a file from a skill's directory (Level 3 progressive disclosure).

    Security: Validates file is within skill directory to prevent traversal.
    """
    skill_loader = ctx.deps.skill_loader

    if skill_name not in skill_loader.skills:
        return f"Error: Skill '{skill_name}' not found"

    skill = skill_loader.skills[skill_name]
    target_file = skill.skill_path / file_path

    # Security: ensure file is within skill directory
    if not target_file.resolve().is_relative_to(skill.skill_path.resolve()):
        return f"Error: Access denied - file must be within skill directory"

    if not target_file.exists():
        return f"Error: File not found: {file_path}"

    return target_file.read_text()
```

### Tool 3: list_skill_files (Resource Discovery)

**Purpose**: Help agent discover what resources are available

```python
async def list_skill_files(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    directory: str = ""
) -> str:
    """
    List files available in a skill's directory.

    Helps the agent discover what resources are available.
    """
    skill_loader = ctx.deps.skill_loader

    if skill_name not in skill_loader.skills:
        return f"Error: Skill '{skill_name}' not found"

    skill = skill_loader.skills[skill_name]
    target_dir = skill.skill_path / directory if directory else skill.skill_path

    if not target_dir.exists():
        return f"Error: Directory not found: {directory}"

    files = []
    for item in target_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(skill.skill_path)
            files.append(str(rel_path))

    return "Files available:\n" + "\n".join(f"- {f}" for f in sorted(files))
```

---

## Agent Dependencies

**Adapted from examples/dependencies.py but simpler (no database):**

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path
from src.skill_loader import SkillLoader
from src.settings import load_settings

@dataclass
class AgentDependencies:
    """Dependencies injected into the agent context."""

    # Skill system
    skill_loader: Optional[SkillLoader] = None

    # Session context
    session_id: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)

    # Configuration
    settings: Optional[Any] = None

    async def initialize(self) -> None:
        """Initialize skill loader and settings."""
        if not self.settings:
            self.settings = load_settings()

        if not self.skill_loader:
            skills_dir = Path(self.settings.skills_dir)
            self.skill_loader = SkillLoader(skills_dir)
            self.skill_loader.discover_skills()

            print(f"Loaded {len(self.skill_loader.skills)} skills:")
            for skill in self.skill_loader.skills.values():
                print(f"  - {skill.name}: {skill.description}")
```

---

## Pydantic AI Agent Integration

### Agent Definition

**Dynamic system prompt with skill metadata:**

```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from src.providers import get_llm_model
from src.dependencies import AgentDependencies
from src.prompts import MAIN_SYSTEM_PROMPT

class AgentState(BaseModel):
    """Minimal shared state for the agent."""
    pass

# Create agent
skill_agent = Agent(
    get_llm_model(),
    deps_type=AgentDependencies,
    system_prompt=""  # Will be set dynamically
)

# Dynamic system prompt with skill metadata
@skill_agent.system_prompt
async def get_system_prompt(ctx: RunContext[AgentDependencies]) -> str:
    """Generate system prompt with skill metadata."""
    # Initialize dependencies to get skill loader
    await ctx.deps.initialize()

    # Get skill metadata for prompt
    skill_metadata = ctx.deps.skill_loader.get_skill_metadata_prompt()

    # Inject into base prompt
    return MAIN_SYSTEM_PROMPT.format(skill_metadata=skill_metadata)
```

### Tool Registration

**Register skill tools with agent:**

```python
from src.skill_tools import load_skill, read_skill_file, list_skill_files

@skill_agent.tool
async def load_skill_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str
) -> str:
    """Load full instructions for a skill."""
    return await load_skill(ctx, skill_name)

@skill_agent.tool
async def read_skill_file_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    file_path: str
) -> str:
    """Read a file from a skill's directory."""
    return await read_skill_file(ctx, skill_name, file_path)

@skill_agent.tool
async def list_skill_files_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    directory: str = ""
) -> str:
    """List files available in a skill's directory."""
    return await list_skill_files(ctx, skill_name, directory)
```

---

## Testing

**Tests mirror the src directory structure:**

```
src/agent.py            →  tests/test_agent.py
src/skill_loader.py     →  tests/test_skill_loader.py
src/skill_tools.py      →  tests/test_skill_tools.py
```

### Unit Tests

```python
import pytest
from pathlib import Path
from src.skill_loader import SkillLoader, SkillMetadata

@pytest.mark.unit
def test_skill_loader_discovers_skills(tmp_path):
    """Test that skill loader discovers skills correctly."""
    # Create dummy skill
    skill_dir = tmp_path / "test_skill"
    skill_dir.mkdir()

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("""---
name: test_skill
description: A test skill
version: 1.0.0
---

# Test Skill

This is a test.
""")

    # Test discovery
    loader = SkillLoader(tmp_path)
    skills = loader.discover_skills()

    assert len(skills) == 1
    assert skills[0].name == "test_skill"
    assert skills[0].description == "A test skill"
```

### Integration Tests

```python
@pytest.mark.integration
async def test_agent_loads_skill(skill_agent, mock_skill):
    """Test that agent can load a skill via tool call."""
    deps = AgentDependencies()
    await deps.initialize()

    # Create context
    ctx = RunContext(deps=deps)

    # Load skill
    result = await load_skill(ctx, "test_skill")

    assert "Test Skill" in result
    assert result.startswith("# Test Skill")
```

---

## Common Pitfalls

### 1. Forgetting to Parse Frontmatter

```python
# ❌ WRONG - Returns frontmatter + body
def load_skill_wrong(skill_path):
    return skill_path.read_text()

# ✅ CORRECT - Strip frontmatter, return only body
def load_skill_correct(skill_path):
    content = skill_path.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content
```

### 2. Missing File Path Security

```python
# ❌ WRONG - Directory traversal vulnerability
target_file = skill_path / file_path

# ✅ CORRECT - Validate file is within skill directory
target_file = skill_path / file_path
if not target_file.resolve().is_relative_to(skill_path.resolve()):
    raise SecurityError("File must be within skill directory")
```

### 3. Not Initializing Dependencies

```python
# ❌ WRONG - Dependencies not initialized
@skill_agent.tool
async def load_skill_tool(ctx: RunContext[AgentDependencies], skill_name: str) -> str:
    return await load_skill(ctx, skill_name)  # ctx.deps.skill_loader is None!

# ✅ CORRECT - Initialize dependencies first
@skill_agent.system_prompt
async def get_system_prompt(ctx: RunContext[AgentDependencies]) -> str:
    await ctx.deps.initialize()  # Initialize before using
    return generate_prompt(ctx.deps.skill_loader)
```

### 4. Missing Type Hints

```python
# ❌ WRONG - No type hints
def load_skill(ctx, skill_name):
    return ctx.deps.skill_loader.skills[skill_name]

# ✅ CORRECT - Full type hints
async def load_skill(
    ctx: RunContext[AgentDependencies],
    skill_name: str
) -> str:
    return await ctx.deps.skill_loader.load_skill(skill_name)
```

---

## Quick Reference

**Skill Discovery:**
```python
loader = SkillLoader(Path("skills"))
skills = loader.discover_skills()
prompt_section = loader.get_skill_metadata_prompt()
```

**Progressive Disclosure:**
```python
# Level 1: Metadata in system prompt (automatic)
# Level 2: Load full instructions
instructions = await load_skill(ctx, "weather")

# Level 3: Load resources
api_docs = await read_skill_file(ctx, "weather", "references/api_reference.md")
```

**Pydantic AI Agent:**
```python
# Define agent
agent = Agent(model, deps_type=AgentDependencies, system_prompt="")

# Add dynamic system prompt
@agent.system_prompt
async def get_prompt(ctx: RunContext[AgentDependencies]) -> str:
    await ctx.deps.initialize()
    return generate_prompt_with_skills(ctx.deps.skill_loader)

# Add tool
@agent.tool
async def tool_func(ctx: RunContext[AgentDependencies], arg: str) -> str:
    """Tool description."""
    pass
```

---

## Implementation-Specific References

For detailed implementation patterns, see:

- **PRD**: `.claude/PRD.md` - Complete product requirements and architecture
- **Examples Reference**: `examples/` - Production MongoDB RAG agent patterns
  - `examples/agent.py` - Pydantic AI agent structure
  - `examples/dependencies.py` - Dependency injection pattern
  - `examples/cli.py` - Rich CLI with streaming
  - `examples/settings.py` - Pydantic Settings configuration

---

## Workshop Context

This project serves as a workshop demonstration showing how to:
1. Extract successful patterns from proprietary systems (Claude Skills)
2. Implement those patterns in open frameworks (Pydantic AI)
3. Build framework-agnostic, reusable components
4. Scale beyond context window limitations through progressive disclosure

**Key Demonstration Points:**
- Progressive disclosure eliminates context window constraints
- Skills are portable across any AI framework
- Type-safe, testable agent architecture
- Simple, understandable implementation

**Workshop Deliverables:**
- Complete working skill-based agent
- Two demo skills (Weather, Code Review)
- Clear documentation of progressive disclosure pattern
- Attendees can extend with their own skills
