# Adversarial Agent Pattern

> **Want to install the whole 12-repo ecosystem?** Paste [this prompt](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/INSTALL-PROMPT.md) into your Claude Code or Codex session — it interviews you, installs in phases, runs smoke tests, and pauses for confirmation between phases. Or browse the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) first.


**The trick that gets an AI to stop telling you what you want to hear.**

> **New to Claude Code?** [Claude Code](https://docs.anthropic.com/claude/code) is Anthropic's command-line AI agent. This repo documents a *pattern* — a structural design that several skills in this ecosystem (qa-loop, prd-review, pressure-test, sales-qa) are built on. See the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) — full system overview + onboarding sequence — or [`claude-code-setup`](https://github.com/derekcedarbaum2/claude-code-setup) for the umbrella reference doc. Vocabulary used here (skill, subagent, context isolation, etc.) is defined in the [glossary](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/GLOSSARY.md).

---

## The problem

Ask an AI: "Is this strategy a good idea?"

It'll tell you yes, here's why. Strong, articulate, well-organized. You feel reviewed.

Now ask the same AI: "Argue *against* this strategy. What's wrong with it?"

It'll tell you no, here's why. Equally strong. Equally articulate. Equally convincing.

That's not the AI lying. It's the AI doing exactly what you asked — building the strongest case for whatever direction you pointed it at. Karpathy called this out: LLMs are extraordinarily competent advocates for *any* direction you assign them. The flip side is they're terrible neutral judges, because their default mode is "what does this person want to hear?"

That's the sycophancy problem. And better prompting doesn't fix it — you're still asking one model for an opinion, and one model still wants to please you.

The fix is structural. Don't ask one model what it thinks. Run *multiple* models that:

1. **Can't see each other's reasoning.** Each runs in its own conversation window with no knowledge of the others.
2. **Have incentive structures, not opinions.** One is told "find every issue" (rewarded for over-flagging). Another is told "challenge issues" (rewarded for valid challenges, punished twice as hard for wrong ones). They can't both be sycophants — their assignments are at right angles.
3. **Get arbitrated by a third agent** that's told its rulings will be checked against verified correct answers. (They won't be — but the framing makes accuracy the dominant strategy.)

What survives the arbitration is what's actually true. Not what the model wanted to say.

This repo documents that pattern, why it works, and the four skills built on it.

---

## The four skills in the family

I built each of these as a separate Claude Code skill. They share a deep design but apply it to different problems:

| Skill | Problem | Roles | Output |
|---|---|---|---|
| [**`qa-loop`**](https://github.com/derekcedarbaum2/qa-loop) | "Is this artifact good?" | Finder · Disprover · Referee | Polished artifact (rewrites only validated issues) |
| **`prd-review`** | "Would my approvers sign off on this PRD?" | BD · Engineering · Product · Referee | Approval-readiness report (pass/fail per approver) |
| **`pressure-test`** | "Is this position defensible?" | For · Against · Null · Alternative (× lens) · Referee | What survived adversarial pressure, what crumbled |
| **`sales-qa`** | "Would the buyer reply / take the meeting / sign?" | 10-criterion scoring agents · rewriter | Iteratively rewritten artifact, ≥9/10 on every criterion |

Three of these compose at runtime — `qa-loop` for prose quality, `prd-review` for stakeholder readiness, `pressure-test` for direction validity. `sales-qa` is the recursive-rewrite cousin used when the artifact's job is to persuade a buyer.

---

## The shared design DNA

Every member of the family enforces the same five rules. These are the design rules — not just patterns, but constraints that determine whether the output can be trusted.

### Rule 1 — Context isolation

Each agent runs as a **separate subagent with a walled-off context.** The Finder agent never sees the Disprover's reasoning. The Disprover never sees the Finder's confidence signals — only the structured issue list. The Referee never sees the skill instructions or knows it's part of a "technique."

Why: shared context produces self-consistency pressure. An agent arguing "For" can't unconsciously soften its case if it's also seen the "Against" agent's argument. With isolated contexts, every agent does its job under no pressure to converge.

The orchestrator (the main context running the skill) controls information flow between agents and **strips meta-signals at each handoff** — confidence words, hedges, references to the other agents.

### Rule 2 — Competing incentives, not opinions

Agents are given **incentive structures** rather than opinions to hold. Examples from `qa-loop`:

| Agent | Incentive | Bias the incentive exploits |
|---|---|---|
| Finder | +1 low / +5 medium / +10 critical issue found | Wants to please → finds everything, including marginal issues |
| Disprover | +score for valid disproof, **−2× score for wrong disproof** | Wants to please → aggressively challenges, but cautious about being wrong |
| Referee | +1 correct ruling, −1 incorrect (told ground truth exists and will be checked) | Wants to please → maximizes accuracy |

The economic asymmetry is the lever. The Disprover is rewarded for disproving issues but punished harder for wrong disproofs — so it only fights battles it can win. The Finder over-finds because there's no penalty for false positives. The Referee converges on truth because that's what scores best.

You don't tell agents to argue or defend. You tell them what they're being scored on, and the scoring shape determines the behavior.

### Rule 3 — Direction assignment, not opinion query

This is the core anti-sycophancy mechanism, sharpest in `pressure-test`:

> Agents are **told** which direction to argue, never **asked** what they think.

Asking "what do you think of this strategy?" gives you whatever framing the model thinks you want. Telling one agent "argue strongly *for* this strategy" and another "argue strongly *against*," then arbitrating, gives you both cases at full strength. The model is just as eager to please in both directions — and that eagerness is now load-bearing.

`pressure-test` extends this with **persona lenses** (CRO, Legal, Engineering, End User, Competitor). The Direction × Lens combo breaks default framings: "argue *for* this acquisition from Legal's perspective AND *against* it from Legal's perspective" forces the model out of "Legal would obviously say X."

### Rule 4 — Arbitration by a structurally-different agent

The Referee isn't another opinion. It's a different role with different rules:

- It's told ground truth exists and its rulings will be checked. (It doesn't actually get checked, but the framing changes its behavior.)
- It doesn't see the skill instructions. It doesn't know it's part of a quality loop. It thinks it's adjudicating a dispute on the merits.
- It sees only the structured outputs of the prior agents — not their reasoning, not their hedges.

This is why the family does not just "run multiple critics and average." Averaging is the wrong aggregation; arbitration is the right one.

### Rule 5 — Rewrite only what survives

The output is constrained by what made it through arbitration:

- `qa-loop` rewrites *only* the issues the Referee validated. Everything else stays untouched. No "while we're here" cleanup.
- `prd-review` produces a pass/fail per approver category, with reasons. The rewrite happens later, by you, with clear targets.
- `pressure-test` reports what survived, what crumbled, what's underdetermined. It doesn't pick a winner — it tells you where the real fault lines are.
- `sales-qa` rewrites until every scored dimension hits ≥9/10. The recursion is the structure.

The discipline is *minimum intervention*. Don't change what wasn't proven wrong.

---

## When to use which

| Situation | Skill | Why |
|---|---|---|
| Polish a PRD, hypothesis, interview synthesis, stakeholder update | `qa-loop` | Generic prose quality with anti-false-positive guard |
| Pre-screen a PRD before formal approval | `prd-review` | Multi-stakeholder lens — catches BD / Eng / Product objections before humans see it |
| Validate a strategic decision before committing | `pressure-test` | Direction × Lens stress test — surfaces what would crumble under real scrutiny |
| Sharpen a pitch deck, proposal, cold email, one-pager | `sales-qa` | Buyer-perspective scoring — measures whether they'd actually act |
| First-draft generation of any of the above | **None of these** | Use a generation skill first; these are review/refine tools |

A common stack: write the artifact → `qa-loop` for prose → `pressure-test` for directional defensibility → `sales-qa` if buyer-facing → `prd-review` if it's a PRD heading to approvers. Each pass takes ~5–15 minutes of agent runtime; the compounding effect is real.

---

## Designing your own member of the family

Here's the template for spinning up a new adversarial-trio skill on a new problem:

### Step 1 — Identify the question

The question must have a structure where multiple legitimate answers can be steel-manned. Bad fit: "what's 2+2?" Good fit: "is this PRD ready?", "should we acquire X?", "is this market wedge defensible?"

### Step 2 — Identify the role axis

What perspectives matter for *this* question? Examples:

- For PRD review: BD / Engineering / Product (matching your real approval committee)
- For acquisition decision: Legal / Finance / Strategy / Cultural fit
- For technical architecture choice: Senior IC / Eng manager / Ops / Security / Cost
- For pricing decision: CRO / Customer / Competitor / Internal CFO

The number of roles is usually 3–5. More than 5 and the Referee can't synthesize cleanly; fewer than 3 and you don't have real adversarial coverage.

### Step 3 — Define incentives, not opinions

For each role, write the scoring rule. Examples:

- **Finder-style** ("find all issues"): "+1 per minor issue, +5 medium, +10 critical. Penalty: 0 for false positives." → encourages over-finding.
- **Disprover-style** ("challenge findings"): "+score for valid disproof, −2× score for wrong disproof." → encourages cautious challenge.
- **Lens-style** ("assess from this role's POV"): "+1 per concern raised that holds against the artifact's claims; −2 per concern that doesn't hold under scrutiny." → encourages substantive role-perspective concerns.
- **Direction-style** ("argue for / against"): "Score = strength of the case built. Aim for the strongest possible argument; don't hedge."

The shape of the scoring rule shapes the behavior. Iterate.

### Step 4 — Write the Referee

The Referee:
- Receives only structured outputs from the role agents (no reasoning, no hedges, no confidence signals).
- Is told ground truth exists and its rulings will be checked.
- Does not see the skill instructions.
- Outputs a structured verdict per disputed item (validate / reject / underdetermined).

### Step 5 — Constrain the rewrite

The skill's final action — rewrite, score, report, etc. — must touch only what survived arbitration. If your skill is a quality loop, write down explicitly: "Fix only what the Referee validated; leave all other text untouched." If it's a report, write it from the Referee's structured verdict.

### Step 6 — Test by attacking it

Run the skill on:
1. A clearly-bad input. Does it catch the issues?
2. A clearly-good input. Does it stop intervening (i.e., not invent issues)?
3. An input the model has a strong default opinion on. Does the structure overcome the default?

If (3) fails, your incentive structure is too weak. Re-tune.

---

## What's in this repo

```
adversarial-agent-pattern/
├── README.md
├── LICENSE
├── template/
│   └── new-adversarial-skill.template.md  ← Drop-in template for designing a new family member
└── examples/
    ├── qa-loop-design-notes.md            ← Annotated breakdown of qa-loop's design choices
    ├── prd-review-design-notes.md         ← Annotated breakdown of prd-review's design choices
    ├── pressure-test-design-notes.md      ← Annotated breakdown of pressure-test's design choices
    └── applied-claim-test-rowboat.md      ← Using the 5 rules as a critique tool against a third-party category claim
```

The skills themselves:
- [`qa-loop`](https://github.com/derekcedarbaum2/qa-loop) — published as a standalone repo
- `prd-review`, `pressure-test`, `sales-qa` — currently personal skills; design notes here, full skill code on request

---

## Why the family beats single-agent reviewers

A single LLM-as-reviewer has three failure modes:

1. **False positives** — flags issues that aren't real, because finding things is what reviewers do.
2. **False negatives** — misses issues that contradict its default framing.
3. **Sycophancy drift** — gradually softens its critique as the conversation continues, especially after pushback.

The family addresses each:

1. False positives → Disprover prunes them.
2. False negatives → Direction assignment forces the model to argue framings it wouldn't naturally take.
3. Sycophancy drift → Context isolation eliminates conversation history; each agent is a fresh context.

The compounding effect is significant: across ~6 months of running this family on real-world knowledge-work artifacts (originally PM artifacts — PRDs, hypotheses, plans, interview syntheses — but the same shape works on engineering RFCs, founder pitches, research summaries, legal memos, anything where finding real issues matters more than feeling reviewed), the false-positive rate dropped from "every review surfaces 2–3 fake issues" to roughly zero, while real-issue catch rate stayed high. The arbitration step is what makes it sharp instead of just noisy.

---

## What this is not

- **Not a prompt template.** This is a structural pattern that requires multiple subagent calls and orchestrator logic. A single prompt asking one model to "act as Finder, then Disprover, then Referee" produces collapsed-context output and doesn't work.
- **Not a replacement for human review.** It's a pre-screening that surfaces what humans should focus on. The final decision stays with you.
- **Not zero-cost.** A `qa-loop` run is 4 subagent invocations (Finder, Disprover, Referee, plus orchestrator). Run it on artifacts that warrant the cost, not on every typo.

---

## License

MIT.
