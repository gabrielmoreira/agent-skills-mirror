# Plan the asset

Read when defining or changing an asset job. Keep the active workflow and approved creative scope.

Within a film, the calling entry decides how generated media serves the motion design: which planned elements it upgrades, and the shot, motion and timing each asset carries. Plan each asset from that role. A standalone asset request follows the user's prompt directly. A "just make it, don't ask" request skips optional creative questions, not this design work and not a missing authorization for paid generation.

## Define the asset and modality

Derive subject, recognizable identity features, action, framing, lighting, style, duration budget and negative space for editable native typography from the active brief, reference segment or user prompt. Reuse approved project assets before generating new ones.

Choose the modality from what must physically change on screen or in the mix:

- **Still image (`modality: "image"`)**: photographic settings, hero product frames, cutouts or backdrop plates where native HTML/CSS/GSAP camera and layer motion carry the choreography.
- **Video (`modality: "video"`)**: continuous subject or environmental footage that native graphics cannot represent directly. Keep text, UI, charts, logos and captions as native editable HTML/SVG overlays above the video plate rather than baking copy into generated video pixels.
- **Speech (`modality: "audio"`)**: spoken narration or dialogue. Use the discovered speech model mode (`"text-to-speech"`) and its native options. The adapter maps the prompt to the model’s actual input field; an input named `text` does not by itself mean speech (some sound-effect models also use it). When captions, visual beats or scene cuts synchronize to individual lines, generate one audio file per sentence or beat within the target duration budget rather than estimating cue timestamps from one monolithic file. Choose a voice for the film language and tone; for Mandarin, confirm the chosen voice supports Chinese. Unless the user specifies otherwise, narration language follows the on-screen copy and target market.
- **Music / sound (`modality: "audio"`)**: background beds, stings or ambient audio where supported by the enabled provider. Use a music or sound-effect model with `mode: "text-to-audio"`. BGM is a use of music, not a separate generation mode. Do not switch to a speech model or require a voice for music/SFX; use the selected model’s native duration, looping and instrumental parameters.
