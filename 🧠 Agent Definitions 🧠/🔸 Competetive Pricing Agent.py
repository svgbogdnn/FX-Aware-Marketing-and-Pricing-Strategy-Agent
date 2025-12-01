from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from google.genai import types


competitive_pricing_agent = Agent(
    model=model,
    name="competitive_pricing_agent",
    description=(
        "Agent that performs competitive pricing analysis for a given product, "
        "using internal synthetic snapshots and optional web context to build a structured view "
        "of competitor prices and a recommended competitive price band."
    ),
    instruction=(
        "You are a pricing analyst focused on competitive intelligence.\n\n"
        "Your task is to analyze the competitive price landscape for a single product in a region.\n"
        "Always follow this workflow:\n"
        "1) Call the internal competitor price snapshot tool to retrieve a synthetic list of competitor offers.\n"
        "2) Optionally use Google Search to refine your understanding of which competitor names and price levels "
        "are typical, but keep in mind that the internal snapshot is the primary data source for any numbers.\n"
        "3) Based on the snapshot, compute an approximate competitive price band:\n"
        "   - low: near the lower quartile of competitor prices, but not obviously dumping.\n"
        "   - high: near the upper quartile, but still realistic in the current market.\n"
        "4) If the caller provides a current or planned 'our_price', evaluate how it compares to this band.\n\n"
        "Your response must contain two clearly separated parts:\n"
        "A) A short narrative (1–3 paragraphs) explaining:\n"
        "   - how many competitor offers you see,\n"
        "   - where the price band roughly sits,\n"
        "   - how our price relates to competitors (below/within/above band).\n"
        "B) A JSON block with the following structure:\n"
        "   {\n"
        '     \"product_name\": str,\n'
        '     \"region\": str,\n'
        '     \"currency\": str,\n'
        '     \"our_price\": float | null,\n'
        '     \"competitor_offers\": [\n'
        "       {\"name\": str, \"price\": float, \"currency\": str, \"is_promo\": bool, \"promo_label\": str | null}\n"
        "     ],\n"
        '     \"suggested_competitive_band\": {\"low\": float, \"high\": float}\n'
        "   }\n\n"
        "Do not claim that prices are real-time or scraped from live sites. They are synthetic and for internal "
        "planning only, but your reasoning and explanation should be realistic and business-like."
    ),
    tools=[
        FunctionTool(get_competitor_price_snapshot),
    ],
)


competitive_pricing_tool = AgentTool(competitive_pricing_agent)


def build_competitive_pricing_prompt(
    product_name: str,
    region: str = "US",
    currency: str = "USD",
    our_price: Optional[float] = None,
) -> str:
    """
    Build a consistent user prompt for the competitive_pricing_agent.

    Args:
        product_name: Name or identifier of the product under analysis.
        region: Sales region to consider.
        currency: Currency for the pricing comparison.
        our_price: Optional current or planned internal price.

    Returns:
        A formatted prompt string for the agent.
    """
    our_price_line = (
        f"- Our current/planned price: {our_price} {currency}\n"
        if our_price is not None
        else "- Our current/planned price: not provided\n"
    )

    return (
        "Perform a competitive pricing analysis for the following product and context:\n"
        f"- Product name: {product_name}\n"
        f"- Region: {region}\n"
        f"- Currency: {currency}\n"
        f"{our_price_line}\n"
        "Use the internal competitor snapshot as the primary data source and apply your instructions to produce "
        "both a narrative explanation and a JSON block with the specified schema."
    )

print("✔️ Competetive Pricing Agent installed!")
