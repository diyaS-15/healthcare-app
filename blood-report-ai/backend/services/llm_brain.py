"""
LLM brain utilities for report explanation
"""

def explain_report(report: dict) -> str:
    """
    Generate a simple human-readable explanation of a blood report.
    """
    markers = report.get("markers", [])

    if not markers:
        return "No markers found in report."

    abnormal = []

    for m in markers:
        value = m.get("value")
        low = m.get("reference_low")
        high = m.get("reference_high")

        if value is None:
            continue

        if low is not None and value < low:
            abnormal.append(f"{m.get('name')} is low")
        elif high is not None and value > high:
            abnormal.append(f"{m.get('name')} is high")

    if not abnormal:
        return "All markers appear within normal range."

    return "Findings:\n- " + "\n- ".join(abnormal)


def general_chat(message: str, context: str = "") -> str:
    """Handle general chat messages."""
    return f"Assistant: {message}"


def follow_up_response(original_analysis: str, user_answer: str) -> str:
    """Handle follow-up questions about the analysis."""
    return "Thank you for your response."


def explain_simple(text: str) -> str:
    """Simple explanation of medical text."""
    return text


def extract_questions_from_response(text: str) -> list:
    """
    Extract user-facing questions from AI output (placeholder logic).
    """
    return []