Defines a competitive pricing specialist agent focused on pricing intelligence.

For a given product and region, this agent:

- consults internal synthetic snapshots and competitor pricing tools to assemble a table of relevant offers,
- analyzes how the internal price compares to the observed competitive range,
- derives a recommended competitive price band (for example, low / mid / high anchor points),
- and emits a structured JSON payload that summarizes competitor prices, spreads, and the suggested corridor.

The result gives the rest of the pipeline a grounded view of “what the market is charging” and a realistic band within which FX-aware pricing decisions can be made.
