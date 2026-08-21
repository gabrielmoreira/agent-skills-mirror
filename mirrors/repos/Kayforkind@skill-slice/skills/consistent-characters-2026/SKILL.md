---
name: consistent-characters-2026
description: "Locks a still-image identity with a six-tier ladder from a single canonical hero frame: verbatim tokens, Midjourney --cref/--cw and v7 --oref/--ow, InstantID/PuLID, Flux Kontext/USO star edits, then a character LoRA, gated by a contact sheet. Use for comics, mascot pose packs, turnarounds, or NPC expression grids. Never treat this as a video/ComfyUI animation graph (consistent-character-builder); not a style-only --sref chair or a rigged-3D identity source."
version: 1.0.1
---

# Consistent Characters 2026

## When to Use

Activate this skill whenever the job-to-be-done is **identity persistence**: the same recognizable subject must survive across more than one image. Trigger on requests like:

- "Make a comic / storyboard / picture book where the hero looks the same on every page."
- "Generate a product mascot in 12 marketing poses."
- "I have one photo of a person — put them in 5 different scenes / outfits / lighting setups."
- "Create a character turnaround (front / 3-4 / profile / back)."
- "Keep this face but change the background / clothing / age / expression."
- "Build a contact sheet of expressions for a game NPC."
- Any multi-shot narrative (manga panels, ad campaign, brand spokes-character, avatar set, dataset for a downstream LoRA).

**Situational conditions that raise priority:**

- The deliverable is a *set* (≥2 images), not a one-off hero shot.
- The subject is a *named, reusable* identity (recurring character, IP, real person with rights/consent).
- Downstream work depends on consistency (LoRA dataset curation, animation reference, sprite sheets).
- The client has already rejected a draft for "it doesn't look like the same person."

### When NOT to use

- **Single, disposable image** with no recurrence requirement — just prompt directly; identity-locking machinery adds cost and rigidity for no benefit.
- **Style consistency without identity** (e.g., "same painterly look across a series" but different subjects) — that is a *style-reference* problem (`--sref`, style LoRA, USO style mode), covered by the style-lock skill, not character identity.
- **Generic "a man," "a woman," "a robot"** with no need to be the *same* one twice — locking a non-identity wastes effort and reduces variety.
- **Real-person likeness without consent / rights**, deepfakes of private individuals, or impersonation for deception. Decline and redirect to original or consented identities. Likeness of public figures for deceptive or harassing purposes is out of scope.
- **Pure text-to-3D or rigged-model pipelines** where the engine itself guarantees identity — there the model is the source of truth, not the diffusion sampler.

## Prerequisites

- Access to at least one generation platform: Midjourney (v6 or v7), Flux (FLUX.1 Kontext, USO, PuLID-FLUX, or FLUX.1 LoRA training), or a ComfyUI/Automatic1111 environment with IP-Adapter/InstantID/PuLID/ControlNet nodes installed.
- For LoRA training (Tier 5): 15–30 curated images of the subject with varied angles, expressions, and lighting; a training environment (e.g., Kohya, ai-toolkit, or equivalent FLUX LoRA trainer).
- For real-person likeness: confirmed rights/consent documentation before proceeding.

## Procedure

The universal arc is **Establish → Build → Lock → Verify**. Pick the platform track, but the gates are the same. Always produce a single **canonical reference** ("the source of truth") early, and reference *it* — not derivatives — for every shot.

### The Consistency Ladder (loosest → tightest)

Start at the lowest tier that could plausibly work, verify, and climb only when verification fails. For a short series, Tier 2–3 usually suffices. For an ongoing franchise, invest once in Tier 5.

| Tier | Mechanism | Identity strength | Flexibility (pose/scene) | Cost / setup | Best for |
|------|-----------|-------------------|--------------------------|--------------|----------|
| 0 | Seed + verbatim prompt token | Very low | High | Free | Same session, same model, minor variations only |
| 1 | Textual identity anchor (detailed, named description) | Low | High | Free | Stylized/illustrated characters with distinctive features |
| 2 | Single image reference (MJ `--cref`/`--oref`, IP-Adapter) | Medium | Medium-High | Low | "One ref → many scenes," fast iteration |
| 3 | Face-embedding ID (InstantID, PuLID, IP-Adapter FaceID) | High | Medium | Medium | Photoreal faces from 1–4 photos |
| 4 | In-context edit (Flux Kontext, MJ retexture/edit) | High (preserves the *given* image) | Low-Medium | Low-Medium | "Keep this exact image, change one thing" |
| 5 | Trained character LoRA / DreamBooth | Very high | Very high | High (training time + dataset) | Production, recurring IP, many shots over time |

### Phase A — Establish the Canonical Reference (all platforms)

1. **Write the identity brief.** Lock the immutable traits in words even if you'll use image refs: name, age range, sex/gender presentation, ethnicity, face shape, eye color, distinctive marks (scar, freckles, mole), hair (color/length/style), build/height, and 1–2 signature wardrobe/props *only if* they're part of the identity. Keep this brief verbatim and reuse it token-for-token.
2. **Generate candidate hero frames.** Produce 4–8 front-facing, neutral-lighting, clear-face options. Front, eye-level, unobstructed face is mandatory for a good reference — it is the highest-information view for every downstream tool.
3. **Select and upscale ONE** as the canonical reference. Favor a clean, well-lit, expression-neutral frame. Upscale it; this becomes the only image you cite as `--cref`/`--oref`/IP-Adapter input/Kontext base.
4. **Optionally build a character sheet** (turnaround + expression strip) from the canonical frame to widen the reference pool before scaling out.

### Phase B — Midjourney Track (Build & Lock)

**v6.x — Character Reference:**
- `--cref <image_url>` with `--cw <0–100>`.
  - `--cw 100` (default) = copy face **and** hair **and** clothing.
  - `--cw 0` = copy the **face only** — the correct setting when you want to *change* the outfit/scene but keep the person.
  - Intermediate values blend. Drop `--cw` toward 0 whenever wardrobe or context must change.

**v7 — Omni-Reference:**
- `--oref <image_url>` with `--ow <0–1000>` (default 100). Omni-Reference generalizes beyond faces to any subject (characters, creatures, objects, props) and is the successor to `--cref` for v7 pipelines. Raise `--ow` for stronger adherence; lower it when omni-reference fights your prompt or causes pose-locking. Very high `--ow` over-copies the reference pose/crop — keep it moderate for new poses.

**Style Reference:**
- `--sref <image_url>` (with `--sw` style weight) controls *look*, **not identity**. Combine `--cref`/`--oref` (who) with `--sref` (how) to hold both identity and art style across a series.

**Steps:**

1. From the canonical upscaled image, copy its URL.
2. For each new shot compose: `<scene + action prompt> --cref <canonical_url> --cw <value>` (v6) or `--oref <canonical_url> --ow <value>` (v7).
3. **Set the weight by intent:**
   - Same outfit & look across shots → `--cw 100` / higher `--ow`.
   - New outfit / new scene, keep the person → `--cw 0` (face only) / moderate `--ow`.
4. Hold art style with `--sref <style_url> --sw <value>` reused across the whole series.
5. Keep the *same* `--cref`/`--oref` URL for every panel. If a panel is excellent, you may *add* it to your reference pool, but the original canonical frame stays primary to prevent drift.
6. Upscale keepers; reject and re-roll off-model results rather than "fixing" them downstream.

### Phase C — Flux Track (Build & Lock)

Choose the sub-track by task:

**"Keep this image, change one thing" → Flux Kontext:**
1. Load the canonical frame as the Kontext base.
2. Issue a *minimal, explicit* edit instruction: "Change the background to a rainy Tokyo street at night. Keep the character's face, hairstyle, and outfit exactly the same."
3. Generate, verify identity, then branch *new* edits **from the canonical frame again** (star pattern), not serially from each edited output (chain pattern), to avoid cumulative drift.

**"Same subject, new scenes/styles from scratch" → USO subject mode:**
1. Provide the canonical frame as subject reference.
2. Prompt the new scene/pose; add a style reference only if a look change is also wanted.
3. Tune subject strength so the face holds without copying the original pose.

**"Photoreal face from a few photos" → PuLID-FLUX (Tier 3):**
1. Supply 1–4 clean face shots.
2. Set ID weight.
3. Prompt scene/pose freely.

**"Production, many shots over time" → Character LoRA (Tier 5):**
1. Curate 15–30 images: varied angles, expressions, lighting; consistent identity; clean backgrounds; minimal occlusion. Quality and *variety* beat quantity.
2. Caption with a unique trigger token (e.g., `ch_arden`).
3. Train the FLUX LoRA; validate on held-out prompts.
4. Generate all future shots with the trigger token + scene prompt. Combine with ControlNet for pose control as needed.

### Phase D — IP-Adapter / Open-Source Track (Build & Lock)

1. **Identity layer:** load IP-Adapter FaceID / InstantID / PuLID with the canonical face; set adapter weight ~0.5–0.8.
2. **Structure layer:** add ControlNet for each shot — `openpose` for body pose, `depth` for scene volume, `face landmarks` for a specific expression. Drive these from pose references or a posed 3D dummy.
3. **Look layer:** apply a style LoRA or style reference if the series needs a unified art direction.
4. Generate; if identity is weak, raise the adapter weight or add a second face reference; if pose is wrong, strengthen/swap the ControlNet, **not** the identity weight.
5. Batch the shot list, then run the Verification Gate before delivery.

**Mental model:** Identity (face embedding/LoRA) + Structure (ControlNet) + Look (style ref/LoRA) are three independent axes. Lock the ones the brief requires; leave the rest free for variety.

### Phase E — Lock the Recipe

Record the exact, reproducible recipe so the *next* session reproduces the character: model + version, canonical reference URL/file, all weights (`--cw`/`--ow`/`--sw`, adapter weights, LoRA name + trigger + strength), seeds where relevant, and ControlNet configs. This recipe **is** the deliverable's reproducibility guarantee.

## Pitfalls

| Failure mode | Typical cause | Fix |
|--------------|--------------|-----|
| **Prompt drift** (face slowly changes across a series) | Chain-referencing each new output instead of the canonical frame; cumulative Kontext edits | Always reference the **same** canonical image (star pattern). For Kontext, branch every edit from the locked hero frame, not from prior edits. Re-establish a fresh canonical frame if drift has set in. |
| **Clothing / wardrobe bleed** (outfit copies when you wanted it changed) | `--cw` too high in MJ; identity ref encodes clothes | Set `--cw 0` (face only) in v6; lower `--ow` in v7. In Flux/IP-Adapter, mask the body and inpaint new wardrobe, or use a face-only embedding (FaceID) rather than a full-image reference. |
| **Background bleed** (scene from the reference leaks in) | Full-image reference at high weight | Lower reference weight; use face-only/FaceID; or generate on a clean background then composite/inpaint the new scene. Crop the reference tighter to the face. |
| **Gender / race / age drift** | Weak identity signal; prompt tokens fighting the reference; ambiguous canonical frame | Strengthen identity (raise adapter weight, switch to InstantID/PuLID or a LoRA). Remove conflicting descriptors from the prompt. Ensure the canonical frame is unambiguous, front-lit, unoccluded. Add explicit, accurate identity tokens to reinforce, never to override, the reference. |
| **Face distortion / melting / asymmetry** | Face too small in frame (low pixel area); extreme pose; over-stacked conditioners | Compose so the face occupies enough pixels; add a `face landmarks` ControlNet; reduce conflicting weights; for tiny faces, generate the portrait separately and composite, or use a face-restore/detailer pass. |
| **Scale / proportion issues** (head-to-body ratio changes, child vs adult slip) | No structural anchor; model defaults | Add `openpose` + `depth` ControlNet to fix body proportions; specify height/build in the brief; use a posed reference skeleton for every shot. |
| **Expression won't change** (identity tool freezes the face) | Identity weight too high; reference expression dominates | Lower identity weight slightly; drive expression with a `face landmarks` ControlNet or explicit prompt; in MJ lower `--cw`/`--ow`. |
| **Pose-locking / "same crop every time"** (MJ Omni-Ref) | `--ow` too high copies pose/composition | Reduce `--ow`; describe the new pose explicitly; provide a pose reference. |
| **Identity weak in profile / back views** | Face embeddings are frontal-biased; little side data | Build a turnaround into the reference pool; for back/profile, lean on a LoRA trained with multi-angle data, or ControlNet pose + looser identity. Accept that pure face-embedding tools degrade off-frontal. |
| **Twins problem** (two characters blend into each other) | Single shared reference; adapters cross-contaminate | Use regional/attention masking so each subject's identity binds to its own region; generate separately and composite when masking fails. |
| **Lighting-induced identity shift** | Strong colored/low-key lighting changes apparent skin/features | Lock lighting in the brief for the series, or normalize via Kontext "keep identity, relight" edits; verify under the target lighting before mass-producing. |
| **LoRA overfitting** (same pose/expression/background every time) | Training set too small or too uniform | Retrain with more varied angles, expressions, lighting, and backgrounds; lower LoRA strength at inference; add prompt/ControlNet variety. |

**Cross-cutting heuristics:**

- When identity *and* something else are both wrong, **fix identity last** — get pose/composition/scene right with structure tools, then dial identity up.
- Prefer **fixing inputs over fixing outputs**: a better canonical frame or tighter crop beats a downstream patch.
- If three re-rolls fail at the current tier, **climb the ladder** rather than fighting the knobs.

## Verification

Do not deliver a character set until every applicable item passes. Treat this as a hard gate, not a suggestion.

**Visual identity check (run on the full set side-by-side):**

- [ ] **Contact sheet built.** All shots tiled into a single grid at uniform size for direct comparison.
- [ ] **Face match across all shots.** Eye color, eye shape/spacing, nose, jaw/chin, brow, lip shape are consistent. No shot reads as "a different person."
- [ ] **Distinctive marks persist.** Every signature trait from the identity brief (scar, freckles, mole, heterochromia, etc.) appears, in the correct place, on every relevant shot.
- [ ] **Hair consistent** in color, length, and style (allowing only intentional, briefed changes).
- [ ] **Skin tone / ethnicity stable** across all lighting conditions — no race or tone drift.
- [ ] **Age presentation stable** — no slips between child/adult/elderly.
- [ ] **Build & proportions stable** — head-to-body ratio and height read consistently.

**Multi-angle / multi-expression validation:**

- [ ] **Angle coverage tested.** Identity holds at front, 3-4, and profile (and back if required). Off-frontal views verified explicitly, not assumed.
- [ ] **Expression range tested.** At least neutral + 2 emotions (e.g., smile, anger/surprise) generated; identity survives expression changes.
- [ ] **Pose variety tested.** At least one non-portrait, full-body or action pose confirms identity holds beyond the headshot.

**Wardrobe / scene isolation (when variation was requested):**

- [ ] **Outfit changed without identity change**, and vice versa — wardrobe and identity are independently controllable.
- [ ] **No background bleed** from the reference into shots that should have new scenes.

**Production / reproducibility:**

- [ ] **Canonical reference recorded** (the single source-of-truth image/URL).
- [ ] **Recipe recorded** — model + version, all weights (`--cw`/`--ow`/`--sw`, adapter weights, LoRA name/trigger/strength), seeds, ControlNet configs — sufficient to reproduce the character in a future session.
- [ ] **Rights / consent confirmed** for any real-person likeness; no impersonation or deceptive use.
- [ ] **Off-model rejects discarded**, not shipped — every delivered frame passes the face-match check above.

If any box fails: identify the failure mode in Pitfalls, apply the fix or climb the consistency ladder, regenerate the affected shots, and re-run the gate. Ship only a fully passing set.
