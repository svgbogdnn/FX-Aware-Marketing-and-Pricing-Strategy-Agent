import logging
logging.getLogger("google_genai.types").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

import json
import io
import contextlib
from typing import Any, Dict, List, Optional


def _check(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)

def _prettify_key(key: str) -> str:
    s = str(key).replace("_", " ").strip()
    if not s:
        return s
    return s[0].upper() + s[1:]


def _format_json_human(
    value: Any,
    indent: int = 0,
    parent_key: Optional[str] = None,
) -> List[str]:
    lines: List[str] = []
    ind = " " * indent

    if isinstance(value, dict):
        items = list(value.items())
        for i, (k, v) in enumerate(items):
            label = _prettify_key(k)
            if isinstance(v, (dict, list)):
                lines.append(f"{ind}{label}:")
                lines.extend(_format_json_human(v, indent + 2, parent_key=k))
            else:
                lines.append(f"{ind}{label}: {v}")

            if indent == 0 and i < len(items) - 1:
                lines.append("")

    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{ind}-")
                lines.extend(_format_json_human(item, indent + 2, parent_key=parent_key))
            else:
                if parent_key == "flags" and isinstance(item, str):
                    text = f"`{item}`"
                else:
                    text = str(item)
                lines.append(f"{ind}- {text}")
    else:
        lines.append(f"{ind}{value}")

    return lines

def _pretty_print_json_maybe(data: Any, title: str) -> None:
    print(title)
    print("." * 60)

    if data is None:
        print("None")
        print()
        return

    obj: Any = data

    if isinstance(data, str):
        text = data.strip()
        if not text:
            print("None")
            print()
            return
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            print(text)
            print()
            return

    if isinstance(obj, (dict, list)):
        lines = _format_json_human(obj, indent=0)
        print("\n".join(lines))
    else:
        print(obj)

    print()


async def run_demo_scenario(demo_index: int, scenario_name: str, config: Dict[str, Any]) -> None:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        run = await test_fx_pricing_orchestrator_once(config)

    result = run["result"]

    raw_decision_brief_text = result.get("decision_brief_text", "") or ""
    structured_summary_json = result.get("structured_summary_json")
    evaluation_json = result.get("evaluation_json")
    observability_summary = run.get("observability_summary", {}) or {}
    health_basic = run.get("health_basic", {}) or {}
    manager_notes = config.get("manager_notes", "").strip() or "(no manager notes provided)"

    splitter = "🔹 STRUCTURED_SUMMARY_JSON 🔹"
    if splitter in raw_decision_brief_text:
        decision_brief_text = raw_decision_brief_text.split(splitter, 1)[0].rstrip()
    else:
        decision_brief_text = raw_decision_brief_text

    print("=" * 60)
    print(f"DEMO {demo_index}: {scenario_name}")
    print("=" * 60)
    print()
    print("=" * 60)
    print("🔸 USER 🔸")
    print(manager_notes)
    print("=" * 60)
    print()
    print("=" * 60)    
    print("🔸 AGENT RESPONSE 🔸")
    print("=" * 60)
    print()
    print("1)🔹 DECISION BRIEF 🔹")
    print("." * 60)
    print(decision_brief_text)
    print()

    _pretty_print_json_maybe(structured_summary_json, "2)🔹 STRUCTURED SUMMARY 🔹")

    _pretty_print_json_maybe(evaluation_json, "3)🔹 EVALUATION 🔹")

    print("4)🔹 OBSERVABILITY SUMMARY 🔹")
    print("." * 60)
    if isinstance(observability_summary, dict) and observability_summary:
        obs_lines = _format_json_human(observability_summary, indent=0)
        print("\n".join(obs_lines))
    else:
        print("None")
    print()

    print("5)🔹 BASIC HEALTH 🔹")
    print("." * 60)
    if isinstance(health_basic, dict) and health_basic:
        health_lines = _format_json_human(health_basic, indent=0)
        print("\n".join(health_lines))
    else:
        print("None")
    print()


demo_scenarios: List[Dict[str, Any]] = [
    (
        "High-end laptop – US launch with CNY purchase",
        {
            "product_name": "Apple MacBook Pro 16 M3 Max",
            "category": "laptop",
            "region": "US",
            "reporting_currency": "USD",
            "purchase_price": 17000.0,
            "purchase_currency": "CNY",
            "volume_units": 300,
            "current_or_planned_price": 3499.0,
            "target_margin_pct": 0.28,
            "manager_notes": (
                "High-end MacBook Pro launch in the US market. "
                "We buy in CNY and report in USD. Please evaluate FX risk, "
                "margin versus key competitors, and provide a clear price "
                "recommendation with risk commentary for the launch."
            ),
            "user_id": "demo-macbook-us-launch",
        },
    )
]

async def run_all_demo_scenarios() -> None:
    for idx, (scenario_name, config) in enumerate(demo_scenarios, start=1):
        await run_demo_scenario(idx, scenario_name, config)

await run_all_demo_scenarios()
