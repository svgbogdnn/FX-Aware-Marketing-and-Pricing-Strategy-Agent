from typing import Optional

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.genai import types


decision_brief_agent = Agent(
    model=model,
    name="decision_brief_agent",
    description=(
        "Agent that synthesizes market research, competitive pricing, FX impact, and margin scenarios "
        "into a single, executive-ready decision brief for marketing and procurement managers."
    ),
    instruction=(
        "You are a senior business analyst preparing an executive decision brief.\n\n"
        "You receive structured inputs from several other agents:\n"
        "- Market research summary (competitors, positioning, typical price band).\n"
        "- Competitive pricing analysis (competitor price table, our price vs band).\n"
        "- FX impact analysis (FX scenarios, landed cost changes, margin erosion or improvement).\n"
        "- Margin scenario planning (candidate prices, margin outcomes, recommended strategies).\n\n"
        "Your goal is to merge these inputs into a coherent, concise, and business-oriented brief that a busy\n"
        "marketing or procurement manager can read in a few minutes and immediately understand:\n"
        "1) What the current market looks like.\n"
        "2) How our pricing compares to competitors.\n"
        "3) What FX risk we are exposed to.\n"
        "4) What pricing strategy you recommend and why.\n\n"
        "Always produce your answer in two clearly separated sections:\n\n"
        "🔹 DECISION BRIEF 🔹\n"
        "Write 4–8 short paragraphs including:\n"
        "- A one-paragraph executive summary.\n"
        "- A market overview (key competitors, positioning, typical price band).\n"
        "- A competitive pricing view (where our price sits vs. the band; risks and opportunities).\n"
        "- An FX risk summary (how much margin could move under adverse and favorable scenarios).\n"
        "- A recommendation section (what price range and strategic posture you recommend).\n"
        "Use plain business English, avoid technical jargon, and call out concrete numbers when available.\n\n"
        "🔹 STRUCTURED_SUMMARY_JSON 🔹\n"
        "After the narrative, output a single JSON object with this structure, and nothing else in that section:\n"
        "{\n"
        "  \"product_name\": str | null,\n"
        "  \"region\": str | null,\n"
        "  \"currency\": str | null,\n"
        "  \"market_summary\": {\n"
        "    \"key_competitors\": [\n"
        "      {\"name\": str, \"positioning\": str}\n"
        "    ],\n"
        "    \"typical_price_band\": {\"low\": float | null, \"high\": float | null}\n"
        "  },\n"
        "  \"competitive_position\": {\n"
        "    \"our_price\": float | null,\n"
        "    \"band_relation\": str,\n"
        "    \"notable_risks\": [str]\n"
        "  },\n"
        "  \"fx_risk\": {\n"
        "    \"scenarios\": [\n"
        "      {\"label\": str, \"margin_pct\": float | null, \"note\": str}\n"
        "    ]\n"
        "  },\n"
        "  \"recommended_pricing\": {\n"
        "    \"recommended_price\": float | null,\n"
        "    \"strategy_label\": str,\n"
        "    \"key_rationale\": [str]\n"
        "  }\n"
        "}\n\n"
        "The caller will embed upstream agent outputs as text/JSON fragments in the prompt. Carefully read them,\n"
        "cross-check key numbers, and keep your narrative consistent with the provided data. If some information\n"
        "is missing or inconsistent, make reasonable, clearly-labeled assumptions, and note them explicitly in\n"
        "the narrative (for example: 'Assuming our target margin is around 20% based on scenario X').\n"
        "Do not claim that any numbers are real-time; treat them as internal planning values."
    ),
    tools=[],
)


decision_brief_tool = AgentTool(decision_brief_agent)


def build_decision_brief_prompt(
    product_name: Optional[str],
    region: Optional[str],
    currency: Optional[str],
    market_research_json: str,
    competitive_pricing_json: str,
    fx_impact_json: str,
    margin_scenarios_json: str,
    additional_notes: Optional[str] = None,
) -> str:
    """
    Build a consolidated prompt for the decision_brief_agent.

    The idea is that the orchestration layer passes the raw JSON outputs from the other agents
    (market research, competitive pricing, FX impact, margin scenarios) as text. This helper
    function stitches them into a single well-structured prompt that the decision_brief_agent
    can consume.

    Args:
        product_name: Optional product name for the brief header.
        region: Optional region identifier (e.g., 'US').
        currency: Optional reporting currency (e.g., 'USD').
        market_research_json: JSON string produced by the market_research_agent.
        competitive_pricing_json: JSON string produced by the competitive_pricing_agent.
        fx_impact_json: JSON string produced by the fx_impact_agent.
        margin_scenarios_json: JSON string produced by the margin_scenario_planner_agent.
        additional_notes: Optional free-form notes from the coordinator or user.

    Returns:
        A formatted prompt string for the decision_brief_agent.
    """
    header_name = product_name if product_name is not None else "unknown product"
    header_region = region if region is not None else "unspecified region"
    header_currency = currency if currency is not None else "unspecified currency"

    notes_block = (
        f"\nADDITIONAL_MANAGER_NOTES:\n{additional_notes}\n"
        if additional_notes
        else ""
    )

    return (
        f"You are preparing a consolidated decision brief for {header_name} in {header_region}, "
        f"with pricing and costs expressed in {header_currency}.\n\n"
        "Below you will find JSON payloads from upstream agents. Use them as your primary source of truth.\n\n"
        "MARKET_RESEARCH_JSON:\n"
        f"{market_research_json}\n\n"
        "COMPETITIVE_PRICING_JSON:\n"
        f"{competitive_pricing_json}\n\n"
        "FX_IMPACT_JSON:\n"
        f"{fx_impact_json}\n\n"
        "MARGIN_SCENARIOS_JSON:\n"
        f"{margin_scenarios_json}\n"
        f"{notes_block}\n"
        "Read all of this carefully and then produce the two sections requested in your instructions:\n"
        "1) 🔹 DECISION BRIEF 🔹\n"
        "2) 🔹 STRUCTURED_SUMMARY_JSON 🔹"
    )

print("✔️ Decision Brief Agent installed!")
