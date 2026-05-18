# Classification Taxonomy

The skill classifies every cluster into exactly one of five **atom types**. Type determines routing. Type determines whether the pattern decays or persists. Type determines whether contradictions matter. Get the taxonomy right and the system stays coherent; conflate types and the auto-memory Router fills with noise.

---

## The five types

### Principle
A durable truth about a domain.

**Test:** Would this still be true in 12 months absent contrary evidence?

**Examples:**
- "Regulated SMBs require air-gap deployment."
- "Hourly billing undersells AI work."
- "Specific dollarized outcomes beat generic credibility roughly 10× in sophisticated-buyer conversion."

**Routing:** Distilled into the matching playbook (via `auto-playbook-distill` domain logic). Promoted to the auto-memory Knowledge Router if `mentions ≥3` AND surfaced across `≥2 ventures`.

**Decays?** No. Stays until contradicted by new evidence.

### Anti-pattern
A durable truth about *what doesn't work*.

**Test:** Same as principle — durable, generalizable, not state-dependent.

**Examples:**
- "Selling the platform instead of the labor gets the vendor absorbed in 12–18 months."
- "Skill instructions without anchored ❌/✅ examples produce unreliable output."

**Routing:** Same as principle.

**Why distinguish from principle?** Anti-patterns have detectors. The right routing target is often the playbook's **anti-patterns** topic file (a checklist of what to flag), not the principle's positive-rule destination.

### State
A current world state — a snapshot.

**Test:** Will this be true a year from now? If unsure, it's state.

**Examples:**
- "Acme is in active eval."
- "Q3 hiring frozen."
- "Bastion Phase 1 PRD in progress."

**Routing:** Appended to the relevant venture's `_learnings.md` Learnings section. **Not promoted** to the Router. State observations belong venture-local.

**Decays?** Yes. State changes. Old state shouldn't poison the Router.

### Commitment
A promise or decision with a binary resolution.

**Test:** Can this be marked "done" or "not done"?

**Examples:**
- "Promised SSO to Acme by Q3."
- "Decided to use JTBD format for PRDs after the QA loop on V1.4."
- "Sending pricing to Nano by Friday."

**Routing:** if a task-manager MCP is configured (Todoist, Linear, Things, etc.) AND the operator has defined a venture → destination mapping, a task is created there; otherwise this step is skipped. **Always**, a row is appended to the venture's `_learnings.md` Key Decisions table.

**Decays?** Resolves. Once the task is closed, the commitment is settled (the `_learnings.md` row stays as historical record).

### Open question
An unresolved question.

**Test:** Is there a question mark, explicit or implicit?

**Examples:**
- "Do credit unions buy on-prem differently than community banks?"
- "Is there a partner motion that beats direct sales for the SMB tier?"

**Routing:** Appended to the venture's `_learnings.md` Open Threads section.

**Decays?** Stays until answered. The next `auto-playbook-distill` or `learnings-resurface` run may answer it from new evidence — when it does, move to Key Decisions.

---

## Why type-specific routing matters

Each destination is shaped for the type it receives:

| Destination | Optimized for | Wrong type would... |
|---|---|---|
| Auto-memory Knowledge Router | Durable cross-venture truth, ≤200 lines total | Get noisy and useless if state lands here |
| Playbook (e.g., `pitch-anatomy.md`) | Operational rules / scorecards / detectors | Drown out actionable content if open questions land here |
| `_learnings.md` (Learnings section) | Per-venture running context | Lose its venture focus if generic principles land here |
| `_learnings.md` (Key Decisions) | Decisions and their dates | Pollute decision tracking if state observations land here |
| `_learnings.md` (Open Threads) | Live unresolved questions | Become unactionable if state observations land here |
| Task-manager MCP (optional) | Concrete actionable items | Become noise if state or principles land here |

Conflating types collapses the system. The taxonomy is what keeps each destination clean.

---

## The artifact-type / optimization-target check

Two atoms only cluster together if they operate on the **same artifact type** AND the **same optimization target**.

This prevents false clustering across surface-similar but semantically different domains:

| Artifact type | Optimization target |
|---|---|
| Marketing copy / decks / one-pagers | Voice, first-principles framing, authenticity |
| Skill logic / analysis output / backend automation | Soundness, gap detection, contradiction catching |
| Pricing / packaging / offer design | Buyer clarity, dollarized counterfactual |
| Visual design / brand identity | Differentiation, restraint |
| Product positioning / wedge | ICP-buyer specificity, defensibility |

**Worked example:** the skill caught a near-miss where two atoms — both about "multi-pass QA loops" — looked semantically similar but applied to different artifact types. One targeted *marketing copy* (where the goal is preserving voice and avoiding sycophancy); the other targeted *skill logic* (where the goal is catching gaps and contradictions). Clustering them would have produced a generic "QA loops are good" principle that's useless because it can't be operationalized in either domain. Splitting them into two clusters routed each to its own destination — `sense-of-style` for the prose side, `qa-loop` / `prd-review` for the logic side — and both produced actionable rules.

When in doubt, split the cluster. Two specific clusters beat one generic one.

---

## Contradiction detection (principle / anti-pattern only)

For each principle/anti-pattern cluster, the skill searches:
1. The auto-memory Router for opposing entries.
2. Existing playbook files for opposing rules.
3. The current corpus itself.

**Before flagging a contradiction**, the skill confirms it's real. A real contradiction holds *within the same artifact type and optimization target*. If the apparent contradiction is actually a category boundary (one rule for marketing copy, an opposite-sounding rule for skill logic), that's not a contradiction — it's two valid rules in two domains. The cluster gets split.

If the contradiction survives this check, the cluster is marked `status: contested`, the contradicting source is recorded, and the pattern surfaces for review. The skill **never auto-invalidates**.
