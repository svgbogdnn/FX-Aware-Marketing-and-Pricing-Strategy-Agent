This section provides a practical test harness around the FX-aware pricing system.

The tests here complement the earlier smoke tests for individual agents and focus on the **end-to-end orchestrator**:

- checking that the full multi-agent pipeline runs successfully on realistic scenarios;
- validating the structure and basic quality of the outputs (decision brief, structured summary JSON, evaluation JSON, observability data and memory entries);
- exercising the integration between the orchestrator, the observability plugins and the memory service;
- providing a repeatable way to run sanity checks before making changes to prompts, tools or pipeline configuration.

The goal is not to build a full formal test suite, but to have a clear, readable set of checks that make it easy to see whether the orchestrator behaves correctly and consistently over time.
