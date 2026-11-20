# S2 · Brand-consistent deck builder

**What it does:** teaches Copilot in PowerPoint your house rules once. That covers sentence-style titles, bullet limits, standard structure, number format and a standard summary slide. Every deck it builds or restyles then follows them.

**Licence:** Microsoft 365 Copilot · **App:** Copilot in PowerPoint · **Status:** draft, pending live test · **Last verified:** pending re-test

## When to use it
- Starting a new deck from a brief or a Word document.
- "Make this on-brand" on a deck someone else built.
- The one-slide summary you rebuild for every proposal, bid or board paper.

## Setup
1. Download [`SKILL.md`](SKILL.md) and **edit everything in [square brackets]** to match your organisation: bullet limits, number format, organisation name.
2. Save it in a folder called `brand-deck-builder` inside the **Skills** folder in your OneDrive.
3. Open your organisation's PowerPoint template, open the Copilot pane, then go to **+ → Skills → brand-deck-builder**.
4. Try: *"Use brand-deck-builder to make a summary slide from the attached brief."*

Tip: also save your template as the default for new presentations. The skill uses whatever layouts are in the open file, so a good template does half the work.

## Limits
- A skill can't hold your actual colours, fonts or logo. Those come from the **template**. The skill enforces *how* slides are written and structured, not the design system itself.
- Microsoft's release notes listed PowerPoint custom skills as web at launch, while the support page listed desktop, Mac and iPad. Check it on your own setup before rolling it out to a team.
- Copilot will occasionally ignore a word limit on a dense slide. Ask it to "apply brand-deck-builder rules again to slide N".

See [`example-output.md`](example-output.md).
