"""
Trend Engine - Statistical Pattern Detection
Finds trends, patterns, and cross-marker correlations in blood markers over time.
This is the CORE AI MOAT — it detects patterns LLMs alone cannot.
"""
import numpy as np
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from pathlib import Path
import json

# ━━━━━━━━━━━━━━ TREND DETECTION ━━━━━━━━━━━━━━

def detect_trend_direction(values: List[float]) -> str:
    """
    Detect if values are trending up, down, or stable.
    Uses least-squares linear regression.
    """
    if len(values) < 2:
        return "insufficient_data"
    
    x = np.array(range(len(values)))
    y = np.array(values)
    
    # Linear regression: y = mx + b
    coefficients = np.polyfit(x, y, 1)
    slope = coefficients[0]
    
    # Determine direction based on slope magnitude relative to values
    relative_slope = abs(slope) / (np.mean(y) if np.mean(y) != 0 else 1)
    
    if relative_slope < 0.05:  # Small relative change
        return "stable"
    elif slope > 0:
        return "increasing"
    else:
        return "decreasing"

def calculate_trend_metrics(values: List[float]) -> Dict:
    """
    Calculate comprehensive metrics for a single marker's trend.
    """
    if len(values) < 2:
        return {
            "direction": "insufficient_data",
            "change_percent": 0,
            "consistency": "unknown",
            "volatility": 0
        }
    
    oldest = values[0]
    newest = values[-1]
    change = newest - oldest
    change_percent = (change / oldest * 100) if oldest != 0 else 0
    
    # Volatility: standard deviation of differences
    diffs = np.diff(values)
    volatility = float(np.std(diffs))
    
    # Consistency: how smooth is the trend
    relative_volatility = volatility / (np.mean(values) if np.mean(values) != 0 else 1)
    
    if relative_volatility < 0.05:
        consistency = "stable"
    elif relative_volatility < 0.15:
        consistency = "gradual"
    elif relative_volatility < 0.30:
        consistency = "fluctuating"
    else:
        consistency = "volatile"
    
    return {
        "direction": detect_trend_direction(values),
        "change_percent": round(change_percent, 2),
        "consistency": consistency,
        "volatility": round(volatility, 2),
        "oldest_value": oldest,
        "newest_value": newest,
    }

# ━━━━━━━━━━━━━━ CROSS-MARKER PATTERNS ━━━━━━━━━━━━━━

def detect_cross_marker_patterns(markers_data: Dict[str, List[float]]) -> List[str]:
    """
    Detect patterns where multiple markers move together.
    Example: LDL ↑ and triglycerides ↑ = lipid-related
    """
    patterns = []
    
    # Get trend directions for all markers
    trends = {name: detect_trend_direction(values) 
              for name, values in markers_data.items() if len(values) >= 2}
    
    # Lipid correlation pattern
    lipid_markers = {"ldl", "hdl", "total_cholesterol", "triglycerides"}
    lipid_keys = [k for k in trends.keys() if any(lm in k for lm in lipid_markers)]
    
    if lipid_keys:
        increasing_lipids = [k for k in lipid_keys if "ldl" in k or "total" in k or "trigly" in k]
        if len(increasing_lipids) >= 2:
            up_count = sum(1 for k in increasing_lipids if trends[k] == "increasing")
            if up_count >= 2:
                patterns.append("📈 Multiple lipid markers (LDL, triglycerides) trending upward together")
    
    # Glucose control pattern
    glucose_markers = {"glucose", "hba1c"}
    glucose_keys = [k for k in trends.keys() if any(gm in k for gm in glucose_markers)]
    if len(glucose_keys) >= 2:
        if all(trends[k] == "increasing" for k in glucose_keys):
            patterns.append("📊 Blood glucose and HbA1c trending upward - glycemic control decreasing")
    
    # Liver stress pattern
    liver_markers = {"alt", "ast", "bilirubin"}
    liver_keys = [k for k in trends.keys() if any(lm in k for lm in liver_markers)]
    if len(liver_keys) >= 2:
        if sum(1 for k in liver_keys if trends[k] == "increasing") >= 2:
            patterns.append("⚠️  Liver enzymes (ALT, AST) elevated - possible inflammation")
    
    # Anemia pattern
    blood_markers = {"hemoglobin", "hematocrit", "rbc"}
    blood_keys = [k for k in trends.keys() if any(bm in k for bm in blood_markers)]
    if len(blood_keys) >= 2:
        if sum(1 for k in blood_keys if trends[k] == "decreasing") >= 2:
            patterns.append("🔴 Red blood cell markers (Hb, Hct, RBC) decreasing - possible anemia development")
    
    return patterns

# ━━━━━━━━━━━━━━ STABILITY SCORE ━━━━━━━━━━━━━━

def calculate_stability_score(markers_data: Dict[str, List[float]]) -> float:
    """
    Calculate a 0-100 score for overall health stability.
    Higher = more stable / predictable
    """
    if not markers_data:
        return 50.0
    
    scores = []
    for marker, values in markers_data.items():
        if len(values) < 2:
            continue
        metrics = calculate_trend_metrics(values)
        
        # Stability decreases with volatility and change
        volatility_penalty = metrics["volatility"] * 10
        change_penalty = abs(metrics["change_percent"]) / 10
        
        marker_stability = max(0, 100 - volatility_penalty - change_penalty)
        scores.append(marker_stability)
    
    return round(np.mean(scores), 2) if scores else 50.0

# ━━━━━━━━━━━━━━ MAIN ANALYSIS ━━━━━━━━━━━━━━

def run_full_analysis(markers_over_time: Dict[str, List[Dict]]) -> Dict:
    """
    Full trend analysis for one user across all their reports.
    
    Input:
    {
      "hemoglobin": [
        {"date": "2023-01-01", "value": 13.2},
        {"date": "2024-01-01", "value": 12.8},
      ]
    }
    
    Output:
    {
      "hemoglobin": {
        "trend_direction": "decreasing",
        "change_percent": -3.0,
        ...
      },
      "patterns": ["Pattern 1", "Pattern 2"],
      "stability_score": 75.3
    }
    """
    
    results = {}
    values_only = {}
    
    # Calculate individual marker trends
    for marker, history in markers_over_time.items():
        if not history:
            continue
        
        # Sort by date
        sorted_history = sorted(history, key=lambda x: x["date"])
        values = [h["value"] for h in sorted_history]
        dates = [h["date"] for h in sorted_history]
        
        values_only[marker] = values
        
        metrics = calculate_trend_metrics(values)
        results[marker] = {
            **metrics,
            "data_points": len(values),
            "date_range": {"from": dates[0], "to": dates[-1]} if dates else None,
        }
    
    # Find cross-marker patterns
    patterns = detect_cross_marker_patterns(values_only)
    
    # Calculate overall stability
    stability = calculate_stability_score(values_only)
    
    return {
        "per_marker": results,
        "patterns": patterns,
        "stability_score": stability,
        "analyzed_count": len(results),
    }
