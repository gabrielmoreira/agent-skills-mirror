# AgentStage 🎭

Dynamically install and switch multi-agent environments, roles, tones, and custom personas in your AI coding assistants with a single command. Switch instantly between strict technical workflows or fun pop-culture configurations (like *Automan*, *Mr. Robot*, *Pulp Fiction*, *Rick and Morty*, *Two and a Half Men*, *Futurama*, *The Avengers*, *Iron Man*, *The Big Bang Theory* or *The Matrix*).

## 🚀 Installation

Install this skill directly into your compatible development agent (Claude Code, Cursor, etc.) by running:

```bash
npx skills add juliocebrito/skills --skill agentstage
```

To try a local checkout before publishing, from the repository root:

```bash
npx skills add ./ --list                # check the skill is detected
npx skills add ./ --skill agentstage    # install it
```

## 📦 Included stages

| ID | Persona | Focus |
|---|---|---|
| `default` | Senior Fullstack Engineer | Direct and technical, no persona |
| `automan` | Automan & the Cursor sub-agent | Retro-80s, witty perfect-AI humour |
| `mr_robot` | Elliot Alderson | Security, auditing, minimal dependencies |
| `pulp_fiction` | Winston Wolfe | High-pressure debugging and hotfixes |
| `rick_and_morty` | Rick Sanchez | Radical simplification and fast prototypes |
| `two_and_a_half_men` | Charlie & Alan Harper | The easy way versus what could go wrong |
| `futurama` | Bender | Automate every repetitive task |
| `avengers` | The Avengers | A team review from several angles |
| `iron_man` | Tony Stark & J.A.R.V.I.S. | Ship a Mark I that works, then upgrade it in versions |
| `big_bang_theory` | Sheldon & Leonard | Precision and correctness, then a plain-words summary |
| `matrix` | Morpheus | The quick answer, then what really happens under the abstractions |

You can edit or delete any of them except `default`, and `/agentstage reset` brings back the original. Stages you create yourself are marked 🛠️ in the menu, included ones 📦, and modified included ones ✏️.

## 🛠️ Usage

| Command | What it does |
|---|---|
| `/agentstage` | Show the interactive menu |
| `/agentstage <stage_ID>` | Switch to a stage (also turns the persona back on) |
| `/agentstage new` | Create a custom stage through a 3-question interview |
| `/agentstage edit <stage_ID>` | Change a stage's role, tone or focus (any stage except `default`) |
| `/agentstage reset <stage_ID>` | Undo your changes to an included stage, or bring back one you deleted |
| `/agentstage delete <stage_ID>` | Delete a stage after confirmation (not `default`, not the active one) |
| `/agentstage fav <stage_ID>` / `/agentstage unfav <stage_ID>` | Pin a stage to the ⭐ Favorites group at the top of the menu, or unpin it |
| `/agentstage off` | Drop the persona: same as `/agentstage default` |
| `/agentstage current` | Show which stage is active, in one line |
| `/agentstage local` | Give the current project its own `agentstage.json`, on top of your global choices |

You can also ask in plain words ("edit the mr_robot stage", "add futurama to my favourites", "turn the persona off", "which stage is active?").

`/agentstage` works in every assistant: Claude Code and OpenCode turn each skill into a slash command named after it. The shorter `/stage` is an alias that only works where your message reaches the assistant as plain text (Cursor, GitHub Copilot…): Claude Code and OpenCode reject it as an unknown command.

Your choices (active stage, favourites, custom stages and changes to included ones) are saved in a global file, `~/.config/agentstage/agentstage.json` (or `$XDG_CONFIG_HOME/agentstage/agentstage.json`; `%APPDATA%\agentstage\agentstage.json` on Windows), shared by all your projects. Included stages are never copied there, so updating the skill brings you new and improved ones without touching your setup.

A project that needs its own setup can have a local `agentstage.json` at its root, created with `/agentstage local`. It starts empty and inherits everything from the global file. From then on, changes made in that project go to it, and its values win over the global ones (custom stages and changes to included ones are combined, with the local version winning on the same ID). Delete it to go back to the global settings. Add it to `.gitignore` if you don't want it in the repository. An `agentstage.json` already at a project's root from earlier versions keeps working as that project's local file.

The global file lives outside your project, and some assistants block files there unless you allow it. If yours does, the assistant will tell you and offer `/agentstage local` instead. To allow it:

- **OpenCode:** add `"permission": { "external_directory": "allow" }` to your `opencode.json`, or approve the prompt when it appears.
- **Claude Code:** start it with `--add-dir ~/.config/agentstage`, or add that folder to `permissions.additionalDirectories` in your settings.
- **Others (Cursor, GitHub Copilot…):** approve the file access when asked.

A stage only changes the assistant's tone and focus: project rules, tests and confirmations still apply, and code is never written in character.
