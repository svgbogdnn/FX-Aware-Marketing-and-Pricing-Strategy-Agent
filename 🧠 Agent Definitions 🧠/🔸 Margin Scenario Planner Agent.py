from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from google.genai import types


margin_scenario_planner_agent = Agent(
    model=model,
    name="margin_scenario_planner_agent",
    description=(
        "Agent that plans margin and pricing scenarios by combining unit cost, "
        "candidate price points, and competitor benchmarks into a structured recommendation."
    ),
    instruction=(
        "You are a pricing and margin planning analyst.\n\n"
        "Your task is to help a marketing or procurement manager understand how margin changes "
        "across different price points, and to propose a small set of recommended strategies.\n\n"
        "You have access to two internal tools:\n"
        "1) plan_margin_scenarios: computes margin percentages and absolute margins for a list of candidate prices.\n"
        "2) build_pricing_recommendation: combines competitor prices and unit cost into a synthesized\n"
        "   recommended price and rationale.\n\n"
        "Always follow this workflow:\n"
        "1) Use plan_margin_scenarios to evaluate margin for the candidate prices provided by the caller.\n"
        "2) If a competitor snapshot is provided, use build_pricing_recommendation to derive a recommended\n"
        "   anchor price and understand where it sits versus competitors.\n"
        "3) From the margin scenarios and competitor context, derive a small set of recommended strategies,\n"
        "   such as:\n"
        "   - 'Match lower band of market, accept lower margin for volume',\n"
        "   - 'Stay at mid-market with target margin',\n"
        "   - 'Take a modest premium with clear differentiation'.\n"
        "4) Clearly explain trade-offs between margin and competitiveness.\n\n"
        "Your response must have two parts:\n"
        "A) A narrative summary (2–4 paragraphs) that explains:\n"
        "   - which candidate prices were evaluated,\n"
        "   - where the margin looks weak or strong,\n"
        "   - how your recommendations balance margin vs. price positioning.\n"
        "B) A JSON block with the following structure:\n"
        "   {\n"
        '     \"unit_cost\": float,\n'
        '     \"currency\": str,\n'
        '     \"candidate_prices\": [float],\n'
        '     \"target_margin_pct\": float | null,\n'
        '     \"margin_scenarios\": [\n'
        "       {\n"
        '         \"price\": float,\n'
        '         \"margin_pct\": float | null,\n'
        '         \"margin_absolute\": float | null,\n'
        '         \"meets_target\": bool\n'
        "       }\n"
        "     ],\n"
        '     \"competitor_summary\": {\n'
        '       \"competitor_min\": float | null,\n'
        '       \"competitor_mean\": float | null,\n'
        '       \"competitor_max\": float | null\n'
        "     },\n"
        '     \"recommended_strategies\": [\n'
        "       {\n"
        '         \"label\": str,\n'
        '         \"recommended_price\": float,\n'
        '         \"rationale\": str\n'
        "       }\n"
        "     ]\n"
        "   }\n\n"
        "If no competitor data is provided, still compute margin scenarios and propose strategies based only on\n"
        "unit cost and target margin. Be explicit about this limitation in the narrative.\n"
        "Do not claim that any of the numbers come from live systems; they are synthetic planning values."
    ),
    tools=[
        FunctionTool(plan_margin_scenarios),
        FunctionTool(build_pricing_recommendation),
    ],
)


margin_scenario_planner_tool = AgentTool(margin_scenario_planner_agent)


def build_margin_scenario_prompt(
    unit_cost: float,
    currency: str,
    candidate_prices: List[float],
    target_margin_pct: Optional[float] = None,
    has_competitor_snapshot: bool = True,
) -> str:
    """
    Build a consistent user prompt for the margin_scenario_planner_agent.

    Args:
        unit_cost: Landed cost per unit in the reporting currency.
        currency: Reporting currency (e.g., 'USD').
        candidate_prices: List of candidate selling prices to evaluate.
        target_margin_pct: Optional target margin fraction (e.g., 0.25 for 25%).
        has_competitor_snapshot: Flag indicating whether a competitor snapshot is available
            and will be provided as tool input via the orchestration layer.

    Returns:
        A formatted prompt string for the agent.
    """
    margin_line = (
        f"- Target margin: {target_margin_pct * 100:.1f}%\n"
        if target_margin_pct is not None
        else "- Target margin: not explicitly specified\n"
    )

    competitor_line = (
        "- Competitor snapshot: will be provided via tools.\n"
        if has_competitor_snapshot
        else "- Competitor snapshot: not available; base recommendations on unit cost and margins only.\n"
    )

    prices_str = ", ".join(f"{p:.2f}" for p in candidate_prices)

    return (
        "Plan pricing and margin scenarios for the following context:\n"
        f"- Unit cost: {unit_cost:.4f} {currency}\n"
        f"- Candidate selling prices: [{prices_str}] {currency}\n"
        f"{margin_line}"
        f"{competitor_line}\n"
        "Use your tools to compute margin scenarios and, if competitor data is available, "
        "to derive a pricing recommendation relative to the market. Then produce a narrative summary "
        "and a JSON block following the schema described in your instructions."
    )

print("✔️ Margin Scenario Planner Agent installed!")
