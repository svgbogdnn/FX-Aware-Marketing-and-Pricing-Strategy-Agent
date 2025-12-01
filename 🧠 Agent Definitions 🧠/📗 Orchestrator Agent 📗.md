Defines the top-level coordinator agent that orchestrates the entire multi-agent FX-aware pricing workflow.

The coordinator:

- exposes all specialist agents as tools:
  - market research,
  - competitive pricing,
  - vendor FX snapshot,
  - FX impact analysis,
  - margin scenario planning,
  - decision brief synthesis,
  - and evaluation,
- receives a business-oriented prompt from a marketing or procurement manager (product, region, currencies, costs, volume, optional price and target margin),
- executes a multi-step workflow:
  1) calls the market research agent,
  2) calls the competitive pricing agent,
  3) retrieves vendor FX rates and runs FX impact scenarios,
  4) runs margin scenario planning on candidate price points,
  5) calls the decision brief agent to synthesize the result,
  6) calls the evaluation agent to score the brief.

The final response is standardized into three clearly separated sections:

- `FINAL_DECISION_BRIEF` – the narrative recommendation,
- `STRUCTURED_SUMMARY_JSON` – the machine-readable summary,
- `EVALUATION_JSON` – the quality and consistency assessment.

The helper that builds the coordinator prompt ensures that every run of the pipeline starts from a consistent, well-structured description of the manager’s situation, which makes the orchestration reliable and easier to test.
