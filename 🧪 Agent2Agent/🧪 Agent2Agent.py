from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass
class A2AServiceSpec:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


@dataclass
class A2AService:
    spec: A2AServiceSpec
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]


def to_a2a(
    handler: Callable[[Dict[str, Any]], Dict[str, Any]],
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    output_schema: Dict[str, Any],
) -> A2AService:
    spec = A2AServiceSpec(
        name=name,
        description=description,
        input_schema=input_schema,
        output_schema=output_schema,
    )
    service = A2AService(spec=spec, handler=handler)
    return service


class RemoteA2aAgent:
    def __init__(self, service: A2AService, service_name: str):
        self.service = service
        self.service_name = service_name

    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("RemoteA2aAgent payload must be a dict")
        result = self.service.handler(payload)
        if not isinstance(result, dict):
            raise ValueError("RemoteA2aAgent handler returned non-dict result")
        return result


print("✅ A2A core (A2AServiceSpec, to_a2a, RemoteA2aAgent) has been installed!")


import math
from typing import Dict, Any


def simulate_vendor_fx_service(request: Dict[str, Any]) -> Dict[str, Any]:
    base = str(request.get("base_currency", "")).upper()
    quote = str(request.get("quote_currency", "")).upper()
    horizon_days = int(request.get("horizon_days", 30))

    if base == "CNY" and quote == "USD":
        spot = 0.14
    elif base == "USD" and quote == "CNY":
        spot = 7.1
    elif base == "EUR" and quote == "USD":
        spot = 1.08
    elif base == "USD" and quote == "EUR":
        spot = 0.93
    else:
        spot = 1.0

    vol_factor = min(max(horizon_days / 365.0, 0.0), 1.0)
    shock = 0.05 + 0.1 * vol_factor

    scenario_up = spot * (1.0 + shock)
    scenario_down = spot * (1.0 - shock)

    result = {
        "base_currency": base,
        "quote_currency": quote,
        "spot_rate": spot,
        "scenario_up": scenario_up,
        "scenario_down": scenario_down,
        "horizon_days": horizon_days,
        "comment": (
            f"Synthetic FX quote from vendor for {base}/{quote} with "
            f"horizon={horizon_days}d and shock≈{round(shock * 100, 1)}%."
        ),
    }
    return result


vendor_fx_input_schema = {
    "type": "object",
    "properties": {
        "base_currency": {
            "type": "string",
            "description": "Base currency code, for example CNY or USD",
        },
        "quote_currency": {
            "type": "string",
            "description": "Quote currency code, for example USD or EUR",
        },
        "horizon_days": {
            "type": "integer",
            "description": "Time horizon in days for FX scenario generation",
        },
    },
    "required": ["base_currency", "quote_currency"],
}

vendor_fx_output_schema = {
    "type": "object",
    "properties": {
        "base_currency": {"type": "string"},
        "quote_currency": {"type": "string"},
        "spot_rate": {"type": "number"},
        "scenario_up": {"type": "number"},
        "scenario_down": {"type": "number"},
        "horizon_days": {"type": "integer"},
        "comment": {"type": "string"},
    },
    "required": [
        "base_currency",
        "quote_currency",
        "spot_rate",
        "scenario_up",
        "scenario_down",
    ],
}

vendor_fx_a2a_service = to_a2a(
    handler=simulate_vendor_fx_service,
    name="vendor-fx-quotes",
    description="Provides synthetic FX spot and simple scenario quotes for base/quote currencies.",
    input_schema=vendor_fx_input_schema,
    output_schema=vendor_fx_output_schema,
)

print("✅ Vendor FX A2A service has been installed!")


remote_vendor_fx_agent = RemoteA2aAgent(
    service=vendor_fx_a2a_service,
    service_name=vendor_fx_a2a_service.spec.name,
)

def call_vendor_fx_remote(
    base_currency: str,
    quote_currency: str,
    horizon_days: int = 90,
) -> Dict[str, Any]:
    payload = {
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "horizon_days": horizon_days,
    }
    response = remote_vendor_fx_agent.invoke(payload)
    return response


print("✅ Remote vendor FX A2A agent has been installed!")
'''

'''
response_cny_usd = call_vendor_fx_remote(
    base_currency="CNY",
    quote_currency="USD",
    horizon_days=180,
)

response_usd_cny = call_vendor_fx_remote(
    base_currency="USD",
    quote_currency="CNY",
    horizon_days=30,
)

print("=== CNY → USD FX quote (A2A) ===")
print(response_cny_usd)
print()
print("=== USD → CNY FX quote (A2A) ===")
print(response_usd_cny)
