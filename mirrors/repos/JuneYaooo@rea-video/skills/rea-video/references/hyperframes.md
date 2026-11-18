# HyperFrames

[HyperFrames](https://github.com/heygen-com/hyperframes) 是开源的 HTML 视频框架：AI 编程助手写 HTML / CSS 动画，渲染成 MP4。代码渲染、MG 动效、插画动画这类镜头本来就是这样做出来的，交给它重做成可改的工程，比 rea-video 自带的 `code-remake` 草稿更接近原片。

## 费用

- 框架开源免费（Apache-2.0），本地渲染。
- 它的 Studio 应用另有付费套餐（接入 HeyGen 的生成模型），只重做代码类镜头用不到。

## 怎么装

需要 Node.js 22 以上。Claude Code 里：

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

其他编程助手（Codex、Cursor 等）运行一次 `npx hyperframes skills update`。装完以后按它的 skill 让助手写视频。

## 给它什么

把这些交给写 HyperFrames 工程的助手，说明「照这个节奏和画面重做，不要用原片像素」：

1. `video/rhythm.md`：每个切点和转场的时间、转场类型和时长、每镜关键帧（时间 + 是哪一种：动作开始 / 到位、转折、元素出入、构图变化……）。每个时间后面的 @数字 是原片帧号，按帧号排（HyperFrames 用同样的帧率），不要按四舍五入的秒数；动画的关键帧就按这里排，中间交给缓动。
2. 每镜关键帧图 `shots/shot_XXX.jpg`，和报告「代码合成」一节：版式、配色（色值）、元素是什么、怎么入场。
3. 声音：`stems/music.wav` 当配乐，或按 `video/sound.md` 的 BPM 和情绪换一首；音效时间点在 `video/sound.md`。
4. 字幕和花字：`packaging/timeline.json`（时间、位置、样式）。

只想重做其中几镜时，说清楚镜头号和时间范围；其余镜头可以原片占位，做好的片段写进 `remake/mine.json`，用 `rea-video remake out/ref` 拼回原时间线（见 `diy.md`）。
