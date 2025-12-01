Demonstrates agent-to-agent (A2A) communication by calling a remote Gemini-powered agent as if it were an external FX microservice.

This block:

- configures a remote agent endpoint using the A2A protocol and wraps it in a client-style agent object;
- sends a small, structured FX-related request (for example, base currency, target currencies and amount) from the local notebook agent to the remote agent;
- receives a structured response (rates, converted amounts and basic metadata) and verifies that serialization and deserialization across the A2A boundary work as expected;
- mirrors the pattern of integrating an external, independently managed agent or service into the local FX-aware pricing pipeline.

The example highlights how the system can delegate part of the reasoning or data retrieval to a remote agent, while keeping the local orchestration logic unchanged and treating the remote agent as just another tool in the overall architecture.
