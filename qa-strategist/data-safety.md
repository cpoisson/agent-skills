# Data Safety

Protect user data from accidental loss, corruption, and unsafe changes. Data safety is not an optional extra for production applications — it is a baseline. Once real user data is live, a data loss incident can destroy trust that took months to build.

## The Three Pillars

1. **Backups** — you can recover data if it is lost or corrupted
2. **Restore testing** — you have actually verified that recovery works
3. **Migration safety** — schema changes cannot corrupt or destroy data

All three must be in place before an application is relied upon by real users.

## Backup Strategy

### Minimum viable backup plan

| Dimension | Minimum | Better |
|-----------|---------|--------|
| Frequency | Daily | Hourly or continuous (WAL archiving for Postgres) |
| Retention | 7 days | 30 days rolling + monthly snapshots |
| Storage | Same platform | Different provider / region |
| Automation | Managed by platform | Custom backup script + verification |

### Backup coverage checklist

```markdown
- [ ] Automatic backups are enabled on the database
- [ ] Backup frequency meets the acceptable data loss window
- [ ] Backups are retained for a sufficient period
- [ ] Backups are stored in a separate location from the primary database
- [ ] Backup files are verified (not just created)
- [ ] A restore procedure is documented
- [ ] The restore procedure has been tested successfully at least once
```

### What to back up

- **Database** — the primary source of truth; always back up
- **User-uploaded files / media** — if stored separately, include in backup scope
- **Application configuration** — environment variables, infra config (document, don't back up secrets in plaintext)

### Backup script essentials

A backup script should:
1. Create a dump of the database (`pg_dump`, `mysqldump`, etc.)
2. Compress the output (`gzip`, `zstd`)
3. Name with timestamp: `backup-2026-03-25T14:00:00.sql.gz`
4. Upload to remote storage
5. Verify the upload succeeded (check size, checksum)
6. Clean up old backups beyond the retention window
7. Log success/failure with timestamp

```bash
# Minimal postgres backup example
DATE=$(date +%Y%m%dT%H%M%S)
FILENAME="backup-${DATE}.sql.gz"
pg_dump "$DATABASE_URL" | gzip > "/tmp/${FILENAME}"
# Upload to storage (s3, railway object storage, etc.)
# Verify
# Rotate old files
```

## Restore Testing

A backup that has never been tested is not a backup — it is a hope.

### Restore test procedure

```markdown
1. Identify a backup file to test (use a recent one, not the oldest)
2. Spin up a temporary/isolated database instance
3. Restore the backup into it:
   gunzip -c backup-TIMESTAMP.sql.gz | psql $TEST_DATABASE_URL
4. Verify data integrity:
   - Row counts in key tables match expectations
   - A known record can be queried
   - Application can connect and serve basic requests against the restored DB
5. Document the result: date tested, backup file used, outcome
6. Tear down the test instance
```

### Restore test schedule

- **Minimum:** Test restore once per month
- **After any major schema migration:** Test restore with post-migration backup
- **After any backup system change:** Immediate test restore

### Restore drill documentation template

```markdown
| Date | Backup File | Test DB | Rows Verified | Outcome | Tested By |
|------|-------------|---------|--------------|---------|-----------|
| 2026-03-25 | backup-20260325T020000.sql.gz | tmp-restore-1 | users: 42, families: 15 | ✅ Pass | |
```

## Migration Safety

Database schema changes are the highest-risk operations in a production system. A bad migration can corrupt data, break the running API, or cause downtime.

### Pre-migration checklist

```markdown
- [ ] The migration has been tested on staging with production-like data volume
- [ ] A backup was taken immediately before running the migration
- [ ] A rollback script (reverse migration) is written and tested
- [ ] The migration is backward-compatible (old app code can run against new schema)
- [ ] The migration is idempotent (safe to run twice if something interrupts it)
- [ ] Team is available to respond if the migration fails
```

### Backward-compatible migration rules

Never do these in a single deploy:

| ❌ Unsafe | ✅ Safe alternative |
|----------|-------------------|
| Rename a column | Add new column → backfill → update app → remove old column (3 deploys) |
| Drop a column still read by app | Remove all reads from app first → then drop in next migration |
| Add NOT NULL without default | Add as nullable → backfill → add constraint |
| Change a column type | Add new column with new type → migrate data → update app → drop old |

### Rollback script rule

For every migration file, create a matching rollback file:

```
migrations/
  003_add_feature_flags.sql          ← migration
  003_add_feature_flags.rollback.sql ← rollback
```

The rollback script should restore the schema to its pre-migration state without losing any data that existed before the migration.

## Data Integrity

Prevent silent data corruption by enforcing integrity at the database level:

- **Foreign keys** — enforce relationships; prevent orphaned records
- **NOT NULL constraints** — fields that must always have a value should be constrained
- **Check constraints** — enforce business rules at the DB level (e.g., points >= 0)
- **Unique constraints** — prevent duplicate records where uniqueness is required
- **Indices** — ensure query correctness for date/time queries that depend on ordering

### Integrity health check queries

Run periodically to detect anomalies:

```sql
-- Orphaned records (example: tasks without a family)
SELECT COUNT(*) FROM tasks WHERE family_id NOT IN (SELECT id FROM families);

-- Negative values where they shouldn't exist
SELECT COUNT(*) FROM children WHERE points < 0;

-- Records with future timestamps (time-travel bug indicator)
SELECT COUNT(*) FROM days WHERE date > CURRENT_DATE + INTERVAL '1 day';
```

## Staging Data Safety

- Staging database is **never** populated from a production dump
- Staging data contains **no real user data**
- If this rule is ever broken (accidentally), treat it as a data breach — notify affected users
- Use a seed script to create synthetic, representative data for staging

## Quick Assessment

| Check | Status |
|-------|--------|
| Automatic backups enabled | ✅ / ❌ |
| Backup retention ≥ 7 days | ✅ / ❌ |
| Restore procedure documented | ✅ / ❌ |
| Restore tested successfully | ✅ / ❌ |
| Pre-migration backup in workflow | ✅ / ❌ |
| Rollback script for each migration | ✅ / ❌ |
| Staging never seeded from prod | ✅ / ❌ |
| Foreign keys enforced in schema | ✅ / ❌ |
