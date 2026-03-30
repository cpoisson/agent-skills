# agent-skills

> **Open-source agent skills** — composable, model-agnostic, designed for the agentic era.
>
> Compatible with **GitHub Copilot** (VS Code) and **Claude** (via the `.agents/skills/` convention).

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Philosophy

When generating code becomes easier, the scarce thing is no longer code. **It is confidence.**

Quality scaffolding and good QA practices matter more than ever in the agentic era — not less. Every change an agent makes needs a clear definition of done. Every feature shipped needs behavioral assertions that prove it works. Tests are not bureaucracy; they are unambiguous contracts that agents and humans both can verify.

This repo packages that expertise as installable agent skills and ready-to-use agent templates.

---

## Skill Catalog

| Skill | Description |
|-------|-------------|
| [`qa-strategist`](qa-strategist/) | Comprehensive QA strategy: risk analysis, test pyramid, E2E design, environments, release safety, observability, and more. Designed for the agentic era. |

More skills coming.

---

## Install a Skill

Skills install into your project's `.agents/skills/` directory and are tracked in `skills-lock.json`.

Run the install command for the skill you want, or manually add the entry to `skills-lock.json`:

```json
{
  "version": 1,
  "skills": {
    "qa-strategist": {
      "source": "cpoisson/agent-skills",
      "sourceType": "github"
    }
  }
}
```

Once installed, the skill is automatically available to all agents in your workspace (Copilot, Claude, or any agent that reads `.agents/skills/`).

---

## Use the QA Strategist Agent

The `agents/` directory contains ready-to-use agent definition templates. These are not auto-installed — copy the file into your own project.

**Setup:**

```bash
# 1. Copy the agent template into your project
cp agents/qa-strategist.agent.md /your-project/.github/agents/qa-strategist.agent.md

# 2. Make sure the qa-strategist skill is installed (see above)
```

Then invoke from your agent chat (Copilot, Claude, or equivalent):

> `@qa-strategist assess my current QA coverage`

> `@qa-strategist help me design E2E tests for the auth flow`

> `@qa-strategist what are my biggest quality risks right now?`

The agent starts by asking questions to understand your project's current state before prescribing anything.

---

## What's In Each Skill

### `qa-strategist`

| Sub-skill | Domain |
|-----------|--------|
| [risk-analysis.md](qa-strategist/risk-analysis.md) | Interactive risk matrix, severity × likelihood, maps risks → QA actions |
| [test-pyramid.md](qa-strategist/test-pyramid.md) | Test pyramid layers, bootstrapping strategy, anti-patterns, CI integration |
| [e2e-test-design.md](qa-strategist/e2e-test-design.md) | User flow inventory, critical path selection, coverage matrix, acceptance criteria |
| [spec-writing.md](qa-strategist/spec-writing.md) | Living specs with YAML frontmatter, gap analysis, ambiguity detection |
| [agentic-coding-qa.md](qa-strategist/agentic-coding-qa.md) | Definition of done for AI-generated code, test-as-contract, agent self-verification |
| [test-environments.md](qa-strategist/test-environments.md) | Local / Staging / Prod topology, parity checklist, seed data strategy |
| [prod-dev-isolation.md](qa-strategist/prod-dev-isolation.md) | Deploy gates, feature flags, migration safety, confidence checklist |
| [hotfix-rollback.md](qa-strategist/hotfix-rollback.md) | Emergency playbook, rollback procedures, post-mortem template |
| [release-train.md](qa-strategist/release-train.md) | Release cadence, changelog discipline, readiness checklist |
| [observability.md](qa-strategist/observability.md) | Structured logging, error tracking, health checks, uptime monitoring |
| [data-safety.md](qa-strategist/data-safety.md) | Backup strategy, restore drills, migration safety, data integrity |
| [program-management.md](qa-strategist/program-management.md) | Roadmap hygiene, progress tracking, prioritization, urgent bug triage, feature start go/no-go |

---

## Agent + Skills Architecture

```
                ┌──────────────────────────────┐
                │   qa-strategist.agent.md      │  ← copy to .github/agents/
                │   (orchestrator + persona)    │
                └──────────────┬───────────────┘
                               │ routes to
                ┌──────────────▼───────────────┐
                │   qa-strategist/SKILL.md      │  ← installed skill (router)
                └──────────────┬───────────────┘
                               │ loads
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    risk-analysis.md    test-pyramid.md    e2e-test-design.md
    spec-writing.md     agentic-coding-qa.md        ...
```

The **agent** is opinionated: it has a philosophy, a point of view, and a preferred way of working. It asks questions before prescribing, pushes back when needed, and adapts its output format to the task.

The **skills** are neutral: they are procedure-oriented reference documents — routing tables, checklists, decision trees, and playbooks. No personality, no framing. They load cleanly into any agent, including ones with a different persona.

You can use the skills without the agent, or wire the agent to your own persona.

---

## Contributing

Contributions welcome. Each skill should:
- Address a single, well-defined QA domain
- Stay under 500 lines
- Be platform-agnostic (no tool-specific assumptions)
- Include concrete templates, checklists, or decision trees — not just prose

Open an issue to propose a new skill before building it.

---

## License

[CC BY 4.0](LICENSE) — free to use, share, and adapt with attribution.
