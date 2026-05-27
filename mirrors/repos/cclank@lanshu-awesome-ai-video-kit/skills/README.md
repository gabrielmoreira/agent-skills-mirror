# Claude Code Skills

**7 个**把方法论自动化的 Skill,覆盖 **15 大主流视频模型**(11 商业 + 4 开源)。

## 安装

把整个 `skills/` 目录的子目录复制到 Claude Code 的 skills 路径:

```bash
cp -r seedance-prompter ~/.claude/skills/
cp -r seedance-storyboard ~/.claude/skills/
cp -r seedance-debugger ~/.claude/skills/
cp -r happyhorse-prompter ~/.claude/skills/
cp -r kling-prompter ~/.claude/skills/
cp -r model-selector ~/.claude/skills/      # ★ 15 模型购物顾问
cp -r prompt-translator ~/.claude/skills/   # ★ 跨模型转换器(基于 110 条对照基准)
```

或用符号链接同步:

```bash
for s in seedance-prompter seedance-storyboard seedance-debugger \
         happyhorse-prompter kling-prompter model-selector prompt-translator; do
  ln -s "$(pwd)/$s" ~/.claude/skills/$s
done
```

## 7 个 Skill 概览

| Skill | 覆盖模型 | 何时触发 | 输出 |
|---|---|---|---|
| ★ [model-selector](model-selector/SKILL.md) | **全 15 模型** | "用哪个模型好"、"Sora 还是 Kling"、"哪个支持中文"、"哪个能本地部署" | 推荐 1-3 个模型 + 理由 + 对应 skill 链接 |
| ★ [prompt-translator](prompt-translator/SKILL.md) | **跨 11 商业模型** | "Sora 已 EOL 转 Veo"、"Kling 转 Wan"、"跨模型 A/B 测试" | 基于 110 条对照基准做查表式转换 + 字段映射表 |
| [seedance-prompter](seedance-prompter/SKILL.md) | Seedance | "帮我写 Seedance 提示词"、"做个视频" | 8 要素结构化提示词 |
| [seedance-storyboard](seedance-storyboard/SKILL.md) | Seedance | "把这个剧情拆成分镜"、"多镜头视频" | 3-5 个分镜 + 4 维度组织 |
| [seedance-debugger](seedance-debugger/SKILL.md) | Seedance | "我的提示词出问题了"、"人脸不像了" | 12 类诊断 + 修复 |
| [happyhorse-prompter](happyhorse-prompter/SKILL.md) | HappyHorse | "5/10/15 秒短片"、"原生带音频" | 30-55 词紧凑 + 音频路径 |
| [kling-prompter](kling-prompter/SKILL.md) | Kling | "可灵"、"Kling"、"图生视频"、"角色对话"、"中文剧情" | 三套写法自适应(4 部分/5 层/图生视频) |

## 选 Skill 的决策树

```
你想要什么?
├── 不知道用哪个模型(含 4 开源)         → model-selector ★
├── 已有 prompt 想换模型(Sora→Kling 等) → prompt-translator ★
├── 中文剧情、原生音频+对话、图生视频    → kling-prompter
├── 5/10/15 秒紧凑 + 要原生环境音            → happyhorse-prompter
├── 10-15 秒单镜头复杂叙事               → seedance-prompter
├── 多镜头剧情切换                       → seedance-storyboard
└── 已有 Seedance 提示词但效果不对        → seedance-debugger
```

> 💡 还没单独写 skill 的模型(Sora / Veo / Runway / Pika / Hailuo / Hunyuan / Wan / 即梦 / LTX / Mochi / CogVideoX / Higgsfield),可以让 Claude 直接基于 [methodology/](../methodology/) 里的公式手写(尤其是 [methodology/13](../methodology/13-六大模型公式速查.md) 商业模型速查 + [methodology/14](../methodology/14-四大开源模型速查.md) 开源模型速查)。或者用 model-selector 帮你选最匹配的现有 skill。

## Skill 之间的协作

它们不冲突，可以串起来用：

1. 先用 `seedance-storyboard` 拆剧情
2. 每个镜头用 `seedance-prompter` 细化
3. 实测后用 `seedance-debugger` 修问题

或者：

1. 先用 `happyhorse-prompter` 做一版 8 秒短片
2. 觉得不够 → 升级用 `seedance-prompter` 做 15 秒版

## 调用方式（在 Claude Code 里）

直接说自然语言就行，Claude 会根据 description 自动匹配：

> 帮我做个产品广告视频，主角是耳机

→ Claude 会调用 `seedance-prompter`，按 8 要素问你 2-3 个澄清问题，然后输出提示词。

> 我用 Seedance 生成的视频里人脸总是不像参考图，提示词是 XXX

→ Claude 会调用 `seedance-debugger`，对照"人物 ID 漂移"诊断手册给修复方案。

## 参考资源

所有 Skill 都引用了 [../methodology/](../methodology/) 里的方法论文档，需要时会让 Claude 读对应文件加载知识。
