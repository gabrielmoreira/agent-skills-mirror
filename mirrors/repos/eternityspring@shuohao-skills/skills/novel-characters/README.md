**中文** · [English](README.en.md)

# novel-characters

丢一本小说或一篇短故事进去，输出每个角色的完整设定：

- **角色表** — 谁出场了，主角还是龙套，跨章节的不同称呼归并到同一个人
- **人物画像** — 性别、年龄、身份、外貌、性情、动机、人物弧光、关系网，每条附**原文逐字引文**
- **卡通形象提示词** — 中英双语出图 prompt + negative prompt + 风格标签，直接喂 Midjourney / SD / GPT-Image
- **音色提示词** — 音色、音高、语速、口音、情绪，中英双语 voice-design prompt，直接喂 Qwen3-TTS / ElevenLabs Voice Design
- **三视图** — 正视/侧视/背视设定表，白底方便抠图，走 codex 内置出图（可选）

产出 `cast.json` + Markdown + 一个双击就能开的 `report.html`。

![report.html](assets/report.png)

三视图（自带样例《渡口》的沈知微）：

![三视图](assets/turnaround.jpg)

## 用

安装见[仓库根 README](../../README.md)。装好后：

```
/novel-characters ./你的小说.txt
```

或者直接说「帮我拆一下这本书的角色」并给出路径。

## 它是怎么工作的

长文本一次性塞进上下文会丢角色，所以拆成两趟：

**第一趟 · 扫描**（便宜）
按段落切成 14k 字符的重叠块，每块并发抽「角色名 + 别名 + 该块里的具体描写 + 逐字引文」。重叠是为了让卡在切口上的角色两边都能看见。

**归并**
按名字和别名建索引，`陆行远` / `陆` / `姑娘` 这类跨块的不同叫法收敛成同一个人。按出现块数当戏份权重排序。

**第二趟 · 出卡**
只对戏份最重的 N 位，把归并后的全部描写喂进去，一次生成完整角色卡。同批角色互相知道对方的名字，避免长相和声线撞车。

**校验**（这步不能跳）
四类硬规则，全部由脚本确定性检查，不靠模型自觉：

| 规则 | 为什么 |
| --- | --- |
| `evidence` 必须是原文**逐字连续**片段 | 防编造。被「他说」断开的对白不许拼接 |
| 出图 prompt **不许出现人名** | 图像模型对人名偏见极重，会画成它记忆里的角色 |
| 字段**语言分工** | `voice.*` 描述必须中文、`image.prompt` 必须英文，模型会漂 |
| 结构 + 枚举 | `importance` 只能是那四个值 |

这四条不是拍脑袋定的——是模型输出真的违反过、被校验脚本当场抓住才立起来的。

## 命令行直接用

脚本本身不需要 agent 也能跑，只有两趟模型调用需要：

```bash
node scripts/novel-characters.mjs chunk book.txt /tmp/wk        # 切块
node scripts/novel-characters.mjs merge /tmp/wk                 # 归并 roster-*.json
node scripts/novel-characters.mjs validate cast.json book.txt   # 校验
node scripts/novel-characters.mjs render cast.json --html       # 出 report.html
node scripts/novel-characters.mjs slug "胡二爷"                  # 安全文件名
```

## 边界

- 单次上限 24 块（约 33 万字符）。超了会明确报 `truncated`，**不静默截断**
- **输出中文优先**：`persona` 和 `voice` 的描述字段强制中文，校验器会拦英文。分析英文原著也是出中文角色卡。想要全英文输出目前需要自己改 `references/` 和校验规则
- 三视图只自动给 `protagonist` 和 `major`，其余只给提示词
- **同一批角色画风会漂**——各自独立出图，实测同样写着 `flat vector cartoon style`，会出成动画感 / 半写实 / 水墨写实三种。可以拿第一张当参考图压一压（见 `references/turnaround.md`），但压不死

> ⚠️ **机器上装了多个 codex 要注意版本。** 旧版本会直接报 `requires a newer version of Codex` 而不是降级。skill 里带了自动挑最高版本的探测逻辑，整体太旧就 `npm i -g @openai/codex`。

## 文件

```
SKILL.md                 给 agent 读的工作流
scripts/
  novel-characters.mjs   chunk / merge / validate / render / slug
  selftest.mjs           73 项断言，不调模型
references/
  roster-pass.md         第一趟：扫描角色
  profile-pass.md        第二趟：生成角色卡（8 条硬规则）
  schema.md              角色卡结构 + 字段语言归属
  turnaround.md          三视图出图的 codex 调用契约
  report-style.md        report.html 的设计约定
examples/
  渡口.txt                自带短故事，4 个角色
  渡口-cast.json          产出，同时是校验自检夹具
  渡口-cast.md            渲染结果，质量基准
```

`examples/渡口.txt` 里货郎全程只有绰号、船夫只被叫过「老伯」——专门用来验别名归并。

## 自测

```bash
node scripts/selftest.mjs
```

73 项断言，覆盖分块 / 别名归并 / 校验 / 渲染。不调模型、不花额度、1 秒跑完。改完脚本先跑这个。

**只在 macOS + Node 24 上实测过。** 代码没有平台相关调用，Linux 和更低版本 Node 理论上没问题，但**没验过**——仓库里的 CI（`ci/selftest.yml`）还没启用。
