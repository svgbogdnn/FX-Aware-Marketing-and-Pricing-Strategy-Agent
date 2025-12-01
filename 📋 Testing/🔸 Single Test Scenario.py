single_test_config = {
    "product_name": "Apple MacBook Pro 16 M3 Max",
    "category": "laptop",
    "region": "US",
    "reporting_currency": "USD",
    "purchase_price": 17000.0,
    "purchase_currency": "CNY",
    "volume_units": 300,
    "current_or_planned_price": 3499.0,
    "target_margin_pct": 0.28,
    "manager_notes": "High-end MacBook Pro launch in US market.",
    "user_id": "orchestrator-single-test-mac",
}

single_run = await test_fx_pricing_orchestrator_once(single_test_config)
    
print("🔹 Decision brief 🔹")
print(single_run["result"]["decision_brief_text"])
print()

print("🔹 Structured summary JSON 🔹")
print(single_run["result"]["structured_summary_json"])
print()

print("🔹 Evaluation JSON 🔹")
print(single_run["result"]["evaluation_json"])
print()

print("🔹 Observability summary 🔹")
print(single_run["observability_summary"])
print()

print("🔹 Basic health 🔹")
print(single_run["health_basic"])

# Test for memory [EXAMPLE]

iphone_summary = FX_MEMORY.consolidate_recent_sessions(
    product_name="Apple MacBook Pro 16 M3 Max",
    region="US",
    max_sessions=10,
)

print("=== Consolidated memory for Apple MacBook Pro 16 M3 Max ===")
print(iphone_summary)
