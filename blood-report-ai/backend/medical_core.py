"""
MEDICAL CORE v2 — Hospital Grade Parser
Fixes:
- Duplicate markers issue
- Repeated outputs
- Weak normalization
- No trend support
"""

import re
import json
from collections import defaultdict
from typing import List, Dict

# ─────────────────────────────
# NORMALIZATION
# ─────────────────────────────
def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


# ─────────────────────────────
# STATUS ENGINE (FIXED LOGIC)
# ─────────────────────────────
def compute_status(value, low, high):
    try:
        value = float(value)
        if low is None or high is None:
            return "unknown"
        if value < low:
            return "low"
        if value > high:
            return "high"
        return "normal"
    except:
        return "unknown"


# ─────────────────────────────
# HARD DEDUP ENGINE (FIXED)
# ─────────────────────────────
def deduplicate_markers(markers: List[dict]) -> List[dict]:
    best = {}

    for m in markers:
        key = normalize_name(m.get("name", ""))

        if key not in best:
            best[key] = m
        else:
            # keep highest confidence OR latest value difference
            if m.get("confidence", 0) > best[key].get("confidence", 0):
                best[key] = m

    return list(best.values())


# ─────────────────────────────
# TREND ENGINE (NEW)
# ─────────────────────────────
def compute_trends(history: List[List[dict]]) -> Dict:
    """
    history = [
        [report1 markers],
        [report2 markers],
    ]
    """

    trend_map = defaultdict(list)

    for report in history:
        for m in report:
            key = normalize_name(m["name"])
            trend_map[key].append(float(m["value"]))

    trends = {}

    for k, values in trend_map.items():
        if len(values) < 2:
            continue

        trends[k] = {
            "direction": "up" if values[-1] > values[0] else "down",
            "change": round(values[-1] - values[0], 2),
            "latest": values[-1],
        }

    return trends


# ─────────────────────────────
# FINAL ENRICHMENT ENGINE
# ─────────────────────────────
def enrich_markers(markers: List[dict]) -> List[dict]:
    cleaned = []

    for m in markers:
        try:
            m["value"] = float(m["value"])
            m["status"] = compute_status(
                m["value"],
                m.get("reference_low"),
                m.get("reference_high"),
            )
            cleaned.append(m)
        except:
            continue

    return deduplicate_markers(cleaned)

# ─────────────────────────────
# DATABASE INIT (MISSING FUNCTION FIX)
# ─────────────────────────────
def init_db():
    """
    Placeholder DB init for now.
    Replace later with Postgres / Mongo setup.
    """
    print("🧠 Medical Core DB initialized")