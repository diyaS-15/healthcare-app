from fastapi import APIRouter, UploadFile, File, Form
import shutil, os, uuid

from services.extractor import extract_text_from_pdf, extract_text_from_image, parse_markers_from_text
from services.normalizer import normalize_markers
from utils.supabase_client import save_report
from services.trend_engine import run_full_analysis
from services.llm_brain import explain_report, follow_up_response, explain_simple

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    report_date: str = Form(...)
):

    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1].lower()
    file_path = f"{UPLOAD_DIR}/{file_id}.{ext}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if ext == "pdf":
        raw_text = extract_text_from_pdf(file_path)
    else:
        raw_text = extract_text_from_image(file_path)

    markers = normalize_markers(parse_markers_from_text(raw_text))

    save_report(user_id, report_date, markers, raw_text)

    analysis = run_full_analysis(user_id)

    explanation = explain_report(
        markers=markers,
        trends=analysis["per_marker"],
        patterns=analysis["patterns"]
    )

    return {
        "markers": markers,
        "trends": analysis["per_marker"],
        "patterns": analysis["patterns"],
        "explanation": explanation
    }


@router.post("/followup")
async def followup(original_analysis: str = Form(...), user_answer: str = Form(...)):
    return {"explanation": follow_up_response(original_analysis, user_answer)}


@router.post("/simple-explain")
async def simple_explain(text: str = Form(...)):
    return {"explanation": explain_simple(text)}


@router.get("/history/{user_id}")
async def get_history(user_id: str):
    return run_full_analysis(user_id)
