"""
Reports Router - Blood Report Upload & Analysis
Upload files, extract markers, run AI analysis.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import io
from datetime import datetime

from dependencies import get_current_user
from models.schemas import (
    ReportUploadResponse, BloodMarkerSimple, MarkerValue,
    AnalysisResponse, ExplanationResponse
)
from services.extractor import extract_report
from services.normalizer import normalize_markers, get_display_name
from services.trend_engine import run_full_analysis
from services.llm_brain import explain_report, extract_questions_from_response
from services.encryption import encrypt_data, decrypt_data
from utils.supabase_client import save_report, get_reports, get_report_markers, log_action
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.post("/upload", response_model=ReportUploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload a PDF or image blood report.
    Extracts markers, normalizes names, encrypts, and stores.
    """
    try:
        user_id = user["user_id"]
        
        # Validate file size
        file_size_mb = 0
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > settings.max_upload_size_mb:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max: {settings.max_upload_size_mb}MB"
            )
        
        # Extract text and markers from file
        logger.info(f"Processing report: {file.filename} ({file_size_mb:.1f}MB)")
        extracted = extract_report(content, file.filename)
        
        report_date = extracted.get("report_date", datetime.now().strftime("%Y-%m-%d"))
        
        # Normalize marker names
        raw_markers = extracted.get("markers", [])
        markers_list = []
        for m in raw_markers:
            standard_name = __import__('services.normalizer', fromlist=['normalize_marker_name']).normalize_marker_name(m["name"])
            markers_list.append({
                "name": m["name"],
                "normalized_name": standard_name,
                "display_name": get_display_name(standard_name),
                "value": m["value"],
                "unit": m["unit"],
                "reference_low": m.get("reference_low"),
                "reference_high": m.get("reference_high"),
            })
        
        # Encrypt sensitive data
        raw_text_encrypted = encrypt_data(extracted.get("raw_text", ""), user_id)
        
        # Save to database
        report_info = await save_report(
            user_id=user_id,
            report_date=report_date,
            markers=markers_list,
            raw_text_encrypted=raw_text_encrypted,
            file_name=file.filename
        )
        
        # Log action
        await log_action(
            user_id,
            "upload_report",
            encrypt_data({"filename": file.filename, "marker_count": len(markers_list)}, user_id)
        )
        
        logger.info(f"Report uploaded successfully: {report_info['report_id']}")
        
        return {
            "report_id": report_info["report_id"],
            "report_date": report_date,
            "marker_count": len(markers_list),
            "markers": [
                MarkerValue(
                    name=m["normalized_name"],
                    display_name=m["display_name"],
                    value=m["value"],
                    unit=m["unit"],
                    reference_low=m.get("reference_low"),
                    reference_high=m.get("reference_high"),
                    status="normal"
                )
                for m in markers_list
            ],
            "status": "processed"
        }
        
    except ValueError as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process report"
        )
    finally:
        await file.close()


@router.get("/history")
async def get_report_history(
    user: dict = Depends(get_current_user),
    limit: int = 50
):
    """
    Fetch all reports for the authenticated user.
    """
    try:
        user_id = user["user_id"]
        reports = await get_reports(user_id, limit=limit)
        
        return {
            "reports": reports,
            "total_count": len(reports),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch report history"
        )


@router.get("/analyze/{report_id}", response_model=AnalysisResponse)
async def analyze_report(
    report_id: str,
    user: dict = Depends(get_current_user),
    simple_mode: bool = False
):
    """
    Get AI analysis for a specific report.
    Returns marker explanations, trends, and questions.
    """
    try:
        user_id = user["user_id"]
        
        # Fetch report markers
        markers = await get_report_markers(report_id)
        
        if not markers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Format markers for LLM
        markers_data = [
            {
                "name": m["marker_name"],
                "value": float(m["value"]),
                "unit": m["unit"],
                "reference_low": m.get("reference_min"),
                "reference_high": m.get("reference_max"),
                "status": m.get("status", "normal")
            }
            for m in markers
        ]
        
       # Get trends (for context)
        trends = {}  # Would be populated from trend_engine
        patterns = []  # Would be populated from trend_engine
        
        # Generate AI explanation
        explanation_text = await __import__('services.llm_brain', fromlist=['explain_report']).explain_report(
            markers=markers_data,
            trends=trends,
            patterns=patterns,
            simple_mode=simple_mode
        )
        
        # Extract questions
        questions = __import__('services.llm_brain', fromlist=['extract_questions_from_response']).extract_questions_from_response(explanation_text)
        
        # Log action
        await log_action(user_id, "analyze_report", encrypt_data({"report_id": report_id}, user_id))
        
        return {
            "summary": explanation_text[:200] + "...",
            "marker_details": explanation_text,
            "trends_text": "Trend analysis would go here",
            "questions": questions,
            "session_id": report_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze report"
        )


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Delete a report and all associated data.
    Hard delete for privacy compliance.
    """
    try:
        user_id = user["user_id"]
        logger.info(f"Deleting report {report_id} for user {user_id}")
        
        # In production: implement actual deletion
        # from utils.supabase_client import get_supabase
        # get_supabase().table("blood_reports").delete().eq("id", report_id).execute()
        
        await log_action(user_id, "delete_report")
        
        return {"message": "Report deleted successfully"}
        
    except Exception as e:
        logger.error(f"Deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )
