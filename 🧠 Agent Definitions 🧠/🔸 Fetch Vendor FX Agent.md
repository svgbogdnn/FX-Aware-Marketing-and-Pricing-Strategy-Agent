Combines a vendor-style FX data tool and a thin agent wrapper that exposes it as an external FX provider.

The tool:

- calls a public JSON FX API to fetch daily exchange rates for a base currency against multiple targets,
- falls back to a deterministic synthetic rate generator if the API is unavailable,
- and returns a structured payload with base currency, as-of date, source type (live vs synthetic), and per-currency rates and converted amounts.

The agent:

- treats the tool output as the authoritative “vendor response”,
- explains the FX snapshot in concise business language (base, date, key pairs),
- and passes through the JSON payload unchanged except for formatting.

This pattern simulates integration with a real FX data vendor while preserving deterministic behavior suitable for notebooks and evaluation.
