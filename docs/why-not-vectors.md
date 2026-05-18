# Why not vectors

This document compares memory-os against the four most-funded names in the AI-memory category as of mid-2026: **Mem0**, **Letta**, **Zep**, and **Cognee**. The goal is not to declare one architecture morally superior. It is to draw the line precisely so a reader can tell, in 30 seconds, which side of the line their use case sits on.

## The category, summarized

Mem0, Letta, Zep, Cognee, and adjacent products (MemGPT, the memory layer inside every agent framework with a deck) share a shape:

1. Ingest user messages or documents.
2. Embed them into vectors with a model.
3. Store the vectors in a database (Pinecone / Weaviate / Qdrant / pgvector / proprietary).
4. At retrieval time, embed the query, find nearest neighbors, return their associated text.
5. Layer on top: summarization, clustering, deduplication, "memory hierarchies," importance scoring.

The marketing varies. The architecture does not.

## Where vectors win, decisively

Vectors are correct for:

- **Multi-tenant retrieval.** A help-desk agent fielding queries from thousands of users, each with their own history, where no human can hand-curate. Vector retrieval is the only architecture that scales without exponential human labor.
- **Corpora the user did not write.** If you ingested 100,000 academic papers, vector retrieval is the only way to find the relevant five for a given query. You cannot hand-tag at that scale.
- **Vocabulary drift across users.** When "claim" means one thing to user A and another to user B, an embedding model bridges the gap because it learns from co-occurrence. A controlled vocabulary cannot, without consensus rituals that don't scale.
- **Pure recall benchmarks.** If the eval is "given query X, return relevant memory Y from a buried corpus," vectors win. That eval is also not what most knowledge workers actually need.

In those cases, use Mem0 or Letta or Zep or pgvector + your own glue. memory-os is the wrong tool.

## Where vectors lose, in the single-knowledge-worker case

For one person working out of their own vault, the same vector-DB architecture imposes costs that are invisible in the benchmark but compound in production:

### 1. Opacity at retrieval

A vector retrieval returns the top-k nearest neighbors with cosine similarity scores. The agent gets text plus a confidence number. *Why* those passages came back — what features of the embedding triggered the match — is unknowable, even to the engineers who built the embedding model. When the agent retrieves something irrelevant, you cannot tell whether the embedding model misclassified it, the query was malformed, or your corpus is too sparse. You can only re-embed and pray.

A `grep` against `_learnings.md` returns file paths and line numbers. When the agent retrieves something irrelevant, the path tells you exactly which note you wrote wrong. The fix is editing one file. The diagnostic is a one-line `grep`.

### 2. Migration tax

Embedding models deprecate roughly every six months. OpenAI's `text-embedding-ada-002` is now legacy. Cohere's v3 superseded v2. Anthropic does not publish a dedicated embedding model but releases new Claude versions that change retrieval behavior under the hood for everyone using API-based embeddings indirectly. Each migration means re-embedding the entire corpus, validating the new index against the old, and accepting that retrieval will be subtly different forever.

Markdown does not deprecate. A `_learnings.md` file written in 2026 will be readable in 2046 with no migration. The substrate is older than your agent.

### 3. Inability to express policy

Suppose you decide that "principles" should always fire on every relevant task, "state" should never appear in a strangers's first three turns with you, and "feedback" should override anything in the model's defaults. That is not a retrieval problem. It is a *policy* problem.

A vector store has no place to put policy. You can prompt-engineer it into the system prompt, but the prompt is global and the policy is per-entry. memory-os encodes policy as filesystem structure: hot pinboard = always-loaded; cold index = lookup-on-demand; subfolder kind: = retrieval-time filter. The agent's behavior changes when you move a file, not when you re-embed a chunk.

### 4. Cost asymmetry per session

Cached `MEMORY.md` reads are fractions of a cent per turn after the first one. Vector store calls charge per-query, and the per-query cost dominates when you have many short turns (which is what a working agent session looks like). For one knowledge worker doing 50 turns a day, the cached file is roughly an order of magnitude cheaper at scale than a hosted vector store, and the math is worse if you're running your own Pinecone cluster.

### 5. Editability and version control

The vault is a git repo. Every change is a diff. Every state of memory is reproducible by checking out a commit. You can blame, revert, merge, branch. You can grep history.

Vector stores have versioning bolted on as an afterthought, if at all. Most users of Mem0 or Zep or pgvector do not version their memory; they ship the latest state and accept the loss. For the single-knowledge-worker case where one person is the source of truth, this asymmetry is enormous.

## Head-to-head, by name

### Mem0

Mem0 markets itself as the memory layer for LLM apps. Architecture: vector store + LLM-driven memory CRUD (decide what to add, update, delete via a model call per write). Strengths: easy to bolt onto an existing chatbot. Weaknesses: opaque retrieval, every write costs an LLM call, no native concept of policy or tiering.

**vs. memory-os:** Mem0 wins for multi-user chatbots. memory-os wins when the user *is* the author of the corpus and wants control over what is remembered, in what order, with what decay rule.

### Letta (formerly MemGPT)

Letta ships a tiered memory model — *core memory* (a user-editable text block read on every turn), *recall memory* (a vector-store middle tier), and *archival memory* (long-tail storage). This is the most architecturally similar product to memory-os in the category. The shape is right: an always-loaded text surface the user controls, plus retrieval backstops behind it.

The differences are real but narrower than the rest of this category. Letta's middle tier is vector-backed, so its retrieval surface inside that tier shares the opacity and migration costs described above. Letta's controlled-vocabulary work happens via an LLM-driven memory CRUD that adapts the taxonomy from usage rather than freezing it in YAML the user maintains.

**vs. memory-os:** Letta and memory-os agree on tiered memory more than this doc previously implied. The honest comparison: memory-os bets the controlled vocab is durable enough that hand-curation beats automated extraction *for one author over 18-24 months*; Letta bets the automated extraction beats hand-curation across longer horizons and broader use cases. Either could be right; the data is not in yet.

memory-os wins on transparency at retrieval (every read is a file path you can audit) and on substrate longevity (no embedding-model migration). Letta wins on scale beyond one author and on automatic taxonomy adaptation. For multi-tenant or year-3+ use cases where vocabulary drift dominates, Letta is the better bet. For the 2-year single-author envelope this repo defines, memory-os is.

### Zep

Zep targets the agent-platform layer with a knowledge graph + vector store hybrid. Strengths: graph structure preserves relationships between entities (good for support agents tracking customer history). Weaknesses: graph schemas drift, knowledge-graph extraction from text is brittle, and graph maintenance is its own engineering effort.

**vs. memory-os:** Zep is correct when relationships between entities are first-class (user X owns account Y purchased product Z). memory-os is correct when relationships are expressed *as Markdown wiki-links a human wrote on purpose*. The wiki-link is the graph edge; the human is the graph maintainer; the cost of maintaining the graph is zero because the human is already writing the notes.

### Cognee

Cognee adds an LLM-driven knowledge-graph extractor on top of vectors. Architecture: ingest documents → vector store + auto-extracted graph → query against both. Strengths: graph emerges from the corpus automatically. Weaknesses: the graph is only as good as the extraction model, and the extraction model is not your taxonomy.

**vs. memory-os:** Cognee bets that LLMs can extract your ontology from your documents. memory-os bets that *you* should define the ontology and the LLM should retrieve against it. The bets diverge most dramatically on idiosyncratic personal taxonomies — Cognee will extract "AI Build Partners" as a tech company; memory-os knows it is Derek's venture with his brother because the folder is named that on purpose.

## When you should use vectors, even with memory-os installed

memory-os is not anti-vector. It is anti-vector-as-the-primary-retrieval-layer-for-personal-knowledge. There are sub-problems inside memory-os's envelope where a vector index helps:

- **Semantic search across very large `_learnings.md` files.** If a single learnings file grows past 5,000 lines, `grep` returns too much. A vector index over that one file gives a useful narrowing.
- **Finding "similar past sessions."** Session archives are conversational; semantic similarity matters more than keyword overlap. A vector index here is useful.
- **Cross-referencing into corpora you didn't write.** Readwise highlights, podcast transcripts, downloaded PDFs. memory-os routes those into the playbook distillation pipeline ([`skills/distill/note-highlight-indexer/`](../skills/distill/note-highlight-indexer/)), but for direct queries against the raw source, vectors are right.

The principle is: vectors at the *edges* (large unstructured corpora, similarity-based discovery), Markdown at the *center* (the curated, policy-bearing, decision-time-loaded core).

## The honest comparison table

| Concern | Vector DB memory | memory-os |
|---|---|---|
| Multi-tenant retrieval | Wins | Wrong tool |
| Corpora you didn't write (100k+ docs) | Wins | Wrong tool |
| Single-user, lived-in vault | Costs more than it saves | Wins |
| Transparency at retrieval | Opaque (similarity scores) | Path + line range |
| Cost per turn at steady state | Per-query, scales with use | ~0 after first cache hit |
| Migration when models deprecate | Re-embed everything | Nothing — Markdown doesn't deprecate |
| Policy encoding (what fires when) | System prompt, global | Filesystem structure, per-entry |
| Editability of memory | Opaque CRUD via API | Edit a file with `vim` |
| Version control | Bolted-on at best | `git log` is the audit trail |
| Cold-start usefulness | Day one | Builds over months |
| Cross-author drift | Embedding handles it | Requires manual consensus |
| Setup cost | Low | High (one-time) |

## What this comparison is not saying

It is not saying vector databases are wrong. They are right for the cases they are designed for, and those cases are large and well-funded.

It is saying that the entire AI-memory product category in mid-2026 has converged on one architecture, that that architecture is wrong for one of the largest and most under-served use cases (the single knowledge worker with a personal vault and a capable agent), and that the correction is not subtle — it is filesystem + `grep` + a controlled vocabulary + a few hundred lines of cron-driven Python — and that the labs will not ship that correction, so the correction is a write-it-yourself problem.

memory-os is one worked example. Steal what fits.
