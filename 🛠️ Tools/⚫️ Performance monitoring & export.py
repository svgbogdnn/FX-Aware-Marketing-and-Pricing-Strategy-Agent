def track_performance_metrics() -> Dict[str, Any]:
    
    """
    Snapshot the current performance metrics and append them to agent.performance_history.

    Returns:
        The metrics dict that was recorded, with keys:
            timestamp
            queries
            tools_called
            avg_response_time
            errors
            memory_usage

    Raises:
        RuntimeError: If the agent is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    if not hasattr(agent, "performance_history") or agent.performance_history is None:
        agent.performance_history = []

    stats: Dict[str, Any] = agent.get_stats()
    metrics: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "queries": stats.get("queries_processed", 0),
        "tools_called": stats.get("tools_called", 0),
        "avg_response_time": stats.get("avg_response_time", 0.0),
        "errors": stats.get("errors", 0),
        "memory_usage": len(getattr(agent.memory, "messages", [])),
    }

    agent.performance_history.append(metrics)

    if hasattr(agent, "logger"):
        agent.logger.info("performance_metrics_tracked", metrics=metrics)

    return metrics


def show_performance_trends() -> Dict[str, Any]:
    
    """
    Compute simple trend information from agent.performance_history.

    Returns:
        Dict with keys:
            snapshots: Number of snapshots in history.
            latest: Most recent metrics dict.
            growth: Dict with fields:
                query_growth
                avg_response_time_delta
            recent: Up to three most recent snapshots (in time order).

    Raises:
        RuntimeError: If the agent is not initialized or no history is present.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")
    _check(
        hasattr(agent, "performance_history")
        and agent.performance_history not in (None, []),
        "No performance history available.",
    )

    history: List[Dict[str, Any]] = list(agent.performance_history)
    snapshots = len(history)
    first = history[0]
    latest = history[-1]

    growth = {
        "query_growth": latest.get("queries", 0) - first.get("queries", 0),
        "avg_response_time_delta": latest.get("avg_response_time", 0.0)
        - first.get("avg_response_time", 0.0),
    }

    recent = history[-3:]

    return {
        "snapshots": snapshots,
        "latest": latest,
        "growth": growth,
        "recent": recent,
    }


def export_performance_data(filename: str = "performance_data.json") -> str:
    
    """
    Export agent.performance_history to a JSON file.

    Args:
        filename: Target path for the JSON file.

    Returns:
        The filename that was written.

    Raises:
        RuntimeError: If the agent is not initialized or no history is available.
        OSError: If writing the file fails.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")
    _check(
        hasattr(agent, "performance_history")
        and agent.performance_history not in (None, []),
        "No performance history available.",
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(agent.performance_history, f, indent=2)

    if hasattr(agent, "logger"):
        agent.logger.info(
            "performance_data_exported",
            filename=filename,
            snapshots=len(agent.performance_history),
        )

    return filename

print("✔️ Performance monitoring & export tools installed!")
