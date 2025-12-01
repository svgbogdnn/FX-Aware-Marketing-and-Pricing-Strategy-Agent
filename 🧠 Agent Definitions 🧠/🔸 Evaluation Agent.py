from typing import Optional

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.genai import types


evaluation_agent = Agent(
    model=model,
    name="evaluation_agent",
    description=(
        "Agent that evaluates the quality and completeness of an executive decision brief "
        "and provides a structured score and feedback."
    ),
    instruction=(
        "You are an internal quality reviewer for AI-generated decision briefs.\n\n"
        "You receive as input:\n"
        "- The final decision brief text produced for a marketing or procurement manager.\n"
        "- The structured JSON summary that the brief is supposed to reflect.\n\n"
        "Your task is to assess how well the brief meets the intended requirements:\n"
        "1) Coverage: Does it clearly address market overview, competitive pricing, FX risk, and pricing strategy?\n"
        "2) Consistency: Is the narrative consistent with the numbers and structure in the JSON summary?\n"
        "3) Clarity: Is the language clear, concise, and suitable for an executive audience?\n"
        "4) Actionability: Does it provide a clear recommendation and highlight key risks and trade-offs?\n\n"
        "You must produce two outputs:\n"
        "A) A short textual critique (2–4 paragraphs) that:\n"
        "   - Highlights strengths of the brief.\n"
        "   - Points out any gaps, inconsistencies, or confusing parts.\n"
        "   - Suggests concrete improvements if needed.\n"
        "B) A JSON object with the following exact structure:\n"
        "{\n"
        "  \"overall_score\": float,\n"
        "  \"dimensions\": {\n"
        "    \"coverage\": float,\n"
        "    \"consistency\": float,\n"
        "    \"clarity\": float,\n"
        "    \"actionability\": float\n"
        "  },\n"
        "  \"flags\": [str],\n"
        "  \"summary_comment\": str\n"
        "}\n\n"
        "Scoring guidelines:\n"
        "- Use a 0.0–5.0 scale for all scores, where 5.0 is excellent and 3.0 is acceptable.\n"
        "- The overall_score should roughly reflect the average of the four dimensions, but you may adjust it\n"
        "  slightly if one dimension is much weaker or stronger than the others.\n"
        "- The flags array should contain short machine-readable notes such as\n"
        "  'missing_fx_section', 'weak_recommendation', 'good_structure', etc.\n"
        "- The summary_comment should be a 1–2 sentence executive summary of your assessment.\n\n"
        "If the brief is missing entire sections, or the JSON summary is obviously malformed or empty, clearly\n        "
        "state this in both the critique and flags, and assign lower scores.\n"
        "Do not rewrite the brief; focus on evaluation and feedback only."
    ),
    tools=[],
)


evaluation_tool = AgentTool(evaluation_agent)


def build_evaluation_prompt(
    decision_brief_text: str,
    structured_summary_json: str,
    context_notes: Optional[str] = None,
) -> str:
    """
    Build a prompt for the evaluation_agent.

    Args:
        decision_brief_text: The full text of the decision brief as produced by the decision_brief_agent.
        structured_summary_json: The JSON block labeled STRUCTURED_SUMMARY_JSON that the brief is supposed to reflect.
        context_notes: Optional notes from the orchestrator, such as which sections were expected.

    Returns:
        A formatted prompt string for the evaluation_agent.
    """
    notes_block = (
        f"\nADDITIONAL_CONTEXT_NOTES:\n{context_notes}\n"
        if context_notes
        else ""
    )

    return (
        "You are asked to evaluate the following AI-generated decision brief and its structured summary.\n\n"
        "DECISION_BRIEF_TEXT:\n"
        f"{decision_brief_text}\n\n"
        "STRUCTURED_SUMMARY_JSON:\n"
        f"{structured_summary_json}\n"
        f"{notes_block}\n"
        "Read both carefully and then provide:\n"
        "1) A concise critique as described in your instructions.\n"
        "2) A JSON object with the exact schema requested in your instructions."
    )

print("✔️ Evaluation Agent installed!")
