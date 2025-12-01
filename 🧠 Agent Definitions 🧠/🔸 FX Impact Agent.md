Defines an FX impact specialist agent that quantifies how currency movements affect landed cost.

Based on:

- purchase price and purchase currency,
- reporting currency,
- current or vendor-provided FX rates,
- and a target volume,

this agent:

- calls the FX scenario tools to generate a set of “what-if” FX scenarios (e.g., ±5%, ±10%),
- computes scenario-based landed unit costs and total costs in the reporting currency,
- and produces both a narrative explanation of FX risk and a structured JSON table of scenarios.

This output gives downstream agents a clear, quantified view of FX sensitivity that can be directly plugged into margin and pricing analysis.
