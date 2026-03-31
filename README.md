# agent-skills

> Installable QA skills for teams that want more confidence when shipping bug fixes and features.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

`qa-strategist` gives your coding agent the behavior of a strong QA analyst: clarify expected behavior, identify the highest-risk paths, and turn that into concrete tests, release checks, and safer rollout decisions.

It is built for teams that do not just want advice. They want stronger evidence before shipping.

## Who This Is For

- Teams shipping bug fixes or features without enough QA confidence
- Developers who want clear, actionable guidance instead of generic testing advice
- Projects that need a portable skill they can install quickly and use across agents

## What Confidence Looks Like

When you use `qa-strategist`, you should expect it to:

- ask a few targeted questions before recommending a large plan
- focus on the user flows most likely to break or hurt
- turn expected behavior into concrete tests, checks, and rollout safeguards
- push bug-fix work toward reproduction, a failing test, a minimal fix, and verification
- give a clear go/no-go view when you ask about feature or release readiness

## Why Tests Matter Here

This skill treats tests as the strongest confidence signal available when shipping software:

- tests make expected behavior explicit
- tests turn bug fixes into verified regressions that stay fixed
- tests give coding agents and humans the same definition of done
- tests reduce "it looks fine" decisions before release

## Quick Install

Fastest path:

```bash
npx skills add cpoisson/agent-skills
```

If you do not want to use the installer, copy [`qa-strategist/`](qa-strategist/) into `.agents/skills/qa-strategist/`.

## Start Using It

Example prompts:

- `Assess the main QA risks in this repo`
- `What should we test before shipping this bug fix?`
- `Help me reproduce this bug and write the first failing test`
- `Turn this acceptance criteria into a test plan`
- `Can we start this feature, or are we missing too much?`
- `What are the biggest release risks right now?`

## Skill Catalog

| Skill | Description |
|-------|-------------|
| [`qa-strategist`](qa-strategist/) | QA strategy and shipping confidence for bug fixes and features: risk analysis, test planning, stronger regression coverage, release readiness, observability, rollback, and roadmap hygiene. |

## What Is Included

| Sub-skill | Outcome |
|-----------|---------|
| [risk-analysis.md](qa-strategist/risk-analysis.md) | Find the highest-confidence QA work first |
| [test-pyramid.md](qa-strategist/test-pyramid.md) | Build or audit the right unit, integration, and E2E mix |
| [e2e-test-design.md](qa-strategist/e2e-test-design.md) | Identify critical user flows and turn them into test coverage |
| [spec-writing.md](qa-strategist/spec-writing.md) | Clarify expected behavior and acceptance criteria |
| [agentic-coding-qa.md](qa-strategist/agentic-coding-qa.md) | Verify AI-generated changes with real evidence |
| [test-environments.md](qa-strategist/test-environments.md) | Improve environment parity and test-data safety |
| [prod-dev-isolation.md](qa-strategist/prod-dev-isolation.md) | Reduce blast radius with safer release controls |
| [hotfix-rollback.md](qa-strategist/hotfix-rollback.md) | Respond to incidents with a controlled rollback path |
| [release-train.md](qa-strategist/release-train.md) | Run a release with explicit readiness checks |
| [observability.md](qa-strategist/observability.md) | Add the signals needed to trust production behavior |
| [data-safety.md](qa-strategist/data-safety.md) | Protect migrations, restores, and data integrity |
| [bug-fix.md](qa-strategist/bug-fix.md) | Drive a bug fix from reproduction to verified completion |
| [program-management.md](qa-strategist/program-management.md) | Keep roadmap, priorities, and feature starts quality-aware |

## Evaluation Metrics

This repository keeps the skill measurable with a deterministic critic and a semantic trigger-plus-routing judge.

- Deterministic quality gate:
  - total quality score at least `90`
  - overall trigger and routing score at least `90`
  - portability score at least `90`
  - description score at least `85`
  - at least `2` eval cases per routed sub-skill
  - single-route load budget at most `2400` words
  - two-route load budget at most `3600` words
- Semantic routing gate:
  - minimum overall trigger and routing accuracy `0.85`

The eval suite now includes:

- positive route-selection cases
- guided and ambiguous prompts
- negative controls that should not trigger the skill
- reporting split across trigger accuracy, triggered-route accuracy, and overall accuracy

Run the checks with:

```bash
python3 scripts/skill_critic.py --thresholds-file evals/skill_critic_thresholds.json --markdown-out EVALUATIONS.md
python3 scripts/semantic_skill_judge.py --provider ollama --model qwen2.5:1.5b --thresholds-file evals/semantic_judge_thresholds.json --markdown-out /tmp/semantic-judge.md
```

The latest deterministic report is published in [EVALUATIONS.md](EVALUATIONS.md).

## Agent And Skill Model

The shared skill files are portable and procedure-focused. The optional agent files add a stronger persona and working style on top.

- Use the skill alone when you want lightweight routing and reusable QA workflows
- Use the agent template when you want a more opinionated QA strategist persona

## Contributing

Each skill should:

- address one clear QA domain
- stay assistant-neutral
- include templates, checklists, decision trees, or test-oriented artifacts
- stay concise enough to load cheaply

Open an issue before adding a new skill.

## Agent-Specific Notes

<details>
<summary>Codex</summary>

- Install the shared skill into `.agents/skills/qa-strategist/`
- Codex-specific repository guidance belongs in your project-level `AGENTS.md`
- Use the shared skill for routing and keep Codex behavior hints in the adapter layer

</details>

<details>
<summary>Claude</summary>

- Install the shared skill into `.agents/skills/qa-strategist/`
- If you want a Claude-specific agent entrypoint, copy [`.claude/agents/qa-strategist.md`](.claude/agents/qa-strategist.md) into your project
- Start with direct prompts such as `what should we test before shipping this fix?`

</details>

<details>
<summary>GitHub Copilot</summary>

- Install the shared skill into `.agents/skills/qa-strategist/`
- Add repo-level Copilot guidance with [`.github/copilot-instructions.md`](.github/copilot-instructions.md) if you want this repo's adapter behavior
- If you want a stronger persona, also copy [`agents/qa-strategist.agent.md`](agents/qa-strategist.agent.md) into your project

</details>

## Related Work

This project sits in the same emerging space as recent work on agent reliability, skill evaluation, and agentic QA:

- [SkillsBench: Benchmarking Agent Skills](https://arxiv.org/abs/2602.12670): Benchmarks whether curated and self-generated skills actually help agent performance across domains, models, and task types.
- [Towards a Science of AI Agent Reliability](https://arxiv.org/abs/2602.16666): Proposes reliability as a separate evaluation axis from raw accuracy, organized around consistency, robustness, predictability, and safety.
- [Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](https://arxiv.org/abs/2602.00180): Argues that AI-assisted software work should begin from explicit contracts, specs, and acceptance criteria rather than informal intent alone.
- [Upskill: Generate and Evaluate Agent Skills](https://huggingface.co/blog/upskill): Describes generating skills from agent traces and evaluating them for both task quality and token efficiency.
- [How to Evaluate and Test Agent Skills](https://www.youtube.com/watch?v=XUzUf_HCgvk): Walks through a practical skill-eval loop built around trigger tests, rubrics, and judge-based automation.
- [Agentic Evaluations Workshop](https://www.youtube.com/watch?v=UxMZfbWI3LY): Surveys broader agent-eval concerns including transparency, environment-based testing, robustness, and governance.

## License

[CC BY 4.0](LICENSE) - free to use, share, and adapt with attribution.
