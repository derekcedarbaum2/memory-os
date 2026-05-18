# Auto Playbook Distill — Tool-Agnostic Prompt (headless variant)

A pure-prompt version of the `auto-playbook-distill` skill, for headless / cron use. Distinct from `playbook-distill.md` (the interactive variant) only in that this version:
- Runs from a single source-file path passed in
- Decides routing without asking the user
- Outputs a one-line confirmation suitable for cron logs
- Maintains a state file for idempotency

Paste this content into any coding agent (Claude Code, Codex CLI, Codex web, etc.) or reference it from a headless invocation script.

For the Claude-Code-specific installable form, see `skills/auto-playbook-distill.md`.

---

## Instructions for the agent

You are running the **auto-playbook-distill** workflow in headless mode. The runner has invoked you with a source file path; your job is to classify, distill, and merge the file's contents into the right cross-vault playbook, then mark it as processed in the state file.

### Input format

The invocation contains:
- A line `Source file: <absolute path>` — the file to process (a Readwise-synced article / book / tweet collection, or any other markdown file with extractable insights)
- (Optional) `Strictness: loose | strict` — defaults to `loose`
- (Optional) `Run id: <uuid>` — for idempotency tracking

### Hard rules (enforced)

1. **NEVER edit files in `Vault/Reading/`.** Readwise regenerates them on sync — any edits are wiped. Read-only on the source.
2. **NEVER delete anything.** No file removal under any circumstance.
3. **NEVER create more than one new playbook in a single run.** If the source spans multiple new domains, route to the dominant one and append the secondary to `Vault/raw-sources/_unrouted-distill-queue.md` for the next run.
4. **NEVER skip the source tag.** Every merged claim must end with `[<source title>, <date>]`. Untagged content is a bug.
5. **NEVER fabricate quotes.** Distillations paraphrase highlights into operational rules; direct quotes from the highlight bullets must be reproduced verbatim if used.
6. **One source file = one run.** Don't go reading other Readwise files for context.
7. **NEVER use `mv` on existing vault folders.** Use `Write` (or your tool's equivalent) to create new files. Use `Edit` (or your tool's equivalent) to update existing files. The ONLY allowed shell filesystem operations during scaffolding are: `mkdir -p <full absolute target path>` and `ls -la` for verification.
8. **ALWAYS use absolute paths for `mkdir -p`.** Never use relative paths or `cd` followed by `mkdir`.
9. **Verify the playbook path BEFORE creating it.** Run `ls -la <parent dir>` to confirm the parent exists. If it doesn't, abort and queue the source to `_unrouted-distill-queue.md` instead of inferring an alternative path.

### Workflow

#### 1. Read the routing index

Read `Vault/Playbooks-Index.md`. It contains the 10 playbook domains and their paths, the routing rules (single domain vs. spanning vs. unrouted), and per-playbook conventions.

#### 2. Read the source file

Note: author, title, category from the metadata block. The `## Highlights` section is the operational substrate. Any tags or topics.

#### 3. Classify the domain

Pick **one primary domain** from the 10. Heuristics:

- **Startup**: founder essays, GTM frameworks, pitch teardowns, AI maturity, B2B / SaaS
- **Investing**: investor biographies, valuation, market history, capital allocation
- **Health**: nutrition, exercise, biomechanics, sleep, longevity, mental health
- **Parenting**: child development, education methods, early learning
- **Writing**: style, voice, rhetoric, copywriting, narrative theory
- **Philosophy**: decision theory, epistemology, ethics, schools of thought
- **Politics + Economics**: monetary theory, trade, market design, policy critique
- **Leadership**: command, coaching, executive operating cadence, debrief
- **Personal OS**: time, attention, habits, knowledge management, systems thinking
- **Tech**: AI/ML, software architecture, agent design, dev tooling, technical writings

If the source spans 2 domains: pick the dominant one for primary merge. The secondary gets a cross-link in its relevant topic file.

If the source spans 3+ domains OR has no clear match: append to `Vault/raw-sources/_unrouted-distill-queue.md` (one line per file, with reason). Do not create an 11th playbook silently. (No interactive confirm in headless mode — queue and move on.)

#### 4. Determine target file inside the playbook

Read the target playbook's `README.md` (if it exists). Look for an existing topic file matching the dimension of the new content.

- **Strong match (existing topic file)** → merge into it.
- **No matching topic file but playbook exists** → create a new topic file in the playbook. Update the README.
- **Playbook doesn't exist yet** → scaffold it (step 5).

#### 5. Scaffold a new playbook (only if needed)

If the target playbook has no folder yet:

1. Create the directory at the path from `Playbooks-Index.md`.
2. Write `README.md` with frontmatter, domain headline, empty file index, empty task router, conventions section, sources captured section.
3. Create the first topic file (named after the dominant dimension of the source content).
4. Update `Vault/Playbooks-Index.md` "Active Playbook Status" table.

#### 6. Distill into operational format

Convert highlights into:
- **Scorecards** (rate something 0–3 or 0–5 across dimensions)
- **Decision triggers** ("if X, then Y")
- **Anti-pattern detectors** (boolean checks for failure modes)
- **Fillable templates** (slot-in formats with examples)
- **Reference tables** (pattern → when it fits → example)

**Loose threshold (default):** include any insight that *might* be useful later, not just provable rules. Better to capture and prune than miss.

**Strict threshold:** only insights that yield a hard decision rule, scorecard row, anti-pattern detector, or fillable template.

Preserve named examples and specific numbers. Preserve direct quotes when they carry the rule.

#### 7. Source-tag every claim inline

Format: `[<short title>, <YYYY-MM-DD>]`. Use the source file's title and the file's modified date.

#### 8. Update the playbook README

If you created a new topic file: add to the file index AND append to "Sources captured." If you only merged: just append to "Sources captured."

#### 9. Update the routing index

Update the "Active Playbook Status" table in `Vault/Playbooks-Index.md`:
- Bump file count if a new topic file was created
- Set "Last Source Added" to the source title + today's date

#### 10. Mark file as processed (state file)

Append to the state file at the configured path (e.g., `~/.claude/state/distilled-readwise.json` for Claude Code; the runner script tells you the path):

```json
{
  "<absolute source path>": {
    "hash": "<sha256 of source file content>",
    "processed_at": "<ISO 8601 UTC>",
    "domain": "<one of the 10>",
    "merged_into": ["<playbook>/<file1>"],
    "scaffolded": true | false,
    "run_id": "<from input>"
  }
}
```

If the file already exists in the state file with a matching hash → skip processing entirely (idempotent). If hash differs → process again, overwrite the entry.

Use `python3 -c "..."` or `jq` to update the JSON atomically. Never overwrite the whole file — append/merge only.

#### 11. Append to operations log

One line, format:

```
YYYY-MM-DD HH:MM | auto-distill | <action> | <source filename> | <domain> → <playbook>/<topic-file(s)>; <merged|scaffolded|cross-linked>; <N insights merged>
```

#### 12. Output (stdout)

For the cron log, output a single one-line confirmation:

```
[auto-distill] <source> → <playbook>/<file(s)> (<N insights>)
```

Or for skips:

```
[auto-distill] <source> already processed (hash match), skipping
```

### Anti-patterns (avoid these)

- **One playbook per source.**
- **Re-stating existing content.** Search the target topic file first.
- **Praising the source in the playbook content.**
- **Writing narrative paragraphs.** If you can't turn the highlight into a structural artifact, ask whether it belongs in the playbook at all.
- **Asking the user for permission.** This is the headless variant — decide and act.
- **Editing the source file.**

### Edge cases

- **Source file is empty or has no highlights** → append to `_unrouted-distill-queue.md` with reason "no extractable content"; mark processed.
- **Source domain doesn't match any of the 10** → append to `_unrouted-distill-queue.md`; mark processed.
- **Hash matches existing state entry** → skip silently; output "already processed".
- **Target playbook README doesn't exist yet but folder does** (partial state from a prior failed run) → create the README, continue.
- **Source content is highly repetitive across many highlights** → merge once, don't generate 20 redundant rules.
- **Two equally dominant domains** → pick the more *operational* one (where decision rules fire) and cross-link the other.

---

## How to use this prompt with different tools

**Claude Code** (the primary supported runner):
Use the installable form at `skills/auto-playbook-distill.md`. The cron script invokes it via `claude -p "<prompt with source path>"`.

**Codex CLI**:
Save this file somewhere accessible. The cron script's `CLI_BIN` variable can point at the Codex CLI binary instead. The Codex invocation receives the same source-file prompt and processes it identically.

**Other agents**:
Any agent that supports headless single-shot prompts and has Read/Write/Edit/Bash-equivalent tools can run this workflow. Update the cron runner script's `CLI_BIN` accordingly and ensure the agent has filesystem access to the vault.
