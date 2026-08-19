# 工作流模板

只是起手式。每个资产复制一份:
`tongflow_workflow_new({ path: '<归属>_<环节>', fromTemplate: '<模板名>' })`,再把具体提示词 / `tf://` 引用写进节点。
复制时每个节点自动选用已安装的默认插件。多步模板:某个资产用不到的步骤直接删掉。

- `character-sheet` —— 文本 → 角色参考图(REF)。
- `location-plate` —— 文本 → 场景定场图(REF)。
- `storyboard-panel` —— 提示词 → 分镜图(SB)。输入:prompt。
- `shot-keyframe` —— 参考图 + 提示词 → 关键帧(KF,图像融合)。输入:refs、prompt。
- `shot-keyframe-hd` —— 图像融合 → 放大(KF)。输入:refs、prompt。
- `dub-line` —— 声线参考 + 台词 → 配音(DLG)。输入:voice、text。
- `voice-preset` —— 台词 → 预设音色语音(VO / DLG)。输入:text。
- `shot-i2v` —— 关键帧 + 运动提示词 → 动画(ANI)。输入:image、prompt。
- `shot-i2v-lipsync` —— 图生视频 → 与台词音频对口型(ANI)。输入:image、prompt、audio。
- `episode-music` —— 情绪提示词 → 音乐(MUS)。输入:prompt。
- `assemble-episode` —— 按顺序拼接已圈选的 ANI,再叠上音乐(CUT)。输入:clips ← tf://EP01/ANI,music ← tf://EP01/MUS。

一个镜头的各部分都齐了以后,`tongflow_workflow_compose({ owner })`(或片场里镜头页的按钮)会把它们合成
`<镜头>_ALL.tongflow.json`,供人审阅、微调、一键重跑;整集同理。
