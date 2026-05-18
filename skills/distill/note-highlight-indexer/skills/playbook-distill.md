---
name: playbook-distill
description: Use this skill when the user pastes content (an article, an essay, transcript excerpt, slide quote, book passage, podcast notes, framework, anything) and signals they want to keep it for future reuse. Classifies the source against the 10-domain taxonomy in Vault/Playbooks-Index.md, scaffolds a new playbook if needed, merges insights into operational format (scorecards, decision triggers, anti-patterns, fillable templates), and source-tags every claim. ACTIVATE on any of these natural-language triggers when content is pasted or referenced - "/playbook-distill", "add this to the playbook", "distill this", "store this", "save this", "capture this", "keep this", "file this", "stash this", "operationalize this", "playbook this", "make a note of this", "hold onto this", or any clear "I want this captured for later" intent paired with substantive content. DO NOT activate for - "save this file" (Write tool), "remember this" / "remember X" (those are memory or _learnings.md updates, distinct subsystem), or storage requests for non-knowledge content (URLs, code snippets, calendar items).
version: 1.0.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Playbook Distill — Capture Pasted Content into the Right Playbook

The interactive variant. Use when the user pastes content directly into a Claude Code session and wants it filed into the playbook system in real time.

The companion `auto-playbook-distill` is the headless cron variant for batch-processing Readwise files. This one is for in-the-moment paste-ins of anything else.

## When to Use

Activate when the user:
- Invokes `/playbook-distill` explicitly
- Pastes content (article, essay, framework, transcript excerpt, slide quote, book passage, tweet thread, podcast notes, anything) AND signals an intent to keep/distill/operationalize it for future reuse
- Uses any of these natural-language triggers paired with content: "add this to the playbook", "distill this", "store this", "save this", "capture this", "keep this", "file this", "stash this", "operationalize this", "playbook this", "make a note of this", "hold onto this"

Do NOT activate for:
- Notes about a single project (those go in that project's `_learnings.md`)
- Meeting summaries (use a dedicated meeting-summary skill)
- Voice memos (use a dedicated voice-memo skill)
- "Save this file" / "save this code" — that's a Write request, not a knowledge-capture request
- **"Remember this" / "remember X"** — these belong to the memory subsystem (auto-memory updates, or `_learnings.md` appends for project-specific facts). The playbook system is for cross-domain operational rules; memory is for user/project facts. Do not blur them.
- Storage of non-knowledge artifacts (raw URLs without commentary, code snippets, calendar items, contact info) — those don't distill into operational rules

## When the trigger is ambiguous

A casual "store this" can mean many things. Before doing the full workflow, briefly check that you have:
1. **Substantive content** — pasted text, a referenced file, or content visible in the conversation context that has operational value (rules, frameworks, decision patterns, named examples). NOT a one-line link or a code blob.
2. **Reuse intent** — the user wants this for future application, not just to save a file or acknowledge they read something.

If both check out → proceed silently and report the merge summary. If only one or neither → ask one clarifying question before doing anything irreversible. Example: "Want me to distill this into the [Tech | Startup | etc.] playbook, or is this a different kind of save?"

Strong signal that the skill SHOULD fire: any of the trigger phrases above + a paste >100 words of operational/conceptual content.

Strong signal that the skill should NOT fire: trigger phrases without content, or content without trigger phrases (just because someone shared an article doesn't mean they want it in the playbook — they have to signal the intent).

## Vault Paths

- **Routing index:** `<your-vault>/Playbooks-Index.md`
- **Playbook root:** `<your-vault>/<domain folder>/<Playbook Name>/` (per Playbooks-Index.md)
- **Operations log:** `<your-vault>/log.md`
- **Raw source archive (optional):** `<your-vault>/raw-sources/`
- **Unrouted queue:** `<your-vault>/raw-sources/_unrouted-distill-queue.md`

(Update these to match your vault layout.)

## Workflow

### 1. Read the routing index first

Always start by reading `<your-vault>/Playbooks-Index.md`. It contains:
- The 10 playbook domains and their paths
- Routing rules (single domain vs. spanning vs. unrouted)
- Per-playbook conventions

Don't skip this — it's how you avoid creating an 11th playbook silently or routing the same content twice.

### 2. Read the pasted content

The user's paste is the substrate. Note:
- Domain signals (who/what is mentioned, the kind of insight, the named tools or frameworks)
- Whether it's narrative or operational (decisions / scorecards / rules already present?)
- Whether it cites a source — capture the source name + date inline if so

### 3. Classify the domain

Pick **one primary domain** from the 10 in `Playbooks-Index.md`. Heuristics:

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

If the source spans 3+ domains OR has no clear match: confirm with the user before doing anything. Default action if user agrees: append to `<your-vault>/raw-sources/_unrouted-distill-queue.md` (one line per file, with reason). Do not create an 11th playbook silently.

### 4. Determine target file inside the playbook

Read the target playbook's `README.md` (if it exists). Look for an existing topic file that matches the dimension of the new content.

- **Strong match (existing topic file)** → merge into it.
- **No matching topic file but playbook exists** → create a new topic file in the playbook. Update the README.
- **Playbook doesn't exist yet** → scaffold it (step 5).

### 5. Scaffold a new playbook (only if needed)

If the target playbook has no folder yet:

1. Create the directory at the path from `Playbooks-Index.md` (use absolute paths, never `cd`).
2. Write `README.md` using the structure from `playbook-readme-template.md`:
   - Frontmatter (type: reference, status: active, classification: internal, dates, author, tags)
   - Domain headline
   - Empty file index
   - Empty task router (the user fills in skill mappings later)
   - Conventions section
   - Sources captured section
3. Create the first topic file (named after the dominant dimension of the source content, e.g., `nutrition-fundamentals.md` for a nutrition piece, `pricing-and-business-model.md` for pricing content).
4. Update `<your-vault>/Playbooks-Index.md` "Active Playbook Status" table.

### 6. Read existing target file(s) before merging

For every file you plan to update, read it fully. You're checking for:
- Duplicate concepts (skip them, don't re-state)
- Adjacent sections where new content extends an existing pattern (merge, don't append a new section)
- Source tags already present (preserve them)

### 7. Distill into operational format

The playbook is for *use*, not reading. Convert narrative content into one or more of:

- **Scorecards** (rate something 0–3 or 0–5 across dimensions, with thresholds)
- **Decision triggers** ("if X, then Y")
- **Anti-pattern detectors** (boolean checks for failure modes)
- **Fillable templates** (slot-in formats with examples)
- **Reference tables** (pattern → when it fits → example)

Preserve named examples and specific numbers — they make patterns sticky. Cut purely narrative passages that don't yield a decision rule.

If the paste is short or anecdotal and yields zero structural artifacts: ask the user whether it belongs in the playbook at all, or whether it's better filed in a project's `_learnings.md`.

### 8. Source-tag every insight inline

Format: `[<short title>, <YYYY-MM-DD>]`. Examples:
- `[YC W26 batch, 2026-05-02]`
- `[a16z 2025-Q4 GTM post, 2026-04-15]`
- `[First Round essay, 2026-05-02]`
- If the user pasted without naming a source: ask for the source name + date *after* completing the merge. Use a placeholder `[unattributed paste, 2026-05-04]` until they provide one.

### 9. Update the playbook README

If you created a new topic file, update the playbook's README:
- Add to the file index
- Append to "Sources captured"

If you only merged into existing files, just append to "Sources captured."

### 10. Update `<your-vault>/Playbooks-Index.md`

Update the "Active Playbook Status" table:
- Bump file count if a new topic file was created
- Bump file count if you scaffolded a brand-new playbook
- Set "Last Source Added" to the source title + today's date

### 11. (Optional) Save the raw paste

If the user pasted substantial source text (vs. a link), offer to save it to `<your-vault>/raw-sources/YYYY-MM-DD-[slug].md` with frontmatter for attribution. Don't do this silently — confirm first if the paste is >500 words.

### 12. Append to vault operations log

Append a dated line to `<your-vault>/log.md`:

```
YYYY-MM-DD HH:MM | playbook-distill | <action> | <source title> | <domain> → <playbook>/<topic-file(s)>; <merged|scaffolded|cross-linked>; <N insights merged>
```

### 13. Report back

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

## Conventions (enforced)

- **No new file unless no existing file fits.** The whole point of the playbook is one synthesized knowledge per dimension.
- **No 11th domain silently.** If the content doesn't fit the 10 domains, queue and confirm — don't invent a domain.
- **Operational format only.** No narrative paragraphs unless they support a decision rule. If you can't turn it into a scorecard, trigger, or detector, ask whether it belongs in the playbook at all.
- **Source-tag every claim inline.** Untagged content is a bug.
- **Frontmatter must match existing files.** Type, status, classification, author, tags follow the established schema.
- **README is the single source of truth for the file list.** Update it whenever the file set changes.

## Anti-Patterns (avoid these)

- **One file per paste.** This recreates the chronological-archive problem the playbook is built to avoid.
- **Re-stating existing content with new wording.** If the playbook already says it, link to it. Don't re-write.
- **Adding a TL;DR summary at the top of a topic file.** The structure is the summary; a TL;DR is filler.
- **Praising the source.** "This is a great article on..." is filler. State what the playbook gained, nothing more.
- **Asking for permission before merging routine content.** Auto-approve when the routing is clear. Show the diff in the closing summary. Only confirm when the routing is ambiguous (3+ domain spans, no-match cases, would-be-11th-domain).

## Example Invocation Flow

User pastes a YC batch analysis covering founder-market fit, GTM, pitch, pricing, and anti-patterns — and says "/playbook-distill"

1. Read `Playbooks-Index.md` → primary domain is **Startup**.
2. Read `Startup Playbook/README.md` → 9 existing files; 5 dimensions match (founder-market-fit, gtm-distribution, pitch-anatomy, pricing-and-business-model, anti-patterns).
3. Read all 5 target files.
4. Distill new content per file, identify net-new vs. duplicate, merge.
5. Update Startup Playbook README "Sources captured."
6. Update `Playbooks-Index.md` Active table.
7. Append to `log.md`.
8. Report: "Playbook updated. Domain: Startup. Playbook: Startup Playbook (existing). Merged into: founder-market-fit, gtm-distribution, pitch-anatomy, pricing-and-business-model, anti-patterns. Source: YC W26 batch [2026-05-02]. Insights merged: 14."

## Example — paste that scaffolds a new playbook

User pastes a long thread about classical-music conducting and says "/playbook-distill"

1. Read `Playbooks-Index.md` → no clear match in the 10 domains.
2. Confirm with user: "This doesn't fit the existing 10 domains (Startup / Investing / Health / Parenting / Writing / Philosophy / Politics+Econ / Leadership / Personal OS / Tech). Want to (a) queue it to the unrouted file for later review, (b) merge into the closest fit (Leadership? Writing?), or (c) we re-think the taxonomy?"
3. User says "merge into Leadership — conducting is operating discipline."
4. Proceed: read `Leadership Playbook/README.md`, find or create the relevant topic file, distill, source-tag, merge, update README, log.

The skill never expands the 10-domain taxonomy on its own. That's a deliberate constraint.
