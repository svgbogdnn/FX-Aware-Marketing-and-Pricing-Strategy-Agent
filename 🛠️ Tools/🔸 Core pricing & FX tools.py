from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.adk.tools import google_search


def _make_rng(key: str) -> random.Random:
    """
    Internal helper to get a deterministic random generator based on a string key.
    Ensures stable outputs for the same inputs across runs.
    """
    
    seed = abs(hash(key)) % (2**32)
    return random.Random(seed)


def get_product_snapshot(
    product_name: str,
    category: str = "general",
    region: str = "US",
    base_currency: str = "USD",
) -> Dict[str, Any]:
    
    """
    Generate a synthetic internal product snapshot for a purchasing/marketing workflow.

    This simulates an internal ERP/catalog record and can be used by agents
    to ground their reasoning in a consistent structure.

    Args:
        product_name: Human-readable product name or SKU.
        category: High-level category name (e.g., "electronics", "fashion").
        region: Sales region (e.g., "US", "EU", "APAC").
        base_currency: Currency used for purchasing and costing.

    Returns:
        Dict with fields:
            product_name
            category
            region
            currency
            unit_cost
            default_list_price
            reorder_lead_time_days
            moq_units
            last_updated_iso
    """
    
    key = f"{product_name}:{category}:{region}"
    rng = _make_rng(key)

    unit_cost = round(5.0 + rng.uniform(1.0, 50.0), 2)
    list_price_multiplier = 1.2 + rng.uniform(0.1, 0.8)
    default_list_price = round(unit_cost * list_price_multiplier, 2)

    reorder_lead_time_days = 14 + rng.randint(0, 28)
    moq_units = 50 + rng.randint(0, 450)

    now = datetime.utcnow()

    return {
        "product_name": product_name,
        "category": category,
        "region": region,
        "currency": base_currency,
        "unit_cost": unit_cost,
        "default_list_price": default_list_price,
        "reorder_lead_time_days": reorder_lead_time_days,
        "moq_units": moq_units,
        "last_updated_iso": now.isoformat() + "Z",
    }


def get_competitor_price_snapshot(
    product_name: str,
    region: str = "US",
    currency: str = "USD",
    competitor_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    
    """
    Generate a synthetic competitor price snapshot for a single product and region.

    This is meant to emulate the output of a web-scraping / price-intelligence system
    so an agent can perform competitive pricing analysis on top of it.

    Args:
        product_name: Product name or SKU used as the anchor.
        region: Target market region.
        currency: Currency for all prices in the snapshot.
        competitor_names: Optional explicit competitor list. If omitted, a default
            synthetic list is used.

    Returns:
        Dict with:
            product_name
            region
            currency
            base_reference_price
            offers: list of dicts with:
                competitor_id
                competitor_name
                price
                is_promo
                promo_label
                url
                last_seen_iso
    """
    
    key = f"{product_name}:{region}:{currency}"
    rng = _make_rng(key)

    if competitor_names is None:
        competitor_names = [
            "AlphaMart",
            "GlobalRetail",
            "BudgetBox",
            "PrimeDeal",
            "SmartWholesale",
        ]

    base_reference_price = round(10.0 + rng.uniform(1.0, 90.0), 2)

    offers: List[Dict[str, Any]] = []
    now = datetime.utcnow()

    for idx, name in enumerate(competitor_names):
        delta_pct = rng.uniform(-0.15, 0.20)
        price = round(base_reference_price * (1.0 + delta_pct), 2)

        is_promo = rng.random() < 0.35
        promo_label = None
        if is_promo:
            promo_label = rng.choice(
                ["Weekend Sale", "Clearance", "Seasonal Promo", "Limited Offer"]
            )

        last_seen = now - timedelta(hours=rng.randint(0, 72))

        offers.append(
            {
                "competitor_id": f"comp_{idx+1}",
                "competitor_name": name,
                "price": price,
                "currency": currency,
                "is_promo": is_promo,
                "promo_label": promo_label,
                "url": f"https://example.com/{name.lower()}/{product_name.replace(' ', '-')}",
                "last_seen_iso": last_seen.isoformat() + "Z",
            }
        )

    return {
        "product_name": product_name,
        "region": region,
        "currency": currency,
        "base_reference_price": base_reference_price,
        "offers": offers,
    }


def calculate_fx_impact_scenarios(
    purchase_price: float,
    purchase_currency: str,
    target_currency: str,
    current_fx_rate: float,
    fx_shocks: Optional[List[float]] = None,
    volume_units: int = 1,
) -> Dict[str, Any]:
    
    """
    Calculate FX impact scenarios for a given purchase price and FX rate.

    Args:
        purchase_price: Price per unit in purchase_currency.
        purchase_currency: Currency used for purchasing (e.g., "CNY").
        target_currency: Reporting/profit currency (e.g., "USD").
        current_fx_rate: Current FX rate as target_currency per unit of purchase_currency.
            Example: if 1 CNY = 0.14 USD, current_fx_rate = 0.14.
        fx_shocks: List of percentage deltas to apply to the FX rate.
            Example: [-0.1, 0.0, 0.1] for -10%, 0%, +10%.
            If None, defaults to [-0.1, -0.05, 0.0, 0.05, 0.1].
        volume_units: Number of units purchased.

    Returns:
        Dict with:
            purchase_price
            purchase_currency
            target_currency
            current_fx_rate
            volume_units
            scenarios: list of dicts with:
                fx_shift_pct
                effective_rate
                landed_cost_per_unit
                landed_cost_total
                relative_cost_vs_current_pct
    """
    
    if fx_shocks is None:
        fx_shocks = [-0.10, -0.05, 0.0, 0.05, 0.10]

    scenarios: List[Dict[str, Any]] = []

    current_landed_per_unit = purchase_price * current_fx_rate

    for shift in fx_shocks:
        effective_rate = current_fx_rate * (1.0 + shift)
        landed_cost_per_unit = purchase_price * effective_rate
        landed_cost_total = landed_cost_per_unit * volume_units

        relative = 0.0
        if current_landed_per_unit > 0:
            relative = (landed_cost_per_unit / current_landed_per_unit) - 1.0

        scenarios.append(
            {
                "fx_shift_pct": shift,
                "effective_rate": round(effective_rate, 6),
                "landed_cost_per_unit": round(landed_cost_per_unit, 4),
                "landed_cost_total": round(landed_cost_total, 2),
                "relative_cost_vs_current_pct": round(relative, 4),
            }
        )

    return {
        "purchase_price": purchase_price,
        "purchase_currency": purchase_currency,
        "target_currency": target_currency,
        "current_fx_rate": current_fx_rate,
        "volume_units": volume_units,
        "scenarios": scenarios,
    }


def plan_margin_scenarios(
    unit_cost: float,
    candidate_prices: List[float],
    target_margin_pct: Optional[float] = None,
) -> Dict[str, Any]:
    
    """
    Compute margin scenarios for a list of candidate selling prices.

    Args:
        unit_cost: Total landed cost per unit in the reporting currency.
        candidate_prices: List of candidate selling prices to evaluate.
        target_margin_pct: Optional target margin in percent (e.g., 0.25 for 25%).
            If provided, each scenario includes a flag whether it meets the target.

    Returns:
        Dict with:
            unit_cost
            target_margin_pct
            scenarios: list of dicts with:
                price
                margin_pct
                margin_absolute
                meets_target
    """
    
    scenarios: List[Dict[str, Any]] = []

    for price in candidate_prices:
        if price <= 0:
            margin_pct = None
            margin_abs = None
            meets = False
        else:
            margin_abs = price - unit_cost
            margin_pct = margin_abs / price
            meets = False
            if target_margin_pct is not None and margin_pct is not None:
                meets = margin_pct >= target_margin_pct

        scenarios.append(
            {
                "price": round(price, 2),
                "margin_pct": None if margin_pct is None else round(margin_pct, 4),
                "margin_absolute": None if margin_abs is None else round(margin_abs, 4),
                "meets_target": meets,
            }
        )

    return {
        "unit_cost": round(unit_cost, 4),
        "target_margin_pct": None if target_margin_pct is None else round(target_margin_pct, 4),
        "scenarios": scenarios,
    }


def build_pricing_recommendation(
    unit_cost: float,
    competitor_snapshot: Dict[str, Any],
    fx_scenarios: Optional[Dict[str, Any]] = None,
    target_margin_pct: float = 0.25,
) -> Dict[str, Any]:
    
    """
    Build a high-level synthetic pricing recommendation based on:
      - competitor prices
      - internal unit cost
      - optional FX scenarios

    This function is intentionally simple and deterministic, so that the LLM agent can
    reason on top of the structured output and explain the trade-offs.

    Args:
        unit_cost: Landed cost per unit in reporting currency.
        competitor_snapshot: Output of get_competitor_price_snapshot().
        fx_scenarios: Optional output of calculate_fx_impact_scenarios().
        target_margin_pct: Target margin as fraction (e.g., 0.25 for 25%).

    Returns:
        Dict with recommendation structure:
            recommended_price
            rationale
            summary_stats
    """
    
    offers = competitor_snapshot.get("offers", [])
    prices = [offer["price"] for offer in offers if isinstance(offer.get("price"), (int, float))]

    if not prices:
        fallback_price = unit_cost * (1.0 + target_margin_pct)
        return {
            "recommended_price": round(fallback_price, 2),
            "rationale": "No competitor prices available; using cost plus target margin.",
            "summary_stats": {
                "unit_cost": round(unit_cost, 4),
                "competitor_min": None,
                "competitor_mean": None,
                "competitor_max": None,
                "target_margin_pct": round(target_margin_pct, 4),
            },
        }

    competitor_min = min(prices)
    competitor_max = max(prices)
    competitor_mean = sum(prices) / len(prices)

    baseline = competitor_mean
    min_allowed = max(unit_cost * (1.0 + target_margin_pct), competitor_min * 0.97)
    max_allowed = competitor_max * 1.03

    candidate = baseline
    if candidate < min_allowed:
        candidate = min_allowed
    if candidate > max_allowed:
        candidate = max_allowed

    fx_note = None
    if fx_scenarios is not None:
        worst = max(
            fx_scenarios.get("scenarios", []),
            key=lambda s: s.get("landed_cost_per_unit", unit_cost),
            default=None,
        )
        if worst is not None:
            worst_cost = worst.get("landed_cost_per_unit", unit_cost)
            min_safe_price = worst_cost * (1.0 + target_margin_pct)
            if candidate < min_safe_price:
                candidate = min_safe_price
                fx_note = (
                    "Adjusted upward to remain profitable under adverse FX scenario."
                )

    rationale_parts: List[str] = [
        "Anchored near the average competitor price.",
        "Respects a minimum margin over unit cost.",
    ]
    if fx_note is not None:
        rationale_parts.append(fx_note)

    return {
        "recommended_price": round(candidate, 2),
        "rationale": " ".join(rationale_parts),
        "summary_stats": {
            "unit_cost": round(unit_cost, 4),
            "competitor_min": round(competitor_min, 2),
            "competitor_mean": round(competitor_mean, 2),
            "competitor_max": round(competitor_max, 2),
            "target_margin_pct": round(target_margin_pct, 4),
        },
    }

print("✔️ Core pricing & FX tools installed!")
