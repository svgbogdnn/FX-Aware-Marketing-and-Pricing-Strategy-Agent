def batch_query(questions: Union[str, List[str]]) -> Dict[str, Any]:
    
    """
    Run a batch of questions through the agent and collect responses.

    Args:
        questions: Either a list of questions or a single string with
            semicolon-separated questions.

    Returns:
        Dict with keys:
            results: Mapping question -> {response, status, error?}.
            summary: Aggregate statistics over the batch.

    Raises:
        RuntimeError: If the agent is not initialized or no questions are provided.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    if isinstance(questions, str):
        parsed = [q.strip() for q in questions.split(";") if q.strip()]
    else:
        parsed = [str(q).strip() for q in questions if str(q).strip()]

    _check(len(parsed) > 0, "No questions provided for batch_query")

    results: Dict[str, Dict[str, Any]] = {}
    start_time = time.time()

    for question in parsed:
        try:
            response = agent.run(question)
            results[question] = {"response": response, "status": "success"}
        except Exception as exc:
            results[question] = {
                "response": None,
                "status": "error",
                "error": str(exc),
            }

    total_time = time.time() - start_time
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    error_count = len(results) - success_count

    summary = {
        "total": len(results),
        "success": success_count,
        "error": error_count,
        "total_time_seconds": total_time,
        "avg_time_per_query_seconds": total_time / len(results),
    }

    if hasattr(agent, "logger"):
        agent.logger.info(
            "batch_query_completed",
            summary=summary,
        )

    return {"results": results, "summary": summary}


def display_batch_results(
    results: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    
    """
    Convert a batch_query results mapping into a sorted list of entries.

    This is useful for rendering or further processing in UIs or notebooks.

    Args:
        results: Mapping produced by batch_query()["results"].

    Returns:
        List of dicts with keys:
            question
            response
            status
            error (optional)
    """
    
    entries: List[Dict[str, Any]] = []

    for question, payload in results.items():
        entry = {"question": question}
        entry.update(payload)
        entries.append(entry)

    entries.sort(key=lambda e: e["question"])
    return entries


def summarize_conversation() -> Dict[str, Any]:
    
    """
    Produce a lightweight heuristic summary of the current conversation.

    The summary is based on simple keyword scanning of user messages.

    Returns:
        Dict with keys:
            summary_text: Multi-line human-readable summary.
            summary_points: List of distinct bullet points.
            message_count: Total number of messages observed.

    Raises:
        RuntimeError: If the agent is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    messages: List[Dict[str, Any]] = list(getattr(agent.memory, "messages", []))
    message_count = len(messages)

    if message_count < 5:
        return {
            "summary_text": "",
            "summary_points": [],
            "message_count": message_count,
        }

    points: List[str] = []

    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = str(msg.get("content", "")).lower()

        if "feature" in content:
            points.append("Feature engineering was discussed.")
        if "model" in content or "xgboost" in content:
            points.append("Model development and tuning were discussed.")
        if "debug" in content or "error" in content:
            points.append("Debugging and error analysis were discussed.")
        if "metric" in content or "score" in content:
            points.append("Evaluation metrics and scores were discussed.")
        if "data" in content or "dataset" in content:
            points.append("Data and dataset handling were discussed.")
        if "competition" in content or "leaderboard" in content:
            points.append("Competition context and leaderboard were discussed.")
        if "baseline" in content:
            points.append("Baseline approaches were discussed.")
        if "strategy" in content or "plan" in content:
            points.append("Competition strategy and planning were discussed.")
        if "insight" in content or "discussion" in content:
            points.append("High-level insights and discussion were captured.")

    distinct_points = sorted(set(points))

    summary_lines = ["Conversation Summary:"]
    summary_lines.extend(f"- {p}" for p in distinct_points)
    summary_text = "\n".join(summary_lines)

    return {
        "summary_text": summary_text,
        "summary_points": distinct_points,
        "message_count": message_count,
    }


def auto_summarize_if_needed() -> Dict[str, Any]:
    
    """
    Automatically summarize the conversation and compress memory if it grows too long.

    If the number of stored messages exceeds a threshold, summarize_conversation is
    called and the raw messages are replaced with a single system summary.

    Returns:
        Dict with keys:
            performed: Whether summarization was executed.
            summary: Summary payload from summarize_conversation (if performed).
            message_count_before: Messages before summarization.
            message_count_after: Messages after summarization.

    Raises:
        RuntimeError: If the agent is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    messages: List[Dict[str, Any]] = list(getattr(agent.memory, "messages", []))
    message_count_before = len(messages)

    threshold = 15
    if message_count_before < threshold:
        return {
            "performed": False,
            "summary": None,
            "message_count_before": message_count_before,
            "message_count_after": message_count_before,
        }

    summary = summarize_conversation()

    agent.memory.clear()
    if summary["summary_text"]:
        agent.memory.add_message("system", summary["summary_text"])

    message_count_after = len(getattr(agent.memory, "messages", []))

    if hasattr(agent, "logger"):
        agent.logger.info(
            "auto_summarize_completed",
            threshold=threshold,
            before=message_count_before,
            after=message_count_after,
        )

    return {
        "performed": True,
        "summary": summary,
        "message_count_before": message_count_before,
        "message_count_after": message_count_after,
    }

print("✔️ Batch execution & summarization tools installed!")
