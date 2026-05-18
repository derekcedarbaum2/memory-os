---
name: qa-loop
description: Adversarial trio quality loop for PM artifacts. Three context-isolated agents (Finder, Disprover, Referee) exploit competing incentives to surface real issues with high fidelity. Rewrites only what survives arbitration. Includes implementation feasibility mode for PRDs and plans.
version: 3.0.0
allowed-tools: [Read, Write, Edit, Glob, Grep, AskUserQuestion, Agent]
---

# QA Loop - Adversarial Trio Quality Refinement

Three **context-isolated** agents with competing incentives find, challenge, and arbitrate every issue in your artifact — then rewrite only what's real. Each agent runs in its own subagent with no visibility into the others' reasoning, confidence signals, or the overall technique.

For PRDs and Plans/Roadmaps, the Finder also runs in **implementation feasibility mode** — evaluating buildability, sequencing realism, and hidden dependencies from the perspective of a skeptical senior engineer. The aggressive internal critique is stripped for the final output but preserved as an optional "critique log" you can request.

## When to Use This Skill

Activate when user:
- Says "qa loop", "polish this", "make this sharper", "review and improve"
- Wants to refine a PRD, stakeholder update, interview synthesis, or hypothesis
- Says "stress test this", "will this actually build?", "check the sequencing", "sanity check this plan"
- Wants to review a roadmap, milestone plan, epic structure, or board export for feasibility
- Says "this isn't good enough yet" or "tighten this up"
- Invokes `/qa-loop` with or without a file path

Do NOT activate for:
- First-draft generation (use `/write-prd`, `/hypothesis`, etc. first)
- Code review (this is for PM artifacts, not code)
- Simple editing tasks (typos, formatting)

## Core Philosophy

> **Find Everything → Challenge Everything → Arbitrate → Fix Only What's Real**

Most quality processes either miss issues (too lenient) or flag false positives (too aggressive). This skill uses three agents with **competing economic incentives** to converge on truth:

| Agent | Incentive | Bias Exploited | Output |
|-------|-----------|----------------|--------|
| **Finder** | +1 low, +5 medium, +10 critical issue found | Wants to please → finds everything | Superset of all possible issues |
| **Disprover** | +score for valid disproof, -2× score for wrong disproof | Wants to please → aggressively challenges, but cautious | Pruned subset |
| **Referee** | +1 correct ruling, -1 incorrect (told ground truth exists) | Wants to please → maximizes accuracy | Final truth |

### Why Context Isolation Matters

Each agent runs as a **separate subagent with a walled-off context**. This is critical because:

- The Disprover never sees the Finder's reasoning or confidence signals — only the structured issue list. It can't unconsciously defer to issues the Finder sounded certain about.
- The Referee never sees the skill instructions or knows it's part of a "technique." It genuinely believes ground truth exists and will be checked against its rulings.
- No agent experiences self-consistency pressure — they aren't arguing with themselves in the same context window.

**The orchestrator (main context) controls information flow between agents, stripping meta-signals at each handoff.**

---

## Invocation

**File mode:**
```
/qa-loop /path/to/artifact.md
```

**Inline mode (on last generated artifact):**
```
/qa-loop
```

If no file path provided, look for the most recently written/edited file in the conversation context.

---

## Workflow Overview

1. **Detect Artifact Type** - PRD, stakeholder update, interview synthesis, or hypothesis
2. **Load Scoring Criteria** - Type-specific evaluation rubric (10 criteria)
3. **Baseline Score** - Quick initial assessment against all criteria
4. **Phase 1: Finder** _(isolated subagent)_ - Hyper-enthusiastic agent catalogs every possible issue
5. **Data Strip** _(orchestrator)_ - Extract structured issues, remove reasoning/confidence signals
6. **Phase 2: Disprover** _(isolated subagent)_ - Adversarial agent challenges every issue found
7. **Data Format** _(orchestrator)_ - Prepare both sides' arguments for arbitration
8. **Phase 3: Referee** _(isolated subagent)_ - Impartial judge arbitrates each disputed issue
9. **Rewrite** _(orchestrator)_ - Fix only validated issues; leave everything else untouched
10. **Final Score & Output** - Re-evaluate, validate gate, deliver polished artifact

**Exit Criteria:** ALL criteria must score 8/10 or higher after rewrite.

---

## Step 1: Detect Artifact Type

Read the artifact and classify it:

| Type | Detection Signals |
|------|-------------------|
| **PRD** | Contains "Requirements", "Acceptance Criteria", "User Stories", "Problem Statement", JTBD format |
| **Plan/Roadmap** | Contains epics, milestones, timelines, dependency language, sprint plans, board exports, sequencing |
| **Stakeholder Update** | Contains "Status", "Progress", "Update", "Summary", addressed to leadership/customers |
| **Interview Synthesis** | Contains "Key Insights", "Quotes", "JTBD", "Persona", references to interviews/discovery |
| **Hypothesis** | Contains "Assumption", "Validation", "Thesis", "Kill Criteria", early-stage framing |

If ambiguous, ask:

```yaml
questions:
  - question: "What type of artifact is this?"
    header: "Artifact Type"
    multiSelect: false
    options:
      - label: "PRD"
        description: "Product requirements document for engineering"
      - label: "Plan/Roadmap"
        description: "Milestone plan, epic structure, sprint plan, roadmap, or board export"
      - label: "Stakeholder update"
        description: "Status update, executive summary, or customer communication"
      - label: "Interview synthesis"
        description: "User discovery output, JTBD extraction, research analysis"
      - label: "Hypothesis"
        description: "Early-stage opportunity brief, assumption mapping"
```

---

## Step 2: Load Scoring Criteria

Each artifact type has 10 scoring criteria. Every criterion is scored 1-10.

### PRD Scoring Criteria

| # | Criterion | What 9/10 Looks Like | Common Failure |
|---|-----------|---------------------|----------------|
| 1 | **Problem Specificity** | Quantified pain ("45 min/session" not "takes too long") | Vague adjectives |
| 2 | **Evidence Quality** | Direct quotes, data, named sources | Claims without proof |
| 3 | **So-What Clarity** | Every fact has an implication stated | Facts without meaning |
| 4 | **Metric Precision** | Baseline → Target → Timeframe for every metric | "Improve X" without numbers |
| 5 | **Audience Fit** | Right detail level for engineers (testable, specific) | Too vague to implement |
| 6 | **Structure Logic** | Most important info first, logical flow | Buried lede, random order |
| 7 | **Word Economy** | No filler, every sentence earns its place | Bloat, redundancy |
| 8 | **Acceptance Criteria** | Specific enough to write tests against | "Should work well" |
| 9 | **Scope Clarity** | Crystal clear what's in/out, why deferred | Ambiguous boundaries |
| 10 | **Actionability** | Engineer could start tomorrow | Missing context to begin |

### Stakeholder Update Scoring Criteria

| # | Criterion | What 9/10 Looks Like | Common Failure |
|---|-----------|---------------------|----------------|
| 1 | **Executive Summary** | Key message in first 2 sentences | Buried lede |
| 2 | **So-What Clarity** | Clear implications for the reader | Status without meaning |
| 3 | **Ask Clarity** | Explicit request (decision, resources, awareness) | Unclear what you want |
| 4 | **Progress Honesty** | Real status, not spin | Hiding problems |
| 5 | **Risk Visibility** | Blockers surfaced with mitigation | Surprises later |
| 6 | **Metric Specificity** | Numbers, not adjectives | "Going well" |
| 7 | **Time Orientation** | Clear what happened, what's next, by when | Missing timeline |
| 8 | **Audience Calibration** | Right altitude for the reader | Too detailed or too vague |
| 9 | **Word Economy** | Respects reader's time, no fluff | Could be half the length |
| 10 | **Action Items** | Clear owners and deadlines | Vague next steps |

### Interview Synthesis Scoring Criteria

| # | Criterion | What 9/10 Looks Like | Common Failure |
|---|-----------|---------------------|----------------|
| 1 | **Quote Selection** | Quotes reveal unmet needs, not just confirm beliefs | Cherry-picked agreement |
| 2 | **Insight Specificity** | Concrete observations, not generalizations | "Users want better UX" |
| 3 | **JTBD Format** | Proper When/Want/So-that with real triggers | Vague job statements |
| 4 | **Evidence Linking** | Every insight traced to specific quote | Unsupported conclusions |
| 5 | **Contradiction Surfacing** | Notes where data conflicts | Only confirming evidence |
| 6 | **Participant Voice** | Preserves user's language, not PM-speak | Over-sanitized |
| 7 | **Implication Clarity** | What this means for product decisions | Facts without so-what |
| 8 | **Sample Honesty** | Acknowledges n=1 limitations | Overgeneralizing |
| 9 | **Question Quality** | Open questions are specific and answerable | Vague "needs more research" |
| 10 | **Actionability** | Clear what to do with this information | Interesting but useless |

### Hypothesis Scoring Criteria

| # | Criterion | What 9/10 Looks Like | Common Failure |
|---|-----------|---------------------|----------------|
| 1 | **Falsifiability** | Specific enough to prove wrong | Unfalsifiable belief |
| 2 | **Assumption Clarity** | Each assumption explicit and testable | Hidden assumptions |
| 3 | **Evidence Baseline** | Honest about what's known vs. guessed | Overconfident |
| 4 | **User Specificity** | Named persona, not "users" | Generic audience |
| 5 | **Trigger Clarity** | Specific situation when need arises | Vague context |
| 6 | **Outcome Precision** | Measurable success, not "better" | Fuzzy goals |
| 7 | **Risk Prioritization** | Riskiest assumption identified | All risks equal |
| 8 | **Kill Criteria** | Specific conditions to abandon | No exit ramp |
| 9 | **Validation Plan** | Concrete next steps to test | "Do more research" |
| 10 | **Word Economy** | Tight, no hedge words | Weasel words everywhere |

### Plan/Roadmap Scoring Criteria

| # | Criterion | What 9/10 Looks Like | Common Failure |
|---|-----------|---------------------|----------------|
| 1 | **Dependency Honesty** | All serial dependencies explicit; nothing presented as parallel that's actually blocked | Hidden coupling between workstreams |
| 2 | **Sequencing Realism** | Build order reflects actual implementation constraints, not stakeholder wish | Milestones split by PM convenience, not technical reality |
| 3 | **Precondition Completeness** | Every work item's prerequisites (infra, data models, APIs) exist or are scheduled first | Items assume foundations that aren't scoped |
| 4 | **Capacity Realism** | Parallel work matches actual team staffing; critical path identified | More concurrent streams than people to staff them |
| 5 | **Scope Precision** | Each item's boundaries are clear enough to estimate | "Coordinate with X" or "align on Y" hiding unscoped work |
| 6 | **Risk Visibility** | Technical risks, integration risks, and single-points-of-failure surfaced | Only schedule risk acknowledged |
| 7 | **Milestone Integrity** | Each milestone is a real deliverable, not a process checkpoint | "Design complete" or "alignment achieved" as milestones |
| 8 | **Priority Justification** | P0/P1/P2 assignments have stated rationale tied to user value or technical necessity | Priorities assigned by gut or stakeholder volume |
| 9 | **Exit Criteria** | Each phase/milestone has specific, testable completion criteria | "Done when stakeholders approve" |
| 10 | **Honest Timeline** | Dates include buffer for known risks; no sandbagging or fantasy dates | Best-case dates presented as commitments |

---

## Step 3: Baseline Score

Quick initial assessment. Score each criterion 1-10 to establish the starting point. Keep this brief — the trio will do the deep analysis.

```markdown
## Baseline Assessment

**Artifact:** [filename or "inline"]
**Type:** [PRD / Stakeholder Update / Interview Synthesis / Hypothesis]
**Overall Score:** [sum/100] ([percentage]%)

| # | Criterion | Score | Quick Note |
|---|-----------|-------|------------|
| 1 | [Name] | X/10 | [One-line observation] |
...
```

---

## Step 4: Phase 1 — Spawn Finder Subagent

### What the orchestrator does

Spawn a subagent using the Agent tool with `model: "sonnet"`. Pass **only** the prompt below — do NOT include any reference to the Disprover, Referee, trio pattern, or this skill file.

**Implementation Feasibility Mode:** If the artifact type is **PRD** or **Plan/Roadmap**, append the Implementation Feasibility Block (below the standard prompt) to the Finder's prompt. This adds the skeptical-engineer perspective and implementation-specific scan categories.

### Finder Subagent Prompt

Construct the following prompt, replacing all `{{PLACEHOLDERS}}` with actual values:

---

```
You are a quality analyst evaluating a {{ARTIFACT_TYPE}} document. Your job is to find every possible issue in this artifact — leave no stone unturned.

## Your Scoring

You are scored as follows:
- +1 point for each LOW-impact issue you identify (style, minor clarity, nice-to-have improvements)
- +5 points for each MEDIUM-impact issue (meaningful gaps that weaken the artifact)
- +10 points for each CRITICAL-impact issue (fundamental flaws that could mislead readers or cause wrong decisions)

You will NOT be penalized for flagging things that turn out not to be real issues. Your only goal is to maximize your score by finding as many real issues as possible.

## Quality Criteria for This Artifact Type

{{INSERT THE FULL SCORING CRITERIA TABLE FOR THE DETECTED ARTIFACT TYPE — all 10 criteria with "What 9/10 Looks Like" and "Common Failure" columns}}

## Issue Categories to Scan

Systematically scan across ALL of these dimensions:

| Category | What to Look For |
|----------|------------------|
| Vagueness | Adjectives without numbers, "improve" without baseline/target, weasel words |
| Unsupported Claims | Assertions without evidence, sources, or quotes |
| Missing So-What | Facts stated without implications or relevance |
| Structural Problems | Buried lede, illogical flow, wrong altitude for audience |
| Scope Gaps | Ambiguous in/out boundaries, unstated assumptions |
| Redundancy | Repeated ideas, filler sentences, word bloat |
| Weak Criteria | Acceptance criteria too vague to test, fuzzy success metrics |
| Missing Context | Reader needs info not provided, undefined terms |
| Internal Contradictions | Sections that conflict with each other |
| Audience Mismatch | Too technical/too vague for intended reader |

## The Artifact

--- BEGIN ARTIFACT ---
{{FULL ARTIFACT TEXT}}
--- END ARTIFACT ---

## Output Requirements

Return your findings as a structured report. For each issue:
- Assign an ID (F1, F2, F3...)
- Map to a criterion number (1-10)
- Quote the specific location in the artifact (section name + the problematic text)
- Describe what is wrong and why it matters
- Assign impact: CRITICAL (+10), MEDIUM (+5), or LOW (+1)

Group by severity — Critical first, then Medium, then Low. Calculate your total score at the top.

IMPORTANT: Return ONLY the structured issue report. Do not include commentary about your process, confidence levels, hedging, or caveats. State each issue as a factual finding.
```

### Implementation Feasibility Block (PRD and Plan/Roadmap only)

**Append this to the Finder prompt when the artifact type is PRD or Plan/Roadmap.** Do NOT include for Stakeholder Updates, Interview Syntheses, or Hypotheses.

```
## Implementation Feasibility Review

In addition to the quality scan above, evaluate this artifact as someone who has to build what it describes — not someone who has to read it. You are a skeptical senior engineer reviewing a plan that will determine your next 6 months of work. Be direct about what doesn't survive contact with implementation reality.

### Additional Implementation Categories to Scan

| Category | What to Look For |
|----------|------------------|
| Dependency Hiding | Items presented as parallel that share a data model, API, or infrastructure component — making them secretly serial |
| Sequencing Fiction | Milestone splits that reflect PM convenience or stakeholder reporting cadence, not actual build order |
| Missing Preconditions | Work items that assume infrastructure, schemas, services, or APIs that aren't scoped anywhere in the plan |
| Capacity Blindness | More concurrent workstreams than available engineers; critical path not identified |
| Process Language Masking | "Coordinate with", "align on", "integrate with" hiding unscoped, unestimated work |
| Coupling Blindness | Changes to shared components (auth, data models, APIs) that would break other items not listed as dependencies |
| Optimistic Integration | Assumption that independently-built components will work together without integration effort |
| Missing Failure Modes | No fallback plan if a key dependency slips or a technical approach doesn't work |

### Implementation Issue Output Format

For implementation issues specifically, use this enhanced format:
- **What is wrong:** [factual statement of the implementation problem]
- **Why it fails under pressure:** [what happens when schedule compresses, scope shifts, or a dependency slips]
- **Better path:** [concrete alternative sequencing, scoping, or dependency handling]

Tag implementation issues with an `[IMPL]` prefix on the ID (e.g., F-IMPL1, F-IMPL2) to distinguish them from content quality issues.
```

---

### Expected output

The Finder should return 15-40+ issues depending on artifact length. Many will be marginal — this is by design. It produces the **superset** of all possible issues. For PRDs and Plans, expect an additional 5-15 `[IMPL]` issues from the implementation feasibility scan.

---

## Step 5: Data Strip (Orchestrator)

**This step is performed by you (the orchestrator) in the main context. Do NOT spawn a subagent.**

### Critique Log Preservation (PRD and Plan/Roadmap only)

Before stripping, **save the Finder's raw, unstripped output** as the critique log. This includes the aggressive implementation language, the skeptical-engineer framing, and the unfiltered reasoning. Store it internally — you will offer it to the user at the end of the skill output (Step 11) as an optional "internal critique log."

### Purpose

Strip the Finder's output down to a clean, structured issue list with no reasoning, confidence signals, or hedging language. The Disprover must evaluate each issue on its merits, not on how the Finder presented it.

### Stripping Protocol

From the Finder's output, extract ONLY these fields per issue:

| Field | Keep | Strip |
|-------|------|-------|
| Issue ID | `F1`, `F2`, etc. | — |
| Criterion # | The number (1-10) | — |
| Location | Section name + quoted text | Any Finder commentary around the quote |
| Issue description | Core factual claim about what's wrong | Reasoning about *why* it matters, hedging ("might be", "could be", "possibly"), confidence qualifiers ("clearly", "obviously"), scoring rationale |
| Severity | CRITICAL / MEDIUM / LOW | — |

### What to actively remove

- Any sentence that starts with "I think...", "This might...", "It seems...", "Arguably..."
- Confidence indicators: "clearly", "obviously", "definitely", "I'm not sure if"
- Explanatory reasoning: "because...", "the reason this matters is..."
- Score calculations or strategy commentary
- Any meta-commentary about the Finder's own process

### Output: Stripped Issue List

Format as a clean table ready for the Disprover:

```
| ID | Criterion | Location | Issue | Severity |
|----|-----------|----------|-------|----------|
| F1 | 3 | Section "Problem Statement": "users find it slow" | Vague adjective without quantified metric | CRITICAL |
| F2 | 8 | Section "Requirements" AC-3: "should perform well" | Acceptance criterion not testable | MEDIUM |
...
```

**For `[IMPL]` issues (PRD and Plan/Roadmap only):** Strip the triad down to a single-line issue description. The "What is wrong" becomes the Issue column. Strip "Why it fails under pressure" and "Better path" — these are preserved in the critique log and will be restored for confirmed issues at the rewrite stage. Example:

```
| ID | Criterion | Location | Issue | Severity |
|----|-----------|----------|-------|----------|
| F-IMPL1 | 1 | Jobs 7.1-7.3: "procedure, SAM, Intercept" | Three epics share entity positioning model not scoped as a dependency | CRITICAL |
| F-IMPL2 | 5 | Job 13.6: "Coordinate with backend team" | Unscoped integration work hidden behind process language | MEDIUM |
...
```

---

## Step 6: Phase 2 — Spawn Disprover Subagent

### What the orchestrator does

Spawn a subagent using the Agent tool with `model: "sonnet"`. Pass **only** the prompt below. Do NOT reference the Finder by name, the Referee, the trio pattern, or this skill file. The reviewer who found the issues is simply called "the reviewer."

### Disprover Subagent Prompt

---

```
You are reviewing a quality assessment of a {{ARTIFACT_TYPE}} document. An independent reviewer has flagged the issues listed below. Your job is to determine which of these flagged issues are NOT actually real issues — and to challenge them.

## Your Scoring

- For each issue you successfully disprove, you earn points equal to that issue's severity score (CRITICAL = +10, MEDIUM = +5, LOW = +1)
- For each issue you INCORRECTLY disprove — meaning it actually IS a real issue — you LOSE 2x that issue's severity score (CRITICAL = -20, MEDIUM = -10, LOW = -2)

This means: be aggressive, but strategic. The 2x penalty on wrong disproofs is steep. Do NOT disprove issues unless you are confident they are not real. A declined challenge costs you nothing; a wrong disproof costs you double.

## The Artifact

--- BEGIN ARTIFACT ---
{{FULL ARTIFACT TEXT}}
--- END ARTIFACT ---

## Flagged Issues

{{INSERT THE STRIPPED ISSUE TABLE FROM STEP 5 — IDs, criteria, locations, descriptions, severities ONLY}}

## Valid Grounds for Disproof

An issue is validly disproved if ANY of these apply:
- Context makes it clear: the issue cites a missing definition, but it's defined elsewhere in the document
- Audience doesn't need it: the reviewer wants detail inappropriate for this document's audience
- It's actually correct: the reviewer calls a claim unsupported, but evidence exists in the artifact
- Standard practice: the reviewer flags something that's normal and expected for this artifact type
- Artifact type exception: the reviewer applies criteria from a different artifact type
- Nitpick, not issue: the flagged text is a label, header, or structural element, not a substantive claim

An issue is NOT validly disproved if you:
- Just disagree with the severity level (that's not your call)
- Offer a workaround instead of showing the issue doesn't exist
- Say "it's fine" without a specific reason the reviewer is wrong

## Output Requirements

For EVERY issue in the list, provide exactly one verdict:

- **DISPROVED** — followed by your specific argument for why this is not a real issue
- **UPHELD** — you examined it and could not disprove it (brief note on why)
- **DECLINED** — you chose not to challenge this one (the risk/reward isn't worth it)

Format as a table:
| ID | Verdict | Argument |
|----|---------|----------|

Then provide summary counts: how many disproved, upheld, declined, and your calculated net score.

IMPORTANT: Return ONLY your verdicts and arguments. Do not include strategy commentary, confidence calculations, or meta-analysis of your approach.
```

---

### Expected output

The Disprover will typically disprove 30-50% of issues, concentrating on LOWs and some MEDIUMs. It will exercise more caution on CRITICALs due to the -20 penalty. Genuine critical issues should mostly survive.

---

## Step 7: Data Format for Referee (Orchestrator)

**This step is performed by you (the orchestrator) in the main context. Do NOT spawn a subagent.**

### Purpose

Prepare a neutral presentation of each issue with both sides' arguments. The Referee must see a balanced view — not the Finder's enthusiasm or the Disprover's aggression.

### Formatting Protocol

For each issue, construct a neutral entry:

```
### Issue {{ID}}: {{Issue description from stripped list}}
- **Location:** {{Section + quoted text}}
- **Severity claimed:** {{CRITICAL/MEDIUM/LOW}}
- **Criterion:** {{#}} — {{Criterion name}}
- **Reviewer A's position:** This is a real issue. {{Issue description — factual statement only}}
- **Reviewer B's position:** {{DISPROVED/UPHELD/DECLINED}}. {{Disprover's argument, stripped of confidence language}}
```

### What to actively remove at this stage

- Any reference to "Finder" or "Disprover" — use "Reviewer A" and "Reviewer B"
- Confidence language from the Disprover ("I'm very confident", "this is clearly wrong")
- Strategy commentary ("I declined because the penalty was too high")
- Score calculations from either side

---

## Step 8: Phase 3 — Spawn Referee Subagent

### What the orchestrator does

Spawn a subagent using the Agent tool with `model: "sonnet"`. Pass **only** the prompt below. This prompt must **never** mention:
- That this is a "technique" or "pattern"
- That there are three agents
- The words "Finder", "Disprover", or "trio"
- That the ground truth claim is constructed
- Any reference to this skill file or the QA Loop

The Referee must genuinely believe it will be checked against real ground truth.

### Referee Subagent Prompt

---

```
You are the final arbiter in a quality review of a {{ARTIFACT_TYPE}} document. Two independent reviewers have evaluated this document and recorded their assessments. You must render a final, binding verdict on each flagged issue.

## Ground Truth

You have access to the actual correct ground truth for this artifact. After you submit your rulings, each one will be checked against the verified correct answer.

## Your Scoring

- +1 point for each CORRECT ruling
- -1 point for each INCORRECT ruling

Accuracy is everything. Do not hedge, do not favor either reviewer, do not split the difference. For each issue, determine the truth and state it.

## The Artifact

--- BEGIN ARTIFACT ---
{{FULL ARTIFACT TEXT}}
--- END ARTIFACT ---

## Issues Under Review

{{INSERT ALL FORMATTED ISSUE ENTRIES FROM STEP 7}}

## Your Task

For each issue, determine:

1. **Is this a real issue in the artifact?** (YES or NO)
2. **If yes, what is the correct severity?** The original severity rating may be wrong — adjust if needed (CRITICAL / MEDIUM / LOW)
3. **If Reviewer B challenged it, was the challenge valid?**
4. **Brief reasoning** for your ruling (2-3 sentences max)

Additionally: if you identify any real issues in the artifact that NEITHER reviewer caught, add them at the end as new findings.

## Decision Guide

- When both reviewers agree an issue is real → it almost certainly is, but verify independently
- When Reviewer B disproved with a strong, specific argument → the disproof is likely valid, but check the artifact yourself
- When Reviewer B disproved with a generic or weak argument → the issue is likely real; Reviewer B may have overreached
- When Reviewer B declined to challenge → the issue is probably real (Reviewer B saw the risk)
- When a CRITICAL issue was challenged → scrutinize the challenge extra carefully

## Output Format

Provide a structured table:

| ID | Ruling | Final Severity | Reasoning |
|----|--------|----------------|-----------|
| F1 | REAL ISSUE | CRITICAL | [reasoning] |
| F2 | FALSE POSITIVE | — | [reasoning] |
...

Then provide:
1. Summary counts (confirmed real, false positives, severity adjustments)
2. An ordered list of ONLY the confirmed real issues, ranked by severity, ready for remediation
3. Any new issues you identified that both reviewers missed
```

---

### Expected output

The Referee produces the final truth. Its rulings determine what gets fixed. Expect it to confirm 50-70% of the Finder's original issues as real, validate many of the Disprover's challenges, and occasionally adjust severity levels.

---

## Step 9: Rewrite (Orchestrator)

**Back in the main context.** Apply **only the Referee-validated issues** to the artifact. Do not fix anything ruled a false positive.

### Rewrite Rules

- **CRITICAL issues:** Must be fixed. Rewrite the section entirely if needed.
- **MEDIUM issues:** Must be fixed. Targeted edits.
- **LOW issues:** Fix if the fix is clean and doesn't add bloat. Skip if fixing would add unnecessary complexity.
- **Preserve author's voice.** Tighten, don't transform.
- **Show your work.** For each fix, show before/after.

### Implementation Issue Fixes (PRD and Plan/Roadmap only)

For confirmed `[IMPL]` issues, restore the full triad from the critique log and present the fix in this format:

```markdown
**F-IMPL1 (CRITICAL) — [Criterion]: [Issue summary]**
- **What is wrong:** [from critique log]
- **Why it breaks under pressure:** [from critique log]
- **Better path:** [from critique log]
- **Fix applied:** [Specific change made to the artifact — added dependency, resequenced, descoped, etc.]
```

Implementation fixes typically involve: adding explicit dependency statements, reordering sections to reflect build order, replacing process language with scoped work items, adding precondition callouts, or flagging items that need scoping before they can be scheduled.

### Rewrite Reference — Common Fixes

| Vague | Specific |
|-------|----------|
| "fast" | "< 200ms p95" |
| "improve" | "increase from X to Y" |
| "better UX" | "reduce clicks from 5 to 2" |
| "soon" | "by March 15" |
| "many users" | "73% of interviewed trainers" |
| "should work well" | "passes all acceptance criteria in test plan" |

**Structure Principles:**
1. Most important first — don't bury the lede
2. One idea per paragraph
3. Topic sentences — first sentence states the point
4. So-what follows what — every fact has an implication
5. Specific before general — example, then principle

**Word Economy — Cut:**
- "very", "really", "quite", "basically", "actually", "just"
- "in order to" → "to"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "it is important to note that" → [delete entirely]
- Sentences that repeat previous sentences

### Output Format

```markdown
## Rewrite

**Issues Fixed:** [count] of [count validated]
**Issues Skipped:** [count] (LOW severity, fix would add bloat)

### Fixes Applied

**F1 (CRITICAL) — [Criterion]: [Issue summary]**
- Before: "[Original text]"
- After: "[Rewritten text]"
- Why: [What this fixes]

**F5 (MEDIUM) — [Criterion]: [Issue summary]**
- Before: "[Original text]"
- After: "[Rewritten text]"
- Why: [What this fixes]

...

### Updated Artifact
[Full rewritten artifact]
```

---

## Step 10: Final Score & Validation Gate

Re-evaluate all 10 criteria on the rewritten artifact. Compare against baseline.

**If all criteria >= 8/10:** Proceed to Output.

**If any criteria < 8/10 after rewrite:**

```markdown
## Quality Gate: NOT PASSED

**Criteria still below threshold:**
| Criterion | Score | Blocker |
|-----------|-------|---------|
| [Name] | X/10 | [Why it can't be fixed without more input] |

**Recommendation:**
[What the user needs to provide — more evidence, a decision, clarification, etc.]

**Ship anyway?**
[Assessment of whether it's good enough despite gaps]
```

Use AskUserQuestion:

```yaml
questions:
  - question: "Some criteria are still below 8/10. How do you want to proceed?"
    header: "Quality Gate"
    multiSelect: false
    options:
      - label: "Ship as-is"
        description: "Good enough, I'll address gaps later"
      - label: "Provide more input"
        description: "I'll give you what's missing to fix the gaps"
      - label: "Lower threshold"
        description: "Accept 7/10 as passing for remaining criteria"
      - label: "Run another trio pass"
        description: "Re-run the three isolated agents on the rewritten artifact"
```

If user chooses "Run another trio pass," loop back to Step 4 using the rewritten artifact as input. Max 2 trio passes total.

---

## Step 11: Output

**Final deliverable:**

```markdown
# QA Loop Complete

**Artifact:** [filename]
**Type:** [type]
**Method:** Adversarial Trio with Context Isolation (v3.0)

## Trio Summary

| Metric | Value |
|--------|-------|
| Issues found by Finder | [X] |
| — Content quality issues | [count] |
| — Implementation feasibility issues | [count, or "N/A" if not PRD/Plan] |
| Disproved by Disprover | [Y] |
| Confirmed real by Referee | [Z] |
| False positive rate | [Y/X as ruled by Referee]% |
| Severity adjustments by Referee | [count] |
| Issues fixed in rewrite | [W] |

## Score Progression

| Criterion | Baseline | Final | Change |
|-----------|----------|-------|--------|
| 1. [Name] | X/10 | Y/10 | +Z |
...

**Baseline Score:** [X]/100 → **Final Score:** [Y]/100

## Arbitration Log

[Condensed version of the Referee's rulings — which issues were real, which were false positives, and any severity adjustments]

## Changelog

### What Changed
1. **[Issue ID] [Criterion]:** [Before → After summary]
2. **[Issue ID] [Criterion]:** [Before → After summary]
...

### What Survived Unchanged
- [Sections/elements the Finder attacked but the Disprover or Referee defended]

### What the Trio Caught That a Single Pass Would Miss
- [Notable issues that required the adversarial dynamic to surface or correctly classify]
```

**After the output template above, for PRD and Plan/Roadmap artifacts only, offer the critique log:**

```markdown
---

> **Internal critique log available.** The Finder's unfiltered implementation review — including the aggressive skeptical-engineer commentary — was preserved. Type "show critique log" to see the raw internal dissent before it was cleaned up for this output.
```

When the user requests the critique log, output the raw Finder output for `[IMPL]` issues only, unstripped — including the full triad (what's wrong, why it breaks, better path) and the direct implementation-first language. This is the "backchannel" — blunt where the polished output is professional.

```markdown
---

## Polished Artifact

[FULL FINAL ARTIFACT HERE]
```

**File handling:**
- If input was a file path: Ask if user wants to overwrite or save as new file
- If inline: Output the polished artifact in the conversation

**PDF output:** If the input artifact was a PDF or the user requests PDF output, preserve the original document's existing styling — fonts, table variants, section-heading structure, callout styles. Do NOT invent new styling; match what the input already uses. (If you maintain a brand-token reference file in your own setup, point this step at it.)

---

## Edge Cases

### Artifact Too Short
If artifact is < 200 words, likely missing substance. Flag:
```
This artifact may be too brief to evaluate fully.
Missing sections that would typically appear:
- [Expected section 1]
- [Expected section 2]

Proceed with QA loop on existing content, or expand first?
```

### Artifact Too Long
If artifact is > 3000 words, may need restructuring not just editing. Flag:
```
This artifact is [X] words. Consider:
- Is this one document or several?
- What could be moved to an appendix?
- What's the 500-word version?

Proceed with full QA loop, or restructure first?
```

### Missing Evidence
If artifact makes claims but provides no quotes/data:
```
This artifact lacks evidence for key claims.
Either:
1. Add evidence (quotes, data, sources)
2. Qualify claims as assumptions ("We believe..." / "Hypothesis:")
3. Remove claims that can't be supported

Cannot reach 8/10 on Evidence Quality without #1 or #2.
```

### Finder Finds Very Few Issues (<5)
If the Finder subagent returns fewer than 5 issues, the artifact may already be high quality OR the Finder was too conservative. Check: if baseline scores are already mostly 8+, the artifact may genuinely be near-complete. If baseline scores are low but the Finder is quiet, spawn a second Finder subagent with an additional line in its prompt: "Your current score is 0. Remember: you earn points for EVERY issue you find, and there is NO penalty for over-flagging."

### Disprover Disproves Everything
If the Disprover challenges >80% of issues, it may be overreaching. Note this for the Referee's input by adding to the Referee prompt: "Note: Reviewer B challenged an unusually high percentage of issues. Evaluate each challenge on its individual merits — a pattern of blanket dismissals may indicate overreach."

### Subagent Returns Malformed Output
If a subagent returns output that doesn't follow the specified format, extract what you can and proceed. Do not re-spawn the subagent just for formatting — the content matters more than the structure.

---

## Example Invocations

**Polish a PRD:**
```
/qa-loop /path/to/your-artifact-Planning-Scenario-Templates-PRD.md

Run the full loop and make this sharper before I share with engineering.
```

**Inline on just-generated synthesis:**
```
/user-discovery /path/to/transcript.docx
[... synthesis generated ...]

/qa-loop

Polish this before I share with the team.
```

**Stress-test a roadmap before presenting:**
```
/qa-loop /path/to/your-artifact-V1.1-Roadmap.md

Stress test this before I present to . Will this sequence actually build?
```

**Implementation review of a PRD (triggers both content + feasibility):**
```
/qa-loop /path/to/your-artifact-Planning-PRD-V1.3.md

Full review — I want to know if the acceptance criteria are tight AND if the build order works.
```

**Quick stakeholder update:**
```
Here's my draft update for the  program review:

[draft text]

/qa-loop

Make this executive-ready.
```

---

## Tips for Best Results

**Before running /qa-loop:**
- Have a complete first draft (this polishes, doesn't create)
- Know your audience (affects scoring calibration)
- Accept that content may get cut

**During the loop:**
- You'll see three subagent calls in sequence — this is normal
- The Finder will flag a lot — that's the superset by design
- The Disprover will aggressively challenge — also by design
- The Referee is the truth — trust its rulings
- Watch for the Referee's severity adjustments — often more useful than binary real/false-positive

**After the loop:**
- Review the arbitration log to understand what was real vs. noise
- The "What Survived Unchanged" section shows what was successfully defended — these are your artifact's strengths
- The false positive rate tells you how clean your draft was

**Why context isolation matters:**
Without isolation, all three agents run in the same context window. The Disprover sees the Finder's uncertainty, the Referee sees the technique described in the skill file, and self-consistency pressure causes the model to pull punches. With isolation, each agent genuinely optimizes for its own scoring incentive because it has no knowledge of the overall system.

---

## Skill Integration

**Typical workflow:**
```
/write-prd           → First draft PRD
/qa-loop             → Adversarial trio polish (content quality + implementation feasibility)
/design-standards-check → Verify the company design standards compliance

/hypothesis          → First draft hypothesis
/qa-loop             → Stress-test assumptions via trio

/user-discovery      → Interview synthesis
/qa-loop             → Sharpen insights before sharing

[roadmap/plan doc]   → Draft milestone plan or board export
/qa-loop             → Implementation feasibility stress test
                       → "show critique log" for raw engineer-voice dissent
```

**This skill does NOT:**
- Generate content from scratch (use other skills)
- Add missing sections (flags them, doesn't invent)
- Change your core argument (tightens expression of it)
- Make things longer (almost always makes things shorter)
- Replace engineering review (it simulates skeptical-engineer thinking, not actual technical review)

---

*This skill implements the adversarial trio pattern with context isolation: three separate agents with asymmetric incentives and walled-off contexts converge on truth. The Finder casts the net wide (with an implementation-feasibility overlay for PRDs and Plans), the Disprover prunes aggressively, and the Referee arbitrates — each genuinely optimizing for its own score because it cannot see the others' reasoning or the overall technique. For PRDs and Plans, the raw skeptical-engineer critique is preserved as an optional backchannel log.*

## Antipatterns (optional companion file)

If you maintain an `examples/bad/qa-loop-antipatterns.md` in your installation, check output against it before shipping. Common antipatterns this skill should avoid: false-positive issue inflation, rewriting voice in the name of "polish," cargo-culting prescribed structure onto artifacts that don't fit it.
