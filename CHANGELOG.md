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
- Negative-control and guided eval cases for `qa-strategist`
- A repository `ROADMAP.md` with QA-backed skill improvement and new-skill priorities

### Changed

- Removed the project-tracker status update requirement from `qa-strategist/bug-fix.md` so the bug-fix workflow no longer tells users to mark tickets In Progress
- Expanded `AGENTS.md` into a project-specific coding-agent playbook covering authoring rules, portability rules, evaluation procedure, load-budget guidance, and definition of done
- Added a self-hosting rule so repository process changes are expected to use `qa-strategist` guidance on the repository itself
- Centralized the repository branch naming convention in `AGENTS.md`, reusing the existing `feat/*`, `fix/*`, and `hotfix/*` patterns already defined in the QA workflow docs
- Expanded routing eval coverage so every routed `qa-strategist` sub-skill has semantic prompt variations
- Split CI into separate deterministic and semantic jobs, and switched the semantic job to Ollama with `qwen2.5:1.5b` as the default fast backend
- Expanded `qa-strategist` trigger metadata to better match GitHub issue fixes, ticket-driven bug work, bootstrap-testing prompts, and issue-prioritization requests
- Removed assistant-specific tool names from `qa-strategist/bug-fix.md` so the shared skill content stays portable across assistants
- Reworked `README.md` to position `qa-strategist` as a QA-confidence skill for bug fixes and feature shipping, switched the quick install to `npx skills add cpoisson/agent-skills`, advertised tests more explicitly, and added collapsible agent-specific setup notes
- Added explicit evaluation metrics and quality-gate thresholds to `README.md`, including the deterministic critic, semantic routing accuracy target, and commands to run both checks
- Rebalanced `ROADMAP.md` toward first-run adoption, expected-behavior clarity, and confidence-oriented documentation
- Expanded the deterministic critic and semantic judge from route-only evaluation into trigger-plus-routing evaluation with negative controls, ambiguity coverage, and richer failure reporting
- Updated `qa-strategist/agentic-coding-qa.md` to emphasize reliability, evidence-before-exit, and efficiency as first-class QA signals for agent-written code
- Stopped ignoring `ROADMAP.md` so repository planning and skill-priority decisions can be versioned with the rest of the QA process
- Switched docs and CI examples to `python3 scripts/...` invocation for better portability across environments that do not allow direct script execution
- Added a short related-work section to `README.md` linking the most relevant recent papers and talks on skill benchmarking, agent reliability, and agentic evaluation
- Added the spec-driven development paper to `README.md` related work to better ground the repo's emphasis on acceptance criteria and testable contracts
- Rewrote the `README.md` related-work descriptions around the concrete takeaway each reference offers for this repo
- Simplified `README.md` related work into short abstract-style paper summaries focused on the most relevant research references
