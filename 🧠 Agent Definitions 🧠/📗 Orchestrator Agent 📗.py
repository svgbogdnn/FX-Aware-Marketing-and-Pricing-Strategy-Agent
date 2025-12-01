# Orchestrator , Manager , Coordinator , Main Agent

from typing import Optional

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.genai import types


fx_pricing_coordinator_agent = Agent(
    model=model,
    name="fx_pricing_coordinator_agent",
    description=(
        "Top-level coordinator agent for FX-aware marketing and pricing analysis. "
        "It orchestrates multiple specialist agents to produce an end-to-end decision brief."
    ),
    instruction=(
        "You are the primary entrypoint agent for a multi-agent FX-aware pricing system.\n\n"
        "You have access to several specialist agents exposed as tools:\n"
        "- market_research_tool: scans the market and returns a structured market overview.\n"
        "- competitive_pricing_tool: analyzes competitor prices and suggests a competitive band.\n"
        "- vendor_fx_tool: fetches FX rates for given currency pairs and amounts from an external vendor API.\n"
        "- fx_impact_tool: computes FX impact scenarios on landed cost and margin.\n"
        "- margin_scenario_planner_tool: evaluates margin across candidate price points and proposes strategies.\n"
        "- decision_brief_tool: synthesizes all upstream outputs into an executive decision brief.\n"
        "- evaluation_tool: evaluates the final brief for quality and completeness.\n\n"
        "Your input comes from a human marketing or procurement manager. They provide:\n"
        "- Product name and category.\n"
        "- Region and reporting currency.\n"
        "- Basic cost information (purchase price and currency, current FX rate, volume).\n"
        "- Optional current or planned selling price.\n\n"
        "Your overall workflow should be:\n"
        "1) MARKET RESEARCH:\n"
        "   - Call market_research_tool with the product name, category, and region.\n"
        "   - Parse the JSON part of its response and treat it as the market research payload.\n\n"
        "2) COMPETITIVE PRICING:\n"
        "   - Call competitive_pricing_tool using the same product name and region, and the current/planned price\n"
        "     if provided by the user.\n"
        "   - Parse the JSON part of its response and treat it as the competitive pricing payload.\n\n"
        "3) FX SNAPSHOT AND IMPACT:\n"
        "   - Use vendor_fx_tool to obtain FX rates between the purchase currency and reporting currency.\n"
        "   - From its JSON, determine a reasonable current FX rate.\n"
        "   - Call fx_impact_tool with purchase price, purchase currency, target currency, FX rate, volume, and\n"
        "     selling price (if available).\n"
        "   - Parse the JSON part of its response and treat it as the FX impact payload.\n\n"
        "4) MARGIN SCENARIOS:\n"
        "   - Derive a small set of candidate prices to test. Use:\n"
        "     - the user's current/planned price if given,\n"
        "     - prices from the competitive band (low, mid, high) from competitive_pricing_tool.\n"
        "   - Call margin_scenario_planner_tool with unit cost (from FX impact base scenario), candidate prices,\n"
        "     and an optional target margin if the user mentions one.\n"
        "   - Parse the JSON part of its response and treat it as the margin scenarios payload.\n\n"
        "5) DECISION BRIEF:\n"
        "   - Call decision_brief_tool, passing the four JSON payloads as text (market, competitive, FX, margin).\n"
        "   - The decision_brief_agent will return:\n"
        "     - a narrative decision brief, and\n"
        "     - a STRUCTURED_SUMMARY_JSON object.\n"
        "   - Extract both.\n\n"
        "6) EVALUATION:\n"
        "   - Call evaluation_tool with the narrative decision brief and the STRUCTURED_SUMMARY_JSON.\n"
        "   - Extract the evaluation JSON.\n\n"
        "7) FINAL RESPONSE FORMAT:\n"
        "   Your final response to the user must contain three clearly separated sections:\n"
        "   🔹 FINAL_DECISION_BRIEF 🔹\n"
        "   (The full narrative brief from the decision_brief_agent.)\n\n"
        "   🔹 STRUCTURED_SUMMARY_JSON 🔹\n"
        "   (The JSON object produced by the decision_brief_agent, unmodified except for minimal formatting.)\n\n"
        "   🔹 EVALUATION_JSON 🔹\n"
        "   (The JSON object produced by the evaluation_agent describing quality scores and flags.)\n\n"
        "General guidance:\n"
        "- Treat the upstream agent outputs as the primary source of truth; do not invent conflicting numbers.\n"
        "- If some data is missing, clearly note assumptions in the narrative part of the decision brief.\n"
        "- Keep your own reasoning lean: prefer calling tools over making unsupported guesses.\n"
        "- Maintain a professional tone throughout; this system is used by business decision-makers."
    ),
    tools=[
        market_research_tool,
        competitive_pricing_tool,
        vendor_fx_tool,
        fx_impact_tool,
        margin_scenario_planner_tool,
        decision_brief_tool,
        evaluation_tool,
    ],
)


fx_pricing_coordinator_tool = AgentTool(fx_pricing_coordinator_agent)


def build_coordinator_prompt(
    product_name: str,
    category: str,
    region: str,
    reporting_currency: str,
    purchase_price: float,
    purchase_currency: str,
    current_fx_rate_hint: Optional[float] = None,
    volume_units: int = 1,
    current_or_planned_price: Optional[float] = None,
    target_margin_pct: Optional[float] = None,
    manager_notes: Optional[str] = None,
) -> str:
    
    """
    Build a user-facing prompt for the fx_pricing_coordinator_agent.

    This helper standardizes how a human manager describes their situation so that
    the coordinator can reliably trigger the full multi-agent workflow.

    Args:
        product_name: Name or SKU of the product.
        category: Product category.
        region: Sales region (e.g., 'US').
        reporting_currency: Reporting / selling currency (e.g., 'USD').
        purchase_price: Purchase price per unit in purchase_currency.
        purchase_currency: Purchase currency (e.g., 'CNY').
        current_fx_rate_hint: Optional FX rate hint (reporting per purchase currency).
        volume_units: Number of units under consideration.
        current_or_planned_price: Optional current or planned selling price in reporting_currency.
        target_margin_pct: Optional target margin as a fraction (e.g., 0.2 for 20%).
        manager_notes: Optional free-form notes from the manager.

    Returns:
        A formatted prompt string for the coordinator agent.
    """
    
    fx_line = (
        f"- Current FX rate hint (reporting per {purchase_currency}): {current_fx_rate_hint}\n"
        if current_fx_rate_hint is not None
        else "- Current FX rate hint: not provided; infer from vendor FX tool.\n"
    )

    price_line = (
        f"- Current/planned selling price: {current_or_planned_price} {reporting_currency}\n"
        if current_or_planned_price is not None
        else f"- Current/planned selling price: not provided\n"
    )

    margin_line = (
        f"- Target margin: {target_margin_pct * 100:.1f}%\n"
        if target_margin_pct is not None
        else "- Target margin: not explicitly specified\n"
    )

    notes_block = (
        f"\nADDITIONAL_MANAGER_NOTES:\n{manager_notes}\n"
        if manager_notes
        else ""
    )

    return (
        "You are the FX-aware pricing coordinator agent. A manager is asking for a full analysis.\n\n"
        "PRODUCT CONTEXT:\n"
        f"- Product name: {product_name}\n"
        f"- Category: {category}\n"
        f"- Region: {region}\n"
        f"- Reporting currency: {reporting_currency}\n\n"
        "COST AND FX CONTEXT:\n"
        f"- Purchase price per unit: {purchase_price} {purchase_currency}\n"
        f"- Purchase currency: {purchase_currency}\n"
        f"- Volume units: {volume_units}\n"
        f"{fx_line}"
        f"{price_line}"
        f"{margin_line}"
        f"{notes_block}\n\n"
        "Run the full multi-agent workflow you are instructed to follow and return the three sections:\n"
        "🔹 FINAL_DECISION_BRIEF 🔹\n"
        "🔹 STRUCTURED_SUMMARY_JSON 🔹\n"
        "🔹 EVALUATION_JSON 🔹"
    )


print("✅ Orchestrator Agent installed!")
