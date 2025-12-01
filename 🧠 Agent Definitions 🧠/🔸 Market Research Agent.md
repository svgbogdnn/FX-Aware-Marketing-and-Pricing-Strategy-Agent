Implements a market research specialist agent that acts like a B2B market analyst.

Given a product or category and a region, this agent:

- uses the internal product snapshot tool to ground itself in the basic product attributes,
- optionally leverages web search tools when available to infer typical brands, competitor types, and positioning,
- and produces a two-part output:
  - a short human-readable narrative describing the market landscape, and
  - a structured JSON payload capturing key competitors, indicative price ranges, and positioning signals.

The JSON output is designed to be consumed by downstream agents, so that later steps can reason over a consistent, machine-readable view of the market.
