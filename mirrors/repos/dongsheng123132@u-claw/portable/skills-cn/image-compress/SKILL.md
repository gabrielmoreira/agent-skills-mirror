---
name: image-compress
description: "图片压缩/转换 - 批量压缩、改尺寸、转格式（jpg/png/webp），本地处理不失隐私"
metadata: { "openclaw": { "emoji": "🖼️" } }
---

# 图片压缩 / 转换

帮用户压缩图片体积、调整尺寸、转换格式，全部本地处理，照片不外传。

## 能力概述

- **压缩**：降低体积（控制质量/分辨率），适合发邮件、传微信
- **改尺寸**：按宽高或百分比缩放
- **转格式**：jpg / png / webp 互转（webp 体积最小）
- **批量**：处理整个文件夹

## 操作方式

用 Bash 工具，Python 的 Pillow 库（跨平台、纯本地）：

```bash
python -c "import PIL" 2>/dev/null || pip install -q Pillow

# 单张压缩（质量 75，宽度限制 1600px 等比缩放）
python - <<'PY'
from PIL import Image
im = Image.open("input.jpg")
if im.width > 1600:
    im = im.resize((1600, int(im.height*1600/im.width)))
im.convert("RGB").save("output.jpg", "JPEG", quality=75, optimize=True)
print("已压缩 -> output.jpg")
PY

# 批量：当前目录所有 jpg/png -> webp（体积更小）
python - <<'PY'
from PIL import Image
import glob, os
for f in glob.glob("*.jpg") + glob.glob("*.png"):
    out = os.path.splitext(f)[0] + ".webp"
    Image.open(f).save(out, "WEBP", quality=80)
    print(f"{f} -> {out}")
PY
```

## 使用建议

- 处理前 `ls -lh` 看原图体积，处理后再 `ls -lh` 对比，告诉用户压缩了多少
- 默认不覆盖原图（输出新文件名），除非用户明确要求覆盖
- 含透明通道的 PNG 转 JPG 会丢透明，转 webp 可保留——按需选格式
