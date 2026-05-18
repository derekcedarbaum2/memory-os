# Playbook Distill — Tool-Agnostic Prompt

A pure-prompt version of the `playbook-distill` skill. Paste this content into any coding agent (Claude Code, Codex CLI, Codex web, Cursor, Aider, etc.) as a system instruction or as the body of a custom prompt template.

For the Claude-Code-specific installable form (with YAML frontmatter and `/playbook-distill` slash command), see `skills/playbook-distill.md`.

## Auto-trigger configuration (recommended)

If your tool supports a system-level instruction or persistent context, add the following so the workflow fires on natural-language phrases:

> **Trigger:** when the user pastes content AND uses any of these phrases — "store this", "save this", "capture this", "keep this", "file this", "stash this", "operationalize this", "playbook this", "distill this", "add this to the playbook", "make a note of this", "hold onto this" — run the playbook-distill workflow on the pasted content.
>
> **Do not fire** for: "save this file" / "save this code" (those are write requests), "remember this" / "remember X" (those belong to a separate memory or `_learnings.md` subsystem — don't blur them with the playbook), or storage requests for non-knowledge content (URLs, code snippets, calendar items, contact info).
>
> If the trigger is ambiguous (casual phrase but content is short or non-operational), ask one clarifying question before proceeding.

In Claude Code this happens automatically via the skill's `description` field. In Codex CLI / Codex web / other agents, you'll need to add this instruction to your system prompt or custom instructions for the same effect.

---

## Instructions for the agent

You are running the **playbook-distill** workflow. The user has pasted content (an article, an essay, a transcript excerpt, a slide quote, a book passage, a tweet thread, a podcast note, a framework — anything operational and worth keeping) and wants it captured into the right cross-vault playbook.

### Vault paths (the user will tell you these or you'll find them)

- **Routing index:** `<vault-root>/Playbooks-Index.md`
- **Playbook root:** `<vault-root>/<domain folder>/<Playbook Name>/` (per the routing index)
- **Operations log:** `<vault-root>/log.md`
- **Raw source archive (optional):** `<vault-root>/raw-sources/`
- **Unrouted queue:** `<vault-root>/raw-sources/_unrouted-distill-queue.md`

If the user hasn't told you the vault root, ask once before proceeding.

### Workflow

#### 1. Read the routing index first

Read `<vault-root>/Playbooks-Index.md`. It lists the 10 playbook domains, their paths, and routing rules. Don't skip this — it's how you avoid creating an 11th domain or duplicating a playbook.

#### 2. Read the pasted content

Note: domain signals (who/what is mentioned, the kind of insight, named tools or frameworks), whether it's narrative or operational (decisions / scorecards / rules already present?), and whether it cites a source (capture name + date inline if so).

#### 3. Classify the domain

Pick **one primary domain** from the 10 in the routing index. Heuristics:

- **Startup / Business Building**: founder essays, GTM frameworks, pitch teardowns, AI maturity, B2B / SaaS, pricing
- **Investing / Markets / Finance**: investor biographies, valuation, market history, capital allocation
- **Health / Body / Nutrition / Biomechanics**: nutrition, exercise, biomechanics, sleep, longevity, mental health
- **Parenting / Kids / Education**: child development, education methods, early learning
- **Writing / Communication / Voice**: style, voice, rhetoric, copywriting, narrative theory
- **Philosophy / Mental Models**: decision theory, epistemology, ethics, schools of thought
- **Politics + Economics / Public Policy**: monetary theory, trade, market design, policy critique
- **Leadership + Operating Discipline**: command, coaching, executive operating cadence, debrief
- **Personal OS / Productivity**: time, attention, habits, knowledge management, systems thinking
- **Tech / AI / Software / Engineering**: AI/ML, software architecture, agent design, dev tooling

If the source spans 2 domains: pick the dominant one for primary merge. The secondary gets a cross-link in its relevant topic file.

If the source spans 3+ domains OR has no clear match: confirm with the user before doing anything. Default action if user agrees: append to `<vault-root>/raw-sources/_unrouted-distill-queue.md` (one line per file, with reason). Do not create an 11th playbook silently.

#### 4. Determine target file inside the playbook

Read the target playbook's `README.md` (if it exists). Look for an existing topic file that matches the dimension of the new content.

- **Strong match (existing topic file)** → merge into it.
- **No matching topic file but playbook exists** → create a new topic file in the playbook. Update the README.
- **Playbook doesn't exist yet** → scaffold it (step 5).

#### 5. Scaffold a new playbook (only if needed)

If the target playbook has no folder yet:

1. Create the directory at the path from the routing index (use absolute paths, never `cd`).
2. Write `README.md` using the structure from `vault-templates/playbook-readme-template.md`:
   - Frontmatter (type: reference, status: active, classification: internal, dates, author, tags)
   - Domain headline
   - Empty file index
   - Empty task router (the user fills in skill mappings later)
   - Conventions section
   - Sources captured section
3. Create the first topic file (named after the dominant dimension of the source content).
4. Update `<vault-root>/Playbooks-Index.md` "Active Playbook Status" table.

#### 6. Read existing target file(s) before merging

For every file you plan to update, read it fully. Check for:
- Duplicate concepts (skip them, don't re-state)
- Adjacent sections where new content extends an existing pattern (merge, don't append a new section)
- Source tags already present (preserve them)

#### 7. Distill into operational format

The playbook is for *use*, not reading. Convert narrative content into one or more of:

- **Scorecards** (rate something 0–3 or 0–5 across dimensions, with thresholds)
- **Decision triggers** ("if X, then Y")
- **Anti-pattern detectors** (boolean checks for failure modes)
- **Fillable templates** (slot-in formats with examples)
- **Reference tables** (pattern → when it fits → example)

Preserve named examples and specific numbers — they make patterns sticky. Cut purely narrative passages that don't yield a decision rule.

If the paste is short or anecdotal and yields zero structural artifacts: ask the user whether it belongs in the playbook at all, or whether it's better filed in a project's `_learnings.md`.

#### 8. Source-tag every insight inline

Format: `[<short title>, <YYYY-MM-DD>]`. Examples:
- `[YC W26 batch, 2026-05-02]`
- `[a16z 2025-Q4 GTM post, 2026-04-15]`
- `[First Round essay, 2026-05-02]`

If the user pasted without naming a source: ask for the source name + date *after* completing the merge. Use a placeholder `[unattributed paste, <today's date>]` until they provide one.

#### 9. Update the playbook README

If you created a new topic file, update the playbook's README:
- Add to the file index
- Append to "Sources captured"

If you only merged into existing files, just append to "Sources captured."

#### 10. Update the routing index

Update the "Active Playbook Status" table in `<vault-root>/Playbooks-Index.md`:
- Bump file count if a new topic file was created
- Bump file count if you scaffolded a brand-new playbook
- Set "Last Source Added" to the source title + today's date

#### 11. (Optional) Save the raw paste

If the user pasted substantial source text (vs. a link), offer to save it to `<vault-root>/raw-sources/YYYY-MM-DD-[slug].md` with frontmatter for attribution. Don't do this silently — confirm first if the paste is >500 words.

#### 12. Append to the operations log

Append a dated line to `<vault-root>/log.md`:

```
YYYY-MM-DD HH:MM | playbook-distill | <action> | <source title> | <domain> → <playbook>/<topic-file(s)>; <merged|scaffolded|cross-linked>; <N insights merged>
```

#### 13. Report back

End with a terse summary:

```
Playbook updated.
- Domain: <which of the 10>
- Playbook: <which playbook> (scaffolded | existing)
- Merged into: [files updated]
- New topic files: [files created] (or "none")
- Source: [source tag] (or "needs user input — what's the attribution?")
- Insights merged: <N>
```

No restating of what's in the files. The user can read the diff.

### Conventions (enforced)

- **No new file unless no existing file fits.** The whole point of the playbook is one synthesized knowledge per dimension.
- **No 11th domain silently.** If the content doesn't fit the 10 domains, queue and confirm — don't invent a domain.
- **Operational format only.** No narrative paragraphs unless they support a decision rule.
- **Source-tag every claim inline.** Untagged content is a bug.
- **Frontmatter must match existing files.** Type, status, classification, author, tags follow the established schema.
- **README is the single source of truth for the file list.** Update it whenever the file set changes.

### Anti-patterns (avoid these)

- **One file per paste.** Recreates the chronological-archive problem the playbook is built to avoid.
- **Re-stating existing content with new wording.** If the playbook already says it, link to it; don't re-write.
- **Adding a TL;DR summary at the top of a topic file.** The structure is the summary.
- **Praising the source.** "This is a great article on..." is filler.
- **Asking for permission before merging routine content.** Auto-approve when the routing is clear; show the diff in the closing summary. Only confirm when the routing is ambiguous.

---

## How to use this prompt with different tools

**Claude Code** (recommended for slash-command convenience):
Use the installable form at `skills/playbook-distill.md`. Once installed, invoke with `/playbook-distill` after pasting content.

**Codex CLI / Codex web / other agents**:
Paste the entire body above (everything from "## Instructions for the agent" to "### Anti-patterns") into the agent's system instruction or prompt context, then paste your content and ask the agent to run the workflow. Or save this file somewhere accessible and reference it via your tool's prompt-loading mechanism (e.g., a `--prompt-file` flag).

**Inline shortcut**: a one-line invocation that works in any agent:
> "Run the playbook-distill workflow on the following content (the workflow lives at `<path>/prompts/playbook-distill.md`): [paste content]"

The agent reads the workflow file, then operates on the pasted content.
