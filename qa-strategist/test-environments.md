# Test Environments

Design and maintain the environment topology that lets you develop and test safely without ever touching production data. Local and staging environments are the two critical layers — they must be trustworthy to be useful.

## Environment Topology

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Local    │ →  │   Staging   │ →  │ Production  │
│  (developer)│    │  (validate) │    │  (users)    │
└─────────────┘    └─────────────┘    └─────────────┘
     ↕                  ↕                   ↕
  local DB          staging DB          prod DB
  (isolated)        (isolated)          (real data)
```

**Key rule:** Data never flows from production to staging/local. Each environment has its own independent database with its own seed data.

## Local Environment

**Purpose:** Fast iteration. Deterministic state. No external dependencies required.

### Requirements

- [ ] **One-command startup** — `docker compose up` or equivalent starts the full stack (DB + API + frontend)
- [ ] **Deterministic seed data** — a seed script creates a known, consistent state every time
- [ ] **Isolated database** — local DB is never connected to staging or production
- [ ] **Environment variables documented** — `.env.example` with all required variables and descriptions
- [ ] **Hot reload** — code changes are reflected without restarting the stack

### Local setup checklist

```markdown
| Component | Status | Notes |
|-----------|--------|-------|
| docker-compose.yml with all services | ✅ / ❌ | db + api + frontend |
| .env.example complete | ✅ / ❌ | all vars documented |
| Seed script exists | ✅ / ❌ | scripts/seed.ts or equivalent |
| One-command startup works | ✅ / ❌ | make dev / docker compose up |
| Hot reload on code change | ✅ / ❌ | |
```

### Seed data strategy

A seed script should create:
1. At least one user account with known credentials (e.g., `dev@example.com` / `password`)
2. Representative state for the primary user flow (not empty, not overwhelming)
3. Edge cases useful for testing (e.g., a user with no history, a user with full history)

The seed should be **idempotent** — running it twice gives the same state as running it once.

### QA / Time-travel Mode

For testing time-sensitive flows (e.g., day validation, streaks, history), consider a QA mode that exposes:
- A way to override the current date
- A way to seed specific historical state
- An endpoint to reset to a known state between tests

This avoids slow test setups and makes reproducible test scenarios trivial.

## Staging Environment

**Purpose:** Final validation before production. Structural clone of production. Independent data.

### Requirements

- [ ] **Deploys automatically** from the staging branch (e.g., `develop`)
- [ ] **Independent database** — never seeded from a production dump
- [ ] **Independent secrets** — different JWT secret, API keys, etc. from production
- [ ] **CORS restricted** — only the staging frontend URL is allowed
- [ ] **Accessible to the team** — developers and QA can log in and test
- [ ] **Resettable** — staging data can be reset to a clean state without manual intervention

### Staging configuration checklist

| Config | Staging Value | Notes |
|--------|--------------|-------|
| Database | `postgres-staging` | Independent, never from prod dump |
| JWT_SECRET | Different from prod | Tokens from staging invalid in prod |
| ALLOWED_ORIGINS | Staging URL only | Prevents accidental prod CORS bleed |
| Auto-deploy | On merge to `develop` | Validate before promoting to prod |
| Seed data | From seed script | Deterministic, representative |

### What staging must match from production

| Aspect | Must Match? | Why |
|--------|-------------|-----|
| Application version | Yes | Staging must run the exact code going to prod |
| Database schema | Yes | Schema differences cause false confidence |
| Environment variable names | Yes | Missing vars in prod = runtime crash |
| Infrastructure (CPU/memory class) | Roughly | Exact match not required for functional testing |
| Third-party service configuration | Yes (or mocked) | Auth providers, email, etc. must behave the same |

### Staging data lifecycle

- **Seed on first deploy** — staging DB starts from the seed script
- **Never restore from prod** — staging data is synthetic and disposable
- **Reset when corrupted** — if staging data is in a broken state, reset from seed rather than manually fixing
- **Do not fix bugs by editing staging data** — fix the bug in code

## Environment Parity Checklist

Run this check before promoting staging to production:

```markdown
- [ ] Staging and prod are running the same app version
- [ ] All environment variables present in staging are also set in production
- [ ] Database schema is in sync (migrations ran in both)
- [ ] No staging-only code paths in the release (QA flags disabled)
- [ ] Third-party integrations tested in staging
- [ ] Manual smoke test passed on staging
```

## Environment Variable Management

| Variable | Local | Staging | Production |
|----------|-------|---------|------------|
| DATABASE_URL | local postgres | staging postgres | prod postgres |
| JWT_SECRET | any dev secret | unique staging secret | unique prod secret (rotated) |
| ALLOWED_ORIGINS | localhost | staging URL | prod URL |
| API_URL | localhost port | staging API URL | prod API URL |
| QA_MODE | true | false | false |

**Never commit real secrets.** Use `.env.example` for documentation. Use the hosting platform's secret management (e.g., Railway environment variables) for real values.

## Common Pitfalls

| Pitfall | Risk | Fix |
|---------|------|-----|
| Staging seeded from prod dump | Real user data in staging; GDPR risk | Always seed from script |
| Shared database between staging and local | Changes corrupt each other | Each environment has its own DB |
| Same JWT_SECRET across environments | Staging tokens valid in prod | Unique secret per environment |
| QA_MODE enabled in production | Exposes internal test endpoints | Strict env-var guard; assert false in prod |
| `.env` committed to git | Secrets exposed | `.env` in `.gitignore`; only `.env.example` committed |
