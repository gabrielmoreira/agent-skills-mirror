# LoopX Adopters

> [简体中文](docs/project/adopters.zh-CN.md)

This is a voluntary, self-attested directory of projects and users who choose
to use LoopX. An entry records a public relationship; it is not a testimonial,
certification, security review, support commitment, or maintainer endorsement.

Looking for projects using or building on LoopX? Browse the
[maintainer-observed ecosystem inventory](docs/community/ecosystem-adoption.md):
it links [development workflows and integrations](docs/community/ecosystem-adoption.md#1-workflows-and-integrations),
[mechanism borrowing](docs/community/ecosystem-adoption.md#2-mechanism-borrowing),
and [proposals with their current limits](docs/community/ecosystem-adoption.md#3-proposals-and-deferred-adoption).
Those public-source observations are maintained there; this directory records
projects and users describing their own use, including planned or experimental trials.

## Current Directory

No projects or users have submitted a self-attested entry yet. This is the
registration status of this directory, not a count of LoopX users. The
[ecosystem inventory](docs/community/ecosystem-adoption.md) already records
public evidence of use. Projects and users can voluntarily add or confirm
their own entry below; observed cases are not copied into this table on their behalf.

| Project or user | Public link | Adoption mode | Status | Public note | Last verified |
| --- | --- | --- | --- | --- | --- |

### Adoption modes

- **Integration** — calls LoopX CLI or contracts from a real project workflow.
- **Workflow** — uses LoopX to govern a recurring or long-running work lane.
- **Learning** — follows LoopX contracts in a tutorial, book, course, or study.
- **Derivative** — builds a fork, package, adapter, or adjacent tool inspired by
  LoopX and identifies the relationship clearly.

Use `active`, `experimental`, `planned`, or `paused` for status. A user may
identify themselves by a public handle or project name; no legal name or private
organization detail is required.

## Add Or Update An Entry

Project and user owners may add, update, or remove their own row through a small
pull request. No private account, internal deployment, credential, customer
detail, raw transcript, or unverifiable performance claim belongs here.

Copy this shape and replace only the fields you can support publicly:

```md
| Project or user | Public link | Integration / Workflow / Learning / Derivative | active / experimental / planned / paused | One sentence describing the public use and boundary | YYYY-MM-DD |
```

The contributor should:

1. use a public project, profile, issue, pull request, release, or documentation
   link;
2. state what is actually used and whether the entry is planned or running;
3. avoid claiming LoopX caused an outcome unless the public evidence supports
   that claim;
4. run the repository's public/private boundary and documentation checks; and
5. sign the commit according to [`CONTRIBUTING.md`](CONTRIBUTING.md).

This is intentionally a narrow public-doc change. A collaborator with merge
permission may self-merge a clean entry after the required checks pass; a
project or user without that permission can submit the same focused PR for the
normal maintainer merge path. Adding a row never grants repository, product,
support, or endorsement authority.

Owners can request removal at any time. Maintainers may ask for a stale link to
be updated or remove a confusing, private, or unsupported claim while keeping
the change history public.
