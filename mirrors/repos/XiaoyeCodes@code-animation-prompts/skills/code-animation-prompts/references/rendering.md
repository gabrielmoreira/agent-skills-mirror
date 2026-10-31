# 浏览器动画导出

## 时间接口

随附渲染器用于提供以下接口的 HTML（不直接渲染任意网页）：

```js
window.renderAt = async function (t) {
  // t 是秒；把所有动画、粒子、相机、字幕定位到这个时刻。
  draw(t);
};
```

页面接收到 `?export=1` 后不启动 requestAnimationFrame／计时器循环，停止 CSS 自播放动画；由 `renderAt(t)` 唯一推进画面。随机粒子启动时用固定种子生成，或者由索引和时间直接计算。异步资源应在 `renderAt` 返回前准备好。Canvas 的像素尺寸、CSS 视口与输出尺寸一致，不包含播放器控件。

`../assets/starter/index.html` 是一个可复制的最小示例。原素材中的 HTML 不保证提供此接口；适配时保存副本，不修改原库。Remotion 等已有项目使用自己的导出工具。

## 依赖

检索和安装只需要 Python 3.10+ 标准库。只有浏览器渲染需要额外安装：

```bash
python -m pip install playwright
python -m playwright install chromium
ffmpeg -version
```

FFmpeg 需安装并位于 PATH 中；安装方法见 [FFmpeg 官方下载](https://ffmpeg.org/download.html)。

## 导出

```bash
python "<技能目录>/scripts/render_video.py" ./index.html \
  --output ./output/video.mp4 --duration 12 --fps 30 --width 1920 --height 1080
```

有已准备好的配乐／配音可增加 `--audio ./narration.wav`。脚本不会生成声音，也不会自动循环短音频；会补静音或裁切到视频时长。默认无声。输出文件已存在时停止，另选文件名即可。

脚本用本地 HTTP 服务加载 HTML，绑定 `127.0.0.1` 的随机端口；依赖资源应放在 HTML 所在目录及其子目录中。按 `t = frame / fps` 逐帧截图，使用 FFmpeg 编码为 H.264 / yuv420p。尺寸必须为正偶数；帧数为 `ceil(duration × fps)`，实际时长可能向上取整至一帧。默认会截取整个输出视口。

长片或高分辨率逐帧渲染较慢。先导出一小段检查视觉与依赖，再渲染全片。输出失败时报告具体缺失项或接口错误，不声称完成。
