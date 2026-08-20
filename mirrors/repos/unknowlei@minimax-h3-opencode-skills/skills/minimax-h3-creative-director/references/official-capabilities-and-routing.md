# MiniMax H3 Official Capabilities and Routing

Source: MiniMax H3 official usage manual, revision 1241: https://vrfi1sk8a0.feishu.cn/wiki/FIWjwgL33ipnkekzk30crmKUnIh

Use this reference for capability, input-limit, and routing decisions. Use the installed official `h3-prompt-writing` skill for exact prompt syntax.

## Product Envelope

- Output duration: 4-15 seconds.
- Frame rate: 24 FPS.
- Output: native stereo audio.
- Prompt length: at most 7000 characters.
- Current official output is 768p; the official online product documents an upgrade path to 1440p.
- T2VA aspect ratios: 21:9, 16:9, 4:3, 1:1, 3:4, 9:16.
- First/last-frame input: 0, 1, or 2 images; image dimensions 256-5760; aspect ratio from 5:2 through 2:5.
- Full-reference output can use a common selected ratio or adaptive ratio.

Treat these as online product/API limits. Check local ComfyUI node and workflow constraints before promising identical behavior locally.

## Full-Reference Input Limits

- Images: at most 9.
- Videos: at most 3; each 2-15 seconds; combined video duration at most 15 seconds.
- Audio: at most 3; each 2-15 seconds; combined audio duration at most 15 seconds. Audio must accompany image or video and cannot be the only reference type.
- Mixed references: at most 12 files total.
- Per-file limits: video 50 MB, image 30 MB, audio 15 MB; API request body 64 MB.
- Accepted inputs: H264/H265 video with AAC/MP3 audio; JPG/JPEG/PNG/WEBP/HEIC/HEIF images; WAV/MP3 audio.

## Official Prompt Planning Formula

Plan the request as:

`reference material description + core creative concept + visual process description`

For every asset, state upload index/order and one or more explicit responsibilities. Valid responsibilities include identity, character, object, scene, costume, style, composition, action, camera movement, storyboard, first/last/key frame, voice/timbre, full or partial audio reuse, and source-video editing.

The core creative concept should name the subject, location, event/action, genre/style, and special camera/edit strategy. H3 may cut by default, so explicitly request a one-take when continuity is required. Name the desired cut type when cuts matter: cut, fade, beat-synced cut, or fast cut.

Break the process into time or shot blocks. Each shot should control shot size, visible content, camera, action, dialogue, and sound effects. Explicitly name exact visible text and negative requirements.

## Mode Selection

| User intent | Primary mode |
| --- | --- |
| Text, idea, script, or storyboard with no assets | T2VA base |
| User explicitly declares one image as a literal first frame, and it has no reusable reference responsibility | I2VA base |
| User explicitly declares one image as a literal last frame, and it has no reusable reference responsibility | L2VA base |
| User explicitly declares a literal first/last pair, and neither image has reusable reference responsibility | FL2VA base |
| Any image with an unstated/ambiguous role | Ref2VA by default |
| Any image that preserves identity/character/person/object/costume/scene/style/action/camera or another trait | Ref2VA |
| A first/key/last-frame image that also preserves reusable traits | Ref2VA with prompt-level frame anchoring |
| Mixed image/video/audio control | Ref2VA |
| Source-video replacement, addition, removal, background/light/effect/audio modification | Ref2VA editing |
| Continue a source video | Ref2VA continuation |
| Existing prompt diagnosis or repair | Reviewer, then the matching base or reference format |

Do not infer pure keyframe mode from the number of images alone. Require explicit boundary wording and absence of reusable reference responsibilities. If either requirement is uncertain, use Ref2VA. Ref2VA can express first/key/last-frame semantics in the prompt while maintaining reference consistency.

## Mandatory Question Gate

Ask structured questions before drafting when the brief is sparse, omits at least two major creative axes, gives an image with only a generic motion request, or asks the AI to improvise. Ask about 1-3 high-impact choices in one batch, prioritizing visual style, action/story progression, camera/editing, dialogue/voice, sound/music, and ending. A strict yes/no choice may have two options; every other choice question must offer at least five materially different, feasible options. If five meaningful options do not exist, ask an open-ended question. Skip this gate only when the user explicitly prohibits questions.

For multishot routing, invoke `minimax-h3-multishot-planner` when the user explicitly requests multiple shots. For an effective duration of at least 10 seconds with no single-shot/multishot preference, ask a binary multishot question; invoke the planner only if accepted. Explicit one-take or no-cut instructions always skip this planning subskill.

## Dialogue, Audio, and Text

- Match dialogue length to shot duration for reliable lip sync.
- Identify the on-screen speaker. State when a voice is off-screen.
- When dialogue crosses a cut, state that it continues and describe the intended J-cut or L-cut relationship.
- Preserve exact speech, singing, lyrics, and reused source audio. For partial reuse, identify the track or time segment.
- To prohibit audience-only music, set `non_diegetic_music: N/A` and do not request extra score elsewhere.
- Write exact wording for titles, signs, captions, subtitles, slogans, logos, buttons, and interface text.

## Common Failure Checks

- One undivided paragraph instead of time/shot structure
- Uploaded asset without a defined role
- Music requested while `non_diegetic_music` is `N/A`
- One continuous take requested while multiple cuts are specified
- Face/identity consistency requested without an identity reference
- Text-only prompt missing subject appearance, scene, action, camera, sound, or style
- Vague metaphor where an observable event is needed
- Too much dialogue or too many events for the chosen duration
- Two boundary images treated as an automatic montage rather than a controlled transition

## Strengths to Exploit

H3 can combine text, image, video, and audio context; transfer character, action, camera, composition, voice, atmosphere, and editing rhythm; and perform source-video edits such as replacing, adding, or removing subjects/objects, changing background/lighting/effects, and modifying dialogue, voice, or audio while preserving untouched content. Use a preservation ledger for multi-edit requests.
