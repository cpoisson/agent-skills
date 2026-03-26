# Hotfix & Rollback

Emergency procedures for production incidents. Speed and clarity matter more than process elegance when users are affected. This sub-skill gives you a playbook to follow under pressure.

## Incident Severity Levels

Define severity before deciding on response speed:

| Level | Definition | Example | Response Time |
|-------|-----------|---------|--------------|
| **P0 — Critical** | Core functionality down for all users; data at risk | Login broken, database unreachable, data loss | Immediate |
| **P1 — High** | Core functionality impaired for most users | Primary flow broken, slow response times >10s | Within 1 hour |
| **P2 — Medium** | Non-critical feature broken; workaround exists | Rewards broken, badge display wrong | Same day |
| **P3 — Low** | Minor UX issue; no data impact | Wrong error message, layout glitch | Next sprint |

P0 and P1 trigger the emergency playbook. P2 and P3 go through the normal bug fix process.

## Emergency Playbook

### Step 1 — Detect

- Error tracking alert fires, or user reports a P0/P1
- Confirm the issue is real: verify in production, not just from a report
- Identify the scope: is it all users, some users, a specific feature?

### Step 2 — Assess

Answer these questions before acting:

1. When did it start? (correlate with last deploy time)
2. Is this caused by the most recent deploy?
3. Is data being corrupted or lost right now? (if yes → highest priority)
4. What is the fastest path to recovery: rollback or hotfix?

### Step 3 — Decide: Rollback or Hotfix?

```
Is the issue caused by the most recent deploy?
  NO  → investigate; may not be a deploy-caused issue
  YES → continue

Can rolling back the deploy fix it without data issues?
  YES → ROLLBACK (fastest path)
  NO  → Is the schema unchanged?
          YES → ROLLBACK still viable
          NO  → HOTFIX required (rollback would break schema)
```

**Default:** Prefer rollback when in doubt. A rollback is reversible; a rushed hotfix may not be.

### Step 4 — Execute Rollback

**Git-based rollback (revert the commit)**

```bash
# Identify the commit that introduced the issue
git log --oneline -10

# Revert it (creates a new commit — safe for shared branches)
git revert <commit-hash>

# Push to the production branch
git push origin main

# Verify the deploy completes successfully
# Check health endpoint
# Verify the primary user flow works
```

**Platform redeploy to previous version**

Most hosting platforms (Railway, Vercel, Render) allow redeploying a previous build:
```
Railway: Dashboard → Service → Deployments → click previous successful deploy → Redeploy
```

This is faster than a git revert when the platform supports it.

### Step 5 — Execute Hotfix (when rollback is not viable)

```bash
# Create hotfix branch off main (production), not develop
git checkout main
git pull origin main
git checkout -b hotfix/<brief-description>

# Make the minimal fix — only what is needed to stop the bleeding
# ...

# Test locally
bun test
bun run lint

# Open emergency PR directly to main
gh pr create --base main --title "hotfix: <description>" --body "..."

# After merge to main, cherry-pick to develop to keep branches in sync
git checkout develop
git cherry-pick <hotfix-commit-hash>
git push origin develop
```

**Hotfix rules:**
- Fix only the immediate problem — do not refactor, improve, or add features
- Keep the diff as small as possible
- If you need to write a test, write it; if it significantly slows you down during P0, document it and add it in the follow-up
- Always cherry-pick back to `develop` after merging to `main`

### Step 6 — Verify Recovery

After rollback or hotfix deploys:

```markdown
- [ ] Deployment succeeded (no build errors)
- [ ] Health check endpoint responds 200
- [ ] Primary user flow works (manual check in production)
- [ ] Error tracking shows the error rate returning to baseline
- [ ] Logs show no new unexpected errors
- [ ] Affected users can confirm the issue is resolved (if contactable)
```

### Step 7 — Post-Mortem

After the incident is resolved, write a post-mortem within 48 hours. Keep it blameless — focus on the system, not the person.

## Post-Mortem Template

```markdown
---
date: YYYY-MM-DD
severity: P0 | P1
duration: <how long users were affected>
---

# Post-Mortem: <Incident Title>

## Summary

One-paragraph description of what happened, the impact, and how it was resolved.

## Timeline

| Time | Event |
|------|-------|
| HH:MM | Issue detected |
| HH:MM | Cause identified |
| HH:MM | Rollback/hotfix initiated |
| HH:MM | Recovery confirmed |

## Root Cause

What was the underlying cause? (code bug, missing validation, infrastructure failure, etc.)

## Contributing Factors

- What allowed this to reach production?
- What made detection slow?
- What made recovery harder than it should have been?

## Impact

- How many users were affected?
- Was any data lost or corrupted?
- What functionality was unavailable?

## Resolution

What was done to fix it? (rollback / hotfix — link to PR)

## Prevention

| Action | Owner | Due |
|--------|-------|-----|
| Add regression test for this case | | |
| Improve monitoring/alerting for this signal | | |
| Gate that would have caught this before deploy | | |

## Lessons Learned

What did we learn that should influence future work?
```

## Database Rollback Considerations

Rolling back application code when a schema migration was involved:

| Scenario | Safe to rollback app? | Action |
|----------|----------------------|--------|
| Migration added a nullable column | ✅ Yes | Old code ignores the column |
| Migration renamed a column | ❌ No | Old code breaks; write forward hotfix |
| Migration dropped a column | ❌ No | Data is gone; write forward hotfix |
| Migration added an index | ✅ Yes | Index adds no behavior change |
| Migration changed a constraint | ⚠️ Maybe | Depends on data state |

When application rollback is blocked by a migration: write a forward hotfix that restores expected behavior with the new schema, rather than reverting the schema change.

## Runbook Checklist Card

Print or keep this handy for P0 moments:

```
INCIDENT RESPONSE CARD

1. DETECT   — Confirm in prod. Scope: all users / some / one feature?
2. ASSESS   — Last deploy time? Caused by deploy? Data at risk?
3. DECIDE   — Rollback or hotfix? (prefer rollback)
4. EXECUTE  — Rollback: revert commit or redeploy previous build
              Hotfix: branch off main → minimal fix → PR to main → cherry-pick to develop
5. VERIFY   — Health check + manual smoke test + error rate normalizing
6. DOCUMENT — Post-mortem within 48h
```
