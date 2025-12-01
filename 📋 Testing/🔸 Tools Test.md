Exercises core utility functions and tools with simple, deterministic inputs.

Each check:

- calls a single tool (for example, product snapshot, competitor snapshot, FX scenarios or margin scenarios),
- uses a fixed seed or fixed parameters so that the result is reproducible across runs,
- and prints a compact summary of the output structure and a few representative values.

These tests act as a quick guard against accidental breaking changes in the tool logic or schemas used by the agents.
