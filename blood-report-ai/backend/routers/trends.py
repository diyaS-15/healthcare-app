"""
Trends Router - Trend Analysis Endpoints
Fetch marker trends, cross-marker patterns, stability scores.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from datetime import datetime

from dependencies import get_current_user
from models.schemas import TrendsResponse, MarkerTrend, TrendPoint
from services.trend_engine import run_full_analysis
from utils.supabase_client import get_reports, get_report_markers, get_trends
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.get("/analysis", response_model=TrendsResponse)
async def get_trend_analysis(user: dict = Depends(get_current_user)):
    """
    Get comprehensive trend analysis for the user.
    Analyzes all reports over time to detect patterns.
    """
    try:
        user_id = user["user_id"]
        
        # Fetch all reports for this user
        reports = await get_reports(user_id)
        
        if not reports:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reports found. Upload a report first."
            )
        
        # Organize markers by name with values over time
        markers_over_time = {}
        
        for report in reports:
            report_date = report.get("report_date", "")
            markers = await get_report_markers(report["id"])
            
            for marker in markers:
                marker_name = marker["marker_name"]
                
                if marker_name not in markers_over_time:
                    markers_over_time[marker_name] = []
                
                markers_over_time[marker_name].append({
                    "date": report_date,
                    "value": float(marker["value"])
                })
        
        # Run trend analysis
        analysis = run_full_analysis(markers_over_time)
        
        # Format response
        trends = []
        per_marker = analysis.get("per_marker", {})
        
        for marker_name, metrics in per_marker.items():
            # Get historical values if available
            values = markers_over_time.get(marker_name, [])
            sorted_values = sorted(values, key=lambda x: x["date"])
            
            trend = MarkerTrend(
                marker_name=marker_name,
                display_name=marker_name.replace("_", " ").title(),
                unit="",  # Would need to fetch from markers
                direction=metrics.get("direction", "insufficient_data"),
                change_percent=metrics.get("change_percent", 0),
                consistency=metrics.get("consistency", "unknown"),
                data_points=[
                    TrendPoint(date=v["date"], value=v["value"])
                    for v in sorted_values
                ],
                interpretation=f"{marker_name} is {metrics.get('direction', 'unknown')}",
                recent_value=metrics.get("newest_value"),
                oldest_value=metrics.get("oldest_value"),
            )
            trends.append(trend)
        
        return {
            "trends": trends,
            "cross_marker_patterns": analysis.get("patterns", []),
            "report_count": len(reports),
            "date_range": {
                "from": min((r.get("report_date") for r in reports), default=""),
                "to": max((r.get("report_date") for r in reports), default="")
            },
            "updated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trend analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze trends"
        )


@router.get("/marker/{marker_name}")
async def get_marker_trend(
    marker_name: str,
    user: dict = Depends(get_current_user)
):
    """
    Get detailed trend for a specific marker.
    Shows historical values, direction, and interpretation.
    """
    try:
        user_id = user["user_id"]
        
        # Fetch all reports
        reports = await get_reports(user_id)
        
        # Find all values for this marker
        values = []
        
        for report in reports:
            markers = await get_report_markers(report["id"])
            for marker in markers:
                if marker["marker_name"].lower() == marker_name.lower():
                    values.append({
                        "date": report.get("report_date", ""),
                        "value": float(marker["value"])
                    })
        
        if not values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for marker: {marker_name}"
            )
        
        # Sort by date
        values.sort(key=lambda x: x["date"])
        
        # Calculate metrics
        from services.trend_engine import calculate_trend_metrics
        values_only = [v["value"] for v in values]
        metrics = calculate_trend_metrics(values_only)
        
        return {
            "marker_name": marker_name,
            "values": values,
            "metrics": metrics,
            "total_data_points": len(values),
            "date_range": {
                "from": values[0]["date"],
                "to": values[-1]["date"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Marker trend error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch marker trend"
        )


@router.get("/stability-score")
async def get_stability_score(user: dict = Depends(get_current_user)):
    """
    Get overall health stability score (0-100).
    Higher = more stable/predictable markers.
    Lower = more volatile changes.
    """
    try:
        user_id = user["user_id"]
        
        # Fetch all reports
        reports = await get_reports(user_id)
        
        if not reports:
            return {
                "score": 50.0,
                "interpretation": "Upload reports to calculate stability"
            }
        
        # Organize markers over time
        markers_over_time = {}
        
        for report in reports:
            markers = await get_report_markers(report["id"])
            for marker in markers:
                marker_name = marker["marker_name"]
                if marker_name not in markers_over_time:
                    markers_over_time[marker_name] = []
                markers_over_time[marker_name].append(float(marker["value"]))
        
        # Calculate stability
        from services.trend_engine import calculate_stability_score
        score = calculate_stability_score(markers_over_time)
        
        # Interpret score
        if score >= 80:
            interpretation = "Excellent stability - markers are consistent"
        elif score >= 60:
            interpretation = "Good stability - minor variations expected"
        elif score >= 40:
            interpretation = "Moderate - some fluctuation in markers"
        else:
            interpretation = "Low stability - significant variations detected"
        
        return {
            "score": score,
            "interpretation": interpretation,
            "based_on_reports": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Stability score error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate stability"
        )


@router.get("/patterns")
async def get_patterns(user: dict = Depends(get_current_user)):
    """
    Get cross-marker patterns (e.g., lipid markers moving together).
    """
    try:
        user_id = user["user_id"]
        
        # Fetch all reports
        reports = await get_reports(user_id)
        
        if not reports:
            return {"patterns": []}
        
        # Organize markers
        markers_over_time = {}
        
        for report in reports:
            markers = await get_report_markers(report["id"])
            for marker in markers:
                marker_name = marker["marker_name"]
                if marker_name not in markers_over_time:
                    markers_over_time[marker_name] = []
                markers_over_time[marker_name].append(float(marker["value"]))
        
        # Detect patterns
        from services.trend_engine import detect_cross_marker_patterns
        patterns = detect_cross_marker_patterns(markers_over_time)
        
        return {
            "patterns": patterns,
            "total_markers": len(markers_over_time),
            "analyzed_reports": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Patterns detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect patterns"
        )
