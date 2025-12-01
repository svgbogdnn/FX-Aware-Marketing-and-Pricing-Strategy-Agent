from google.adk.runners import InMemoryRunner
from google.genai import types
MAX_PREVIEW_CHARS = 300



# 1) Market Research Agent
print("\n" + "=" * 80)
print("[1] Market Research Agent")
print("=" * 80 + "\n")

runner = InMemoryRunner(
    agent=market_research_agent,
    app_name=APP_NAME,
)

session = await runner.session_service.create_session(
    app_name=APP_NAME,
    user_id="test-user",
)

prompt = build_market_research_prompt(
    product_name="Apple Iphone 17 Air",
    category="smartphone",
    region="US",
)

content = types.Content(
    role="user",
    parts=[types.Part.from_text(text=prompt)],
)

chunks = []
for event in runner.run(
    user_id="test-user",
    session_id=session.id,
    new_message=content,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)

full_text = "".join(chunks)
print(full_text[:MAX_PREVIEW_CHARS])



# 2) Competitive Pricing Agent
print("\n" + "=" * 80)
print("[2] Competitive Pricing Agent")
print("=" * 80 + "\n")

runner = InMemoryRunner(
    agent=competitive_pricing_agent,
    app_name=APP_NAME,
)

session = await runner.session_service.create_session(
    app_name=APP_NAME,
    user_id="test-user",
)

prompt = build_competitive_pricing_prompt(
    product_name="Apple iPhone 17 Air",
    region="US",
    currency="USD",
    our_price=999.0,
)

content = types.Content(
    role="user",
    parts=[types.Part.from_text(text=prompt)],
)

chunks = []
for event in runner.run(
    user_id="test-user",
    session_id=session.id,
    new_message=content,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)

full_text = "".join(chunks)
print(full_text[:MAX_PREVIEW_CHARS])



# 3) Vendor FX Agent
print("\n" + "=" * 80)
print("[3] Vendor FX Agent")
print("=" * 80 + "\n")

runner = InMemoryRunner(
    agent=vendor_fx_agent,
    app_name=APP_NAME,
)

session = await runner.session_service.create_session(
    app_name=APP_NAME,
    user_id="test-user",
)

prompt = build_vendor_fx_prompt(
    base_currency="CNY",
    target_currencies=["USD", "EUR"],
    amount=1000.0,
)

content = types.Content(
    role="user",
    parts=[types.Part.from_text(text=prompt)],
)

chunks = []
for event in runner.run(
    user_id="test-user",
    session_id=session.id,
    new_message=content,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)

full_text = "".join(chunks)
print(full_text[:MAX_PREVIEW_CHARS])



# 4) FX Impact Agent
print("\n" + "=" * 80)
print("[4] FX Impact Agent")
print("=" * 80 + "\n")

runner = InMemoryRunner(
    agent=fx_impact_agent,
    app_name=APP_NAME,
)

session = await runner.session_service.create_session(
    app_name=APP_NAME,
    user_id="test-user",
)

prompt = build_fx_impact_prompt(
    purchase_price=800.0,
    purchase_currency="CNY",
    target_currency="USD",
    current_fx_rate=0.14,
    volume_units=1000,
    selling_price=1199.0,
    fx_shocks=[-0.1, 0.0, 0.1],
)

content = types.Content(
    role="user",
    parts=[types.Part.from_text(text=prompt)],
)

chunks = []
for event in runner.run(
    user_id="test-user",
    session_id=session.id,
    new_message=content,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)

full_text = "".join(chunks)
print(full_text[:MAX_PREVIEW_CHARS])



# 5) Margin Scenario Planner Agent
print("\n" + "=" * 80)
print("[5] Margin Scenario Planner Agent")
print("=" * 80 + "\n")

runner = InMemoryRunner(
    agent=margin_scenario_planner_agent,
    app_name=APP_NAME,
)

session = await runner.session_service.create_session(
    app_name=APP_NAME,
    user_id="test-user",
)

prompt = build_margin_scenario_prompt(
    unit_cost=750.0,
    currency="USD",
    candidate_prices=[899.0, 999.0, 1099.0, 1199.0],
    target_margin_pct=0.25,
    has_competitor_snapshot=False,
)

content = types.Content(
    role="user",
    parts=[types.Part.from_text(text=prompt)],
)

chunks = []
for event in runner.run(
    user_id="test-user",
    session_id=session.id,
    new_message=content,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)

full_text = "".join(chunks)
print(full_text[:MAX_PREVIEW_CHARS])



# 6) Decision Brief Agent
print("\n" + "=" * 80)
print("[6] Decision Brief Agent")
print("=" * 80 + "\n")

runner = InMemoryRunner(
    agent=decision_brief_agent,
    app_name=APP_NAME,
)

session = await runner.session_service.create_session(
    app_name=APP_NAME,
    user_id="test-user",
)

dummy_market_json = '{"product_name": "Apple iPhone 17 Air", "region": "US", "currency": "USD", "key_competitors": [{"name": "Samsung Galaxy S26", "positioning": "premium", "notes": "flagship Android competitor"}], "typical_price_band": {"currency": "USD", "low": 799.0, "high": 1399.0}, "key_features": ["5G", "OLED", "triple camera"]}'
dummy_competitive_json = '{"product_name": "Apple iPhone 17 Air", "region": "US", "currency": "USD", "our_price": 1099.0, "competitor_offers": [{"name": "Samsung Galaxy S26", "price": 999.0, "currency": "USD", "is_promo": false, "promo_label": null}], "suggested_competitive_band": {"low": 999.0, "high": 1299.0}}'
dummy_fx_json = '{"purchase_price": 800.0, "purchase_currency": "CNY", "target_currency": "USD", "current_fx_rate": 0.14, "selling_price": 1099.0, "volume_units": 1000, "scenarios": []}'
dummy_margin_json = '{"unit_cost": 820.0, "currency": "USD", "candidate_prices": [999.0, 1099.0, 1199.0], "target_margin_pct": 0.25, "margin_scenarios": [], "competitor_summary": {"competitor_min": 899.0, "competitor_mean": 1049.0, "competitor_max": 1299.0}, "recommended_strategies": []}'

prompt = build_decision_brief_prompt(
    product_name="Apple iPhone 17 Air",
    region="US",
    currency="USD",
    market_research_json=dummy_market_json,
    competitive_pricing_json=dummy_competitive_json,
    fx_impact_json=dummy_fx_json,
    margin_scenarios_json=dummy_margin_json,
    additional_notes="Synthetic test of decision_brief_agent.",
)

content = types.Content(
    role="user",
    parts=[types.Part.from_text(text=prompt)],
)

chunks = []
for event in runner.run(
    user_id="test-user",
    session_id=session.id,
    new_message=content,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)

full_text = "".join(chunks)
print(full_text[:MAX_PREVIEW_CHARS])



# 7) Evaluation Agent
print("\n" + "=" * 80)
print("[7] Evaluation Agent")
print("=" * 80 + "\n")

runner = InMemoryRunner(
    agent=evaluation_agent,
    app_name=APP_NAME,
)

session = await runner.session_service.create_session(
    app_name=APP_NAME,
    user_id="test-user",
)

dummy_decision_text = (
    "This is a synthetic decision brief for Apple iPhone 17 Air. "
    "It summarizes the flagship smartphone market in the US, competitive pricing, "
    "FX exposure on CNY-based purchasing, and recommends a mid-to-premium price point."
)

dummy_structured_json = '{"product_name": "Apple iPhone 17 Air", "region": "US", "currency": "USD", "market_summary": {"key_competitors": [{"name": "Samsung Galaxy S26", "positioning": "premium"}], "typical_price_band": {"low": 799.0, "high": 1399.0}}, "competitive_position": {"our_price": 1099.0, "band_relation": "within_band", "notable_risks": ["price slightly above main Android competitor"]}, "fx_risk": {"scenarios": [{"label": "base", "margin_pct": 0.22, "note": "current FX"}, {"label": "pessimistic", "margin_pct": 0.15, "note": "CNY strengthens"}, {"label": "optimistic", "margin_pct": 0.28, "note": "CNY weakens"}]}, "recommended_pricing": {"recommended_price": 1099.0, "strategy_label": "mid_premium", "key_rationale": ["aligns with flagship positioning", "keeps some margin buffer vs FX risk"]}}'

prompt = build_evaluation_prompt(
    decision_brief_text=dummy_decision_text,
    structured_summary_json=dummy_structured_json,
    context_notes="Synthetic unit test of evaluation_agent.",
)

content = types.Content(
    role="user",
    parts=[types.Part.from_text(text=prompt)],
)

chunks = []
for event in runner.run(
    user_id="test-user",
    session_id=session.id,
    new_message=content,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)

full_text = "".join(chunks)
print(full_text[:MAX_PREVIEW_CHARS])
