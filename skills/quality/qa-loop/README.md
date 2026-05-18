# QA Loop

**Adversarial trio quality refinement for written artifacts.** Three context-isolated subagents with competing economic incentives find every issue, challenge every issue, and arbitrate — then rewrite only what survives.

Built for product managers, but the architecture works on any prose where you want to find real issues without false-positive inflation: PRDs, hypotheses, stakeholder updates, interview synthesis, plans, roadmaps.

---

## The pattern

Most quality processes either miss issues (too lenient) or flag false positives (too aggressive). This skill uses three subagents with **competing economic incentives** to converge on truth:

| Agent | Incentive | Bias exploited | Output |
|-------|-----------|----------------|--------|
| **Finder** | +1 low / +5 medium / +10 critical issue found | Wants to please → finds *everything* | Superset of all possible issues |
| **Disprover** | +score for valid disproof, **−2× score for wrong disproof** | Cautious — only challenges issues it's confident are wrong | Pruned subset |
| **Referee** | +1 correct ruling, −1 incorrect (told ground truth exists) | Maximizes accuracy | Final truth |

Each agent runs in its own subagent with **no visibility into the others' reasoning, confidence signals, or the overall technique.** That isolation is what makes the pattern work — agents who knew they were one of three would game the protocol.

For PRDs and Plans/Roadmaps, the Finder also runs in **implementation feasibility mode** — evaluating buildability, sequencing realism, and hidden dependencies from the perspective of a skeptical senior engineer.

---

## Why it works

Three things happen at once that don't happen in single-agent QA:

1. **Recall before precision.** Finder gets a fat tail of candidate issues, including some false positives. That's fine — Disprover catches them.
2. **Asymmetric loss for wrong disproofs.** Disprover doesn't kill issues it's *not sure* are wrong — the −2× penalty makes that bad EV. So real issues survive even when they look weak.
3. **Arbitration.** Referee resolves the remaining disputes with no skin in the original critique. Final ruling stops oscillation.

The headline result: **rewrites only what's real**, doesn't soften voice in the name of "polish," and doesn't bury the user under noise.

---

## Install

### Claude Code

```bash
mkdir -p ~/.claude/skills/qa-loop
cp SKILL.md ~/.claude/skills/qa-loop/SKILL.md
```

That's it. Invoke with `/qa-loop` or `/qa-loop /path/to/artifact.md`.

### Codex CLI

The skill is a single `SKILL.md`. Codex doesn't have a skill loader, so use it as a prompt template:

```bash
mkdir -p ~/.codex/prompts
cp SKILL.md ~/.codex/prompts/qa-loop.md
```

Invoke by pasting the file contents into a Codex session, or wrap in a shell alias. The agent-orchestration logic depends on Codex's subagent or tool-use surface — read the SKILL.md and adapt the Agent invocations to your version.

---

## Usage

```
/qa-loop /path/to/artifact.md     # full file path
/qa-loop                          # operates on the last generated artifact in context
```

**Pairs with:** [`sense-of-style`](https://github.com/derekcedarbaum2/sense-of-style) — qa-loop fixes the *argument*; sense-of-style fixes the *prose*. Run them in sequence on high-stakes writing.

---

## Artifact types supported

Out of the box, the skill scores against type-specific criteria for:

- **PRDs** — JTBD framing, success metrics, scope clarity, edge cases, kill criteria
- **Plans / Roadmaps** — sequencing realism, dependency exposure, milestone definition
- **Hypotheses** — assumption mapping, falsifiability, leading indicators
- **Interview Synthesis** — pattern density, JTBD extraction, opportunity sizing
- **Stakeholder Updates** — exec-readability, decision asks, risk surface
- **Generic** — falls back to a baseline prose criteria set

Easy to extend: add a new type with its own scoring rubric in the SKILL.md.

---

## License

MIT. Fork it. The pattern is more valuable than any one implementation — if you find a better incentive structure, ship it.
