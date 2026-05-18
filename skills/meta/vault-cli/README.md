# vault-cli · Deterministic primitives for AI agents

> **Want to install the whole 12-repo ecosystem?** Paste [this prompt](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/INSTALL-PROMPT.md) into your Claude Code or Codex session — it interviews you, installs in phases, runs smoke tests, and pauses for confirmation between phases. Or browse the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) first.


**A small command-line tool that lets your AI agent do the boring, repetitive work safely — instead of asking the LLM to do it every time.** The LLM does only judgment; the CLI does the deterministic mutations. Part of [the writing-layer-over-retrieval-layer thesis](https://github.com/derekcedarbaum2/claude-code-setup#the-thesis-writing-layer-over-retrieval-layer).

> **New to Claude Code?** [Claude Code](https://docs.anthropic.com/claude/code) is Anthropic's command-line AI agent — like ChatGPT, but in your terminal, able to read/write files and run commands. The patterns in this repo assume you're running it (or [Codex CLI](https://github.com/openai/codex)). See the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) — full system overview + onboarding sequence — or [`claude-code-setup`](https://github.com/derekcedarbaum2/claude-code-setup) for the umbrella reference doc. Vocabulary used here (skill, hook, vault, etc.) is defined in the [glossary](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/GLOSSARY.md).

---

## The problem

If you've been using Claude Code (or any AI agent) seriously, you've probably hit this pattern: you keep asking the AI to do small, mechanical tasks. *"Look up which file holds my Bastion notes." "Add this learning to the right file." "Make a new skill folder with the standard structure."*

These tasks have two failure modes when the AI does them:

1. **Slow and expensive.** The AI loads context, reads files, thinks, and writes — all at LLM speed. For something that's really just `grep` and `mkdir`, that's overkill.
2. **Sometimes wrong.** The AI may forget a step, miscount, write to the wrong path, or break an "append-only" rule. Once in a while, that costs you real work.

The fix: do the **mechanical** parts in a script (always the same, fast, testable), and let the AI do only the **judgment** parts (which file is the right home? is this insight a principle or a state observation?). That split is the architecture.

`vault-cli` is the script half. It's a single command-line tool — `vault` — that exposes every mechanical operation your AI agent might want, as a clean subcommand. Your agent calls `vault <command>` for anything mechanical; you can also run those commands yourself for debugging.

> **You don't use this directly day to day. Your AI does.** The CLI is the plumbing; you still talk to Claude Code as normal. The only place you'd touch `vault` directly is debugging or one-off ops.

> **Architectural inspiration: [Garry Tan's `gbrain`](https://github.com/garrytan/gbrain).**
> The "thin harness, fat skills" ethos, the skillify pipeline pattern (`skill new` / `skill check`), the `AGENTS.md` + `llms.txt` agent-installable repo standard, and the JSON-on-non-TTY output convention are patterns gbrain crystallized. `vault-cli` is independent code (pure Node.js, no shared implementation) targeting a different scope — vault-specific primitives for a Claude Code setup, not a general agent brain. See [Credits](#credits) at the bottom.

---

## What you get

Before:

```
~/.claude/hooks/auto-distill-readwise.sh    ← bash, scattered
~/.claude/hooks/learnings-resurface.sh      ← bash, scattered
~/.claude/hooks/archive-session.sh          ← bash, scattered
~/scripts/monologue-sync.sh                  ← bash, in a different folder
... plus deterministic logic embedded inside SKILL.md files,
    where the LLM does the work at inference time (slow, expensive, sometimes wrong)
```

After:

```
vault distill run [--dry-run] [--backfill]
vault distill state get
vault resurface run [--window N]
vault session archive
vault session list [--limit N]
vault voice-memo list [--unprocessed]
vault router lookup "PRD review"
vault router check                             ← validates every Knowledge Router pointer resolves
vault frontmatter audit
vault frontmatter add <file>
vault learnings append <venture> "<entry>"
vault learnings decision <venture> "<entry>"
vault learnings open-thread <venture> "<question>"
vault skill new <name>                          ← scaffolds the standard folder structure
vault skill check <name>                        ← validates against the conformance standard
vault skill list
vault state list / get
vault today path | read | stale | regenerate    ← ephemeral working-memory artifact (Today.md)
```

Skills become 60% shorter. Deterministic ops are testable without the LLM. The deterministic-vs-judgment boundary stops being a *principle* you're aiming at and becomes a *constraint* enforced by the architecture.

---

## What v0.1 ships

| Group | Native impl | Wraps existing script |
|---|---|---|
| `vault distill` | state ops | `auto-distill-readwise.sh` |
| `vault resurface` | state ops | `learnings-resurface.sh` |
| `vault session` | list | `archive-session.sh` |
| `vault voice-memo` | list, get | (none — read-only) |
| `vault router` | **lookup, list, check** (all native) | — |
| `vault frontmatter` | **check, audit, add** (all native) | — |
| `vault learnings` | **append, decision, open-thread** (native, append-only enforced) | — |
| `vault skill` | **new, check, list** (all native) | — |
| `vault state` | list, get | — |
| `vault today` | **path, read, stale** (all native); regenerate wraps `generate-today.sh` | `generate-today.sh` |

The wrapped commands keep your existing skills/hooks/crons working unchanged. The native commands are the new surface — `skill scaffold/check`, `frontmatter audit/add`, `router check`, `learnings append`. Migrate skills to call the CLI as you touch them, not before.

---

## `vault today` — ephemeral working-memory primitive

`Today.md` is a regenerated derived view of "what is true right now" — calendar, open commitments, last-24h voice memos, Open Threads from active venture `_learnings.md` files. **Not memory.** Memory persists; Today.md is overwritten every regen cycle. Sibling artifact to `Playbooks-Index.md` (also regenerated, by `note-highlight-indexer`).

The `today` group is the cleanest demonstration of the deterministic-vs-judgment split that motivates this CLI:

| Subcommand | Layer | What it does |
|---|---|---|
| `vault today path` | deterministic | Resolve and print the path |
| `vault today read` | deterministic | Cat the file (with `--json` for size/mtime metadata) |
| `vault today stale [--max N]` | deterministic | Exit 1 if Today.md older than N hours (default 6) |
| `vault today regenerate` | wraps | Shells out to `~/.claude/hooks/generate-today.sh`, which invokes the `today` skill via headless `claude -p` to do the LLM aggregation |

Skills that need current state should `vault today stale` first; if non-stale, `vault today read`. If stale, either accept the staleness or `vault today regenerate` and re-read.

---

## Install

Requires **Node.js 22+** (already installed on most modern macOS setups).

```bash
git clone https://github.com/derekcedarbaum2/vault-cli.git
cd vault-cli
npm link    # creates a global `vault` symlink in your $PATH
```

Verify:

```bash
vault --version
vault --help
vault router check
```

If `npm link` requires sudo on your system, alternatives:
- `cp -r vault-cli ~/.local/share/ && ln -s ~/.local/share/vault-cli/src/cli.js ~/.local/bin/vault`
- Add `~/Library/<wherever>/vault-cli/src/cli.js` directly to your `$PATH`.

---

## Configuration

The CLI auto-discovers paths so most users need zero configuration. Override only if your setup is unusual:

| Variable | What it does |
|---|---|
| `VAULT_PATH` | Override the auto-discovered vault root. Defaults probed: `$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault` (Obsidian iCloud), `$HOME/Documents/Vault`, `$HOME/vault`, `$HOME/notes`. The first one with a `CLAUDE.md` wins; otherwise the first existing directory. |
| `CLAUDE_HOME` | Override `~/.claude` (almost never needed) |
| `VAULT_MEMORY_DIR` | Override the auto-discovered memory dir. Default: most-recently-modified `~/.claude/projects/*/memory/` containing `MEMORY.md`. |

Add to `~/.zshrc` or `~/.bashrc` if you need to override.

---

## Usage from skills

Every skill that does deterministic work can call the CLI in its workflow:

**Before (deterministic logic inlined in SKILL.md):**

```markdown
3. For each cluster, compute weighted recency: sum of `1 / (1 + days_old / 30)` across atoms.
4. Drop clusters with mentions count < 3 or distinct human sources < 2.
5. Hash the cluster fingerprint as sha256(title + sorted source paths).
6. Read ~/.claude/state/learnings-resurface.json. If fingerprint exists with same mentions count, skip.
   Otherwise, ...
```

**After (CLI does the deterministic part):**

```markdown
3. Run `vault resurface extract --window 90`. The CLI returns clusters as JSON with weighted recency scores, source-diversity counts, and idempotency fingerprints already computed.
4. For each cluster the CLI returns, make these JUDGMENT calls: principle vs state vs commitment vs open-question; does it contradict the Router?
5. For each routed cluster, call `vault learnings append <venture> "<entry>"` for state, or `vault router promote <fingerprint>` for principles. The CLI enforces append-only and writes the state file atomically.
```

The skill becomes shorter, more focused on judgment, and impossible to get the deterministic math wrong.

---

## What v0.1 does NOT do

- **Native implementations of the big ops.** `vault distill run`, `vault resurface run`, `vault session archive` currently wrap the existing bash scripts. Native impls of the inner logic (atom extraction, clustering, source-diversity scoring, contradiction detection) are v0.2+. Note for v0.2: the `learnings-resurface` repo shipped a v2.0 two-phase architecture (bash enumerate → claude phase A cluster → bash idempotency guard → claude phase B route → bash finalize) with persisted per-phase state for resumability. The native `vault resurface run` impl should preserve that decomposition — phases A and B remain LLM, everything else is deterministic CLI.
- **Skill migration.** None of your existing skills have been changed to call the CLI. They keep working through their original logic. Migration is incremental as you touch each skill.
- **CI gate.** `vault skill check` returns exit code 1 on critical/high issues, ready to wire into a pre-commit hook or CI, but no CI is configured here.
- **Web UI / dashboard.** The CLI is CLI-only. If you ever need a UI, that's `vault serve --http` in some future version.

---

## Migration plan (recommended)

The "right" sequence to migrate from scattered scripts to CLI-driven skills:

1. **Install vault-cli alongside existing setup.** Both work; nothing breaks. (You're here.)
2. **Add `vault router check` to your weekly checks.** Catches broken pointers early.
3. **Use `vault skill new <name>` for every new skill.** Old skills don't migrate; new ones are born conformant.
4. **Migrate one existing skill** (e.g., `learnings-resurface`) to call CLI primitives instead of inlining logic. Validate output matches.
5. **Build native implementations** of the wrapped commands (`vault distill ingest --native`, `vault resurface extract`, etc.). Skill migration unblocks more of these as it surfaces what's needed.
6. **Retire the bash scripts** once all skills point at the CLI.

Don't try to do steps 4–6 in one weekend. They're incremental, and each migration unlocks the next.

---

## What's in this repo

```
vault-cli/
├── README.md               ← this file
├── AGENTS.md               ← agent operating protocol
├── llms.txt                ← LLM nav index
├── LICENSE                 ← MIT
├── package.json
└── src/
    ├── cli.js              ← entrypoint
    ├── commands/
    │   ├── distill.js
    │   ├── resurface.js
    │   ├── session.js
    │   ├── voice-memo.js
    │   ├── router.js
    │   ├── frontmatter.js
    │   ├── learnings.js
    │   ├── skill.js
    │   ├── state.js
    │   └── today.js
    └── lib/
        ├── version.js
        ├── config.js       ← env-var driven path resolution
        ├── output.js       ← JSON-on-non-TTY convention
        ├── state.js        ← atomic state-file ops
        └── frontmatter.js  ← YAML parser + validator
```

No external dependencies. Pure Node.js 22.

---

## Related repos

- [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) — three-tier memory pattern. The CLI's `router lookup`, `router check`, and Knowledge Router promotion target this.
- [`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions) — frontmatter schema, vault structure, hooks. The CLI's `frontmatter audit` validates against this schema.
- [`learnings-resurface`](https://github.com/derekcedarbaum2/learnings-resurface) — the cron + skill that `vault resurface run` wraps. Now v2.0: two-phase orchestrator (bash enumerate → claude Phase A → bash guard → claude Phase B → bash finalize) with state persistence + resume support. Native CLI impl is v0.2 of vault-cli; should preserve that phase decomposition.
- [`note-highlight-indexer`](https://github.com/derekcedarbaum2/note-highlight-indexer) — the cron + skill that `vault distill run` wraps.
- [`agentic-architecture-map`](https://github.com/derekcedarbaum2/agentic-architecture-map) — the architecture-tracking pattern this CLI represents a structural change to.
- [`claude-code-setup`](https://github.com/derekcedarbaum2/claude-code-setup) — the public Claude Code setup this CLI consolidates (built originally as one PM's setup; generalizes).

---

## Credits

Architectural patterns informing this CLI:

- **[Garry Tan's `gbrain`](https://github.com/garrytan/gbrain)** (MIT) — the design reference. The "thin harness, fat skills" ethos, the skillify pipeline (`skill new` / `skill check`), the `AGENTS.md` + `llms.txt` agent-installable repo convention, and the JSON-on-non-TTY output rule were all crystallized in gbrain first. vault-cli is independent code with a different scope (vault-specific PM primitives, not a general agent brain), but gbrain is the reason the architecture has the shape it does.
- **[`llms.txt` standard](https://llmstxt.org)** — the documentation map format.
- **[gh CLI](https://cli.github.com)** — the JSON-on-non-TTY convention this CLI follows.
- **[Letta benchmark](https://letta.com)** — the filesystem+grep beats specialized retrieval finding that justifies this CLI's structured-curation approach over a vector DB.

No code from any of the above is copied here. The patterns are the borrowed part; the implementation is original.

## License

MIT.
