Provides helpers for running multiple queries and keeping the conversation context compact:

- **`batch_query(questions)`**  
  Accepts either a list of questions or a semicolon-separated string, runs each question through the agent and captures:
  - the response,
  - status information,
  - and any errors.  
  Returns both per-question results and aggregate summary statistics for the batch.

- **`display_batch_results(results)`**  
  Converts the `batch_query()["results"]` mapping into a sorted list of entries that is easier to render in tables or UIs.

- **`summarize_conversation()`**  
  Walks through the conversation and builds a high-level summary focused on common ML/competition topics (features, models, debugging, metrics, data, strategy, etc.).  
  The summary is represented as a structured payload that can be logged or fed back into the agent.

- **`auto_summarize_if_needed()`**  
  Monitors the length of the conversation and, once a threshold is exceeded, automatically:
  - calls `summarize_conversation()`,
  - clears the detailed message history,
  - and injects a compact summary back into memory.  
