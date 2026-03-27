# Agentic Coding QA

Quality assurance for code written by AI coding agents. In the agentic era, the bottleneck shifts from writing code to verifying it. This sub-skill defines how agents (and the humans who use them) establish a meaningful definition of done, use tests as executable contracts, and avoid the most common failure modes of AI-generated code.

## The Core Problem

An AI coding agent can:
- Write syntactically correct code that compiles and runs
- Pass a test suite that doesn't test the right things
- Make a change that satisfies the stated request while breaking adjacent behavior
- Produce plausible-looking code that silently returns wrong results

**"It compiles" is not a definition of done. "The tests pass" is only as good as the tests.**

## Definition of Done for Agent-Generated Code

A task is done when all of the following are true:

### Tier 1 — Mandatory (block merge if failing)

- [ ] **All existing tests pass** — the change does not break anything currently tested
- [ ] **Lint and type checks pass** — code meets the project's style and type contracts
- [ ] **New behavior is covered** — any new logic, API endpoint, or user-facing behavior has at least one test
- [ ] **No hardcoded credentials, secrets, or user data** in the changed code
- [ ] **The change is scoped** — it only touches what was asked; no unrelated modifications

### Tier 2 — Required for non-trivial changes

- [ ] **Unhappy paths are handled** — error states, missing input, and edge cases are addressed
- [ ] **Input is validated** at the system boundary (API request bodies, user form inputs)
- [ ] **Data mutations are safe** — no destructive DB operations without appropriate guards
- [ ] **The change works in staging** (for API/backend changes)

### Tier 3 — For changes to critical flows

- [ ] **E2E smoke test passes** for any affected user-facing flow
- [ ] **Spec is updated** if behavior diverged from the existing spec
- [ ] **Risk register is reviewed** if the change touches an area marked high-risk

## Test-as-Contract Pattern

Tests are the most unambiguous way to specify what a function, endpoint, or component should do. Treat them as executable contracts between the agent and the rest of the system.

**Before starting a task, state the expected behavior as tests:**

```
Request: "Add a function that calculates the level from a point total"

Contract (test first):
- calculateLevel(0) → 1
- calculateLevel(99) → 1
- calculateLevel(100) → 2
- calculateLevel(500) → 6
- calculateLevel(-1) → throws / returns 1

Now write the implementation that satisfies these contracts.
```

This pattern forces clarity before code. It also makes verification unambiguous: the agent is done when the tests pass, not when it feels done.

## When Agents Should Write Tests Before Code (TDD in Agent Context)

Write the test first when:
- The function has clear inputs and expected outputs (calculation, transformation, validation)
- The behavior is specified in an AC or spec document
- The agent is fixing a confirmed bug (test reproduces the bug first)

Write tests after the code when:
- The shape of the output is not known until the code is written (exploratory)
- The feature is complex UI that needs iteration before assertions make sense
- The agent is scaffolding structure, not implementing logic

**Default:** For any data logic or API handler, write the test specification first, even informally as comments, before implementing.

## Agent Self-Verification Steps

After completing a task, an agent should run through this checklist before declaring done:

```
1. Run tests:              bun test / npm test / pytest
2. Run lint:               bun run lint / eslint / ruff
3. Run type check:         bun run build / tsc --noEmit / mypy
4. Search for regressions: grep for any function/variable I renamed or deleted
5. Check scope:            git diff — did I touch files unrelated to the task?
6. Check for secrets:      grep for hardcoded credentials, tokens, or passwords
7. Read the failing test:  if any test fails, understand why before dismissing it
8. Smoke test:             if the task affects a UI flow, manually verify it works
```

## Common Agent Failure Modes

| Failure Mode | How to Detect | Prevention |
|---|---|---|
| Scope creep — touches unrelated files | `git diff` review before commit | Tight task scoping; one task per PR |
| Plausible but wrong logic | Tests with edge cases; review AC | Test-first specification |
| Silently drops error handling | Code review; integration test with error cases | Unhappy path tests required |
| Removes used code incorrectly | `grep` for removed symbols; TypeScript errors | Full type check before merge |
| Passes tests written for wrong spec | Manual review of test assertions | AC-to-test traceability |
| Hardcodes test data in production code | Secret scanning; code review | Only constants in a dedicated config file |
| Merges half-finished work | PR description completeness check | DoD checklist in PR template |

## AGENTS.md Integration

Project-level AGENTS.md should document the minimum verification steps expected from any coding agent:

```markdown
## Validation

Before marking any task complete:
1. Run the project test command (e.g. `bun test` / `npm test` / `pytest`) — all tests must pass
2. Run the project lint command (e.g. `bun run lint` / `eslint .` / `ruff check .`) — no new errors
3. Run the project type check or build command — no type errors
4. If you added new behavior: add at least one test for it
5. If you fixed a bug: add a regression test that would have caught it
6. Confirm `git diff` does not include unrelated changes
```

## Writable Definition of Done Template

Add this to your PR template (`.github/pull_request_template.md`):

```markdown
## Definition of Done

- [ ] All existing tests pass
- [ ] Lint passes
- [ ] Type check passes
- [ ] New behavior has test coverage
- [ ] No unrelated file changes
- [ ] Tested in staging (for API/backend changes)
- [ ] Spec updated if behavior changed
```

## On Test Coverage as a Proxy

Coverage percentage is a weak signal for agent-generated code. An agent can trivially hit 90% coverage with tests that don't assert anything meaningful.

Better proxies for agentic code quality:
- **Mutation testing** — do tests fail when the code is deliberately broken?
- **AC coverage** — are all acceptance criteria mapped to a test?
- **Regression rate** — how many bugs are caught before production vs. after?
- **Definition of done adherence** — does every PR have test coverage for new behavior?
