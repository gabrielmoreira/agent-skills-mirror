# CLI Advisors on Hermes

`ask` consults an outside model. When the advisor the user named is a coding CLI installed on this machine, Hermes bundles a skill for running that CLI from the terminal:

| Advisor | Bundled Hermes skill |
| --- | --- |
| Claude Code | `claude-code` |
| Codex | `codex` |
| OpenCode | `opencode` |

Load the one for the advisor the user named, when it is in your skill list, and take only the invocation from it: a single non-interactive run, started in the repository the question is about. Those skills are written for handing coding work to the CLI; here the CLI answers a question. A CLI with no bundled skill is run from its own help output, or reported as unavailable.

What stays with `ask`:

- The advisor is the one the user named or configured. None of these CLIs is the default, and this table recommends none of them.
- An advisor answers; it does not edit. Run it in its read-only or planning mode where it has one, or with its file-writing tools turned off, and read `git status` afterwards: a changed file means the run did more than advise, and you say so.
- The question carries what the advisor needs to answer: the question, and the files or excerpts it concerns. Secrets, credentials, and private material stay out unless the user opted in for this question.
- The answer is advice. Attribute it to the advisor, say which points you accept and which you reject and why, and record no review, verification, or approval from it.
- A run that fails, times out, or stops for a sign-in is reported as that, with no advice written in its place.
