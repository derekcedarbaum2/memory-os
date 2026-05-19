---
name: skill-improve
description: "Close the use → critique → patch loop on any Claude Code skill. Given a skill name and a recent output (or fresh test run), scores the output against the skill's eval bundle, calls /skill-critique if below threshold, proposes a single-variable SKILL.md edit, and on user approval applies it and logs to the skill's eval history. The compounding mechanism — each invocation can update the tool itself. Trigger phrases: 'skill improve', 'improve this skill', 'patch this skill', 'self-improve skill', '/skill-improve [skill-name]'."
version: 1.0.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion]
model: opus
---

> Reads the eval bundle layout defined in `docs/skill-eval-bundle.md`.

# Skill Improve — single-step self-modification

`/autoresearch` runs many experiments and converges. `/skill-critique` produces a deep structural review. **`/skill-improve` is the cheap, frequent step between them** — one invocation = one scored output, one proposed patch, one decision.

This is the compounding mechanism: skills carry their own tests, the agent updates the tooling in-flight, every use of the skill is an opportunity to make it better. Without this loop the skill library is static and plateaus.

## When to use

Activate when the user:
- Says "improve this skill" / "patch this skill" / "self-improve skill"
- Invokes `/skill-improve <skill-name>` with or without a recent output path
- Just used a skill, didn't love the output, and wants to tighten the SKILL.md before the next use

Do NOT activate for:
- First-time eval bundle creation → use `/skill-critique` to bootstrap, then collect anchored examples manually
- Multi-experiment prompt optimization → that's `/autoresearch`
- Generating a brand-new skill → not this skill
- Style polish on the SKILL.md prose → use `/sense-of-style` on the file

## Inputs

Resolve via `AskUserQuestion` if not provided:

1. **Skill name** (required) — resolves to `<skills-root>/<name>/SKILL.md`
2. **Recent output** (one of):
   - Path to a file the skill produced
   - Pasted content of a recent invocation's output
   - "fresh run" → re-execute the skill against one input from `evals/test-inputs.md` (default: first `train` input)
3. **Pass threshold** (default: 80% of evals must pass to skip critique)

## Pre-flight gate

Before scoring, the skill must have an eval bundle. Check `<skill-dir>/evals/eval-suite.md`:

- **Exists** → continue
- **Missing** → halt. Tell the user: *"<name> has no eval bundle. Bootstrap path: (1) run `/skill-critique <skill>` to surface probable failure modes; (2) write 3–6 binary evals to `evals/eval-suite.md`; (3) collect 5–8 test inputs to `evals/test-inputs.md`. Then rerun `/skill-improve`."* Exit cleanly.

This pre-flight is the "tests bundled with the skill" invariant. Without it the loop is just vibes.

## Workflow

### Step 1: Load context

- Read `<skill-dir>/SKILL.md`
- Read `<skill-dir>/evals/eval-suite.md`
- Read `<skill-dir>/evals/history.jsonl` (last 10 entries — trend awareness)
- Read 1–2 most recent `examples/good/` and `examples/bad/` if present

### Step 2: Score the recent output

For each eval in `eval-suite.md`, render a binary 0/1 against the output. One-line justification per eval (kept in working memory, not logged). Compute `pass_rate = sum(scores) / count(evals)`.

If `pass_rate >= threshold`:
- Log success to `history.jsonl`
- Tell the user: pass rate, which evals passed, no patch needed. Exit.

If `pass_rate < threshold`: continue to Step 3.

### Step 3: Diagnose

Identify the **single failing eval with the highest leverage** — the one whose pass would most improve overall output quality. If multiple tie, pick the one with the longest failure streak in `history.jsonl`.

Do NOT try to fix all failing evals in one patch. Single-variable mutation is the autoresearch principle: change one thing, observe, keep or revert. Multi-variable patches are unattributable.

### Step 4: Call `/skill-critique` (subagent)

Spawn `/skill-critique` as a subagent (`Agent` tool, `subagent_type: "general-purpose"`) with this prompt:

> Run the skill-critique skill on `<path>`. The skill is failing eval **<eval-N: name>** — *<eval question>*. Recent failing output excerpt: *<≤150 words of the bad output>*. The current SKILL.md text most relevant to this failure mode appears to be: *<the relevant section, quoted>*. Return: (a) root cause of why the SKILL.md under-constrains this eval, (b) a single-variable SKILL.md edit — exact old_string and new_string — that would most likely fix it without regressing other evals, (c) a one-sentence prediction of which other evals this edit could regress.

The full 11-section skill-critique pass is overkill for a single-eval fix; the subagent should focus.

### Step 5: Propose the patch

Show the user:

```
Skill: <name>
Pass rate: <N>% (below threshold <T>%)
Failing evals: <list>
Targeting: EVAL <N> — <name>

Proposed single-variable edit to SKILL.md:

  Old:
    <quoted text>

  New:
    <quoted text>

Rationale: <one paragraph from skill-critique>
Regression risk: <one sentence from skill-critique>
```

Ask the user: **Apply / revise / skip**.

### Step 6: Apply or skip

**Apply** → use `Edit` to patch SKILL.md. Append a line to `history.jsonl`:

```json
{"ts":"<ISO>","run_id":"<uuid-short>","input":"<input ref>","scores":{...},"pass_rate":<float>,"patch_applied":true,"target_eval":"<eval-N>","skill_sha_before":"<short hash>","skill_sha_after":"<short hash>"}
```

Compute SHA via `shasum -a 256 SKILL.md | cut -c1-12`.

**Revise** → user gives counter-suggestion; apply that instead, log as `patch_applied:true, patched_by:"user"`.

**Skip** → log `patch_applied:false` with a `reason:` field. The failure stays in history so trend analysis still sees it.

### Step 7: Re-score (optional, only if patch applied)

If user wants validation in-loop: re-run the skill against the same input, re-score. Append a second `history.jsonl` line with `verification: true`. If the patch *regressed* another eval, surface that immediately and offer to revert via a second `Edit` call.

Opt-in — it costs another full skill execution. Default off; user opts in via *"validate"* at step 6.

## Output

A short summary to the user, in this exact shape:

```
Skill: <name>
Result: <pass | patched | patched+verified | skipped>
Pass rate: <before> → <after>
Patch: <one-line description, or "none">
Next: <suggested follow-up, e.g., "after 3 more uses, consider running /autoresearch for a deeper pass">
```

## Rules

- **Pre-flight gate is hard.** No eval bundle → no run. Refuse politely with the bootstrap path.
- **Single-variable mutation only.** One target eval, one SKILL.md edit, one decision. If two are obviously coupled, still pick one and explain the deferral of the other.
- **Never silently apply.** The Edit happens only after explicit user *Apply*. This is a self-modifying tool; the human stays in the loop on every change.
- **`history.jsonl` is append-only.** Never rewrite. Trend integrity > tidiness.
- **No optimization of SKILL.md prose for prose's sake.** This skill targets *eval failures*. Style polish belongs in `/sense-of-style`.
- **No bundle bootstrapping.** This skill assumes the bundle exists. Bootstrapping is `/skill-critique` + manual eval authorship.

## Cost / speed

- Score + diagnose + skill-critique subagent + propose: ~30–60 seconds, ~$0.05–0.15 (one Opus turn + one subagent).
- Re-score verification doubles the cost.
- One invocation per use of a worked-with skill is the intended cadence. If a skill is used 10× a day, this loop fires 10× — that's the compounding.

## Related

- `/skill-critique` — bootstraps eval ideas; this skill calls it as a subagent for diagnosis
- `/autoresearch` — multi-experiment converge; use after `/skill-improve` has revealed a stubborn failure mode
- `docs/skill-eval-bundle.md` — the bundle layout this skill operates on
