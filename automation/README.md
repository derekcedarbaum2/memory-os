# automation/ — the self-healing layer

This folder is the load-bearing evidence for the "self-maintaining" claim in the master [README](../README.md). Every script here runs on a cron schedule against a working vault and a working memory directory. They are short, readable, and idempotent. Together they do roughly 30 minutes of vault maintenance every week without asking.

## What runs when

| Schedule | Script | Purpose |
|---|---|---|
| **Sunday 10:00 PM PT** | [`learnings-resurface.sh`](learnings-resurface.sh) | Cross-corpus pattern reconciliation. Clusters session archives + `_learnings.md` + voice memos, classifies by type, routes per type. |
| **Sunday 11:00 PM PT** | [`weekly-memory-maintenance.sh`](weekly-memory-maintenance.sh) | Wrapper for the three jobs below. Fires after `learnings-resurface` so it sees freshly-routed state. |
| └ inside the wrapper | [`dormancy-decay.py`](dormancy-decay.py) | Marks vault `_learnings.md` as `status:dormant` if no touch in 90 days. |
| └ inside the wrapper | [`active-venture-refresh.py`](active-venture-refresh.py) | Demotes stale `MEMORY.md` pinboard entries to `INDEX.md`. Surfaces promotion candidates without auto-promoting. |
| └ inside the wrapper | [`prune-memory-dryrun.py`](prune-memory-dryrun.py) | Headless audit of the memory dir against the new structure. Appends summary to `Vault/log.md`. |
| **Daily 7:00 AM PT** | external | Voice-memo sync (Monologue → vault). |
| **Daily 7:15, 11, 14, 17 PT** | [`generate-today.sh`](generate-today.sh) | Regenerates `Vault/Today.md` (calendar + due tasks + recent activity + open threads). |
| **Daily 7:30 AM PT** | [`auto-distill-readwise.sh`](auto-distill-readwise.sh) | Distills the day's Readwise highlights into the right domain playbook. |
| **Sunday 9:00 PM PT** | [`tweet-pipeline/pull.py`](tweet-pipeline/) | Pulls x.com URLs shared in your Slack workspace, scrapes the full tweet bodies with cookies imported from your real browser, topic-routes into `Vault/Research/X Research/tweets-*.md`. |

The launchd plists for each schedule live in [`plists/`](plists/). They are macOS-specific. The shell scripts are portable; the schedulers are not.

## Hand-runnable utilities (no schedule)

- [`tag-backfill.py`](tag-backfill.py) — one-time idempotent script that walks the memory dir + vault and fills in controlled-vocabulary `tags:` based on path conventions. Re-runnable. Used once after the May 2026 reorg to backfill ~30 memory files + 550 vault files in one pass.
- [`archive-session.sh`](archive-session.sh) — SessionEnd hook that snapshots a Claude Code session into `Vault/AI Toolkit/CC Chat History/`.
- [`tweet-pipeline/import_cookies.py`](tweet-pipeline/import_cookies.py) — one-time setup + recurring auth refresh for the tweet pipeline. Lifts `x.com` cookies from your real browser (Chrome / Safari / Brave / Firefox) and saves them as a Playwright `storage_state.json`. Re-run when X invalidates the session.

## Why the schedule looks like this

**Sunday late evening** is the lowest-conflict window for a personal vault — no live editing, no meetings, no concurrent voice-memo processing. The two jobs running back-to-back (resurface at 10pm, maintenance at 11pm) give a clean state Monday morning.

**Daily-morning** crons fire before the working day starts so the vault is current when the first session of the day opens. Today.md regenerates four times daily so afternoon sessions don't drift.

## The five-step orchestrator pattern (used by `learnings-resurface.sh`)

The most architecturally interesting of the scripts is `learnings-resurface.sh`. It demonstrates a decomposition pattern: split a long-running agent job into three deterministic shell steps and two judgment-bearing model calls.

```
┌──────────────┐     ┌────────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌─────────────┐
│ 1. Enumerate │ ──▶ │ 2. Phase A     │ ──▶ │ 3. Pre-route │ ──▶ │ 4. Phase B      │ ──▶ │ 5. Finalize │
│   (bash,     │     │ (Claude:       │     │ guard        │     │ (Claude:        │     │ (bash,      │
│   no LLM)    │     │  cluster +     │     │ (bash, no    │     │  route + log)   │     │  no LLM)    │
│              │     │  classify)     │     │  LLM)        │     │                 │     │             │
└──────────────┘     └────────────────┘     └──────────────┘     └─────────────────┘     └─────────────┘
```

- Steps 1, 3, 5 are deterministic: file enumeration, idempotency filtering, log roll-up. Bash, fast, free.
- Steps 2 and 4 are judgment-bearing: clustering patterns and routing them per type. These are the only parts that need a frontier model.
- Each step writes a JSON file under `~/.claude/state/learnings-resurface/runs/<run-id>/`. If any step fails, the run is resumable from the last completed JSON.

This pattern — *judgment compressed, surrounded by deterministic scaffolding* — is the only way to keep agent costs sane and reliability acceptable for long-running jobs. memory-os generalizes it across every cron job that does more than one thing.

The deeper write-up is in [`../skills/distill/learnings-resurface/`](../skills/distill/learnings-resurface/) — the full skill spec for the judgment steps.

## What these scripts do NOT do

- **They do not promote anything to the hot pinboard automatically.** Promotion is always human-reviewed. The `active-venture-refresh.py` surfaces *candidates* to `Vault/log.md`; a human reads the log and decides.
- **They do not delete files.** Ever. Dormancy adds a frontmatter tag; archival moves a folder. Hard deletion is always manual.
- **They do not rewrite `_learnings.md` content.** Append-only is a vault invariant; the scripts respect it.
- **They do not run during the daily 7am window.** That window is reserved for the morning sync chain (voice memo → today regenerate → readwise distill). The maintenance jobs are kept at Sunday late evening to avoid cross-cron file-write conflicts.

## Concurrency

Each script uses an `mkdir`-based lockdir in `/tmp/`. If a previous run is still in flight (or crashed without cleaning up), the new run either waits or exits cleanly with a warning. Stale locks older than 2 hours are auto-cleaned. This pattern is documented in [`../skills/memory/vault-conventions/`](../skills/memory/vault-conventions/).

## Logging convention

Every script appends to `Vault/log.md` in a single canonical format:

```
YYYY-MM-DDTHH:MM:SSZ | <script-name> | <event-type> | <body>
```

Pipe-separated for `grep -F | cut -d'|' -f2 | sort | uniq -c`. Grep-friendly trumps human-friendly here — the log is read by `awk` more than by humans.

## A note on running these yourself

These scripts assume:

1. A vault at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault/`. Hard-coded path.
2. A memory dir at `~/.claude/projects/<project-id>/memory/` with the subfolder layout described in [`../vault/memory-protocol.md`](../vault/memory-protocol.md).
3. `python3` and `bash` on PATH.

If you adopt memory-os, you will edit the hard-coded paths to match your own vault location. That is intentional — the configuration *is* the artifact, and it should be visible in the code, not abstracted into a config file you never look at.
