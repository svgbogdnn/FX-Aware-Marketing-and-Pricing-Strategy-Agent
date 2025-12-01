from typing import Any, Dict, List

import requests
from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool


def fetch_vendor_fx_rates(
    base_currency: str,
    target_currencies: List[str],
    amount: float = 1.0,
) -> Dict[str, Any]:
    """
    Fetch FX rates from an external vendor-like API and compute converted amounts.

    This function first attempts to call a public JSON FX API that provides
    daily exchange rates without an API key. If the HTTP request fails for
    any reason, it falls back to a deterministic synthetic rate generator
    so that downstream agents can still operate.

    Args:
        base_currency: ISO currency code used as base (e.g., 'USD', 'EUR', 'CNY').
        target_currencies: List of ISO currency codes to convert into.
        amount: Amount in base_currency to convert.

    Returns:
        Dict with the following structure:
            {
              "vendor": "fawazahmed0/currency-api",
              "base_currency": "USD",
              "amount": 100.0,
              "as_of_date": "2025-11-23",
              "source": "live" or "synthetic",
              "rates": [
                {
                  "target_currency": "EUR",
                  "rate": 0.92,
                  "converted_amount": 92.0
                },
                ...
              ],
              "raw": {...}  (raw vendor payload or synthetic metadata)
            }
    """
    base = base_currency.upper()
    targets = [c.upper() for c in target_currencies]

    url = (
        f"https://cdn.jsdelivr.net/npm/@fawazahmed0/"
        f"currency-api@latest/v1/currencies/{base.lower()}.json"
    )

    live_data: Dict[str, Any] = {}
    source = "synthetic"
    as_of_date = datetime.utcnow().date().isoformat()

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        live_data = response.json()
        if "date" in live_data:
            as_of_date = str(live_data["date"])
        base_obj = live_data.get(base.lower(), {})
        rates: Dict[str, float] = {}
        for k, v in base_obj.items():
            code = k.upper()
            if code in targets:
                try:
                    rates[code] = float(v)
                except (TypeError, ValueError):
                    continue
        if rates:
            source = "live"
        else:
            live_data = {}
    except Exception:
        live_data = {}

    if not live_data or source != "live":
        key = base + ":" + ",".join(sorted(targets))
        rng = _make_rng(key)
        rates = {}
        for t in targets:
            raw_rate = 0.3 + rng.uniform(-0.1, 0.3)
            if base == "USD":
                raw_rate = 0.6 + rng.uniform(-0.2, 0.4)
            rates[t] = round(abs(raw_rate), 6)
        live_data = {
            "date": as_of_date,
            "base": base,
            "synthetic": True,
        }

    rate_list = []
    for t in targets:
        r = rates.get(t)
        if r is None:
            continue
        converted = amount * r
        rate_list.append(
            {
                "target_currency": t,
                "rate": round(r, 6),
                "converted_amount": round(converted, 4),
            }
        )

    return {
        "vendor": "fawazahmed0/currency-api",
        "base_currency": base,
        "amount": float(amount),
        "as_of_date": as_of_date,
        "source": source,
        "rates": rate_list,
        "raw": live_data,
    }


vendor_fx_agent = Agent(
    model=model,
    name="vendor_fx_agent",
    description=(
        "External vendor-style FX agent that wraps a public JSON FX API and exposes "
        "vendor-controlled exchange rates to internal consumers."
    ),
    instruction=(
        "You act as an FX data vendor interface.\n\n"
        "You have one primary tool that returns FX rates for a base currency against a list "
        "of target currencies, along with converted amounts for a given base amount.\n"
        "Treat the tool output as the authoritative vendor response. Your job is to:\n"
        "1) Call the tool with the requested currencies and amount.\n"
        "2) Return a concise explanation of the FX snapshot (base, date, key pairs) followed by\n"
        "   the JSON payload from the tool, unchanged except for formatting if needed.\n\n"
        "Do not invent your own FX rates. If the tool indicates the source is 'synthetic', clearly state\n"
        "that this is a fallback scenario for demonstration/testing only.\n"
        "Do not claim to provide real-time trading data; you are a planning and analytics data source."
    ),
    tools=[
        FunctionTool(fetch_vendor_fx_rates),
    ],
)


vendor_fx_tool = AgentTool(vendor_fx_agent)


def build_vendor_fx_prompt(
    base_currency: str,
    target_currencies: List[str],
    amount: float = 1.0,
) -> str:
    """
    Build a prompt for the vendor_fx_agent.

    Args:
        base_currency: Base currency code (e.g., 'USD').
        target_currencies: List of target currency codes (e.g., ['EUR', 'CNY']).
        amount: Amount in base_currency to convert.

    Returns:
        A formatted prompt string for the vendor_fx_agent.
    """
    targets_str = ", ".join(target_currencies)
    return (
        "Fetch an FX snapshot from your vendor tool and summarize it.\n"
        f"- Base currency: {base_currency}\n"
        f"- Target currencies: [{targets_str}]\n"
        f"- Amount in base currency: {amount}\n\n"
        "Then provide a short explanation and the JSON payload from the tool."
    )

print("✔️ Fetch Vendor FX Agent installed!")
