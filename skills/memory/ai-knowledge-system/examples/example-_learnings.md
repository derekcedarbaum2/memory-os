---
title: "Toolkit Knowledge Base"
type: reference
status: active
classification: unclassified
created: 2026-04-06
updated: 2026-04-28
last_reviewed: 2026-04-21
author: "Example User"
tags: [toolkit, agent, automation]
---

# Toolkit — Knowledge Base

> Sanitized example from a working installation. Shows the four-section structure populated with realistic content.

Captures agent workflows, API patterns, automation gotchas, and skill/prompt architecture decisions across all projects.

## Learnings

### Agent Skills & Architecture

- Claude Code skills with `disable-model-invocation: true` only run on explicit user trigger — useful for high-cost or destructive flows. *(source: [[2026-04-08-skill-routing-debug]])*
- Subagents inherit the global rules and memory context — every byte in CLAUDE.md/AGENTS.md and MEMORY.md multiplies cost across delegated work. *(source: [[2026-04-12-subagent-cost-audit]])*

### Jira / Confluence API

- Jira Cloud `Won't Do` transition is two steps: transition to Done first, then update the resolution field separately. Inline resolution on the transition call fails with "Field cannot be set." *(source: [[2026-04-28-jira-resolution-quirk]])*
- Confluence storage XML parsed via lxml needs the namespace declarations wrapped manually — `ac:` and `ri:` prefixes have no declaration in the fragment itself. *(source: [[2026-04-15-confluence-xml-parse]])*

### Cost Optimization

- For batch operations over 100 issues on Claude Code: delegate Steps N–M of any skill to a cheaper-model subagent — typical 50–60% savings vs. running everything on the top-tier model. *(source: [[2026-04-12-subagent-cost-audit]])*

## Key Decisions

| Date | Decision | Session |
|------|----------|---------|
| 2026-04-06 | Replace monolithic learnings.md + concept-graph with domain-routed `_learnings.md` files. Old system had 0% read rate during real work. | [[2026-04-06-knowledge-system-redesign]] |
| 2026-04-12 | Default to a cheaper model for archive-session subagent step; reserve top-tier model for synthesis only. | [[2026-04-12-subagent-cost-audit]] |
| 2026-04-28 | Flatten Jira board hierarchy — drop umbrella Epics, parent Stories directly to work-bearing Epics. | [[2026-04-28-board-flatten]] |

## Open Threads

- Whether to add `job-jX` labels to Epics for cleaner JQL filtering, or keep description-based filtering as the V1 convention. *(from [[2026-04-28-board-flatten]])*
- Best pattern for clearing JPD `Roadmap` field on archived items — single-field call vs. UI; current API call errors with empty array. *(from [[2026-04-27-jpd-archive-cleanup]])*

## Related Sessions

| Date | Type | Summary | Link |
|------|------|---------|------|
| 2026-04-06 | planning | Designed three-tier knowledge system; replaced monolithic learnings file. | [[2026-04-06-knowledge-system-redesign]] |
| 2026-04-08 | debug | Traced why a skill wasn't firing on slash command — `disable-model-invocation` flag. | [[2026-04-08-skill-routing-debug]] |
| 2026-04-12 | research | Audited subagent token costs across archive-session runs. | [[2026-04-12-subagent-cost-audit]] |
| 2026-04-15 | debug | Confluence XML parse failures — namespace declarations missing in fragments. | [[2026-04-15-confluence-xml-parse]] |
| 2026-04-27 | build | Closed out 6 stale JPD discovery items; documented field-clear gotchas. | [[2026-04-27-jpd-archive-cleanup]] |
| 2026-04-28 | build | Flattened PROJ1 board hierarchy; stripped bracket prefixes from Epic summaries. | [[2026-04-28-board-flatten]] |
