# {{title}}

漫剧制作,按真实剧组的方式运转。这个文件夹就是唯一的真相源:agent 在这里写文字,TongFlow 工作流把媒体生成为一条条编号的 take,你圈选喜欢的那条。

```
project.json          项目清单
story/                故事:梗概、大纲、剧本(纯文本,由 agent 撰写)
world/<ID>/           角色与设定:CHR_ 角色 · LOC_ 场景 · PRP_ 道具 · STY_ 风格
                       card.md · consistency.json · REF/(参考图)· VO/(声线参考)
episodes/EP01/        scenes.json —— 分镜表(场 → 镜、台词、提示词)
                       + MUS/ SFX/ MIX/ CUT/(单集音乐、音效、混音、成片剪辑)
shots/<SHOT>/         SB/ 分镜图 · KF/ 关键帧 · ANI/ 动画 · DLG/ 台词配音
inbox/                你丢给剧组的素材
workflows/            每个生成物一份 *.tongflow.json(可在画布上打开);templates/ 是起手模板
notes/                审片笔记与 agent 的自检报告
export/               成片输出
```

编号:`EP01` · `EP01_SC003` · `EP01_SC003_SH0010` · `CHR_MEI` · take `T01…`。
引用:`tf://CHR_MEI/REF`、`tf://EP01_SC003_SH0010/KF`、`tf://EP01/ANI`、`tf://EP01_SC003_SH0010/dialogue`。

{{logline}}
