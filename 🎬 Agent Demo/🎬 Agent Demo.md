Presents a human-readable demo of the FX-aware pricing agent that can be run end-to-end on one or more realistic launch scenarios.

- Utility helpers `_trim_text(...)` and `_pretty_print_json_maybe(...)` format long texts and JSON blocks into compact, readable sections, trimming overly long content while preserving structure.
- `run_demo_scenario(demo_index, scenario_name, config)`:
  - executes `test_fx_pricing_orchestrator_once(config)` to run the full multi-agent pipeline for the given scenario;
  - extracts `decision_brief_text`, `structured_summary_json`, `evaluation_json`, `observability_summary` and the basic health flag from the returned `result`;
  - prints a structured console view with clear separators:
    - a header identifying the demo number and scenario name,
    - a USER block that shows the original product + FX context / manager notes,
    - an AGENT RESPONSE block split into: ① decision brief, ② structured summary, ③ evaluation, ④ observability summary.
  - trims very long fields (for example, decision briefs and JSON strings) so that the demo stays easy to read in the notebook, while still showing that the agent produces rich, multi-section output.
- `demo_scenarios` contains one or more realistic launch configs (for example, a MacBook Pro FX-risk scenario), and `run_all_demo_scenarios()` simply iterates over them and calls `run_demo_scenario(...)` for each.
- The last line, when uncommented, runs the full demo suite with a single command, turning the notebook into a repeatable, presentation-ready walkthrough of how the FX-aware pricing agent behaves on a concrete scenario.
