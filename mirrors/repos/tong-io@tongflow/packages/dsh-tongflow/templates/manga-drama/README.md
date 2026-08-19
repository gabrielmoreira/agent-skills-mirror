# {{title}}

Manga-drama production, run like a film crew. This folder is the single source
of truth: the agent writes text here, TongFlow workflows generate media into
numbered takes, and you circle the takes you like.

```
project.json          project manifest
story/                treatment, outline, script (plain text — written by the agent)
world/<ID>/           cast & world: CHR_ characters · LOC_ locations · PRP_ props · STY_ style
                       card.md · consistency.json · REF/ (reference images) · VO/ (voice reference)
episodes/EP01/        scenes.json — the shot breakdown (scenes → shots, dialogue, prompts)
                       + MUS/ SFX/ MIX/ CUT/ (episode-level audio and the cut)
shots/<SHOT>/         SB/ storyboard · KF/ keyframe · ANI/ animation · DLG/ dialogue audio
inbox/                files you drop in for the crew
workflows/            one *.tongflow.json per generated asset (open on the canvas); templates/ = starting shapes
notes/                review notes and the agent's own QC reports
export/               finished deliverables
```

Ids: `EP01` · `EP01_SC003` · `EP01_SC003_SH0010` · `CHR_MEI` · takes `T01…`.
References: `tf://CHR_MEI/REF`, `tf://EP01_SC003_SH0010/KF`, `tf://EP01/ANI`, `tf://EP01_SC003_SH0010/dialogue`.

{{logline}}
