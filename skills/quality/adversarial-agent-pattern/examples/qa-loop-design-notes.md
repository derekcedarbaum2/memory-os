# `/qa-loop` — Design Notes

The first member of the family. Generic prose-quality loop for PM artifacts (PRDs, hypotheses, interview syntheses, stakeholder updates). Published as a standalone repo: https://github.com/derekcedarbaum2/qa-loop

## The question it answers

> "Is this artifact good enough to send?"

Specifically: does it have real issues — gaps in argument, weak claims, contradictions, missing context — or is it ready?

The naive version of this is "ask Claude to review it." That fails because:
- A single review pass either over-flags (every paragraph gets a comment) or under-flags (defaults to "looks good!").
- The reviewer has no skin in the game on false positives, so flagging is safe and cheap.
- A single context conflates finding issues, defending issues, and ruling on issues — three different cognitive stances that contaminate each other.

## The three roles

| Agent | Incentive | What this produces |
|---|---|---|
| **Finder** | +1 low / +5 medium / +10 critical issue. No false-positive penalty. | Superset of all possible issues. Aggressive. |
| **Disprover** | +score for valid disproof, **−2× score** for wrong disproof. | Pruned subset. Cautious. |
| **Referee** | +1 correct ruling, −1 incorrect (told ground truth exists). | Final truth. |

The asymmetric scoring on the Disprover is the key. Without it, the Disprover would also over-find (in this case, over-disprove), and the system would converge on "everything is fine." The 2× penalty makes the Disprover only fight battles it can actually win.

## The information flow

```
Artifact ──► Finder ──► raw issues with reasoning
                       │
                       ▼ orchestrator strips reasoning, keeps issues
                       │
                       ▼
            Disprover (sees only the issue list)
                       │
                       ▼ orchestrator merges Finder claims + Disprover challenges
                       │
                       ▼
            Referee (sees only the disputes, no reasoning, no skill context)
                       │
                       ▼
            Validated issues only
                       │
                       ▼
            Rewriter (orchestrator) — fixes ONLY validated issues
                       │
                       ▼
            Polished artifact + score
```

## Specific design choices and why

**Why context-isolated subagents and not multiple turns in one context?** A single context with three "roles" produces collapsed output — the model can't actually forget what it just argued. The cost of separate subagents is tokens; the value is real disagreement.

**Why strip reasoning at handoffs?** The Disprover seeing the Finder's reasoning ("I think this is a critical issue because…") biases its challenge. With only the structured issue list, the Disprover evaluates the *claim*, not the rhetoric.

**Why does the Referee not know it's part of a "loop"?** The Referee told it's part of a quality system tries to be helpful by validating issues to "complete the loop." The Referee told it's adjudicating a dispute on the merits ranks correctness above process completion.

**Why "rewrite only what survives" instead of "rewrite based on validated issues"?** Subtle but important. "Based on validated issues" leaves room for the rewriter to add improvements it noticed along the way. "Only what survives" means the artifact's untouched paragraphs stay verbatim. The discipline is what prevents the loop from becoming a general-purpose editor.

## Failure modes observed

- **Sycophantic Finder:** rare with this scoring, but happens when the artifact is by a "high-status" author and the model softens. The fix is incentive-only framing — never tell the model whose work it is.
- **Over-aggressive Disprover:** happens when the Finder produces vague issues ("this could be tighter"). Fix: require the Finder to produce specific, location-anchored issues.
- **Hedging Referee:** the Referee defaults to "underdetermined" when it doesn't want to commit. Fix: require explicit verdict per item; "underdetermined" must include a specific reason.

## Implementation feasibility mode

For PRDs and plan/roadmap artifacts, the Finder runs in **implementation feasibility mode** — evaluating buildability, sequencing realism, hidden dependencies from a skeptical senior engineer's perspective. The aggressive internal critique is stripped for the final output (so the rewritten PRD doesn't read as defensive) but preserved as an optional "critique log" the user can request.

This mode change is just a prompt swap on the Finder. The rest of the loop is identical.
