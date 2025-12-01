from typing import Any, Dict, List, Optional, Union
import json
from datetime import datetime
import time


def export_conversation_history(filename: str = "conversation_history.txt") -> str:
    
    """
    Export the current agent conversation history and basic statistics to a text file.

    The output is intended for offline inspection and debugging and mirrors the
    structure of the agent's in-memory message store.

    Args:
        filename: Target path for the text file.

    Returns:
        The filename that was written.

    Raises:
        RuntimeError: If the global agent is not initialized.
        OSError: If writing the file fails.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    stats: Dict[str, Any] = agent.get_stats()
    memory_stats: Dict[str, Any] = stats.get("memory_stats", {})
    messages: List[Dict[str, Any]] = list(getattr(agent.memory, "messages", []))

    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("AGENT - CONVERSATION HISTORY\n")
        f.write("=" * 60 + "\n\n")

        f.write("Session Statistics:\n")
        f.write(f"  Total Queries: {stats.get('queries_processed', 0)}\n")
        f.write(f"  Tools Called: {stats.get('tools_called', 0)}\n")
        f.write(
            f"  Average Response Time: "
            f"{stats.get('avg_response_time', 0.0):.2f}s\n"
        )
        f.write(f"  Errors: {stats.get('errors', 0)}\n\n")

        f.write("=" * 60 + "\n")
        f.write("CONVERSATION LOG\n")
        f.write("=" * 60 + "\n\n")

        for msg in messages:
            role = str(msg.get("role", "unknown")).upper()
            timestamp = msg.get("timestamp", "N/A")
            content = str(msg.get("content", ""))

            f.write(f"[{timestamp}] {role}:\n")
            f.write(content + "\n")
            f.write("-" * 60 + "\n\n")

        f.write("=" * 60 + "\n")
        f.write(
            f"Total Messages: {memory_stats.get('total_messages', len(messages))}\n"
        )
        f.write(f"User Messages: {memory_stats.get('user_messages', 0)}\n")
        f.write(f"Agent Messages: {memory_stats.get('agent_messages', 0)}\n")
        f.write("=" * 60 + "\n")

    if hasattr(agent, "logger"):
        agent.logger.info(
            "conversation_history_exported",
            filename=filename,
            stats=stats,
            message_count=len(messages),
        )

    return filename


def export_agent_logs(filename: str = "agent_logs.json") -> str:
    
    """
    Export agent performance metrics, logger output, and conversation messages to JSON.

    Args:
        filename: Target path for the JSON file.

    Returns:
        The filename that was written.

    Raises:
        RuntimeError: If the global agent is not initialized.
        OSError: If writing the file fails.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    stats: Dict[str, Any] = agent.get_stats()

    export_data: Dict[str, Any] = {
        "performance_metrics": {
            "queries_processed": stats.get("queries_processed", 0),
            "tools_called": stats.get("tools_called", 0),
            "avg_response_time": stats.get("avg_response_time", 0.0),
            "errors": stats.get("errors", 0),
        },
        "memory_stats": stats.get("memory_stats", {}),
        "logger_stats": stats.get("logger_stats", {}),
        "logs": list(getattr(getattr(agent, "logger", None), "logs", [])),
        "conversation": list(getattr(agent.memory, "messages", [])),
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)

    if hasattr(agent, "logger"):
        agent.logger.info(
            "agent_logs_exported",
            filename=filename,
            logger_stats=stats.get("logger_stats", {}),
            snapshots=len(export_data["conversation"]),
        )

    return filename


def reset_agent() -> Dict[str, Any]:
    
    """
    Reset the agent state and return statistics from the previous session.

    Returns:
        Dict with keys:
            previous_stats: Statistics snapshot before reset.
            reset: Boolean flag indicating that reset was performed.

    Raises:
        RuntimeError: If the global agent is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    previous_stats: Dict[str, Any] = agent.get_stats()
    agent.reset()

    if hasattr(agent, "logger"):
        agent.logger.info("agent_reset", previous_stats=previous_stats)

    return {"previous_stats": previous_stats, "reset": True}

print("✔️ Conversation history, logging & reset tools installed!")
