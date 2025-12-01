def collect_feedback(
    question: str,
    response: str,
    rating: Optional[int] = None,
    comments: Optional[str] = None,
) -> Dict[str, Any]:
    
    """
    Record structured feedback for a given Q&A pair.

    Args:
        question: Original user question.
        response: Agent response text.
        rating: Optional numeric rating, typically in [1, 5].
        comments: Optional free-form feedback text.

    Returns:
        The feedback entry dict that was stored.

    Raises:
        RuntimeError: If the agent is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    entry: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "response": response,
        "rating": rating,
        "comments": comments,
    }

    if not hasattr(agent, "feedback") or agent.feedback is None:
        agent.feedback = []

    agent.feedback.append(entry)

    if hasattr(agent, "logger"):
        agent.logger.info("feedback_collected", entry=entry)

    return entry


def show_feedback_summary() -> Dict[str, Any]:
    
    """
    Aggregate basic statistics over collected feedback entries.

    Returns:
        Dict with keys:
            total: Number of feedback entries.
            average_rating: Average rating over non-null ratings (or None).
            with_comments: Count of entries that include comments.
            recent: Up to three most recent feedback entries.

    Raises:
        RuntimeError: If the agent is not initialized.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    feedback: List[Dict[str, Any]] = list(getattr(agent, "feedback", []) or [])
    total = len(feedback)

    if total == 0:
        return {
            "total": 0,
            "average_rating": None,
            "with_comments": 0,
            "recent": [],
        }

    ratings = [f["rating"] for f in feedback if f.get("rating") is not None]
    average_rating = sum(ratings) / len(ratings) if ratings else None
    with_comments = sum(1 for f in feedback if f.get("comments"))

    recent = feedback[-3:]

    return {
        "total": total,
        "average_rating": average_rating,
        "with_comments": with_comments,
        "recent": recent,
    }


def validate_response(question: str, response: str) -> Dict[str, Any]:
    
    """
    Run a set of simple heuristic quality checks over a response.

    Checks are intentionally lightweight and interpretable and can be extended.

    Args:
        question: Original user question.
        response: Agent response text.

    Returns:
        Dict with keys:
            score: Total number of checks passed.
            max_score: Total number of checks.
            checks: Mapping of check name -> bool.
            feedback: List of human-readable suggestions.
    """
    
    _check("agent" in globals() and agent is not None, "Agent not initialized")

    text = response.strip()
    lower = text.lower()

    checks: Dict[str, bool] = {
        "min_length": len(text) >= 50,
        "has_examples": "for example" in lower or "e.g." in lower,
        "has_structure": "\n\n" in text or "- " in text or "1." in text,
        "mentions_limitations": "cannot" in lower or "as an ai" in lower,
        "addresses_question": any(
            token in lower for token in question.lower().split()[:5]
        ),
    }

    feedback: List[str] = []

    if not checks["min_length"]:
        feedback.append("Response is very short; consider adding more detail.")
    if not checks["has_examples"]:
        feedback.append("Add at least one concrete example.")
    if not checks["has_structure"]:
        feedback.append("Use paragraphs or bullet points to structure the answer.")
    if not checks["addresses_question"]:
        feedback.append("Ensure the response explicitly addresses the user's question.")

    score = sum(1 for v in checks.values() if v)
    max_score = len(checks)

    result = {
        "score": score,
        "max_score": max_score,
        "checks": checks,
        "feedback": feedback,
    }

    if hasattr(agent, "logger"):
        agent.logger.info("response_validated", result=result)

    return result


def auto_validate_response(question: str, response: str) -> Dict[str, Any]:
    
    """
    Convenience wrapper around validate_response that adds an acceptability flag.

    Args:
        question: Original user question.
        response: Agent response text.

    Returns:
        Dict returned by validate_response with an additional key:
            is_acceptable: True if the score passes a simple threshold.
    """
    
    result = validate_response(question, response)

    threshold = max(1, int(round(0.6 * result["max_score"])))
    result["is_acceptable"] = result["score"] >= threshold

    return result

print("✔️ Feedback & response quality tools installed!")
