# Cron log sample

Sanitized excerpt from `Vault/log.md` showing what the self-healing layer produces in a typical week. Every line is pipe-separated, grep-friendly, append-only.

```
2026-05-17T03:00:00Z | today | regenerate | sections=5 | size=87lines
2026-05-17T11:00:00Z | today | regenerate | sections=5 | size=92lines
2026-05-17T14:30:00Z | auto-distill | processed | source=readwise-2026-05-17-marc-andreessen-tech-policy-essay | playbook=Vault/Company Building/Startup Playbook/gtm-distribution.md | 4-paragraphs-merged
2026-05-17T19:55:00Z | memory-reorg | restructure | subfolders=5 | project-files-migrated=12 | tags-added=30
2026-05-17T20:50:00Z | tag-backfill | one-time | memory-files=30 | vault-files=550 | legacy-tags-dropped=247
2026-05-18T04:05:00Z | cron-added | com.user.weekly-memory-maintenance | Sun 11pm PT
2026-05-18T07:00:00Z | monologue-sync | imported | files=3 | path=Vault/Voice Memos/2026-05-18/
2026-05-18T07:15:00Z | today | regenerate | sections=5 | size=89lines
2026-05-19T22:00:00Z | learnings-resurface | run-summary | window=7d | atoms=412 → clusters=14 → routed=4 (2 principle / 1 commitment / 1 question), 0 queued, 0 contested
2026-05-19T22:08:00Z | learnings-resurface | principle | "Specific dollarized outcomes beat generic credibility ~10x" | mentions=4 ventures=[unlikely-labs, ai-build-partners, neros] | routed → principle_specific_outcomes_beat_generic.md + Startup Playbook/gtm-distribution.md (merged)
2026-05-19T22:09:00Z | learnings-resurface | commitment | "Send Julia Goodman Estivon revised proposal" | mentions=2 | routed → Vault/Ideas/Estivon Agentic Real Estate/_learnings.md Open Threads + Todoist task 8XQp9k
2026-05-19T22:10:00Z | learnings-resurface | open-question | "What's the right pricing floor for Archer-Recon vs. Skydio X10D?" | mentions=3 | routed → Vault/Work/Neros/_learnings.md Open Threads
2026-05-19T22:55:00Z | weekly-memory-maintenance | start
2026-05-19T22:55:30Z | dormancy-decay | mark dormant | Ideas/Aristotle's World/_learnings.md | 94d stale
2026-05-19T22:55:30Z | dormancy-decay | mark dormant | Ideas/Litmus/_learnings.md | 101d stale
2026-05-19T22:56:00Z | active-venture-refresh | summary | pinboard_active=7 demoted=0 warn=1 candidates=2
2026-05-19T22:56:00Z | active-venture-refresh | warn | Estivon | 32d stale | Vault/Ideas/Estivon Agentic Real Estate/_learnings.md
2026-05-19T22:56:00Z | active-venture-refresh | promotion-candidate | Vault/Work/CapitalGrid/_learnings.md | touched 4d ago
2026-05-19T22:56:00Z | active-venture-refresh | promotion-candidate | Vault/Personal Brand/_learnings.md | touched 11d ago
2026-05-19T22:57:00Z | prune-memory-dryrun | summary | critical=0 warning=0 info=1 | MEMORY.md=45/80
```

## What this shows

- The morning chain (voice-memo sync at 7am → Today.md at 7:15am → Readwise distill at 7:30am) runs without intervention.
- Sunday 10pm: `learnings-resurface` clusters a week of accumulated atoms (412 → 14 clusters → 4 routed). One principle promoted across three ventures' worth of evidence. One commitment auto-created as a Todoist task with venture-tagged context. One open question routed to the relevant `_learnings.md`.
- Sunday 11pm: `weekly-memory-maintenance` runs three jobs in sequence. Two dormant projects (Aristotle's World, Litmus) get auto-tagged after 94 and 101 days no touch. One warning about Estivon approaching dormancy (32 days). Two promotion candidates surface without auto-acting.
- Final dry-run audit: clean. MEMORY.md at 45/80 lines.

## What I do with this on Monday morning

Read `Vault/log.md` for entries since last Monday. Takes 90 seconds. Decide:

- The dormant markers: agree (let them stand) or disagree (touch the file to reset). Almost always agree.
- The promotion candidates: promote (move pinboard pointer) or ignore (file is incidental). Maybe 1 in 5 gets promoted.
- The principle promotion: read the merged playbook entry, sanity check the routing, edit if needed.
- The commitment task: confirm it ended up in the right Todoist project.

Total time: 5–10 minutes. The system did 30 minutes of work for me overnight.

## The signal-to-noise ratio matters

The log format is optimized for **scan-ability**. Every line answers "what happened, when, to what, why." Nothing requires opening another tool to interpret. If a line is unclear at 90 seconds, the script is wrong, not the human.

That bar — `grep`-able + scan-able in 90 seconds — is the entire reason I trust this maintenance loop. The moment it stops being readable, I'll stop reading the log, and the day after that the system rot starts.
