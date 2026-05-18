---
name: sense-of-style
description: Diagnose and rewrite prose using Steven Pinker's Sense of Style principles. Scores writing on 8 style dimensions, flags specific line-level problems (nominalizations, passive voice, hedges, broken topic chains, clichés), and produces a rewrite. Use on any prose document — PRDs, updates, posts, emails, essays — when the content is right but the writing is soft. Pairs with qa-loop (qa-loop fixes argument; sense-of-style fixes prose).
version: 1.0.0
allowed-tools: [Read, Write, Edit, Glob, Grep, AskUserQuestion]
---

> **Optional voice file:** If you maintain a personal voice file (your tone, vocabulary preferences, sentence-structure defaults), point this skill at it — by default look for `~/.claude/skills/_shared/voice.md`. The skill will enforce Pinker's principles on top of your voice — they should align, not conflict. If no voice file is configured, the skill falls back to Pinker-only enforcement (still useful, just less personalized). See `examples/voice-example-derek.md` for what a real voice file looks like; copy `examples/voice.template.md` as a starting point.

# Sense of Style — Prose Diagnostic & Rewrite

A style-focused quality pass grounded in Steven Pinker's *The Sense of Style*. Scores prose on 8 dimensions, flags line-level problems with concrete fixes, and produces a rewrite that preserves voice while killing the things that make writing soft.

## When to Use

Activate when:
- User says "run sense-of-style", "style pass", "tighten the prose", "Pinker this"
- Content is right but the writing feels bloated, academic, or soft
- Post-`qa-loop` polish — argument is sound, now fix the prose
- User invokes `/sense-of-style` with or without a file path

Do NOT use for:
- First drafts (generate content first)
- Pure content/argument problems (use `qa-loop`)
- Code review (prose only)

## How It Differs From qa-loop

| qa-loop | sense-of-style |
|---------|----------------|
| Scores argument, evidence, structure | Scores prose quality |
| Fixes "this claim is unsupported" | Fixes "this sentence is a nominalization swamp" |
| Asks "is this true?" | Asks "does this read well?" |
| Works on PM artifacts | Works on any prose |

Run them in sequence when polishing high-stakes writing: `qa-loop` first (fix the thinking), `sense-of-style` second (fix the writing).

---

## The 8 Scoring Dimensions

Each dimension scored 1–10. Target: all ≥ 8/10.

### 1. Classic Style
Writer and reader are equals looking at something concrete in the world. No throat-clearing, no "in this document I will argue," no meta-commentary.

**9/10:** "The auth middleware stores session tokens in plaintext. Legal flagged this in Q3."
**3/10:** "It is important to note that in this section we will be discussing certain concerns that have been raised regarding authentication."

### 2. Curse of Knowledge
Reader doesn't know what you know. Jargon gets defined, abstractions get examples, references get context.

**Flags:** unexplained acronyms, insider shorthand, abstract concepts without grounding examples, assumptions about reader's mental model.

### 3. Concreteness (Verbs & Nouns)
Nouns should be things you can point at. Verbs should be actions. Kill nominalizations.

**Common fixes:**
- "make a decision" → "decide"
- "provide clarification" → "clarify"
- "the implementation of" → "implementing" or just "we built"
- "utilization of the framework" → "using the framework"

### 4. Active Voice & Named Agents
Default to active. Name who's doing what. Passive is legitimate only when the patient is the topic or the agent is unknown/irrelevant.

**Flags:** "it was decided that," "mistakes were made," agentless passives, abstract subjects doing abstract things.

### 5. Given-Before-New (Topic Chains)
Each sentence starts with what the reader already knows, ends with new information. Broken topic chains = reader feels lost without knowing why.

**Flags:** paragraphs where each sentence introduces a fresh subject, missing connective tissue, jumps that require the reader to reconstruct the link.

### 6. Syntax Load & Rhythm
Shallow syntax trees. Heavy phrases at the end, not the front. Vary sentence length. Short sentences land. Long sentences explain.

**Flags:** heavy left-branching, garden-path sentences, stacks of prepositional phrases, uniform sentence length across a paragraph.

### 7. Word Economy
Every word earns its place. Cut hedges, metadiscourse, and filler.

**Cut list:**
- Hedges: "somewhat," "rather," "arguably," "in some sense," "kind of"
- Intensifiers that weaken: "very," "really," "quite," "basically," "actually," "just"
- Metadiscourse: "it is important to note," "as mentioned above," "in this section"
- Bloat: "in order to" → "to"; "due to the fact that" → "because"; "at this point in time" → "now"

### 8. Freshness (No Clichés, No Bureaucratese)
Dead language signals dead thinking. Stock phrases get replaced with the specific thing you actually mean.

**Flags:** "at the end of the day," "move the needle," "unlock value," "leverage synergies," "best-in-class," "going forward," "circle back," "touch base."

---

## Workflow

1. **Load document** (file path or inline content)
2. **Diagnostic pass** — line-level flags with specific problems
3. **Score** all 8 dimensions with evidence quotes
4. **Ask** user: diagnostic only, full rewrite, or section-by-section?
5. **Rewrite** (if requested) preserving voice
6. **Re-score** and output changelog

---

## Step 1: Load Document

**File mode:** `/sense-of-style /path/to/draft.md`
**Inline mode:** `/sense-of-style` (operates on most recently written/edited content in conversation)

If document is > 3000 words, ask whether to process whole doc or target a specific section.

---

## Step 2: Diagnostic Pass

Scan the document and flag concrete line-level problems. Output as a table, grouped by dimension. Every flag must quote the actual text and propose a specific fix.

**Output format:**

```markdown
## Diagnostic Flags

### Nominalizations (Concreteness)
| Line/Quote | Problem | Fix |
|------------|---------|-----|
| "The implementation of the new framework..." | Zombie noun "implementation" | "We built the new framework..." |
| "Utilization of the tool has increased" | "Utilization" hiding the verb | "More people use the tool" |

### Passive Voice (Active Voice)
| Line/Quote | Problem | Fix |
|------------|---------|-----|
| "It was decided that we would ship Friday" | Agentless passive | "Leadership decided to ship Friday" |

### Hedges & Metadiscourse (Word Economy)
| Line/Quote | Problem | Fix |
|------------|---------|-----|
| "It is important to note that users..." | Pure metadiscourse | [delete — say it directly] |
| "This is arguably somewhat concerning" | Double hedge | "This is a problem" |

### Clichés & Bureaucratese (Freshness)
| Line/Quote | Problem | Fix |
|------------|---------|-----|
| "We need to move the needle on engagement" | Cliché | "Engagement is flat at 12% — we need it above 25%" |

### Curse of Knowledge
| Line/Quote | Problem | Fix |
|------------|---------|-----|
| "The LTV:CAC ratio is underwater" | Unexplained jargon for mixed audience | Define on first use or replace |

### Broken Topic Chains (Given-Before-New)
| Paragraph | Problem | Fix |
|-----------|---------|-----|
| Para 3 | Each sentence introduces a new subject; reader has to reconstruct connection | Reorder so each sentence picks up the previous sentence's topic |

### Syntax Load
| Line/Quote | Problem | Fix |
|------------|---------|-----|
| [long heavy sentence] | 4 prepositional phrases stacked | Break into two sentences, move heavy phrase to end |

### Classic Style Violations
| Line/Quote | Problem | Fix |
|------------|---------|-----|
| "In this document we will examine..." | Throat-clearing | Delete; start with the substance |
```

If a dimension has zero flags, mark it clean and skip the section.

---

## Step 3: Score

Score each of the 8 dimensions 1–10, with a one-line rationale and one representative quote.

**Output:**

```markdown
## Style Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Classic Style | X/10 | "[quote]" — [why this score] |
| 2 | Curse of Knowledge | X/10 | "[quote]" — [why this score] |
| 3 | Concreteness | X/10 | "[quote]" — [why this score] |
| 4 | Active Voice | X/10 | "[quote]" — [why this score] |
| 5 | Given-Before-New | X/10 | "[paragraph ref]" — [why this score] |
| 6 | Syntax Load | X/10 | "[quote]" — [why this score] |
| 7 | Word Economy | X/10 | "[quote]" — [why this score] |
| 8 | Freshness | X/10 | "[quote]" — [why this score] |

**Overall:** [sum]/80 ([%])
**Weakest dimensions:** [top 3 to target]
```

---

## Step 4: Ask User How to Proceed

```yaml
questions:
  - question: "Diagnostic is complete. How do you want to proceed?"
    header: "Next Step"
    multiSelect: false
    options:
      - label: "Full rewrite"
        description: "Rewrite the whole document fixing all flagged problems"
      - label: "Section-by-section"
        description: "Walk through sections; I approve each rewrite"
      - label: "Diagnostic only"
        description: "Just the flags and scores — I'll rewrite myself"
      - label: "Target weakest dimensions"
        description: "Only rewrite sentences flagged on the 3 lowest-scoring dimensions"
```

---

## Step 5: Rewrite

**Rules for rewriting:**

1. **Preserve the author's voice.** If the draft is direct and profane, the rewrite is direct and profane. Pinker's principles serve voice, not replace it.
2. **Fix flagged problems only.** Don't rewrite clean sentences. Don't add content. Don't change the argument.
3. **Tighten aggressively.** Expect 15–30% word reduction.
4. **Preserve specificity.** Numbers, names, dates, quotes stay exact.
5. **One idea per sentence.** Break up stacked clauses when they exceed working-memory capacity.

**Output format:**

```markdown
## Rewrite

### Changes Summary
- Cut X words ([percentage]% reduction)
- Fixed [N] nominalizations, [N] passives, [N] hedges, [N] clichés
- Restructured [N] paragraphs for topic chain coherence

### Side-by-Side (Notable Changes)

**Change 1: [dimension]**
- Before: "[original]"
- After: "[rewrite]"

**Change 2: [dimension]**
- Before: "[original]"
- After: "[rewrite]"

[... show 5-10 representative changes, not every edit ...]

### Full Rewritten Document

[full rewrite]
```

---

## Step 6: Re-Score

Run scoring again on the rewrite. Output the score progression:

```markdown
## Score Progression

| Dimension | Before | After | Change |
|-----------|--------|-------|--------|
| Classic Style | X/10 | X/10 | +X |
| ... | ... | ... | ... |

**Overall:** [before]/80 → [after]/80

**Still below 8/10:** [list any]
**Why:** [root cause — usually "requires author input" or "structural problem beyond prose"]
```

---

## Pinker's Bogus-Rules Ignore List

Do NOT flag these as problems. They are folklore, not grammar:

- Split infinitives ("to boldly go")
- Ending sentences with prepositions
- Starting sentences with "and," "but," or "because"
- Singular "they"
- Using "which" restrictively
- Contractions in formal writing
- First-person "I" in any context

If the author uses these, leave them alone. If someone else flagged them, note that the rule is bogus.

---

## File Handling

**If input was a file path:**

```yaml
questions:
  - question: "How should I save the rewrite?"
    header: "Save"
    multiSelect: false
    options:
      - label: "Overwrite original"
        description: "Replace the original file with the rewrite"
      - label: "Save as new file"
        description: "Save as [original]-styled.md alongside original"
      - label: "Output inline only"
        description: "Don't save; just show in conversation"
```

**If inline:** Output the rewrite in the conversation. Don't create a file unless asked.

---

## Edge Cases

**Document is already tight:** If overall score is ≥ 72/80 on initial pass, report "no rewrite needed" with the diagnostic. Don't manufacture changes.

**Voice conflicts with Pinker:** If a user's configured voice file (e.g., direct, first-principles, occasionally profane — classic style) would be softened by a Pinker principle, **keep the voice.** The principles serve the voice. This is the most important rule of the skill: never sand down a writer's signal in the name of "style."

**Technical document with unavoidable jargon:** Flag curse-of-knowledge for the intended audience only. A PRD for engineers can assume engineering terms. A pitch deck for executives cannot.

**Creative or stylistic breaks:** If the author deliberately uses a fragment, a long sentence, or a cliché for effect, leave it. Flag only if the break seems accidental.

---

## Example Invocations

**Polish a blog post:**
```
/sense-of-style /path/to/draft-post.md
```

**Inline on a just-written email:**
```
[write email in conversation]
/sense-of-style
```

**After qa-loop:**
```
/qa-loop /path/to/prd.md    → fixes argument
/sense-of-style             → fixes prose
```

---

*Based on Steven Pinker, The Sense of Style (2014). This skill operationalizes 8 of Pinker's core principles as a scoring rubric and rewrite engine. It preserves voice; it kills bloat.*

## Antipatterns to avoid

- **Sanding down voice in the name of "style."** If the user writes punchy fragments, don't lengthen them. If they curse for emphasis, don't sanitize. Style serves voice.
- **Manufacturing problems on tight prose.** If overall score is ≥ 72/80, report "no rewrite needed." Don't justify your existence with cosmetic changes.
- **Treating Pinker's principles as commandments.** They're heuristics. If the writer broke one deliberately and it works, leave it. Flag only when the break feels accidental.
- **Rewriting for an audience the document isn't aimed at.** A PRD for engineers can assume engineering terms. A pitch deck for executives cannot. Calibrate curse-of-knowledge to the *intended* reader.
