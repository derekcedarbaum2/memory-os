---
name: [skill-name]
description: [one-line description with trigger phrases]
version: 0.1.0
allowed-tools: [Read, Write, Edit, Glob, Grep, AskUserQuestion, Agent]
model: opus
---

# [Skill Name] — Adversarial [Question]

[2–3 sentences describing what this skill does and what question it answers.]

## When to Use This Skill

Activate when user:
- Says "[trigger phrase 1]"
- Says "[trigger phrase 2]"
- Wants to [common scenario]

Do NOT activate for:
- [Excluded scenario] (use `[other-skill]` instead)
- [Excluded scenario]

## Core Philosophy

> **[The one-line thesis of the skill — what it believes that other approaches miss.]**

[Brief explanation of why this skill exists — what failure mode in single-agent review it addresses.]

### Why Context Isolation Matters

Each agent runs as a **separate subagent with a walled-off context**. This is critical because:

- [Specific reason for this skill — e.g., "the [Role A] agent never sees the [Role B] agent's reasoning, so it can't unconsciously defer to it."]
- [Another specific reason]

The orchestrator (main context) controls information flow between agents, stripping meta-signals at each handoff.

---

## Roles

| Agent | Incentive | Bias Exploited | Output |
|-------|-----------|----------------|--------|
| **[Role A]** | [scoring rule] | [bias the incentive exploits] | [what it produces] |
| **[Role B]** | [scoring rule] | [bias the incentive exploits] | [what it produces] |
| **[Role C]** (optional) | [scoring rule] | [bias the incentive exploits] | [what it produces] |
| **Referee** | +1 correct ruling, -1 incorrect (told ground truth exists) | Wants to please → maximizes accuracy | Final verdict |

---

## Workflow

1. **Detect input type** — [the artifact / question type the skill handles]
2. **Load context** — [reference files needed]
3. **Phase 1: [Role A]** *(isolated subagent)* — [what it does]
4. **Data Strip** *(orchestrator)* — Extract structured output from Phase 1, remove reasoning / confidence signals
5. **Phase 2: [Role B]** *(isolated subagent)* — [what it does], given only the structured output of Phase 1
6. **Data Format** *(orchestrator)* — Prepare both phases' outputs for arbitration
7. **Phase 3: Referee** *(isolated subagent)* — Arbitrates each disputed item
8. **Final Output** — [Rewrite, report, score, etc. — touching only what survived arbitration]

---

## Phase 1 prompt: [Role A]

```
You are [role description].

Your task: [what they're scored on].

Scoring:
- [scoring rule with specific values]

Output format:
- [structured format the orchestrator can parse]

DO NOT:
- [things that would compromise context isolation]
- [hedges, self-censorship, etc.]
```

## Phase 2 prompt: [Role B]

```
You are [role description].

You will receive: [structured output from Phase 1, with reasoning stripped]

Your task: [what they're scored on, often "challenge each item"].

Scoring:
- [scoring rule, often asymmetric — penalty for wrong disproofs/challenges larger than reward for correct ones]

Output format:
- [structured format the orchestrator can parse]
```

## Phase 3 prompt: Referee

```
You are an impartial judge ruling on a dispute.

You will see [structured outputs from Phase 1 and Phase 2 — no reasoning, no hedges].

For each disputed item, rule:
- VALIDATE: the issue/concern is real
- REJECT: the issue/concern was successfully challenged
- UNDETERMINED: cannot rule on available evidence

You are scored on accuracy. Ground truth exists and your rulings will be checked.

DO NOT:
- Try to find a middle ground
- Default to "validate" or "reject"
- Add new concerns the prior phases didn't raise
```

---

## Output

[Describe the final output format — e.g., "rewritten artifact with only validated issues fixed", "structured report with pass/fail per category", "list of what survived adversarial pressure".]

The final action **must touch only what survived arbitration**. Do not perform "while we're here" cleanup or add the Referee's editorial preferences.

---

## Anti-patterns (avoid these)

- **Letting agents see each other's context.** Defeats the entire isolation rule.
- **Asking agents for opinions instead of assigning incentives.** Reverts to default sycophancy.
- **Symmetric incentives across roles.** Asymmetry is the lever — the Disprover-style agent must have a heavier penalty for wrong challenges than reward for right ones.
- **Skipping the Referee.** Without arbitration, you have multiple critics arguing past each other. The Referee is what makes the family converge instead of just diverge.
- **Telling the Referee it's part of a technique.** It performs better when it believes it's adjudicating a real dispute on the merits.
- **Rewriting beyond what was validated.** "While we're here, let me also fix..." erodes trust in the loop and reintroduces sycophancy through the back door.
