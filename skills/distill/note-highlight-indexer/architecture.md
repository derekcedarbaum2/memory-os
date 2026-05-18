# Architecture

Two modes share the same playbook system. The manual paste-in mode is the primary entry point. Readwise auto-processing is optional.

The system is **tool-agnostic** — it works with any coding agent that accepts markdown prompts and has filesystem access (Claude Code, Codex CLI, Codex web, Cursor, Aider, etc.). The diagrams below show Claude Code as the example since it has the cleanest installable-skill story; Codex/other agents follow the same flow with the prompt loaded inline or via a custom-prompt mechanism.

## Mode 1 — Manual paste-in (primary)

```
┌─────────────────────────────────────────────────────────────────┐
│              PASTE INTO YOUR CODING AGENT                       │
│              (Claude Code, Codex CLI, Codex web, etc.)          │
│                                                                 │
│   Article body, essay, transcript excerpt, slide quote,         │
│   book passage, tweet thread, podcast notes, framework,         │
│   Slack message, anything operational and worth keeping         │
└─────────────────────────────────────────────────────────────────┘
                          │
                          │  Claude Code: /playbook-distill
                          │  Codex / other: invoke prompts/playbook-distill.md
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  playbook-distill PROMPT                        │
│  Claude Code: ~/.claude/skills/playbook-distill/SKILL.md        │
│  Codex / other: prompts/playbook-distill.md                     │
│                                                                 │
│   1. Read Vault/Playbooks-Index.md (10-domain taxonomy)         │
│   2. Read pasted content                                        │
│   3. Classify domain → pick primary playbook                    │
│   4. Read target playbook README + relevant topic file          │
│   5. Distill content → operational format:                      │
│        scorecards, decision triggers, anti-patterns,            │
│        fillable templates, reference tables                     │
│   6. Merge into existing topic file (or scaffold new playbook)  │
│   7. Source-tag every claim inline                              │
│   8. Update playbook README "Sources captured" section          │
│   9. Update Vault/Playbooks-Index.md "Active" status            │
│   10. Append entry to Vault/log.md                              │
│   11. Report a one-paragraph summary back to user               │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CONSUMPTION                               │
│                                                                 │
│   Vault/<domain folder>/<Playbook>/                             │
│     ├── README.md          ← task router (which file for which) │
│     ├── topic-1.md         ← operational rules, source-tagged   │
│     ├── topic-2.md                                              │
│     └── ...                                                     │
│                                                                 │
│   Used by:                                                      │
│   - Claude Code skills (load relevant playbook for task)        │
│   - Future paste-in invocations (skill reads existing files     │
│     before merging — no duplication)                            │
│   - Any agent that needs domain context — reads markdown,       │
│     greps if needed                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Mode 2 — Readwise auto-processing (optional)

```
Readwise (web/mobile)                                              ┐
- article highlights                                               │
- book highlights (Kindle, etc.)                                   │
- tweets / PDF annotations                                         │
       │                                                           │
       ▼  (Readwise → Obsidian sync)                               │
Vault/Reading/{Articles,Books,Tweets}/*.md  ────────────────────►  │
                                                                   │
       │  (7:30 AM PT daily — launchd plist)                       │
       ▼                                                           │
~/.claude/hooks/auto-distill-readwise.sh                           │   Same destination
- mkdir-based lockdir at /tmp/auto-distill-readwise.lock.d         │   as Mode 1.
- enumerate Reading folder                                         │
- hash-check vs ~/.claude/state/distilled-readwise.json            │   The auto-distill
- for each unprocessed file → headless `claude -p` invokes:        │   skill is a
                                                                   │   headless variant
       │                                                           │   of playbook-distill —
       ▼                                                           │   same outputs,
auto-playbook-distill SKILL                                        │   no user prompts.
(headless variant of playbook-distill)                             │
- same workflow as manual variant                                  │
- decides routing without confirms                                 │
- writes one-line stdout for cron log                              │
                                                                   │
       │                                                           │
       ▼                                                           │
Vault/<domain folder>/<Playbook>/  ◄────────────────────────────── ┘
```

If you don't use Readwise, ignore this mode entirely. The manual skill stands on its own.

## Components

| Component | Where | Required? | What it is |
|---|---|---|---|
| **Manual skill** | `~/.claude/skills/playbook-distill/SKILL.md` | **Yes** | The paste-in skill — primary entry point |
| **Routing index** | `Vault/Playbooks-Index.md` | **Yes** | The 10-domain taxonomy + routing rules; lives in vault root |
| **Playbook README template** | `vault-templates/playbook-readme-template.md` | **Yes (referenced)** | Used when scaffolding a new playbook for the first time |
| **Operations log** | `Vault/log.md` | **Yes** | Append-only, one line per distill action; grep-friendly |
| Headless skill | `~/.claude/skills/auto-playbook-distill/SKILL.md` | Optional | The Readwise / cron variant |
| Cron runner | `~/.claude/hooks/auto-distill-readwise.sh` | Optional | Bash; iterates Reading folder, invokes headless claude per unprocessed file |
| Cron schedule | `~/Library/LaunchAgents/com.user.auto-distill.plist` | Optional | launchd; fires 7:30 AM PT daily |
| Concurrency lock | `/tmp/auto-distill-readwise.lock.d` | Optional | mkdir-based atomic lock; 2h stale-clean |
| State file | `~/.claude/state/distilled-readwise.json` | Optional | Idempotency tracking for the cron |
| Unrouted queue | `Vault/raw-sources/_unrouted-distill-queue.md` | Both modes | Sources that span 3+ domains or no clear match — manual review |

## The 10 playbook domains

| # | Domain | Typical sources |
|---|---|---|
| 1 | Startup / Business Building | YC analyses, founder essays, GTM frameworks, pitch teardowns |
| 2 | Investing / Markets / Finance | Investor biographies, valuation theory, market history |
| 3 | Health / Body / Nutrition / Biomechanics | Nutrition books, exercise science, sleep, longevity |
| 4 | Parenting / Kids / Education | Doman, Montessori, Waldorf, child development |
| 5 | Writing / Communication / Voice | Pinker, Strunk & White, copywriting, rhetoric |
| 6 | Philosophy / Mental Models | Decision theory, epistemology, ethics, schools of thought you read |
| 7 | Politics + Economics / Public Policy | Monetary theory, market design, policy critique, the political/economic authors you read |
| 8 | Leadership + Operating Discipline | Command, coaching, executive cadence, the leadership authors you read |
| 9 | Personal OS / Productivity | Time, attention, habits, knowledge management |
| 10 | Tech / AI / Software / Engineering | AI/ML, agent design, software architecture, dev tooling |

You can edit these in `Playbooks-Index.md`, but resist adding more than 10 — the system depends on a small finite taxonomy. If a paste doesn't fit, the skill confirms with you before doing anything (it doesn't silently invent an 11th).

## Design principles

1. **Filesystem-only.** No vector store, no graph DB, no proprietary index. Markdown files + grep. Letta's 2026 benchmark (74% accuracy on long-conversation memory tasks) and Anthropic's managed-agents post both confirmed filesystem beats specialized memory tools.
2. **Operationalize on capture, not on recall.** The distill step pays the synthesis cost once at write time. Future readers (you or an agent) get pre-cooked rules.
3. **One synthesized knowledge per dimension.** New content merges into existing topic files. Don't append-as-new-file. Splits only when a topic file exceeds ~400 lines.
4. **Source-tag inline.** Every rule ends with `[<title>, <date>]`. Attribution is traceable; stale claims are findable.
5. **Idempotent in cron mode.** Hash check against the state file. Reruns are no-ops unless the source changed.
6. **Single new playbook per run.** If a paste spans multiple new domains, the skill confirms with you before scaffolding. Prevents runaway taxonomy growth.
7. **Routing is transparent.** The 10 domains live in a markdown file you can edit. The decision rule is in the skill prompt, not buried in code.
