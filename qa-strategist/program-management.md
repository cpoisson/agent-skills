# Program Management

Use this sub-skill to keep delivery aligned with quality and product goals. It standardizes how to maintain a `ROADMAP.md`, report progress, and answer planning questions such as:

- What should we work on next?
- What is the urgent bug to fix now?
- Can we start feature `X`?

## Core Responsibilities

1. Ensure roadmap hygiene (always current, actionable, and prioritized)
2. Convert status signals (incidents, CI, delivery progress) into ranked work
3. Gate new feature starts based on risk, readiness, and active incidents

## Step 1 - Ensure `ROADMAP.md` Exists

At the start of any program-management request:

1. Check for `ROADMAP.md` in the repository root
2. If missing, create it from the template in this skill
3. If present, update the date, status snapshot, and priority queues

Never answer prioritization questions from memory only; always reconcile against the roadmap first.

## Step 2 - Refresh Program State

Update the roadmap from current evidence:

- Open incidents and production bugs (especially P0/P1)
- CI and release health
- Recently completed milestones
- In-progress initiatives and blockers
- Planned features and dependency readiness

If data is missing, call it out explicitly in a short "Assumptions" section.

## Step 3 - Priority Scoring Model

Use a lightweight score for candidate work items:

$$
\text{Priority Score} = \frac{(3 \times \text{User Impact}) + (2 \times \text{Risk Reduction}) + (2 \times \text{Time Criticality}) + (1 \times \text{Strategic Alignment})}{\text{Effort}}
$$

Scales:

- User Impact: 1-5
- Risk Reduction: 1-5
- Time Criticality: 1-5
- Strategic Alignment: 1-5
- Effort: 1-5 (5 = largest)

Sorting rule:

1. Always handle active P0 first
2. Then highest score
3. Tie-break on smaller effort and blocked dependencies

## Step 4 - Answer Key Questions

### A) "What should we work on next?"

Respond with:

1. Top 3 ranked items from the roadmap
2. Why item #1 is next (score + dependency rationale)
3. What must be true to start item #2 and #3

### B) "What's the urgent bug to be fixed?"

Use severity gates:

- **P0**: Production outage, data loss/corruption, security breach in progress
- **P1**: Core flow broken for many users, no acceptable workaround
- **P2**: Major but non-critical degradation with workaround
- **P3**: Minor issue/cosmetic/edge-case

Answer format:

1. Most urgent bug (ID + severity + user impact)
2. Why it outranks others
3. Immediate containment step
4. Owner recommendation and next checkpoint time

If there is no P0/P1, say so explicitly and recommend the top quality debt item.

### C) "Can I start my feature `xxx`?"

Apply a start gate checklist:

- [ ] No unresolved P0/P1 incident requiring current team capacity
- [ ] Spec and acceptance criteria are clear
- [ ] Dependencies are available (API, design, infra, data)
- [ ] Test plan exists (unit/integration/E2E as needed)
- [ ] Rollout and rollback strategy is defined
- [ ] Owner and reviewer are identified

Decision rules:

- Any unchecked critical gate -> **Not yet**
- All gates checked with manageable risk -> **Yes, start now**
- Partial readiness with low risk -> **Start discovery/spike only**

## `ROADMAP.md` Template

Use this when creating a new roadmap file.

```markdown
# ROADMAP

Last updated: YYYY-MM-DD
Program owner: <name>

## Status Snapshot

- Delivery health: Green / Yellow / Red
- CI health: Green / Yellow / Red
- Open incidents: <count> (P0: <n>, P1: <n>)
- Current release focus: <text>

## Completed Recently

- [x] <item> (YYYY-MM-DD)

## In Progress

- [ ] <item> - owner: <name> - ETA: <date>

## Next Up (Prioritized)

| Rank | Item | Type | Score | Effort | Depends On | Notes |
|------|------|------|-------|--------|------------|-------|
| 1 |  | bug/feature/infra/qa |  |  |  |  |
| 2 |  | bug/feature/infra/qa |  |  |  |  |
| 3 |  | bug/feature/infra/qa |  |  |  |  |

## Urgent Bug Queue

| ID | Severity | Summary | User Impact | Owner | Status | Updated |
|----|----------|---------|-------------|-------|--------|---------|

## Feature Start Decisions

| Feature | Decision | Reason | Required Before Start | Last Reviewed |
|---------|----------|--------|------------------------|---------------|
```

## Output Templates

### Program update

```markdown
Roadmap updated (YYYY-MM-DD):
- Completed: ...
- In progress: ...
- Next: ...
- Urgent bug: ...
- Risks/blockers: ...
```

### Feature start decision

```markdown
Feature: <name>
Decision: Yes, start now / Start discovery only / Not yet
Why: <2-3 bullets>
Required before full start:
1. ...
2. ...
```
