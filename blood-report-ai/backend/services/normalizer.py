"""
Marker normalization utilities
Handles normalization, display formatting, and status determination.
Supports 100+ common blood markers.
"""

# Comprehensive marker name mapping for consistency
# Includes common abbreviations and variations
MARKER_NAME_MAP = {
    # Hematology
    "wbc": "White Blood Cells (WBC)",
    "rbc": "Red Blood Cells (RBC)",
    "hb": "Hemoglobin",
    "hemoglobin": "Hemoglobin",
    "hct": "Hematocrit",
    "plt": "Platelets",
    "platelet": "Platelets",
    "mch": "Mean Corpuscular Hemoglobin (MCH)",
    "mchc": "Mean Corpuscular Hemoglobin Concentration",
    "mcv": "Mean Corpuscular Volume (MCV)",
    "mpv": "Mean Platelet Volume",
    "rdw": "Red Cell Distribution Width",
    
    # Liver Function
    "ast": "AST (Aspartate Aminotransferase)",
    "sgot": "AST (Aspartate Aminotransferase)",
    "alt": "ALT (Alanine Aminotransferase)",
    "sgpt": "ALT (Alanine Aminotransferase)",
    "alp": "Alkaline Phosphatase",
    "bilirubin": "Total Bilirubin",
    "total bilirubin": "Total Bilirubin",
    "direct bilirubin": "Direct Bilirubin",
    "indirect bilirubin": "Indirect Bilirubin",
    "albumin": "Albumin",
    "protein": "Total Protein",
    "total protein": "Total Protein",
    "globulin": "Globulin",
    "ggt": "Gamma-Glutamyl Transferase (GGT)",
    
    # Renal Function
    "creatinine": "Creatinine",
    "bun": "Blood Urea Nitrogen (BUN)",
    "urea": "Blood Urea Nitrogen (BUN)",
    "uric acid": "Uric Acid",
    "egfr": "Estimated Glomerular Filtration Rate",
    "gfr": "Estimated Glomerular Filtration Rate",
    
    # Electrolytes
    "sodium": "Sodium (Na)",
    "potassium": "Potassium (K)",
    "chloride": "Chloride (Cl)",
    "bicarbonate": "Bicarbonate (CO2)",
    "co2": "Bicarbonate (CO2)",
    "calcium": "Calcium",
    "phosphorus": "Phosphorus",
    "magnesium": "Magnesium",
    
    # Lipid Profile
    "cholesterol": "Total Cholesterol",
    "total cholesterol": "Total Cholesterol",
    "hdl": "HDL Cholesterol (Good)",
    "ldl": "LDL Cholesterol (Bad)",
    "triglycerides": "Triglycerides",
    "vldl": "VLDL Cholesterol",
    "chol/hdl": "Cholesterol/HDL Ratio",
    "ldl/hdl": "LDL/HDL Ratio",
    "non-hdl": "Non-HDL Cholesterol",
    
    # Glucose Metabolism
    "glucose": "Blood Glucose",
    "fasting glucose": "Blood Glucose (Fasting)",
    "random glucose": "Blood Glucose (Random)",
    "hba1c": "Hemoglobin A1C (HbA1c)",
    "glycated hemoglobin": "Hemoglobin A1C (HbA1c)",
    
    # Cardiovascular Markers
    "troponin": "Cardiac Troponin",
    "ck-mb": "Creatine Kinase-MB",
    "ldh": "Lactate Dehydrogenase",
    "bnp": "B-Type Natriuretic Peptide",
    "nt-probnp": "NT-Pro B-Type Natriuretic Peptide",
    "myoglobin": "Myoglobin",
    "crp": "C-Reactive Protein",
    "hs-crp": "High-Sensitivity CRP",
    
    # Thyroid Function
    "tsh": "Thyroid Stimulating Hormone (TSH)",
    "t3": "Triiodothyronine (T3)",
    "t4": "Thyroxine (T4)",
    "free t3": "Free Triiodothyronine",
    "free t4": "Free Thyroxine",
    "tpo": "Thyroid Peroxidase Antibodies",
    "thyroglobulin": "Thyroglobulin",
    
    # Iron Metabolism
    "iron": "Serum Iron",
    "tibc": "Total Iron Binding Capacity",
    "ferritin": "Ferritin",
    "transferrin": "Transferrin",
    
    # Immunology
    "igm": "Immunoglobulin M",
    "igg": "Immunoglobulin G",
    "iga": "Immunoglobulin A",
    "complement c3": "Complement C3",
    "complement c4": "Complement C4",
    "rheumatoid factor": "Rheumatoid Factor",
    "ana": "Antinuclear Antibody",
    "tppa": "TPPA (Syphilis)",
    "vdrl": "VDRL (Syphilis Screening)",
    
    # Pancreatic Enzymes
    "amylase": "Amylase",
    "lipase": "Lipase",
    
    # Other Enzymes & Proteins
    "cpk": "Creatine Phosphokinase",
    "ck": "Creatine Kinase",
    "5'nt": "5'-Nucleotidase",
    "nucleotidase": "5'-Nucleotidase",
    "mao": "Monoamine Oxidase",
    
    # Hormones
    "cortisol": "Cortisol",
    "acth": "Adrenocorticotropic Hormone",
    "testosterone": "Testosterone",
    "estrogen": "Estrogen",
    "progesterone": "Progesterone",
    "fsh": "Follicle Stimulating Hormone",
    "lh": "Luteinizing Hormone",
    "prolactin": "Prolactin",
    "insulin": "Insulin",
    
    # Coagulation
    "pt": "Prothrombin Time",
    "inr": "International Normalized Ratio",
    "ptt": "Partial Thromboplastin Time",
    "aptt": "Activated Partial Thromboplastin Time",
    "bleeding time": "Bleeding Time",
    "d-dimer": "D-Dimer",
    "fibrinogen": "Fibrinogen",
    
    # Vitamins & Minerals
    "vitamin b12": "Vitamin B12",
    "b12": "Vitamin B12",
    "folate": "Folate",
    "folic acid": "Folate",
    "vitamin d": "Vitamin D",
    "25-oh vitamin d": "Vitamin D (25-Hydroxy)",
    "vitamin a": "Vitamin A",
    "vitamin e": "Vitamin E",
    "vitamin c": "Vitamin C",
    "ascorbic acid": "Vitamin C",
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
