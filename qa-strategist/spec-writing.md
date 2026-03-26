# Spec Writing

Write and maintain living specifications that bridge user intent, implementation, and test coverage. Specs are the shared source of truth — they should be readable by humans, executable in spirit, and gap-detectable by tools.

## What Is a Living Spec?

A living spec is a markdown document with a YAML frontmatter header that describes:
- What the feature does (behaviour, not implementation)
- Acceptance criteria that can be directly translated to tests
- Open questions and ambiguities
- Current status (proposed / in-review / implemented / tested / deprecated)

Specs live in `docs/specs/{area}/{feature}.md`. They are versioned alongside code.

## Spec File Format

```markdown
---
title: <Feature Name>
area: <functional area: auth | daily-loop | rewards | settings | etc.>
status: proposed | in-review | implemented | tested | deprecated
version: "1.0"
last-verified: YYYY-MM-DD
owner: <name or team>
---

# <Feature Name>

## Summary

One-paragraph description of what this feature does from the user's perspective.

## User Story

As a [type of user], I want to [goal], so that [benefit].

## Acceptance Criteria

- [ ] AC1: <specific, testable criterion>
- [ ] AC2: <specific, testable criterion>
- [ ] AC3: <specific, testable criterion>

## Out of Scope

What this feature deliberately does NOT cover.

## Edge Cases

- <Edge case 1>: <expected behaviour>
- <Edge case 2>: <expected behaviour>

## Open Questions

- [ ] Q1: <unresolved question> (owner: <name>, due: <date>)

## Test Coverage

| # | Acceptance Criteria | Unit | Integration | E2E | Manual |
|---|---------------------|------|-------------|-----|--------|
| AC1 | | ❌ | ❌ | ❌ | ⬜ |
| AC2 | | ❌ | ❌ | ❌ | ⬜ |

## Change Log

- YYYY-MM-DD: Initial draft
```

## Gap Analysis

A spec gap analysis compares three layers:
1. **Spec exists** — is there a written specification?
2. **Implementation exists** — is the feature built?
3. **Tests exist** — are there tests covering the acceptance criteria?

Run this analysis per functional area:

```markdown
| Feature | Spec | Implemented | Unit tests | Integration tests | E2E tests | Gaps |
|---------|------|-------------|-----------|-------------------|-----------|------|
| Login | ✅ | ✅ | ✅ | ✅ | ✅ | None |
| Register | ✅ | ✅ | ❌ | ❌ | ❌ | No tests at all |
| Onboarding | ❌ | ✅ | ❌ | ❌ | ❌ | No spec, no tests |
| Rewards | ✅ | ⚠️ partial | ✅ | ❌ | ❌ | Implementation not complete |
```

Gap types and priorities:
- **No spec, no tests** → write spec first; tests are blocked until spec is clear
- **Spec exists, no tests** → add tests against AC; these are the easiest to write
- **Implementation exists, no spec** → reverse-engineer spec from code and review with team
- **Spec and implementation diverge** → flag immediately; decide which is wrong

## Ambiguity Detection Checklist

When reviewing a spec, flag any of the following patterns as ambiguous:

- [ ] Vague quantifiers: "fast", "quickly", "sometimes", "usually"
- [ ] Missing actor: who initiates the action?
- [ ] Missing error state: what happens if it fails?
- [ ] Missing boundary conditions: what happens at the limit (empty input, max length, zero, negative)?
- [ ] Untestable criterion: "users should feel confident" — what is the measurable proxy?
- [ ] Assumed context: "as before", "same as X" without a reference
- [ ] Missing data state: the criterion is silent about what state the system is in beforehand

For each ambiguity found, add an Open Question to the spec and assign an owner.

## Writing Acceptance Criteria

Acceptance criteria should be:
- **Specific**: describe exact conditions, not general outcomes
- **Testable**: a human or a computer can verify it unambiguously
- **Independent**: each criterion stands alone; no hidden dependencies
- **Positive and negative**: include at least one unhappy path per feature

Good AC:
```
✅ When the user submits the login form with a valid email and password, 
   the app redirects to /app and a session token is stored in localStorage.

✅ When the user submits the login form with an incorrect password, 
   the API returns 401 and the UI displays "Invalid credentials".
```

Poor AC:
```
❌ The login should work correctly.
❌ Users can log in.
❌ Errors are handled properly.
```

## Spec-to-Test Traceability

Each test case should reference the AC it covers. In test files, add a comment or tag:

```typescript
// AC: Login — valid credentials redirect to /app
test('redirects to /app after successful login', async ({ page }) => {
  ...
});

// AC: Login — invalid password returns 401 and shows error message  
test('shows error message on wrong password', async ({ page }) => {
  ...
});
```

This traceability lets you answer: "Which ACs are not covered by any test?" — an automated gap report.

## Update Workflow

Update a spec when:
- A feature changes behavior (implementation diverges from spec)
- An open question is resolved
- A bug is fixed that was caused by a spec ambiguity
- A test reveals the spec was wrong

Update the `last-verified` date and `status` field with every meaningful change. Deprecate specs for removed features rather than deleting them — they serve as historical record.

## Spec Directory Structure

```
docs/specs/
├── auth/
│   ├── login.md
│   └── register.md
├── daily-loop/
│   ├── task-validation.md
│   └── day-validation.md
├── rewards/
│   └── graines-purchase.md
├── settings/
│   ├── pin-management.md
│   └── account-deletion.md
└── README.md    ← index of all specs with status summary
```

The `docs/specs/README.md` index should list all specs with their `status` field — a one-line overview of what's specified, implemented, and tested.
