# First use and stage guidance

## Installation handoff and first invocation

A standalone Skill is loaded when invoked; its files do not provide a universal post-install execution hook. When the assistant performs installation, verify it and then read the installed `SKILL.md` and present the introduction in that same conversation. If the user installed through a terminal or another host, present it on the first invocation. Do not add an npm install hook, background task, second Skill or plugin just to display a welcome. Say "installed" only after installation has actually been verified.

Maintain one shared guide, not separate onboarding editions for each README language. Follow an explicit guidance-language request first, otherwise use the user's current conversation language. If that is unclear, use the host/application or local language setting when it is already available; do not scan unrelated settings to infer it. If neither gives a clear language, ask one brief language question. Translate the explanation and examples naturally; keep commands, paths, service/voice identifiers and A/B style codes intact. Guidance language is independent of narration/subtitle language: a Chinese conversation can request an English video, and English-default narration must not force English onboarding. Do not infer guidance language from the README edition or source article alone.

Give a readable quick-start, not just a greeting or two mode names. Show it once in the current conversation, not before every task. Do not write global user settings or an installed-Skill marker to remember it. When resuming, inspect the existing checkpoint and outputs instead of replaying onboarding or production.

### A practical first-use explanation

With no brief yet, use short headings like a README quick-start. Explain the actual deliverable, suitable content/duration, tools to prepare, production sequence and a copyable request. Distinguish what the assistant does from what the user needs to do. Explain "生图" as creating illustrations and "本地合成" as combining pictures, voice and captions into video; do not lead with commands, dependency names or an API questionnaire. Treat durations as recommendations, not enforced limits. Link the relevant [A-style catalog](style-catalog.md) or [B1 style](b1-minimal-handdrawn.md) when the user asks about the choices.

Adapt this Chinese example to the actual environment and installation status:

### 欢迎使用火柴人视频 Skill

给我一个话题、需求、文章链接或故事脚本，就可以开始。**不用先写好完整文案**，我会帮你整理内容，再按你选的模式往下做。一次安装即可使用下面两种模式。

#### A · Director 导演模式：先拿分镜和提示词，自己掌控生成与剪辑

- **适合做什么**：TikTok / Shorts、反转短剧、需要人物互动和具体动作的故事；可以先做 30 秒，也适合 1～3 分钟短片。
- **你会拿到什么**：故事提案、分段旁白、画面分镜，以及可以逐条复制使用的视频生成提示词。
- **需要准备什么**：在支持 Skill 的 AI 助手里和我沟通；生成视频时使用 Google Flow 等工具，最后在剪映等软件里完成剪辑。写提案和提示词不需要先配置 API。
- **怎么进行**：给话题和要求 → 我给提案 → 你确认或修改 → 我给逐段提示词 → 你生成片段并剪辑。

可以直接这样说：

```text
我想做《人类的第一份工作是怎么来的？》，用 A3「史前洞穴风」，
横屏 16:9，30 秒，英文旁白。先给我导演提案，确认后再给逐段提示词。
```

#### B · Autopilot 自动成片：确认样片后，自动做完整视频

- **适合做什么**：YouTube 知识讲解、产品宣传、故事解说和连续故事短剧；可以先试 20 秒，再做 5～10 分钟或更长的内容，不用逐段手动拼装。
- **你会拿到什么**：配好旁白、字幕、微动画和音效的完整 MP4 视频，以及字幕文件。画面以插画、重点文字和微动画配合讲述。
- **需要准备什么**：在 Codex、Claude Code 等能操作文件、执行命令的环境中使用；还需要可用的生图、配音服务，以及把素材合成视频的本地工具。我会先检查已有配置，只带你补缺少的部分。
- **怎么进行**：给内容和需求 → 检查配置 → 确认脚本、画风和声音 → 看约 20 秒有声样片 → 确认后自动制作整片 → 拿到视频文件。

可以直接这样说：

```text
用 Autopilot，把这篇文章做成适合 YouTube 的 5 分钟宣传视频。
横屏 16:9，用 B1「极简手绘风」，英文旁白，配好字幕和音效。
先帮我检查生图、配音和视频合成配置，再给我脚本与 20 秒有声样片。
文章链接：[粘贴链接]
```

#### 现在怎么开始？

直接发来**内容＋想拿到的结果**就行，例如：“我想做一个介绍这个工具的 YouTube 视频，希望自动拿到完整成片。”也可以补充时长、横竖屏、画风、语言和音色；没想好的部分，我会接着引导，不需要一次填完所有选项。A 模式沿用原有英语、稳定男声默认；B 模式按所选画风配置字幕和配音，B1 默认英语和 Google Gemini 的 Bodi 音色，你也可以指定其他语言、平台或音色。不同 B 画风可以有各自的默认配置，但都会配好旁白和字幕。

如果工具还没配好，可以先说：**“我想用自动成片，但不知道怎么配置，先帮我检查。”** 我会说明哪些能用了、哪些还缺，以及具体怎么补；涉及收费的生成会先说明，不会因为安装好了就直接开始付费制作。

### Adapt instead of replaying the README

If the user's deliverable or mode is already clear, acknowledge it in one sentence, explain only the relevant mode's output/preparation/next stage, and continue with its first incomplete stage. Do not send the full two-mode tutorial to a user who already gave a complete brief or asked to skip it. Do not make the user choose A/B again, paste their source again, or answer questions already resolved. If the brief is complete, proceed rather than waiting for "start". Installation alone is not authorization for paid generation or full production.

## Progress at each substantive stage

After a real stage completes, or when something blocks it, give a compact update in the conversation language. Usually use three short lines, adapted to the situation:

- **已完成**：the concrete output or check, with its link/path when useful. Distinguish checked, user-approved and still unverified.
- **还缺什么**：only the actual missing input, configuration, permission or acceptance; say "无" if there is none. Group missing choices in one concise question. Do not invent blockers to fill the format.
- **下一步**：state what the assistant will do next and, only if needed, exactly what the user must supply or confirm. Give a useful reply example when it saves effort.

Make these lines useful to a beginner: identify the missing item's role, who will handle it and the smallest concrete action. "配音未配置，请配置后继续" is not enough. After checking the selected service, explain its actual supported connection/login or environment-variable setup, and show how to report completion without asking for secret values. Do not invent account screens, commands, service availability or check results. If multiple things are missing, show the checklist but lead with one actionable next step; expand details when the user reaches it rather than dumping every setup manual at once.

For example, after a real preview is ready, link it and give an explicit review handoff rather than merely saying "waiting for confirmation":

> 已完成：约 20 秒有声样片已生成，已检查画面、字幕和音效轨；[播放样片]应替换为真实文件链接。
> 还缺什么：请你观看并试听，确认人物和画风、配音、字幕与切镜节奏是否合适。
> 下一步：需要调整，直接说哪处不对；满意后，可以回复“这版样片通过”。我会结合此前授权和已说明的费用确认能否继续整片，不需要你逐段拼装。

The example is not a canned claim: report only checks actually completed, insert the real playable file, and separately disclose any remaining full-production cost/authorization. A sample's user approval does not fill a missing cost approval.

These are stage handoffs, not per-command logs or recurring reminders. When no user action is needed and the next step is authorized, continue doing it in the same turn. Stop only at the mode's existing approval gates or a genuine blocker. Do not ask permission again for every scene, file or command. At an approval gate, name what is being approved; a generic "continue" must not silently become approval of an unseen sample or new costs.

## A · Director handoffs

| Stage | What to explain / next action |
|---|---|
| Brief | Reuse source, ratio and style/theme already supplied. Ask for missing required items together. Duration defaults to 60 seconds under the existing Director contract. Do not require Node, FFmpeg, an API key or service login merely to produce a proposal or prompts. |
| Proposal | Deliver the current storyboard, narration and visual/voice plan. Say that approval of this proposal is still needed; invite a specific change or confirmation, then stop. Topic approval is not proposal approval. |
| Prompt package | After approval, deliver independently usable clip prompts and stitching guidance. Explain that these are prompts, not generated video files. Next, the user generates clips in a supported video tool and edits/assembles them; offer targeted help if a clip needs correction. |

Keep all existing setup, style, voice and revision rules unchanged. A global change returns to the proposal gate; explain what changed instead of restarting already valid setup.

## B · Autopilot handoffs

Read [Autopilot](autopilot.md), its [runtime configuration](autopilot-runtime.md) and the selected B-style reference before production.

### 1. Brief and source

Resolve the topic/source, audience, purpose, duration, ratio, B-style and narration choices. Accept a topic, requirement, article/post/news link or script; the user need not write a story first. Use supplied choices; propose reasonable creative details for confirmation rather than presenting a long blank questionnaire. If a link cannot be read, ask for its text or screenshots and explain what source material is still missing. Never fill the gap with invented facts.

### 2. Configuration check

Run the documented local `doctor` check and inspect the user's chosen image and voice services. Resolve each setting as **explicit user choice → selected B-style default → B common fallback**, as defined in Autopilot. Check that resolved provider/voice first; for new B1 projects without a user override this is Google Gemini/Bodi. Do not ask the user to choose a platform again merely because they accepted defaults. Summarize actual findings in plain language, separating **ready**, **missing** and **not yet verified**:

- Local composition: Node 20+, FFmpeg/FFprobe, renderer dependencies and suitable fonts. If something is missing, name that component, explain its role briefly, and give the next platform-appropriate installation/configuration step. Install project dependencies only with the host's normal permissions; after a repair, verify the affected check again.
- Image and voice generation: reuse an available configured tool or authenticated interface if suitable. Do not demand a Gemini API key when the chosen browser/native tool does not use one. If image generation is not configured, guide selection of an available image service. For narration, check the resolved provider/voice and explain only the missing login, access or configuration; do not require Bodi when the user or selected style specifies another voice. For API adapters use environment variables, never pasted secret values. Do not silently replace the selected voice/service with local OS TTS.
- Evidence and cost: `doctor` checks local dependencies and key presence, not login, model access, quota or billing. Report those as unverified unless separately checked; an account subscription or an environment variable alone does not make generation ready. Disclose the planned billable calls/cost and obtain authorization before making them. Do not make a paid test call simply to populate the checklist.

State the smallest next fix, not just "configuration failed" or a raw terminal dump. For example:

> 已完成：本地合成工具检查通过，已确认横屏 16:9 和 B1 极简手绘风。
> 还缺什么：生图服务尚未选择；默认 Google Gemini/Bodi 的模型访问和额度还未验证。
> 下一步：先确认使用哪种生图工具；配音按默认 Bodi 路径继续检查，只有缺少访问权限或配置时再带你补齐。暂不调用付费生成，脚本可以先继续准备。

If the host cannot read/write files or execute commands, explain that Autopilot cannot render here and offer a compatible environment or Director mode. Do not silently switch modes or call a prompt package a finished film.

### 3. Script, character and voice plan

Show the short outline/script, design, caption treatment and voice choices required by Autopilot. State what needs confirmation before generating media, and identify any service/cost blockers still open. Follow the settings order above; B1's caption and voice defaults do not constrain another B style. Verify the selected provider/model/voice as described in Autopilot; check Bodi availability only when Bodi is selected. Narration and synchronized subtitles are required. Carry the approved voice and assets forward unchanged.

For B, explain the selected service/model and named voice, not a custom descriptive voice profile. Use that voice as provided with no added style/direction instructions; follow Autopilot's voice-led rule for every B style.

### 4. Approximately 20-second sample

Make and inspect the representative sample with narration, subtitles, acting/micro-animation and SFX. Only the sample range needs finished shots/media at this stage. Link the playable result. Say what was technically checked and ask the user to review the actual picture and sound. Request approval of this exact sample and authorization for the remaining production, with any remaining cost explained. Do not run `approve` based on technical success alone. If revisions are requested, keep valid audio/assets and revise only the affected scope; update the preview/approval when its scoped fingerprint changes, not merely because later shots were completed. Changes to the approved script, global settings or cost still need the corresponding authorization.

### 5. Full production and delivery

After genuine sample/full-production approval, render the rest with pictures following the approved original-speed narration. Give updates at meaningful production stages; do not wait for a new confirmation after each shot. On interruption or failure, explain completed outputs and the exact blocked step, inspect existing jobs/cache and resume valid work rather than resubmitting blindly.

Deliver MP4, subtitle sidecars and project/checkpoint paths with a short verification summary. If any check, listening review or output is still missing, say so; do not call a partial file a complete film. End with the useful next action (for example, review the film or request a specific revision), not automatic publication, a new video or another paid call.
