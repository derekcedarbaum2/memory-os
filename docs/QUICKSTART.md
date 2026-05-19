# Quickstart

You cloned `memory-os` and you want to be running it. This doc gets you from a fresh machine to a working vault with the cron firing, in roughly two hours of setup and one month of accumulation. Every step is a command. No undefined nouns.

If you already have a working vault and you want operations / cadence / refactor procedures, skip this doc and read [`HOW-TO.md`](HOW-TO.md) instead.

**Platform note up front:** the cron automation is macOS-only. It uses `launchd` plists. The shell scripts and Python scripts are portable; the *scheduler* isn't. If you're on Linux, you'll translate the plists to systemd units yourself. If you're on Windows, this isn't a supported configuration today.

---

## Vocabulary (one read, then move on)

You'll see these terms throughout. Skim once, refer back if needed.

| Term | What it is |
|---|---|
| **vault** | A folder of `.md` files you treat as your second brain. Obsidian opens it; any text editor works too. `memory-os` assumes the vault is at `~/Documents/Vault/` or similar, but you choose the path. |
| **`CLAUDE.md`** | The instruction file Claude Code reads at the start of every session. One lives at `~/.claude/CLAUDE.md` (global, for you the user). Another lives at the *vault root* (project-scoped, for the vault). |
| **memory directory** | Claude Code's per-project persistent memory at `~/.claude/projects/<project-id>/memory/`. The `<project-id>` is auto-generated from your current working directory; check `ls ~/.claude/projects/` to find yours. |
| **`MEMORY.md`** | Inside the memory directory. Always loaded into every Claude session. **Hot pinboard.** 80-line cap. |
| **`INDEX.md`** | Sibling of `MEMORY.md`. Read on demand only. **Cold pointers.** |
| **`_learnings.md`** | Per-venture file inside each venture folder in the vault. Append-only. Decisions, key facts, open threads, related sessions for that one venture. |
| **`tag-vocabulary.md`** | The controlled vocab for YAML `tags:` across vault and memory. `tags: []` is an enforced error. Lives at `~/.claude/reference/tag-vocabulary.md`. |
| **skill** | A `SKILL.md` file Claude Code loads as a named capability. They live at `~/.claude/skills/<skill-name>/SKILL.md`. Memory-os ships a dozen. |
| **launchd plist** | macOS's cron equivalent. An XML file at `~/Library/LaunchAgents/` that tells the system when to run a script. Loaded with `launchctl load`. |
| **the cron** | Shorthand for the launchd-plist-driven automation. Same thing as "scheduled job." |

That's the whole vocabulary. Everything below uses these terms; nothing else.

---

## Week 1 — Substrate setup

### 1. Decide where your vault lives

Pick a path. Common choices:

```
~/Documents/Vault/                                                # Plain folder
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault/    # Obsidian on iCloud
~/Dropbox/Vault/                                                  # Synced via Dropbox
```

This doc uses `$VAULT` to refer to your chosen path. Set it:

```bash
export VAULT="$HOME/Documents/Vault"
mkdir -p "$VAULT"
```

If you want Obsidian, install it (`brew install --cask obsidian`) and point it at `$VAULT`.

### 2. Lay down the folder skeleton

```bash
mkdir -p "$VAULT"/{Work,Ideas,Personal,Writing,Reading,"AI Toolkit","Company Building",_archive,_attachments,raw-sources}
mkdir -p "$VAULT/AI Toolkit/CC Chat History"
```

### 3. Drop in the vault-level conventions

From your cloned `memory-os` repo:

```bash
cp memory-os/vault/conventions.md           "$VAULT/CLAUDE.md"
cp memory-os/vault/frontmatter-schema.md    "$VAULT/"
cp memory-os/vault/learnings-template.md    "$VAULT/"
```

(You're using `vault/conventions.md` as the vault's own CLAUDE.md so the agent reads it when it opens the vault. The other two are reference files inside the vault.)

### 4. Set up your Claude Code memory directory

Find your project-scoped memory directory. The path depends on what directory you launch Claude Code from. If you launch it from your home directory:

```bash
ls ~/.claude/projects/-Users-$USER/
```

Inside there should be a `memory/` subfolder. If not, create it:

```bash
MEMORY_DIR=~/.claude/projects/-Users-$USER/memory
mkdir -p "$MEMORY_DIR"/{user,feedback,principle,location,pipeline}
```

Now drop in starter `MEMORY.md` and `INDEX.md`:

```bash
cp memory-os/vault/memory-protocol.md "$MEMORY_DIR/MEMORY.md.template"
# Now edit MEMORY.md.template to remove the protocol description and keep only
# the structure — user identity, sticky preferences, principles, active ventures.
# Save as MEMORY.md.
```

If you want a worked example of a populated `MEMORY.md`, look at the top-level [README.md](../README.md) in this repo for the shape.

### 5. Install the global `CLAUDE.md`

```bash
cp memory-os/vault/operations.md ~/.claude/CLAUDE.md
```

This is the global instruction file Claude reads on every session. You'll customize it over time; this gives you a working starting point.

### 6. Install the tag vocabulary

```bash
mkdir -p ~/.claude/reference
cp memory-os/vault/tag-vocabulary.md ~/.claude/reference/tag-vocabulary.md
cp memory-os/vault/operations.md     ~/.claude/reference/operations.md
```

### 7. Install the cron infrastructure (macOS)

Copy the scripts:

```bash
mkdir -p ~/.claude/hooks ~/.claude/logs
cp memory-os/automation/*.py ~/.claude/hooks/
cp memory-os/automation/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py ~/.claude/hooks/*.sh
```

Edit `~/.claude/hooks/weekly-memory-maintenance.sh` and any of the Python scripts to point at *your* vault path — they're hard-coded. Search for `Vault/` and replace.

Copy and load the plists:

```bash
cp memory-os/automation/plists/*.plist ~/Library/LaunchAgents/
# Edit each plist to replace /Users/derekcedarbaum/ with your actual home path
sed -i '' "s|/Users/derekcedarbaum|$HOME|g" ~/Library/LaunchAgents/com.user.*.plist

# Load all five
for plist in ~/Library/LaunchAgents/com.user.*.plist; do
  launchctl load "$plist"
done

# Verify they're loaded
launchctl list | grep com.user
```

You should see five lines: `weekly-memory-maintenance`, `learnings-resurface`, `today`, `auto-distill`, `vault-lint`. The leading `-` in each line means they're loaded but not currently running; that's correct.

### 8. Install the skills

```bash
mkdir -p ~/.claude/skills
for skill_dir in memory-os/skills/*/*/; do
  skill_name=$(basename "$skill_dir")
  cp -r "$skill_dir" ~/.claude/skills/"$skill_name"/
done
```

Verify Claude Code sees them: open a new Claude Code session and type `/`. You should see the memory-os skills in the autocomplete.

### 9. Verify the basic loop works

Open a Claude Code session. Ask the agent something simple about itself. Then run:

```
/archive-session
```

The skill should produce a session archive at `$VAULT/AI Toolkit/CC Chat History/YYYY-MM-DD-*.md`. If it doesn't, the session-to-vault path is misconfigured; check the skill's `SKILL.md` for the output directory and edit to match `$VAULT`.

You now have a working substrate. The vault is empty. The agent has no context yet. The cron will fire next Sunday at 11pm. This is correct.

---

## Week 2 — Start populating

Pick your three most active engagements. For each:

```bash
mkdir -p "$VAULT/Work/<engagement-name>"
cp memory-os/vault/learnings-template.md "$VAULT/Work/<engagement-name>/_learnings.md"
# Edit the frontmatter — set title, tags (venture:<slug>, kind:state, decay:high), dates.
```

`Work/` is for paid engagements; `Ideas/` is for pre-revenue ventures; `Personal/` is for life stuff. Pick the folder that fits.

Then start using the system. Rules:

- **End every Claude Code session with `/archive-session`.** It captures decisions, insights, open threads, and updates the project index.
- **Append to a venture's `_learnings.md` whenever you decide something or learn something.** Under `## Learnings` for insights, `## Key Decisions` for decisions, `## Open Threads` for unresolved.
- **Don't try to populate `MEMORY.md` yet.** You don't have enough state to know what should be hot vs. cold.

Don't expect the agent to feel transformed yet. This is week 2. The compounding hasn't started.

---

## Month 1 — Tag vocab and pinboard

By now you should have 20-30 `_learnings.md` files and a couple dozen session archives in `AI Toolkit/CC Chat History/`. Time to set up the hot pinboard.

Edit `MEMORY.md` to add an "Active ventures" section with the 5–7 engagements you actually work on. Each line in the format:

```markdown
- **<Venture Name>** — <one-line description> → `Vault/Work/<name>/_learnings.md`
```

The `active-venture-refresh.py` cron will read this section every Sunday. Everything else (locations, less-active ventures, gotchas, MCP configs) goes in `INDEX.md`.

Audit your tags. If you're using terms that aren't in `~/.claude/reference/tag-vocabulary.md`, add them there *first*, then use them. Run:

```bash
python3 ~/.claude/hooks/tag-backfill.py
```

It's idempotent. It'll fix any `tags: []` or legacy free-text tags across the whole vault and memory dir in one pass.

---

## Month 3 — Pattern surfacing

The weekly cron should now find real things. Cross-venture principles surface in `$VAULT/log.md` Monday mornings. The first time you see one:

1. Read the new entry in the playbook the cron routed it to.
2. Decide: keep, edit, or remove.
3. If it's decision-time-load-bearing across multiple future tasks (not just an interesting observation), promote it to an inline rule in `MEMORY.md` under "Decision-time principles."

Otherwise leave it where the cron put it. The cron is conservative; it surfaces candidates, you decide.

Run `/prune-memory` and `/vault-lint --fix` for the first time. Expect issues to surface — drifted frontmatter, missing tags, broken wiki-links. Spend an afternoon cleaning. Subsequent monthly runs take 5 minutes.

---

## Month 6 — Compounding

If you've been consistent, you should now have:

- ~80 `_learnings.md` files
- 5-7 active ventures on the hot pinboard
- 20+ accumulated principles, several inlined in `MEMORY.md`
- A signal-dense weekly log in `$VAULT/log.md` that takes 90 seconds to skim on Monday

The agent now starts every session already knowing your ventures, your preferences, your current open threads, and the principles you've accumulated. Week-one Derek's agent started cold. Month-six Derek's agent starts warm.

This is when memory-os pays back. If you abandoned the system in week 4 because it didn't feel transformative yet, you abandoned it on the steepest part of the deferred-payoff curve. The value is on the far side of that valley.

---

## Where to go next

- **Operations cadence (daily/weekly/monthly):** [`HOW-TO.md`](HOW-TO.md)
- **The argument:** [`thesis.md`](thesis.md)
- **The honest envelope:** [`envelope.md`](envelope.md)
- **The conventions in canonical form:** [`../vault/`](../vault/)
- **The cron scripts you just installed:** [`../automation/`](../automation/)

If you hit something that doesn't fit your work shape (single-program research, single-product indie hacking, single-book writing), read the "What shape of work this assumes" section in [`HOW-TO.md`](HOW-TO.md). The architecture generalizes; the folder taxonomy doesn't, and you'll want to translate.
