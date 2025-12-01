Defines an async test harness around `run_full_fx_pricing_pipeline` so the full FX-aware pricing orchestrator can be validated in a repeatable way.

- `_check(...)` is a tiny assertion helper that fails fast with a clear error message if any expectation is not met.
- `test_fx_pricing_orchestrator_once(config)` runs the end-to-end pipeline for a single product configuration and performs a series of structural checks:
  - ensures that `decision_brief_text` is a non-empty, sufficiently long string (the brief should look like a real explanation, not a stub);
  - verifies that `structured_summary_json` and `evaluation_json` are valid JSON dicts and can be parsed with `json.loads`;
  - checks that the main JSON outputs for the sub-agents (market research, competitive pricing, FX impact, margin scenarios, vendor FX) are non-empty strings;
  - inspects `observability_summary` and `observability_detailed`, expecting a non-zero number of model, tool and agent invocations as well as a non-zero event count;
  - calls `evaluate_pipeline_output_basic(result)` to compute a simple health summary for the run.
- The helper also calls `FX_MEMORY.search_memory(...)` to confirm that at least one memory entry was persisted for this product and region, and that the last entry matches the tested configuration.
- `test_fx_pricing_orchestrator_full(base_config)` executes the orchestrator twice with the same base configuration, aggregates timings for both runs and checks that memory contains at least two entries after the two executions. It prints per-run duration and total duration, plus a short view of the observability summaries, and returns a combined structure with both runs and the collected memory entries.
- At the end the block only registers these helpers and prints a short confirmation message so that no heavy test run is triggered automatically when the notebook is imported.
