# Applied Claim Test — "Knowledge graph tracks state across conversations"

A worked example of applying the five-rule design DNA *as a critique tool*, not a software design tool. The pattern is generative beyond skills: it's a discipline for stress-testing any agent-system claim.

This example tests a marketing claim made about a third-party product (Rowboat) — that "a knowledge graph of typed entities tracks ground truth across conversations, while a wiki of summaries does not." The claim is the kind of thing that sounds right and goes unchallenged in agent-system writing. We run it through the five rules to see what survives.

This isn't about Rowboat specifically. It's about how to apply this pattern's discipline to evaluate any "our system handles X" claim before adopting it.

## The claim

> A wiki page about "Project X" gives you a summary of what was discussed.
> But a knowledge graph gives you every decision made, who made it, what was promised, when it was promised, and **whether anything has shifted since**.
>
> *(Source: third-party article promoting a knowledge-graph-based agent memory system.)*

The implicit position: knowledge graphs of typed entities (People/, Projects/, Decisions/) are *categorically better* than wikis at tracking state, because the graph "extends nodes" rather than compiling pages.

## Why this is the kind of claim worth running through the pattern

The claim is a category claim ("knowledge graphs strictly dominate wikis at state tracking"). Category claims fail or survive on structural arguments, not anecdotes. The five-rule pattern is structurally suited to category claims because it forces argument-vs-counterargument under separated incentives.

Single-pass review fails here for the same reason it fails on artifacts: a friendly single agent will accept the framing, an adversarial single agent will reject everything reflexively. We need *separated* roles.

## Running the rules

### Rule 1 — Context isolation

Three contexts, none seeing each others' reasoning:

- **Defender** — assigned to make the strongest case the claim is true.
- **Challenger** — assigned to find structural reasons the claim collapses.
- **Referee** — sees only the claims, not the reasoning, and rules.

For a category claim like this, the Challenger's job is to find the case the Defender's framing assumes away.

### Rule 2 — Competing incentives

| Agent | Incentive |
|---|---|
| Defender | +1 per supporting structural argument; no penalty for over-arguing. |
| Challenger | +score per valid structural rebuttal that survives Defender's counter-counter; **−2× penalty for invalid rebuttals.** |
| Referee | +1 per correct ruling; −1 per incorrect (told ground truth exists). |

The asymmetric penalty on the Challenger is what stops it from blanket-rejecting the claim. Only structural rebuttals it can defend get scored.

### Rule 3 — Direction assignment, not opinion query

We do **not** ask any agent "is this claim true?" We assign:

- Defender: "Steel-man this claim. Build the strongest argument it is structurally true."
- Challenger: "Find the structural cases this claim assumes away."

The model is competent at advocacy in either direction; we just don't let one model do both.

### Rule 4 — Arbitration by a structurally-different agent

The Referee:
- Sees only the structured claim list (no reasoning, no anecdotes).
- Is told its ruling will be checked against ground truth (it won't be — but the framing makes correctness dominant).
- Is given a binary verdict requirement per claim: SURVIVES / COLLAPSES / DEPENDS-ON.

## What the run produced

### Defender's strongest argument (steel-manned)

A typed-entity knowledge graph stores each decision, commitment, and deadline as a discrete node with provenance and timestamps. When two sources contradict, the graph has both as separate atoms attached to the same entity, with their dates. A wiki page compiles inputs into a single narrative — by definition, it loses the multiplicity that state tracking requires. **Therefore, graphs structurally dominate wikis at tracking state across conversations.**

### Challenger's structural rebuttals

**Rebuttal 1 — The dichotomy is false.** "Wiki" and "knowledge graph" are not categorically distinct architectures; they're two points on a granularity axis. A wiki page compiled from typed atomic notes (one note per decision, one per commitment) has the same state-tracking properties as a graph traversal. A graph that summarizes attached atoms into a single rendered "Sarah Chen overview" has the same flattening properties as a wiki. The architectural fact is *granularity of input*, not graph-vs-wiki.

**Rebuttal 2 — "Extends nodes" is hand-waving over the hard problem.** When a new email arrives that contradicts a prior commitment, the claim says the graph "extends the node." But *extends how*? Append both as line items? That's a wiki. Replace the prior with the new? That's lossy. Annotate with a contradiction flag? That requires arbitration — which is exactly where wikis fail too. The graph framing doesn't solve state drift; it relocates it.

**Rebuttal 3 — The article's own example doesn't survive.** The article cites: "a deadline agreed in one email thread and moved to a later date in another thread, while the team still assumed the original date." A knowledge graph extracting both emails atomically has Decision[deadline=A] and Decision[deadline=B] as separate nodes. **The graph does not know which is current.** The agent at query time still has to reason about it — which is exactly what a wiki-with-source-tagged-atoms also does. The "graph tracks ground truth" claim conflates *storing both states* with *knowing which is current*.

**Rebuttal 4 — Cadence dominates structure.** Periodic regeneration of a wiki from atomic source notes (the [`note-highlight-indexer`](https://github.com/derekcedarbaum2/note-highlight-indexer) + [`learnings-resurface`](https://github.com/derekcedarbaum2/learnings-resurface) pattern) tracks state better than a graph that grows monotonically without reconciliation. A wiki regenerated weekly from sources beats a graph that never reconciles. The architectural fact that determines state-tracking quality is *regeneration cadence*, not graph-vs-wiki.

### Defender's counter-counters

To Rebuttal 1: graphs make granularity *enforced* by structure (every decision is a node). Wikis allow it but don't require it.
To Rebuttal 2: granted, but typed entities provide a place for arbitration to run.
To Rebuttal 3: granted at query time, but the graph at least has both states stored.
To Rebuttal 4: graph regen cadence can be just as fast.

### Referee's ruling

| Claim | Verdict | Reason |
|---|---|---|
| "Graphs structurally dominate wikis at state tracking." | **COLLAPSES** | Survives only the version where graph = high granularity + reconciliation; that version applies equally to atomic wikis. The structural claim doesn't survive Rebuttal 1 + 4. |
| "Graphs store contradictions natively." | **SURVIVES** (weakly) | True that typed-entity nodes give a natural attachment point. Same is achievable in a wiki with source-tagged atoms; the difference is enforcement, not capability. |
| "Wikis lose multiplicity." | **DEPENDS-ON** | Depends entirely on how the wiki is constructed. A wiki regenerated from atomic sources retains multiplicity; a wiki of hand-written summaries does not. The claim is true of *one* wiki implementation, not wikis as a category. |
| "Graph tracking solves drift." | **COLLAPSES** | Storage ≠ tracking. The graph stores both Decision[A] and Decision[B]; arbitration of which is current is a separate operation that graphs do not provide. |

## What survived

A weaker version of the claim survives:
- **Typed entities make granularity enforced rather than aspirational.** True.
- **Storage of contradictions is easier with typed nodes.** True but available to atomic wikis too.

What did not survive:
- **Categorical superiority of graphs over wikis for state.** Failed on the granularity argument.
- **"Graph tracks ground truth."** Failed on the storage-vs-arbitration argument.

The honest framing: the relevant axis is *regeneration cadence and atomic granularity*, not *graph vs. wiki*. Two systems can be both atomic and regenerated; either can do the job.

## Why this exercise matters for the family

This applied test demonstrates a non-obvious property of the pattern:

**The five rules are a critical-thinking discipline, not just a software architecture.** Any time you encounter a category claim about agent systems — *"X is strictly better than Y at Z"* — you can:

1. Steel-man it (Defender role) — required, because most category claims are partially true.
2. Find the assumed-away cases (Challenger role) — required, because category claims that survive single-pass evaluation almost always have hidden conditionals.
3. Adjudicate per-claim, not in aggregate (Referee role) — required, because most claims have surviving and collapsing parts.

When evaluating whether to adopt an agent-system pattern, run the claim through this lens before committing engineering time. Single-pass evaluation will accept the framing. The pattern's separated incentives surface what the framing assumed away.

## What changes in this ecosystem as a result

- The [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) README now distinguishes **memory** (persistent, append-only) from **regenerated artifacts** (whole-file overwritten on schedule). This is the surviving distinction from the test — granularity + regeneration cadence are the real axes, and our system already runs both (memory tiers + Today.md/Playbooks-Index.md as regenerated artifacts).
- Naming `Today.md` an *ephemeral artifact* rather than a "fourth memory tier" is a direct consequence of taking the test seriously — the article wanted to call it memory; it isn't.

## When to run a claim test like this

Use this pattern when:

- A vendor / article makes a category claim about agent architecture ("X dominates Y at Z").
- A recommended pattern would require non-trivial engineering to adopt.
- The claim's framing already feels familiar — that's exactly when single-pass evaluation accepts it without scrutiny.

Don't use this pattern when:

- The claim is narrow and empirical ("this benchmark improved by N%"). Run an experiment, not a debate.
- You've already adopted the pattern and just need to optimize. Adversarial framing ossifies an existing choice rather than evaluating it.

---

*See `qa-loop-design-notes.md` for the family's first prose-quality member, `pressure-test-design-notes.md` for the lens-based variant. This file is the first **applied critique** example — using the five rules as a thinking tool, not a software design.*
