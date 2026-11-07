# QuantDinger Roadmap

QuantDinger's public roadmap connects product direction with scoped, reviewable
contributions. Use the public
[QuantDinger Roadmap project](https://github.com/orgs/OpenByteInc/projects/1)
to follow planning and delivery. The canonical roadmap index is
[#257](https://github.com/OpenByteInc/QuantDinger/issues/257), and progress for
the current theme is also visible in the
[Portfolio Research and Execution milestone](https://github.com/OpenByteInc/QuantDinger/milestone/1).

Roadmap items communicate direction rather than release-date promises. Proposed
work may change after technical review, user feedback, security analysis, or
provider validation.

## Planning stages

| Stage | Meaning |
| --- | --- |
| Proposed | A problem has been recorded, but the scope is not committed. |
| RFC | Product behavior and architecture are being designed. |
| Ready | Acceptance criteria and ownership boundaries are clear. |
| Claimed | A contributor and maintainer have agreed on scope. |
| In progress | Implementation or documentation work is active. |
| Review | A pull request is open and under review. |
| Done | The change is merged and documented. |

We use **Now**, **Next**, **Later**, and **Exploring** as planning horizons.
They are not delivery guarantees.

## Current roadmap theme

The first public theme builds a reproducible path from dynamic universe
selection through portfolio research, pair/spread modeling, execution, and
auditable analytics.

| Workstream | Priority | Horizon | Tracking issue |
| --- | --- | --- | --- |
| Dynamic universe and point-in-time stock screening | P0 | Now | [#251](https://github.com/OpenByteInc/QuantDinger/issues/251) |
| Portfolio strategies and scheduled rebalancing | P0 | Now | [#252](https://github.com/OpenByteInc/QuantDinger/issues/252) |
| Pairs and spread trading foundation | P0 | Now | [#253](https://github.com/OpenByteInc/QuantDinger/issues/253) |
| Multi-leg order coordination and recovery | P0 | Next | [#254](https://github.com/OpenByteInc/QuantDinger/issues/254) |
| Pair-level positions, PnL, and analytics | P1 | Next | [#255](https://github.com/OpenByteInc/QuantDinger/issues/255) |
| Auditable AI entry filters | P1 | Done | [#263](https://github.com/OpenByteInc/QuantDinger/issues/263) |
| External signal integrations | P1 | Next | [#256](https://github.com/OpenByteInc/QuantDinger/issues/256) |

## Future architecture RFCs

| Workstream | Stage | Target | Design document |
| --- | --- | --- | --- |
| Hyperscale event-driven trading architecture for 20,000 users and 100,000 active strategies | RFC | V6 | [V6 hyperscale architecture plan](docs/architecture/V6_HYPERSCALE_ARCHITECTURE_PLAN.md) |

## How to contribute

Only scoped work marked **Ready** and **help wanted** should be implemented
without another design round. Roadmap epics must be split before implementation.

1. Read the relevant epic and linked architecture documentation.
2. Comment with the specific task you want to own and a short implementation
   plan.
3. Wait for a maintainer to confirm the scope and assign the issue.
4. Post a draft pull request or progress update within seven days of assignment.
5. Keep the pull request focused and link it to the issue.

An inactive claim may be released so another contributor can continue the work.
Read [CONTRIBUTING.md](CONTRIBUTING.md) for repository rules and validation
requirements.

## Proposing roadmap work

Use [GitHub Discussions](https://github.com/OpenByteInc/QuantDinger/discussions)
for broad product ideas, new markets, new asset classes, and architectural
alternatives. Once the problem and boundaries are understood, maintainers can
promote the proposal to a scoped roadmap issue.

Use a regular feature request for a bounded improvement that does not require an
architecture discussion. Do not include credentials, private financial records,
or exploitable security details in public issues.
