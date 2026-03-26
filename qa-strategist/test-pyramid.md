# Test Pyramid

Design, assess, and incrementally bootstrap a healthy test pyramid. The pyramid is not a destination — it is a growing scaffold you build alongside the product, starting with the minimum viable layer and adding to it with every bug fix and feature.

## The Pyramid

```
          ▲
         /E\      End-to-End (few, high value, slow)
        /   \     → Critical user journeys in a real browser
       /─────\
      / Integ \   Integration (moderate, covers API + DB contracts)
     /─────────\  → API endpoints, service boundaries, data flows
    /   Unit    \ Unit (many, fast, cheap)
   /─────────────\ → Pure logic, calculations, transformations
```

**Inverted pyramid (anti-pattern):** Too many E2E tests, too few unit tests. Slow, flaky, expensive to maintain.  
**Ice cream cone (anti-pattern):** Mostly manual testing, some E2E, no unit or integration. Bottleneck before every release.  
**Trophy (alternative model):** Emphasizes integration tests as the sweet spot. Valid for API-heavy apps. Overlaps with the pyramid at the integration layer.

## Layer Guidance

### Unit Tests

**Purpose:** Lock down business logic. Fast feedback. Safe refactoring.

**What to test:**
- Pure functions with clear inputs/outputs
- Calculation logic (pricing, scoring, date math, state transitions)
- Data transformation utilities
- Validation rules

**What NOT to unit test:**
- UI rendering (use component or E2E tests instead)
- Database queries (use integration tests)
- Network calls (mock or use integration tests)

**Target:** Every pure function with non-trivial logic. Aim for 100% coverage of the logic layer — not the whole codebase.

**Tools:** Jest, Vitest, pytest, Go test, etc.

### Integration Tests

**Purpose:** Verify components work together. Catches contract violations between layers.

**What to test:**
- API endpoints (request → response, including auth middleware)
- Database queries (real DB, controlled state)
- Service-to-service contracts
- Data flows through the system (input → storage → retrieval)

**What NOT to integration test:**
- Browser UI (use E2E)
- External third-party services (mock at the boundary)

**Target:** Every API endpoint with at least one happy-path test. High-value error paths (auth failure, validation errors, not-found).

**Tools:** Supertest, Hono test client, pytest + TestClient, httpx, etc.

### End-to-End Tests

**Purpose:** Validate critical user journeys from the user's perspective. The last line of defense before production.

**What to test:**
- The 5–10 flows that, if broken, would immediately hurt users
- Authentication and session management
- The primary value-delivering loop
- High-risk flows after major changes

**What NOT to E2E test:**
- Edge cases better covered by unit/integration tests
- Every permutation of a form field
- Admin or internal flows that are not user-facing

**Target:** Full coverage of the smoke suite (must pass on every deploy). Regression suite grows with each confirmed production bug.

**Tools:** Playwright (recommended), Cypress, etc.

### Manual / Exploratory

**Purpose:** Catch what automation misses. Validate new features before they enter the automation suite.

**When to use:**
- New feature validation before writing automated tests
- Accessibility and visual polish review
- Scenarios too complex or time-consuming to automate now
- Post-deploy production smoke check

**Formalize over time:** Exploratory tests that find bugs should become regression tests.

## Bootstrapping Strategy

### Phase 1 — Minimal Viable Pyramid (do this first)

1. **Identify the 3 highest-risk pure logic functions** → write unit tests for them
2. **Identify the primary happy-path API endpoint** → write one integration test
3. **Identify the most critical user journey** → write one E2E smoke test
4. **Wire all three to CI** — they must pass before any PR can merge

Done. You now have a working pyramid. It's small. Grow it.

### Phase 2 — Grow with bug fixes

Every confirmed production bug gets:
1. A failing test that reproduces the bug
2. A fix
3. The test stays permanently — it is now a regression test

This is the most sustainable way to grow the pyramid. Each bug adds value.

### Phase 3 — Grow with features

Every new feature gets:
1. Unit tests for any new logic
2. Integration test for any new API endpoint
3. E2E test if it introduces or changes a critical user flow

Not every feature needs all three layers — match the layer to the risk.

## Coverage Metrics That Matter

| Metric | Useful? | Notes |
|--------|---------|-------|
| Line coverage % | Partly | Useful to find dead zones; 100% is vanity |
| Branch coverage % | Yes | Ensures conditional paths are tested |
| API endpoint coverage | Yes | Track which endpoints have integration tests |
| User flow coverage | Yes | Track which flows are covered by E2E |
| Time-to-green (CI) | Yes | Fast feedback loop matter |
| Test flakiness rate | Yes | A flaky test is worse than no test |

**Avoid:** Coverage targets that incentivize writing tests for untestable/trivial code just to hit a number.

## CI Integration

Pyramid layer → CI gate mapping:

| Layer | CI Gate | Failure Policy |
|-------|---------|---------------|
| Unit | Run on every push + PR | Block merge if failing |
| Integration | Run on every PR | Block merge if failing |
| E2E smoke | Run on every PR + post-deploy | Block merge / alert on failure |
| E2E regression | Run on PR to main / nightly | Block main merge if failing |
| Manual | Pre-release checklist | Not automated |

## Pyramid Health Assessment

Ask these questions to assess the current state:

- [ ] Do unit tests exist for the core logic layer?
- [ ] Are unit tests in CI and blocking merges?
- [ ] Do integration tests exist for the primary API endpoints?
- [ ] Is there at least one E2E test for the primary user journey?
- [ ] Do E2E tests run in CI?
- [ ] Is the CI feedback loop under 10 minutes?
- [ ] Is the tests flakiness rate under 5%?
- [ ] Does every recent production bug have a corresponding regression test?

Score: 1 point per check. Interpret:
- 7–8: Healthy pyramid. Focus on coverage growth and speed.
- 5–6: Functional. Identify the missing layer and add it next.
- 3–4: At risk. Prioritize CI integration and gap closure.
- 0–2: Blind. Bootstrap Phase 1 immediately.
