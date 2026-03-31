# SKILL 机制集成指南

本文档说明如何将 SKILL 机制集成到现有的 DB-GPT agent 中。

## 集成步骤

### 1. 导入 SKILL 模块

在需要使用 SKILL 的文件中添加导入：

```python
from dbgpt.agent.skill import (
    Skill,
    SkillBuilder,
    SkillLoader,
    SkillManager,
    SkillType,
    get_skill_manager,
    initialize_skill,
)
```

### 2. 修改 Agent 类以支持 Skill

在你的 Agent 类中添加 Skill 支持：

```python
from dbgpt.agent.expand.tool_assistant_agent import ToolAssistantAgent
from dbgpt.agent.skill import Skill

class SkillEnabledAgent(ToolAssistantAgent):
    def __init__(self, skill: Optional[Skill] = None, **kwargs):
        super().__init__(**kwargs)
        self._skill = skill

        if self._skill:
            self._apply_skill_to_profile()

    @property
    def skill(self) -> Optional[Skill]:
        return self._skill

    def _apply_skill_to_profile(self):
        """应用 Skill 配置到 Agent profile。"""
        if self.skill.prompt_template:
            self.bind_prompt = self.skill.prompt_template

        if self.profile:
            self.profile.goal = self.skill.metadata.description

    async def load_resource(self, question: str, is_retry_chat: bool = False):
        """加载 Skill 所需的资源。"""
        if self.skill:
            await self._load_skill_resources()
        return await super().load_resource(question, is_retry_chat)

    async def _load_skill_resources(self):
        """加载 Skill 所需的工具和知识。"""
        if not self.resource:
            return

        # 检查必需的工具
        if self.skill.required_tools:
            available_tools = self.resource.get_resource_by_type("tool")
            available_tool_names = [t.name for t in available_tools]

            for required_tool in self.skill.required_tools:
                if required_tool not in available_tool_names:
                    raise ValueError(
                        f"Required tool '{required_tool}' not found. "
                        f"Available tools: {available_tool_names}"
                    )

        # 检查必需的知识库
        if self.skill.required_knowledge:
            available_knowledge = self.resource.get_resource_by_type("knowledge")
            available_knowledge_names = [k.name for k in available_knowledge]

            for required_knowledge in self.skill.required_knowledge:
                if required_knowledge not in available_knowledge_names:
                    raise ValueError(
                        f"Required knowledge '{required_knowledge}' not found. "
                        f"Available knowledge: {available_knowledge_names}"
                    )
```

### 3. 初始化 Skill Manager

在应用启动时初始化 Skill Manager：

```python
from dbgpt.component import SystemApp

def initialize_app():
    system_app = SystemApp()
    initialize_skill(system_app)
    return system_app
```

### 4. 注册 Skill

```python
from dbgpt.agent.skill import get_skill_manager

def register_my_skills(system_app):
    skill_manager = get_skill_manager(system_app)

    # 创建并注册 Skill
    skill = (
        SkillBuilder(name="my_skill", description="My skill description")
        .with_skill_type(SkillType.Chat)
        .with_prompt_template("You are a helpful assistant.")
        .build()
    )

    skill_manager.register_skill(
        skill_instance=skill,
        name="my_skill",
    )
```

### 5. 使用 Skill 创建 Agent

```python
from dbgpt.agent import AgentContext, LLMConfig, AgentMemory

async def create_agent_with_skill():
    # 获取 Skill
    skill_manager = get_skill_manager()
    skill = skill_manager.get_skill(name="my_skill")

    # 创建 Agent
    agent = SkillEnabledAgent(skill=skill)

    # 绑定配置
    context = AgentContext(conv_id="test_conv")
    llm_config = LLMConfig()
    memory = AgentMemory()

    await agent.bind(context).bind(llm_config).bind(memory).build()

    return agent
```

## 修改现有 Agent 示例

### 示例：修改 IntentRecognitionAgent

原始文件：`packages/dbgpt-serve/src/dbgpt_serve/agent/agents/expand/intent_recognition_agent.py`

```python
import logging
from dbgpt.agent import ConversableAgent, get_agent_manager
from dbgpt.agent.core.profile import DynConfig, ProfileConfig
from dbgpt.agent.skill import Skill
from dbgpt_serve.agent.agents.expand.actions.intent_recognition_action import (
    IntentRecognitionAction,
)

class IntentRecognitionAgent(ConversableAgent):
    profile: ProfileConfig = ProfileConfig(...)

    def __init__(self, skill: Optional[Skill] = None, **kwargs):
        super().__init__(**kwargs)
        self._skill = skill
        self._init_actions([IntentRecognitionAction])

        if self._skill:
            self._apply_skill_to_profile()

    @property
    def skill(self) -> Optional[Skill]:
        return self._skill

    def _apply_skill_to_profile(self):
        if self.skill and self.skill.prompt_template:
            self.bind_prompt = self.skill.prompt_template

agent_manage = get_agent_manager()
agent_manage.register_agent(IntentRecognitionAgent)
```

## SKILL 文件格式

### JSON 格式

```json
{
  "metadata": {
    "name": "intent_recognition",
    "description": "Intent recognition skill for user queries",
    "version": "1.0.0",
    "author": "DB-GPT Team",
    "skill_type": "custom",
    "tags": ["intent", "recognition", "nlp"]
  },
  "prompt_template": "You are an intent recognition expert. Analyze user queries and identify their intents.",
  "required_tools": [],
  "required_knowledge": [],
  "config": {
    "max_intents": 10,
    "enable_slot_filling": true
  }
}
```

### Python 格式

```python
from dbgpt.agent.skill import Skill, SkillMetadata, SkillType
from dbgpt.core import PromptTemplate

class IntentRecognitionSkill(Skill):
    def __init__(self):
        metadata = SkillMetadata(
            name="intent_recognition",
            description="Intent recognition skill",
            version="1.0.0",
            skill_type=SkillType.Custom,
            tags=["intent", "recognition"],
        )
        prompt = PromptTemplate.from_template(
            "You are an intent recognition expert."
        )
        super().__init__(
            metadata=metadata,
            prompt_template=prompt,
            config={"max_intents": 10},
        )
```

## 测试 SKILL 集成

```python
import pytest
from dbgpt.agent.skill import SkillBuilder, SkillType

def test_skill_integration():
    # 创建 Skill
    skill = (
        SkillBuilder(name="test_skill", description="Test skill")
        .build()
    )

    # 创建 Agent
    agent = SkillEnabledAgent(skill=skill)

    # 验证
    assert agent.skill is not None
    assert agent.skill.metadata.name == "test_skill"
```

## 最佳实践

1. **分离关注点**：Skill 应该专注于特定领域的能力
2. **版本管理**：为 Skill 使用语义化版本号
3. **依赖声明**：清晰声明 Skill 所需的工具和知识
4. **文档完善**：为 Skill 编写详细的文档和示例
5. **测试覆盖**：为每个 Skill 编写单元测试

## 常见问题

### Q: 如何动态切换 Skill？

A: 在 Agent 中添加 `switch_skill` 方法：

```python
def switch_skill(self, skill: Skill):
    self._skill = skill
    self._apply_skill_to_profile()
```

### Q: Skill 可以包含多个工具吗？

A: 可以，使用 `with_required_tool` 多次添加：

```python
skill = (
    SkillBuilder(name="multi_tool", description="Multi tool skill")
    .with_required_tool("tool1")
    .with_required_tool("tool2")
    .with_required_tool("tool3")
    .build()
)
```

### Q: 如何从文件加载 Skill？

A: 使用 `SkillLoader`：

```python
from dbgpt.agent.skill import SkillLoader

loader = SkillLoader()
skill = loader.load_skill_from_file("path/to/skill.json")
```
