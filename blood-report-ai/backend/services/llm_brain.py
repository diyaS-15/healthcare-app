"""
LLM brain utilities for report explanation
Uses OpenAI GPT-4 for medical insights
IMPORTANT: This tool provides EDUCATIONAL analysis only, NOT medical diagnosis
"""
import json
import openai
from config import get_settings

settings = get_settings()

# Safety disclaimer to include in all responses
MEDICAL_DISCLAIMER = """
⚠️ IMPORTANT: This analysis is for educational purposes only and does NOT constitute medical advice or diagnosis.
Always consult with a qualified healthcare provider for any medical concerns.
"""


def _get_client():
    """Initialize OpenAI client."""
    return openai.OpenAI(api_key=settings.openai_api_key)


def explain_report(report: dict) -> str:
    """
    Generate a comprehensive educational explanation of a blood report using GPT-4.
    IMPORTANT: This is NOT a diagnostic tool - provides educational information only.
    """
    markers = report.get("markers", [])
    report_date = report.get("report_date", "Unknown date")
    lab_name = report.get("lab_name", "Unknown lab")

    if not markers:
        return "No markers found in report for analysis."

    marker_text = "\n".join([
        f"- {m.get('name', 'Unknown')}: {m.get('value')} {m.get('unit', '')} "
        f"(ref: {m.get('reference_low', 'N/A')}-{m.get('reference_high', 'N/A')})"
        for m in markers
    ])

    prompt = f"""
    You are an EDUCATIONAL health information assistant. You are NOT a doctor and cannot diagnose.
    
    CRITICAL RULES:
    1. NEVER diagnose or suggest medical conditions
    2. NEVER prescribe treatments or medications
    3. NEVER suggest the patient has a disease or disorder
    4. ALWAYS recommend consulting a healthcare provider
    5. Provide ONLY educational information about markers
    6. Include the medical disclaimer with your response
    
    Report Date: {report_date}
    Lab: {lab_name}
    
    Markers:
    {marker_text}
    
    Please provide:
    1. What each abnormal value MIGHT indicate (educationally)
    2. General information about what causes values to be outside normal ranges
    3. Lifestyle factors that can support healthy marker levels
    4. Why consulting a healthcare provider is important
    
    REMEMBER: You are providing EDUCATIONAL information, NOT diagnosis.
    Always emphasize this is not medical advice.
    """

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an EDUCATIONAL health assistant. You CANNOT and WILL NOT diagnose diseases. You provide general health information and ALWAYS recommend consulting healthcare providers. Every response must include the medical disclaimer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content + "\n\n" + MEDICAL_DISCLAIMER
    except Exception as e:
        # Fallback to basic explanation if API fails
        return _fallback_explain_report(markers) + "\n\n" + MEDICAL_DISCLAIMER


def _fallback_explain_report(markers: list) -> str:
    """Fallback basic explanation when API fails."""
    abnormal = []
    
    for m in markers:
        value = m.get("value")
        low = m.get("reference_low")
        high = m.get("reference_high")
        name = m.get("name", "Unknown")
        
        if value is None:
            continue
        
        if low is not None and value < low:
            abnormal.append(f"{name} is below normal range ({value} < {low})")
        elif high is not None and value > high:
            abnormal.append(f"{name} is above normal range ({value} > {high})")
    
    if not abnormal:
        return "All markers appear within normal reference ranges."
    
    return "Findings:\n- " + "\n- ".join(abnormal)


def general_chat(message: str, context: str = "") -> str:
    """
    Handle general health questions using GPT-4.
    CRITICAL: This is NOT a diagnostic or medical advice tool.
    """
    system_prompt = """You are an EDUCATIONAL health information assistant. CRITICAL RULES:
    1. NEVER diagnose diseases or medical conditions
    2. NEVER prescribe treatments or medications
    3. NEVER suggest what disease someone might have
    4. ALWAYS recommend consulting a healthcare provider for medical concerns
    5. Provide ONLY general, educational information
    6. If someone describes symptoms, NEVER suggest causes or diagnosis
    7. Include medical disclaimer in responses about health concerns
    
    You can explain what blood markers mean generally, but NEVER diagnose based on them.
    Always be helpful but firm about this being educational only."""
    
    if context:
        system_prompt += f"\n\nGeneral context about the user's markers: {context}"
    
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        result = response.choices[0].message.content
        
        # Always include disclaimer for health-related queries
        if any(keyword in message.lower() for keyword in ["health", "symptom", "disease", "condition", "sick", "ill"]):
            result += "\n\n" + MEDICAL_DISCLAIMER
        
        return result
    except Exception as e:
        return f"I encountered an error processing your question: {str(e)}. Please consult a healthcare provider for medical concerns."


def follow_up_response(original_analysis: str, user_answer: str) -> str:
    """Handle follow-up questions about the analysis using GPT-4."""
    prompt = f"""
    Original Analysis:
    {original_analysis}
    
    User Follow-up Question:
    {user_answer}
    
    Please provide a helpful response to the user's follow-up question, staying consistent with the original analysis.
    """
    
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant answering follow-up questions about blood report analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I'd be happy to help with that follow-up question, but I'm having technical difficulties. Please try again."


def explain_simple(text: str) -> str:
    """Simplify complex medical terminology in text."""
    prompt = f"""Simplify this medical text for a patient to understand. Use clear, everyday language.
    Keep it concise but complete.
    
    Text: {text}"""
    
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You simplify medical terminology into everyday language for patients."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception:
        return text  # Return original if simplification fails


def extract_questions_from_response(text: str) -> list:
    """Extract clarifying questions from AI-generated analysis for follow-up."""
    prompt = f"""From this medical analysis, extract 2-3 important follow-up questions 
    that would help the patient better understand their results. Return as a JSON list.
    
    Analysis: {text}
    
    Return format:
    {{"questions": ["question 1", "question 2", "question 3"]}}
    """
    
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You extract clarifying questions from medical analyses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [])
    except Exception:
        return []  # Return empty list if extraction fails