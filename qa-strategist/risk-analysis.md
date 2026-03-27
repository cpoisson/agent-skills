# Risk Analysis

Identify, prioritize, and act on quality risks. This sub-skill guides an interactive risk assessment conversation — the agent shares its view, asks for yours, then recommends a prioritized QA action plan.

## How to Run a Risk Assessment

### Step 1 — Gather context (ask the user)

Start with these questions before forming any opinion:

1. What is the application's primary user-facing function? What would hurt users most if it broke?
2. Is real user data live in production? How sensitive is it?
3. When was the last time you had a regression or incident in production?
4. What is currently untested that you are most nervous about?
5. What is the next planned change and how large is it?

### Step 2 — Inventory risk categories

Score each category 1–3 (1 = low, 2 = medium, 3 = high) on two dimensions:
- **Likelihood** — how probable is a failure in this area given current state?
- **Impact** — how severe would the consequence be if it failed?

| Risk Category | Description | Default Likelihood | Default Impact |
|---------------|-------------|-------------------|----------------|
| **Data loss** | User data deleted, corrupted, or inaccessible | 1 | 3 |
| **Auth failure** | Login, registration, or session management broken | 2 | 3 |
| **Core user flow regression** | The primary happy path breaks after a change | 2 | 3 |
| **Silent API failure** | API returns 200 but produces wrong output | 2 | 2 |
| **Security vulnerability** | Injection, access control bypass, sensitive data exposure | 1 | 3 |
| **UX breakage** | UI renders incorrectly, interactions unresponsive | 2 | 2 |
| **Performance degradation** | Slow response times under normal load | 1 | 2 |
| **Environment drift** | Staging behaves differently from production | 2 | 2 |
| **Migration failure** | Schema change breaks existing data or API | 1 | 3 |
| **CI gate failure** | Broken tests block deploys, or tests pass despite real regressions | 2 | 2 |

### Step 3 — Adjust scores with user input

For each category where the default score seems off, ask:
> "My default assessment of [X] is likelihood [N], impact [N]. Does that feel right given your project, or should we adjust it?"

Override defaults based on user response.

### Step 4 — Build the risk register

Sort by **Risk Score = Likelihood × Impact** (descending).

```markdown
| Risk | Likelihood | Impact | Score | Status | Recommended Action |
|------|-----------|--------|-------|--------|-------------------|
| Auth failure | 2 | 3 | 6 | Unmitigated | Add E2E smoke test for login flow |
| Data loss | 1 | 3 | 3 | Has backup | Verify restore procedure works |
| Core flow regression | 2 | 2 | 4 | Minimal tests | Add integration tests for primary flow |
```

### Step 5 — Map risks to QA actions

For each high-score risk (score ≥ 4), assign a concrete action:

| Risk Score | Recommended Response |
|------------|---------------------|
| 6–9 (Critical) | Block current work. Add test or protection before next deploy. |
| 4–5 (High) | Add to current sprint / next PR. Do not accumulate more than 2 unresolved. |
| 2–3 (Medium) | Add to backlog. Address during next refactor or related feature work. |
| 1 (Low) | Document. Review quarterly. |

## Risk → QA Action Mapping

| Risk Category | Primary QA Action | Secondary Action |
|---------------|------------------|-----------------|
| Data loss | Verify backup + restore procedure | Add pre-migration backup step |
| Auth failure | E2E test: register → login → logout → protected route | API integration test for token validation |
| Core user flow regression | E2E test for primary happy path | Add to smoke suite (run on every deploy) |
| Silent API failure | Integration test with response body assertions | Schema validation on API responses |
| Security vulnerability | OWASP audit (access control, input validation, injection) | Rate limiting on auth endpoints |
| UX breakage | Visual regression test or manual smoke checklist | e.g. Playwright E2E on critical UI interactions |
| Performance degradation | Add response time assertion to health check | Load test for primary endpoint |
| Environment drift | Environment parity checklist (see test-environments.md) | Automated parity check in CI |
| Migration failure | Dry-run migration on staging first | Pre-migration backup; rollback SQL documented |
| CI gate failure | Audit test suite for false positives / missing assertions | Review CI job coverage vs. risk register |

## Risk Register Template

Copy this into your project's `docs/qa/risk-register.md`:

```markdown
---
updated: YYYY-MM-DD
reviewer: <name>
---

# QA Risk Register

| # | Risk | Likelihood (1-3) | Impact (1-3) | Score | Status | Owner | Action | Due |
|---|------|-----------------|-------------|-------|--------|-------|--------|-----|
| 1 | | | | | Unmitigated | | | |
```

## Reassessment Triggers

Re-run this risk assessment when:
- A new feature area is being built
- A production incident occurs (update scores upward for affected category)
- A previously high-risk area gets mitigated (update scores downward)
- More than 4 weeks have passed since last review
- The team size or deployment frequency changes significantly

## Interaction Pattern

The agent should:
1. Share its initial risk scores as a starting point, not as final truth
2. Explicitly ask the user to confirm or adjust each high-score risk
3. Not prescribe all actions at once — focus on the top 2–3 and ask if the user wants to continue
4. Record the agreed risk register in `docs/qa/risk-register.md` when asked
