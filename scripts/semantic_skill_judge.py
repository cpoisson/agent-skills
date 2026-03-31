#!/usr/bin/env python3
"""Semantic trigger and routing evals using a switchable inference provider."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skill_critic import (
    EVAL_CASES_PATH,
    REPO_ROOT,
    classify_failure_mode,
    load_eval_cases,
    parse_frontmatter,
    parse_routes,
    read_text,
)


DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "huggingface": "https://router.huggingface.co/v1",
    "llamacpp": "http://localhost:8080/v1",
    "ollama": "http://localhost:11434",
}
DEFAULT_MODELS = {
    "openai": "gpt-5-mini",
    "huggingface": "google/gemma-2-2b-it:cerebras",
    "llamacpp": "local-model",
    "ollama": "qwen2.5:7b",
}
DEFAULT_API_KEY_ENVS = {
    "openai": "OPENAI_API_KEY",
    "huggingface": "HF_TOKEN",
}


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass
class JudgeResult:
    case_id: str
    prompt: str
    category: str
    variation: str
    expected_trigger: bool
    expected_route: str | None
    predicted_trigger: bool
    predicted_route: str
    passed: bool
    confidence: float | None
    rationale: str
    raw_response: str
    failure_mode: str


@dataclass
class ProviderConfig:
    provider: str
    model: str
    base_url: str
    api_key: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=sorted(DEFAULT_BASE_URLS), default="openai")
    parser.add_argument("--model", help="Model id. Defaults depend on the selected provider.")
    parser.add_argument("--base-url", help="Override provider base URL.")
    parser.add_argument("--api-key-env", help="Environment variable containing the provider API key.")
    parser.add_argument(
        "--hf-provider",
        help="Optional Hugging Face provider suffix, appended as model:provider when using --provider huggingface.",
    )
    parser.add_argument("--cases-file", default=str(EVAL_CASES_PATH))
    parser.add_argument("--router-file", default=str(REPO_ROOT / "qa-strategist" / "SKILL.md"))
    parser.add_argument("--thresholds-file", default=str(REPO_ROOT / "evals" / "semantic_judge_thresholds.json"))
    parser.add_argument("--markdown-out", help="Optional markdown summary output path.")
    parser.add_argument("--max-cases", type=int, help="Limit the number of eval cases.")
    parser.add_argument("--fail-below", type=float, help="Override minimum accuracy threshold.")
    return parser.parse_args()


def resolve_provider_config(args: argparse.Namespace) -> ProviderConfig:
    provider = args.provider
    model = args.model or DEFAULT_MODELS[provider]
    if provider == "huggingface" and args.hf_provider and ":" not in model:
        model = f"{model}:{args.hf_provider}"
    base_url = (args.base_url or DEFAULT_BASE_URLS[provider]).rstrip("/")
    api_key_env = args.api_key_env or DEFAULT_API_KEY_ENVS.get(provider)
    api_key = os.getenv(api_key_env) if api_key_env else None
    return ProviderConfig(provider=provider, model=model, base_url=base_url, api_key=api_key)


def build_routing_context(router_file: Path) -> tuple[str, list[str], str]:
    description = parse_frontmatter(router_file).get("description", "")
    routes = parse_routes(router_file)
    route_lines = [
        f"- {route.slug}: intent={route.intent}; load_when={route.load_when}"
        for route in routes
    ]
    return description, [route.slug for route in routes], "\n".join(route_lines)


def build_messages(prompt: str, description: str, route_context: str, allowed_routes: list[str]) -> tuple[str, str]:
    system_prompt = (
        "You are evaluating whether a QA skill should trigger for a user prompt and, if it should, "
        "which routed sub-skill should handle it. "
        "Choose exactly one route slug from the allowed list when the skill should trigger. "
        "Return JSON only with keys should_trigger, route, confidence, rationale. "
        "If should_trigger is false, route must be an empty string."
    )
    user_prompt = (
        f"Top-level skill description:\n{description}\n\n"
        f"Allowed routes:\n{route_context}\n\n"
        f"Allowed route slugs: {', '.join(allowed_routes)}\n\n"
        f"User prompt:\n{prompt}\n\n"
        'Return JSON only, for example: {"should_trigger":true,"route":"bug-fix","confidence":0.93,"rationale":"..."}'
    )
    return system_prompt, user_prompt


def http_post(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} returned HTTP {exc.code}: {body}") from exc


def call_openai_compatible(config: ProviderConfig, system_prompt: str, user_prompt: str) -> str:
    headers = {"Authorization": f"Bearer {config.api_key}"} if config.api_key else {}
    payload = {
        "model": config.model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    response = http_post(f"{config.base_url}/chat/completions", headers, payload)
    message = response["choices"][0]["message"]["content"]
    if isinstance(message, list):
        return "".join(part.get("text", "") for part in message if isinstance(part, dict))
    return str(message)


def call_ollama(config: ProviderConfig, system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": config.model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0},
    }
    response = http_post(f"{config.base_url}/api/chat", {}, payload)
    return str(response["message"]["content"])


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if not match:
            raise ValueError(f"Could not find JSON object in response: {text}")
        return json.loads(match.group(0))


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    return False


def judge_prompt(
    config: ProviderConfig,
    prompt: str,
    description: str,
    allowed_routes: list[str],
    route_context: str,
) -> tuple[bool, str, float | None, str, str]:
    system_prompt, user_prompt = build_messages(prompt, description, route_context, allowed_routes)
    if config.provider == "ollama":
        raw = call_ollama(config, system_prompt, user_prompt)
    else:
        raw = call_openai_compatible(config, system_prompt, user_prompt)
    parsed = extract_json_object(raw)
    should_trigger = parse_bool(parsed.get("should_trigger"))
    predicted = str(parsed.get("route", "")).strip()
    if predicted not in allowed_routes:
        predicted = ""
    if not should_trigger:
        predicted = ""
    confidence_raw = parsed.get("confidence")
    confidence = float(confidence_raw) if isinstance(confidence_raw, (int, float)) else None
    rationale = str(parsed.get("rationale", "")).strip()
    return should_trigger, predicted, confidence, rationale, raw


def render_markdown(
    provider: ProviderConfig,
    min_accuracy: float,
    overall_accuracy: float,
    trigger_accuracy: float,
    route_accuracy: float,
    route_counts: dict[str, int],
    category_counts: dict[str, int],
    results: list[JudgeResult],
) -> str:
    lines = [
        "# Semantic Judge Evaluations",
        "",
        f"- Provider: `{provider.provider}`",
        f"- Model: `{provider.model}`",
        f"- Base URL: `{provider.base_url}`",
        f"- Minimum overall accuracy: `{min_accuracy:.2f}`",
        f"- Actual overall accuracy: `{overall_accuracy:.3f}`",
        f"- Trigger accuracy: `{trigger_accuracy:.3f}`",
        f"- Triggered-route accuracy: `{route_accuracy:.3f}`",
        "",
        "## Coverage",
        "",
    ]
    for slug in sorted(route_counts):
        lines.append(f"- route `{slug}`: {route_counts[slug]} cases")
    for category in sorted(category_counts):
        lines.append(f"- category `{category}`: {category_counts[category]} cases")
    failed = [result for result in results if not result.passed]
    failure_counts = Counter(result.failure_mode for result in failed)
    lines.extend(["", "## Results", ""])
    if not failed:
        lines.append("No failures.")
    else:
        for mode, count in failure_counts.most_common():
            lines.append(f"- `{mode}`: {count}")
        lines.append("")
        for result in failed[:20]:
            expected_route = result.expected_route or "NO_TRIGGER"
            got = result.predicted_route if result.predicted_trigger else "NO_TRIGGER"
            lines.append(
                f"- `{result.case_id}` expected `{expected_route}`, got `{got}` for prompt: {result.prompt}"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    load_dotenv(REPO_ROOT / ".env")
    config = resolve_provider_config(args)
    if config.provider in {"openai", "huggingface"} and not config.api_key:
        missing = args.api_key_env or DEFAULT_API_KEY_ENVS[config.provider]
        print(f"Missing API key in environment variable {missing}.", file=sys.stderr)
        return 2

    thresholds = json.loads(read_text(Path(args.thresholds_file)))
    min_accuracy = args.fail_below if args.fail_below is not None else float(thresholds["min_accuracy"])
    all_cases = load_eval_cases(Path(args.cases_file))
    cases = all_cases[: args.max_cases] if args.max_cases is not None else all_cases
    description, allowed_routes, route_context = build_routing_context(Path(args.router_file))

    results: list[JudgeResult] = []
    route_counts = {slug: 0 for slug in allowed_routes}
    category_counts: Counter[str] = Counter()
    trigger_passes = 0
    route_passes = 0
    overall_passes = 0
    routed_cases = [case for case in cases if case.should_trigger]
    for case in cases:
        category_counts[case.category] += 1
        if case.expected_route:
            route_counts[case.expected_route] = route_counts.get(case.expected_route, 0) + 1
        predicted_trigger, predicted_route, confidence, rationale, raw = judge_prompt(
            config,
            case.prompt,
            description,
            allowed_routes,
            route_context,
        )
        trigger_ok = predicted_trigger == case.should_trigger
        route_ok = case.should_trigger and predicted_trigger and predicted_route == (case.expected_route or "")
        passed = trigger_ok and (route_ok if case.should_trigger else True)
        trigger_passes += int(trigger_ok)
        if case.should_trigger:
            route_passes += int(route_ok)
        overall_passes += int(passed)
        results.append(
            JudgeResult(
                case_id=case.case_id,
                prompt=case.prompt,
                category=case.category,
                variation=case.variation,
                expected_trigger=case.should_trigger,
                expected_route=case.expected_route,
                predicted_trigger=predicted_trigger,
                predicted_route=predicted_route,
                passed=passed,
                confidence=confidence,
                rationale=rationale,
                raw_response=raw,
                failure_mode=classify_failure_mode(case, predicted_trigger, predicted_route),
            )
        )

    trigger_accuracy = trigger_passes / len(cases) if cases else 0.0
    route_accuracy = route_passes / len(routed_cases) if routed_cases else 0.0
    overall_accuracy = overall_passes / len(cases) if cases else 0.0
    report = {
        "provider": config.provider,
        "model": config.model,
        "base_url": config.base_url,
        "min_accuracy": min_accuracy,
        "overall_accuracy": overall_accuracy,
        "trigger_accuracy": trigger_accuracy,
        "route_accuracy": route_accuracy,
        "coverage": {
            "routes": route_counts,
            "categories": dict(category_counts),
        },
        "results": [
            {
                "id": result.case_id,
                "prompt": result.prompt,
                "category": result.category,
                "variation": result.variation,
                "expected_trigger": result.expected_trigger,
                "expected_route": result.expected_route,
                "predicted_trigger": result.predicted_trigger,
                "predicted_route": result.predicted_route,
                "passed": result.passed,
                "confidence": result.confidence,
                "rationale": result.rationale,
                "failure_mode": result.failure_mode,
                "raw_response": result.raw_response,
            }
            for result in results
        ],
    }
    if args.markdown_out:
        Path(args.markdown_out).write_text(
            render_markdown(
                config,
                min_accuracy,
                overall_accuracy,
                trigger_accuracy,
                route_accuracy,
                route_counts,
                dict(category_counts),
                results,
            ),
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if overall_accuracy >= min_accuracy else 2


if __name__ == "__main__":
    raise SystemExit(main())
