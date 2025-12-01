Implements utilities for working with the agent’s conversation and logging state:

- **`export_conversation_history(...)`**  
  Dumps the current in-memory conversation (messages, roles, timestamps) plus basic statistics into a human-readable text file.  
  Useful for debugging, offline review and attaching transcripts to evaluations or reports.

- **`export_agent_logs(...)`**  
  Serializes a structured view of conversation messages and logger metadata into a JSON file.  
  This mirrors what the logging plugin collects and makes it easy to analyze runs or feed them into external tooling.

- **`reset_agent()`**  
  Resets the agent’s state (including memory) and returns a snapshot of key statistics from the previous session.  
  Also emits a structured log event so that resets are visible in observability data.
