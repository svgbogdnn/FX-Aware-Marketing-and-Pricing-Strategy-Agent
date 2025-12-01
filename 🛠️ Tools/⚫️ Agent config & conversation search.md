Adds tools for inspecting the conversation and tuning the agent configuration at runtime:

- **`search_conversation(keyword)`**  
  Scans the in-memory conversation for messages containing a given keyword (case-insensitive).  
  Returns a list of matches with indices, roles, timestamps and content, which helps quickly locate relevant turns in long sessions.

- **`update_agent_config(temperature, max_tokens, model_name)`**  
  Validates and applies runtime changes to the shared `CONFIG` mapping: sampling temperature, maximum response tokens and base model.  
  All parameters are checked for basic validity, and the function returns a summary of what changed.

- **`get_agent_config_and_stats()`**  
  Returns a combined snapshot of the current config (model, temperature, max tokens) and the agent’s internal stats (e.g. counters from plugins).  
