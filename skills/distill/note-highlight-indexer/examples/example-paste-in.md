# Example — Manual Paste-In Session

> **Note on this example:** the pasted content below is a *synthetic* essay excerpt written for demonstration. The attribution `[Example Pricing Essay, 2026-05-04]` is intentionally fictional — there is no "Example Pricing Essay" to find. The point is to show the shape of input → output, not to surface a real source. Real users will paste real content with real attributions.

This is the **primary use case**. You're reading something interesting, you want to capture the *rules* (not just save the link), so you paste it into Claude Code and run `/playbook-distill`.

---

## What the user pastes

User opens their coding agent (Claude Code, Codex CLI, or any other) in their vault and pastes the following excerpt from an essay on B2B pricing:

> The dirty secret of B2B pricing is that most founders pick a number, run with it, and tell themselves a story about why it's the right number. They are almost always wrong, and almost always too low.
>
> The number is wrong because it was set against the wrong reference point. Founders price against what they think customers will pay. Customers don't pay based on what they think they will pay — they pay based on the alternatives in front of them and what those alternatives cost. If your reference point isn't a real alternative the customer is actually evaluating, your price is fiction.
>
> Three rules:
>
> **Rule 1 — Always anchor against a real alternative, not a hypothetical one.** "We charge $500/month because the customer pays a junior analyst $50K/year to do this manually" works. "We charge $500/month because that's what feels reasonable for SaaS" doesn't.
>
> **Rule 2 — Charge from day one.** A free product collects users with a different set of incentives than a paid product. Free users will tell you what makes them happy. Paid users will tell you what they actually need. You only need the second signal.
>
> **Rule 3 — Raise prices when you have proof, not when you have nerve.** Proof = a customer who already paid full price and renewed. Nerve = "I think we could probably get more." Founders who raise on nerve usually get the discount they pre-negotiated in their head.
>
> Anti-pattern: pricing in tiers when you have no idea who buys which tier. Tiers exist to map customer segments to price points. If you can't name the segment in each tier, you have one product priced three different ways and a confused buyer.

Then the user invokes the prompt:
- **Claude Code**: types `/playbook-distill`
- **Codex CLI / web / other agents**: invokes `prompts/playbook-distill.md` (paste it inline, or via the tool's prompt-file flag)

---

## What the skill does (visible to user)

```
Reading Vault/Playbooks-Index.md...
Reading pasted content...
Domain: Startup (pricing content, B2B framing, founder context)
Reading Vault/Company Building/Startup Playbook/README.md...
Found existing topic file: pricing-and-business-model.md
Reading existing file to check for duplicate concepts...
Distilling 4 insights → operational format...
Merging into pricing-and-business-model.md...
Updating README "Sources captured"...
Updating Playbooks-Index.md "Active Playbook Status"...
Appending to Vault/log.md...

Playbook updated.
- Domain: Startup
- Playbook: Startup Playbook (existing)
- Merged into: pricing-and-business-model.md
- New topic files: none
- Source: needs user input — what's the attribution?
- Insights merged: 4 (1 anchor rule, 1 charge-from-day-one rule, 1 raise-prices trigger, 1 anti-pattern detector)
```

The skill asks at the end: *"What's the attribution for this paste? (e.g., 'Patrick McKenzie pricing essay 2024', or 'unknown — leave as placeholder')"*

User responds: `Example Pricing Essay 2026-05-04`

The skill goes back and replaces the placeholder source tag in the merged content with `[Example Pricing Essay, 2026-05-04]` and updates the README's "Sources captured" line.

---

## What got written to `pricing-and-business-model.md`

(New sections appended into the existing topic file. Existing content preserved.)

```markdown
## Anchor pricing — reference-point rule

**Rule:** always anchor your price against a *real* alternative the customer is currently evaluating, not a hypothetical "feels reasonable for SaaS" number.

| Anchor type | Example | Verdict |
|---|---|---|
| Real alternative the customer evaluates | "Junior analyst at $50K/year to do this manually" → $500/month | ✅ load-bearing |
| Hypothetical category norm | "Most SaaS in this space is $X" | ❌ fiction |
| Cost-plus | "Our infra costs $Y, so we charge 3x" | ❌ irrelevant to buyer |

If you cannot name the real alternative your customer is comparing you against, you don't have a price — you have a guess. [Example Pricing Essay, 2026-05-04]

## Charge from day one

**Decision trigger:** if your goal is product feedback, free is a worse signal than paid. Free users tell you what makes them happy; paid users tell you what they actually need. The second signal is the load-bearing one. [Example Pricing Essay, 2026-05-04]

Corollary: "free during beta then we'll charge later" is a delayed-decision pattern. The pricing conversation has the same hard parts whether you have it on day one or month nine — but on day nine you also have to break a promise. [Example Pricing Essay, 2026-05-04]

## Price-raise trigger

**IF** you've had at least one customer pay full price AND renew at full price → you have proof and can raise.
**IF** you're raising because "I think we could probably get more" → you have nerve, not proof. Expect to be talked down. [Example Pricing Essay, 2026-05-04]

## Anti-pattern detector — premature tiering

Boolean check. If TRUE → simplify to one price.

- [ ] You have 3 pricing tiers but cannot name the customer segment that buys each tier

If you can't name the segment per tier, you have one product priced three different ways and a confused buyer. Tiers exist to map *segments* to *price points*. No segment → no tier. [Example Pricing Essay, 2026-05-04]
```

---

## What got written to `Vault/log.md`

```
2026-05-04 14:22 | playbook-distill | merged | Example pricing essay | Startup → pricing-and-business-model.md; 4 insights merged
```

---

## What this example illustrates

1. **You read once, capture once, never re-derive.** The next time you need to price something, the rules are already crystallized in `pricing-and-business-model.md`, source-tagged so you know where they came from.
2. **The skill merges, not appends.** The existing topic file gained 4 new sections in the right places. It didn't get a new file called "Example pricing essay 2026-05-04 notes.md" cluttering the vault.
3. **No quote dump.** The output is *rules*, not "this article said X." The narrative is gone. The decision triggers and detectors stay.
4. **Source attribution is preserved.** Six months from now when you wonder "where did this rule come from?" the inline tag tells you.
5. **The skill asks for missing metadata.** It didn't pretend to know the attribution; it asked.

This is the loop most users will run multiple times per day during research-heavy work. No Readwise required.
