---
name: auto-playbook-distill
description: Headless distill of a single Readwise file (article, book highlights, tweet thread) into the right cross-vault playbook. Classifies the source's domain against the 10-domain taxonomy in Vault/Playbooks-Index.md, scaffolds a new playbook if the domain has no playbook yet, merges insights into operational format (scorecards, decision triggers, anti-patterns, fillable templates), source-tags every claim, and records the file as processed in ~/.claude/state/distilled-readwise.json. Invoked headless from the daily auto-distill cron.
version: 1.0.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Auto Playbook Distill

The headless / cron variant of `/playbook-distill`. The interactive version asks the user where to merge and confirms creates. This version decides on its own using the 10-domain taxonomy and writes a one-line entry to `Vault/log.md` documenting the decision.

## Input format

The user message contains:
- A line `Source file: <absolute path>` — the Readwise file (article / book / tweet collection)
- (Optional) `Strictness: loose | strict` — defaults to `loose`
- (Optional) `Run id: <uuid>` — for idempotency tracking

## Hard rules (enforced)

1. **NEVER edit files in `Vault/Reading/`.** Readwise regenerates them on sync — any edits are wiped. Read-only on the source.
2. **NEVER delete anything.** No file removal under any circumstance.
3. **NEVER create more than one new playbook in a single run.** If the source spans multiple new domains, route to the dominant one and append the secondary to `Vault/raw-sources/_unrouted-distill-queue.md` for the next run.
4. **NEVER skip the source tag.** Every merged claim must end with `[<source title>, <date>]`. Untagged content is a bug.
5. **NEVER fabricate quotes.** Distillations paraphrase highlights into operational rules; direct quotes from the highlight bullets must be reproduced verbatim if used.
6. **One source file = one run.** Don't go reading other Readwise files for context.
7. **NEVER use `mv` on existing vault folders.** A prior incident moved 5 top-level vault folders into a stray wrapper because Bash `mv` was used during scaffolding. The ONLY allowed Bash filesystem operations during scaffolding are: `mkdir -p <full absolute target path>` and `ls -la` for verification. Use `Write` (not `mv`) to create new files. Use `Edit` (not `mv` or `cp`) to update existing files.
8. **ALWAYS use absolute paths for `mkdir -p`.** Never use relative paths or `cd` followed by `mkdir`. The risk: cwd may not be the vault root.
9. **Verify the playbook path BEFORE creating it.** Run `ls -la <parent dir>` to confirm the parent exists at the expected location. If it doesn't, abort and queue the source to `_unrouted-distill-queue.md` instead of inferring an alternative path.

## Workflow

### 1. Read the routing index

Always start with `Vault/Playbooks-Index.md`. It contains:
- The 10 playbook domains and their paths
- Routing rules (single domain vs. spanning vs. unrouted)
- Per-playbook conventions

### 2. Read the source file

Use `Read` on the `Source file:` path. Note:
- Author, title, category from the metadata block
- The `## Highlights` section — this is the operational substrate
- Any tags or topics

### 3. Classify the domain

Pick **one primary domain** from the 10. Heuristics:

- **Startup**: founder essays, GTM frameworks, pitch teardowns, AI maturity, B2B / SaaS
- **Investing**: investor biographies, valuation, market history, capital allocation
- **Health**: nutrition, exercise, biomechanics, sleep, longevity, mental health
- **Parenting**: child development, education methods (Doman, Montessori), early learning
- **Writing**: style, voice, rhetoric, copywriting, narrative theory
- **Philosophy**: decision theory, epistemology, ethics, schools of thought
- **Politics + Economics**: monetary theory, trade, market design, policy critique
- **Leadership**: command, coaching, executive operating cadence, debrief
- **Personal OS**: time, attention, habits, knowledge management, systems thinking
- **Tech**: AI/ML, software architecture, agent design, dev tooling, technical writings

If the source spans 2 domains: pick the dominant one for primary merge. The secondary gets a cross-link in its relevant topic file.

If the source spans 3+ domains OR has no clear match: append to `Vault/raw-sources/_unrouted-distill-queue.md` (one line per file, with reason). Do not create an 11th playbook silently.

### 4. Determine target file inside the playbook

Read the target playbook's `README.md` (if it exists). Look for an existing topic file that matches the dimension of the new content.

- **Strong match (existing topic file)** → merge into it.
- **No matching topic file but playbook exists** → create a new topic file in the playbook. Update the README.
- **Playbook doesn't exist yet** → scaffold it (step 5).

### 5. Scaffold a new playbook (only if needed)

If the target playbook has no folder yet:

1. Create the directory at the path from `Playbooks-Index.md`.
2. Write `README.md` with:
   - Frontmatter (type: reference, status: active, classification: internal, dates, author, tags)
   - Domain headline
   - Empty file index
   - Empty task router (the user will fill in skill mappings later)
   - Conventions section (inherited from the standard playbook pattern — see playbook-readme-template.md)
   - Sources captured section
3. Create the first topic file (named after the dominant dimension of the source content, e.g., `nutrition-fundamentals.md` for a nutrition book).
4. Update `Vault/Playbooks-Index.md` "Active Playbook Status" table.

### 6. Distill into operational format

The playbook is for *use*, not reading. Convert highlights into:

- **Scorecards** (rate something 0–3 or 0–5 across dimensions)
- **Decision triggers** ("if X, then Y")
- **Anti-pattern detectors** (boolean checks for failure modes)
- **Fillable templates** (slot-in formats with examples)
- **Reference tables** (pattern → when it fits → example)

**Loose threshold (default):** include any insight that *might* be useful later, not just provable rules. Better to capture and prune than miss.

**Strict threshold:** only insights that yield a hard decision rule, scorecard row, anti-pattern detector, or fillable template.

Preserve named examples and specific numbers — they make patterns sticky. Preserve direct quotes when they carry the rule.

### 7. Source-tag every claim inline

Format: `[<short title>, <YYYY-MM-DD>]`. Use the source file's title and the file's modified date.

Examples:
- `[A Theory of Human Motivation, 2026-02-01]`
- `[How I AI — Jason Levin, 2026-05-03]`
- `[YC W26 batch, 2026-05-02]`

### 8. Update the playbook README

If you created a new topic file, update the playbook's README:
- Add to the file index
- Append to "Sources captured"

If you only merged into existing files, just append to "Sources captured."

### 9. Update `Vault/Playbooks-Index.md`

Update the "Active Playbook Status" table:
- Bump file count if a new topic file was created
- Set "Last Source Added" to the source title + today's date

### 10. Mark file as processed (state file)

Append to `~/.claude/state/distilled-readwise.json`:

```json
{
  "<absolute source path>": {
    "hash": "<sha256 of source file content>",
    "processed_at": "<ISO 8601 UTC>",
    "domain": "<one of the 10>",
    "merged_into": ["<playbook>/<file1>", "<playbook>/<file2>"],
    "scaffolded": true | false,
    "run_id": "<from input>"
  }
}
```

If the file already exists in the state file with a matching hash → skip processing entirely (idempotent). If hash differs (Readwise re-synced with new highlights) → process again, overwrite the entry.

Use `Bash` with `python3 -c "..."` or `jq` to update the JSON atomically. Never overwrite the whole file with `Write` — append/merge only.

### 11. Append to `Vault/log.md`

One line, format:

```
YYYY-MM-DD HH:MM | auto-distill | <action> | <source filename> | <domain> → <playbook>/<topic-file(s)>; <merged|scaffolded|cross-linked>; <N insights merged>
```

### 12. Output (stdout)

For the cron log, output a single one-line confirmation:

```
[auto-distill] <source> → <playbook>/<file(s)> (<N insights>)
```

Or for skips:

```
[auto-distill] <source> already processed (hash match), skipping
```

## Anti-Patterns (avoid these)

- **One playbook per source.** That recreates the chronological-archive problem the playbook system is built to avoid.
- **Re-stating existing content.** If the playbook already says it (search the target topic file first), skip — don't duplicate.
- **Praising the source in the playbook content.** "This great book argues..." is filler. State the rule, source-tag it, move on.
- **Writing narrative paragraphs.** If you can't turn the highlight into a scorecard / trigger / detector / template, ask: does this belong in the playbook at all? Loose threshold is "include if might be useful," not "include narrative summaries."
- **Asking the user for permission.** This is the headless variant. Decide and act. The runtime sees stdout + log.md.
- **Editing the source file.** It will be wiped on next Readwise sync.

## Edge cases

- **Source file is empty or has no highlights** → append to `_unrouted-distill-queue.md` with reason "no extractable content"; mark processed.
- **Source domain doesn't match any of the 10** → append to `_unrouted-distill-queue.md`; mark processed.
- **Hash matches existing state entry** → skip silently; output "already processed".
- **Target playbook README doesn't exist yet but folder does** (partial state from a prior failed run) → create the README, continue.
- **Source content is highly repetitive across many highlights** → merge once, don't generate 20 redundant rules.
- **Two equally dominant domains** → pick the more *operational* one (where decision rules fire) and cross-link the other.

## Reference: state file format

`~/.claude/state/distilled-readwise.json` is a single JSON object keyed by absolute source path:

```json
{
  "<absolute path>/Reading/Books/Be the Greatest Product Manager Ever.md": {
    "hash": "abc123...",
    "processed_at": "2026-05-04T07:32:15Z",
    "domain": "Startup",
    "merged_into": ["Company Building/Startup Playbook/ai-product-design-tenets.md"],
    "scaffolded": false,
    "run_id": "20260504-073200"
  }
}
```

To check if a file is already processed:

```bash
python3 -c "
import json, sys, hashlib
state_path = '<HOME>/.claude/state/distilled-readwise.json'
src_path = sys.argv[1]
try:
  with open(state_path) as f: state = json.load(f)
except FileNotFoundError: state = {}
with open(src_path, 'rb') as f: h = hashlib.sha256(f.read()).hexdigest()
if state.get(src_path, {}).get('hash') == h:
  print('SKIP')
else:
  print('PROCESS')
" "$SOURCE_PATH"
```
