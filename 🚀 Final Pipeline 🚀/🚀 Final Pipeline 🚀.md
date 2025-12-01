Runs the full FX-aware pricing pipeline from a single entry point.

The pipeline:

- accepts a structured configuration describing the product, region, reporting and purchase currencies, volume, unit costs and optional pricing constraints (current price, target margin and manager notes);
- builds a standardized coordinator prompt from that configuration so that every run starts from a consistent description of the business scenario;
- calls the orchestrator agent, which internally invokes all specialist agents and tools:
  - market research,
  - competitive pricing,
  - vendor FX snapshot,
  - FX impact analysis,
  - margin scenario planning,
  - decision brief synthesis,
  - and quality evaluation;
- collects all intermediate artifacts (snapshots, scenarios and recommendations) into a single consolidated result object;
- attaches diagnostic context from observability plugins (timings, call counts, basic stats) and, when available, a snapshot of long-term memory for this product and region.

The final return value contains:

- a narrative decision brief suitable for business stakeholders,
- a machine-readable structured summary JSON that mirrors the brief,
- an evaluation JSON object with quality scores and comments,
- and optional telemetry that can be used for debugging, performance analysis and regression testing.

This function is the canonical way to execute the multi-agent system on a real FX-aware pricing question and is reused across the demo and regression sections of the notebook.
