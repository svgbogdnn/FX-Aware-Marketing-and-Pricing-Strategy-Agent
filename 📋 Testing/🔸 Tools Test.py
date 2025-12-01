import json
import os
from datetime import datetime


def _check(cond, message):
    """Raise RuntimeError with the given message if the condition is false."""
    if not cond:
        raise RuntimeError(message)


# -------- Core pricing & FX tools --------

def test_get_product_snapshot():
    """Run a basic functional check for get_product_snapshot and print a short preview."""
    print("\n" + "=" * 80)
    print("[1] get_product_snapshot()")
    print("=" * 80 + "\n")

    result = get_product_snapshot(
        product_name="Apple MacBook Pro 16 M3 Max",
        category="laptop",
        region="US",
        base_currency="USD",
    )
    _check(isinstance(result, dict), "get_product_snapshot must return dict")
    _check(bool(result), "get_product_snapshot returned empty dict")
    print(json.dumps(result, indent=2)[:400])
    print("\n✔️ get_product_snapshot OK\n")


def test_get_competitor_price_snapshot():
    """Run a basic functional check for get_competitor_price_snapshot and print a preview."""
    print("\n" + "=" * 80)
    print("[2] get_competitor_price_snapshot()")
    print("=" * 80 + "\n")

    result = get_competitor_price_snapshot(
        product_name="Apple MacBook Pro 16 M3 Max",
        region="US",
        currency="USD",
    )
    _check(isinstance(result, dict), "get_competitor_price_snapshot must return dict")
    _check(bool(result), "get_competitor_price_snapshot returned empty dict")
    print(json.dumps(result, indent=2)[:400])
    print("\n✔️ get_competitor_price_snapshot OK\n")


def test_calculate_fx_impact_scenarios():
    """Run a basic functional check for calculate_fx_impact_scenarios."""
    print("\n" + "=" * 80)
    print("[3] calculate_fx_impact_scenarios()")
    print("=" * 80 + "\n")

    result = calculate_fx_impact_scenarios(
        purchase_price=17000.0,
        purchase_currency="CNY",
        target_currency="USD",
        current_fx_rate=0.14,
        fx_shocks=[-0.1, 0.0, 0.1],
        volume_units=300,
    )
    _check(isinstance(result, dict), "calculate_fx_impact_scenarios must return dict")
    _check(bool(result), "calculate_fx_impact_scenarios returned empty dict")
    print(json.dumps(result, indent=2)[:400])
    print("\n✔️ calculate_fx_impact_scenarios OK\n")


def test_plan_margin_scenarios():
    """Run a basic functional check for plan_margin_scenarios using an FX scenario as input."""
    print("\n" + "=" * 80)
    print("[4] plan_margin_scenarios()")
    print("=" * 80 + "\n")

    fx_result = calculate_fx_impact_scenarios(
        purchase_price=17000.0,
        purchase_currency="CNY",
        target_currency="USD",
        current_fx_rate=0.14,
        fx_shocks=[0.0],
        volume_units=300,
    )

    unit_cost = fx_result["purchase_price"] * fx_result["current_fx_rate"]

    candidate_prices = [
        unit_cost * 1.1,
        unit_cost * 1.2,
        unit_cost * 1.3,
    ]

    result = plan_margin_scenarios(
        unit_cost=unit_cost,
        candidate_prices=candidate_prices,
        target_margin_pct=0.25,
    )
    _check(isinstance(result, dict), "plan_margin_scenarios must return dict")
    _check(bool(result), "plan_margin_scenarios returned empty dict")
    print(json.dumps(result, indent=2)[:400])
    print("\n✔️ plan_margin_scenarios OK\n")


def test_build_pricing_recommendation():
    """Run a basic functional check for build_pricing_recommendation with synthetic inputs."""
    print("\n" + "=" * 80)
    print("[5] build_pricing_recommendation()")
    print("=" * 80 + "\n")

    product_snapshot = get_product_snapshot(
        product_name="Apple MacBook Pro 16 M3 Max",
        category="laptop",
        region="US",
        base_currency="USD",
    )

    competitor_snapshot = get_competitor_price_snapshot(
        product_name="Apple MacBook Pro 16 M3 Max",
        region="US",
        currency="USD",
    )

    fx_result = calculate_fx_impact_scenarios(
        purchase_price=17000.0,
        purchase_currency="CNY",
        target_currency="USD",
        current_fx_rate=0.14,
        fx_shocks=[-0.1, 0.0, 0.1],
        volume_units=300,
    )

    unit_cost = fx_result["purchase_price"] * fx_result["current_fx_rate"]

    result = build_pricing_recommendation(
        unit_cost=unit_cost,
        competitor_snapshot=competitor_snapshot,
        fx_scenarios=fx_result,
        target_margin_pct=0.25,
    )

    _check(isinstance(result, dict), "build_pricing_recommendation must return dict")
    _check(bool(result), "build_pricing_recommendation returned empty dict")
    print(json.dumps(result, indent=2)[:400])
    print("\n✔️ build_pricing_recommendation OK\n")


def run_all_core_tool_checks():
    """Run the test suite for core pricing and FX tools."""
    test_get_product_snapshot()
    test_get_competitor_price_snapshot()
    test_calculate_fx_impact_scenarios()
    test_plan_margin_scenarios()
    test_build_pricing_recommendation()


run_all_core_tool_checks()


# -------- Admin / observability tools --------

class SimpleMemory:
    """In-memory store of messages with timestamps for testing and tooling."""

    def __init__(self):
        """Initialize the memory store with an empty message list."""
        self.messages = []

    def clear(self):
        """Remove all stored messages from memory."""
        self.messages = []

    def add_message(self, role, content):
        """Append a new message with role, content, and timestamp to memory."""
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )


class SimpleLogger:
    """Minimal logger that records structured events into an in-memory list."""

    def __init__(self):
        """Initialize the logger with an empty log list."""
        self.logs = []

    def info(self, event, **kwargs):
        """Record an informational event with optional structured metadata."""
        self.logs.append({"event": event, "data": kwargs})


class SimpleAgent:
    """Lightweight stand-in agent used for testing tools and utilities."""

    def __init__(self):
        """Initialize the agent with memory, logger, feedback, and stats."""
        self.memory = SimpleMemory()
        self.logger = SimpleLogger()
        self.feedback = []
        self.performance_history = []
        self._stats = {
            "queries_processed": 0,
            "tools_called": 0,
            "avg_response_time": 0.0,
            "errors": 0,
            "memory_stats": {},
            "logger_stats": {},
        }

    def get_stats(self):
        """Return the current snapshot of internal agent statistics."""
        return self._stats

    def reset(self):
        """Reset memory, feedback, performance history and basic counters."""
        self.memory.clear()
        self.feedback = []
        self.performance_history = []
        self._stats["queries_processed"] = 0
        self._stats["tools_called"] = 0
        self._stats["errors"] = 0

    def run(self, question: str) -> str:
        """Return a simple text response used for testing agent-related utilities."""
        self._stats["queries_processed"] += 1
        return f"SimpleAgent response to: {question}"


agent = SimpleAgent()
CONFIG = {
    "model": "simple-model",
    "temperature": 0.3,
    "max_tokens": 2048,
}


def test_export_conversation_history():
    """Check export_conversation_history and preview the created file."""
    print("\n" + "=" * 80)
    print("[1] export_conversation_history()")
    print("=" * 80 + "\n")

    filename = "conversation_history_test.txt"
    result = export_conversation_history(filename=filename)
    _check(isinstance(result, str), "export_conversation_history must return str (filename)")
    _check(os.path.exists(result), "conversation history file was not created")
    with open(result, "r", encoding="utf-8") as f:
        preview = f.read(400)
    print(preview)
    print("\n✔️ export_conversation_history OK\n")


def test_export_agent_logs():
    """Check export_agent_logs and validate the JSON structure."""
    print("\n" + "=" * 80)
    print("[2] export_agent_logs()")
    print("=" * 80 + "\n")

    filename = "agent_logs_test.json"
    result = export_agent_logs(filename=filename)
    _check(isinstance(result, str), "export_agent_logs must return str (filename)")
    _check(os.path.exists(result), "agent logs file was not created")
    with open(result, "r", encoding="utf-8") as f:
        data = json.load(f)
    _check(isinstance(data, dict), "agent logs must be JSON object")
    print(json.dumps(data, indent=2)[:400])
    print("\n✔️ export_agent_logs OK\n")


def test_reset_agent():
    """Check reset_agent and print the returned stats snapshot."""
    print("\n" + "=" * 80)
    print("[3] reset_agent()")
    print("=" * 80 + "\n")

    result = reset_agent()
    _check(isinstance(result, dict), "reset_agent must return dict")
    _check("previous_stats" in result, "reset_agent result must contain previous_stats")
    print(json.dumps(result, indent=2)[:400])
    print("\n✔️ reset_agent OK\n")


def test_search_conversation():
    """Check search_conversation and inspect the first result."""
    print("\n" + "=" * 80)
    print("[4] search_conversation()")
    print("=" * 80 + "\n")

    results = search_conversation("feature")
    _check(isinstance(results, list), "search_conversation must return list")
    if results:
        _check(isinstance(results[0], dict), "search_conversation items must be dict")
        print(json.dumps(results[0], indent=2)[:400])
    else:
        print("No messages found for keyword (this is still OK for this check).")
    print("\n✔️ search_conversation OK\n")


def test_configure_and_show_agent_config():
    """Check configure_agent and show_agent_config."""
    print("\n" + "=" * 80)
    print("[5] configure_agent() + show_agent_config()")
    print("=" * 80 + "\n")

    result = configure_agent(
        temperature=0.3,
        max_tokens=2048,
        model_name=CONFIG.get("model", "placeholder-model"),
    )
    _check(isinstance(result, dict), "configure_agent must return dict")
    config_snapshot = show_agent_config()
    _check(isinstance(config_snapshot, dict), "show_agent_config must return dict")
    _check("model" in config_snapshot, "config snapshot must contain model")
    print(json.dumps(config_snapshot, indent=2)[:400])
    print("\n✔️ configure_agent + show_agent_config OK\n")


def test_batch_query_and_display_results():
    """Check batch_query and display_batch_results."""
    print("\n" + "=" * 80)
    print("[6] batch_query() + display_batch_results()")
    print("=" * 80 + "\n")

    questions = [
        "Give me one short tip for feature engineering.",
        "What is overfitting in simple terms?",
    ]
    batch_result = batch_query(questions)
    _check(isinstance(batch_result, dict), "batch_query must return dict")
    _check("results" in batch_result, "batch_query result must contain 'results'")
    results = batch_result["results"]
    _check(isinstance(results, dict), "'results' must be a dict")
    entries = display_batch_results(results)
    _check(isinstance(entries, list), "display_batch_results must return list")
    if entries:
        print(json.dumps(entries[0], indent=2)[:400])
    print("\n✔️ batch_query + display_batch_results OK\n")


def test_summarize_conversation_and_auto_summarize():
    """Check summarize_conversation and auto_summarize_if_needed."""
    print("\n" + "=" * 80)
    print("[7] summarize_conversation() + auto_summarize_if_needed()")
    print("=" * 80 + "\n")

    summary = summarize_conversation()
    _check(isinstance(summary, dict), "summarize_conversation must return dict")
    print(json.dumps(summary, indent=2)[:400])
    auto_result = auto_summarize_if_needed()
    _check(isinstance(auto_result, dict), "auto_summarize_if_needed must return dict")
    print(json.dumps(auto_result, indent=2)[:400])
    print("\n✔️ summarize_conversation + auto_summarize_if_needed OK\n")


def test_collect_feedback_and_show_feedback_summary():
    """Check collect_feedback and show_feedback_summary."""
    print("\n" + "=" * 80)
    print("[8] collect_feedback() + show_feedback_summary()")
    print("=" * 80 + "\n")

    fb_entry = collect_feedback(
        question="How to improve my Kaggle solution?",
        response="You can try feature engineering and cross-validation.",
        rating=5,
        comments="Very helpful response",
    )
    _check(isinstance(fb_entry, dict), "collect_feedback must return dict")
    summary = show_feedback_summary()
    _check(isinstance(summary, dict), "show_feedback_summary must return dict")
    print(json.dumps(summary, indent=2)[:400])
    print("\n✔️ collect_feedback + show_feedback_summary OK\n")


def test_validate_and_auto_validate_response():
    """Check validate_response and auto_validate_response."""
    print("\n" + "=" * 80)
    print("[9] validate_response() + auto_validate_response()")
    print("=" * 80 + "\n")

    question = "Explain cross-validation in ML."
    response = (
        "Cross-validation is a way to estimate model performance. "
        "For example, you can split the data into k folds, train on k-1 folds "
        "and validate on the remaining fold. This helps reduce overfitting."
    )
    validation = validate_response(question, response)
    _check(isinstance(validation, dict), "validate_response must return dict")
    print(json.dumps(validation, indent=2)[:400])
    auto_validation = auto_validate_response(question, response)
    _check(isinstance(auto_validation, dict), "auto_validate_response must return dict")
    print(json.dumps(auto_validation, indent=2)[:400])
    print("\n✔️ validate_response + auto_validate_response OK\n")


def test_track_performance_and_show_trends():
    """Check track_performance_metrics and show_performance_trends."""
    print("\n" + "=" * 80)
    print("[10] track_performance_metrics() + show_performance_trends()")
    print("=" * 80 + "\n")

    metrics = track_performance_metrics()
    _check(isinstance(metrics, dict), "track_performance_metrics must return dict")
    print(json.dumps(metrics, indent=2)[:400])
    trends = show_performance_trends()
    _check(isinstance(trends, dict), "show_performance_trends must return dict")
    print(json.dumps(trends, indent=2)[:400])
    print("\n✔️ track_performance_metrics + show_performance_trends OK\n")


def test_export_performance_data():
    """Check export_performance_data and validate the JSON list structure."""
    print("\n" + "=" * 80)
    print("[11] export_performance_data()")
    print("=" * 80 + "\n")

    filename = "performance_data_test.json"
    result = export_performance_data(filename=filename)
    _check(isinstance(result, str), "export_performance_data must return str (filename)")
    _check(os.path.exists(result), "performance data file was not created")
    with open(result, "r", encoding="utf-8") as f:
        data = json.load(f)
    _check(isinstance(data, list), "performance data must be a JSON list")
    print(json.dumps(data, indent=2)[:400])
    print("\n✔️ export_performance_data OK\n")


def run_all_admin_tool_checks():
    """Run the test suite for admin and observability-oriented tools."""
    test_export_conversation_history()
    test_export_agent_logs()
    test_reset_agent()
    test_search_conversation()
    test_configure_and_show_agent_config()
    test_batch_query_and_display_results()
    test_summarize_conversation_and_auto_summarize()
    test_collect_feedback_and_show_feedback_summary()
    test_validate_and_auto_validate_response()
    test_track_performance_and_show_trends()
    test_export_performance_data()


run_all_admin_tool_checks()
