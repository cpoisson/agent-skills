# Production / Development Isolation

Protect users from the consequences of your changes. This sub-skill covers the gates, guards, and practices that prevent development and testing activity from reaching production users unintentionally.

## The Core Principle

Every change should travel a path: **local → tested → staged → reviewed → production**.

The narrower the gap between any two steps, the smaller the blast radius if something goes wrong.

## Change Protection Gates

A gate is a mandatory check that must pass before a change can proceed to the next stage.

### Recommended gate chain

```
Write code
    │
    ▼
[ Gate 1: Local tests pass ]
    │  bun test / pytest / go test
    ▼
[ Gate 2: Lint + type check pass ]
    │  tsc, eslint, ruff
    ▼
Open PR
    │
    ▼
[ Gate 3: CI passes ]
    │  unit tests + integration tests + lint in CI
    ▼
[ Gate 4: Code review ]
    │  human review (or agent review + human approval for solo projects)
    ▼
Merge to staging branch
    │
    ▼
[ Gate 5: Staging deploy succeeds ]
    │  auto-deploy on merge to staging branch
    ▼
[ Gate 6: E2E smoke suite passes on staging ]
    │  fast Playwright smoke tests — staging must always be in a working state
    │  if the full suite is too slow, run only the critical-path subset here
    ▼
[ Gate 7: Manual spot check (optional) ]
    │  verify specific changed flows if needed
    ▼
Merge to production branch
    │
    ▼
[ Gate 8: Post-deploy health check ]
    └  smoke test against production immediately after deploy
```

**Staging is always working.** Gate 6 is a hard gate — a failing E2E smoke on staging blocks the path to production. If the full E2E suite takes too long to run on every merge, split it:
- **On merge to staging** → fast smoke suite (critical user flows, <5 min)
- **Nightly** → full E2E suite against staging (all flows, edge cases, slow tests)

**Minimum viable gate chain (solo project):** Gates 1, 2, 3, 5, 6, 8.

## Database Migration Safety

Schema changes are the highest-risk category of change — they can corrupt data or break deployed code if not handled carefully.

### Rules

1. **Always migrate before deploying code that depends on the new schema.**
2. **Backward-compatible migrations only** — do not rename or drop columns while old code is still live.
3. **Test migrations on staging first** — run the migration against staging data before production.
4. **Back up before migrating** — take a snapshot before running any migration in production.
5. **Include rollback SQL** — every migration should have a matching rollback script.

### Backward-compatibility patterns

| Operation | Safe? | Pattern |
|-----------|-------|---------|
| Add a nullable column | ✅ Yes | Old code ignores it; new code reads it |
| Add a column with a default | ✅ Yes | Old code ignores it; new code reads it |
| Rename a column | ❌ No | Add new column, copy data, deprecate old, remove in next release |
| Drop a column | ❌ No | Remove all code reading it first, then drop in a subsequent migration |
| Add a NOT NULL column without default | ❌ No | Add as nullable first, backfill, then add constraint |
| Add an index | ✅ Yes (with CONCURRENTLY) | Use `CREATE INDEX CONCURRENTLY` to avoid table lock |

### Migration checklist

```markdown
- [ ] Migration tested on staging
- [ ] Pre-migration backup taken
- [ ] Rollback script written and tested
- [ ] Old code can run against the new schema (backward-compatible)
- [ ] New code can run against the old schema during the deploy window
- [ ] Migration is idempotent (safe to run twice)
```

## Feature Flags

Use feature flags to decouple deployment from release. Code ships to production but the feature is off until you turn it on.

### When to use

- New feature that is not ready for all users
- A risky change that you want to roll out gradually
- A behavior change dependent on infrastructure (e.g., a new background job)
- A/B testing a UI change

### Lightweight implementation (no flag service needed)

For small teams, a simple environment variable or database flag is sufficient:

```typescript
// Server-side: environment variable
const ENABLE_NEW_FEATURE = process.env.ENABLE_NEW_FEATURE === 'true';

// Database flag (per-user or per-tenant)
const { feature_flags } = await db.query(
  `SELECT feature_flags FROM users WHERE id = $1`, [userId]
);
const ENABLE_NEW_FEATURE = feature_flags?.newFeature ?? false;
```

When to graduate to a flag service: when you have >3 active flags, or when flag updates need to happen without a redeploy.

### Flag cleanup

Feature flags accumulate as technical debt. For each flag, define an expiry condition:
- "Remove this flag when the new feature is verified in production for 2 weeks"
- Add a TODO or ticket for flag removal at the time of creation

## Deploy Confidence Checklist

Run before merging to the production branch:

```markdown
### Pre-merge
- [ ] All CI checks pass (lint, types, tests)
- [ ] Manual smoke test passed on staging
- [ ] E2E smoke suite passed on staging
- [ ] Migration safety rules followed (if schema change)
- [ ] Pre-migration backup taken (if schema change)
- [ ] No unrelated files changed in the PR

### Post-deploy
- [ ] Deployment succeeded (no build/start errors)
- [ ] Health check endpoint responds 200
- [ ] Primary user flow works in production (quick manual check)
- [ ] Error tracking shows no new spike in errors
- [ ] Logs show no unexpected errors
```

## Blast Radius Reduction

Strategies to limit how much can go wrong in a single deploy:

| Strategy | Description | When to use |
|----------|-------------|------------|
| Small PRs | Keep changes tightly scoped | Always |
| Feature flags | Ship dark, enable gradually | High-risk new features |
| Staged rollout | Route % of traffic to new version | Platform support required |
| Database migration in isolation | Separate PR for schema change | Any schema change |
| Immutable deploys | Each deploy is a new version; rollback = redeploy previous | When platform supports it |

## Environment Protection Rules

| Rule | Rationale |
|------|-----------|
| Never push directly to `main` (production branch) | Bypasses all gates |
| Production database is never accessible from dev machines directly | Accidental mutations |
| `QA_MODE`, debug flags are off in production | Exposes internal state |
| Production secrets are not in local `.env` files | Leakage risk |
| Staging is the last stop before production — treat it seriously | Rushing through staging = skipping the gate |
