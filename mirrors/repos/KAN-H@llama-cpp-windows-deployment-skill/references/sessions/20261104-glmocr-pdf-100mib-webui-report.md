# 2026-11-04 专题报告：WebUI 上传整本 PDF 到 GLM-OCR — 100 MiB 请求体上限 + 上下文双墙

> **一句话**：llama.cpp 自带 WebUI **支持** PDF 上传，但它的实现是「**把每一页渲染成 PNG，全部塞进同一条 chat 请求**」。
> 一本几百页的扫描书会同时撞穿 **llama-server 的 100 MiB 请求体硬上限** 和 **OCR 模型的 16K 上下文**，
> 而前端把传输层失败显示成 **「Unable to connect to server - please check if the server is running」**，
> 极易被误判为「服务没起 / 模型坏了」。实测模型本身完全正常（单页 0.9–1.8 s，文字准确）。

---

## 1. 现象与误判路径

| 观察 | 容易得出的错误结论 | 实际 |
|---|---|---|
| WebUI 弹「Unable to connect to server - please check if the server is running」 | 服务挂了 / 端口错了 | 服务**一直活着**，`/health` 200；是请求体被拒后连接被掐断 |
| 换小一点的 PDF 有时又能过 | 模型不稳定 | 只取决于**页数 × 每页字节数**是否越过 100 MiB |
| 换模型（Gemma / Qwen）好像「有时能识别」 | GLM-OCR 不行 | 视觉模型都能用；差别只在各自 ctx 与每图 token 数 |

**关键事实**：这句话**只在 `fetch` 抛 `TypeError`（传输层失败）时出现**，收到 HTTP 4xx/5xx 会显示别的文案。
反查前端 bundle 可见：

```js
ae.name === "TypeError" && ae.message.includes("fetch")
  ? new Error("Unable to connect to server - please check if the server is running")
```

---

## 2. WebUI 的 PDF 实现（b11960 实测反查）

```js
async function toImages(file, scale = 1.5) {          // pdf.js
  const doc = await getDocument({ data }).promise;
  const imgs = [];
  for (let p = 1; p <= doc.numPages; p++) {           // ← 遍历每一页，无上限、无页范围
    const vp = (await doc.getPage(p)).getViewport({ scale });
    canvas.width = vp.width; canvas.height = vp.height;
    imgs.push(render.promise.then(() => canvas.toDataURL("image/png")));
  }
  return await Promise.all(imgs);                     // ← 全部页面一起返回
}
// 调用处：attach = { base64Data, content: `PDF file with ${imgs.length} pages`, images: imgs }
```

- **没有页范围选择、没有分批**，页数完全由文件决定。
- 若关闭 PDF-as-image 或模型不支持视觉 → 退回「PDF 抽文本」路径；**扫描件（无文本层）走这条等于什么都没抽到**。
- UI 里还有一个「PDF 预览 / PAGES 标签」，会**再渲染一遍**，浏览器内存翻倍。

---

## 3. 两堵墙的实测数字

### 3.1 请求体硬上限 = **100 MiB**（不可调）

| 请求体 | 结果 |
|---:|---|
| 99 MiB | HTTP 200 |
| **100 MiB** | **HTTP 413，空 body，0.1 s** |
| 128 / 256 / 512 / 1024 MiB | HTTP 413 |

- **router 与子实例都一样**（分别对 `:8082` 与子实例端口测过）。
- `llama-server --help` 里**没有**任何 payload / max-request 相关开关 ⇒ 这是编译期常量，改不了。
- 413 在 0.1 s 内返回，说明服务端按 `Content-Length` **在读完 body 之前**就拒绝并关闭 socket；
  浏览器此时仍在传数据 ⇒ Chrome 报 `ERR_CONNECTION_RESET` 一类错误 ⇒ `fetch` TypeError。

### 3.2 上下文：每页 ≈ 1.3K tokens

GLM-OCR（`glm4` 架构、0.9B、mmproj `clip.vision.image_size=336 / patch=14 / projector=glm4v`），
对 832×1200 扫描页（`scale 1.5` → 892×1263）实测：

| 一次请求页数 | 结果 |
|---:|---|
| 1 页 | 200，`prompt_tokens = 1301` |
| **12 页** | **200，`prompt_tokens = 15518`** |
| 14 页 | 400 `request (18102 tokens) exceeds the available context size (16384 tokens)` |
| 20 页 | 400（25854 tokens） |

⇒ **ctx 16384 只能放 12 页**（还要留输出预算；真做完整 OCR 时建议按
`ctx ÷ (每页 prompt + 每页输出)` 估，例如 16384 ÷ (1300+500) ≈ 9 页）。

> ⚠️ 注意：模型 `glm4.context_length = 131072`，即 **ctx 是配置压的，不是模型限制**。
> 用 16384 只是启动器当初为省显存设的值。

---

## 4. 一本 561 页扫描书的实际开销

| 项 | 值 |
|---|---|
| 页数 / 有文本层的页 | 561 / **1**（全扫描，PDF 抽文本无用） |
| 内嵌图 | 832×1200，CCITT G4 1-bit（≈100 DPI） |
| WebUI canvas 尺寸 | 892×1263（scale 1.5） |
| 单页 canvas PNG | **≈ 300 KB** |
| 561 页 base64 | **≈ 215 MiB**（+ PDF 本体 base64 10.4 MiB） |
| 561 页 tokens（理论） | 561 × 1.3K ≈ **730K** = 16K 配置的 **45 倍** |

⇒ 即使把 payload 上限放开，也还是会被 400 挡下；即使 ctx 拉到原生 131072，也还差 5.6 倍。
**「整本 PDF 一次过」在 WebUI 里无解。**

---

## 5. 解决方案（按推荐度）

### 5.1 逐页脚本（唯一可处理整本的方式）

`scripts/ocr_pdf.py`（本技能已附带，脱敏通用版）：

```
python scripts/ocr_pdf.py <book.pdf>            # 逐页，断点续跑
python scripts/ocr_pdf.py <book.pdf> --from 1 --to 20
```

- pymupdf 渲染（`--scale` 默认 1.5，与 WebUI 对齐）→ 每页一次 `/v1/chat/completions`
- 输出 `<页>.txt` + 合并 `<书名>_ocr.md`；已有文件自动跳过（断点续跑）
- 自动识别模型（`/v1/models` 里含 `ocr` 的）、自动读 `n_ctx`
  （**注意：Router 模式下 `/props` 的 `n_ctx` 恒为 0**，要读 `/v1/models` 的 `meta.n_ctx`
  或 `status.args` 里的 `--ctx-size`）
- 遇到 `exceed_context_size_error` 自动**折半批大小**重试；请求体按 90 MiB 保守切分
- 实测：**≈1.4 s/页**（0.9B 模型，217 tok/s 解码），561 页约 12–15 分钟

> ⚠️ **`--batch > 1` 不可靠**：模型不会输出页分隔符，实测 20 页一批只回了 316 token（大量漏页）。
> 要逐页结果就用默认 `--batch 1`。

### 5.2 抬高 ctx（可选提速，不解决整本）

`preset-overrides.json` 里把该模型 `ctx-size` 提到 65536（16K→64K，显存 **+1.1 GB** 实测）：

| ctx | 每请求可放 | KV(q4_0) 代价 |
|---:|---:|---:|
| 16384 | 12 页 | 0.36 GB |
| 65536 | ~45 页 | 1.4 GB |
| 131072（原生） | ~90 页 | 2.8 GB |

改完必须**重新生成配置并重启 router** 才生效（ini 只在启动时读）。
ID 里带 `16K/64K` 的模型名记得同步改，否则名字和配置会对不上。

### 5.3 包成 MCP 工具（给 agent 用）

`launcher/mcp_ocr_server.py`（本机实现，可参照）把脚本包成 4 个工具：
`ocr_pdf_submit / ocr_pdf_status / ocr_pdf_read / ocr_pdf_health`。
**agent 调工具，而不是把 PDF 塞进模型上下文** —— 这是 DSH / Copilot 这类 agent 的正确用法。

两个实现坑：

1. **stdio 必须显式 UTF-8**：Windows 默认 `cp936`，中文正文会让 JSON-RPC 出现非法字节。
   `sys.stdout.reconfigure(encoding="utf-8", newline="\n")`。
2. **进度采集必须开线程**：`for line in proc.stdout` 会**阻塞到 EOF**，
   直接放在 status 处理函数里会一直卡到任务结束。用 daemon thread 持续 drain。

---

## 6. 复现命令（把占位符换成自己的）

```powershell
# 1) 单页应成功
curl -s -H "Authorization: Bearer <key>" -H "Content-Type: application/json" ^
  -d "{\"model\":\"<ocr-model-id>\",\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"Text Recognition:\"},{\"type\":\"image_url\",\"image_url\":{\"url\":\"data:image/png;base64,<b64>\"}}]}],\"max_tokens\":64}" ^
  http://127.0.0.1:8080/v1/chat/completions

# 2) 请求体上限（prompt 极小 + 巨型被忽略字段，秒级返回）
python -c "import json,urllib.request,sys; b=json.dumps({'prompt':'hi','n_predict':1,'_junk':'A'*(100*1024*1024)}).encode(); r=urllib.request.Request('http://127.0.0.1:8080/v1/completions',data=b,headers={'Content-Type':'application/json','Authorization':'Bearer <key>'}); print(urllib.request.urlopen(r,timeout=60).status)"
# 99 MiB -> 200 ; 100 MiB -> HTTPError 413 (空 body)
```

---

## 7. 教训

1. **「Unable to connect」不一定是连不上** —— 先分清「传输层失败」与「HTTP 错误」，看服务端是否仍在 `/health`。
2. **浏览器有一个请求体上限之外的上限：服务端会提前拒绝**。超大 body 的失败形态是网络错误，不是 413 弹窗。
3. **多模态输入要按「每页 token」算预算，而不是按「图片张数」**。同一模型、不同分辨率，差 2–3 倍。
4. **WebUI 的 PDF 支持是「一次性全页」，不是「分页阅读」** —— 它只适合几页的短文档。
5. **配置改了不等于生效**：Router 的 preset 只在启动时读取，改 ini 后必须重启。
6. **模型能做 OCR ≠ 模型能当对话模型**：GLM-OCR 是 image-to-text 专用，没有工具调用能力，
   不要把它注册成 agent 的主模型；要注册成**工具**。
