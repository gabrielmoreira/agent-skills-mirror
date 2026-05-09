---
name: mi-car-trial
description: >-
  根据用户描述（车型名、总车价、首付金额或首付比例、期数），调用小米天星金融
  af-portal-api 的免登录聚合试算接口，返回所有可选产品方案及每个方案的试算结果。
  本技能仅适用于小米汽车（小米 SU7 / SU7 Pro / SU7 Max / SU7 Ultra / YU7 等系列），
  不适用于小鹏 / 蔚来 / 理想等其他品牌。
  触发词：试算、贷款方案、聚合试算、我想买、小米SU7、小米YU7、购车方案、月供。
license: MIT
compatibility:
  - claude-code
  - opencode
  - cursor
  - copilot
  - codex
  - gemini
metadata:
  author: 天星数科科技有限公司 (Xiaomi Finance / Airstar Finance)
  version: 1.0.5
  homepage: https://github.com/caojia321/mifi-skills
  repository: https://github.com/caojia321/mifi-skills
  tags:
    - xiaomi
    - finance
    - car-loan
    - su7
    - yu7
    - chinese
    - cli
  external_costs: >-
    无费用；调用小米天星金融公开聚合试算接口 https://afs.airstarfinance.net/api/ ，
    可能受限流或接口变更影响。
---

# Mi Car Trial（小米汽车贷款试算）

调用**小米天星金融** 免登录聚合试算接口，根据用户一句话需求（如「我想买一辆小米 SU7 标准版，总车价 21.59 万，首付 5 万，分 36 期」）返回所有可用产品方案与逐方案试算结果。

> **适用范围**：本技能只覆盖**小米汽车**（Xiaomi）在售的 SU7 / SU7 Pro / SU7 Max / SU7 Ultra / SU7 Ultra 赛道专业改装版 / SU7 Ultra 纽博格林版 / YU7 / YU7 Pro / YU7 Max / 小米定制版等系列。若用户询问小鹏、蔚来、理想、特斯拉、比亚迪等其他品牌车型，**必须明确告知本技能不支持**，不得强行把其他品牌车型名送进 `match` 子命令。

## 目录结构

```text
mi-car-trial/
  SKILL.md
  scripts/
    cli.py          # 统一 CLI 入口（所有外部调用只走它）
    core/           # 纯函数核心业务（HTTP、金额换算、评估、车型匹配…）
      http.py  money.py  terms.py  car_models.py  aggregate.py  evaluate.py
```

CLI 与 core 的分层约定：

- `core/*`：只接受/返回 Python 对象，失败抛 `MiCarTrialError`，**不做 print / sys.exit**。
- `scripts/cli.py`：唯一对外可执行入口，负责参数解析 + UTF-8 JSON IO + 退出码。
- 主会话 / 其它脚本 / 未来用户自己的工具：**只调 `python scripts/cli.py <子命令>`**，不直接 import core、不直接打接口。

## 核心设计原则：一切计算与接口调用下沉到 CLI

**本技能严格禁止在主会话中做以下事情**：

- **任何数学运算**：单位换算（元/万元 ↔ 分）、首付比例 → 金额、月供/贷款金额推算、首付区间判断、期数支持校验——全部通过 CLI 完成。
- **手动组装或解析 HTTP 请求/响应的 JSON**：不要用 `Invoke-RestMethod` / `curl` 直接调接口。
- **凭记忆写出支持期数**：必须每次运行 `cli.py terms`。
- **肉眼扫描 schemes 筛可用方案**：必须走 `cli.py evaluate` 拿结构化结果。

主会话的职责只有两件：**① 向用户问清参数 ② 按以下 "CLI 子命令 → 读 JSON" 的流程串起来**。

### CLI 子命令清单

| 子命令 | 职责 | 输入 | 输出（stdout） |
|---|---|---|---|
| `terms` | `GET /supported-terms` | 无 | `{"terms":[12,24,36,48,60]}` |
| `car-models` | `GET /car-models` | 无 | `{"cars":[{carModelId,modelName,totalAmount(分),serialId,serialName},...]}` |
| `match` | `/car-models` + 包含匹配（忽略空格/大小写） | `--name <车型名>` | `{"status":"ok"/"multiple"/"none",...}` |
| `calc-down` | 金额/比例 → 分 换算 | `--yuan` \| `--wan` \| `--vehicleValue --rate/--percent` | `{"fen":<分>}` |
| `aggregate` | `POST /aggregate` | `--carModelId --vehicleValue --downPaymentAmount --termNo`（全部分/整数） | `ProductTrialAggregateVO` 的 `data` 对象 |
| `evaluate` | 首付范围 + 期数支持 + 过滤 + 分组排序 | stdin UTF-8 JSON | 含 available/downOutOfRange/termUnsupported/both/summary 的结构 |

所有 CLI 调用：

- 成功 → exit 0 + stdout 输出紧凑 UTF-8 JSON
- 失败 → exit != 0 + stderr 打印错误；**严禁使用任何本地兜底值继续**
- 跨平台 Python 3.7+（只依赖标准库 urllib + json），无需 pip 安装

## 触发条件

满足任一即可触发：

- 用户提到「试算」「聚合试算」「贷款方案」「购车方案」「月供」「分期」，**且**语境指向小米汽车
- 用户以「我想买一辆…车」「查一下 xxx 车的贷款方案」等句式描述购车意图，并点名小米系车型
- 用户明确点名**小米**车型（如 小米 SU7 / SU7 Ultra / 小米 YU7 等）并希望估算贷款
- 仅出现「SU7」「YU7」等型号而未写品牌时，**默认视为小米**（这两个型号当前只有小米在售）；但若用户明确写「小鹏 SU7」等**错误品牌组合**，应先纠正并确认其真实意图

## 输入抽取（从用户自然语言解析）

必须抽取以下字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `carModelName` | 是 | 车型名（如 "SU7 标准版"），用于通过 `cli.py match` 匹配 `carModelId` |
| `vehicleValue` | 否 | 总车价（**分**，整数）。用户未提供时从 `match` 的响应取 `totalAmount` |
| `downPaymentAmount` | **最终必填** | 首付金额（**分**，整数）。用户以比例/元/万元表达时，调用 `cli.py calc-down` 换算 |
| `termNo` | 是 | 分期期数。**传整数（如 12、24、36、48、60）**，不要传 `TERM_36` 这种字符串 |

### 规则

1. **聚合试算接口只接受首付金额**（单位：分）。比例/元/万元一律经 `cli.py calc-down` 换算为分后再传。
2. **不要在主会话里手算**。即便是"5 万元 = 5000000 分"这种看起来简单的换算，也必须走 `cli.py calc-down --yuan 50000`，以避免口算错误和单位混淆。
3. **换算透明性**：CLI 换算后，向用户简要说明（例如"按 25% × 25.35 万，CLI 计算首付 63,375 元"），避免用户以为接口直接收了比例。
4. **金额单位是「分」**：CLI 读写一律用分。展示给用户时再除以 100 转元。
5. **期数**传 `int` 数字。后端 `TermNoEnum` 用 `@JsonValue` 序列化为数字 code，传 `"TERM_36"` 会报 `NumberFormatException`。
6. 若用户提供「贷款金额」而非首付，告知暂不支持，询问改用首付金额或首付比例。

### 信息不全时：问答式收集

如果用户首次输入缺少任何必填字段，**不要假设默认值**、**不要一次问一堆问题**，按以下顺序逐项追问（每次只问 1 个）：

1. **缺 `carModelName`** → 问：「请问您想试算哪款**小米汽车**？（如 小米 SU7 / SU7 Pro / SU7 Max / YU7 / SU7 Ultra 等）」
2. **缺首付** → 问：「请问按首付金额（如 5 万）还是按首付比例（如 30%）试算？」
3. **缺 `termNo`** → **先运行** `python scripts/cli.py terms` 拿到 `terms` 数组，然后按返回顺序向用户展示候选：「请问分期多少期？（当前支持：{terms 拼接，如 12 / 24 / 36 / 48 / 60}）」。CLI 失败（非 0 退出）→ **原样报错并终止流程**，不得自行猜期数。
4. **两个首付字段都给了**（同时给了金额和比例） → 问：「您同时给了首付金额和首付比例，只能二选一，保留哪个？」

每次用户回答后，重新检查剩余缺失字段：有缺 → 继续问；齐全 → 进入调用流程。

`vehicleValue` 始终可选，不需要主动问。缺省时走 Step B 的 `cli.py match` 自动拿到 `totalAmount` 后直接用。

## 环境

- **所属公司**：小米天星金融（airstarfinance，小米集团金融板块）
- **Base URL**：`https://afs.airstarfinance.net/api`
- 所有接口均免登录（无需鉴权头）。
- 该接口只返回**小米汽车**的车型与金融方案，不涉及其他品牌。
- CLI 内部统一用 UTF-8 编解码，不需要在主会话里处理 `Console.OutputEncoding`、`chcp 65001` 等终端编码问题。

## 调用流程

> **约定**：下文所有 `python scripts/cli.py ...` 命令都在本技能 base directory 下执行。实际调用时用绝对路径 `python <skill-base>/scripts/cli.py ...`。Windows 可改用 `py scripts/cli.py ...`。

### Step A：准备参数

#### A.1 若用户用「首付比例」表达 → 先换算为金额

需要知道 `vehicleValue`（分）才能换算，因此先做 Step B 拿到 `totalAmount` 再回来做 A.1；或直接在 A.2 之后执行。

```
# 比例（百分数）
python scripts/cli.py calc-down --vehicleValue 21990000 --percent 30
# 或小数
python scripts/cli.py calc-down --vehicleValue 21990000 --rate 0.3
# 输出：{"fen":6597000}
```

#### A.2 若用户用「元 / 万元」表达金额 → 换算为分

```
python scripts/cli.py calc-down --yuan 50000     # 5 万元 → {"fen":5000000}
python scripts/cli.py calc-down --wan 21.99      # 21.99 万元 → {"fen":21990000}
```

### Step B：匹配车型（得到 carModelId 和 vehicleValue）

```
python scripts/cli.py match --name "SU7 标准版"
```

CLI 内部自动 `GET /car-models` 并做**忽略空格/大小写的包含匹配**。可能的返回：

- `{"status":"ok","car":{carModelId,modelName,totalAmount,...}}` → 唯一命中，取其 `carModelId` 和 `totalAmount`（后者作为 `vehicleValue`）。
- `{"status":"multiple","candidates":[...]}` → 多条命中，向用户展示 `candidates[].modelName` 让其挑选；再用 `carModelId` 直接进入 Step C（本次会话已持有完整列表，无需重复查）。
- `{"status":"none","availableModelNames":[...]}` → 零命中，告知用户并列出 `availableModelNames`。

> 注意：车型名为 `"SU7"` / `"SU7 Pro"` / `"SU7 Max"` / `"SU7 Ultra"` 等，没有 `"SU7 标准版"` 这种字样。用户说"标准版"时映射到 `modelName=="SU7"`（最基础版本）。
>
> 用户只说「SU7」会匹配到多个（SU7、SU7 Pro、SU7 Max、SU7 Ultra……都包含"SU7"），属于 `status=multiple`，需要让用户进一步明确。

### Step C：提交聚合试算

```
python scripts/cli.py aggregate \
  --carModelId 600046406 \
  --vehicleValue 21990000 \
  --downPaymentAmount 5000000 \
  --termNo 36
```

stdout 是 `ProductTrialAggregateVO` 的 `data` 对象，结构见下文。

**注意**：

- **只允许 `downPaymentAmount`**。禁止传 `downPaymentRate`（即便后端结构体里可能存在该字段，在当前环境的解析/单位约定与预期不符，会导致首付被误判为极小值，贷款金额异常放大）。
- `termNo` 必须是**整数**（如 `36`）。
- 所有金额字段单位是**分**。

### Step D：评估方案（首付范围 + 期数支持 + 过滤 + 排序）

**禁止主会话肉眼遍历 `schemes[]` 做以下判断**：首付是否在范围内、期数是否支持、`calculate == null` 是否该过滤、月供排序——必须交给 `cli.py evaluate`。

```python
# 推荐：通过 Python 进程管道调用（跨平台、UTF-8 干净）
import json, subprocess

# 1) POST /aggregate
agg_raw = subprocess.check_output([
    "python", "scripts/cli.py", "aggregate",
    "--carModelId", "600046406",
    "--vehicleValue", "21990000",
    "--downPaymentAmount", "5000000",
    "--termNo", "36",
])
aggregate = json.loads(agg_raw.decode("utf-8"))

# 2) 交给 evaluate 子命令处理
payload = json.dumps({
    "aggregate": aggregate,
    "userDownAmount": 5000000,
    "termNo": 36,
    "vehicleValue": 21990000,
}, ensure_ascii=False).encode("utf-8")

result_raw = subprocess.check_output(
    ["python", "scripts/cli.py", "evaluate"],
    input=payload,
)
result = json.loads(result_raw.decode("utf-8"))
# result.keys() = available / downOutOfRange / termUnsupported / both / filtered / summary
```

> **重要**：必须用**字节流管道 + 显式 UTF-8 解码**（如上示例）。Windows Python 的 `sys.stdin` 默认编码不是 UTF-8，直接传字符串管道会把中文破坏成代理字符。
>
> 如果一定要在 PowerShell / bash 命令行里跑，只要保证 `cli.py evaluate` 的 stdin 是 UTF-8 字节流即可（CLI 已强制按 UTF-8 解码 stdin）。示例（bash）：
>
> ```bash
> python scripts/cli.py aggregate --carModelId 600046406 --vehicleValue 21990000 --downPaymentAmount 5000000 --termNo 36 \
>   | python -c "import json,sys; agg=json.load(sys.stdin); print(json.dumps({'aggregate':agg,'userDownAmount':5000000,'termNo':36,'vehicleValue':21990000},ensure_ascii=False))" \
>   | python scripts/cli.py evaluate
> ```

### evaluate 输出结构

```json
{
  "available":      [<enriched scheme>, ...],
  "downOutOfRange": [<enriched scheme>, ...],
  "termUnsupported":[<enriched scheme>, ...],
  "both":           [<enriched scheme>, ...],
  "filtered":       [<enriched scheme>, ...],
  "summary": {
    "availableCount": 2,
    "downOutOfRangeCount": 1,
    "termUnsupportedCount": 0,
    "bothCount": 0,
    "filteredCount": 0,
    "recommended": {"productTypeName":"标准产品","customerName":"限时7年低息B","monthlyPayment":501677}
  }
}
```

enriched scheme = 原始 scheme + 三个本地计算字段：
- `minAmount` / `maxAmount`（分，可能为 null）——CLI 按 `downInfo.amount` / `downInfo.rate × vehicleValue ÷ 10_000_000` 推算（rate 单位是**百万分比**：`4600000` = 46%）
- `downPaymentSupported`（bool，downInfo 为 null 时视为 true）
- `termSupportedResolved`（bool，综合 `termSupported` 字段与 `supportedTerms` 列表）

### ProductTrialAggregateVO 原始结构（仅供参考，不需要主会话解析）

```json
{
  "carModelId": 600046406,
  "vehicleValue": 21990000,
  "termNo": "36",
  "downPaymentAmount": 5000000,
  "hasFinancialScheme": true,
  "schemes": [
    {
      "productTypeName": "标准产品",
      "productSnapshotId": "...",
      "customerName": "限时7年低息A",
      "description": "首付9.99万元起，年化费率1.9%",
      "marketingTag": "优惠",
      "supportedTerms": ["12","24","36","48","60","72","84"],
      "downInfo": {"rate": 4600000, "maxRate": 8500000, "amount": 9990000, "maxAmount": 18691500, "byAmount": true},
      "termSupported": true,
      "calculate": {"monthlyPayment": 498845, "loanAmount": 16990000, "totalInterest": 968436},
      "calculateError": null
    }
  ]
}
```

若 `data.hasFinancialScheme == false` 且 `schemes == []`：告知用户该车型当前无可用金融方案。

## 输出给用户

以 Markdown 表格展示 `cli.py evaluate` 返回的 `available + downOutOfRange + termUnsupported + both`（按该顺序分组），关键列：

| 产品名 | 类型 | 月供 | 贷款金额 | 总利息 | 首付支持范围 | 状态 | 营销标签 |
|---|---|---|---|---|---|---|---|

**展示时把所有金额字段除以 100 转元**，必要时再换算为万元。以下是**字段级的展示规则**，严格按 evaluate 结果字段组装，不要手动二次计算任何数值：

### 「首付支持范围」列

- 取 enriched scheme 的 `minAmount` / `maxAmount`（CLI 已推算好，单位分）
- 两端除以 100 展示元/万元，例如 `3万 - 15万`
- `downPaymentSupported == false` → 在范围前加 ⚠️ 并标粗，例如 `⚠️ **9.99万 - 18.69万（当前首付 5 万低于下限）**`
- `minAmount == null && maxAmount == null` → 显示 `—`

### 「月供 / 贷款金额 / 总利息」列

- `calculate != null` → 分别取 `calculate.monthlyPayment` / `calculate.loanAmount` / `calculate.totalInterest`，除以 100 展示
- `calculate == null`（即 termUnsupported 或 both 分组）→ 这三列统一显示 `—`

### 「状态」列

- `available` → ✅ 可用
- `downOutOfRange` → ⚠️ 首付超限
- `termUnsupported` → ⚠️ 期数不支持（支持：{supportedTerms 拼接}）
- `both` → ⚠️ 期数不支持 + 首付超限

### 表格下方追加提示

- 若 `downOutOfRangeCount > 0`：
  > ⚠️ **以下方案当前首付不在支持范围内**：
  > - {customerName}：支持首付 {minAmount/100} - {maxAmount/100} 元，当前首付 {userDownAmount/100} 元
  >
  > 如需使用上述方案，请调整首付金额至对应区间。

- 若 `termUnsupportedCount > 0`：
  > ⏱️ **以下方案不支持当前期数（{termNo} 期）**：
  > - {customerName}：支持期数 {supportedTerms 拼接}
  >
  > 如需使用上述方案，请调整期数至其支持范围内。

- 总结：「共 {availableCount} 个可用方案（其中 {downOutOfRangeCount} 个因首付超限需调整，{termUnsupportedCount} 个因期数不支持需调整），推荐 {summary.recommended.customerName}（月供 {recommended.monthlyPayment/100} 元）」。
- 如果 `availableCount == 0`，按"首付/期数"异常更多的一类给出调整建议。
- `filtered` 分组（calculate=null 且 termSupported=true 的无明显原因失败项）**不主动报给用户**。

## 错误处理

| 情况 | 处理 |
|---|---|
| `cli.py match` 返回 `status=none` | 告知用户并列出 `availableModelNames` |
| `cli.py match` 返回 `status=multiple` | 展示 `candidates[].modelName` 让用户精确指定 |
| `cli.py terms` / `car-models` / `aggregate` 退出码 != 0 | 原样转述 stderr 错误并终止；**不得使用任何本地兜底数据继续** |
| 用户既没给金额也没给比例 | 询问「请问按首付金额还是首付比例试算？」 |
| 用户两个都给了 | 告知只能二选一；最终以金额形态调用 `cli.py calc-down` |
| `aggregate.hasFinancialScheme == false` | 告知该车型当前无可用金融方案 |
| `cli.py evaluate` 失败 | 转述 stderr 错误；不要肉眼代替它解析 schemes |

## Safety Rules

- **不要伪造 `carModelId`**：必须来自 `cli.py match` 或 `cli.py car-models` 响应。
- **不要在主会话做任何数学运算**：一切金额/比例/月供/首付区间计算交给 CLI。即便你"一眼就能看出" 5 万 × 30% = 1.5 万，也要走 CLI，避免单位搞错。
- **不要在主会话直接调 HTTP 接口**：一切 `GET` / `POST` 通过 `cli.py` 的子命令。
- **不要凭记忆写期数列表**：每次需要候选期数都运行 `cli.py terms`。
- **不要使用兜底数据**：CLI 失败一律原样报错终止流程，禁止把"默认 [12,24,36,48,60]"之类的兜底传给下游。
- **换算透明性**：比例 → 金额的换算结果要明示给用户（如"按 30% × 21.99 万，CLI 计算首付 65,970 元"），避免用户以为接口直接消费了比例。
- **严禁在用户工作目录（CWD）或项目目录落地任何文件**。CLI 内部只读内存和标准输入输出，不写临时文件；主会话也不要写 `payload.json` 之类的文件。
- **展示前金额单位换算**：CLI 返回的所有金额都是**分**，展示给用户前一律除以 100 转元，必要时再除以 10000 转万元；**展示时必须保留两位小数或按常识取整**，不要展示裸分。
- **禁止展示乱码字段**：CLI 已强制 UTF-8 I/O；如果你看到 `customerName` / `description` 仍是乱码，说明终端渲染问题（Windows cp936 等），**不要把乱码当真展示给用户**，也不要"推测翻译"，应切换为"字节流管道 + 显式 UTF-8 解码"方式重跑（见 Step D 示例）。

## 扩展：直接把 core 作为库使用（可选）

`scripts/core/*` 全是纯函数，失败抛 `MiCarTrialError`。如果你想写脚本而不是调 CLI，也可以：

```python
import sys, os
sys.path.insert(0, "<skill-base>/scripts")
from core.car_models import match_car_model
from core.aggregate import post_aggregate
from core.evaluate import evaluate_schemes

car = match_car_model("SU7 Pro")["car"]
agg = post_aggregate(int(car["carModelId"]), int(car["totalAmount"]), 5000000, 36)
result = evaluate_schemes(agg, 5000000, 36, int(car["totalAmount"]))
```

> 但在 skill 运行时（主会话里），**仍然只允许走 CLI**——core 不做 stdout/退出码约定，会让 skill 的"脚本失败就原样报错"合约难以保证。
