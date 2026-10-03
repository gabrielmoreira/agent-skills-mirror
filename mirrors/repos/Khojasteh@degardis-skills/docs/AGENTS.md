# Reader Documentation Conventions

Rules for writing a reader-facing page: the root `README.md`, a guide in `docs/`, or a skill's `README.md`. When a release rewrites one belongs to [`.github/AGENTS.md`](../.github/AGENTS.md).

## The pages

The root `README.md` is the catalog and entry point only: what the collection is, the security caution, one row per released skill with its version and download, where to ask, and an index of the guides. Anything longer is a guide, one per question:

| Guide | Owns |
| --- | --- |
| `installation.md` | Agent directories and scopes, platform notes, putting a downloaded or built skill in place, the installed version, upgrading (backing up changes, emptying the directory, removing superseded skills), sharing one copy, and AI chat apps that accept a ZIP. |
| `building-from-source.md` | Getting the source and compiler, and building a folder or ZIP. |
| `using-skills.md` | Naming the outcome, what a request carries, and choosing model capability by evidence. |
| `troubleshooting.md` | A skill the agent can't see, won't load, ignores after loading, or loses to another installed copy or skill. |
| `design-principles.md` | The behavior every published bundle shares, and what a skill cannot promise. |
| `feedback.md` | Discussions versus issues, field reports, and the problem-report prompt. |

- A guide belongs to the collection: it names a skill only as an example and carries no release mechanics.
- The root `README.md` and the guides stay domain-neutral. Examples come from work any reader recognizes, and a reader's work lives in their workspace, not a project or repository. Examples from one subject belong on that skill's README.
- Describe what a skill does for the reader, never how its bundle is built inside; that can change with any release.
- Link what another project owns instead of restating it: the Degardis source format and commands, or a host's settings and upload steps. State only what the reader needs to act here, and never describe another product's behavior you haven't verified.
- Behavioral claims about the skills belong in `design-principles.md`; another guide links there rather than restating one. Reconcile it against the principles the shipped skills share, and drop what a released skill no longer does.

## Voice

Every reader-facing page reads like a helpful colleague: second person, short plain sentences, one idea per paragraph, contractions where natural, and a reason rather than an order. Assume the reader knows the basics of AI agents and skills but is new to this collection. Safety notices stay direct and unhedged: the install warning, the guidance-is-not-a-guarantee caution, and every instruction to sanitize a report.

## A skill README

Write it for an end user deciding whether to install the skill. It owns the skill's download link, security warning, and links to the guides. It doesn't repeat installation, invocation, design principles, or troubleshooting prose, and carries no release mechanics. Add no category or collection READMEs under `skills/`.

## What a page may claim

README and catalog text describe the bundle this snapshot publishes, not unreleased source. A never-released skill may describe work in progress, but has no catalog row or download link; point it at the build-from-source guide.

A skill the last release published keeps its catalog row, download link, and inbound links until the release that retires it drops them, even once its directory is gone, per [`RETIRING.md`](../.github/RETIRING.md).

`.github/scripts/check-docs.py` checks version lines, catalog rows, and that every relative link, release link, and heading fragment resolves; don't restate those checks as prose.
