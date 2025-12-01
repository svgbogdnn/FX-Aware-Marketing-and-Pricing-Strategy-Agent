def search_conversation(keyword: str) -> List[Dict[str, Any]]:
    
    """
    Search the in-memory conversation for messages containing the given keyword.

    Args:
        keyword: Case-insensitive substring to search for in message content.

    Returns:
        List of dicts with fields:
            index: Position of the message in memory.
            role: Message role.
            timestamp: Optional timestamp field.
            content: Full message text.

    Raises:
        RuntimeError: If the global agent is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    messages: List[Dict[str, Any]] = list(getattr(agent.memory, "messages", []))
    keyword_lower = keyword.lower()

    results: List[Dict[str, Any]] = []

    for idx, msg in enumerate(messages):
        content = str(msg.get("content", ""))
        if keyword_lower in content.lower():
            results.append(
                {
                    "index": idx,
                    "role": msg.get("role", ""),
                    "timestamp": msg.get("timestamp", None),
                    "content": content,
                }
            )

    return results


def configure_agent(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    
    """
    Update basic agent configuration parameters in a shared CONFIG mapping.

    Args:
        temperature: Sampling temperature in [0.0, 1.0].
        max_tokens: Maximum tokens for model responses, must be positive.
        model_name: Underlying model identifier.

    Returns:
        Dict with keys:
            changes: List of human-readable change descriptions.
            config: Snapshot of the updated CONFIG mapping.

    Raises:
        RuntimeError: If the agent or CONFIG is not available, or arguments are invalid.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")
    _check("CONFIG" in globals(), "CONFIG mapping is not defined")

    changes: List[str] = []

    if temperature is not None:
        _check(0.0 <= temperature <= 1.0, "temperature must be between 0.0 and 1.0")
        CONFIG["temperature"] = float(temperature)
        changes.append(f"temperature={temperature}")

    if max_tokens is not None:
        _check(max_tokens > 0, "max_tokens must be positive")
        CONFIG["max_tokens"] = int(max_tokens)
        changes.append(f"max_tokens={max_tokens}")

    if model_name is not None:
        CONFIG["model"] = str(model_name)
        changes.append(f"model={model_name}")

    if hasattr(agent, "logger") and changes:
        agent.logger.info("agent_reconfigured", changes=changes, config=dict(CONFIG))

    return {"changes": changes, "config": dict(CONFIG)}


def show_agent_config() -> Dict[str, Any]:
    
    """
    Return a structured snapshot of the agent configuration and basic runtime stats.

    Returns:
        Dict with keys:
            model: Current model name.
            temperature: Current sampling temperature.
            max_tokens: Current token limit.
            stats: Output of agent.get_stats().

    Raises:
        RuntimeError: If the global agent or CONFIG is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")
    _check("CONFIG" in globals(), "CONFIG mapping is not defined")

    stats: Dict[str, Any] = agent.get_stats()

    return {
        "model": CONFIG.get("model"),
        "temperature": CONFIG.get("temperature"),
        "max_tokens": CONFIG.get("max_tokens"),
        "stats": stats,
    }

print("✔️ Agent config & conversation search tools installed!")
