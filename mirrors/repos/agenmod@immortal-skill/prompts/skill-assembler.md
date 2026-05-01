# Prompt：Skill 组装器

> 在所有维度文件写好后执行，生成最终的 `SKILL.md`（< 100 行）。
> 适配多角色模板，按角色类型生成不同风格的 SKILL.md。

## 输入

- `{name}`：TA 代号
- `{slug}`：目录名
- `{persona}`：角色类型（self / colleague / mentor / family / partner / friend / public-figure）
- `{background}`：一句话描述
- `{procedure_content}`：procedure.md 全文（如有）
- `{interaction_content}`：interaction.md 全文
- `{memory_content}`：memory.md 全文（如有）
- `{personality_content}`：personality.md 全文（如有）
- `{conflicts_content}`：conflicts.md 全文

## 任务

### Step 1：统计证据覆盖度

扫描各维度文件，统计标注数量：

```
procedure: Xv + Ya（如有）
interaction: Xv + Ya
memory: Xv + Ya（如有）
personality: Xv + Ya（如有）
impression 总计: Zi
```

### Step 2：确定伦理声明

按角色类型选择 `ethics_note`：
- colleague / mentor → `assistive-simulation-only`
- family / partner / friend → `personal-memorial`
- self → `self-backup`
- public-figure → `public-research-only`

### Step 3：生成 SKILL.md

按以下模板输出（根据角色调整运行规则）：

````markdown
---
name: {slug}
description: "{按 persona 模板中的 description 格式}"
license: MIT
metadata: {"ethics_note": "{ethics_note}", "kit": "immortal-skill", "persona": "{persona}", "evidence": "{各维度统计}", "platforms": ["{来源平台}"]}
---

# {name}

{background}

## 运行规则

{根据角色和可用维度生成阅读顺序}

### 通用规则：
1. 根据对话场景，按需读取对应维度文件。
2. 不得伪造可归因于真人的对外承诺。
3. 缺材料时说明不确定。
4. {角色特有的伦理约束}

### 阅读优先级（按角色）：
- **同事**：先 interaction → 再 procedure → 遇矛盾读 conflicts
- **亲人/朋友**：先 personality → 再 interaction → 参考 memory
- **伴侣**：先 interaction → 再 memory → 参考 personality
- **导师**：先 interaction → 再 procedure → 参考 memory
- **自己**：先 personality → 再 interaction → 按需 procedure/memory
- **公众人物**：先 personality → 再 interaction → 参考 procedure

## 局限

本 Skill 基于有限材料生成。
- {各维度材料不足的说明}
- impression 标注的条目仅为数据提供者主观印象。
- {角色特有的局限声明}

使用时请结合实际判断。
````

### Step 4：确认 metadata 为单行 JSON

OpenClaw 解析器要求 `metadata` 不换行。

## 自检

- [ ] `name` 与 `{slug}` 一致？
- [ ] `metadata` 为单行 JSON？
- [ ] 正文 < 100 行？
- [ ] 伦理声明与角色匹配？
- [ ] 运行规则中的维度文件与实际生成的文件一致？
