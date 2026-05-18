# How to build and run a memory-os vault

You cloned `memory-os`. Now what? This doc answers four questions:

1. What do I do every day, week, and month to keep this thing alive?
2. How do I bootstrap a vault from zero — and what does the first 6 months actually look like?
3. What breaks, and how do I fix it?
4. Which skill do I invoke when?

Read the cheat sheet first if you already know the system. Read the narrative sections if you don't. Skip to "Failure modes" if something is currently on fire.

---

## Cheat sheet

### Daily rituals

| Time | Action | Why |
|---|---|---|
| Morning, automatic | `Vault/Today.md` regenerates at 7:15am, 11am, 2pm, 5pm via cron | Working memory for time-sensitive tasks; never edit by hand |
| Morning, automatic | Voice memos sync from your phone to `Vault/Voice Memos/` at 7:00am | Captures whatever you said into your phone walking the dog |
| Morning, automatic | Readwise highlights auto-distill into domain playbooks at 7:30am | Yesterday's reading becomes today's operational rules |
| Whenever a session ends | Run `/archive-session` | Captures decisions, insights, open threads to `Vault/AI Toolkit/CC Chat History/` |
| Whenever you decide something venture-scoped | Append to that venture's `_learnings.md` — under `## Learnings` or `## Key Decisions` | If you don't write it down, it doesn't compound |
| Whenever you have a thought you need outside your head | Talk to your phone (Monologue or equivalent); it lands in `Vault/Voice Memos/` next morning | Don't trust your brain to remember; trust the substrate |

### Weekly rituals

| When | Action | Why |
|---|---|---|
| Sunday 10pm, automatic | `learnings-resurface` cron clusters the week's session archives + `_learnings.md` + voice memos, classifies by type, routes per type | Cross-corpus pattern detection; principles get promoted, commitments get tasks created |
| Sunday 11pm, automatic | `weekly-memory-maintenance` cron runs dormancy-decay → active-venture-refresh → prune-memory-dryrun | Self-healing: stale ventures decay, stale pinboard entries demote, audit summary lands in `Vault/log.md` |
| Monday morning | Skim `Vault/log.md` from last week (90 seconds) | Decide: agree with demotions? promote any candidates? confirm task creation? |
| Mid-week, on demand | When a doc is shipping to a stakeholder, run `/qa-loop` on it | Three adversarial agents catch real issues; rewrites only what survives |
| Mid-week, on demand | When a written argument is going public (essay, README, pitch), run `/pressure-test` on it | Adversarial personas attack from multiple directions; surfaces the load-bearing weakness |
| Mid-week, on demand | When you've just dumped a lot of voice memos, run `/voice-memo-process` if it didn't auto-fire | Turns ephemeral talk into Todoist tasks or vault notes |

### Monthly rituals

| When | Action | Why |
|---|---|---|
| First Monday of the month | Run `/vault-lint --fix` on the whole vault | Catches drifting frontmatter, broken wiki-links, stale `_learnings.md` files, missing tags |
| First Monday of the month | Skim `INDEX.md` (the cold pointer index) | Things you haven't thought about; sometimes one surfaces as suddenly relevant |
| First Monday of the month | Read your last month of session archive titles | Quick check: am I working on what I said I'd work on? |
| First Monday of the month | Run `/prune-memory` if `MEMORY.md` is approaching 70 lines | Cap is 80; intervene before the cron has to truncate |
| End of month, on demand | Check `Vault/AI Toolkit/agentic-architecture.md` Evolution log | Did any structural changes happen this month? Note them if not already logged |

### Skill decision tree

> **You have a piece of prose or an artifact. You're not sure if it's ready. Pick one:**

```
Is it an ARGUMENT going public (essay, README, public pitch)?
    YES → /pressure-test (4-persona adversarial attack)
    NO  ↓

Is it a DELIVERABLE going to a stakeholder (PRD, proposal, brief)?
    YES → /qa-loop (Finder/Disprover/Referee on substance)
    NO  ↓

Is it WRITING where the substance is right but the prose is soft?
    YES → /sense-of-style (Pinker-grounded line-level rewrite)
    NO  ↓

Is it about the VAULT itself (orphans, broken links, drifting frontmatter)?
    YES → /vault-lint (--fix for safe categories)
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
| Multiple humans writing into the same corpus | Pick one taxonomic owner or use a vector store; don't try to enforce controlled vocab across writers |
| Work that's identity-changing and invalidates 80% of your taxonomy | Pause; consider whether memory-os fits the new shape before forcing it |

### Failure-mode quick triage

| Symptom | Likely cause | Quick fix |
|---|---|---|
| Cron didn't run Sunday night | Lockdir left over from a crashed run | `rm -rf /tmp/weekly-memory-maintenance.lock`, re-run manually |
| `MEMORY.md` jumped to 100+ lines silently | Hot pinboard accumulating; cron didn't catch it | Run `/prune-memory`; demote stale entries to INDEX.md by hand |
| Wiki-links suddenly broken everywhere | Renamed a file without updating references | `grep -r "\[\[old-name\]\]" Vault/` and fix the survivors |
| Half my pinboard auto-demoted to dormant | You took a long break or changed roles | This is the system telling you something. Honor it or `touch` the files you actually want to keep active |
| Tag drift mid-quarter (tags getting added ad hoc) | Adding new tags inline without updating `tag-vocabulary.md` first | Run `/vault-lint`, audit unknown tags, decide which to canonicalize and which to retag |
| Year 2-3 vocabulary fossilization | The taxonomy no longer carves nature at its joints | See the **Annual vocab refactor** section below — it's a feature, not a failure |

---

## Narrative: the rituals

### Daily

The morning chain runs without you. By 7:30am your vault has: yesterday's voice memos turned into tasks or notes, a regenerated `Today.md` with calendar + due Todoist items + recent open threads, and the day's Readwise highlights distilled into the right domain playbook.

Your job in the morning is to read `Today.md`. That's it. Read it once around 9am and once around 2pm. It will tell you what's on fire.

Your job during the day is to capture into the right place. Two rules:

- **A thought that's venture-scoped goes into that venture's `_learnings.md`.** Under `## Learnings` if it's an insight; under `## Open Threads` if it's a question; under `## Key Decisions` if you've decided something with a binary outcome. Always cite the source — at minimum a date, ideally a session ID once `/archive-session` has run.
- **A thought that's not venture-scoped goes into a voice memo.** Walk outside, talk into your phone, forget about it. The morning cron handles the rest.

End-of-session, run `/archive-session`. It snapshots the conversation, extracts decisions and insights and open threads, writes a session archive to `Vault/AI Toolkit/CC Chat History/`, updates the project index, and rolls fresh insights into the cumulative learnings file. The skill takes 30 seconds. Skipping it loses you the compounding effect entirely. Don't skip it.

### Weekly

Sunday night, the system audits itself. Two crons fire — `learnings-resurface` at 10pm and `weekly-memory-maintenance` at 11pm — and by Monday morning `Vault/log.md` has the audit trail. Read it Monday before opening anything else. It takes 90 seconds.

You're looking for:

- **Promotion candidates.** Files the cron noticed you've been touching frequently but that aren't on your `MEMORY.md` hot pinboard. Promote (move the pointer to `MEMORY.md`), ignore (file is incidental), or leave for next week. Maybe 1 in 5 gets promoted.
- **Demoted ventures.** Files that have gone dormant. Agree (let it stand) or disagree (touch the file to reset the clock). Almost always agree.
- **Routed principles.** Cross-corpus patterns the cron promoted into your playbook. Read the new entry, sanity-check the routing, edit if needed.
- **Auto-created Todoist tasks.** Commitments the cron extracted from session archives. Confirm they ended up in the right project; rephrase if the auto-generated title is rough.

Mid-week, the on-demand skills earn their keep. `/qa-loop` before you send a PRD to engineering. `/pressure-test` before you publish a public argument. `/sense-of-style` before you publish prose where the substance is solid but the lines are soft. Don't run all of them on everything — that's noise. Pick the one whose specific incentive matches what the artifact needs.

### Monthly

The first Monday of the month is hygiene day. Block 30 minutes. In order:

1. **`/vault-lint --fix`** on the whole vault. Catches drifted frontmatter, broken wiki-links, stale `_learnings.md`, missing tags. Auto-fixes the safe categories with your approval.
2. **Skim `INDEX.md`** (the cold pointer index). Things you haven't thought about. Sometimes one surfaces as suddenly relevant — promote it to `MEMORY.md`.
3. **Read your last month of session archive titles.** Are you working on what you said you'd work on? If not, why? Adjust the active-venture pinboard.
4. **Run `/prune-memory`** if `MEMORY.md` is creeping past 70 lines. The cap is 80, and the cron will warn you, but you'd rather intervene yourself than have entries auto-demoted.
5. **Glance at `agentic-architecture.md`'s Evolution log.** Did anything structural change this month that didn't get logged? Add a backfill entry.

Monthly hygiene is the difference between a vault that compounds for two years and a vault that rots in six months. Don't skip it.

---

## Narrative: bootstraps

### Starting from zero — a new vault

A common failure mode for adopters is to clone `memory-os`, expect the system to work on day one, and abandon it when the agent's first session doesn't feel transformed. This is the deferred-payoff problem: memory-os doesn't pay value linearly from day one like a vector store does. It pays asymptotically — close to zero in week one, useful by month two, dominant by month six.

**Week 1 — Substrate setup.**
- Set up your Markdown vault (Obsidian recommended, but any folder of `.md` files works).
- Drop in the `vault/` reference docs from `memory-os` so the conventions are visible.
- Create the top-level folders: `Work/`, `Ideas/`, `Personal/`, `Writing/`, `Reading/`, `AI Toolkit/`, `Company Building/`, `_archive/`.
- Set up your `CLAUDE.md` at the vault root pointing the agent at the conventions.
- Set up `MEMORY.md` in your Claude Code memory directory with the hot-pinboard template (see `vault/memory-protocol.md`).
- Tag every file you write going forward with controlled-vocab tags. Empty `tags: []` is an enforced error.

The vault is basically empty. The agent has no context yet. This is expected.

**Week 2 — Start populating.**
- Pick your three most active engagements. Create a folder for each under `Work/` or `Ideas/`. Create a `_learnings.md` in each from `vault/learnings-template.md`.
- Start using `/archive-session` after every Claude Code session.
- Run a voice-memo sync if you have a service like Monologue. If not, manually capture thoughts into a `Voice Memos/` folder.
- Don't worry yet about the principle layer or cross-corpus reconciliation. Just write decisions and learnings into the venture `_learnings.md` as they happen.

**Month 1 — Tag vocab and pinboard.**
- By now you should have 20-30 `_learnings.md` files and a couple dozen session archives.
- Audit your tags. Add to `tag-vocabulary.md` if you're using terms not in the controlled set. The vocab is yours; the discipline is the convention.
- Set up your `MEMORY.md` active-venture pinboard with the 5-7 you actually work on. The rest are cold pointers in `INDEX.md`.
- Install the weekly cron (`weekly-memory-maintenance.sh` + the launchd plist) so Sunday-night maintenance starts running.
- Don't expect the cron to do anything dramatic yet — there's not enough corpus to find patterns in.

**Month 3 — Pattern surfacing.**
- The weekly cron should now find real things. Cross-venture principles surface in `Vault/log.md` Monday mornings.
- Promote 2-3 of these principles to inline rules in `MEMORY.md`. They should be decision-time-load-bearing — fire on every relevant task.
- Run `/prune-memory` and `/vault-lint --fix` for the first time. Expect a lot of small issues to surface; spend an afternoon cleaning them up. After this, monthly maintenance gets fast.

**Month 6 — Compounding.**
- ~80 `_learnings.md` files. Twenty inline principles or so. Hot pinboard saturated at 7-8 active ventures. Cold index has dozens of locations.
- The cron now produces signal-dense weekly summaries. 90 seconds of Monday reading and you know what changed.
- The agent now starts every session already knowing your ventures, preferences, current open threads, and the principles you've accumulated.
- This is when memory-os pays back. Year-one Derek had to re-explain himself every session. Month-six Derek's agent starts warm.

If you abandon the system in week 4 because it doesn't feel transformative yet, you've abandoned it on the steepest part of the deferred-payoff curve. The value is on the far side of that valley, not in week one.

### Starting a new venture inside an existing vault

When you start a new venture or engagement, the bootstrap is much smaller. The convention does most of the work.

1. **Pick the right parent folder.** `Work/` for paid engagements; `Ideas/` for pre-revenue ventures; `Personal/` for life stuff. If it doesn't fit any of these, you might be over-categorizing — just put it in `Ideas/` and let it earn a graduation later.
2. **Create the venture folder.** Folder name = the venture name, no boilerplate.
3. **Create `_learnings.md`** from `vault/learnings-template.md`. Set the frontmatter:
   - `title`: `<venture> — Learnings`
   - `tags`: `[venture:<slug>, kind:state, decay:high]`
   - `classification`: usually `internal` or `confidential` depending on whether it's a client engagement
4. **Write the status snapshot.** One paragraph. What is this venture? Who's involved? What's load-bearing right now? Update this section in place over time; it's the only section that's not append-only.
5. **Add to `MEMORY.md` pinboard** if this is one of your active engagements. Otherwise add to `INDEX.md` cold pointers.
6. **Optionally create `_strategy.md`** as a sibling file if there's a durable strategic anchor (5-field strategy template, North Star, etc.). The `_strategy.md` doesn't change much; the `_learnings.md` accumulates.
7. **Optionally create subfolders** as work happens. Don't pre-build them. `Meetings/`, `Research/`, `Deliverables/` accrete naturally when there's actual content to put in them. Build the folders when you have files to put in them, not before.

The new-venture bootstrap takes ~5 minutes. The conventions are doing the heavy lifting.

---

## Narrative: failure modes and recovery

### "My Sunday cron didn't run"

Cause is almost always a leftover lockdir from a crashed previous run. The wrapper script uses `mkdir`-based locking with a stale-lock cleanup at 2 hours, but if your machine was asleep at the auto-clean window, the lock can persist.

Fix:
```bash
rm -rf /tmp/weekly-memory-maintenance.lock
bash ~/.claude/hooks/weekly-memory-maintenance.sh
```

Check `~/.claude/logs/weekly-memory-maintenance.log` for the actual error. If a Python script crashed, the underlying file system state is fine (the scripts are idempotent) — just rerun.

### "MEMORY.md is over 80 lines and the cron didn't catch it"

Likely cause: the prune-memory cron runs in dry-run only — it audits and warns but doesn't auto-trim. You need to intervene.

Fix: run `/prune-memory` interactively. The skill surfaces:
- Duplicates with CLAUDE.md (delete)
- Entries that should be in INDEX.md instead of MEMORY.md (demote)
- Stale entries (review with you)

If `MEMORY.md` is creeping over 80 chronically, that's a signal you're trying to put too much on the hot pinboard. Demote ruthlessly. The pinboard is for the 5-7 things you actually need in every session — not 30.

### "Wiki-links are suddenly broken across the vault"

You renamed a file without updating references. Or moved a file to `_archive/` without re-routing.

Fix:
```bash
grep -r "\[\[old-name\]\]" "/path/to/Vault/" | head
```

Then either rename the link target back, or do a vault-wide find-replace to update references. `/vault-lint` will surface the broken links as warnings; the auto-fix is suggestive only — it proposes the most likely correct target but won't write the fix.

### "Half my pinboard auto-demoted to dormant"

Two possibilities. One: you took a long break (vacation, illness, family) and the 90-day dormancy clock caught up. Two: you changed roles and the venture taxonomy is genuinely out of date.

If it's a break: just `touch` the files you actually want active, or edit them to reset the clock. The cron is mechanical and doesn't know context.

If it's a role change: this is the system telling you something. Resist the urge to override. Spend 30 minutes asking: which of these ventures are dead, which are paused-but-real, which are truly active under the new shape? Then rebuild the pinboard with the survivors.

### "Tag drift mid-quarter"

You've been adding ad-hoc tags inline instead of canonicalizing them in `tag-vocabulary.md`. The audit catches it.

Fix:
1. Run `/vault-lint` to surface the unknown tags.
2. For each unknown tag, decide: add to vocabulary, or rewrite the entries that use it to use a canonical tag.
3. Update `tag-vocabulary.md` first, then use the new tag — never inline, then retrocanonical.

If you find yourself adding 3+ new tags a month, the vocabulary itself may be drifting. Time for the annual refactor (see below) earlier than scheduled.

### Annual vocab refactor (year 2-3)

This is the big one. The repo's `envelope.md` is honest about it: a controlled vocabulary survives roughly 18-24 months of stable cognitive frame. After that, the corpus contains ventures the original taxonomy didn't anticipate, role changes that reshape which domains discriminate, and semantic drift in what counts as a "principle" vs. "state" vs. "identity."

The refactor playbook:

1. **Block a weekend.** Don't try to do this in pieces. It's a single coherent surgical pass.
2. **Audit current tag usage.** Run a `grep -c` over each tag in `tag-vocabulary.md`. Tags with <5 uses are probably dead. Tags with >100 uses are probably non-discriminating.
3. **Draft the new vocabulary.** Add new namespaces or values that the last 12 months of work would have wanted. Mark old values as deprecated but don't delete yet.
4. **Write a migration script.** Extend `tag-backfill.py` to map old tags to new tags. Run in dry-run first. Inspect the diff. Run for real.
5. **Update `tag-vocabulary.md`** to reflect the new state. Remove deprecated values.
6. **Run `/vault-lint --fix`** to catch any lingering references to old tags.
7. **Log the refactor** as an Evolution log entry in `agentic-architecture.md`. Note what changed, why, and what the next refactor will likely need to address.

The refactor takes a weekend every 24 months. That's much cheaper than re-embedding a vector store every 6 months, which is the equivalent maintenance cost on the other architecture.

If you ever find yourself doing the refactor *quarterly*, the system is wrong for your work. Either your work is changing faster than any taxonomy can keep up (consider a hybrid graph-extraction layer) or you're over-engineering the vocab. Step back.

---

## Closing — when to abandon

Memory-os patterns earn their keep inside the envelope. The envelope is in `docs/envelope.md` and it's load-bearing. Re-read it once a year. If you're outside the envelope — your corpus has multiple writers, your scale exceeds personal, your model can't iterate on retrieval — switch to the right tool.

Otherwise, do the rituals, run the cron, refactor at year 2-3, and let the compounding work.
