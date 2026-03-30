---
name: qa-strategist
description: >
  QA strategy and quality confidence routing for software teams in the agentic era. Use this skill
  whenever the user mentions testing, QA, coverage, specs, release safety, observability, data
  safety, bug triage, GitHub issues, tickets, regressions, roadmap hygiene, or failing tests —
  even if they don't say "QA" explicitly. Trigger phrases: "test plan", "test coverage",
  "what should I test", "risk analysis", "test pyramid", "bootstrap tests", "e2e tests",
  "release readiness", "hotfix", "rollback", "observability", "qa strategy", "qa audit",
  "coverage audit", "fix GitHub issue", "fix this ticket", "write a failing test",
  "prioritize issues", "urgent bug queue".
license: CC BY 4.0
metadata:
  author: cpoisson
  version: "1.1"
---

## Routing

Load the sub-skill that matches the user's intent. Load one at a time unless the request clearly spans two domains.

| Intent | Sub-skill | Load when... |
|--------|-----------|--------------|
| Assess current risks, prioritize QA actions | [risk-analysis.md](risk-analysis.md) | "what are my risks", "where should I start with QA", "quality risks", "risk register", "highest confidence payoff", "what matters most from a QA perspective" |
| Design or assess the test pyramid | [test-pyramid.md](test-pyramid.md) | "test pyramid", "test strategy", "no tests", "bootstrap tests", "zero automated tests", "unit vs integration vs e2e", "unit integration e2e coverage", "coverage gaps", "CI tests" |
| Design E2E tests, identify critical user flows | [e2e-test-design.md](e2e-test-design.md) | "e2e tests", "user flows", "coverage matrix", "what to automate", "critical paths", "acceptance criteria" |
| Write or audit specifications | [spec-writing.md](spec-writing.md) | "spec", "feature spec", "acceptance criteria", "definition of done", "gap analysis", "ambiguous requirements" |
| Verify agent-generated code, agentic QA | [agentic-coding-qa.md](agentic-coding-qa.md) | "agent verify", "ai code review", "review ai-generated change", "evidence of done", "don't trust the diff", "verify agent output", "definition of done for agents", "test-as-contract", "coding agent qa" |
| Design or audit testing environments | [test-environments.md](test-environments.md) | "staging", "local environment", "qa environment", "test data", "environment parity", "seed data" |
| Protect production from bad changes | [prod-dev-isolation.md](prod-dev-isolation.md) | "production safety", "deploy gate", "feature flag", "migration safety", "blast radius", "change protection" |
| Handle an outage, roll back, hotfix | [hotfix-rollback.md](hotfix-rollback.md) | "outage", "rollback", "hotfix", "emergency", "production down", "revert", "post-mortem" |
| Plan releases, changelogs, release readiness | [release-train.md](release-train.md) | "release", "changelog", "release checklist", "versioning", "deploy to prod", "release cadence" |
| Logging, error tracking, health checks | [observability.md](observability.md) | "logging", "error tracking", "health check", "alerting", "monitoring", "instrument errors", "production monitoring", "post-deploy verification" |
| Backup strategy, restore testing, migration safety | [data-safety.md](data-safety.md) | "backup", "restore", "data safety", "migration risk", "schema change", "data integrity" |
| Fix a confirmed bug end-to-end (branch → failing test → fix → PR → CI) | [bug-fix.md](bug-fix.md) | "fix a bug", "bug fix workflow", "there's a bug in", "reproduce the bug", "write a failing test", "fix this issue", "fix GitHub issue", "fix this ticket", "regression", "open a PR", "ticket-driven fix" |
| Program roadmap updates, next-work prioritization, urgent bug triage, feature start go/no-go | [program-management.md](program-management.md) | "roadmap", "program management", "what should we work on next", "urgent bug", "can I start feature", "prioritization", "program status", "open issues", "prioritize issues", "next sprint", "urgent bug queue" |
