# The envelope

`memory-os` works inside a narrow range of conditions. Outside that range, other architectures (usually vector stores) are correct. This document is the formal description of the range — what I call the *envelope*.

The point of writing it down is to make the pitch falsifiable. A reader can compare their conditions against the envelope and decide whether to keep reading or close the tab. That honesty is also how memory-os credibly claims dominance inside the envelope: by refusing to claim dominance outside it.

## The four envelope conditions

memory-os assumes all four are true:

### 1. Single author for the curated corpus

One human writes the canonical files. One taxonomy. One controlled vocabulary. One set of decisions about what goes where. Multiple humans reading from the vault is fine; multiple humans *writing* breaks the model.

Why: the controlled-vocabulary tag system (`kind:`, `decay:`, `venture:`) survives only as long as one person enforces it. Two authors will drift in semantics — "principle" to author A means a durable heuristic; to author B it means a current strategic bet — within weeks. The cost of consensus rituals to keep them aligned exceeds the cost of just using a vector store.

If you have multiple writers: use a vector store, or pick one of the writers to be the canonical taxonomist and treat the others as input sources rather than co-authors.

### 2. Lived-in Markdown vault

A real working corpus that has accumulated through use, not a corpus you intend to build. Hundreds of files, organic folder structure, frontmatter that means something to the author. Personal investment in the file system as a working surface.

Why: memory-os pays its retrieval costs upfront in structuring decisions. If the corpus is small (under 50 files) the structuring decisions are unnecessary — the agent could read everything in one turn. If the corpus is theoretical (you plan to start writing) the system has nothing to grep against and cold-start dominates everything.

If you don't have a vault yet: build one for two weeks before installing memory-os. Otherwise the structure has nowhere to land.

### 3. Capable model with filesystem access

Sonnet- or Opus-class model, or comparable frontier reasoner, with shell access to read and write files. Specifically: the agent must be able to iterate on retrieval — write a `grep` query, read results, refine the query, read more, decide what to load into context.

Why: the Letta benchmark on filesystem-vs-specialized-memory showed that filesystem retrieval wins *because capable agents iterate*. A weak model that runs one `grep` and gives up will look worse than a vector store. A capable model that runs three `grep` queries refining each time will beat the vector store on the same corpus.

This is also the reason memory-os has not retreated to "use embeddings as a fallback." The fallback is the model's own ability to refine. If the model can't refine, you have a different problem.

### 4. Personal-scope use case

The agent is helping one knowledge worker think, decide, write, and remember across their work and life. Not customer-service routing. Not legal discovery. Not retrieval-augmented generation for a publication. Personal scope — meaning the corpus, the questions, and the consequences all sit inside one person's domain.

Why: the operating manual is the load-bearing artifact, and operating manuals are personal. The decisions about what counts as a principle vs. state, what decay rate applies, which ventures live on the pinboard — all of these are taste decisions. They cannot be defaulted because there is no neutral default for "what matters to Derek right now." memory-os exposes the taste decisions as files you can read; it does not hide them inside an embedding.

If your use case is non-personal — a multi-user knowledge base, an enterprise wiki, a customer-facing assistant — memory-os is wrong. Use a vector store and a real product.

## The four conditions, restated as a single test

You are inside the envelope if you can answer YES to all four:

1. **Author:** Am I the sole author of the canonical files in my corpus?
2. **Corpus:** Do I already have at least 100 Markdown files I've written or curated, organized into folders that mean something to me?
3. **Model:** Is my agent a capable frontier model with filesystem read/write access?
4. **Scope:** Am I trying to make an agent better at helping *me*, specifically — not better at serving a population I don't know?

If any of these is NO, memory-os is the wrong tool. Use a vector store (Mem0, Letta, Zep, Cognee) or a real product.

## Edge cases

### "I'm one person but I have 100,000 files I downloaded from arXiv"

Outside the envelope on condition 1 (technically you didn't *author* them) and condition 2 (the structure isn't yours). Vector index over the arxiv corpus + memory-os for *your own notes about what you read* is the right hybrid. See [`skills/distill/note-highlight-indexer/`](../skills/distill/note-highlight-indexer/) — that skill is the bridge.

### "I'm one person but I want to share my agent with my spouse"

Edge case on condition 1. If your spouse is a *reader* of your vault, you're fine. If your spouse is going to *write* into the vault, they need their own taxonomic discipline or you need to accept drift. The simplest workaround: one shared "Family" vault with simpler structure (no controlled vocab) + each spouse's own work vault.

### "I have a vault but it's chaos"

Probably still inside the envelope. The first month of memory-os is mostly hygiene — backfilling tags, sorting files into the right folders, killing duplicates, deciding what gets a `_learnings.md`. The tag-backfill script ([`automation/tag-backfill.py`](../automation/tag-backfill.py)) does the mechanical part. The taxonomic part is judgment you do once, then never again, because the cron keeps it clean.

### "I'm using a small open-source model (7B, 13B) instead of a frontier model"

Outside the envelope on condition 3. Small models do not iterate on retrieval. They run one query, take the first result, and stop. memory-os needs a model that can read 10K-token search results and decide what's relevant — that's a Sonnet/Opus-class capability.

If you're locked to small models for cost or privacy reasons, use a vector store. The smaller the model, the more the retrieval layer has to compensate.

### "I'm using this at work and security blocks shell access for AI"

Outside the envelope on condition 3. The agent must be able to read and write files. If your security posture forbids that, memory-os doesn't run. Either lobby for the access (this is the right answer long-term) or accept a hosted vector store with auditable retrieval.

### "I want to use this for my whole company's knowledge base"

Outside the envelope on conditions 1 and 4. Don't. Use a real product (Glean, Notion AI, Atlassian Rovo). Those exist because the multi-user enterprise case is genuinely different and genuinely large.

## Cold-start cost

Inside the envelope, you still pay one upfront cost: roughly two weeks of friction setting up the vault, the conventions, and the first dozen `_learnings.md` files. After that the system compounds. Year-two users have hundreds of accumulated learnings, principles that fire across many tasks, dormant ventures that auto-decay, fresh ones that auto-surface — none of which the year-one user had.

This is a *deferred-payoff* system, not an instant-on one. Vector stores pay their value linearly from day one. memory-os pays its value asymptotically — close to zero in week one, useful by month two, dominant by month six. If you need value this week, vectors are correct. If you're investing in your own working environment for the next five years, memory-os is correct.

## What gets stronger over time

To make the deferred-payoff argument concrete, here is what changes between week one and year two:

- **Week 1:** ~5 `_learnings.md` files. No principles yet. Hot pinboard mostly empty. Crons running but finding nothing to demote. System is barely better than `cat` + `grep`.
- **Month 1:** ~30 `_learnings.md` files. First few principles surface from cross-venture work. Hot pinboard has 3-4 active ventures. Crons start producing real dormancy reports.
- **Month 6:** ~80 `_learnings.md` files. Twenty principles. Hot pinboard saturates at 7-8 ventures. Cron output is signal-dense; weekly log review takes 90 seconds. Adversarial-quality loop runs on every important document.
- **Year 2:** ~150 `_learnings.md` files, many dormant. Principles routed automatically into a small set of inline rules. Cold index has dozens of useful pointers. The system tells *you* things you'd forgotten about your own work — promotion candidates from areas you stopped touching.

The asymptote isn't speed; it's the *quality of the agent's first turn in a new session*. Year-two Derek's agent starts every conversation already knowing his ventures, his preferences, his current open threads, the principles he's accumulated, and the dormancy state of every project. Week-one Derek's agent starts cold.

## When to abandon memory-os

This is the honest part. memory-os should be abandoned, or at least drastically simplified, if:

- The maintenance cron eats more time than it saves. (Symptom: skipping the weekly log review.)
- The taxonomy becomes its own product instead of a means to an end. (Symptom: spending more time on the vocab than on the work.)
- You change roles in a way that invalidates the venture taxonomy. (Symptom: half the pinboard is dormant within a month.)
- A frontier lab ships a successor that does the operating-manual layer well enough. (Symptom: you read their docs and think "they actually got it.")

The last one is the most likely failure mode. I expect Anthropic or OpenAI to ship something memory-os-shaped within three years. When that happens, this repo becomes a historical artifact and the lessons migrate into whatever they shipped. That is fine. The thesis is the contribution; the artifact is replaceable.

## Final test

If after reading this you can name your envelope conditions and place yourself inside or outside them, the doc has done its job. The pitch is not "you should use memory-os." The pitch is "here is a worked example of the operating-manual layer; if you're inside the envelope, the cost of stealing from it is low; if you're outside, the cost of trying is high."

Choose accordingly.
