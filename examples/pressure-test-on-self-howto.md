# pressure-test, round 2 — on the HOW-TO doc

Three days after publishing `docs/HOW-TO.md`, I ran the `pressure-test` skill on it. Four context-isolated adversarial agents, each playing a different persona, attacking from a different direction. Referee verdict synthesized; rewrites applied; the resulting HOW-TO is what's live now.

This is the second sanitized referee artifact in this repo. The [first one](pressure-test-on-self.md) demonstrated the skill on argument prose (`thesis.md`, `envelope.md`, `why-not-vectors.md`). This one demonstrates it on instruction prose (`HOW-TO.md`), which is a different beast — the failure modes are different and the personas are different.

## The setup

Question to the four agents: *Is the HOW-TO doc actually followable, useful, and honest about what it is?*

| Persona | Direction | What they're attacking |
|---|---|---|
| Cold first-time adopter | NULL | "I cannot follow this — assumes prior knowledge I don't have" |
| Year-3 fossilization survivor | AGAINST | "The annual refactor playbook is motivational, not runnable" |
| Anti-ritualist skeptic | NULL | "Daily/weekly/monthly rituals are performative; nobody follows them" |
| Different-shape knowledge worker (researcher) | ALTERNATIVE | "The doc is Derek-shaped dressed up as generic" |

## The headline finding

All four agents converged on one meta-critique that the original doc didn't see:

> **The doc accidentally undersells the architecture by demanding things from the human that the architecture is supposed to do for them.**

The architecture's central claim is *self-healing-via-cron*. The original HOW-TO kept saying "Block 30 minutes," "Don't skip it," "Read it Monday before opening anything else." Those two framings contradict each other — and the contradiction is what let every agent's specific critique land.

Fix: **lead with the cron, frame human practices as optional polish.** That single reframing dissolved roughly 60% of the attacks across all four agents.

## What landed — by agent

### Cold first-time adopter

*Setup steps weren't runnable.* Three undefined nouns in five bullets, no actual install commands, no Linux story. Verbatim landings:

> "Set up MEMORY.md in your Claude Code memory directory with the hot-pinboard template" — three unknowns in one sentence on step 4 of week 1.

> "Install the weekly cron (weekly-memory-maintenance.sh + the launchd plist)" — naming two artifacts is not an install instruction. I expected a command. I got a parenthetical.

> "Promote 2-3 of these principles to inline rules in MEMORY.md" — abstraction whiplash from "walk the dog and talk."

**Rewrite applied:** Split the doc. The setup content moved entirely to a new [`QUICKSTART.md`](../docs/QUICKSTART.md) — week 1 with actual `cp`, `launchctl load`, and `sed` commands. Every noun defined in a glossary table at the top. Linux/Windows gap named explicitly. The `HOW-TO.md` now assumes the substrate exists.

### Year-3 fossilization survivor

*The annual refactor playbook was motivational, not runnable.* The genuinely hard parts of refactoring a controlled vocabulary weren't named:

> "Tags with <5 uses are probably dead. Tags with >100 uses are probably non-discriminating." — both bounds wrong in named ways. A `domain:hiring` used 4 times where each was a hire decision is the *most* load-bearing tag, not dead.

> "Write a migration script. Extend tag-backfill.py to map old tags to new tags." — most non-trivial old tags map to *multiple* new ones depending on per-file context. A regex script can't decide; the human has to.

> "Block a weekend. Don't try to do this in pieces." — wish-fulfillment. Day 1 surfaces ambiguities that require 2–3 days of background processing before you can resolve them.

**Rewrite applied:** The annual-refactor section is now 10 explicit steps, with realistic time estimates (8–16 hours focused work spread across 2–3 calendar weeks), an explicit dependency-audit step (grep skills/scripts/hooks for hard-coded tag references before any rename), an explicit human-adjudication pass between drafting and scripting (the one-to-many mapping problem made visible), and an explicit post-refactor validation step (re-run the routing crons in dry-run; spot-check 5 random files).

### Anti-ritualist skeptic

The deepest meta-critique. Verbatim:

> "The doc treats human discipline as a load-bearing input when the entire architectural pitch is supposed to be that the substrate compounds *because* the cron is doing the work. Every ritual sentence that demands a specific human time slot is a confession that the automated layer isn't actually sufficient."

> "First Monday of the month is hygiene day. Block 30 minutes." — first Monday is the worst possible default. It's the day everyone with a real job has month-open standups, board prep, payroll, invoice cycles, kickoffs.

> "Don't skip it" is the productivity-genre tell. Real systems don't beg.

**Rewrite applied:** Wholesale reframing. The new HOW-TO has two clearly separated sections:

1. **"What the cron does automatically (no human input)"** — the load-bearing layer. This is what runs the system.
2. **"What you optionally do (when convenient)"** — polish on top. These add value at the margin but are not load-bearing.

Plus a new section: **"What to do when you skip optional rituals for 3+ weeks."** Names the recovery path explicitly: read `Vault/log.md` from the silent period forward, revive any falsely-demoted ventures, skim accumulated promotion candidates, run `/prune-memory` and `/vault-lint`. ~30 minutes of focused work to fully catch up.

"First Monday of the month is hygiene day. Block 30 minutes" is gone. The closest replacement: *"If you have time, once a quarter is fine, do: [list]. If you don't have time, the cron's weekly audit catches most of the same things on a longer lag."*

### Different-shape knowledge worker

The doc claimed generality the architecture couldn't deliver. Researcher landed it:

> "Pick your three most active engagements" — I don't have engagements. I have one research program with sub-projects.

> "Two possibilities. One: you took a long break. Two: you changed roles." — there's a third dominant case the doc didn't name: *in-flight, blocked on an external dependency*. A paper at Nature for 4 months. A grant in NIH study section for 5 months. Not dormant; *waiting*.

> "Hot pinboard saturated at 7-8 active ventures" — assumes multi-stream work. Mine is one stream at different phases.

**Rewrite applied:** New section near the top of HOW-TO: **"What shape of work this assumes."** Names the assumed shape (rolling parallel engagements with discrete identities, 5–8 active concerns, months-scale lifecycle) and gives three worked translations:

- Academic researcher: `Program/Papers/Grants/Collaborations/` instead of `Work/Ideas/`; phase board instead of pinboard; per-tag decay policy with `phase:under-review` having no decay.
- Indie hacker: `Product/Features/Experiments/Customers/`; pinboard by release status.
- Writer: `Manuscript/Research/Drafts/Notes/`; pinboard chapters by status.

The "in-flight blocked on external dependency" case is now named in the failure-mode triage table: *touch the file or add `status:in-flight` tag and exclude it from the dormancy cron*.

## What survived across all four agents

These attacks didn't land — the durable parts of the doc:

1. **The skill decision tree.** Cold-adopter said it's the *one* part of the doc usable standalone.
2. **The failure-mode triage table.** "Reads well because the symptoms are concrete and the fixes are shell commands."
3. **The "When NOT to use" matrix.** "The most honest piece in the doc."
4. **The framing that vocabulary fossilization is a *feature* at year 2-3, not a failure.** Year-3 user explicitly conceded this is correct and rare.
5. **The substrate claims** (Markdown + grep + frontmatter + git audit trail). Researcher's verdict was "adopt the retrieval substrate, replace the folder taxonomy."

All five made it into the rewritten doc unchanged.

## The structural changes that shipped

| File | What changed |
|---|---|
| `docs/QUICKSTART.md` (new) | Split out from HOW-TO. Cold-adopter focused. Week 1 with actual commands. Glossary table defines every noun. macOS-only gap named. |
| `docs/HOW-TO.md` (rewritten) | Cron-first reframing throughout. New "What shape of work this assumes" section near top. New "What to do when you skip optional rituals for 3+ weeks" recovery section. Annual refactor section rewritten as 10 explicit runnable steps. |
| `README.md` | Surface QUICKSTART for new readers; HOW-TO for existing users. |
| `examples/pressure-test-on-self-howto.md` (new) | This file. |

## What the next pressure-test should attack

Predictions for round 3, in 1–3 months, on the rewritten docs:

- The QUICKSTART will probably fail on someone who tries to follow it on Linux despite the macOS-only warning. The translation work needs its own doc, or the warning needs to be louder.
- The "What shape of work this assumes" section will probably surface a fourth or fifth work shape I didn't name (consultant who *only* takes one engagement at a time? lawyer with case files? designer with client-by-client portfolios?).
- The annual-refactor section will probably hold until someone actually runs it and discovers a step I missed. The proof of the playbook is whether it survives first contact.

When that round happens, the artifact lands here as `examples/pressure-test-on-self-howto-round-3.md` and the rewrites that result land in the docs.

## Why the public-adversarial-review pattern matters

Most repos that say "feedback welcome" mean it in a passive sense. This pattern — *run the adversarial review on yourself, publish the critique, publish the rewrites* — is closer to what feedback actually accomplishes when it works. It also doubles as evidence the `pressure-test` skill works on real artifacts and not just toy examples.

The cost of doing this is ~45 minutes (the four parallel agents run in parallel; the synthesis is single-pass; the rewrites take ~1 hour). The benefit is the doc is now demonstrably stronger than it was 90 minutes ago, and the critique is preserved as a baseline for future rounds.

I expect to run this once a quarter on whatever the doc-of-the-quarter is. The system gets better when the critique is public.
