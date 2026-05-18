# `/pressure-test` — Design Notes

The directional-defensibility sibling. Where `qa-loop` polishes prose and `prd-review` checks stakeholder readiness, `pressure-test` answers a different shape of question entirely:

> "Is this position defensible, and where are the real fault lines?"

## The Karpathy observation that motivated it

> *LLMs are extremely competent at arguing almost any direction.*

This is usually framed as a weakness — sycophancy, lack of conviction, willingness to defend nonsense. But it's also a structural feature. If you tell one agent to argue *for* a position and another to argue *against*, both will argue at full strength because both are doing what you asked. The model's eagerness to please is now load-bearing — it produces stronger arguments on both sides than a single agent ever could on either.

The anti-sycophancy mechanism is structural: agents are *told* which direction to argue, never *asked* what they think.

## The two orthogonal axes

`pressure-test` has two design axes that compose:

### Axis 1 — Direction

What position to argue:
- **For** — argue strongly in favor
- **Against** — argue strongly against
- **Null** — argue that the choice doesn't matter (no action / status quo / underspecified)
- **Alternative** — argue for a specific other path not in the original framing

### Axis 2 — Lens (persona)

From whose perspective:
- **CRO** — revenue, deal velocity, commercial risk
- **Legal** — liability, compliance, contract structure
- **Cyber / Security** — threat model, blast radius, attack surface
- **VP Engineering** — buildability, ops, on-call burden
- **VP Design** — user surface, friction, brand fit
- **End User** — daily experience, friction, trust
- **Competitor** — opening it gives a rival, mimic risk
- **Custom** — any persona the user defines

You can use either axis or both:

| Configuration | Setup | Useful for |
|---|---|---|
| **Direction only** | "Argue for and against migrating to microservices" — 2 agents, no persona | Generic strategic decision |
| **Lens only** | "Evaluate this pricing decision as CRO, Legal, and Customer Success" — 3 agents, each with their natural bias | Stakeholder impact map |
| **Direction × Lens** | "Argue for this acquisition from Legal's perspective AND against it from Legal's perspective" — forces the LLM out of default framing for that role | The real sycophancy killer — breaks "Legal would obviously say X" |

The Direction × Lens combo is the deepest test. It surfaces the cases where the *role* has a default framing that makes you think you've already considered the role's view, but the role can actually argue both directions credibly.

## How this differs from the prose-quality and stakeholder-readiness siblings

| Dimension | `qa-loop` | `prd-review` | `pressure-test` |
|---|---|---|---|
| Question | "Is this prose good?" | "Would approvers sign off?" | "Is this position defensible?" |
| Input | An artifact (prose document) | A PRD specifically | A position / argument / decision (often just text) |
| Output shape | Polished artifact | Pass/fail report | What survived, what crumbled, what's underdetermined |
| Verdict? | Yes (issues are validated or rejected) | Yes (per-approver pass/fail) | **No — the skill reports the topology, not a winner** |
| Composes with | Most other skills | `qa-loop`, `pressure-test` | Most other skills, especially before commitment |

The big design call: **`pressure-test` does not pick a winner.** This is intentional. A skill that picks a winner re-introduces sycophancy at the meta-level — "the user must want me to confirm their position, so I'll arbitrate in their favor." Instead, the Referee maps:

- What survived adversarial pressure on both sides (the durable claims)
- What crumbled (claims that fall under scrutiny from any direction)
- What's underdetermined (the real fault lines — where both arguments are credible)

The user uses this map to decide. The skill's job is to make sure no one direction was unfairly steel-manned.

## Specific design choices and why

**Why steel-man and not straw-man?** Asking an agent to argue against a position weakly produces a weak strawman that the for-side easily defeats. Telling an agent "argue this position as strongly as possible — your job is to build the best case, not to find weaknesses in it" produces credible adversarial input. The structural symmetry (every direction gets the same instruction) is what keeps the Referee's arbitration fair.

**Why does the Null direction exist?** Most strategic decisions implicitly assume "we must do something." The Null agent's job is to argue for the do-nothing / status-quo case, which is often stronger than people expect. Including it surfaces the "are we sure we even need to act?" question that gets skipped when the For/Against framing is taken as exhaustive.

**Why the Custom lens?** The named lenses (CRO, Legal, Cyber, etc.) cover the most common stakeholder roles, but real organizations have specific personas that matter — "the chief of staff who blocks anything that adds meeting load," "the engineering culture that distrusts vendor lock-in," "the founding customer who would feel betrayed by a pivot." The Custom lens lets the user inject these.

**Why arrays of (Direction, Lens) pairs at runtime?** A pressure test isn't one configuration — it's a matrix. The orchestrator typically runs 3–6 (Direction, Lens) pairs in parallel, then the Referee synthesizes. Skipping pairs (e.g., only running For/Against without lenses) loses the role-perspective coverage; running all combinations is cost-prohibitive. The right matrix is question-specific.

## Failure modes observed

- **Steel-man becomes straw-man under pressure:** if the For agent isn't given enough context, it argues a generic version of the position that the Against agent easily defeats. Fix: feed each agent the full position document, not a summary.
- **Lens defaults override direction assignment:** "argue *for* this acquisition from Legal's perspective" sometimes produces "Legal would say no for these reasons." The agent reverts to the lens's natural opinion. Fix: explicit instruction in the prompt that direction overrides default lens framing — "Legal can argue both directions; here you are arguing for."
- **Referee picks a winner anyway:** "what survived adversarial pressure" sometimes gets compressed into "side X won." Fix: explicit Referee output schema with three sections — Surviving Claims, Crumbled Claims, Fault Lines (Underdetermined). The schema enforces the topology, not a winner.

## Pre-flight: artifact type detection

The skill works on:
- **Text positions** — pasted argument, hypothesis, recommendation
- **File-based arguments** — PRDs, strategy memos, decision documents

For file-based input, the skill loads the file plus any referenced supporting docs. For text input, it asks the user one clarifying question (the question being tested) before spawning agents.

## Where this composes in a stack

A common workflow:

1. **Generate** the position (write-prd / hypothesis / strategy memo).
2. **`qa-loop`** for prose quality.
3. **`pressure-test`** for directional defensibility — surfaces what would crumble before commitment.
4. **Address fault lines** — the user uses the pressure-test report to strengthen weak claims, drop crumbled ones, and explicitly address underdetermined issues.
5. **`prd-review`** if the artifact is a PRD heading to approvers.

Each pass is ~5–15 minutes of agent runtime. The compounding effect is real: an artifact that survives all three passes is meaningfully harder to attack than one that survived just generation.
