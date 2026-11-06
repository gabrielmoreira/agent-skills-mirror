# Vox : une photo devient une animation de cinéma

Un skill pour Claude Code qui transforme une simple photo en animation façon documentaire Vox : la photo en similigravure détourée aux ciseaux, du papier déchiré, du grain, des mouvements en stop-motion et une caméra qui avance lentement. Tu décris ton idée, Claude fait l'animation, et tu changes n'importe quoi avec un autre prompt (« fais-le avec Napoléon »).

## En 3 étapes

1. **Installe Codex à côté de Claude Code** : c'est lui qui génère les images, avec ton abonnement ChatGPT.

   ```bash
   npm i -g @openai/codex
   codex login
   ```

2. **Ajoute le skill à Claude**, dans le dossier de ton projet :

   ```bash
   npx skills add Melvynx/video-agent-skills --skill vox -a claude-code
   ```

3. **Envoie ta photo et décris ton idée** dans Claude Code :

   ```text
   /vox photo.jpg Victor Hugo à Paris en 1885, avec des journaux de l'époque qui tombent autour de lui
   ```

   Puis modifie-la avec un autre prompt : « fais-le avec Napoléon », « ajoute un train », « passe en 16:9 ».

Il te faut aussi ffmpeg et Node 20+ (Claude vérifie et te dit quoi installer).

## Ce que fait le skill

- Garde ta vraie photo (jamais redessinée par une IA), la détoure et l'imprime en similigravure par code.
- Fait générer le décor et les objets par Codex (un calque par image, sur fond vert, détourés avec ffmpeg).
- Assemble tout dans une page HTML animée (tu la vois jouer dans ton navigateur), puis l'exporte en MP4 1080x1920.

---

# Vox: one photo into a cinematic paper-collage animation (English)

A Claude Code skill that turns one photo into an animation in the style of Vox explainer documentaries: halftone cut-outs with a white scissor border, torn paper, grain, stop-motion moves and a slow camera push-in. Describe your idea, then change anything with one more prompt.

```bash
npm i -g @openai/codex && codex login          # Codex makes the images with your ChatGPT plan
npx skills add Melvynx/video-agent-skills --skill vox -a claude-code
```

Then in Claude Code: `/vox <photo> <your animation idea>`. Needs ffmpeg and Node 20+.

Part of [video-agent-skills](https://github.com/Melvynx/video-agent-skills): free skills to script, edit and publish your videos with Claude Code.
