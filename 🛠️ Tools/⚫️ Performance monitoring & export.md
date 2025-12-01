Tracks and exports high-level performance metrics for the agent over time:

- **`track_performance_metrics()`**  
  Constructs a metrics snapshot and appends it to `agent.performance_history`.  
  Enables time-series analysis of how the agent behaves across runs.

- **`get_performance_summary()`**  
  Reads the accumulated `performance_history` and computes:
  - number of snapshots,
  - the most recent metrics,
  - simple growth indicators,
  - and a small window of recent snapshots for quick inspection.

- **`export_performance_data(filename)`**  
  Writes the entire `performance_history` to a JSON file and emits a log event with the export metadata.  
