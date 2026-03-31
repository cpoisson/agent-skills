# Release Train

Design a release process that builds confidence without creating unnecessary ceremony. For small teams and solo developers, the goal is a lightweight, repeatable cadence — not a ticket-driven waterfall.

## Core Concept

A release is not an event, it is a flow. Every change travels:

```
feature branch → staging → optional manual validation → production
```

The "release train" is the rhythm at which batches of changes are promoted from staging to production.

## Cadence Models

Choose the cadence that matches your team size and deployment risk:

| Model | Frequency | Best for |
|-------|-----------|---------|
| **Continuous** | Every merge to develop that passes CI + smoke | Low-risk, high-confidence codebase with strong test coverage |
| **Daily train** | Once per day, bundle staging changes into a prod release | Small team, moderate test coverage |
| **Weekly train** | Once per week, validate staging thoroughly | Early-stage product, mixed test coverage |
| **Feature-gated** | Release when a feature is complete and validated | New major features with high visibility |

**Default for early-stage product:** Weekly or feature-gated. Continuous delivery requires mature CI + staging validation.

## Develop → Main PR Checklist

Before opening a PR from `develop` → `main` (production):

```markdown
### Staging Validation
- [ ] All CI checks pass on develop (lint, types, tests, E2E smoke)
- [ ] All changes have been live on staging for at least [N hours / 1 day]
- [ ] Manual smoke test passed on staging for each changed flow
- [ ] No unresolved issues found during staging validation

### Code Quality
- [ ] No TODO comments introduced without a tracking issue
- [ ] No debug code, console.log, or temporary workarounds left in
- [ ] All new features have test coverage

### Data Safety
- [ ] Any migrations have been tested on staging
- [ ] Pre-migration backup plan confirmed (if releasing a schema change)
- [ ] Rollback plan documented (if high-risk change)

### Documentation
- [ ] CHANGELOG updated
- [ ] Specs updated if behavior changed
- [ ] README updated if setup or usage changed

### Post-Deploy Plan
- [ ] Post-deploy health check owner identified
- [ ] Monitoring in place to detect regressions
```

## Changelog Discipline

Maintain a `CHANGELOG.md` at the repo root. Update it with every PR that changes user-facing behavior.

### Format (Keep a Changelog convention)

```markdown
# Changelog

## [Unreleased]
### Added
- (new features not yet released)

## [1.2.0] — 2026-03-25
### Added
- Daily loop: task reordering via drag and drop
### Fixed
- Rewards: graines purchase now correctly deducts balance
### Changed
- Settings: PIN management UI redesigned for clarity
### Removed
- Legacy onboarding flow removed (replaced by guided setup)
```

Categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

**What belongs in the changelog:**
- User-visible behavior changes
- Bug fixes that affected users
- Security fixes (without details that could be exploited)
- Breaking changes (with migration guide)

**What does NOT belong:**
- Internal refactors with no behavior change
- Dependency updates (unless they fix a user-visible issue)
- Test additions or documentation updates

## Version Tagging

Tag releases in git so any version can be traced and redeployed:

```bash
# After merging develop → main and deploying:
git checkout main
git pull origin main
git tag v1.2.0 -m "Release 1.2.0: graines fix + task reordering"
git push origin v1.2.0
```

### Versioning strategy

Use **semantic versioning** (`MAJOR.MINOR.PATCH`):
- `PATCH` — bug fixes, no new features, backward-compatible
- `MINOR` — new features, backward-compatible
- `MAJOR` — breaking changes (rare for a product app; more common for libraries)

For pre-v1 products: use `0.MINOR.PATCH` freely. Graduate to `1.0.0` when the product is stable enough to make backward-compatibility promises.

## Release Readiness Checklist

A concise go/no-go check before every production deploy:

```markdown
| Check | Status |
|-------|--------|
| CI all green on develop | ✅ / ❌ |
| E2E smoke suite passing on staging | ✅ / ❌ |
| Manual smoke passed on staging | ✅ / ❌ |
| CHANGELOG updated | ✅ / ❌ |
| No known P0/P1 bugs in this release | ✅ / ❌ |
| Migration safety confirmed (if applicable) | ✅ / N/A |
| Rollback plan ready (if high-risk) | ✅ / N/A |
```

If any ❌: fix before releasing. Do not override without documenting why.

## Hotfix vs. Regular Release

| Scenario | Branch | Review | Merge target |
|----------|--------|--------|-------------|
| Regular feature/fix | `feat/*` or `fix/*` off `develop` | Normal PR review | `develop` first, then `main` via train |
| Hotfix (P0/P1 in production) | `hotfix/*` off `main` | Emergency review (fastest path) | `main` directly, then cherry-pick to `develop` |
| Patch (small fix, low risk) | `fix/*` off `develop` | Normal PR | `develop` → can promote to `main` same day |

## Anti-Patterns

| Anti-pattern | Risk | Fix |
|---|---|---|
| Pushing directly to `main` | Bypasses all gates; hard to trace | Always use PRs from `develop` |
| Releasing on Friday afternoon | No one available to respond to incidents | Prefer Mon–Thu releases |
| Batching too many unverified changes | Large blast radius | Smaller, more frequent releases |
| Skipping staging validation | False confidence | Staging is never optional |
| No rollback plan for schema changes | Stuck if migration breaks prod | Document rollback before every migration |
| CHANGELOG updated only at release | Incomplete history | Update with every PR |
