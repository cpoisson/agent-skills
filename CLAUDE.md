# Claude Project Memory

Use the QA strategist materials in this repository as reusable workflows, not as Claude-only prompts.

## Where To Look

- Router: [`qa-strategist/SKILL.md`](qa-strategist/SKILL.md)
- Sub-skills: the topic files in [`qa-strategist/`](qa-strategist)
- Claude adapter: [`.claude/agents/qa-strategist.md`](.claude/agents/qa-strategist.md)

## Usage

- Route testing, QA, release-safety, observability, incident-response, and bug-fix requests through `qa-strategist`.
- For issue-fix prompts, prefer `bug-fix.md` when the user is asking to reproduce a defect, add a failing test, implement a minimal fix, and open a PR.
- For planning prompts about issue prioritization or sprint sequencing, prefer `program-management.md`.
- When improving this repository itself, use `qa-strategist` as the default operating framework rather than treating the repo as an exception.

## Authoring Rule

Keep shared skill markdown assistant-neutral. Put Claude-specific memory and invocation guidance in `.claude/`.
