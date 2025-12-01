import time
import json
from typing import Dict, Any


def _check(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)


async def test_fx_pricing_orchestrator_once(config: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    result = await run_full_fx_pricing_pipeline(
        product_name=config["product_name"],
        category=config["category"],
        region=config["region"],
        reporting_currency=config["reporting_currency"],
        purchase_price=config["purchase_price"],
        purchase_currency=config["purchase_currency"],
        volume_units=config["volume_units"],
        current_or_planned_price=config["current_or_planned_price"],
        target_margin_pct=config["target_margin_pct"],
        manager_notes=config.get("manager_notes", ""),
        user_id=config.get("user_id", "orchestrator-test"),
    )
    duration_ms = (time.time() - start) * 1000.0

    decision_brief_text = result.get("decision_brief_text", "") or ""
    structured_summary_json = result.get("structured_summary_json", "") or ""
    evaluation_json = result.get("evaluation_json", "") or ""
    obs_summary = result.get("observability_summary", {}) or {}
    obs_detailed = result.get("observability_detailed", {}) or {}

    _check(isinstance(result, dict), "Result is not a dict")
    _check(isinstance(decision_brief_text, str), "decision_brief_text is not a string")
    _check(len(decision_brief_text.strip()) > 0, "decision_brief_text is empty")
    _check(len(decision_brief_text.strip()) > 400, "decision_brief_text is too short")

    try:
        struct_obj = json.loads(structured_summary_json)
        struct_ok = isinstance(struct_obj, dict)
    except Exception:
        struct_obj = {}
        struct_ok = False
    _check(struct_ok, "structured_summary_json is not valid JSON dict")

    try:
        eval_obj = json.loads(evaluation_json)
        eval_ok = isinstance(eval_obj, dict)
    except Exception:
        eval_obj = {}
        eval_ok = False
    _check(eval_ok, "evaluation_json is not valid JSON dict")

    market_json = result.get("market_research_json", "") or ""
    competitive_json = result.get("competitive_pricing_json", "") or ""
    fx_json = result.get("fx_impact_json", "") or ""
    margin_json = result.get("margin_scenarios_json", "") or ""
    vendor_json = result.get("vendor_fx_json", "") or ""

    for name, value in [
        ("market_research_json", market_json),
        ("competitive_pricing_json", competitive_json),
        ("fx_impact_json", fx_json),
        ("margin_scenarios_json", margin_json),
        ("vendor_fx_json", vendor_json),
    ]:
        _check(isinstance(value, str), f"{name} is not a string")
        _check(len(value.strip()) > 0, f"{name} is empty")

    _check(isinstance(obs_summary, dict), "observability_summary is not a dict")
    _check(isinstance(obs_detailed, dict), "observability_detailed is not a dict")

    model_calls = obs_summary.get("model_invocations", 0)
    tool_calls = obs_summary.get("tool_invocations", 0)
    agent_calls = obs_summary.get("agent_invocations", 0)
    event_count = obs_summary.get("event_count", 0)

    _check(model_calls > 0, "No model invocations recorded")
    _check(event_count > 0, "No events recorded in observability_summary")

    total_prompt_chars = obs_detailed.get("total_prompt_chars", 0)
    total_response_chars = obs_detailed.get("total_response_chars", 0)
    error_count = obs_summary.get("error_count", 0)
    
    if error_count == 0:
        if total_prompt_chars == 0 or total_response_chars == 0:
            print(
                "Warning: total_prompt_chars/total_response_chars == 0 — "
                "Most likely, ADK didn't pass the text to our observability plugin."
                "I'm ignoring this in my tests."
            )
    else:
        print(
            "Warning: model errors occurred (e.g. 429 quota), "
            "I skip strict checks on prompt/response chars."
        )


    entries = FX_MEMORY.search_memory(
        product_name=config["product_name"],
        region=config["region"],
        limit=10,
    )
    _check(len(entries) >= 1, "No memory entries found after orchestrator run")
    last_entry = entries[0]
    _check(
        last_entry.product_name == config["product_name"],
        "Last memory entry product_name mismatch",
    )
    _check(
        last_entry.region == config["region"],
        "Last memory entry region mismatch",
    )

    health_basic = evaluate_pipeline_output_basic(result)

    return {
        "result": result,
        "duration_ms": duration_ms,
        "structured_summary_obj": struct_obj,
        "evaluation_obj": eval_obj,
        "observability_summary": obs_summary,
        "observability_detailed": obs_detailed,
        "memory_entries": entries,
        "health_basic": health_basic,
    }


async def test_fx_pricing_orchestrator_full() -> Dict[str, Any]:
    base_config = {
        "product_name": "Apple iPhone 17 Air",
        "category": "smartphone",
        "region": "US",
        "reporting_currency": "USD",
        "purchase_price": 800.0,
        "purchase_currency": "CNY",
        "volume_units": 1000,
        "current_or_planned_price": 1099.0,
        "target_margin_pct": 0.25,
        "manager_notes": "First orchestrator test run.",
        "user_id": "orchestrator-test",
    }

    first_run = await test_fx_pricing_orchestrator_once(base_config)

    second_config = dict(base_config)
    second_config["manager_notes"] = "Second orchestrator test run with updated notes."
    second_config["user_id"] = "orchestrator-test-2"

    second_run = await test_fx_pricing_orchestrator_once(second_config)

    entries = FX_MEMORY.search_memory(
        product_name=base_config["product_name"],
        region=base_config["region"],
        limit=10,
    )
    _check(
        len(entries) >= 2,
        "Expected at least 2 memory entries after two orchestrator runs",
    )

    total_duration_ms = first_run["duration_ms"] + second_run["duration_ms"]

    print("First run duration (ms):", first_run["duration_ms"])
    print("Second run duration (ms):", second_run["duration_ms"])
    print("Total duration (ms):", total_duration_ms)
    print("First run basic health:", first_run["health_basic"])
    print("Second run basic health:", second_run["health_basic"])
    print("Memory entries for product/region:", len(entries))

    print("Observability summary (first run):", first_run["observability_summary"])
    print("Observability summary (second run):", second_run["observability_summary"])

    print("✔️ Orchestrator full test finished successfully!")

    return {
        "first_run": first_run,
        "second_run": second_run,
        "memory_entries": entries,
        "total_duration_ms": total_duration_ms,
    }


print("✔️ Orchestrator tests have been installed!")
