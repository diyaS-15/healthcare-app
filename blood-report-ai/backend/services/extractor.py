"""
Blood Report Extractor
Handles PDF and image files → extracts raw text → parses into markers.
Works on both Windows and Linux environments.
"""
import re
import io
import os
import platform
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import openai
import json

from config import get_settings

settings = get_settings()

# Conditional Tesseract path for cross-platform support
if platform.system() == "Windows":
    # Windows path
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
else:
    # Linux/Mac - assumes tesseract is in PATH
    try:
        # Try to find tesseract in PATH
        import shutil
        if shutil.which("tesseract"):
            # tesseract is in PATH, no need to set cmd
            pass
    except Exception:
        pass  # Use system's default PATH


# ─── Text Extraction ────────────────────────────────────────


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_image(file_bytes: bytes) -> str:
    """Extract text from an image using Tesseract OCR."""
    image = Image.open(io.BytesIO(file_bytes))
    # Improve OCR accuracy with preprocessing
    image = image.convert("L")  # Grayscale
    text = pytesseract.image_to_string(image, config="--psm 6")
    return text


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Route to correct extractor based on file type."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp"]:
        return extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ─── LLM Parsing ────────────────────────────────────────────

EXTRACTION_PROMPT = """
You are a medical data parser. Extract all blood test markers from this lab report text.

Return ONLY a JSON object (no markdown, no explanation) with this exact structure:
{
  "report_date": "YYYY-MM-DD or null if not found",
  "lab_name": "lab name or null",
  "markers": [
    {
      "name": "original name as shown in report",
      "value": 12.5,
      "unit": "g/dL",
      "reference_low": 11.5,
      "reference_high": 16.5
    }
  ]
}

Rules:
- Extract every marker with a numeric value
- Include reference ranges if shown
- Use null for missing reference values
- Convert all values to numbers (not strings)
- If date is ambiguous, use null
"""


def parse_markers_with_llm(raw_text: str) -> dict:
    """Parse extracted text into structured medical data using OpenAI."""
    client = openai.OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"Extract markers:\n\n{raw_text[:8000]}"}
        ],
        temperature=0,
        max_tokens=2000,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


def extract_report(file_bytes: bytes, filename: str) -> dict:
    """
    Full pipeline: file → text → structured JSON.
    Returns dict with report_date, lab_name, markers list.
    """
    raw_text = extract_text(file_bytes, filename)
    if len(raw_text.strip()) < 50:
        raise ValueError("Could not extract enough text from this file. Try a clearer image.")
    parsed = parse_markers_with_llm(raw_text)
    return parsed
