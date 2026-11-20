# Prompts for admins, coordinators and PAs

For the people who keep registers, inboxes and diaries running.

---

### Create a tracking list from a plain-English description

**App:** SharePoint list agent (Microsoft Lists) · **Role:** Admin / coordinator · **Licence:** Microsoft 365 Copilot · **Last verified:** pending re-test

**Prompt:**
> Create a list to track [what you're tracking] for [team or project]. Columns: [field 1], [field 2], [field 3] … Make [status field] a choice column with the options [option A, option B, option C], and add a calculated column for [e.g. days open].

For example:
> Create a list to track requests for information on [project name]. Columns: request number, date raised, raised by, discipline, question, date response required, status, and days open. Make status a choice column with the options Open, Awaiting response, Closed.

**Use when:** you're about to build the same tracking spreadsheet again for a new job, team or quarter.

**Where it falls short:** this is web-only and still rolling out. Check the suggested column types before you click create. A date that's been set as text, or a person stored as a plain name, is painful to fix once the list has data in it. Copilot can't add permissions, views or Power Automate flows for you.

**Time saved:** _TBC from rollout feedback_

---

### File the one thing your inbox is drowning in, with a single command

**App:** Outlook (Copilot chat) · **Role:** Admin / coordinator · **Licence:** Microsoft 365 Copilot · **Last verified:** pending re-test

**Prompt:**
> Create a folder called "[folder name]", then move every email from the last [month] that mentions [keyword, reference number or sender] into it, and categorise them as [category].

For example:
> Create a folder called "Invoices – Q4", then move every email from the last month that has an invoice attached or mentions an invoice number into it, and categorise them as Accounts.

**Use when:** one type of email (invoices, supplier updates, a project's correspondence) is burying everything else.

**Where it falls short:** this works across Outlook on Windows, web, Mac and mobile, but only in English at launch. Copilot acts on your mailbox directly, so check the folder afterwards. Fuzzy criteria like "anything about the project" will sweep in false positives, while an exact reference number or sender won't. It can create inbox rules too, but read the rule it proposes before you accept it.

**Time saved:** _TBC from rollout feedback_
