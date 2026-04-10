import openai, os, json
from dotenv import load_dotenv
load_dotenv()
from rag import retrieve_context


openai.api_key = os.getenv("OPENAI_API_KEY")

MASTER_SYSTEM_PROMPT = """
You are a health information assistant that helps people understand their blood test results.

STRICT RULES — follow these every single response:
1. NEVER diagnose any condition or disease
2. NEVER name specific diseases based on marker values
3. NEVER say "you have" or "you might have" 
4. ONLY explain what markers measure in general terms
5. Use simple, everyday language (8th grade reading level)
6. Always end with: "These observations are educational only. Please discuss with your healthcare provider."
7. Use phrases like: "commonly monitored in relation to...", "often associated with...", "people tracking this typically..."

When explaining trends:
- Describe direction and magnitude in plain English
- Explain what the marker generally measures
- Avoid clinical alarm language; be calm and informative

When generating questions:
- Ask about lifestyle factors only (diet, sleep, exercise, stress, travel)
- Never ask medical history questions
- Never imply a specific condition

Format responses clearly with sections:
[SUMMARY], [MARKER DETAILS], [TRENDS], [QUESTIONS FOR YOU]
"""

def explain_report(markers: list, trends: dict, patterns: list, user_context: str = "") -> str:
    trend_summary = json.dumps(trends, indent=2)
    pattern_summary = json.dumps(patterns, indent=2)

    user_message = f"""
    Here is a patient's blood report data for educational explanation:

    CURRENT MARKERS:
    {json.dumps(markers, indent=2)}

    TREND ANALYSIS ACROSS ALL REPORTS:
    {trend_summary}

    CROSS-MARKER PATTERNS DETECTED:
    {pattern_summary}

    USER CONTEXT (from previous questions):
    {user_context if user_context else "No additional context yet."}

    Please provide:
    1. A simple summary (2-3 sentences, plain English)
    2. For each marker with a notable trend, explain what changed and what that marker generally does
    3. Note any cross-marker patterns in general educational terms
    4. Generate 3 follow-up questions to better understand lifestyle context
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": MASTER_SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.4,
        max_tokens=1200
    )
    return response.choices[0].message.content

def follow_up_response(original_analysis: str, user_answer: str) -> str:
    """Re-contextualizes the explanation based on user's answer to a question."""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",    "content": MASTER_SYSTEM_PROMPT},
            {"role": "assistant", "content": original_analysis},
            {"role": "user",      "content": f"My answer to your question: {user_answer}. Please update your explanation with this context."}
        ],
        temperature=0.4,
        max_tokens=800
    )
    return response.choices[0].message.content

def explain_simple(text: str) -> str:
    """'Explain like I'm 15' mode."""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": MASTER_SYSTEM_PROMPT + "\nNow explain everything as if talking to a curious 15-year-old. Use analogies and comparisons to everyday things."},
            {"role": "user",   "content": text}
        ],
        temperature=0.5,
        max_tokens=600
    )
    return response.choices[0].message.content