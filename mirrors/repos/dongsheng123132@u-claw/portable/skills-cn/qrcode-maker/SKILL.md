---
name: qrcode-maker
description: "二维码生成 - 把网址/文本/WiFi 信息生成二维码图片，本地离线生成"
metadata: { "openclaw": { "emoji": "🔳" } }
---

# 二维码生成

帮用户把网址、文本、联系方式、WiFi 信息生成二维码图片，本地离线生成，不上传任何数据。

## 能力概述

- **网址/文本二维码**：任意内容转二维码 PNG
- **WiFi 二维码**：扫码即连，免手输密码
- **终端预览**：直接在对话里用字符画展示二维码

## 操作方式

用 Bash 工具，Python 的 qrcode 库（轻量、纯本地）：

```bash
python -c "import qrcode" 2>/dev/null || pip install -q "qrcode[pil]"

# 网址/文本 -> PNG
python - <<'PY'
import qrcode
qrcode.make("https://u-claw.org").save("qrcode.png")
print("已生成 -> qrcode.png")
PY

# WiFi 二维码（扫码自动连网）
python - <<'PY'
import qrcode
ssid, pwd, enc = "MyWiFi", "password123", "WPA"   # enc: WPA / WEP / nopass
data = f"WIFI:T:{enc};S:{ssid};P:{pwd};;"
qrcode.make(data).save("wifi-qr.png")
print("已生成 WiFi 二维码 -> wifi-qr.png")
PY

# 终端字符画预览（不存文件，直接看）
python - <<'PY'
import qrcode
q = qrcode.QRCode(); q.add_data("https://u-claw.org"); q.make()
q.print_ascii(invert=True)
PY
```

## 使用建议

- 先确认用户要编码的内容、是否保存为文件
- 生成后用 Read 工具把 PNG 展示给用户看
- 内容过长（如整段文字）二维码会很密集，提示用户改用短链
