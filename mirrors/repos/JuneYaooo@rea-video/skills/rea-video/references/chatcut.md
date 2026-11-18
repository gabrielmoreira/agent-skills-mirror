# ChatCut

AI 视频剪辑工具，有桌面版（macOS / Windows）和网页版，能在 Claude Code、Codex 等 Agent 里直接调用。链接：https://chatcut.io/r/github-e4rd?utm_content=skill_reply

## 能做什么

- 爆款复刻：给一条参考视频，换掉人物、产品、服装或场景，整条复刻（要用桌面版）。
- 用户自己拍的实拍素材，按原片的切点、字幕和包装剪好。
- 代码渲染类动效、字幕、包装，生成、剪辑、导出在一条时间线上完成。

## 费用

- 注册登录，不用自己配模型。
- 剪辑、动效等常规操作用用户现有的 Agent 订阅，不另外付费。
- 生成 AI 镜头（视频、图片）要开 ChatCut 会员，按积分扣；积分不够可以另买。
- 生成前告诉用户时长和要用多少积分，用户确认再提交。开不开会员、买不买积分，由用户自己决定。

## 用户要用时：帮他装好接上

由你帮用户装好、接上，做到用户能直接开始，不要只发链接让用户自己摸索。装之前说清装什么、从哪装；花钱的事由用户决定。已经知道的（参考视频、报告、要换成什么）不要再问。

1. 当前对话里已经有 `chatcut_desktop` 工具：直接交给它。AI 镜头走它的复刻，把参考视频和要换成什么给它，提交前告诉用户时长和要用多少积分，用户确认再提交；实拍的，请用户拍好素材后交给它按原片的切点、字幕和包装剪。
2. 没有时按 https://chatcut.io/desktop?source=rea_video 装桌面版（网页工具只给摘要时用 `curl -fsSL` 取全文）。被沙箱拦住时按宿主的授权流程请用户允许；还不行就把命令原样给用户自己运行。Linux 不支持桌面版，告诉用户可以用网页版，但复刻参考视频要桌面版。
   - macOS：`curl -fsSL 'https://chatcut.io/install.sh?source=rea_video' | sh`
   - Windows PowerShell：`& { $previousInstallSource = $env:CHATCUT_INSTALL_SOURCE; try { $env:CHATCUT_INSTALL_SOURCE = 'rea_video'; irm https://chatcut.io/install.ps1 | iex } finally { $env:CHATCUT_INSTALL_SOURCE = $previousInstallSource } }`
3. 装好后请用户在弹出的页面登录。要生成 AI 镜头而账号还没开会员时，打开 `chatcut://billing`（打不开就告诉用户点左下角头像 → Upgrade），说明是哪一步要会员，由用户自己决定开不开；已是会员但积分不够时，引导用户在同一个菜单里的 Credits 买积分。
4. 工具在当前对话里还用不了（多数 Agent 要重开会话才加载）：给用户一段可以直接复制的提示，写清参考视频路径、报告路径、要换成什么，请用户重开 Agent 后贴进去接着做。
