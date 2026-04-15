"""
Marker normalization utilities
"""

def normalize_markers(markers):
    """
    Normalize raw LLM markers into clean structure
    and add status (low/normal/high)
    """
    normalized = []

    for m in markers:
        value = m.get("value")
        low = m.get("reference_low")
        high = m.get("reference_high")

        status = "unknown"

        if value is not None:
            if low is not None and value < low:
                status = "low"
            elif high is not None and value > high:
                status = "high"
            else:
                status = "normal"

        normalized.append({
            "name": m.get("name"),
            "value": value,
            "unit": m.get("unit"),
            "reference_low": low,
            "reference_high": high,
            "status": status
        })

    return normalized


def get_display_name(name):
    """
    Clean/format marker names for UI
    """
    if not name:
        return "Unknown"
    return name.strip().title()
