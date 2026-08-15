# localimage — examples

User slash: **only** `/localimage` (backend: `localimage-stills`).  
Always run `local-media-router/discover.ps1` first; route style → model.

```
/localimage realistic Michael Jackson on stage, fedora, white glove
→ Flux fp8 photoreal

/localimage 4x hero photoreal concert portrait, clear face
→ pick best → refs/hero.png after QA

/localimage pixar redhead listening to music
→ ASK (no Pixar ckpt) — Flux photoreal or Krea?

/localimage krea stylized portrait
→ Krea path

/localimage edit .\refs\hero.png fix eyes, keep identity
→ img2img
```
