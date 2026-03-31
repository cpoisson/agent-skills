# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Assistant adapter files for Codex/OpenAI, Claude, and GitHub Copilot via `AGENTS.md`, `CLAUDE.md`, `.claude/agents/qa-strategist.md`, and `.github/copilot-instructions.md`
- A local skill critic executable in `scripts/skill_critic.py`
- Routing eval cases in `evals/skill_critic_cases.json`
- Threshold-based quality gates in `evals/skill_critic_thresholds.json`
- A provider-swappable semantic judge in `scripts/semantic_skill_judge.py` for `openai`, `ollama`, `llamacpp`, and `huggingface`
- Semantic judge thresholds in `evals/semantic_judge_thresholds.json`
- CI enforcement in `.github/workflows/skill-critic.yml`
- A generated evaluation report in `EVALUATIONS.md`
- Load-budget checks for single-route and two-route skill loading paths

### Changed

- Expanded `AGENTS.md` into a project-specific coding-agent playbook covering authoring rules, portability rules, evaluation procedure, load-budget guidance, and definition of done
- Added a self-hosting rule so repository process changes are expected to use `qa-strategist` guidance on the repository itself
- Centralized the repository branch naming convention in `AGENTS.md`, reusing the existing `feat/*`, `fix/*`, and `hotfix/*` patterns already defined in the QA workflow docs
- Expanded routing eval coverage so every routed `qa-strategist` sub-skill has semantic prompt variations
- Split CI into separate deterministic and semantic jobs, and switched the semantic job to Ollama with `qwen2.5:1.5b` as the default fast backend
- Expanded `qa-strategist` trigger metadata to better match GitHub issue fixes, ticket-driven bug work, bootstrap-testing prompts, and issue-prioritization requests
- Removed assistant-specific tool names from `qa-strategist/bug-fix.md` so the shared skill content stays portable across assistants
- Reworked `README.md` to position `qa-strategist` as a QA-confidence skill for bug fixes and feature shipping, switched the quick install to `npx skills add cpoisson/agent-skills`, advertised tests more explicitly, and added collapsible agent-specific setup notes
- Rebalanced `ROADMAP.md` toward first-run adoption, expected-behavior clarity, and confidence-oriented documentation
