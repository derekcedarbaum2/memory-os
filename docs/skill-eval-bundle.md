# Skill Eval Bundle — convention for per-skill self-tests

Each skill folder may ship with an **eval bundle** — its own tests + anchored examples + reference inputs. Marcus Spillane's framing: each skill bundle carries its own tests, the agent can modify them in-flight, and that's what creates the compounding effect. Static skill libraries plateau fast.

This bundle is **opt-in per skill**. Not every skill needs evals (one-shot conversational helpers don't). Skills that produce structured artifacts — PRDs, decks, briefs, outreach, lint reports — should have one.

## Layout

```
skills/<skill-name>/
  SKILL.md                          # the skill itself
  evals/
    eval-suite.md                   # 3–6 binary checks (pass/fail)
    test-inputs.md                  # 5–8 prompts/scenarios, marked train vs holdout
    history.jsonl                   # one line per scored run (append-only)
  examples/
    good/                           # ✅ anchored outputs that should pass every eval
      <case-name>.md
    bad/                            # ❌ anchored failures — what NOT to produce
      <case-name>.md
  reference/                        # deep-link docs the skill loads on demand
```

## File schemas

### `evals/eval-suite.md`

```markdown
# Evals — <skill-name>

3–6 binary checks. Specific enough that two agents would score the same output the same way.

## EVAL 1: <short-name>
Question: <yes/no question about the output>
Pass: <specific success criterion>
Fail: <specific failure trigger>

## EVAL 2: ...
```

### `evals/test-inputs.md`

```markdown
# Test inputs — <skill-name>

Marked `train` (visible to optimization loop) vs `holdout` (only for baseline + final).

## INPUT 1 [train]: <case name>
<the exact prompt/scenario>

## INPUT 2 [holdout]: <case name>
<the exact prompt/scenario>
```

### `evals/history.jsonl`

One JSON object per line. Append-only.

```json
{"ts":"2026-05-19T11:30","run_id":"r-001","input":"<input-name>","scores":{"eval-1":1,"eval-2":0,"eval-3":1},"pass_rate":0.67,"output_path":"...","skill_sha":"<hash of SKILL.md>"}
```

### `examples/good/<case>.md` and `examples/bad/<case>.md`

```markdown
---
case: <name>
verdict: pass | fail
evals_passed: [1, 3, 5]
evals_failed: [2, 4]
notes: <why this is anchored as good/bad>
---

<the full output that should serve as the anchor>
```

## How the toolchain uses the bundle

- **`/autoresearch`** — when invoked on a skill that has `evals/`, autoresearch skips its bootstrap interview (no need to ask user for criteria + inputs) and loads them directly. Without `evals/`, autoresearch falls back to the interview path.
- **`/skill-critique`** — reads `evals/eval-suite.md` to ground its gap-checklist pass. Empty or absent eval suite is itself a structural gap flag.
- **`/skill-improve`** — the use→critique→patch loop. Reads `evals/`, scores recent output, calls skill-critique if below threshold, proposes a single-variable SKILL.md edit, logs to `history.jsonl`.

## Rules

- **Binary evals only.** No scales, no "quality on a 1–10." Two agents must score identically.
- **3–6 evals.** More and the SKILL.md starts parroting eval criteria instead of improving.
- **Train/holdout split is non-negotiable** for any eval-driven optimization. 60/40 or 70/30. Holdout is the overfitting detector.
- **`history.jsonl` is append-only.** Never rewrite past entries. They're the trajectory.
- **Anchored examples are immutable.** When SKILL.md evolves and a "good" example no longer matches behavior, write a new one and move the old to `examples/archive/`. Don't rewrite history.
- **`examples/bad/` is the antipatterns folder** that many existing skills already reference at the end of their SKILL.md. The bundle formalizes that pattern.

## Bootstrap path for an existing skill with no bundle

1. Run `/skill-critique <path-to-SKILL.md>` — produces a critique that surfaces probable failure modes.
2. From the critique's gap table, draft 3–6 binary evals → `evals/eval-suite.md`.
3. Collect 5–8 real prompts you've used the skill for → `evals/test-inputs.md` (mark holdouts).
4. Capture one anchored good output and one anchored bad output → `examples/good/`, `examples/bad/`.
5. Run `/autoresearch` on the skill to validate the bundle and converge a baseline.
6. From then on, every invocation of `/skill-improve` is a single-step compound — score, patch one thing, repeat.

Roll out gradually. Start with the 3–5 skills that produce the highest-stakes artifacts — not the 50+ skills at once.
