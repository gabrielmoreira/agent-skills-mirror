# SKILL 机制 - DB-GPT Agent 技能加载系统

## 概述

SKILL 机制是 DB-GPT Agent 框架的高级特性，允许 Agent 加载和管理预定义的技能包，实现 Agent 能力的模块化和可复用性。

## 核心文件

```
packages/dbgpt-core/src/dbgpt/agent/skill/
├── __init__.py           # 模块入口，导出主要类
├── base.py              # Skill 基础类定义
├── parameters.py        # Skill 参数类
├── manage.py           # Skill 管理器
└── loader.py           # Skill 加载器和构建器
```

## 主要特性

### 1. Skill 定义

Skill 包含以下组件：
- **Metadata**：技能元信息（名称、描述、版本、类型、标签）
- **Prompt Template**：系统提示词模板
- **Required Tools**：所需的工具列表
- **Required Knowledge**：所需的知识库列表
- **Actions**：可执行的动作
- **Config**：特定配置参数

### 2. Skill 类型

| 类型 | 说明 |
|------|------|
| `Coding` | 编程技能 |
| `DataAnalysis` | 数据分析技能 |
| `WebSearch` | 网络搜索技能 |
| `KnowledgeQA` | 知识问答技能 |
| `Chat` | 对话技能 |
| `Custom` | 自定义技能 |

## 快速开始

### 1. 创建 Skill

```python
from dbgpt.agent.skill import SkillBuilder, SkillType

skill = (
    SkillBuilder(name="my_skill", description="My awesome skill")
    .with_version("1.0.0")
    .with_author("Your Name")
    .with_skill_type(SkillType.Coding)
    .with_tags(["coding", "python"])
    .with_prompt_template(
        "You are a coding assistant. Help users write clean, efficient code."
    )
    .with_required_tool("python_interpreter")
    .build()
)
```

### 2. 注册 Skill

```python
from dbgpt.agent.skill import get_skill_manager, initialize_skill
from dbgpt.component import SystemApp

system_app = SystemApp()
initialize_skill(system_app)
skill_manager = get_skill_manager(system_app)

skill_manager.register_skill(
    skill_instance=skill,
    name="my_awesome_skill",
)
```

### 3. 创建 Skill-based Agent

```python
from dbgpt.agent import ConversableAgent
from dbgpt.agent.skill import Skill

class SkillBasedAgent(ConversableAgent):
    def __init__(self, skill: Skill, **kwargs):
        super().__init__(**kwargs)
        self._skill = skill
        self._apply_skill_to_profile()

    @property
    def skill(self) -> Skill:
        return self._skill
```

### 4. 使用 Agent

```python
agent = SkillBasedAgent(skill=skill)
await agent.bind(context).bind(llm_config).bind(memory).build()
```

## API 参考

### SkillBuilder

| 方法 | 参数 | 说明 |
|------|------|------|
| `with_version(version)` | version: str | 设置版本 |
| `with_author(author)` | author: str | 设置作者 |
| `with_skill_type(type)` | type: SkillType | 设置技能类型 |
| `with_tags(tags)` | tags: List[str] | 设置标签 |
| `with_prompt_template(template)` | template: str | 设置提示词模板 |
| `with_required_tool(name)` | name: str | 添加必需工具 |
| `with_required_knowledge(name)` | name: str | 添加必需知识库 |
| `with_action(action)` | action: Any | 添加动作 |
| `with_config(config)` | config: Dict | 设置配置 |
| `build()` | - | 构建 Skill |

### SkillManager

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `register_skill()` | skill_cls, skill_instance, name, metadata | None | 注册技能 |
| `get_skill()` | name, skill_type, version | SkillBase | 获取技能 |
| `get_skills_by_type()` | skill_type | List[SkillBase] | 按类型获取技能 |
| `list_skills()` | - | List[Dict] | 列出所有技能 |

### SkillLoader

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `load_skill_from_file()` | file_path | Optional[SkillBase] | 从文件加载技能 |
| `load_skill_from_module()` | module_path | Optional[SkillBase] | 从模块加载技能 |
| `load_skills_from_directory()` | directory, recursive | List[SkillBase] | 从目录加载所有技能 |

## 文件格式

### JSON 格式

```json
{
  "metadata": {
    "name": "web_search_assistant",
    "description": "Web search assistant",
    "version": "1.0.0",
    "author": "DB-GPT Team",
    "skill_type": "web_search",
    "tags": ["web", "search"]
  },
  "prompt_template": "You are a web search assistant.",
  "required_tools": ["google_search"],
  "required_knowledge": [],
  "config": {}
}
```

### Python 格式

```python
from dbgpt.agent.skill import Skill, SkillMetadata, SkillType
from dbgpt.core import PromptTemplate

class CustomSkill(Skill):
    def __init__(self):
        metadata = SkillMetadata(
            name="custom_skill",
            description="A custom skill",
            version="1.0.0",
            skill_type=SkillType.Custom,
        )
        prompt = PromptTemplate.from_template("You are a custom assistant.")
        super().__init__(
            metadata=metadata,
            prompt_template=prompt,
        )
```

## 示例

### 完整示例

查看 `examples/agents/skill_agent_example.py` 获取完整的使用示例。

### 技能文件

- `skills/web_search_skill.json` - 网络搜索技能示例
- `skills/data_analysis_skill.json` - 数据分析技能示例

### 实现指南

- `skills/skill_implementation_guide.py` - 详细的实现指南
- `skills/INTEGRATION_GUIDE.md` - 集成到现有 Agent 的指南

## 集成步骤

1. **导入 SKILL 模块**
   ```python
   from dbgpt.agent.skill import Skill, SkillBuilder, get_skill_manager
   ```

2. **修改 Agent 类**
   ```python
   class MyAgent(ConversableAgent):
       def __init__(self, skill: Optional[Skill] = None, **kwargs):
           super().__init__(**kwargs)
           self._skill = skill
           if self._skill:
               self._apply_skill_to_profile()
   ```

3. **初始化 Skill Manager**
   ```python
   from dbgpt.component import SystemApp
   system_app = SystemApp()
   initialize_skill(system_app)
   ```

4. **注册并使用 Skill**
   ```python
   skill_manager = get_skill_manager(system_app)
   skill_manager.register_skill(skill_instance=skill)
   agent = MyAgent(skill=skill)
   ```

## 高级用法

### 动态 Skill 切换

```python
class DynamicSkillAgent(ConversableAgent):
    def switch_skill(self, skill_name: str):
        self._skill = self._skills[skill_name]
        self._apply_skill_to_profile()
```

### 多 Skill 组合

```python
class CompositeSkillAgent(ConversableAgent):
    def __init__(self, skills: List[Skill], **kwargs):
        super().__init__(**kwargs)
        self._skills = skills

    def get_all_tools(self) -> List[str]:
        all_tools = []
        for skill in self._skills:
            all_tools.extend(skill.required_tools)
        return list(set(all_tools))
```

## 最佳实践

1. **模块化设计**：每个 Skill 专注于单一领域
2. **版本管理**：使用语义化版本号（如 1.0.0）
3. **依赖声明**：清晰声明所需的工具和知识库
4. **文档完善**：为 Skill 编写详细的文档
5. **测试覆盖**：为每个 Skill 编写单元测试

## 故障排除

### 常见问题

**Q: Skill 加载失败？**
A: 检查文件路径、JSON 格式是否正确

**Q: 找不到必需的工具？**
A: 确保在绑定 Agent 时提供了所有必需的工具

**Q: 提示词模板不生效？**
A: 确保在 `_apply_skill_to_profile` 中正确设置了 `bind_prompt`

## 贡献指南

欢迎贡献新的 Skill！请遵循以下步骤：

1. Fork 项目
2. 创建新的 Skill 文件
3. 编写测试
4. 提交 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
