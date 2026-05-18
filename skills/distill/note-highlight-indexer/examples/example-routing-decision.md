# Example Routing Decision — Step-by-Step

This walkthrough shows how the skill turns input content into a merged playbook entry — not as a black box, but as a sequence of decisions you can audit and tune.

Applies to **both modes** (manual paste-in and Readwise auto-processing). The internal logic is identical; the only difference is whether the input arrives via `/playbook-distill` paste or via the cron picking up a Readwise file.

For the **manual paste-in flow**, see `example-paste-in.md` first — it shows a full session.

This file uses the **Readwise example** (input file `example-input-article.md`, output file `example-output-playbook.md`) because the file-based example is easier to step through. The same 11-step logic applies to manual pastes.

## Input

`Vault/Reading/Articles/What Happens When the Coding Becomes the Least Interesting Part of the Work.md`
- Author: Obie Fernandez
- Category: `#articles`
- 6 highlights about working with coding agents (Claude Code, Cursor)
- File length: ~30 lines

## Step 1 — Read the routing index

Distiller reads `Vault/Playbooks-Index.md`. It sees the 10 domains:

```
1. Startup    2. Investing    3. Health    4. Parenting    5. Writing
6. Philosophy 7. Politics+Econ 8. Leadership 9. Personal OS 10. Tech
```

## Step 2 — Read the source

Distiller reads the article highlights. Looks for: dominant subject matter, named tools, named frameworks, the *kind* of insight (operational rules, opinion, narrative).

Substrate: 6 highlights about pair-programming with agents, articulation rules, judgment skills that don't transfer to the agent. Heavy operational content. Mentions Claude Code, agents, "blast radius," "sequencing," "reversibility."

## Step 3 — Classify

Match against the 10 domains:

| Domain | Match strength | Why |
|---|---|---|
| Tech / AI / Software | **Strong** | Article is literally about working with coding agents; mentions Claude Code, blast radius, sequencing, false-confidence tests |
| Startup | Weak | Mentions "client-billed work" — adjacent but tangential |
| Personal OS | Weak | "Articulation as a debugging tool for thinking" — tangential |
| Leadership | Weak | "Judgment, tradeoffs, intent" — tangential |
| All others | None | |

**Decision:** primary domain = **Tech**. Single-domain match (no cross-link needed).

## Step 4 — Find the target playbook + topic file

Path from Playbooks-Index: `Professional Development/AI/Tech Playbook/`

Distiller checks: does the folder exist? **Yes**. Read the playbook's `README.md`. See existing topic files. Look for a topic file whose dimension matches "working with coding agents."

Match found: **`working-with-coding-agents.md`** already exists (was scaffolded from a prior article on the same topic).

**Decision:** merge into existing file. No new topic file needed. No scaffolding.

## Step 5 — Read the existing topic file before merging

Distiller reads `working-with-coding-agents.md` to:
1. Avoid re-stating what's already there
2. Find adjacent sections where new highlights extend an existing pattern
3. Preserve existing source tags

## Step 6 — Distill highlights → operational format

For each highlight, the distiller asks: "what's the **rule** here, not just the quote?"

| Highlight | Operationalized as |
|---|---|
| "Agents force you to say the unspoken parts out loud... If you only describe the what and not the how, expect to be underwhelmed." | **Rule:** every non-trivial coding-agent prompt includes both *what* and *how I'm thinking about it*. → "Articulation rule" section |
| "You can't just let the AI guess the correct abstraction level... or that something is meant to be a temporary kluge." | **Scorecard:** rate the brief on Abstraction Level, Risk Profile, Permanence (0–3 each). Total <10/15 → rewrite before sending. → "Spec scorecard" section |
| "That act of explanation does something important. It slows you down enough to notice when your instincts are off." | **Trigger:** if writing the brief surfaces a question you can't answer, the implementation is premature. → "Pair-programming side-effect" section |
| "Other tools show up just as often: blast radius / sequencing / reversibility / social cost / allergy to false confidence." | **Reference table:** the 5 judgment skills agents don't replace, with pre-merge questions. → "Five judgment skills" section |
| "If the part you care about is the decision-making around the code, agents feel like they clear space." | **Decision rule:** at senior experience level, marginal time on brief + review beats marginal time on keystrokes. → "Value-shift implication" section |
| "When I spend time actually typing code... it feels like a waste of my time." | **Anti-pattern detector:** "typing code yourself when the brief would have been faster" → "Anti-pattern detectors" section |

Plus a **fillable template** synthesized from the abstraction-level + risk-profile + permanence highlights:
```
WHAT: ...
HOW (mental model): ...
ABSTRACTION LEVEL: ...
RISK PROFILE: ...
PERMANENCE: ...
NON-GOALS: ...
```

## Step 7 — Source-tag every claim

Every paragraph, every row, every bullet ends with the inline source tag:
`[Coding Becomes the Least Interesting Part — Obie Fernandez, 2026-02-01]`

(The date is the file's modified date in the Reading folder. Multiple sources stack as a comma-separated list.)

## Step 8 — Update the playbook README

Append to `Tech Playbook/README.md`:
- `## Sources captured` section gets a new line:
  - `- Coding Becomes the Least Interesting Part — Obie Fernandez [2026-02-01] — merged into working-with-coding-agents.md (5 new sections, 4 anti-pattern detectors)`

## Step 9 — Update the routing index

`Vault/Playbooks-Index.md` "Active Playbook Status" table gets:
- Tech Playbook: Files = 1 (no change), Last Source Added = "Coding Becomes the Least Interesting Part — Obie Fernandez 2026-05-04"

## Step 10 — Mark file as processed

Append to `~/.claude/state/distilled-readwise.json`:
```json
{
  "<vault>/Reading/Articles/What Happens When the Coding Becomes the Least Interesting Part of the Work.md": {
    "hash": "abc123...",
    "processed_at": "2026-05-04T07:32:15Z",
    "domain": "Tech",
    "merged_into": ["Professional Development/AI/Tech Playbook/working-with-coding-agents.md"],
    "scaffolded": false,
    "run_id": "20260504-073200"
  }
}
```

Next time the cron runs, this file will be skipped (hash match) unless Readwise re-syncs and changes the file.

## Step 11 — Append to vault log

`Vault/log.md` gets one line:
```
2026-05-04 07:32 | auto-distill | merged | Coding Becomes the Least Interesting Part.md | Tech → working-with-coding-agents.md; 6 insights merged
```

## Output (stdout to cron log)

```
[auto-distill] Coding Becomes the Least Interesting Part.md → Tech Playbook/working-with-coding-agents.md (6 insights)
```

---

## What this example illustrates

1. **The article never gets stored as "an article note."** It gets dissolved into operational rules inside an existing topic file. Six months from now, you don't remember reading the article — but the rules show up in your prompt-writing.
2. **One source can produce multiple structural artifacts.** This article alone added a scorecard, a fillable template, a decision-trigger list, an anti-pattern detector, and a reference table. All in the same topic file.
3. **The merge is idempotent.** Run the cron twice, the file processes once. Run it after Readwise re-syncs with a new highlight, the file processes again — and the new highlight gets merged without duplicating the prior content (the distiller reads the existing file before merging).
4. **No "summary at the top."** No "this article argues..." filler. Just the rules, source-tagged, ready to be loaded into a future skill that needs them.
