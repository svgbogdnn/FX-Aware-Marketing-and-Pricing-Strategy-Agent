import time
import json
from typing import Any, Dict, List


async def run_batch_fx_pricing_pipeline(
    batch_configs,
    user_id_prefix: str = "batch-manager",
):
    
    """
    Run the full FX pricing pipeline for a batch of product configs
    and collect both per-item results and lightweight observability meta.
    """
    
    batch_results = []
    batch_meta = []
    total_start = time.time()

    total_items = len(batch_configs)

    for idx, cfg in enumerate(batch_configs, start=1):
        print(f"--- [{idx}/{total_items}] Starting {cfg['product_name']} ({cfg['region']}) ---")
        start = time.time()

        result = await run_full_fx_pricing_pipeline(
            product_name=cfg["product_name"],
            category=cfg["category"],
            region=cfg["region"],
            reporting_currency=cfg["reporting_currency"],
            purchase_price=cfg["purchase_price"],
            purchase_currency=cfg["purchase_currency"],
            volume_units=cfg["volume_units"],
            current_or_planned_price=cfg["current_or_planned_price"],
            target_margin_pct=cfg["target_margin_pct"],
            manager_notes=cfg.get("manager_notes", ""),
            user_id=f"{user_id_prefix}:{idx}",
        )

        duration_ms = (time.time() - start) * 1000.0

        obs = result.get("observability_detailed", {}) or {}
        batch_meta.append(
            {
                "index": idx,
                "product_name": cfg["product_name"],
                "region": cfg["region"],
                "duration_ms": duration_ms,
                "model_invocations": obs.get("model_invocations"),
                "tool_invocations": obs.get("tool_invocations"),
                "agent_invocations": obs.get("agent_invocations"),
                "total_prompt_chars": obs.get("total_prompt_chars"),
                "total_response_chars": obs.get("total_response_chars"),
            }
        )
        batch_results.append(result)

        print(f"--- [{idx}/{total_items}] Done in {duration_ms:.1f} ms ---")

    total_duration_ms = (time.time() - total_start) * 1000.0

    return {
        "batch_results": batch_results,
        "batch_meta": batch_meta,
        "total_duration_ms": total_duration_ms,
    }


print("✔️ Batch FX pricing pipeline has been installed!")


def evaluate_pipeline_output_basic(result: dict) -> dict:
    """
    Perform basic health checks on a single FX pipeline result and
    return a pass/fail flag plus a list of detected issues.
    """
    
    issues = []

    structured_summary_json = result.get("structured_summary_json", "")
    evaluation_json = result.get("evaluation_json", "")
    decision_brief_text = result.get("decision_brief_text", "") or ""
    obs_summary = result.get("observability_summary", {}) or {}

    try:
        struct_obj = json.loads(structured_summary_json)
    except Exception:
        struct_obj = {}
        issues.append("structured_summary_not_valid_json")

    try:
        eval_obj = json.loads(evaluation_json)
    except Exception:
        eval_obj = {}
        issues.append("evaluation_not_valid_json")

    if not decision_brief_text.strip():
        issues.append("empty_decision_brief")

    if len(decision_brief_text.strip()) < 400:
        issues.append("decision_brief_too_short")

    model_calls = obs_summary.get("model_invocations", 0)
    if model_calls == 0:
        issues.append("no_model_invocations")

    if not isinstance(struct_obj, dict):
        issues.append("structured_summary_not_dict")

    if not isinstance(eval_obj, dict):
        issues.append("evaluation_not_dict")

    passed = len(issues) == 0

    return {
        "passed": passed,
        "issue_count": len(issues),
        "issues": issues,
    }


async def run_regression_suite(test_cases, user_id_prefix: str = "regression"):
    """
    Run a regression suite over multiple test cases, evaluate each pipeline
    output with basic checks and collect per-case health and observability.
    """
    
    regression_results = []

    total = len(test_cases)
    for idx, cfg in enumerate(test_cases, start=1):
        print(f"=== Regression case {idx}/{total}: {cfg['product_name']} ({cfg['region']}) ===")

        result = await run_full_fx_pricing_pipeline(
            product_name=cfg["product_name"],
            category=cfg["category"],
            region=cfg["region"],
            reporting_currency=cfg["reporting_currency"],
            purchase_price=cfg["purchase_price"],
            purchase_currency=cfg["purchase_currency"],
            volume_units=cfg["volume_units"],
            current_or_planned_price=cfg["current_or_planned_price"],
            target_margin_pct=cfg["target_margin_pct"],
            manager_notes=cfg.get("manager_notes", ""),
            user_id=f"{user_id_prefix}:{idx}",
        )

        health = evaluate_pipeline_output_basic(result)
        status = "PASS" if health["passed"] else "FAIL"

        print(f"Result {status}: issues={health['issues']}")

        regression_results.append(
            {
                "index": idx,
                "input": cfg,
                "health": health,
                "observability_summary": result.get("observability_summary", {}) or {},
            }
        )

    return regression_results


def summarize_batch_run(batch_output: Dict[str, Any]) -> Dict[str, Any]:
    
    """
    Compute aggregate statistics for a batch run:
    durations, average invocation counts and payload sizes across all items.
    """
    
    batch_meta = batch_output.get("batch_meta", []) or []
    total_duration_ms = float(batch_output.get("total_duration_ms", 0.0) or 0.0)
    total_items = len(batch_meta)

    if total_items == 0:
        return {
            "item_count": 0,
            "total_duration_ms": total_duration_ms,
            "avg_item_duration_ms": 0.0,
            "avg_model_invocations": 0.0,
            "avg_tool_invocations": 0.0,
            "avg_agent_invocations": 0.0,
            "avg_prompt_chars": 0.0,
            "avg_response_chars": 0.0,
        }

    sum_item_duration = 0.0
    sum_model = 0.0
    sum_tool = 0.0
    sum_agent = 0.0
    sum_prompt = 0.0
    sum_response = 0.0

    for m in batch_meta:
        sum_item_duration += float(m.get("duration_ms", 0.0) or 0.0)
        sum_model += float(m.get("model_invocations", 0.0) or 0.0)
        sum_tool += float(m.get("tool_invocations", 0.0) or 0.0)
        sum_agent += float(m.get("agent_invocations", 0.0) or 0.0)
        sum_prompt += float(m.get("total_prompt_chars", 0.0) or 0.0)
        sum_response += float(m.get("total_response_chars", 0.0) or 0.0)

    return {
        "item_count": total_items,
        "total_duration_ms": total_duration_ms,
        "avg_item_duration_ms": sum_item_duration / total_items,
        "avg_model_invocations": sum_model / total_items,
        "avg_tool_invocations": sum_tool / total_items,
        "avg_agent_invocations": sum_agent / total_items,
        "avg_prompt_chars": sum_prompt / total_items,
        "avg_response_chars": sum_response / total_items,
    }


def summarize_regression_suite_results(regression_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    
    """
    Compute high-level metrics for a regression suite:
    pass rate, number of failing cases and the most frequent issue codes.
    """
    
    total = len(regression_results)
    if total == 0:
        return {
            "case_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "pass_rate": 0.0,
            "issue_frequency": {},
        }

    pass_count = 0
    issue_counter: Dict[str, int] = {}

    for item in regression_results:
        health = item.get("health", {}) or {}
        passed = bool(health.get("passed", False))
        if passed:
            pass_count += 1
        issues = health.get("issues", []) or []
        for issue in issues:
            issue_counter[issue] = issue_counter.get(issue, 0) + 1

    fail_count = total - pass_count
    pass_rate = pass_count / total if total > 0 else 0.0

    return {
        "case_count": total,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": pass_rate,
        "issue_frequency": issue_counter,
    }


def export_regression_report_to_json(
    regression_results: List[Dict[str, Any]],
    filename: str = "regression_report.json",
) -> str:
    """
    Export full regression results to a JSON file and return the filename
    so it can be referenced in logs or UI.
    """
    
    payload = {
        "results": regression_results,
        "summary": summarize_regression_suite_results(regression_results),
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return filename


print("✔️ Regression, evaluation and summary helpers have been installed!")
