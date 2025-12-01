Provides the core domain tools used by the agents to reason about pricing and FX impact:

- **Deterministic RNG helper (`_make_rng`)**  
  Creates a seeded `random.Random` instance from a string key, so that tool outputs are stable and reproducible for the same inputs.

- **`get_product_snapshot(...)`**  
  Generates a synthetic internal product record (costs, default list price, MOQ, lead times, currency, timestamps).  
  This simulates an ERP/catalog entry and gives the agent a structured, machine-readable view of the product.

- **`get_competitor_price_snapshot(...)`**  
  Produces a synthetic competitor pricing snapshot for the product and region, including multiple competitor offers, promotional flags and last-seen timestamps.  
  The structure is designed for downstream comparison and reasoning about pricing corridors.

- **`calculate_fx_impact_scenarios(...)`**  
  Computes what happens to landed costs under a range of FX shifts (e.g. −10%, −5%, 0%, +5%, +10%).  
  Returns a scenario table with effective FX rates, per-unit and total landed costs, and relative changes vs the current baseline.

- **`plan_margin_scenarios(...)`**  
  Evaluates a set of candidate selling prices against a given unit cost, producing margin scenarios and flags indicating whether each price meets a target margin.

- **`build_pricing_recommendation(...)`**  
  Combines unit cost, competitor snapshot and optional FX scenarios into a single structured recommendation that includes:
  - recommended price,
  - margin and competitiveness statistics,
  - and a short rationale payload.

These tools intentionally keep the logic deterministic and transparent, so that the LLM agent can explain its decisions on top of a stable structured substrate.
