from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from google.genai import types

APP_NAME = "fx_marketing_agent_system"


market_research_agent = Agent(
    model=model,
    name="market_research_agent",
    description=(
        "Agent that performs lightweight market scans for a given product or category, "
        "identifying key competitors, representative SKUs, and high-level positioning."
    ),
    instruction=(
        "You are a B2B market research analyst. "
        "Your goal is to help a marketing or procurement manager quickly understand the market "
        "landscape for a product or category.\n\n"
        "Always do the following:\n"
        "1) Use the internal product snapshot tool to ground yourself in the basic product info.\n"
        "2) Use Google Search when useful to infer competitor types, typical brands, and positioning.\n"
        "3) Produce a response that contains two parts:\n"
        "   a) A short, human-readable summary (2–4 paragraphs) describing the market landscape.\n"
        "   b) A JSON block with the following structure:\n"
        "      {\n"
        '        \"product_name\": str,\n'
        '        \"category\": str,\n'
        '        \"region\": str,\n'
        '        \"key_competitors\": [\n'
        "          {\"name\": str, \"positioning\": str, \"notes\": str}\n"
        "        ],\n"
        '        \"typical_price_band\": {\"currency\": str, \"low\": float, \"high\": float},\n'
        '        \"key_features\": [str]\n'
        "      }\n\n"
        "If you are unsure about exact names or data, you may synthesize realistic but clearly "
        "approximate examples, and keep the narrative honest about uncertainty.\n"
        "Do not fabricate that information is exact or real-time; this is an internal planning tool."
    ),
    tools=[
        FunctionTool(get_product_snapshot)
    ],
)


market_research_tool = AgentTool(market_research_agent)


def build_market_research_prompt(
    product_name: str,
    category: str,
    region: str = "US",
) -> str:
    """
    Build a consistent user prompt for the market_research_agent.

    This helper makes it easier for the orchestrator (and for manual testing)
    to ask for market research in a uniform way.
    """
    return (
        f"Please perform a market scan for the following:\n"
        f"- Product name: {product_name}\n"
        f"- Category: {category}\n"
        f"- Region: {region}\n\n"
        "Describe the key competitors, typical positioning (budget vs premium), "
        "and an approximate price band in the target currency. "
        "Return both a narrative and a JSON block in the schema described in your instructions."
    )

print("✔️ Research Agent Agent installed!")
