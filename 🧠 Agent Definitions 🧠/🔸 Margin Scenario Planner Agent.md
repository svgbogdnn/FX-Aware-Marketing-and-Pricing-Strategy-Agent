Defines a margin planning agent that turns FX-aware unit costs into concrete pricing strategies.

Given:

- a base unit cost (usually coming from the FX impact agent),
- a set of candidate selling prices,
- and an optional target margin,

this agent:

- evaluates margin for each candidate price point,
- incorporates competitive benchmarks where available,
- flags prices that meet or miss the target margin,
- and proposes a small set of recommended strategies (for example, “defensive”, “balanced”, “aggressive”).

The output is a structured JSON payload plus a short explanation that helps a business user understand the trade-offs between margin and competitiveness across the price range.
