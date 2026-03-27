---
name: qa-strategist
description: >
  QA strategy and quality confidence routing for software teams in the agentic era. Use this skill
  whenever the user mentions testing, QA, coverage, specs, release safety, observability, or data
  safety — even if they don't say "QA" explicitly. Trigger phrases: "test plan", "test coverage",
  "what should I test", "risk analysis", "test pyramid", "e2e tests", "release readiness",
  "hotfix", "rollback", "observability", "qa strategy", "qa audit", "coverage audit".
license: CC BY 4.0
metadata:
  author: cpoisson
  version: "1.0"
---

## Routing

Load the sub-skill that matches the user's intent. Load one at a time unless the request clearly spans two domains.

| Intent | Sub-skill | Load when... |
|--------|-----------|--------------|
| Assess current risks, prioritize QA actions | [risk-analysis.md](risk-analysis.md) | "what are my risks", "where should I start", "prioritize", "what matters most" |
| Design or assess the test pyramid | [test-pyramid.md](test-pyramid.md) | "test pyramid", "test strategy", "unit vs integration vs e2e", "coverage gaps", "CI tests" |
| Design E2E tests, identify critical user flows | [e2e-test-design.md](e2e-test-design.md) | "e2e tests", "user flows", "coverage matrix", "what to automate", "critical paths", "acceptance criteria" |
| Write or audit specifications | [spec-writing.md](spec-writing.md) | "spec", "feature spec", "acceptance criteria", "definition of done", "gap analysis", "ambiguous requirements" |
| Verify agent-generated code, agentic QA | [agentic-coding-qa.md](agentic-coding-qa.md) | "agent verify", "ai code review", "definition of done for agents", "test-as-contract", "coding agent qa" |
| Design or audit testing environments | [test-environments.md](test-environments.md) | "staging", "local environment", "qa environment", "test data", "environment parity", "seed data" |
| Protect production from bad changes | [prod-dev-isolation.md](prod-dev-isolation.md) | "production safety", "deploy gate", "feature flag", "migration safety", "blast radius", "change protection" |
| Handle an outage, roll back, hotfix | [hotfix-rollback.md](hotfix-rollback.md) | "outage", "rollback", "hotfix", "emergency", "production down", "revert", "post-mortem" |
| Plan releases, changelogs, release readiness | [release-train.md](release-train.md) | "release", "changelog", "release checklist", "versioning", "deploy to prod", "release cadence" |
| Logging, error tracking, health checks | [observability.md](observability.md) | "logging", "error tracking", "health check", "alerting", "monitoring", "post-deploy verification" |
| Backup strategy, restore testing, migration safety | [data-safety.md](data-safety.md) | "backup", "restore", "data safety", "migration risk", "schema change", "data integrity" |
| Fix a confirmed bug end-to-end (branch → failing test → fix → PR → CI) | [bug-fix.md](bug-fix.md) | "fix a bug", "bug fix workflow", "there's a bug in", "reproduce the bug", "write a failing test", "fix this issue" |
