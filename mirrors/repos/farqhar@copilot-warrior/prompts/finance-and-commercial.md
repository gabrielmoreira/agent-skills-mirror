# Prompts for finance and commercial

For people whose spreadsheets have to be right, not just fast.

---

### Add a calculated column, then click through every change Copilot made

**App:** Copilot in Excel · **Role:** Finance / commercial · **Licence:** Microsoft 365 Copilot · **Last verified:** pending re-test

**Prompt:**
> In this [report], add a column showing [the calculation] for each [row type], highlight any [row type] where [the threshold], and build a summary table of the five largest [outliers].

For example:
> In this cost report, add a column showing the variance between budget and actual for each cost code, highlight any code more than 10% over budget, and build a summary table of the five largest overruns.

Then **click every link in Copilot's reply.** Each one jumps to something it changed: a new sheet, table, range or chart. The Show Changes pane also labels which edits came from Copilot.

**Use when:** you want Copilot to do the formula work, but you need to sign off on the number.

**Where it falls short:** the links show you *where* Copilot changed things, not *whether* the logic is right. Check one row by hand. Copilot works best on a clean table with headers. Merged cells, subtotal rows mixed into the data and multiple tables on one sheet all confuse it. The file needs to be saved to OneDrive or SharePoint.

**Time saved:** _TBC from rollout feedback_

---

### Build an interactive dashboard slide

**App:** Copilot in PowerPoint (Interactive Slide) · **Role:** Finance / commercial · **Licence:** Microsoft 365 Copilot · **Last verified:** pending re-test

**Prompt:**
Home ribbon → **Interactive Slide**, then:
> Create an interactive dashboard slide for [report name]. Show [metric 1], [metric 2] and [metric 3] for each [category], using the figures in [attached file or pasted table]. Let me click a [category] to open its detail.

For example:
> Create an interactive timeline slide for the [project name] programme. Show each stage from start-up to completion, with the key dates, who's responsible and the main hold points. Let me click a stage to open its detail.

**Use when:** a monthly report slide is too dense and you'd rather let the audience drill in.

**Where it falls short:** the interactivity only works in slide show on Windows, Mac and web. It doesn't work on iPhone or Android, or when the deck is printed or saved to PDF, so always keep a static fallback slide. At launch it was rolling out in stages, so some people won't see the button yet. Check every number on the slide against the source. Copilot builds the layout well but can transpose figures.

**Time saved:** _TBC from rollout feedback_
