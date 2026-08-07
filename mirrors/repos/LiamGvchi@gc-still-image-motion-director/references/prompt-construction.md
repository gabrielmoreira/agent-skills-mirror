# Image-to-Video Prompt Construction

Use this reference to turn a motion decision into a platform-ready prompt.

## Prompt Order

Write in this order:

1. camera and global stability;
2. primary subject action;
3. range, path, and timing;
4. physically related secondary response;
5. explicit lock list;
6. failure prohibitions;
7. duration and rhythm.

The source image already defines style, composition, and identity. Focus the prompt on motion control instead of redescribing the full image.

## Core Formula

```text
固定镜头，保持原图构图和版式。

只让【主体】在【原始区域】内沿【方向或路径】缓慢完成【一个动作】，
动作范围为【具体幅度】，从【起始状态】逐渐到【结束状态】。

同时让【关联元素】因为【同一物理原因】产生【轻微反应】。

【文字、数字、纸张、边框、照片框、批注、线稿及其他脆弱元素】完全固定。

禁止【最可能发生的3–6种错误】。
4秒，动作克制、连续，最后稳定下来。
```

Replace every bracket with image-specific content. Do not leave generic phrases such as "move naturally" as the only motion instruction.

## Describe Range Precisely

Prefer:

- rotate 3–5 degrees and return once;
- lower the rear knee while both feet stay planted;
- move within the existing blue square by less than 5% of its width;
- let two or three droplets descend inside the photo only;
- allow one narrow light pass across the specimen frame;
- bend the stem slightly toward the visible wind direction.

Avoid:

- move a little;
- cinematic motion;
- make the picture come alive;
- dynamic atmosphere;
- natural camera movement.

## Lock Lists

Name the fragile elements visible in the image. Common locks:

- English and Chinese text;
- numbers, dates, labels, and handwriting;
- old paper color and texture;
- collage geometry, tape, frames, and crop boundaries;
- grids, measurement lines, diagrams, arrows, and thin vector marks;
- subject count, face, clothing, silhouette, and object connectivity;
- background negative space.

"Keep everything else fixed" is helpful but not sufficient. Name the elements most likely to drift.

## Negative Constraints

Choose only relevant prohibitions:

- no camera push, pan, tilt, roll, or zoom;
- no paper breathing, rippling, or exposure flicker;
- no text rewriting, number changes, or layout reflow;
- no new subjects or disappearing subjects;
- no limb fusion, object morphing, or silhouette changes;
- no broken ropes, stems, handles, joints, or frame edges;
- no motion outside the photo or colored block;
- no full-frame glow, particles, or generic parallax.

## Examples

### Compass needle

```text
固定镜头。只让长指针围绕原轴心缓慢偏转3–5度，轻微回摆一次后停住。
短指针、轴心、蓝色延长线、英文文字、数字、纸张和所有排版完全固定。
禁止连续旋转、钟表式走针、轴心漂移、文字变化和纸张呼吸。
4秒，先停留，随后偏转并稳定。
```

### Rainy-window collage

```text
固定整张拼贴。只让窗户照片内部两三颗雨滴缓慢向下滑落，
窗外模糊树影出现极轻微明暗变化；花枝只向同一方向摆动几度。
照片边界、蓝色矩形、胶带、标题、箭头、文字和旧纸完全固定。
禁止雨水越出照片框、窗框变形、花枝脱离拼贴区域和镜头移动。
4秒，安静、稀疏，最后回到稳定。
```

### Moth specimen

```text
固定镜头，蛾类标本保持完全静止。
只让一层非常微弱的观察光在标本照片内部缓慢掠过一次，
随后恢复原有明暗。照片框、编号、文字、档案标记和纸张完全固定。
禁止蛾扇翅、飞行或改变形态，禁止照片变形、文字变化和全画面闪光。
4秒，像一次安静的档案观察。
```

### Swimmer symbol

```text
固定海报和蓝色方框。白色游泳者沿现有水平轴缓慢向前移动，
位移不超过蓝色方框宽度的5%；上下两条水纹产生一次小幅扩散后稳定。
标题、正文、方框边界、纸张纹理和留白完全固定。
禁止游泳者离开方框、身体变形、水纹扩散到纸面或镜头推近。
4秒，缓慢、平稳。
```

## Platform Adaptation

- When the user names a platform, use its requested language and known prompt conventions.
- Do not claim undocumented controls. If the platform exposes motion masks, brushes, regions, or keyframes, recommend limiting them to the allowed-motion regions.
- If platform behavior is uncertain, provide a platform-neutral prompt and state the uncertainty.
- If the user asks for a single prompt, do not add analysis around it.

## Repairing a Failed Result

When reviewing a generated clip:

1. identify the first frame where drift appears;
2. classify the failure as subject, connection, layout, text, paper, camera, or lighting drift;
3. replace broad language with a specific lock or bounded path;
4. remove extra motion instructions before adding more negatives;
5. retry with lower amplitude and fewer active regions.

Do not solve uncontrolled motion by making the prompt longer in every direction. Reduce the number of moving parts.
