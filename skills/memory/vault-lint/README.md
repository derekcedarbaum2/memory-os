# vault-lint · Weekly health audit for AI-agent vaults

> **Want to install the whole 12-repo ecosystem?** Paste [this prompt](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/INSTALL-PROMPT.md) into your Claude Code or Codex session — it interviews you, installs in phases, runs smoke tests, and pauses for confirmation between phases. Or browse the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) first.


**A weekly health check for an AI agent's Markdown knowledge base. Tells you what's broken; lets you decide what to fix.** Read-only by default. Catches orphan pages, broken wikilinks, missing frontmatter, stale `_learnings.md`, contradictions between domain files. Pairs with [vault-conventions](https://github.com/derekcedarbaum2/vault-conventions).

> **New to Claude Code?** [Claude Code](https://docs.anthropic.com/claude/code) is Anthropic's command-line AI agent. A "vault" is a folder of Markdown files that the agent reads and writes — typically [Obsidian](https://obsidian.md). See the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) for the full system overview + onboarding sequence. Vocabulary used here (vault, frontmatter, `_learnings.md`, etc.) is defined in the [glossary](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/GLOSSARY.md).

---

## The problem

If your AI agent has been writing into a Markdown vault for a few months, the vault is rotting and you haven't noticed.

The rot looks like this: wikilinks that point to renamed files. Frontmatter missing on docs the agent now skips when filtering. `_learnings.md` files with stale bullets that contradict each other. A `MEMORY.md` index that creeps past 200 lines and starts truncating. Two domain files with conflicting positions on the same question. Orphan documents that no one links to.

None of this is loud. The agent keeps working. You don't see anything fail. But each silent fault eats a little of the vault's value, and the longer it sits, the more the next AI session inherits the cruft.

The fix is a periodic audit that knows what good filing looks like in *this* vault — knows the frontmatter schema, knows the conventions, knows the cross-layer references — and just tells you what's broken. Not a generic linter. A vault-aware one.

This is that audit. Reads-only by default — every fix is your call. Optional `--fix` mode for safe categories (frontmatter backfill only; never deletes or rewrites content). Runs on Sonnet, costs under $1 per typical run, triggers automatically via launchd (default: Sundays at 6 AM).

---

## What's in this package

```
vault-lint/
├── README.md                            # this file
├── LICENSE                              # MIT
├── SKILL.md                             # the skill itself (parameterized paths)
├── examples/
│   ├── README.md                        # what the examples illustrate
│   ├── example-broken-wikilinks-and-staleness.md
│   └── example-cross-layer-drift.md
└── launchd/
    └── com.user.vault-lint.plist        # sample weekly trigger
```

---

## Install (5 minutes)

### 1. Drop the skill into your Claude Code skills folder

```bash
mkdir -p ~/.claude/skills/vault-lint
cp SKILL.md ~/.claude/skills/vault-lint/
cp -r examples ~/.claude/skills/vault-lint/
```

### 2. Configure paths in SKILL.md

Open `~/.claude/skills/vault-lint/SKILL.md` and replace these placeholders with your absolute paths:

| Placeholder | Replace with |
|---|---|
| `{{VAULT_ROOT}}` | The folder containing your `_learnings.md` files |
| `{{MEMORY_PATH}}` | Your auto-memory file (e.g., `~/.claude/projects/<project>/memory/MEMORY.md`) |
| `{{CLAUDE_MD}}` | Your global `CLAUDE.md` (typically `~/.claude/CLAUDE.md`) |
| `{{SESSION_ARCHIVE_DIR}}` | Where your session archives live in the vault (e.g., `CC Chat History/`) |

### 3. Test it manually

```bash
claude -p "/vault-lint"
```

Expect a report at `<your-vault>/Lint Reports/lint-YYYY-MM-DD.md`. If the folder doesn't exist, the skill creates it.

### 4. (Optional) Schedule the weekly run

Edit `launchd/com.user.vault-lint.plist`:
- Replace every `USERNAME` with your macOS short username (`whoami`)
- Adjust the day/time if Sunday 6 AM doesn't suit you (`Weekday`: 0/7=Sun, 1=Mon … 5=Fri … 6=Sat)

Then install:

```bash
cp launchd/com.user.vault-lint.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.vault-lint.plist
```

Verify: `launchctl list | grep vault-lint`. Run on demand: `launchctl start com.user.vault-lint`. Remove later: `launchctl unload ~/Library/LaunchAgents/com.user.vault-lint.plist`.

---

## Invocation modes

- `/vault-lint` — full audit
- `/vault-lint --folder=<vault-relative-path>` — scope to one folder (e.g., `Products/Alpha/`); cheap targeted run
- `/vault-lint --fix` — pre-approve auto-fixes for safe categories (frontmatter backfill); per-category yes/no confirm; never auto-deletes

---

## What the skill expects from your vault

The skill is opinionated. It assumes:

- A vault root containing markdown files
- One or more `_learnings.md` files for distilled domain knowledge (one per domain works best)
- A multi-layer knowledge structure: global `CLAUDE.md` → `MEMORY.md` → per-domain `_learnings.md`
- Wikilink syntax (`[[target]]`) for inter-page references
- YAML frontmatter on every `.md` file with required fields: `title`, `type`, `status`, `classification`, `created`, `updated`. Plus `last_reviewed: YYYY-MM-DD` on `_learnings.md` files for staleness tracking.

If your vault uses different conventions (markdown links instead of wikilinks, no frontmatter, single knowledge layer), see "Adapting to Your Vault" at the bottom of `SKILL.md` — most checks degrade gracefully.

---

## Always-excluded paths

The skill always skips:

- `_archive/`, `_attachments/`, `.git/`, `.obsidian/`
- **`Reading/Books/`, `Reading/Articles/`, `Reading/Tweets/`** — Readwise-generated. Any "fix" here is overwritten on next sync. **If you also use the [Note Highlight Indexer](https://github.com/derekcedarbaum2/note-highlight-indexer) or another Readwise integration, this exclusion is what keeps lint reports useful instead of full of 200+ false positives.**
- Your session archive folder — included from inventory but excluded from orphan and most semantic checks (intentionally terminal leaf nodes).

---

## What the skill does NOT do

- It does not edit vault content beyond what `--fix` explicitly enables (frontmatter backfill only) and the user confirms per category.
- It does not delete files, rename files, or rewrite content.
- It does not apply changes from prior reports — that's a separate skill (`/apply-lint-fixes`, not included here).
- It does not push reports anywhere. Reports stay local in `Lint Reports/`.

---

## Cost

Sonnet model, target under $5 per run, typical runs come in around $0.20–$0.75. The skill is bounded by reading only `_learnings.md` files, `MEMORY.md`, `CLAUDE.md`, and recent session archives — not the whole vault.

---

## Sample reports

See `examples/`. Both are illustrative reports from a 350+ file PM knowledge vault. The first focuses on structural issues; the second on semantic drift. Use them as a style reference when writing or evaluating reports.

---

## Related

- [Note Highlight Indexer](https://github.com/derekcedarbaum2/note-highlight-indexer) — companion package for Readwise → playbook distillation. Vault Lint's `Reading/*` exclusions exist specifically so the two coexist cleanly.

---

## License

MIT. See `LICENSE`. Use it, fork it, modify it. Attribution appreciated but not required.

---

## Questions

Open an issue on the repo.
