# ROADMAP

Last updated: 2026-03-31
Program owner: cpoisson

## Status Snapshot

- Delivery health: Yellow
- CI health: Yellow
- Open incidents: 0 (P0: 0, P1: 0)
- Current release focus: strengthen evaluation quality beyond route-only happy paths

## Completed Recently

- [x] Added deterministic and semantic evaluation gates for `qa-strategist`
- [x] Added adapter files for Codex, Claude, and GitHub Copilot

## In Progress

- [ ] Expand eval coverage to include negative controls, guided prompts, and richer trigger reporting - owner: cpoisson - ETA: 2026-03-31
- [ ] Refresh `qa-strategist/agentic-coding-qa.md` with evidence-before-exit and reliability guidance - owner: cpoisson - ETA: 2026-03-31

## Next Up (Prioritized)

| Rank | Item | Type | Score | Effort | Depends On | Notes |
|------|------|------|-------|--------|------------|-------|
| 1 | Deepen `qa-strategist` evals with trigger controls, ambiguity coverage, failure modes, and efficiency reporting | qa | 4.4 | 2 | None | Highest leverage because it improves every future skill revision |
| 2 | Improve `qa-strategist/agentic-coding-qa.md` with reliability, verification quality, and bounded-failure guidance | skill | 4.0 | 2 | Item 1 telemetry | Keeps the shared skill aligned with the repo's own eval bar |
| 3 | Create a new `agent-evals` skill for rubric design, judge design, negative controls, and transparent eval reporting | feature | 3.8 | 3 | Item 1 patterns | Best new skill candidate based on the research repo |
| 4 | Create a new `agent-failure-analysis` skill for trace review, failure taxonomy, and misroute diagnosis | feature | 3.4 | 3 | Item 1 artifacts | Useful once there is enough eval output to analyze |
| 5 | Create a new `spec-driven-agent-workflows` skill for task contracts, environment setup, and eval-ready acceptance criteria | feature | 3.0 | 4 | Item 3 | Valuable, but lower leverage than eval instrumentation right now |

## Urgent Bug Queue

| ID | Severity | Summary | User Impact | Owner | Status | Updated |
|----|----------|---------|-------------|-------|--------|---------|

## Feature Start Decisions

| Feature | Decision | Reason | Required Before Start | Last Reviewed |
|---------|----------|--------|------------------------|---------------|
| `agent-evals` skill | Start discovery only | Strong demand signal from research, but the current repo first needs stable eval artifacts and repeatable patterns | Lock the revised eval schema, failure labels, and reporting format | 2026-03-31 |
| `agent-failure-analysis` skill | Start discovery only | Valuable after trace volume grows; premature as a full skill today | Gather recurring failure classes from semantic judge outputs | 2026-03-31 |
| `spec-driven-agent-workflows` skill | Not yet | Good long-term fit, but lower confidence payoff than eval/reporting improvements | Validate that users want spec-driven agent setup as a distinct workflow | 2026-03-31 |
