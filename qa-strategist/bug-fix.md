# Bug Fix Workflow

Structured process for fixing a confirmed bug: from branch creation through a green CI pipeline. Every step is mandatory and must be completed in order.

## Guiding Principles

- **Reproduce before fixing** — a failing test that demonstrates the bug is the proof that you understand it
- **Minimal scope** — the fix touches only what is necessary; no opportunistic cleanup
- **CI is the final judge** — a fix is done only when the pipeline is green on the PR
- **Questions first, code second** — if the expected behavior is ambiguous, ask before writing a single line

---

## Step 1 — Create a Branch

Branch off the default integration branch (`main`, `develop`, or equivalent). Naming convention: `fix/<issue-id>-<short-description>`.

```bash
git checkout main           # or develop — whichever is the integration branch
git pull origin main
git checkout -b fix/<issue-id>-<short-description>
git push -u origin fix/<issue-id>-<short-description>
```

> If no issue ID is available, use a brief slug: `fix/payment-rounding-error`.

---

## Step 2 — Put the Issue In Progress

Move the issue to **In Progress** in the project tracker before writing any code.

Using the GitHub CLI:

```bash
# If using GitHub Issues + Projects
gh issue edit <issue-number> --add-label "in-progress"

# If the project board supports status fields via gh api, update the status field
# (see project-specific tooling for GitKraken / Linear / Jira equivalents)
```

> This signals ownership and prevents duplicate work.

---

## Step 3 — Write a Failing Test for the Bug

Write a test that **reproduces the bug and currently fails**. This is non-negotiable: if you cannot write a failing test, the bug is not yet understood.

### Before writing the test — clarify behavior if needed

Ask yourself: **Is the expected correct behavior explicitly described in the ticket?**

- **Yes** → write the test directly from the ticket's acceptance criteria
- **No / ambiguous** → **use `ask_user` to ask a clarifying question before proceeding**

#### Questions to ask when behavior is ambiguous

- "The ticket says X is broken, but it doesn't say what the correct output should be. Should it be [A] or [B]?"
- "Is this a regression (it used to work) or a first-time implementation gap?"
- "Are there edge cases the fix should cover that aren't mentioned in the ticket (e.g. empty input, concurrent requests)?"

> Do not assume. Do not infer from unrelated code. Ask the question, get an answer, document it in the ticket as a comment, then write the test.

### Writing the test

Prefer adding the test to the existing test file closest to the breakage site. If no suitable test file exists, create one.

```
Pattern:
  describe("<component / function being tested>", () => {
    it("should <expected correct behavior> when <condition that triggers the bug>", () => {
      // Arrange: set up the state that triggers the bug
      // Act:     call the function / trigger the flow
      // Assert:  confirm the output that should be true but currently isn't
    });
  });
```

Run the test suite and confirm the new test **fails** before moving on:

```bash
# Run only the new test to confirm it is red
bun test --filter "<test description>"     # or: npm test, pytest -k, etc.
```

---

## Step 4 — Plan the Fix

Before editing production code, write a short fix plan (a few bullet points is enough):

1. **Root cause** — what exactly is wrong and why?
2. **Change location** — which file(s) and function(s) need to change?
3. **Approach** — what is the minimal change that makes the test pass?
4. **Side effects** — what adjacent behavior could be affected? Which existing tests cover that area?

> If the root cause is not clear from reading the code, use `search` and `read` to trace the data flow before planning. Do not guess.

Document the plan as a comment in the PR description (written in Step 6) — it becomes the review narrative.

---

## Step 5 — Implement & Verify the Tests Pass

Apply the planned fix with minimal scope. Then run the full test suite:

```bash
# Run the full suite to catch regressions
bun test          # or: npm test / pytest / go test ./...

# Also run lint and type checks
bun run lint      # or: npm run lint / ruff check . / etc.
```

**Required outcomes before continuing:**

- [ ] The new failing test now **passes**
- [ ] All previously passing tests still **pass**
- [ ] Lint and type checks **pass**

If any previously passing test now fails, the fix has introduced a regression. Revisit the plan before continuing.

---

## Step 6 — Create a Pull Request

Open a PR targeting the integration branch. The description must include:

- **What:** one-sentence summary of the bug
- **Why it happened:** root cause (from Step 4)
- **How it was fixed:** summary of the change
- **How to verify:** steps or test name that demonstrates the fix

```bash
gh pr create \
  --base main \
  --title "fix(<scope>): <short description> (#<issue-number>)" \
  --body-file /tmp/pr-body.md    # write the body to a file first, then reference it
```

Link the issue so it auto-closes on merge:

```
Closes #<issue-number>
```

---

## Step 7 — Assess CI

After the PR is open, **wait for CI to complete** and verify every check is green.

```bash
# Watch CI status in the terminal
gh pr checks <pr-number> --watch
```

### If CI fails

| Failure type | Action |
|---|---|
| Test failure on a test you wrote | Fix the implementation or the test — do not skip or suppress |
| Pre-existing flaky test | Re-run once; if it fails again, investigate — do not merge over a flaky test |
| Lint / type error | Fix immediately; these are blocking |
| Infrastructure / runner issue | Re-run via `gh run rerun`; if it persists, flag to the team |

> **Do not merge until all required CI checks are green.** A passing local run is not a substitute for a passing CI run.

### Definition of Done

The bug fix is complete when:

- [ ] Branch exists and is pushed
- [ ] Issue is marked In Progress (and will auto-close when PR merges)
- [ ] A test reproducing the bug exists and was red before the fix
- [ ] All tests pass locally after the fix
- [ ] PR is open with a clear description and linked issue
- [ ] All CI checks are green
