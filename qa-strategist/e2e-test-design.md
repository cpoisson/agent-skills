# E2E Test Design

Identify critical user flows, design readable test cases, and build a coverage matrix. This sub-skill helps you answer: *what* to test end-to-end, in what order, and how to express it clearly — before touching any test framework.

## Step 1 — User Flow Inventory

### From routes and pages

List all user-facing routes/pages and the primary action on each:

```markdown
| Route / Screen | Primary Action | Auth Required |
|----------------|---------------|---------------|
| /login | Submit credentials | No |
| /register | Create account | No |
| /app | View and interact with daily content | Yes |
| /settings | Configure account and preferences | Yes |
| /history | Review past activity | Yes |
```

### From API endpoints (server-side flows)

Group API endpoints by functional area to identify the data flows a user depends on:

```markdown
| Functional Area | Example Endpoints | User-Visible Impact |
|-----------------|------------------|---------------------|
| Authentication | POST /auth/login, /register | Access to the app |
| Core daily loop | GET /state, PATCH /tasks/:id, POST /days/validate | Primary value loop |
| Settings | PATCH /settings/*, DELETE /account | Account management |
| Rewards / graines | PATCH /graines/purchase | Reward system |
```

### From user stories

Write flows as user stories to anchor test design in user intent:

```
As a [type of user], I want to [goal], so that [benefit].
```

Example:
```
As a parent, I want to validate my child's day, so that their progress is saved and visible in history.
```

## Step 2 — Critical Path Selection

Not all flows are equally important. Use this heuristic to rank them:

**Score = Frequency × Impact × Fragility**

| Dimension | 1 (Low) | 2 (Medium) | 3 (High) |
|-----------|---------|-----------|---------|
| **Frequency** | Rarely used (admin, one-time setup) | Weekly | Daily |
| **Impact** | Minor inconvenience if broken | Degrades UX significantly | Core experience broken |
| **Fragility** | Stable, rarely changes | Changes occasionally | Changes often or depends on complex logic |

**Prioritize flows with score ≥ 6** for immediate E2E coverage. Flows with score 4–5 are next. Below 4 — defer or cover at integration level.

### Example scoring table

| Flow | Frequency | Impact | Fragility | Score | Priority |
|------|-----------|--------|-----------|-------|----------|
| Login | 3 | 3 | 2 | 18 | P0 |
| Primary daily loop | 3 | 3 | 2 | 18 | P0 |
| Register | 2 | 3 | 1 | 6 | P1 |
| Validate a day | 3 | 3 | 2 | 18 | P0 |
| Setting: change PIN | 1 | 2 | 1 | 2 | P3 |
| Delete account | 1 | 3 | 1 | 3 | P2 |

## Step 3 — Coverage Matrix

Track which flows are covered, at what level, and in which environments:

```markdown
| Flow | Unit | Integration | E2E Smoke | E2E Regression | Manual | Status |
|------|------|-------------|-----------|----------------|--------|--------|
| Register | ❌ | ❌ | ❌ | ❌ | ⬜ | No coverage |
| Login | ✅ | ✅ | ✅ | ❌ | ⬜ | Partial |
| Logout | ❌ | ✅ | ❌ | ❌ | ⬜ | Partial |
| Daily loop | ✅ | ❌ | ❌ | ❌ | ⬜ | Partial |
| Validate day | ✅ | ❌ | ❌ | ❌ | ⬜ | Partial |
| History edit | ❌ | ❌ | ❌ | ❌ | ⬜ | No coverage |
```

Status definitions:
- **No coverage** — zero automated tests
- **Partial** — some layers covered
- **Smoke covered** — covered in the CI smoke suite
- **Fully covered** — smoke + regression exist

## Step 4 — Test Case Design

### Structure: Given / When / Then

Use this structure to write readable test cases that serve as both documentation and executable specs:

```
Given [initial state / preconditions]
When  [user action or event]
Then  [expected outcome / assertions]
```

Example:

```
Scenario: Validate a successful day

Given the user is logged in as a parent
And today's tasks are partially completed
When the user clicks "Validate Day"
Then the day is saved to history with today's date
And the child's points are updated
And the daily loop resets for tomorrow
```

### Test case template

```markdown
---
flow: <flow name>
priority: P0 | P1 | P2 | P3
area: auth | daily-loop | rewards | settings | history | admin
tags: @smoke | @regression | @critical | @slow
---

## <Test Scenario Title>

**Given** <initial state>
**When** <action>
**Then** <assertion 1>
  And <assertion 2>

**Notes:** <edge cases, known quirks, setup requirements>
```

## Step 5 — Functional Area Map

Organize flows by functional area to plan systematic coverage:

| Area | Flows | Recommended Test Type | Risk Level |
|------|-------|----------------------|-----------|
| **Authentication** | Register, login, logout, password reset | E2E smoke | High |
| **Onboarding** | First-time setup flow | E2E regression | High |
| **Core daily loop** | View tasks, toggle, validate day | E2E smoke | Critical |
| **History** | View history, edit notes | E2E regression | Medium |
| **Rewards** | View catalog, spend currency | Integration + E2E | High |
| **Settings** | Change PIN, password, account deletion | Integration + E2E | Medium |
| **Admin / family** | Add/edit/remove child, manage tasks | Integration | Medium |
| **Notifications** | Permission request, schedule | E2E + manual | Low |

## Step 6 — Smoke vs. Regression vs. Full Suite

| Suite | Flows Included | When to Run | Max Duration |
|-------|---------------|------------|-------------|
| **Smoke** | P0 flows only (login, primary loop, critical data write) | Every PR, every deploy | < 3 min |
| **Regression** | P0 + P1 flows | Every PR to main, nightly | < 15 min |
| **Full** | All automated flows + edge cases | Weekly / pre-release | No limit |

Tag tests to enable selective runs:
```
@smoke   — must always pass
@critical — P0 flows
@regression — broader regression set
@slow  — >5 seconds, exclude from fast feedback
```

## Design Risks to Flag

When reviewing proposed E2E test plans, flag these patterns:

| Anti-pattern | Problem | Better approach |
|---|---|---|
| Testing every field in a form | Slow, fragile, covers unit-level concerns | Test the critical submission path; cover field validation in unit tests |
| Asserting on exact copy/text | Breaks on any wording change | Assert on behavior, aria labels, or test-ids instead |
| No test isolation | Tests depend on each other's state | Each test should set up its own preconditions or use seed data |
| Testing third-party services live | Flaky, slow, creates side-effects | Mock at the boundary; test third-party integration separately |
| Full suite on every PR | Slow feedback loop | Smoke on PR; full suite nightly or on main merges |
| Missing unhappy paths | Only the happy path is tested | Add one unhappy path per critical flow (e.g., login with wrong password) |
