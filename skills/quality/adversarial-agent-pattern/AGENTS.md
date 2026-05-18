# AGENTS.md — `adversarial-agent-pattern`

Operating protocol for agents using this repo to design or install adversarial-trio skills.

## What this repo provides

Meta-pattern documentation for the adversarial-agent skill family: context-isolated agents with competing incentives + arbitration as the structural anti-sycophancy mechanism. Covers four published / personal skills (`qa-loop`, `prd-review`, `pressure-test`, `sales-qa`) and provides a template for designing new family members on new problems.

## Read order

1. `README.md` — the family overview, the five design rules, when to use which member, the failure modes the family addresses.
2. `template/new-adversarial-skill.template.md` — drop-in SKILL.md template for designing a new family member, with prompt skeletons for each role.
3. `examples/qa-loop-design-notes.md` — annotated breakdown of `qa-loop`'s design choices.
4. `examples/prd-review-design-notes.md` — same for `prd-review`.
5. `examples/pressure-test-design-notes.md` — same for `pressure-test`.

## Trust boundary

- The five design rules in `README.md` are load-bearing. **Do not weaken them when designing a new family member.** Specifically:
  - Context isolation cannot be approximated by "act as Role A, then Role B" in one context.
  - Incentive structures must be asymmetric (penalty for wrong challenges > reward for right ones).
  - The Referee must not see the skill instructions or know it's part of a "technique."
  - Rewrite/output must touch *only* what survived arbitration.
- This is a meta-pattern repo, not executable code. The actual skills are separate (`qa-loop` is published; the others are personal).

## Common tasks

### Designing a new family member

1. Read `README.md` (the five rules) and the design notes for the closest existing sibling.
2. Copy `template/new-adversarial-skill.template.md` to `~/.claude/skills/<your-skill-name>/SKILL.md`.
3. Fill in:
   - Question the skill answers.
   - Roles (3–5 typically). For each role, write the incentive structure (NOT an opinion).
   - Phase prompts for each role.
   - Referee prompt (told ground truth exists; doesn't know it's part of a technique).
   - Output constraint (rewrite only what survived).
4. Test on three inputs:
   - A clearly-bad input — does it catch issues?
   - A clearly-good input — does it stop intervening?
   - An input the model has a strong default opinion on — does the structure overcome the default?
5. If test (3) fails, the incentive structure is too weak. Re-tune the asymmetry.

### Installing `qa-loop`

`qa-loop` is the only family member published as a standalone repo: https://github.com/derekcedarbaum2/qa-loop. See its install instructions there.

`prd-review`, `pressure-test`, `sales-qa` are currently personal skills. Code on request.

## Adaptation checklist when designing a new sibling

- [ ] Question has multiple legitimately-arguable answers (not "what is 2+2?").
- [ ] Role count is 3–5 (more = referee can't synthesize; less = no real adversarial coverage).
- [ ] At least one role uses asymmetric incentive (penalty for wrong challenge > reward for right one).
- [ ] Each phase prompt instructs the agent to produce structured output (parseable by orchestrator).
- [ ] Orchestrator strips reasoning / hedges between handoffs.
- [ ] Referee prompt does not mention the skill, the technique, or the existence of other phases.
- [ ] Final output explicitly limited to "what the Referee validated" (no "while we're here" cleanup).

## Related

- [`qa-loop`](https://github.com/derekcedarbaum2/qa-loop) — the published family member.
- The pattern was inspired by Karpathy's observation that LLMs are competent at arguing any direction; structural assignment of direction (rather than asking for opinions) is the anti-sycophancy mechanism.
