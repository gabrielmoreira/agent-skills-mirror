# Settling the language

The ubiquitous language: one vocabulary the user and the code share inside a bounded context. Follow this whenever domain words come up: in step 2 of this skill, or during feature-design's or ux-brainstorm's interview, where your questions join that skill's round, follow its question rules, and count against its budget.

Collect the terms in play: the user's words, `GLOSSARY.md`'s, the code's, and the docs'. For each one:

- **One meaning per context.** When a word has two meanings and both are right ("customer" in sales and in billing), that is evidence of two bounded contexts: note it for the architecture step rather than qualifying the word ("billing customer").
- **The experts' words.** Operations are domain verbs (`credential.revoke(reason)`, not `updateStatus(3)`); events are past tense (`CredentialRevoked`); names come from the domain, never from patterns (`Manager`, `Helper`).
- **Hidden events.** "When…", "after…", "if that happens…", and "notify…" usually hide a domain event. Name it.
- **Implicit concepts.** A flag, a status code, a cluster of conditionals, or an awkward method name often hides a concept the experts already name: a policy, a constraint, a specification. Give it a term.

Settle each term from the code and docs when you can. When the user's word differs from the project's ("booking" where the code says "loan"), name the project's term and use it from then on. When only the user can say, ask a concrete scenario with realistic names and two to four answers: "Ana returns one item from a shipped order. Is that a *cancellation*, a *return*, or something else?" Write each term into `GLOSSARY.md` in the turn it is settled, per [formats.md](formats.md#glossary).

Done when every term the work touches has one meaning per context, a code name, and the words to avoid, and every conflict between the user, the glossary, and the code is settled or is a question.
