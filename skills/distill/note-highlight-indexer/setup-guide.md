# Setup Guide

The system works with any coding agent that supports markdown prompts. The two well-supported paths are:

- **Claude Code** — installable as a slash command (`/playbook-distill`). 5 minutes.
- **Codex CLI / Codex web / other agents** — paste the prompt or load it as a custom prompt file. 2 minutes.

Both pull from the same prompt logic. Pick the path that matches your tool.

---

## Pre-flight checklist (especially if an agent is doing this install)

The install has four layers. The first two are low-risk; the last two have user-shaping consequences and should NOT be done silently. If an agent is installing on the user's behalf, ask these questions BEFORE making decisions:

### 1. Vault root
**What's the absolute path to the Obsidian vault (or markdown folder) the system should operate on?** No defaults — ask the user.

### 2. Playbook paths — adapt to existing folders, or scaffold new ones?

The default `Playbooks-Index.md` template uses paths like `Company Building/Startup Playbook/`, `Personal/Health & Wellness/Health Playbook/`, `Writing/Writing Playbook/`, `Professional Development/AI/Tech Playbook/`. These assume a particular personal-vault layout.

**Look at the user's actual top-level vault folders before proceeding.** If they don't match, ask:

- **(a) Adapt paths to existing folders.** Edit the `Playbook Path` column in `Playbooks-Index.md` to map each domain onto a folder that already exists (e.g., for a work vault: `Tech → Toolkit/Tech Playbook/`, `Startup → Products/Startup Playbook/`). Best when the user wants playbooks to live alongside existing work.
- **(b) Scaffold new top-level folders.** Leave the default paths; the skill will create them on first hit. Best when the user wants clean separation between e.g. work content and personal reading.

This is a vault-layout decision with long-term consequences. Don't make it for them silently.

### 3. Readwise integration — yes or no?

**Does the user use Readwise with "Sync Highlights to Obsidian" pointing into this vault?**
- **No** → stop after installing the manual skill (Layer 1). Do NOT install the headless variant or the cron.
- **Yes** → continue to Q4.

### 4. Cron vs ad-hoc (only if Readwise = yes)

If the user uses Readwise, ask:
- **Daily cron** (Layer 4) — installs a launchd plist that runs every morning at 7:30 AM. Persistent system job; burns one headless API call per Readwise file (capped at 5/day). Only install with **explicit** user confirmation. This is the only layer with persistent system-level effects.
- **Headless skill only, no cron** (Layer 3 only) — installs the second skill but no scheduled job. User runs `auto-distill-readwise.sh --backfill` manually when they want a batch pass.

### Default agent behavior

When in doubt: install Layers 1 + 2, skip Layers 3 + 4, and report back to the user what's installed and what's deferred. The Readwise layers can always be added later; once the cron is wired and writing daily, removing it is messier.

---

## Install layers (overview)

| Layer | What | Required? | Blast radius |
|---|---|---|---|
| 1 | Manual skill / prompt | Always | Low — just files |
| 2 | Routing index in vault (`Playbooks-Index.md`) | Always | Low — one file in vault |
| 3 | Headless skill (`auto-playbook-distill`) | Optional (if user wants batch processing of Readwise files) | Low — just one more file |
| 4 | Daily cron (launchd plist + script) | Optional (only if user explicitly wants daily auto-processing) | Persistent system job; daily API calls |

Layers 1 and 2 are bundled below as "Path A (Claude Code)" or "Path B (Codex/other)." Layer 3 is in "Optional — Headless skill for batch processing." Layer 4 is in "Optional — Daily cron." Each can be installed independently.

---

## Path A — Claude Code (slash-command convenience)

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- A folder of markdown files you treat as your "second brain" (Obsidian vault, plain folder, anything)

### Step 1 — Install the skill

```bash
mkdir -p ~/.claude/skills/playbook-distill
cp skills/playbook-distill.md ~/.claude/skills/playbook-distill/SKILL.md
```

Verify: launch Claude Code (`claude`) inside your vault and check the skill list. `playbook-distill` should appear.

### Step 2 — Drop the routing index into your vault

```bash
cp vault-templates/Playbooks-Index.md "<your-vault-path>/Playbooks-Index.md"
```

Open it. Edit:
- The `author` field in the frontmatter
- **The `Playbook Path` column** — this is the load-bearing decision. The default paths assume top-level folders like `Company Building/`, `Personal/`, `Writing/`, `Professional Development/`. If your vault doesn't already have those, you have two choices (see Pre-flight Q2 above):
  - **(a) Adapt** — change each `Playbook Path` to point at folders that already exist (e.g., `Tech → Toolkit/Tech Playbook/`).
  - **(b) Scaffold** — leave the defaults; the skill will create the top-level folders on first hit.
- Optionally the 10 domains themselves — but resist adding more than 10. The system depends on a small finite taxonomy.

The file does **not** need every playbook folder to exist yet. The skill scaffolds them on first hit (per choice b above).

### Step 3 — Smoke-test it

Open Claude Code in your vault. Paste any short article or essay you've read recently. Type `/playbook-distill`.

Expected behavior:
- Skill reads `Playbooks-Index.md`
- Classifies the content into one of the 10 domains
- If no playbook exists for that domain yet, scaffolds it (creates folder + README + first topic file)
- Distills the content into operational format and merges
- Reports a one-paragraph summary
- Appends a line to `<your-vault>/log.md`

You're done. Run `/playbook-distill` whenever you read something worth keeping.

---

## Path B — Codex CLI / Codex web / other agents (paste-in)

### Prerequisites

- A coding agent that accepts markdown prompts (Codex CLI, Codex web, Cursor, Aider, etc.)
- A folder of markdown files you treat as your "second brain"

### Step 1 — Drop the routing index into your vault

Same as Path A. Copy `vault-templates/Playbooks-Index.md` into your vault root, edit the author, and **adapt the `Playbook Path` column to your vault layout** (or commit to scaffolding new top-level folders — see Pre-flight Q2 above).

```bash
cp vault-templates/Playbooks-Index.md "<your-vault-path>/Playbooks-Index.md"
```

### Step 2 — Pick how you want to invoke the prompt

**Option 1 — Inline reference (simplest):** when you want to distill content, tell the agent:

> "Run the playbook-distill workflow on the following content. The workflow lives at `<absolute path to>/prompts/playbook-distill.md`. After reading the workflow, process this content: [paste content]"

The agent reads the workflow file, then operates on your content. Works in any agent that can read local files.

**Option 2 — Custom prompt template:** save the prompt as a custom template in your tool. Most agents support this.

- **Codex CLI**: save `prompts/playbook-distill.md` somewhere accessible (e.g., `~/codex-prompts/playbook-distill.md`) and reference it via your tool's prompt-file flag, or paste its contents as a system instruction.
- **Codex web**: paste the entire `## Instructions for the agent` section of `prompts/playbook-distill.md` as a system message at the start of a session.
- **Cursor / Aider / other**: store the prompt where your tool keeps custom prompts and invoke per their convention.

**Option 3 — Paste the whole prompt every time (low friction, no setup):** open `prompts/playbook-distill.md`, copy everything from "## Instructions for the agent" through the end of the workflow, paste into your agent, then paste your content and ask it to run.

### Step 3 — Smoke-test it

Paste a short article you've read into your agent, invoke the prompt (whichever Option 1/2/3 you chose), and watch:
- The agent reads `Playbooks-Index.md`
- Classifies the content into one of the 10 domains
- Scaffolds a new playbook if needed (creates folder + README + first topic file)
- Distills the content into operational format and merges
- Reports a summary
- Appends a line to `<your-vault>/log.md`

You're done. Repeat whenever you read something worth keeping.

---

## Layer 3 — Optional: headless skill for batch processing

Skip this section if you don't use Readwise.

This layer installs the second skill (or makes the second prompt available). It does NOT install a cron — you can run batch processing on-demand only. Add Layer 4 separately if you want daily automation.

### Prerequisites

- Readwise account with "Sync Highlights to Obsidian" writing to `<your-vault>/Reading/{Articles,Books,Tweets}/`
- A headless-capable coding agent (Claude Code or Codex CLI both work)
- Python 3 (ships with macOS) — only needed if you also install Layer 4

### Step 1 — Install the headless skill

If you're using Claude Code:

```bash
mkdir -p ~/.claude/skills/auto-playbook-distill
cp skills/auto-playbook-distill.md ~/.claude/skills/auto-playbook-distill/SKILL.md
```

If you're using Codex CLI or another agent: keep `prompts/auto-playbook-distill.md` accessible. Reference it via your tool's prompt-loading mechanism (or paste it inline when running batches).

### Step 2 — Install the runner script (no cron yet)

```bash
mkdir -p ~/.claude/hooks
cp cron/auto-distill-readwise.sh ~/.claude/hooks/auto-distill-readwise.sh
chmod +x ~/.claude/hooks/auto-distill-readwise.sh
```

Edit the variables at the top of the script:

```bash
VAULT="$HOME/path/to/your/Vault"     # absolute path to your vault
CLI_BIN="$HOME/.local/bin/claude"    # or your Codex CLI path, or another agent
CLI_FLAG="-p"                         # claude uses -p; adjust for other agents
```

If you're using Codex CLI: set `CLI_BIN` to your codex binary path. The single-shot/headless flag may differ — check your tool's docs and update `CLI_FLAG` accordingly. Then edit the prompt body in the script's `process_file()` function: replace `Use the auto-playbook-distill skill to process this file.` with `Follow the workflow in <absolute path to>/prompts/auto-playbook-distill.md to process this file.`

### Step 3 — Run on-demand

When you want to process new Readwise files:

```bash
# Process up to 5 unprocessed files (default daily cap):
~/.claude/hooks/auto-distill-readwise.sh

# Or backfill mode — up to 25 files per invocation; rerun until done:
~/.claude/hooks/auto-distill-readwise.sh --backfill

# Or a single file (smoke test):
~/.claude/hooks/auto-distill-readwise.sh --file "<absolute path>"
```

You're done with Layer 3. Stop here if you don't want a daily scheduled job.

---

## Layer 4 — Optional: daily cron (macOS launchd)

**This layer adds a persistent system job that runs every morning. Only install with explicit user confirmation — it has system-level effects (launchd plist) and burns headless API calls daily.**

### Prerequisites

- Layer 3 already installed (headless skill + runner script working)
- macOS (Linux users: substitute systemd or cron — see Linux note below)

### Step 1 — Smoke-test Layer 3 first

Before scheduling, confirm the runner works manually:

```bash
~/.claude/hooks/auto-distill-readwise.sh --file "<absolute path to one Reading/Articles/*.md>"
```

What you should see:
- A new playbook folder gets created (or an existing one gets a new topic file or a merge)
- `Vault/Playbooks-Index.md` updates the "Active Playbook Status" table
- `Vault/log.md` gets a new line
- `~/.claude/state/distilled-readwise.json` gets a new entry

Run again with the same file → should print "already processed (hash match), skipping". If this works, proceed.

### Step 2 — Install the launchd plist (daily 7:30 AM)

```bash
cp cron/com.user.auto-distill.plist ~/Library/LaunchAgents/com.user.auto-distill.plist
sed -i '' "s|<YOUR_HOME>|$HOME|g" ~/Library/LaunchAgents/com.user.auto-distill.plist
launchctl load ~/Library/LaunchAgents/com.user.auto-distill.plist
```

Verify it's scheduled:

```bash
launchctl list | grep auto-distill
```

### Step 3 — (Optional) Backfill existing highlights

If you already have years of highlights in `Reading/`, run a backfill pass. This caps at 25 files per invocation; rerun until done:

```bash
~/.claude/hooks/auto-distill-readwise.sh --backfill
```

Or just let the daily cron grind through it 5/day. It'll catch up over a few weeks.

### Linux note

The launchd plist is macOS-specific. On Linux, achieve the same by either:
- A systemd timer (`auto-distill-readwise.timer` + `auto-distill-readwise.service`)
- A crontab entry: `30 7 * * * /home/<user>/.claude/hooks/auto-distill-readwise.sh`

The runner script itself is portable.

---

## Natural-language triggers (saying "store this" instead of typing the slash command)

The skill is designed to activate on casual phrasings paired with pasted content — you shouldn't have to remember `/playbook-distill` every time.

### Recognized trigger phrases

When you paste substantive content and use any of these phrases, the workflow should fire:
- "store this" / "save this" / "capture this" / "keep this"
- "file this" / "stash this" / "hold onto this"
- "make a note of this"
- "operationalize this" / "playbook this" / "distill this"
- "add this to the playbook"

It will NOT fire on:
- **"Remember this" / "remember X"** — these are reserved for memory or `_learnings.md` updates, a distinct subsystem. The playbook is for cross-domain *operational rules*; memory is for user/project *facts*. Blurring them turns the playbook into a junk drawer.
- Trigger phrase without content (e.g., bare "store this" in conversation)
- Content without trigger phrase (just sharing an article doesn't mean you want it captured — you have to signal intent)
- "Save this file" / "save this code" (those are write-tool requests, different operation)
- Storage requests for non-knowledge content (raw URLs, code snippets, calendar items)

### How it works in each tool

**Claude Code (automatic):** The skill's `description` field includes the trigger phrase list. Claude Code's skill auto-activation reads it and fires the skill when phrases match. No setup required beyond Path A install.

**Codex CLI / Codex web / Cursor / Aider / other agents (manual setup):** these tools don't have an equivalent skill auto-activation mechanism. You have two options:

1. **Add a system-level instruction.** Put the auto-trigger block at the top of your tool's persistent context / system prompt / custom instructions. Use the wording from `prompts/playbook-distill.md` "Auto-trigger configuration" section. Once configured, the agent will fire the workflow on natural phrases as if it were native.

2. **Invoke explicitly.** Skip the auto-trigger setup and just paste the prompt body (or reference `prompts/playbook-distill.md`) when you want to capture content. More verbose, but works without persistent-context support.

### When the trigger is ambiguous

If you say "store this" but the content is short, code, a one-liner, or otherwise not playbook-worthy, the skill is instructed to ask one clarifying question before proceeding rather than running the full workflow on something that won't distill cleanly. Example: *"Want me to distill this into the [Tech | Startup | etc.] playbook, or is this a different kind of save?"*

This is the right behavior — fewer false positives, no silent merges of wrong content.

---

## Troubleshooting

**Manual mode — skill doesn't show up:**
- Verify the file is at `~/.claude/skills/playbook-distill/SKILL.md` (not just `playbook-distill.md`)
- Restart Claude Code

**Manual mode — skill picks the wrong domain:**
- Edit the heuristics in `~/.claude/skills/playbook-distill/SKILL.md` (step 3, "Classify the domain")
- Or, prepend your paste with a hint: "this is health content" / "this is a startup framework"

**Cron mode — cron doesn't fire at 7:30:**
- Check `~/.claude/logs/auto-distill.err` for launchd errors
- Verify the plist loaded: `launchctl list | grep auto-distill`
- Ensure your Mac is awake at 7:30 AM (launchd doesn't wake the machine for `StartCalendarInterval`); if it sleeps, the run fires on next wake

**Cron mode — "another auto-distill instance is running":**
- The previous run is still going (backfill mode can take a while). The lockdir self-cleans after 2h.
- If it's been longer, manually clear: `rmdir /tmp/auto-distill-readwise.lock.d`

**Cron mode — files keep getting re-processed every run:**
- Check the state file: `cat ~/.claude/state/distilled-readwise.json | jq`
- Hash check is by SHA-256 of the source file. If Readwise re-syncs and changes whitespace, the file gets reprocessed. Acceptable cost.

**Want to disable cron temporarily:**
- `launchctl unload ~/Library/LaunchAgents/com.user.auto-distill.plist`
- Re-enable: `launchctl load ~/Library/LaunchAgents/com.user.auto-distill.plist`

---

## Optional — wire skills to load playbooks

The real value comes from your *other* skills loading the relevant playbook(s) for their task. E.g.:

- A "write tweets" skill loads `Writing Playbook/` + `Startup Playbook/gtm-distribution.md`
- A "code review" skill loads `Tech Playbook/working-with-coding-agents.md`
- A "weekly planning" skill loads `Personal OS Playbook/` + `Health Playbook/`

This isn't built in — you wire it on a per-skill basis. The pattern: each skill's `SKILL.md` instructs Claude to read the relevant playbook README first, then load only the topic files needed for the task.
