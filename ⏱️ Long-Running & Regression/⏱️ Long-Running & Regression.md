Adds support for long-running workloads where the pricing pipeline is executed many times in a row.

The focus here is on:

- running the end-to-end agent pipeline repeatedly,
- capturing statistics across runs (latency, success rate, tool usage),
- and verifying that the system remains stable over longer sessions.

This kind of workload is useful to simulate real usage patterns, observe how the agent behaves over time, and surface any hidden resource or state issues.
