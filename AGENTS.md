# Agent Skills Repository

This repository publishes assistant-portable skill content.

## Purpose

- Treat the markdown files in `qa-strategist/` as the source of truth for QA, release-safety, and bug-fix workflows.
- Use [`qa-strategist/SKILL.md`](qa-strategist/SKILL.md) as the router. Match the user's prompt to a single sub-skill unless the request clearly spans two domains.
- Prefer assistant-neutral language in reusable skill files. Keep tool names and platform-specific conventions in adapter files such as this one, not in the core skill docs.

## Repository Model

- `qa-strategist/SKILL.md` is the router and trigger surface.
- The other markdown files in `qa-strategist/` are routed sub-skills.
- `AGENTS.md`, `CLAUDE.md`, `.claude/agents/`, and `.github/copilot-instructions.md` are adapter layers for specific assistants.
- `evals/` stores routing fixtures and quality thresholds.
- `scripts/skill_critic.py` is the local and CI validation entrypoint.

## Self-Hosting Rule

- This repository should use its own `qa-strategist` skill to improve itself.
- Changes to evals, CI quality gates, test strategy, release discipline, bug-fix workflow, observability, or roadmap hygiene should route through the relevant `qa-strategist` sub-skill first.
- When changing the critic, thresholds, changelog discipline, or merge gates, prefer the `program-management.md`, `test-pyramid.md`, `agentic-coding-qa.md`, `release-train.md`, and `bug-fix.md` procedures as the operating model for the repository itself.
- If a proposed repo change contradicts an existing `qa-strategist` recommendation, either update the skill intentionally or explain why this repository is making an exception.

## Authoring Rules

- Keep shared skill content assistant-agnostic.
- Do not mention platform-specific tool names such as `ask_user`, `read`, `search`, `edit`, `shell`, or equivalent in shared skill markdown.
- Put assistant-specific invocation hints, memory, or client conventions in adapter files only.
- Optimize `description` fields for recall. Include realistic user phrases, especially the phrasing people actually use in tickets, issues, and coding-assistant chat.
- Keep `SKILL.md` focused on routing and navigation. Put detailed procedures in routed sub-skill files.
- Prefer one routed sub-skill per request. If a request spans two domains, keep the combination explicit and intentional.

## Routing Hints

- Requests about tests, QA, coverage, release readiness, observability, migration safety, or rollback should route to `qa-strategist`.
- Requests like "fix GitHub issue", "fix this ticket", "reproduce the bug", "write a failing test", or "open a PR for this regression" should route to `qa-strategist/bug-fix.md`.
- Requests like "prioritize issues", "what should we work on next sprint", or "urgent bug triage" should route to `qa-strategist/program-management.md`.

## Portability Rules

- Keep the portable workflow in the shared markdown.
- Put assistant-specific entrypoints in `AGENTS.md`, `CLAUDE.md`, `.claude/agents/`, and `.github/copilot-instructions.md`.
- When adding support for a new assistant, add an adapter file instead of forking the shared skill content.
- Shared procedures should still read correctly if copied into another assistant ecosystem with no tool translation.

## Evaluation And CI

- Run the critic before merging changes that touch skill metadata, routing, or adapter files:

```bash
./scripts/skill_critic.py --thresholds-file evals/skill_critic_thresholds.json --markdown-out EVALUATIONS.md
```

- The quality gate currently checks:
  - score thresholds for description, routing recall, portability, and total quality
  - load budget for the single-route path
  - load budget for the two-route path
- Update `evals/skill_critic_cases.json` whenever a real-world prompt reveals a recall miss.
- Update `evals/skill_critic_thresholds.json` only when intentionally changing the quality bar.
- Keep `EVALUATIONS.md` refreshed when the critic behavior or thresholds change.

## Load Budget Guidance

- Design for normal loading behavior, not full-directory ingestion.
- Budget for `description + SKILL.md + one routed file` as the standard path.
- Budget for `description + SKILL.md + two routed files` as the exceptional but acceptable path.
- Treat loading the entire skill directory as a failure mode or client limitation, not as the desired operating model.

## Change Process

- If you add or rename a routed sub-skill, update `qa-strategist/SKILL.md`, relevant adapter files, eval cases, and the changelog in the same change.
- If you change trigger phrasing, add or update at least one eval case that proves the intended routing behavior.
- If you change portability behavior, update the adapter files and confirm the portability score still passes.
- Record notable repository changes in `CHANGELOG.md` under `Unreleased`.
- For repository-process changes, update the relevant `qa-strategist` content first or in the same change so the repository continues to eat its own food.

## Definition Of Done

- The affected skill content is assistant-neutral unless the file is an explicit adapter.
- Routing changes are covered by eval cases.
- `./scripts/skill_critic.py --thresholds-file evals/skill_critic_thresholds.json --markdown-out EVALUATIONS.md` passes.
- `EVALUATIONS.md` reflects the current thresholds and measurements.
- `CHANGELOG.md` includes a concise note for the user-visible change.
