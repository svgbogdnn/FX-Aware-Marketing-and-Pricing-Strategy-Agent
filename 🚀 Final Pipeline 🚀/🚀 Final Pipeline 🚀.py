import json
import re
import time

from google.adk.runners import InMemoryRunner
from google.genai import types


def _extract_json_block(text: str) -> str:
    match = list(re.finditer(r"```json(.*?)```", text, re.S))
    if match:
        block = match[-1].group(1)
        return block.strip()
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first:last + 1].strip()
    return "{}"


def _split_text_and_json(text: str):
    if "```json" in text:
        head, _, tail = text.partition("```json")
        json_part = _extract_json_block("```json" + tail)
        return head.strip(), json_part
    return text.strip(), "{}"


async def _run_single_agent(
    agent,
    prompt: str,
    app_name: str,
    user_id: str,
    obs_plugin=None,
):
    plugins = [obs_plugin] if obs_plugin is not None else []
    runner = InMemoryRunner(
        agent=agent,
        app_name=app_name,
        plugins=plugins,
    )
    
    session = await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
    )
    
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )
    
    chunks = []
    for event in runner.run(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                text = getattr(part, "text", None)
                if text:
                    chunks.append(text)
    return "".join(chunks)


async def run_full_fx_pricing_pipeline(
    product_name: str,
    category: str,
    region: str,
    reporting_currency: str,
    purchase_price: float,
    purchase_currency: str,
    volume_units: int,
    current_or_planned_price: float,
    target_margin_pct: float,
    manager_notes: str,
    user_id: str = "fx-manager",
):
    obs_plugin = FxObservabilityPlugin(
        log_prompts=False,
        log_responses=False,
    )

    previous_entry = FX_MEMORY.load_last_session(
        product_name=product_name,
        region=region,
    )

    history_note = ""
    if previous_entry is not None:
        history_note = (
            "Previous decision exists for this product and region. "
            f"Last run at {time.ctime(previous_entry.created_at_ts)}, "
            f"last notes: {previous_entry.manager_notes[:200]}"
        )

    combined_notes = manager_notes
    if history_note:
        combined_notes = manager_notes + " | Historical context: " + history_note

    user_id_effective = f"{user_id}:{product_name}:{region}"

    market_prompt = build_market_research_prompt(
        product_name=product_name,
        category=category,
        region=region,
    )
    
    market_output = await _run_single_agent(
        agent=market_research_agent,
        prompt=market_prompt,
        app_name=APP_NAME,
        user_id=user_id_effective,
        obs_plugin=obs_plugin,
    )
    
    market_research_json = _extract_json_block(market_output)

    competitive_prompt = build_competitive_pricing_prompt(
        product_name=product_name,
        region=region,
        currency=reporting_currency,
        our_price=current_or_planned_price,
    )
    
    competitive_output = await _run_single_agent(
        agent=competitive_pricing_agent,
        prompt=competitive_prompt,
        app_name=APP_NAME,
        user_id=user_id_effective,
        obs_plugin=obs_plugin,
    )
    
    competitive_pricing_json = _extract_json_block(competitive_output)

    vendor_prompt = build_vendor_fx_prompt(
        base_currency=purchase_currency,
        target_currencies=[reporting_currency],
        amount=purchase_price,
    )
    
    vendor_output = await _run_single_agent(
        agent=vendor_fx_agent,
        prompt=vendor_prompt,
        app_name=APP_NAME,
        user_id=user_id_effective,
        obs_plugin=obs_plugin,
    )
    
    vendor_fx_json = _extract_json_block(vendor_output)

    current_fx_rate = 0.14
    try:
        vendor_obj = json.loads(vendor_fx_json)
        if isinstance(vendor_obj, dict):
            if "rate" in vendor_obj and isinstance(vendor_obj["rate"], (int, float)):
                current_fx_rate = float(vendor_obj["rate"])
            elif "quotes" in vendor_obj and isinstance(vendor_obj["quotes"], list) and vendor_obj["quotes"]:
                q0 = vendor_obj["quotes"][0]
                if isinstance(q0, dict) and "rate" in q0 and isinstance(q0["rate"], (int, float)):
                    current_fx_rate = float(q0["rate"])
    except Exception:
        pass

    fx_prompt = build_fx_impact_prompt(
        purchase_price=purchase_price,
        purchase_currency=purchase_currency,
        target_currency=reporting_currency,
        current_fx_rate=current_fx_rate,
        volume_units=volume_units,
        selling_price=current_or_planned_price,
        fx_shocks=[-0.1, 0.0, 0.1],
    )
    
    fx_output = await _run_single_agent(
        agent=fx_impact_agent,
        prompt=fx_prompt,
        app_name=APP_NAME,
        user_id=user_id_effective,
        obs_plugin=obs_plugin,
    )
    
    fx_impact_json = _extract_json_block(fx_output)

    unit_cost_reporting = purchase_price * current_fx_rate
    candidate_prices = [
        round(current_or_planned_price * m, 2)
        for m in [0.95, 1.0, 1.05, 1.1]
    ]

    margin_prompt = build_margin_scenario_prompt(
        unit_cost=unit_cost_reporting,
        currency=reporting_currency,
        candidate_prices=candidate_prices,
        target_margin_pct=target_margin_pct,
        has_competitor_snapshot=True,
    )
    
    margin_output = await _run_single_agent(
        agent=margin_scenario_planner_agent,
        prompt=margin_prompt,
        app_name=APP_NAME,
        user_id=user_id_effective,
        obs_plugin=obs_plugin,
    )
    
    margin_scenarios_json = _extract_json_block(margin_output)

    decision_prompt = build_decision_brief_prompt(
        product_name=product_name,
        region=region,
        currency=reporting_currency,
        market_research_json=market_research_json,
        competitive_pricing_json=competitive_pricing_json,
        fx_impact_json=fx_impact_json,
        margin_scenarios_json=margin_scenarios_json,
        additional_notes=combined_notes,
    )
    
    decision_output = await _run_single_agent(
        agent=decision_brief_agent,
        prompt=decision_prompt,
        app_name=APP_NAME,
        user_id=user_id_effective,
        obs_plugin=obs_plugin,
    )
    
    decision_brief_text, structured_summary_json = _split_text_and_json(decision_output)

    evaluation_prompt = build_evaluation_prompt(
        decision_brief_text=decision_brief_text,
        structured_summary_json=structured_summary_json,
        context_notes=f"FX pricing evaluation for {product_name} in {region}.",
    )
    
    evaluation_output = await _run_single_agent(
        agent=evaluation_agent,
        prompt=evaluation_prompt,
        app_name=APP_NAME,
        user_id=user_id_effective,
        obs_plugin=obs_plugin,
    )
    
    evaluation_text, evaluation_json = _split_text_and_json(evaluation_output)

    FX_MEMORY.add_session_to_memory(
        product_name=product_name,
        region=region,
        reporting_currency=reporting_currency,
        manager_notes=manager_notes,
        market_research_json=market_research_json,
        competitive_pricing_json=competitive_pricing_json,
        fx_impact_json=fx_impact_json,
        margin_scenarios_json=margin_scenarios_json,
        decision_brief_text=decision_brief_text,
        structured_summary_json=structured_summary_json,
        evaluation_json=evaluation_json,
    )

    obs_summary = obs_plugin.get_summary()
    obs_detailed = obs_plugin.get_detailed_summary()

    return {
        "product_name": product_name,
        "region": region,
        "reporting_currency": reporting_currency,
        "decision_brief_text": decision_brief_text,
        "structured_summary_json": structured_summary_json,
        "evaluation_json": evaluation_json,
        "evaluation_text": evaluation_text,
        "market_research_json": market_research_json,
        "competitive_pricing_json": competitive_pricing_json,
        "fx_impact_json": fx_impact_json,
        "margin_scenarios_json": margin_scenarios_json,
        "vendor_fx_json": vendor_fx_json,
        "observability_summary": obs_summary,
        "observability_detailed": obs_detailed,
    }


print("✔️ FX pricing pipeline has been installed!")
