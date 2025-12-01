Implements a simple, in-memory long-term memory layer for FX pricing sessions.  
Each session stores a structured snapshot of the agent’s work for a given product and region (product metadata, market research, competitor pricing, FX scenarios, margin analysis and the final decision brief), together with timestamps and basic tags.

The memory layer is designed to be:

- **Structured** – each entry follows a predictable schema, making it easy to filter, aggregate and reuse in prompts.
- **Deterministic** – new sessions are appended explicitly via helper methods; there is no hidden side-effect or background mutation.
- **Agent-friendly** – stored payloads can be injected back into the context as “prior knowledge” to make new recommendations more consistent over time.
