# staging.json 格式

一份 staging.json 记一部剧（或其中几集）每一场**开场那一刻**谁在哪。中途换位置不记——那是分镜的事，分镜从这一刻往后接着写。

```json
{
  "source": "渡口",
  "lang": "zh",
  "locations": [ … ],
  "scenes": [ … ]
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `source` | string | 剧名，`seed` 从 script.json 搬过来 |
| `lang` | `zh` / `en` | 工作语言：东西的名字、人名、走位句用哪种语言写。报告界面默认也跟它 |
| `locations` | location[] | 每个地点（美术场景）一条：从它的场景图里认出来的东西 |
| `scenes` | scene[] | 每一场（剧本的场次）一条：开场站位 |

## 坐标系

所有方位都按**场景**说，不按画面说：

- **主视角**（场景图的标准取景）的机位在**南侧**，向北看。所以图的左边是西、右边是东，越往上（越远）越靠北，越往下（越近）越靠南。
- **平面**（`plan`）是把整个房间摆平以后从正上方看：北在上、西在左，0 到 1，从西北角量起——横向从西墙（0）到东墙（1），纵向从北墙（0）到南边机位那一侧（1）。
- 人的位置写成「在哪件东西的哪一侧、沿着这一侧多远」，不写平面坐标。平面上的点由程序按这句话算出来，所以画出来的和写出来的永远是一回事。

## location

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `sceneId` | string | `S01` 格式，对账 art.json 的场景 |
| `name` | string | 地点名，`seed` 从 art.json 搬过来；报告按它找图（`images/<名字>-sheet.png`） |
| `readFrom` | `picture` / `prompt` / null | `picture`：看着场景图认的；`prompt`：还没有图，按 art.json 的锚点和主视角提示词推算的。null = 还没认 |
| `items` | item[] | 4–20 件，按从北到南排 |

### item

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 用工作语言写，十个字以内，写成走位里说得出口的叫法；同类的东西带上方位或特征区分（「北端主位太师椅」「东侧落地窗」）。不重复 |
| `alt` | string | 同一件东西的另一种语言，英文走位句用它 |
| `box` | [左, 上, 右, 下] | 它在图上的位置，0–1，以整张图的宽高为 1。`readFrom` 是 `picture` 时必填；`prompt` 时没有图，不写 |
| `plan` | [西, 北, 东, 南] | 它在平面上占的地方，0–1。按透视推算，不是照抄 box |
| `on` | boolean | 人能坐在、站在它上面（椅子、长凳、床、台子、台阶、船板） |
| `round` | boolean，可选 | 从正上方看是圆的（圆桌、圆地毯）：画成圆，人围着它一圈；不写就看名字里有没有「圆」 |

## scene

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ep` | number | 集号 |
| `scene` | number | 这一集的第几场，从 1 开始，对账 script.json 的 `episodes[].scenes[]` 顺序 |
| `sceneId` | string | 在哪个地点，对账 `locations[].sceneId` |
| `lighting` | string，可选 | 剧本写的时段光照，`seed` 搬过来，只给人看 |
| `cast` | {id, name}[] | 这一场的出场人物，`seed` 从剧本搬过来，不改 |
| `places` | place[] | 出场人物每人正好一条，顺序就是走位句的顺序 |
| `extras` | number | 除了出场人物还有几个群演。剧本没写有别人就是 0 |
| `extrasWhere` | string / null | 群演在哪（「长桌西侧南端」）；`extras` 是 0 时写 null |
| `why` | string，可选 | 一句话：为什么这么排。报告里显示，给人改的时候参考 |

### place

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` / `name` | string | 照抄 `cast` |
| `present` | boolean | 开场时这个人在不在。后面才进来的写 false |
| `item` | string / null | 照抄这个地点 `items` 里的一个名字；不在场写 null |
| `side` | `north` / `east` / `south` / `west` / `on` / null | 在这件东西的哪一侧；在它上面写 `on`（只有 `on: true` 的东西可以） |
| `along` | number / null | 沿这一侧的位置，0–1：东侧、西侧从北端（0）到南端（1）；北侧、南侧从西端（0）到东端（1）。`side` 是 `on` 时写 0.5 |
| `posture` | `sit` / `stand` | 坐还是站；不在场可以写 null |
| `facing` | 八个方位之一 | `north` / `northeast` / `east` / `southeast` / `south` / `southwest` / `west` / `northwest`；不在场可以写 null |

## 开场走位句

`blocking` 命令和报告按上面的数据写出每一场的开场走位：在场的每个人一句，按 `places` 的顺序，最后一句交代还有没有别人。

> 沈知微站在岸端土坡上，面朝北；老周坐在靠岸的渡船上，面朝南；其余座位空着，没有其他人。

同一件东西同一侧落在同一段的几个人，后面的人会带上「、XX 南侧」说清先后。分镜写这一场第一段的开场走位时，照抄这一句。
