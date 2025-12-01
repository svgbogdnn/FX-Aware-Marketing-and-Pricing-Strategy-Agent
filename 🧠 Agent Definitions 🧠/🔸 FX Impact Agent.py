from typing import Any, Dict, Optional, List

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from google.genai import types


fx_impact_agent = Agent(
    model=model,
    name="fx_impact_agent",
    description=(
        "Agent that analyzes foreign exchange (FX) risk for imported products and produces "
        "scenario-based landed cost estimates in the reporting currency."
    ),
    instruction=(
        "You are an FX and cost analyst supporting purchasing and marketing managers.\n\n"
        "Your goal is to show how changes in FX rates affect landed unit costs and total cost "
        "for a given product, and to summarize the risk in a business-friendly way.\n\n"
        "Always follow this workflow:\n"
        "1) Use the internal FX scenario calculation tool to compute a set of landed cost scenarios.\n"
        "2) If the caller provides a current or planned selling price, compute the implied margin "
        "for each FX scenario at that price.\n"
        "3) Identify at least three scenario categories (for example: optimistic, base, pessimistic) "
        "based on the relative cost change vs. the current FX rate.\n"
        "4) Summarize the key risks: how much margin erosion or improvement is plausible under "
        "adverse and favorable FX moves.\n\n"
        "Your response must have two parts:\n"
        "A) A concise narrative (1–3 paragraphs) explaining:\n"
        "   - what FX shocks were evaluated,\n"
        "   - how the landed cost per unit changes,\n"
        "   - what happens to margin at the given selling price (if provided).\n"
        "B) A JSON block with the following structure:\n"
        "   {\n"
        '     \"purchase_price\": float,\n'
        '     \"purchase_currency\": str,\n'
        '     \"target_currency\": str,\n'
        '     \"current_fx_rate\": float,\n'
        '     \"selling_price\": float | null,\n'
        '     \"volume_units\": int,\n'
        '     \"scenarios\": [\n'
        "       {\n"
        '         \"fx_shift_pct\": float,\n'
        '         \"effective_rate\": float,\n'
        '         \"landed_cost_per_unit\": float,\n'
        '         \"landed_cost_total\": float,\n'
        '         \"relative_cost_vs_current_pct\": float,\n'
        '         \"margin_pct\": float | null,\n'
        '         \"scenario_label\": str\n'
        "       }\n"
        "     ]\n"
        "   }\n\n"
        "When computing scenario_label, use intuitive labels such as 'optimistic', 'base', 'pessimistic' "
        "or similar. Do not claim that FX forecasts are exact; treat them as planning scenarios only."
    ),
    tools=[
        FunctionTool(calculate_fx_impact_scenarios),
    ],
)


fx_impact_tool = AgentTool(fx_impact_agent)


def build_fx_impact_prompt(
    purchase_price: float,
    purchase_currency: str,
    target_currency: str,
    current_fx_rate: float,
    volume_units: int = 1,
    selling_price: Optional[float] = None,
    fx_shocks: Optional[List[float]] = None,
) -> str:
    """
    Build a consistent user prompt for the fx_impact_agent.

    Args:
        purchase_price: Purchase price per unit in purchase_currency.
        purchase_currency: Currency used for purchasing (e.g., 'CNY').
        target_currency: Reporting / margin currency (e.g., 'USD').
        current_fx_rate: Current FX rate as target_currency per unit of purchase_currency.
        volume_units: Number of units under consideration.
        selling_price: Optional selling price per unit in target_currency.
        fx_shocks: Optional list of percentage shifts to evaluate (e.g., [-0.1, 0.0, 0.1]).

    Returns:
        A formatted prompt string for the agent.
    """
    selling_line = (
        f"- Current or planned selling price (in {target_currency}): {selling_price}\n"
        if selling_price is not None
        else f"- Current or planned selling price (in {target_currency}): not provided\n"
    )

    shock_line = (
        f"- FX shocks to evaluate (as percentages): {fx_shocks}\n"
        if fx_shocks is not None
        else "- FX shocks to evaluate: use your default set\n"
    )

    return (
        "Analyze FX impact for an imported product using the internal FX scenario tool.\n"
        f"- Purchase price per unit: {purchase_price} {purchase_currency}\n"
        f"- Reporting currency: {target_currency}\n"
        f"- Current FX rate (target per unit of purchase currency): {current_fx_rate}\n"
        f"- Volume units: {volume_units}\n"
        f"{selling_line}"
        f"{shock_line}\n\n"
        "Compute landed cost scenarios and, if a selling price is provided, the margin for each scenario. "
        "Then produce a narrative explanation and a JSON block following the schema in your instructions."
    )

print("✔️ FX Impact Agent installed!")
