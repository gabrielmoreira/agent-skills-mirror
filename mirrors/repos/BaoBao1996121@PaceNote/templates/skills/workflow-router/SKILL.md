---
name: workflow-router
description: |
  研发工作流入口 - 帮助用户快速进入正确的工作流阶段。
  触发关键词: 工作流, 流程, 从哪开始, 帮我, 我该怎么做, 下一步, 
  workflow, 不知道用什么, 新手引导, 怎么用
---

# 🚀 研发工作流入口

帮助用户快速定位当前所处的研发阶段，并引导到对应的 Skill。

---

## 触发后立即执行

使用 `ask_questions` 对话框引导用户选择当前阶段：

```
header: "工作流"
question: "请选择当前所处的研发阶段，我会引导你使用对应的工具："
options:
  - label: "📋 需求返讲"
    description: "拿到 PBI 后，分析需求、生成返讲文档、检查完整性"
    recommended: true
  - label: "📐 设计评审（圆桌会议）"
    description: "需求已明确，需要多角色生成设计文档"
  - label: "💻 编码实现"
    description: "设计方案已确认，按设计文档自动编码"
  - label: "🔍 技术调研 / 代码定位"
    description: "需要分析技术方案、定位代码、了解平台接口"
```

## 根据用户选择路由

### 选择「需求返讲」

输出引导：

```markdown
📋 **进入需求返讲模式** → `#pbi-reviewer`

请提供 PBI 信息（以下任一方式）：
1. DevOps 链接：`https://your-devops-server.example.com/YourProject
2. PBI 编号：`1073716`
3. PBI 标题：`PBI_Func_{{APP_NAME}}_Feature_XXX_功能优化
4. 直接粘贴 PBI 内容

💡 示例：`需求返讲 1073716`
```

然后加载 `#pbi-reviewer` Skill 并执行。

### 选择「设计评审」

输出引导：

```markdown
📐 **进入设计评审模式** → `#roundtable-debate`

请提供需求信息：
1. PBI 编号或内容
2. 如有返讲文档，可一并提供

💡 示例：`用圆桌会议分析 PBI 1073716`
```

然后加载 `#roundtable-debate` Skill 并执行。

### 选择「编码实现」

输出引导：

```markdown
💻 **进入编码模式** → `#coding-agent`

编码前请确认：
1. ✅ 设计方案已经过团队评审
2. ✅ `.copilot-temp/roundtable-{NNN}/` 中有设计文档

💡 直接说：`根据设计编码` 或 `开始编码`
```

然后加载 `#coding-agent` Skill 并执行。

### 选择「技术调研 / 代码定位」

输出引导：

```markdown
🔍 **进入技术调研模式** → `#coding-agent`

请描述你的问题：
- 需要定位哪个功能的代码？
- 需要了解哪个接口/组件？
- 需要制定什么技术方案？

💡 示例：`帮我分析 DataLoad 的加载流程`
```

然后加载 `#coding-agent` Skill 并执行。
