---
date: 2026-09-29
title: 'Install the media engine in one click, with no setup tour'
---

# 2026-09-29 — Install the media engine in one click, with no setup tour

- **Context:** until the stable-diffusion.cpp engine was installed, the Images
  and Video pages showed a card with two numbered steps (engine, model) and a
  "Start setup" button. That button opened a two-step dialog: an intro page,
  then an engine row with its own Install button, then Done. Getting the
  engine took four clicks through a modal that repeated what the card said.
  The model step was already out of the tour: the studio's empty canvas offers
  "Download model" and opens the form's picker.
- **Decision:** the card is the first screen and carries one primary button,
  "Install the image engine" ("Install the media engine" on Video), which
  starts the install directly. Progress stays on that button as a fill and a
  percentage, with the byte count below it. A failure shows its reason in the
  same slot, and the button is the retry. The downloads panel and the "Image
  engine is ready" toast are unchanged. When the engine lands, the page opens
  the studio, and the canvas offers the model download. The `install` error
  action, and `download` while the engine is missing, also start the install
  instead of opening a dialog. The setup dialog keeps only the model list that
  Media settings opens. The intro and engine steps are removed, and so are
  `setupStep` and their strings.
- **Consequences:** it takes one click from an empty page to the studio.
  Nothing on first run is modal. The byte count and the error share one fixed
  slot, and the idle label holds the button's width while the percentage shows,
  so the centered card does not move during the install. That is measured in
  `ImageSetupCard.layout.test.tsx`. The intro bullets (privacy, recipes) no
  longer appear anywhere. The card's description still says the page runs
  locally. A host with no engine build sees the reason on the card, with no
  button.
- **Owner:** team
- **Links:** `web-app/src/containers/images/ImageSetupCard.tsx`,
  `web-app/src/containers/dialogs/ImageSetupDialog.tsx`, commit a2682b84c
  (the studio opens once the engine is installed).
