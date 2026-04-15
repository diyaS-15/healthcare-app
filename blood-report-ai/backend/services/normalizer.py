"""
Marker normalization utilities
Handles normalization, display formatting, and status determination.
"""

# Marker name mapping for consistency
MARKER_NAME_MAP = {
    "wbc": "White Blood Cells (WBC)",
    "rbc": "Red Blood Cells (RBC)",
    "hb": "Hemoglobin",
    "hct": "Hematocrit",
    "plt": "Platelets",
    "glucose": "Blood Glucose",
    "creatinine": "Creatinine",
    "bun": "Blood Urea Nitrogen",
    "ast": "AST (SGOT)",
    "alt": "ALT (SGPT)",
    "cholesterol": "Total Cholesterol",
    "hdl": "HDL Cholesterol",
    "ldl": "LDL Cholesterol",
    "triglycerides": "Triglycerides",
    "albumin": "Albumin",
    "protein": "Total Protein",
}


def normalize_marker_name(raw_name: str) -> str:
    """
    Normalize individual marker name to standard format.
    Handles abbreviations and common variations.
    
    Args:
        raw_name: Raw marker name from lab report
        
    Returns:
        Standardized marker name for consistency
    """
    if not raw_name:
        return "Unknown Marker"
    
    # Normalize to lowercase for comparison
    normalized = raw_name.lower().strip()
    
    # Check mapping
    if normalized in MARKER_NAME_MAP:
        return MARKER_NAME_MAP[normalized]
    
    # Check partial matches
    for key, display_name in MARKER_NAME_MAP.items():
        if key in normalized or normalized in key:
            return display_name
    
    # If no match, clean up and return
    return get_display_name(raw_name)


def normalize_markers(markers):
    """
    Normalize raw LLM markers into clean structure
    and add status (low/normal/high).
    Also normalizes marker names for consistency.
    """
    normalized = []

    for m in markers:
        value = m.get("value")
        low = m.get("reference_low")
        high = m.get("reference_high")
        raw_name = m.get("name", "Unknown")

        status = "unknown"

        if value is not None:
            if low is not None and value < low:
                status = "low"
            elif high is not None and value > high:
                status = "high"
            else:
                status = "normal"

        normalized.append({
            "name": normalize_marker_name(raw_name),
            "original_name": raw_name,
            "value": value,
            "unit": m.get("unit", ""),
            "reference_low": low,
            "reference_high": high,
            "status": status
        })

    return normalized


def get_display_name(name):
    """
    Clean/format marker names for UI display.
    Converts abbreviations to full names when possible.
    """
    if not name:
        return "Unknown"
    
    # Try normalized name first
    normalized = normalize_marker_name(name)
    if normalized != "Unknown Marker":
        return normalized
    
    # Fallback to title case
    return name.strip().title()
