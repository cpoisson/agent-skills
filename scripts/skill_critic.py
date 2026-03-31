#!/usr/bin/env python3
"""Local scorecard for skill discoverability, trigger quality, portability, and routing recall."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_CASES_PATH = REPO_ROOT / "evals" / "skill_critic_cases.json"
TOOL_LEAK_PATTERNS = (
    r"`ask_user`",
    r"`read`",
    r"`search`",
    r"`edit`",
    r"`shell`",
    r"`web_search`",
    r"`web_fetch`",
    r"`task`",
    r"`skill`",
)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "help",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "now",
    "of",
    "on",
    "or",
    "our",
    "should",
    "the",
    "this",
    "to",
    "we",
    "what",
    "when",
    "with",
    "you",
}


@dataclass
class SkillRoute:
    intent: str
    file_name: str
    load_when: str
    source_path: Path

    @property
    def slug(self) -> str:
        return self.source_path.stem


@dataclass
class Thresholds:
    min_total: float | None = None
    min_routing: float | None = None
    min_portability: float | None = None
    min_description: float | None = None
    min_cases_per_route: int | None = None
    max_single_route_load_words: int | None = None
    max_two_route_load_words: int | None = None
    strict_findings: bool = False


@dataclass
class EvalCase:
    case_id: str
    prompt: str
    should_trigger: bool
    expected_route: str | None
    reason: str
    category: str
    variation: str


@dataclass
class EvalResult:
    case_id: str
    prompt: str
    category: str
    variation: str
    expected_trigger: bool
    predicted_trigger: bool
    expected_route: str | None
    predicted_route: str
    passed: bool
    trigger_score: float
    matched_phrases: list[str]
    shared_tokens: list[str]
    ranking: list[tuple[str, float]]
    failure_mode: str


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in STOPWORDS and len(token) > 1
    ]


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def discover_skill_roots() -> list[Path]:
    roots = []
    for skill_path in REPO_ROOT.glob("*/SKILL.md"):
        if skill_path.parts[0].startswith("."):
            continue
        roots.append(skill_path.parent)
    return sorted(roots)


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = read_text(skill_md)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    result: dict[str, str] = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("name:"):
            result["name"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("description:"):
            raw = line.split(":", 1)[1].strip()
            if raw in {">", "|"}:
                i += 1
                chunks = []
                while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                    chunks.append(lines[i].strip())
                    i += 1
                result["description"] = " ".join(chunk for chunk in chunks if chunk)
                continue
            result["description"] = raw.strip('"')
        i += 1
    return result


def parse_routes(skill_md: Path) -> list[SkillRoute]:
    routes: list[SkillRoute] = []
    for line in read_text(skill_md).splitlines():
        if not line.startswith("|") or ".md]" not in line:
            continue
        cols = [col.strip() for col in line.strip("|").split("|")]
        if len(cols) < 3 or cols[0] == "Intent":
            continue
        file_match = re.search(r"\[([^\]]+\.md)\]\(([^)]+)\)", cols[1])
        if not file_match:
            continue
        link_target = file_match.group(2)
        source_path = (skill_md.parent / link_target).resolve()
        routes.append(
            SkillRoute(
                intent=cols[0],
                file_name=file_match.group(1),
                load_when=cols[2],
                source_path=source_path,
            )
        )
    return routes


def load_eval_cases(path: Path = EVAL_CASES_PATH) -> list[EvalCase]:
    raw_cases = json.loads(read_text(path))
    cases: list[EvalCase] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        expected_route_raw = raw_case.get("expected_route", raw_case.get("expected"))
        should_trigger = bool(raw_case.get("should_trigger", expected_route_raw not in {None, ""}))
        expected_route = str(expected_route_raw).strip() if expected_route_raw not in {None, ""} else None
        cases.append(
            EvalCase(
                case_id=str(raw_case.get("id", f"case-{index:03d}")),
                prompt=str(raw_case["prompt"]),
                should_trigger=should_trigger,
                expected_route=expected_route,
                reason=str(raw_case.get("reason", "")).strip(),
                category=str(raw_case.get("category", "positive")).strip() or "positive",
                variation=str(raw_case.get("variation", "direct")).strip() or "direct",
            )
        )
    return cases


def score_description(description: str) -> tuple[float, list[str]]:
    findings: list[str] = []
    words = tokenize(description)
    score = 100.0
    if not description:
        return 0.0, ["Missing description in frontmatter."]
    word_count = len(words)
    if word_count < 18:
        score -= 30
        findings.append(f"Description is thin ({word_count} content words).")
    elif word_count > 80:
        score -= 10
        findings.append(f"Description is long ({word_count} content words) and may dilute triggering.")
    trigger_phrases = len(re.findall(r'"[^"]+"', description))
    if trigger_phrases < 4:
        score -= 20
        findings.append(f"Description exposes few trigger phrases ({trigger_phrases}).")
    if "github" not in description.lower() and "issue" not in description.lower():
        score -= 10
        findings.append("Description never mentions GitHub issues or tickets.")
    return clamp(score), findings


def score_structure(skill_root: Path, routes: list[SkillRoute]) -> tuple[float, list[str]]:
    findings: list[str] = []
    score = 100.0
    skill_md = skill_root / "SKILL.md"
    line_count = len(read_text(skill_md).splitlines())
    if line_count > 500:
        score -= 25
        findings.append(f"SKILL.md is over the 500-line target ({line_count} lines).")
    elif line_count > 350:
        score -= 10
        findings.append(f"SKILL.md is getting large ({line_count} lines).")
    subskills = [path for path in skill_root.glob("*.md") if path.name != "SKILL.md"]
    if not routes:
        score -= 35
        findings.append("No routing table rows were parsed from SKILL.md.")
    if routes and len(routes) != len(subskills):
        score -= 15
        findings.append(
            f"Routing table covers {len(routes)} markdown targets but skill folder has {len(subskills)} sub-skill files."
        )
    broken_links = [route.file_name for route in routes if not route.source_path.exists()]
    if broken_links:
        score -= 30
        findings.append(f"Routing references missing files: {', '.join(sorted(broken_links))}.")
    return clamp(score), findings


def score_portability(skill_root: Path, routes: list[SkillRoute]) -> tuple[float, list[str]]:
    findings: list[str] = []
    score = 100.0
    portability_targets = {
        "AGENTS.md": REPO_ROOT / "AGENTS.md",
        "CLAUDE.md": REPO_ROOT / "CLAUDE.md",
        ".github/copilot-instructions.md": REPO_ROOT / ".github" / "copilot-instructions.md",
        f".claude/agents/{skill_root.name}.md": REPO_ROOT / ".claude" / "agents" / f"{skill_root.name}.md",
    }
    missing = [name for name, path in portability_targets.items() if not path.exists()]
    if missing:
        score -= 15 * len(missing)
        findings.append("Missing assistant adapter files: " + ", ".join(missing) + ".")
    tool_leaks = []
    for route in routes:
        text = read_text(route.source_path)
        for pattern in TOOL_LEAK_PATTERNS:
            for match in re.findall(pattern, text):
                tool_leaks.append(f"{route.source_path.relative_to(REPO_ROOT)}: {match}")
    if tool_leaks:
        score -= min(40, len(tool_leaks) * 10)
        findings.append("Assistant-specific tool leakage in skill docs: " + "; ".join(tool_leaks) + ".")
    return clamp(score), findings


def iter_trigger_phrases(description: str, routes: list[SkillRoute]) -> list[str]:
    phrases = [phrase.strip().strip('"') for phrase in re.findall(r'"[^"]+"', description)]
    for route in routes:
        phrases.extend(part.strip().strip('"') for part in route.load_when.split(","))
        phrases.append(route.slug)
        phrases.append(route.slug.replace("-", " "))
    deduped: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        normalized = phrase.lower().strip()
        if len(normalized) < 3 or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def build_trigger_surface(description: str, routes: list[SkillRoute]) -> Counter[str]:
    surface_parts = [description]
    for route in routes:
        surface_parts.extend([route.intent, route.load_when, route.slug.replace("-", " ")])
    return Counter(tokenize(" ".join(surface_parts)))


def score_trigger(prompt: str, description: str, routes: list[SkillRoute]) -> tuple[bool, float, list[str], list[str]]:
    prompt_lower = prompt.lower()
    prompt_tokens = Counter(tokenize(prompt))
    surface_tokens = build_trigger_surface(description, routes)
    token_score = float(sum(prompt_tokens[token] * surface_tokens[token] for token in prompt_tokens))
    matched_phrases = [phrase for phrase in iter_trigger_phrases(description, routes) if phrase in prompt_lower]
    shared_tokens = sorted(token for token in prompt_tokens if surface_tokens[token] > 0)
    total_score = token_score + 6.0 * len(matched_phrases)
    should_trigger = bool(matched_phrases) or len(shared_tokens) >= 2 or total_score >= 6.0
    return should_trigger, total_score, matched_phrases[:8], shared_tokens[:8]


def route_prompt(prompt: str, description: str, routes: list[SkillRoute]) -> tuple[str, list[tuple[str, float]]]:
    prompt_lower = prompt.lower()
    prompt_tokens = Counter(tokenize(prompt))
    route_scores: list[tuple[str, float]] = []
    for route in routes:
        route_text = " ".join(
            [
                description,
                route.intent,
                route.load_when,
                route.slug.replace("-", " "),
                read_text(route.source_path).split("\n", 3)[0],
            ]
        ).lower()
        route_tokens = Counter(tokenize(route_text))
        token_score = sum(prompt_tokens[token] * route_tokens[token] for token in prompt_tokens)
        phrase_score = 0.0
        for phrase in [item.strip().strip('"') for item in route.load_when.split(",")]:
            normalized = phrase.lower()
            if normalized and normalized in prompt_lower:
                phrase_score += 8.0
        if route.slug in prompt_lower:
            phrase_score += 4.0
        if route.slug.replace("-", " ") in prompt_lower:
            phrase_score += 4.0
        route_scores.append((route.slug, token_score + phrase_score))
    route_scores.sort(key=lambda item: (-item[1], item[0]))
    return route_scores[0][0], route_scores


def classify_failure_mode(
    case: EvalCase,
    predicted_trigger: bool,
    predicted_route: str,
) -> str:
    if case.should_trigger and not predicted_trigger:
        return "false_negative"
    if not case.should_trigger and predicted_trigger:
        return "false_positive"
    if not case.should_trigger:
        return "pass"
    if predicted_route != (case.expected_route or ""):
        return "ambiguity_misroute" if case.category == "ambiguous" else "wrong_route"
    return "pass"


def evaluate_routing(
    description: str,
    routes: list[SkillRoute],
    cases: list[EvalCase],
) -> tuple[float, float, float, list[str], list[dict[str, object]]]:
    findings: list[str] = []
    if not routes:
        return 0.0, 0.0, 0.0, ["Cannot run routing evals without parsed routes."], []

    results: list[EvalResult] = []
    trigger_passes = 0
    route_passes = 0
    overall_passes = 0
    predicted_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()

    routed_cases = [case for case in cases if case.should_trigger]
    for case in cases:
        predicted_trigger, trigger_score, matched_phrases, shared_tokens = score_trigger(case.prompt, description, routes)
        predicted_route = ""
        ranking: list[tuple[str, float]] = []
        if predicted_trigger:
            predicted_route, ranking = route_prompt(case.prompt, description, routes)
            predicted_counts[predicted_route] += 1

        trigger_ok = predicted_trigger == case.should_trigger
        route_ok = case.should_trigger and predicted_trigger and predicted_route == (case.expected_route or "")
        passed = trigger_ok and (route_ok if case.should_trigger else True)
        failure_mode = classify_failure_mode(case, predicted_trigger, predicted_route)
        trigger_passes += int(trigger_ok)
        if case.should_trigger:
            route_passes += int(route_ok)
        overall_passes += int(passed)
        failure_counts[failure_mode] += 1
        results.append(
            EvalResult(
                case_id=case.case_id,
                prompt=case.prompt,
                category=case.category,
                variation=case.variation,
                expected_trigger=case.should_trigger,
                predicted_trigger=predicted_trigger,
                expected_route=case.expected_route,
                predicted_route=predicted_route,
                passed=passed,
                trigger_score=trigger_score,
                matched_phrases=matched_phrases,
                shared_tokens=shared_tokens,
                ranking=ranking[:3],
                failure_mode=failure_mode,
            )
        )

    trigger_accuracy = 100.0 * trigger_passes / len(cases) if cases else 0.0
    route_accuracy = 100.0 * route_passes / len(routed_cases) if routed_cases else 0.0
    overall_accuracy = 100.0 * overall_passes / len(cases) if cases else 0.0

    if trigger_accuracy < 80:
        findings.append(f"Trigger eval accuracy is {trigger_accuracy:.1f}%.")
    if route_accuracy < 80:
        findings.append(f"Triggered-route eval accuracy is {route_accuracy:.1f}%.")
    skewed = [slug for slug, count in predicted_counts.items() if count >= max(4, len(routed_cases) // 2 or 1)]
    if skewed:
        findings.append("Routing is overly biased toward: " + ", ".join(sorted(skewed)) + ".")
    failed_prompts = [result for result in results if not result.passed]
    if failed_prompts:
        samples = ", ".join(
            f'"{item.prompt}" -> {item.failure_mode}' for item in failed_prompts[:3]
        )
        findings.append("Representative eval misses: " + samples + ".")
    dominant_failures = [mode for mode, count in failure_counts.items() if mode != "pass" and count >= 2]
    if dominant_failures:
        findings.append("Repeated failure modes: " + ", ".join(sorted(dominant_failures)) + ".")

    return (
        overall_accuracy,
        trigger_accuracy,
        route_accuracy,
        findings,
        [
            {
                "id": result.case_id,
                "prompt": result.prompt,
                "category": result.category,
                "variation": result.variation,
                "expected_trigger": result.expected_trigger,
                "predicted_trigger": result.predicted_trigger,
                "expected_route": result.expected_route,
                "predicted_route": result.predicted_route,
                "passed": result.passed,
                "failure_mode": result.failure_mode,
                "trigger_score": round(result.trigger_score, 2),
                "matched_phrases": result.matched_phrases,
                "shared_tokens": result.shared_tokens,
                "ranking": result.ranking,
            }
            for result in results
        ],
    )


def format_findings(prefix: str, findings: Iterable[str]) -> list[str]:
    return [f"{prefix}: {finding}" for finding in findings]


def route_word_metrics(description: str, skill_md_text: str, routes: list[SkillRoute]) -> dict[str, object]:
    description_words = count_words(description)
    skill_md_words = count_words(skill_md_text)
    route_word_counts = [
        {
            "slug": route.slug,
            "words": count_words(read_text(route.source_path)),
        }
        for route in routes
    ]
    route_word_counts.sort(key=lambda item: (-item["words"], item["slug"]))
    return {
        "route_word_counts": route_word_counts,
        "max_single_route_load_words": description_words
        + skill_md_words
        + sum(item["words"] for item in route_word_counts[:1]),
        "max_two_route_load_words": description_words
        + skill_md_words
        + sum(item["words"] for item in route_word_counts[:2]),
    }


def case_coverage_metrics(cases: list[EvalCase], routes: list[SkillRoute]) -> dict[str, object]:
    route_counts = Counter(case.expected_route for case in cases if case.expected_route)
    route_slugs = [route.slug for route in routes]
    category_counts = Counter(case.category for case in cases)
    variation_counts = Counter(case.variation for case in cases)
    return {
        "route_case_counts": [{"slug": slug, "count": route_counts.get(slug, 0)} for slug in sorted(route_slugs)],
        "routes_without_cases": [slug for slug in sorted(route_slugs) if route_counts.get(slug, 0) == 0],
        "category_counts": [{"name": name, "count": count} for name, count in sorted(category_counts.items())],
        "variation_counts": [{"name": name, "count": count} for name, count in sorted(variation_counts.items())],
    }


def load_thresholds(args: argparse.Namespace) -> Thresholds:
    threshold_values: dict[str, object] = {}
    if args.thresholds_file:
        threshold_values.update(json.loads(read_text(Path(args.thresholds_file))))
    for field in (
        "min_total",
        "min_routing",
        "min_portability",
        "min_description",
        "min_cases_per_route",
        "max_single_route_load_words",
        "max_two_route_load_words",
    ):
        value = getattr(args, field)
        if value is not None:
            threshold_values[field] = value
    threshold_values["strict_findings"] = args.strict_findings
    return Thresholds(**threshold_values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thresholds-file", help="Optional JSON file with pass/fail thresholds.")
    parser.add_argument("--markdown-out", help="Optional markdown summary output path.")
    parser.add_argument("--min-total", type=float, help="Fail if a skill total score falls below this value.")
    parser.add_argument("--min-routing", type=float, help="Fail if overall trigger+route eval score falls below this value.")
    parser.add_argument("--min-portability", type=float, help="Fail if a skill portability score falls below this value.")
    parser.add_argument("--min-description", type=float, help="Fail if a skill description score falls below this value.")
    parser.add_argument("--min-cases-per-route", type=int, help="Fail if any routed sub-skill has fewer eval cases than this.")
    parser.add_argument(
        "--max-single-route-load-words",
        type=int,
        help="Fail if description + SKILL.md + the heaviest routed file exceeds this word budget.",
    )
    parser.add_argument(
        "--max-two-route-load-words",
        type=int,
        help="Fail if description + SKILL.md + the two heaviest routed files exceeds this word budget.",
    )
    parser.add_argument(
        "--strict-findings",
        action="store_true",
        help="Fail if any informational findings remain, even if thresholds pass.",
    )
    return parser.parse_args()


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Skill Evaluations",
        "",
        "Generated by `python3 scripts/skill_critic.py`.",
        "",
        "## Thresholds",
        "",
        f"- `min_total`: {report['thresholds']['min_total']}",
        f"- `min_routing`: {report['thresholds']['min_routing']}",
        f"- `min_portability`: {report['thresholds']['min_portability']}",
        f"- `min_description`: {report['thresholds']['min_description']}",
        f"- `min_cases_per_route`: {report['thresholds']['min_cases_per_route']}",
        f"- `max_single_route_load_words`: {report['thresholds']['max_single_route_load_words']}",
        f"- `max_two_route_load_words`: {report['thresholds']['max_two_route_load_words']}",
        "",
        "## Summary",
        "",
        "| Skill | Status | Total | Trigger | Route | Overall Eval | Portability | Description | Single-route load | Two-route load | Directory words |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for skill in report["skills"]:
        metrics = skill["metrics"]
        scores = skill["scores"]
        lines.append(
            f"| `{skill['skill']}` | {skill['status']} | {scores['total']} | {scores['trigger_eval']} | "
            f"{scores['route_eval']} | {scores['routing_eval']} | {scores['portability']} | "
            f"{scores['description']} | {metrics['max_single_route_load_words']} | "
            f"{metrics['max_two_route_load_words']} | {metrics['directory_words']} |"
        )
    for skill in report["skills"]:
        lines.extend(["", f"## {skill['skill']}", ""])
        if skill["threshold_failures"]:
            lines.append("Threshold failures:")
            for failure in skill["threshold_failures"]:
                lines.append(f"- {failure}")
        if skill["findings"]:
            lines.append("Findings:")
            for finding in skill["findings"]:
                lines.append(f"- {finding}")
        else:
            lines.append("No findings.")
        lines.append("Route eval coverage:")
        for coverage in skill["metrics"]["route_case_counts"]:
            lines.append(f"- `{coverage['slug']}`: {coverage['count']} cases")
        lines.append("Case mix:")
        for item in skill["metrics"]["category_counts"]:
            lines.append(f"- category `{item['name']}`: {item['count']}")
        for item in skill["metrics"]["variation_counts"]:
            lines.append(f"- variation `{item['name']}`: {item['count']}")
        failure_counts = Counter(
            result["failure_mode"] for result in skill["routing_results"] if result["failure_mode"] != "pass"
        )
        lines.append("Failure modes:")
        if failure_counts:
            for mode, count in failure_counts.most_common(5):
                lines.append(f"- `{mode}`: {count}")
        else:
            lines.append("- none")
        failed_results = [result for result in skill["routing_results"] if not result["passed"]]
        if failed_results:
            lines.append("Representative failures:")
            for result in failed_results[:5]:
                lines.append(
                    f"- `{result['id']}`: `{result['failure_mode']}` on prompt: {result['prompt']}"
                )
        lines.append("Top route file sizes:")
        for route_metric in skill["metrics"]["route_word_counts"][:5]:
            lines.append(f"- `{route_metric['slug']}`: {route_metric['words']} words")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    thresholds = load_thresholds(args)
    skill_roots = discover_skill_roots()
    if not skill_roots:
        print("No skill roots found.", file=sys.stderr)
        return 1

    report: dict[str, object] = {
        "repo": str(REPO_ROOT),
        "thresholds": {
            "min_total": thresholds.min_total,
            "min_routing": thresholds.min_routing,
            "min_portability": thresholds.min_portability,
            "min_description": thresholds.min_description,
            "min_cases_per_route": thresholds.min_cases_per_route,
            "max_single_route_load_words": thresholds.max_single_route_load_words,
            "max_two_route_load_words": thresholds.max_two_route_load_words,
            "strict_findings": thresholds.strict_findings,
        },
        "skills": [],
    }
    exit_code = 0
    cases = load_eval_cases()
    for skill_root in skill_roots:
        skill_md = skill_root / "SKILL.md"
        skill_md_text = read_text(skill_md)
        frontmatter = parse_frontmatter(skill_md)
        description = frontmatter.get("description", "")
        routes = parse_routes(skill_md)
        directory_words = sum(count_words(read_text(path)) for path in skill_root.rglob("*.md"))
        load_metrics = route_word_metrics(description, skill_md_text, routes)
        coverage_metrics = case_coverage_metrics(cases, routes)

        description_score, description_findings = score_description(description)
        structure_score, structure_findings = score_structure(skill_root, routes)
        portability_score, portability_findings = score_portability(skill_root, routes)
        routing_score, trigger_score, route_score, routing_findings, routing_results = evaluate_routing(
            description, routes, cases
        )

        total_score = round(
            0.25 * description_score
            + 0.2 * structure_score
            + 0.25 * portability_score
            + 0.3 * routing_score,
            1,
        )

        all_findings = (
            format_findings("description", description_findings)
            + format_findings("structure", structure_findings)
            + format_findings("portability", portability_findings)
            + format_findings("routing", routing_findings)
        )
        threshold_failures: list[str] = []
        if thresholds.min_total is not None and total_score < thresholds.min_total:
            threshold_failures.append(f"total {total_score} < {thresholds.min_total}")
        if thresholds.min_routing is not None and routing_score < thresholds.min_routing:
            threshold_failures.append(f"routing_eval {routing_score} < {thresholds.min_routing}")
        if thresholds.min_portability is not None and portability_score < thresholds.min_portability:
            threshold_failures.append(f"portability {portability_score} < {thresholds.min_portability}")
        if thresholds.min_description is not None and description_score < thresholds.min_description:
            threshold_failures.append(f"description {description_score} < {thresholds.min_description}")
        if thresholds.min_cases_per_route is not None:
            undercovered = [
                item["slug"]
                for item in coverage_metrics["route_case_counts"]
                if item["count"] < thresholds.min_cases_per_route
            ]
            if undercovered:
                threshold_failures.append(
                    f"routes below min_cases_per_route {thresholds.min_cases_per_route}: {', '.join(undercovered)}"
                )
        if (
            thresholds.max_single_route_load_words is not None
            and load_metrics["max_single_route_load_words"] > thresholds.max_single_route_load_words
        ):
            threshold_failures.append(
                f"max_single_route_load_words {load_metrics['max_single_route_load_words']} > "
                f"{thresholds.max_single_route_load_words}"
            )
        if (
            thresholds.max_two_route_load_words is not None
            and load_metrics["max_two_route_load_words"] > thresholds.max_two_route_load_words
        ):
            threshold_failures.append(
                f"max_two_route_load_words {load_metrics['max_two_route_load_words']} > "
                f"{thresholds.max_two_route_load_words}"
            )
        if threshold_failures or (thresholds.strict_findings and all_findings):
            exit_code = 2

        report["skills"].append(
            {
                "skill": skill_root.name,
                "name": frontmatter.get("name", skill_root.name),
                "status": "pass" if not threshold_failures and not (thresholds.strict_findings and all_findings) else "fail",
                "scores": {
                    "description": round(description_score, 1),
                    "structure": round(structure_score, 1),
                    "portability": round(portability_score, 1),
                    "trigger_eval": round(trigger_score, 1),
                    "route_eval": round(route_score, 1),
                    "routing_eval": round(routing_score, 1),
                    "total": total_score,
                },
                "metrics": {
                    "description_words": count_words(description),
                    "skill_md_words": count_words(skill_md_text),
                    "max_single_route_load_words": load_metrics["max_single_route_load_words"],
                    "max_two_route_load_words": load_metrics["max_two_route_load_words"],
                    "route_case_counts": coverage_metrics["route_case_counts"],
                    "category_counts": coverage_metrics["category_counts"],
                    "variation_counts": coverage_metrics["variation_counts"],
                    "route_word_counts": load_metrics["route_word_counts"],
                    "directory_words": directory_words,
                },
                "threshold_failures": threshold_failures,
                "findings": all_findings,
                "routing_results": routing_results,
            }
        )

    if args.markdown_out:
        markdown_path = Path(args.markdown_out)
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
