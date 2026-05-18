# `/prd-review` — Design Notes

The stakeholder-readiness sibling. Where `qa-loop` asks "is this prose good?", `prd-review` asks "would my actual approvers sign off?"

## The question it answers

> "Is this PRD ready for the formal approval meeting, or will it get shredded?"

In any organization with a PRD-approval process, sign-off authority is split across roles — typically BD, Engineering, and Product leadership. Each has different criteria. A PRD that's sound on Product strategy can fail on Engineering buildability or on BD market sizing. You only learn this in the meeting, where the cost of a "no" is high.

`/prd-review` simulates the three reviews in parallel before the meeting, then arbitrates.

## The three roles

| Agent | Mandate | Scoring |
|---|---|---|
| **BD Reviewer** | Reviews from business / commercial perspective: market size, revenue model, competitive positioning, customer commitment risk | +1 per concern that holds; −2 per concern that doesn't hold under scrutiny |
| **Engineering Reviewer** | Reviews from buildability perspective: scope realism, sequencing, hidden dependencies, technical feasibility, integration risk | Same |
| **Product Reviewer** | Reviews from product strategy perspective: alignment with roadmap, user value, JTBD coverage, success metrics | Same |
| **Referee** | Arbitrates conflicts and produces final pass/fail per category | +1 correct ruling, −1 incorrect |

The scoring asymmetry (−2 for unsubstantiated concerns, +1 for substantiated ones) is identical in shape to `qa-loop`'s Disprover, but applied at the agent level rather than between agents. Each role agent is its own Disprover-of-itself. This works because each role has a natural over-flagging tendency in this context — they want to be seen catching things — and the asymmetric penalty pushes them toward only raising substantive concerns.

## How this differs from `qa-loop`

| Dimension | `qa-loop` | `prd-review` |
|---|---|---|
| Agents | 1 generic Finder + 1 Disprover + Referee | 3 role-specialized reviewers + Referee |
| Question | "Is this prose good?" | "Would each approver sign off?" |
| Output | Polished artifact | Pass/fail per approver category + structured concerns |
| Rewrite step? | Yes | No — output is a report; PM rewrites with clear targets |
| Composes with | `pressure-test`, `sales-qa` | `qa-loop` (run prose pass first), `pressure-test` (run on directional questions) |

The big design call: **no rewrite step**. `prd-review` is diagnostic, not prescriptive. The PM closes the gaps; the skill doesn't. This is intentional — a skill that rewrites a PRD without the PM's judgment introduces drift that a real approval process would catch on the next pass anyway.

## Specific design choices and why

**Why three reviewers and not two or four?** The number tracks the real approval committee. Three is the natural count for "BD / Eng / Product" structure. Skills built for orgs with different approval shapes (e.g., "Legal / Compliance / Engineering / Product / GTM") should add roles to match. The Referee scales to N; the orchestrator complexity does not.

**Why role-specialized prompts and not just "review as BD"?** Role identity isn't enough — you need the role's *evaluation criteria* loaded explicitly. The BD reviewer prompt includes: market sizing methodology preferences, revenue model framing, customer commitment language, competitive positioning expectations. Without these, "BD review" is a vague aesthetic.

**Why no rewrite step?** Two reasons: (1) the PM is the one accountable for the final PRD, so the skill shouldn't pre-empt their judgment on how to address concerns; (2) different concerns warrant different responses (some are wrong, some are partial, some require new analysis), and a rewrite skill can't tell which is which.

**Why the Engineering reviewer includes implementation feasibility?** This is the same mode `qa-loop` has — `prd-review` inherits it directly. PRDs that look strategically sound but are operationally fantasy are the most common failure mode at the Engineering gate.

## Failure modes observed

- **Generic concerns from role agents:** "the market sizing is unclear" without specific call-outs. Fix: require each concern to anchor to a specific PRD section + a specific evidence ask.
- **Roles arguing past each other:** BD raises a market concern, Engineering raises a feasibility concern, neither addresses the other. The Referee is what bridges this — its job includes identifying when concerns from different roles compound (e.g., the market is small AND the build is expensive, so the joint case is much worse than either alone).
- **Sycophantic verdicts when the PRD is by the user themselves:** mitigated by the same incentive-only framing as `qa-loop`. Never tell the model whose PRD it is.

## Pre-flight context loading

Before spawning agents, the skill reads:
1. `~/.claude/reference/prd-approval-criteria.md` — the org's actual approval criteria, roles, and process. This is the document that turns a generic "BD review" into "BD review *as this org practices it*."
2. The PRD itself (full text).
3. Optionally: `~/.claude/reference/glossary.md` and `~/.claude/reference/company-context.md` if domain terms are used.

The org-specific criteria file is the single biggest determinant of output quality. Without it, the skill produces generic concerns; with it, the skill catches the specific shape of objections that approvers actually raise.
