# memory-os

**An operating system for an AI agent's long-term memory — written in Markdown, run on your filesystem, maintained by cron jobs you can read.**

Frontier labs are racing to ship the *storage* layer for AI memory. ChatGPT has Memory. Claude Code has the memory directory. Cursor has Project Rules. Anthropic shipped Skills this year. Inside the next 18 months that layer will be commodity, and the *slots* on top of it — `decay:` as a setting, "always loaded" as a toggle, controlled-vocab tag namespaces, cross-session reconciliation — will be table stakes for any agent platform that wants to keep paying users.

What labs cannot give you is the filled-in version of those slots. The moat is not the architecture; it is the accumulated corpus you have already curated by the time the platforms hand you a settings panel. Two years from now, when your AI assistant offers a "set decay schedule" dropdown, the people who have 150 hand-tagged `_learnings.md` files with stable vocabularies will out-compound the people starting from zero. The work is what compounds.

`memory-os` is one worked example of how to do that work — a snapshot of one knowledge worker's operating manual for the 18–24 month transition window before platform parity arrives. The substrate is filesystem-native and platform-portable, so when the parity lands, the corpus comes with you. It is what runs my actual day-to-day knowledge work — Product Management at Red 6 Aerospace, consulting at Unlikely Labs, four side ventures, and a household — across roughly 700 Markdown files in an Obsidian vault that a Claude Code agent reads from and writes to constantly.

Everything in this repo is plain Markdown, plain text, plain Python, plain bash. No vector database. No SaaS. No proprietary format. You could read it with `cat` and grep it with `grep`. That is the point.

---

## What's in here

```
memory-os/
├── docs/                       The argument + how to actually run this
│   ├── HOW-TO.md                  Daily/weekly/monthly rituals, bootstraps, failure modes, skill decision tree
│   ├── thesis.md                  Writing-layer over retrieval-layer (long-form)
│   ├── why-not-vectors.md         Where Mem0 / Letta / Zep / Cognee win, and where they lose
│   └── envelope.md                When this approach works and when it doesn't
│
├── vault/                      The conventions
│   ├── conventions.md             Folder structure and naming
│   ├── frontmatter-schema.md      YAML schema for every .md file
│   ├── tag-vocabulary.md          Controlled vocab (kind, decay, venture, domain, status)
│   ├── memory-protocol.md         Hot pinboard + cold index + subfolder taxonomy
│   └── learnings-template.md      Append-only per-venture knowledge file template
│
├── skills/                     The judgment layer
│   ├── memory/                    Three-tier memory pattern, frontmatter discipline, weekly audit
│   ├── quality/                   Adversarial trio (qa-loop), Pinker-grounded prose review
│   ├── distill/                   Readwise → playbook distillation, cross-venture pattern surfacing
│   └── meta/                      Living architecture map, deterministic CLI primitives
│
├── automation/                 The self-healing layer
│   ├── weekly-memory-maintenance.sh  Wrapper — runs the three jobs below every Sunday at 11pm
│   ├── dormancy-decay.py             Marks _learnings.md as dormant after 90 days no touch
│   ├── active-venture-refresh.py     Demotes stale pinboard entries → cold index
│   ├── prune-memory-dryrun.py        Weekly memory health audit
│   ├── tag-backfill.py               Idempotent controlled-vocab tag enforcement
│   ├── learnings-resurface.sh        Weekly cross-corpus pattern detection
│   └── plists/                       launchd configs for macOS
│
└── examples/                   Sanitized worked output
```

## The argument in one paragraph

A capable model with a lived-in Markdown vault and shell access does not need vector search to remember. It needs (a) a folder structure that mirrors how a knowledge worker actually thinks, (b) frontmatter that lets `grep` do the indexing job, (c) a small library of operating heuristics — promote what fires across multiple sessions, decay what hasn't been touched in a quarter, separate state from pattern — and (d) a few hundred lines of cron-driven Python and bash to enforce all of the above while you sleep. The substrate is filesystem-native, the retrieval is `grep`, the audit trail is `git log`, and the agent's actions land as diffs you can read on a phone. That is the entire moat. Everything else is implementation detail.

Long-form: [`docs/thesis.md`](docs/thesis.md).

## Evidence: the self-healing layer

The strongest claim memory-os makes is *self-maintaining*. That claim is concrete. Here is what the weekly cron does every Sunday at 11pm PT, after a separate cross-corpus reconciliation pass at 10pm:

1. **Dormancy decay** ([`automation/dormancy-decay.py`](automation/dormancy-decay.py)) scans every `_learnings.md` in the vault. Any with no edit in 90 days gets `status:dormant` added to its frontmatter. One line per change appended to `Vault/log.md`.
2. **Active-venture refresh** ([`automation/active-venture-refresh.py`](automation/active-venture-refresh.py)) reads the "Active ventures" section of `MEMORY.md` (the hot pinboard, always loaded into the agent's context). Pinboard entries whose `_learnings.md` has 90+ days of dust get demoted to the cold `INDEX.md`. Non-pinboard files touched in the last 14 days get surfaced as promotion candidates — but never auto-promoted; that is a judgment call.
3. **Prune-memory dry-run** ([`automation/prune-memory-dryrun.py`](automation/prune-memory-dryrun.py)) audits the memory directory: line counts vs. the 80-line cap on the hot pinboard, subfolder/filename consistency, tag-vocabulary compliance, deprecated patterns. Summary line written to `Vault/log.md` so Monday morning shows last night's findings without me opening a tool.

None of these scripts make creative decisions. They demote, they decay, they surface, they log. Promotion and rewriting stay manual. The agent's hot context tightens automatically; nothing important is touched without me.

Sanitized cron output: [`examples/cron-log-sample.md`](examples/cron-log-sample.md).

## Who this is for

It is not a product. It is not a framework you install. It is one knowledge worker's operating system, in public, so other knowledge workers can see one way to do this and steal the parts that fit.

You will get the most out of it if you:

- Already use a Markdown vault (Obsidian, Foam, plain folders).
- Already use an agent that can read and write to your filesystem (Claude Code, Codex CLI, similar).
- Have hit the wall where every new session starts cold — re-explaining context, re-asserting preferences, re-remembering which folder a project lives in.
- Are skeptical of "AI memory" SaaS that puts a vector DB between you and your own notes.

You will probably not get much out of it if:

- You don't have a vault. (Build one. Two weeks of friction, then you will not go back.)
- You need multi-tenant, many-users-writing-to-one-corpus retrieval. (That is what vector DBs are for. Read [`docs/envelope.md`](docs/envelope.md).)
- You want a clean install path with `pip install`. (There isn't one, and there shouldn't be. The configuration *is* the artifact.)

## Why the prose is so direct

I am Derek Cedarbaum. I'm a Product Manager at Red 6 Aerospace, a defense AR-training startup. I also run Unlikely Labs, a small AI consultancy. I write the way I talk: first-principles, no corporate cushioning, occasional profanity in the source material I haven't sanitized for this README. If you want a corporate-AI-vendor pitch, this is not that.

The repo absorbs and supersedes twelve smaller repos I shipped between February and May 2026. Those are archived; their READMEs are preserved as section content inside the four buckets. The full history is in `git log`.

## License

MIT. See [LICENSE](LICENSE).

## Further reading

- [`docs/HOW-TO.md`](docs/HOW-TO.md) — daily/weekly/monthly rituals, bootstraps from zero, failure modes, the skill decision tree
- [`docs/thesis.md`](docs/thesis.md) — the long-form argument
- [`docs/why-not-vectors.md`](docs/why-not-vectors.md) — direct comparison with the vector-DB memory category
- [`docs/envelope.md`](docs/envelope.md) — when this works and when it doesn't
- [`vault/`](vault/) — the conventions in canonical form
- [`skills/`](skills/) — the judgment layer, organized into four buckets
- [`automation/`](automation/) — the self-healing layer
- [`examples/pressure-test-on-self.md`](examples/pressure-test-on-self.md) — the repo's own adversarial review and the rewrites that resulted
