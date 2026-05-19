# How to operate a memory-os vault

You've got the substrate running. Now what? This doc covers ongoing operation. It assumes you've already done the install in [`QUICKSTART.md`](QUICKSTART.md) — if you haven't, start there.

Three things you'll get from reading this:

1. A clear separation of **what the cron does automatically** (the load-bearing part) from **what you optionally do** (the polish on top).
2. The skill decision tree, failure-mode triage, and "when NOT to use" matrix.
3. The runnable version of the annual vocab refactor — the only thing about this system that genuinely demands a multi-week pass every couple years.

---

## What shape of work this assumes

Before anything else: **memory-os was built for one specific shape of work.** It works for that shape. For other shapes, the architecture generalizes but the folder taxonomy and pinboard semantics need translation. If you skip this section and try to force your work into the default shape, you'll spend month one fighting the conventions before realizing the mismatch.

**The assumed shape:** rolling parallel engagements with discrete identities. Roughly 5–8 active concerns at a time, each with its own folder, its own `_learnings.md`, its own decay cycle. New engagements start and old ones end on the order of months. This is consulting-shape, PM-shape, founder-shape — work where the *granularity is the venture or the client* and the parallelism is real.

### Translations for other shapes

If your work isn't like that, the architecture still generalizes — but you'll want to replace the folder taxonomy and rethink the pinboard. Three worked examples:

**Academic researcher (one program, 4–6 sub-projects, 4–6 month review cycles):**
- Replace `Work/Ideas/` with `Program/Papers/Grants/Collaborations/Reading/`.
- Replace the active-venture pinboard with a *phase board*: what's in writing, what's in analysis, what's under review, what's blocked-on-external-dependency.
- Replace the 90-day dormancy cron with a per-tag policy: `phase:under-review` has no decay; `phase:writing` decays at 30 days; etc. Edit `dormancy-decay.py` to read the `phase:` tag.
- "Active ventures" in `MEMORY.md` becomes "Active phases" — sub-projects keyed by what verb they're at.

**Indie hacker (one product, many features, release cycles):**
- Replace `Work/Ideas/` with `Product/Features/Experiments/Customers/`.
- Pinboard by feature release status, not parallel projects.
- Dormancy is per release cycle, not 90 days.

**Writer (one book, many chapters, draft-revise rhythm):**
- Replace `Work/Ideas/` with `Manuscript/Research/Drafts/Notes/`.
- Pinboard chapters by status (drafting / revising / cut / parked).
- Dormancy doesn't apply the way the default cron assumes — chapters that aren't being touched are usually *finished*, not stale.

In all three cases the substrate (Markdown + grep + `_learnings.md` + cron-driven maintenance) is correct. The folder names and decay policy aren't. Translate them once, then the rest of this doc applies.

If your work doesn't match any of the four shapes named above, write down what your actual unit-of-work is before you build a vault. The convention is a means to an end; pick the version that fits.

---

## Cheat sheet

### What the cron does automatically (no human input)

| Schedule | What runs | What you get |
|---|---|---|
| Daily 7:00 AM PT | Voice memo sync | Phone memos land in `Vault/Voice Memos/` |
| Daily 7:15, 11, 2, 5 PT | `generate-today.sh` | `Vault/Today.md` regenerated |
| Daily 7:30 AM PT | `auto-distill-readwise.sh` | New Readwise highlights distilled into domain playbooks |
| Sunday 10:00 PM PT | `learnings-resurface.sh` | Cross-corpus pattern detection; principles routed, commitments turned into tasks |
| Sunday 11:00 PM PT | `weekly-memory-maintenance.sh` | Dormancy decay (90d), active-venture pinboard refresh, memory dir audit |
| Per session end | `archive-session.sh` (hook) | Raw transcript saved to `Vault/AI Toolkit/CC Chat History/` |

This layer is the load-bearing part. If you do nothing else, the cron keeps the system healthy.

### What you optionally do (when convenient)

| When | What | Why bother |
|---|---|---|
| End of any non-trivial Claude Code session | `/archive-session` | Enriched metadata + insights extraction + project index update beyond what the raw hook captures |
| Monday morning, when it fits | Skim last week's entries in `Vault/log.md` | Catch surprising cron output earlier than next week |
| Whenever a doc is shipping to a stakeholder | `/qa-loop` on it | Three adversarial agents catch real issues before the stakeholder does |
| Whenever an argument is going public | `/pressure-test` on it | Multi-persona adversarial attack on the load-bearing claims |
| Whenever prose is soft but substance is solid | `/sense-of-style` | Pinker-grounded line-level rewrite |
| Occasionally, when you remember | `/vault-lint --fix` | Catches drifted frontmatter, broken wiki-links, stale `_learnings.md`, missing tags |
| Occasionally, when MEMORY.md feels bloated | `/prune-memory` | Audit + demote / consolidate |

None of these are required. The cron-driven layer above keeps the system running indefinitely without any of these manual steps. These add polish. Treat them as *available* rather than *due*.

### Skill decision tree

> **You have an artifact. You're not sure if it's ready. Pick one:**

```
Is it an ARGUMENT going public (essay, README, public pitch)?
    YES → /pressure-test
    NO  ↓

Is it a DELIVERABLE going to a stakeholder (PRD, proposal, brief)?
    YES → /qa-loop
    NO  ↓

Is the substance right but the prose soft?
    YES → /sense-of-style
    NO  ↓

Is it about the VAULT itself (orphans, broken links, drifting frontmatter)?
    YES → /vault-lint  (add --fix for safe auto-corrections)
    NO  ↓

Is it about MEMORY.md (oversized, stale entries, project_*.md leftovers)?
    YES → /prune-memory
    NO  ↓

Probably no skill — just edit it.
```

### When NOT to use memory-os patterns

| Task | Do this instead |
|---|---|
| Single throwaway one-shot script | Just write it; don't make a `_learnings.md` |
| A note you'll reread once in 48 hours and never again | Drop in `raw-sources/`; let it expire |
| Highly confidential client work that can't co-mingle | Separate vault; don't fold into this one |
| Bulk import of 100k+ documents you didn't write | Vector index over them; not Markdown + grep |
| Multiple humans writing into the same corpus | Pick one taxonomic owner or use a vector store; controlled vocab doesn't survive multiple writers |
| Work that's identity-changing and invalidates 80% of your taxonomy | Pause; consider whether memory-os fits the new shape before forcing it |

### Failure-mode triage

| Symptom | Likely cause | Quick fix |
|---|---|---|
| Cron didn't run Sunday night | Lockdir left over from a crashed run | `rm -rf /tmp/weekly-memory-maintenance.lock`, re-run manually |
| `MEMORY.md` jumped to 100+ lines silently | Hot pinboard accumulating; cron only audits, doesn't auto-trim | Run `/prune-memory`; demote stale entries to INDEX.md |
| Wiki-links suddenly broken everywhere | Renamed a file without updating references | `grep -r "\[\[old-name\]\]" Vault/` and fix references |
| Half my pinboard auto-demoted to dormant | Long break, role change, or *in-flight blocked on external dependency* | If real activity is happening but invisible to the cron (waiting on reviewer 2, NIH study section, etc.), `touch` the file or add a `status:in-flight` tag and exclude it from the dormancy cron |
| Tag drift mid-quarter | Adding new tags inline without canonicalizing | Run `/vault-lint`, audit unknown tags, decide which to canonicalize and which to retag |
| You haven't done Monday review in 3 weeks | Life | See "What to do when you skip optional rituals" below |
| Year 2-3 vocabulary fossilization | The taxonomy no longer carves nature at its joints | See **Annual vocab refactor** below — it's a multi-week process, not a weekend |

---

## Narrative: what the cron actually does

The architecture's central claim is *self-healing-via-cron*. Here's what that means in practice.

**Sunday 10 PM PT** — `learnings-resurface.sh` fires. It reads every session archive, every `_learnings.md`, and every voice memo from the past week. Clusters semantically similar atoms across files. Applies the source-diversity rule (need ≥2 distinct human sources, not 3 voice memos from the same person). Classifies clusters by type (principle / anti-pattern / state / commitment / open question). Routes per type — principles into playbooks, commitments into Todoist, open questions into the relevant `_learnings.md`. Promotes cross-venture principles to `MEMORY.md` only if they fire across ≥2 ventures with ≥3 sources. Logs every routing decision to `Vault/log.md`.

**Sunday 11 PM PT** — `weekly-memory-maintenance.sh` fires after the 10 PM job has settled. Three jobs in sequence: `dormancy-decay.py` (any `_learnings.md` with no edit in 90 days gets `status:dormant` in frontmatter), `active-venture-refresh.py` (pinboard entries whose `_learnings.md` is 90+ days untouched get demoted to `INDEX.md` "Dormant ventures"), `prune-memory-dryrun.py` (audit-only check: line count vs. 80-line cap, subfolder/filename consistency, tag-vocabulary compliance).

**Daily 7 AM PT chain** — voice memo sync at 7:00, Today.md regenerate at 7:15, Readwise auto-distill at 7:30. By the time you sit down to work, the vault is current.

**Per session** — `archive-session.sh` (a Claude Code SessionEnd hook, not a cron) writes raw session transcripts to `Vault/AI Toolkit/CC Chat History/`. Running `/archive-session` interactively enriches that raw archive with metadata extraction.

What this means concretely: **you can skip every optional ritual below and the system still compounds.** The cron will surface dormancy decisions, promotion candidates, and weekly summaries on its own. The append-only `_learnings.md` discipline is event-driven (you write when you decide), not calendar-driven. The cron handles the calendar.

The optional human practices below are about *catching things earlier* than the next cron run, *acting on candidates the cron surfaces*, and *applying quality skills* to artifacts that are about to leave your hands. None of them are load-bearing.

---

## Narrative: optional human practices

### Capturing into the right place (event-driven, not calendar-driven)

When you decide something venture-scoped, write it down. Append to that venture's `_learnings.md` under `## Key Decisions` if it has a binary outcome, `## Learnings` if it's an insight, `## Open Threads` if it's unresolved. This is the *only* practice that's genuinely load-bearing on the human side, because the cron can't write decisions you didn't capture.

When you have a thought that doesn't fit anywhere yet, talk into your phone. Whatever voice-memo tool you use (Monologue, Otter, whatever), it lands in `Vault/Voice Memos/` overnight and the daily auto-distill chain handles routing.

When a Claude Code session has produced meaningful decisions or insights, run `/archive-session` before closing it. The raw SessionEnd hook captures the transcript; the interactive skill enriches it with metadata extraction. The enriched version compounds; the raw version doesn't.

### Reading the weekly log (when it fits)

Sometime Monday or Tuesday — or whenever you next sit down for focused work — open `Vault/log.md` and scroll to the most recent Sunday-11 PM `weekly-memory-maintenance` block. Read the summary lines from the two crons. Three things to look at:

1. **Demoted ventures.** Files the cron moved from hot pinboard to cold index. Almost always agree. If one feels wrong, the venture is in-flight-but-blocked rather than dormant — touch the file or add `status:in-flight` and exclude it from future dormancy runs.
2. **Promotion candidates.** Files touched recently that aren't on the pinboard. Read the file. Promote if it's compounding into something real; ignore if incidental.
3. **Routed principles.** Cross-corpus patterns the cron promoted into a playbook. Read the new entry, sanity-check the routing, edit if needed.

If you don't get to this in any given week, the cron still ran. The next week's log will show both weeks of decisions. Nothing breaks.

### Running quality skills on outgoing artifacts

Three skills earn their keep at specific moments:

- `/qa-loop` before a deliverable goes to a stakeholder (PRD, proposal, brief)
- `/pressure-test` before an argument goes public (essay, README, pitch)
- `/sense-of-style` when the substance is solid but the prose is soft

Don't run all three on everything. Pick the one whose specific incentive matches what the artifact needs. The skill decision tree in the cheat sheet is the lookup.

### Monthly hygiene (genuinely optional)

If you have time, once a quarter is fine, do:

- `/vault-lint --fix` on the whole vault.
- Skim `INDEX.md` to catch anything dormant that's quietly become relevant.
- Read your last month of session archive titles to confirm you're working on what you intended to.

If you don't have time, the cron's weekly audit catches most of the same things on a longer lag. The difference between doing this monthly and doing it never is real but small — call it 5–10% better signal density. The difference between doing the cron and not doing the cron is much larger.

---

## What to do when you skip optional rituals for 3+ weeks

This will happen. A deadline lands, you travel, family stuff, sickness. You stop reading the Monday log, you stop running `/archive-session`, the human layer goes silent for a month.

When you come back:

1. **Read `Vault/log.md` from the silent period forward.** This is the longest part of the recovery. Probably 5–15 minutes.
2. **Skim the demoted ventures.** Anything that got marked dormant during the gap that's actually still active needs a `touch` or a frontmatter edit to revive.
3. **Skim accumulated promotion candidates.** The cron has been surfacing files; you've been ignoring them. Decide which to promote, mark the rest as "reviewed, not promoting."
4. **Run `/prune-memory`** to catch anything that drifted in `MEMORY.md`.
5. **Run `/vault-lint`** (read-only first; `--fix` if it looks safe) to catch frontmatter or wiki-link issues that built up.
6. **Start running `/archive-session` again.** The sessions you ran during the silent period have raw archives but no enriched metadata; the project indexes are stale by however much.

Recovery takes one focused 30-minute pass. The system doesn't punish you for the gap — the cron kept running, the substrate kept absorbing, the only thing you lost is some catch-up time.

The point: **the architecture survives ritual lapses.** If it didn't, it would be a discipline-gated system pretending to be self-healing, which is the failure mode of every productivity framework written before this one. memory-os is built to survive your bad weeks; act like it does.

---

## Annual vocab refactor — the runnable version

The controlled vocabulary survives roughly 18–24 months of stable cognitive frame. After that, the corpus contains new ventures the taxonomy didn't anticipate, role changes that reshape which `domain:` tags discriminate, and semantic drift in what counts as a "principle" vs. "state" vs. "identity."

Refactoring the vocab is a multi-week elapsed process — not a weekend. About 8–16 hours of focused work, but spread across 2–3 calendar weeks because day 1 surfaces ambiguities that need background processing before you can resolve them. The actual steps:

### Step 1 — Dependency audit (1 hour, day 1)

Before you rename anything, find every skill, script, hook, and cron that hard-codes a tag. Grep is your friend:

```bash
# Every controlled tag value, where it's referenced:
grep -rE "kind:(identity|feedback|state|principle|location|pipeline|gotcha)" ~/.claude/skills/ ~/.claude/hooks/ ~/.claude/reference/
grep -rE "decay:(low|medium|high)" ~/.claude/skills/ ~/.claude/hooks/ ~/.claude/reference/
grep -rE "venture:[a-z-]+" ~/.claude/skills/ ~/.claude/hooks/ ~/.claude/reference/
```

Write down every file that references each tag value. These are your *renames-with-cascade*. Renaming a tag without updating these silently produces wrong cron output for weeks.

### Step 2 — Usage audit (30 minutes, day 1)

Count tag usage across the vault and memory dir:

```bash
grep -rohE "(kind|decay|venture|domain|status):[a-z-]+" \
    "$VAULT" ~/.claude/projects/-Users-*/memory/ \
  | sort | uniq -c | sort -rn > /tmp/tag-usage.txt
```

Read `tag-usage.txt`. Don't trust frequency heuristics blindly:

- **Low-frequency tags can be load-bearing.** A `domain:hiring` used 4 times where each use was a major hire decision is more important than a `domain:misc` used 200 times.
- **High-frequency tags can be either signal or noise.** `kind:reference` *should* be high-count by design. Frequency alone doesn't tell you which.

For each tag value, decide: keep / merge into another / split into multiple / retire. Write the decisions in a scratch file — you'll need them in step 4.

### Step 3 — Draft the new vocabulary (2–4 hours, day 1–2)

Open `~/.claude/reference/tag-vocabulary.md`. Mark deprecated values with `(deprecated, see <new-value>)`. Add new values. Don't delete old values yet.

Important: most non-trivial renames are *one-to-many* depending on context. A `kind:principle` entry might now be `kind:identity` (if it's about who you are) or `kind:feedback` (if it's a learned preference). The new vocabulary needs to capture both meanings; the migration script can't decide which one applies to each file.

Save the draft. Sleep on it. Day-1 ambiguities surface as day-2 clarifications about 80% of the time. The remaining 20% need real thought.

### Step 4 — Human-adjudication pass (4–8 hours, days 3–14)

For each file whose tags will change, decide what the new tags should be. The mechanical part is a script; the *deciding* is the work.

Generate a migration plan:

```bash
python3 ~/.claude/hooks/tag-backfill.py --plan-only > /tmp/migration-plan.json
```

(You'll need to extend `tag-backfill.py` to support `--plan-only` mode that outputs proposed changes per file rather than applying them. The current version only enforces; extend it for refactor.)

Read the plan. For each file where the proposed change is ambiguous (multiple possible new tags), open the file, read it, decide. Annotate the plan with your decision. This is the part that takes 2–3 weeks elapsed — you can't do it all in one sitting, and the ambiguities accumulate as you uncover them.

### Step 5 — Run the migration in dry-run (1 hour)

```bash
python3 ~/.claude/hooks/tag-backfill.py --migration-plan /tmp/migration-plan.json --dry-run
```

Inspect the diff. If anything surprises you, go back to step 4 for that file.

### Step 6 — Apply the migration (15 minutes)

```bash
python3 ~/.claude/hooks/tag-backfill.py --migration-plan /tmp/migration-plan.json
```

### Step 7 — Update dependent skills and scripts (1–2 hours)

For every reference found in step 1 (dependency audit), update the hard-coded tag value to the new vocabulary. Re-run the dependency-audit greps to confirm zero remaining references to deprecated values.

### Step 8 — Update `tag-vocabulary.md` (15 minutes)

Remove the deprecated values. The vocabulary is now clean.

### Step 9 — Post-refactor validation (1 hour)

Did the refactor actually work? Run the routing crons in dry-run mode to confirm:

```bash
python3 ~/.claude/hooks/learnings-resurface.py --dry-run  # confirm principle routing still finds principles
python3 ~/.claude/hooks/active-venture-refresh.py          # confirm pinboard parsing still works
python3 ~/.claude/hooks/prune-memory-dryrun.py             # confirm memory dir audit is clean
```

Spot-check 5 random `_learnings.md` files: do their new tags retrieve correctly with `grep`? If not, you have residual drift.

### Step 10 — Log the refactor (15 minutes)

Append an entry to `Vault/AI Toolkit/agentic-architecture.md` Evolution log: what changed in the vocabulary, why, which dependent skills/scripts were updated, what the next refactor will likely need to address. This entry is the most valuable artifact the refactor produces — it tells future-you what your past judgment was.

### When the refactor isn't enough

If you find yourself doing the refactor *quarterly*, the system is wrong for your work. Either your work is changing faster than any taxonomy can keep up (consider a hybrid graph-extraction layer to supplement the controlled vocab), or you're over-engineering the vocab (consolidate categories, fewer namespaces). Step back.

If the refactor takes more than 3 weeks elapsed, something is wrong with the vocabulary design rather than the refactor process. Don't power through; rethink the namespaces.

---

## Closing — when to abandon

Memory-os patterns earn their keep inside the envelope. The envelope is in [`envelope.md`](envelope.md). Re-read it once a year. If you're outside the envelope — your corpus has multiple writers, your scale exceeds personal, your model can't iterate on retrieval, your work shape doesn't translate cleanly — switch to the right tool.

Otherwise: let the cron run, capture decisions into `_learnings.md` when they happen, run quality skills on what's about to leave your hands, refactor the vocab every 18–24 months. The system survives your bad weeks. Act like it does.
