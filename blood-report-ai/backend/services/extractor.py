"""
Blood Report Extractor
Handles PDF and image files → extracts raw text → parses into markers.
Works on both Windows and Linux environments.
Optimized for blood test documents with advanced OCR preprocessing.
"""
"""
Production-Grade Blood Report Extractor
Robust OCR + LLM + Fallback Parsing + Validation
"""

import re
import io
import os
import platform
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - handled at runtime
    fitz = None
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
try:
    import openai
except ImportError:  # pragma: no cover - handled at runtime
    openai = None
import json
import shutil

from config import get_settings

settings = get_settings()
DEFAULT_EXTRACTION_MODEL = os.getenv("OPENAI_EXTRACTION_MODEL", "").strip() or os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini"

# ─────────────────────────────────────────
# Tesseract Setup
# ─────────────────────────────────────────
if platform.system() == "Windows":
    for path in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# ─────────────────────────────────────────
# Image Preprocessing
# ─────────────────────────────────────────
def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        image = image.convert("RGB")

    if image.width < 800:
        scale = 800 / image.width
        image = image.resize(
            (int(image.width * scale), int(image.height * scale)),
            Image.Resampling.LANCZOS,
        )

    image = image.convert("L")

    image = ImageEnhance.Contrast(image).enhance(2.2)
    image = ImageEnhance.Brightness(image).enhance(1.1)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = ImageEnhance.Sharpness(image).enhance(2.0)

    return image


# ─────────────────────────────────────────
# OCR Helpers
# ─────────────────────────────────────────
def is_text_valid(text: str) -> bool:
    if len(text.strip()) < 80:
        return False
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    return alpha_ratio > 0.5


def ocr_image(image: Image.Image) -> str:
    config = "--psm 6 --oem 3 -c preserve_interword_spaces=1"
    return pytesseract.image_to_string(image, config=config)


# ─────────────────────────────────────────
# Text Extraction
# ─────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    if fitz is None:
        raise RuntimeError("PyMuPDF is not installed, so PDF extraction is unavailable.")
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""

    for i, page in enumerate(doc):
        page_text = page.get_text()

        if not is_text_valid(page_text):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img = preprocess_image_for_ocr(img)
            page_text = ocr_image(img)

        text += f"\n--- Page {i+1} ---\n{page_text}"

    return text


def extract_text_from_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    image = preprocess_image_for_ocr(image)
    return ocr_image(image)


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp"]:
        return extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ─────────────────────────────────────────
# Cleaning
# ─────────────────────────────────────────
def clean_text(text: str) -> str:
    text = re.sub(r"[ ]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    fixes = {
        "0O": "OO",
        "l0": "10",
        "rn": "m",
    }
    for k, v in fixes.items():
        text = text.replace(k, v)

    return text.strip()


# ─────────────────────────────────────────
# Chunking
# ─────────────────────────────────────────
def chunk_text(text: str, size=4000):
    return [text[i:i + size] for i in range(0, len(text), size)]


# ─────────────────────────────────────────
# LLM Prompt
# ─────────────────────────────────────────
EXTRACTION_PROMPT = """
You are an expert medical data parser.

Extract ALL blood test markers from lab reports.

Return ONLY JSON:
{
  "report_date": "YYYY-MM-DD or null",
  "lab_name": "string or null",
  "patient_name": "string or null",
  "markers": [
    {
      "name": "string",
      "value": number,
      "unit": "string",
      "reference_low": number or null,
      "reference_high": number or null,
      "confidence": number (0-1)
    }
  ]
}

Rules:
- Extract ALL markers with numbers
- Reports are often tables
- Use null if missing
- Do not hallucinate values
"""


# ─────────────────────────────────────────
# LLM Parsing (Chunked)
# ─────────────────────────────────────────
def parse_with_llm(text: str):
    if openai is None:
        raise RuntimeError("openai package is not installed")
    client = openai.OpenAI(api_key=settings.openai_api_key)
    chunks = chunk_text(text)

    all_markers = []
    meta = {}

    for chunk in chunks:
        res = client.chat.completions.create(
            model=DEFAULT_EXTRACTION_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": chunk},
            ],
        )

        data = json.loads(res.choices[0].message.content)

        all_markers.extend(data.get("markers", []))

        for key in ["report_date", "lab_name", "patient_name"]:
            if data.get(key) and not meta.get(key):
                meta[key] = data[key]

    meta["markers"] = all_markers
    return meta


# ─────────────────────────────────────────
# Regex Fallback
# ─────────────────────────────────────────
def regex_fallback(text: str):
    pattern = re.findall(
        r"([A-Za-z ]+)\s+([\d.]+)\s*([a-zA-Z/%]+)?\s*\(?([\d.]*)-?([\d.]*)\)?",
        text,
    )

    markers = []

    for name, val, unit, low, high in pattern:
        try:
            markers.append({
                "name": name.strip(),
                "value": float(val),
                "unit": unit or "",
                "reference_low": float(low) if low else None,
                "reference_high": float(high) if high else None,
                "confidence": 0.6,
            })
        except:
            continue

    return markers


# ─────────────────────────────────────────
# Deduplication
# ─────────────────────────────────────────
def normalize(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def deduplicate(markers):
    seen = {}
    for m in markers:
        key = normalize(m["name"])
        if key not in seen or m["confidence"] > seen[key]["confidence"]:
            seen[key] = m
    return list(seen.values())


# ─────────────────────────────────────────
# Status Calculation
# ─────────────────────────────────────────
def compute_status(marker):
    val = marker["value"]
    low = marker.get("reference_low")
    high = marker.get("reference_high")

    if low is None or high is None:
        return "unknown"

    if val < low:
        return "low"
    elif val > high:
        return "high"
    return "normal"


# ─────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────
def extract_report(file_bytes: bytes, filename: str):
    text = extract_text(file_bytes, filename)
    text = clean_text(text)

    if len(text) < 50:
        raise ValueError("Not enough text extracted")

    # LLM
    try:
        parsed = parse_with_llm(text)
    except Exception:
        parsed = {
            "report_date": None,
            "lab_name": None,
            "patient_name": None,
            "markers": [],
        }

    # Fallback
    fallback = regex_fallback(text)

    markers = parsed.get("markers", []) + fallback

    # Deduplicate
    markers = deduplicate(markers)

    # Validate + enrich
    final = []
    for m in markers:
        try:
            m["value"] = float(m["value"])
            m["status"] = compute_status(m)

            if m.get("confidence", 0.6) >= 0.5:
                final.append(m)
        except:
            continue

    if not final:
        raise ValueError("No valid markers found")

    return {
        "report_date": parsed.get("report_date"),
        "lab_name": parsed.get("lab_name"),
        "patient_name": parsed.get("patient_name"),
        "markers": final,
        "count": len(final),
    }
