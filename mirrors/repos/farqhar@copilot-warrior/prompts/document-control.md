# Prompts for document control and records

For the people who get asked "which one is the latest?" ten times a day.

---

### Ask a whole document library one question instead of opening five files

**App:** Copilot in SharePoint · **Role:** Document control · **Licence:** Microsoft 365 Copilot (admin opt-in) · **Last verified:** pending re-test

**Prompt:**
Open the document library, click the floating Copilot button, choose **Ask a question**, then:
> Across everything in this library, [your question]. For each answer, tell me which file it came from and link to it.

For example:
> Across everything in this library, list every place we've committed to a completion date, with the date, the document it's in and who issued that document.

**Use when:** the answer is spread across several files and you'd otherwise open them one at a time.

**Where it falls short:** Copilot in SharePoint needs an admin to opt in, and Microsoft's support page still labelled it public preview at the time of writing. It only reads what *you* have permission to see, and very large libraries may not be fully covered. Asking it to cite the file isn't decoration. Without the source, you can't tell a real answer from a confident guess.

**Time saved:** _TBC from rollout feedback_

---

### Find the current version of a document and what changed

**App:** Copilot Search → Copilot Chat · **Role:** Document control · **Licence:** Microsoft 365 Copilot · **Last verified:** pending re-test

**Prompt:**
Search Copilot for the document by name, then ask in chat:
> Which version of this is current, who last updated it, and what changed from the previous revision?

Or ask it from inside a SharePoint library:
> Find every revision of [document name] in this library. Tell me which one is current, who last updated it, and what changed in the latest revision.

**Use when:** there are three copies called `FINAL`, `FINAL v2` and `FINAL – use this one`.

**Where it falls short:** "current" means "most recently modified" unless your file names or metadata say otherwise. Copilot can't know which version was actually *issued*. If a revision was emailed as an attachment and never saved back to SharePoint, Copilot won't find it. "What changed" works well for Word documents and poorly for scanned PDFs and drawings.

**Time saved:** _TBC from rollout feedback_
