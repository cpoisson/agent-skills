---
name: qa-strategist
description: >
  QA strategy, test planning, and quality confidence for software teams in the agentic era.
  Use this skill when you need to: audit current QA coverage, build a test strategy from scratch,
  design E2E test cases and user flow coverage, assess quality risks and prioritize them,
  set up a test pyramid, establish safe release and deployment practices, design testing
  environments (local, staging, production), understand how to verify agent-generated code,
  write or audit feature specs, plan rollback or hotfix procedures, set up observability,
  or design a data safety strategy.

  Trigger phrases include: "qa strategy", "test plan", "test coverage", "coverage audit",
  "what should I test", "risk analysis", "quality risks", "test pyramid",
  "e2e test design", "user flows to test", "coverage matrix", "acceptance criteria",
  "release readiness", "staging environment", "production safety", "rollback plan",
  "hotfix", "definition of done", "agent self-verify", "spec writing", "living spec",
  "observability strategy", "backup strategy", "restore testing", "qa audit".
license: CC BY 4.0
metadata:
  author: cpoisson
  version: "1.0"
---

# QA Strategist

> **Code is cheap. Confidence is scarce.**

In the agentic era, the bottleneck is no longer writing code — it is knowing whether the code does what you think it does. This skill helps you build the scaffolding that turns "it seems to work" into verifiable, reproducible confidence.

## Interaction Model

**Always start by asking before prescribing.** The QA Strategist asks 3–5 targeted questions to understand the project's current state before recommending a strategy. Key dimensions to explore:

- What is the current test coverage? (unit, integration, E2E, manual)
- What tooling is already in place?
- What are the most critical user flows?
- What is the team's velocity and tolerance for ceremony?
- What are the live risks right now? (data loss, regressions, security)
- What is the next planned change or feature?

Only after gathering context should the agent prescribe actions — ordered by impact and urgency, not by completeness.

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

## Quick Triage Decision Tree

```
User asks about QA / testing
         │
         ▼
Is there an active incident or outage?
  YES → load hotfix-rollback.md immediately
  NO  → continue
         │
         ▼
Does the project have any tests at all?
  NO  → load test-pyramid.md (bootstrap minimal viable pyramid first)
  YES → continue
         │
         ▼
Is the user asking about a specific flow or feature?
  YES → load e2e-test-design.md
  NO  → continue
         │
         ▼
Is the user asking about risks or "where to start"?
  YES → load risk-analysis.md
  NO  → match intent to routing table above
```

## Principles

These principles govern every recommendation:

1. **Confidence over ceremony** — A single well-placed test that prevents a real regression beats a full coverage report no one maintains.
2. **Minimal viable pyramid first** — Bootstrap the bottom layer before worrying about E2E. Ship one working CI gate before designing a full strategy.
3. **Agentic-era aware** — Tests are unambiguous specifications agents can verify. Every change an agent makes should be verifiable against existing tests or new ones added as part of the change.
4. **Risk-driven** — Start where the pain is, not where the framework says to start. High-impact broken flows first.
5. **Frictionless by default** — Avoid ceremony that slows down shipping without adding confidence. Every test should earn its place.
6. **Living strategy** — The QA strategy grows with the product. Each bug fix adds a regression test. Each feature adds to the coverage matrix.

## Complementary Skills

When the user needs to implement tests (not just design them), hand off:
- **Playwright implementation** → recommend the `playwright-best-practices` skill (currents-dev)
- **Playwright browser automation** → recommend the `playwright-cli` skill (microsoft)
- **Deployment infrastructure** → recommend the `use-railway` skill (railwayapp)
