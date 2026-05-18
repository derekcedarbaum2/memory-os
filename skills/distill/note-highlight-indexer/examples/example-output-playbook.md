---
title: Working With Coding Agents — Spec, Judgment, Skills That Don't Transfer
type: reference
status: active
classification: internal
created: 2026-05-04
updated: 2026-05-04
author: "<your-name>"
tags: [tech, ai, coding-agents, claude-code, pair-programming, judgment]
---

# Working With Coding Agents

Operational rules for getting useful output from coding agents (Claude Code, Cursor, etc.) — and the senior engineering judgment skills that don't transfer to the agent and remain the human's job.

## The articulation rule

The agent only knows what you say out loud. Things you've internalized as obvious — abstraction level, risk tolerance, kluge-vs-permanent, sequencing — must be specified explicitly or the agent guesses, usually badly.

> "If you only describe the what and not the how, expect to be underwhelmed." [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

**Rule:** every non-trivial coding-agent prompt includes both *what* and *how I'm thinking about it*. The "how" is the part that's hard to make explicit — and the part that determines whether the output is useful.

## Spec scorecard — score the prompt before sending

Rate the brief 0–3 on each. Total below 10/15 → rewrite before sending.

| Dimension | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| **What** — the change to make | unclear | named feature | named feature + acceptance criteria | + non-goals |
| **How** — the mental model behind it | absent | one sentence | a few sentences of reasoning | full mental model the agent can pattern-match against |
| **Abstraction level** | unspecified | implied by context | named (function / module / system) | named + example of the right level |
| **Risk profile / blast radius** | unspecified | implied | named (loud refactor / quiet patch / spike) | + which files/systems are off-limits |
| **Permanence** | unspecified | implied | named (production / kluge / spike) | + the trigger that retires the kluge |

[Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

## Fillable template — agent brief

```
WHAT: <feature / change / bug to fix>
HOW (mental model): <how I'm thinking about the problem — the reasoning, not just the goal>
ABSTRACTION LEVEL: <single function | module | system | cross-cutting>
RISK PROFILE: <loud refactor | quiet contained patch | exploratory spike>
PERMANENCE: <production-grade | temporary kluge until <date / condition> | throwaway spike>
NON-GOALS: <what NOT to touch / change / abstract>
```

If you can't fill three of these, the brief isn't ready. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

## Decision triggers

- IF agent output feels underwhelming or generic → check whether you specified the *how*, not just the *what*. Rewrite the brief and re-run before debugging the output. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]
- IF you want a quick hack → say "temporary kluge, will be replaced when X" *explicitly*. The agent will otherwise default to production-grade abstractions. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]
- IF you want a quiet contained change → say "minimal blast radius, do not refactor surrounding code." Agents trend toward gardening. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]
- IF the agent suggests a clever pattern → ask "would the next reader understand this?" before merging. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

## Anti-pattern detectors

Boolean checks. Any TRUE → stop and fix the prompt or the review process.

- [ ] Letting the agent guess abstraction level (you didn't specify it)
- [ ] Letting the agent guess risk tolerance (you didn't specify blast radius)
- [ ] Letting the agent guess permanence (you didn't flag it as a kluge)
- [ ] Treating green tests as evidence the model is correct (the test may be wrong)
- [ ] Merging clever code without asking who else reads this
- [ ] Typing code yourself when the brief would have been faster — "When I spend time actually typing code these days with my own fingers, it feels like a waste of my time" [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

## The five judgment skills agents don't replace

These remain the human's job. The agent does mechanical expression; you do the judgment. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

| Skill | What it catches | Pre-merge question |
|-------|-----------------|---------------------|
| **Blast radius** | Which changes are safe to make loudly vs. should be quiet and contained | "Who else does this touch? What downstream effects?" |
| **Sequencing** | A technically correct change that's still wrong because the system or team isn't ready | "Is the system / team ready for this *now*?" |
| **Reversibility** | Locking the system into a path that's hard to back out of | "If wrong, can we undo this cheaply?" |
| **Social cost** | Clever-but-confusing solutions that confuse more people than they help | "Will the next reader understand this without you in the room?" |
| **Allergy to false confidence** | Tests green but the model is wrong | "Are these tests actually exercising the thing I think they are?" |

## The pair-programming side-effect

The act of articulating the brief slows you down enough to notice when your own instincts are off. Treat the brief as a debugging tool for *your thinking*, not just instruction for the agent. Same effect as good human pair programming. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

**Trigger:** if writing the brief surfaces a question you can't answer, the implementation is premature regardless of what the agent could produce.

## Value-shift implication

At senior experience level, the core value offering is judgment, tradeoffs, and intent — not typing code. Agents clear space for that by absorbing the mechanical expression. The PM / architect / staff-engineer move is to spend marginal time on the *brief* and the *review*, not on the keystrokes between them. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]

For client-billed work, this is sharper: typing code at a senior hourly rate is value destruction when a brief + review would produce the same output faster. [Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]
