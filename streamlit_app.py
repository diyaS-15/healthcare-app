"""HealthLens - Blood Test Analysis Platform"""
import html
import json
import os
import sys
import uuid
from datetime import date
from pathlib import Path

import streamlit as st
from PIL import Image
from Risk_Score.risk_engine import (
    AuthSession,
    DEFAULT_SAMPLE_IMAGE,
    StorageConfig,
    analyze_ingredient_image,
    build_profile_payload,
    export_scan_result,
    fetch_profile_from_supabase,
    save_profile,
    sign_in_with_supabase,
    sign_out_from_supabase,
    sign_up_with_supabase,
)

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = PROJECT_ROOT / "blood-report-ai" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def bootstrap_backend_env() -> None:
    load_env_file(PROJECT_ROOT / ".env")
    load_env_file(BACKEND_ROOT / ".env")

    shared_supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    os.environ.setdefault("SUPABASE_SERVICE_KEY", shared_supabase_key or "demo-service-key")
    os.environ.setdefault("SUPABASE_ANON_KEY", shared_supabase_key or "demo-anon-key")
    os.environ.setdefault("SUPABASE_JWT_SECRET", "demo-supabase-jwt-secret")
    os.environ.setdefault(
        "ENCRYPTION_SECRET",
        "f47ac10b2540c4d46da6ff3e5f3b3f0d5e7a3c1b9f2e4d6a8c0b1e3f5a7d9b1",
    )
    os.environ.setdefault("JWT_SECRET", "demo-jwt-secret")
    os.environ.setdefault("OPENAI_API_KEY", "")
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("APP_NAME", "Blood Report AI")
    os.environ.setdefault("APP_VERSION", "2.0.0")


def get_backend_services():
    bootstrap_backend_env()

    extractor_error = None
    try:
        from services.extractor import (
            clean_text,
            compute_status,
            deduplicate,
            extract_report,
            extract_text,
            regex_fallback,
        )
    except Exception as exc:
        extractor_error = str(exc)
        clean_text = None
        compute_status = None
        deduplicate = None
        extract_report = None
        extract_text = None
        regex_fallback = None

    try:
        from services.llm_brain import explain_report, extract_questions_from_response, general_chat
        from services.normalizer import normalize_markers
        from services.trend_engine import run_full_analysis
    except Exception as exc:
        return {"error": str(exc), "extractor_error": extractor_error}

    return {
        "extract_report": extract_report,
        "extract_text": extract_text,
        "clean_text": clean_text,
        "regex_fallback": regex_fallback,
        "deduplicate": deduplicate,
        "compute_status": compute_status,
        "normalize_markers": normalize_markers,
        "explain_report": explain_report,
        "extract_questions_from_response": extract_questions_from_response,
        "general_chat": general_chat,
        "run_full_analysis": run_full_analysis,
        "extractor_error": extractor_error,
    }


st.set_page_config(page_title="Health Risk Score Dashboard", page_icon="H", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #eef5ff 100%);
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .app-title {
        margin: 0;
        color: #123b6b;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.04em;
    }
    .app-subtitle {
        margin: 0.6rem 0 0 0;
        color: #516277;
        font-size: 1.05rem;
    }
    .hero-card {
        padding: 1.4rem 1.5rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #edf6ff 0%, #e7f0ff 55%, #dff2ff 100%);
        border: 1px solid #d3e4ff;
        margin-bottom: 1.2rem;
        box-shadow: 0 14px 36px rgba(24, 73, 145, 0.08);
    }
    .login-shell {
        max-width: 720px;
        margin: 1rem auto 0 auto;
        padding: 2rem 2rem 1.2rem 2rem;
        border-radius: 24px;
        background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
        border: 1px solid #dbe7f6;
        box-shadow: 0 18px 45px rgba(33, 85, 160, 0.08);
    }
    .login-title {
        margin: 0;
        color: #123b6b;
        font-size: 1.6rem;
        font-weight: 700;
    }
    .login-subtitle {
        margin: 0.4rem 0 0 0;
        color: #66768b;
    }
    h1 { color: #123b6b; font-size: 2.5rem; font-weight: 700; }
    h2 { color: #123b6b; font-size: 1.5rem; font-weight: 600; }
    h3 { color: #123b6b; font-size: 1.1rem; }
    .card {
        background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
        padding: 25px;
        border-radius: 22px;
        border: 1px solid #dce7f7;
        box-shadow: 0 14px 34px rgba(33, 85, 160, 0.07);
        margin-bottom: 20px;
    }
    .metric-box {
        background: linear-gradient(135deg, #edf6ff 0%, #f7fbff 100%);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #dce7f7;
        border-left: 4px solid #2f80ed;
        margin: 12px 0;
    }
    .status-good { color: #059669; font-weight: 600; }
    .status-warning { color: #d97706; font-weight: 600; }
    .status-alert { color: #dc2626; font-weight: 600; }
    .chat-message {
        padding: 16px;
        margin: 12px 0;
        border-radius: 10px;
        line-height: 1.6;
    }
    .user-message {
        background: linear-gradient(135deg, #2f80ed 0%, #5aa9ff 100%);
        color: white;
        margin-left: 40px;
        border-radius: 10px 0px 10px 10px;
    }
    .ai-message {
        background: #f7fbff;
        color: #123b6b;
        margin-right: 40px;
        border-radius: 0px 10px 10px 10px;
        border-left: 4px solid #2f80ed;
    }
    .insight-box {
        background: linear-gradient(135deg, #fff9e6 0%, #fff 100%);
        border-left: 4px solid #d97706;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    .recommendation {
        background: linear-gradient(135deg, #e6f7f1 0%, #f0fdf4 100%);
        border-left: 4px solid #059669;
        padding: 14px;
        margin: 8px 0;
        border-radius: 6px;
    }
    .risk-pill {
        display: inline-block;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        color: white;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #c8daf6;
        background: linear-gradient(135deg, #2f80ed 0%, #5aa9ff 100%);
        color: white;
        font-weight: 600;
    }
    .stButton > button:hover {
        border-color: #2f80ed;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.6rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #50708f;
    }
    .stTabs [aria-selected="true"] {
        color: #2f80ed !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis = None
if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "report_history" not in st.session_state:
    st.session_state.report_history = []
if "trend_analysis" not in st.session_state:
    st.session_state.trend_analysis = None
if "active_profile" not in st.session_state:
    st.session_state.active_profile = {}
if "latest_scan" not in st.session_state:
    st.session_state.latest_scan = None
if "latest_image" not in st.session_state:
    st.session_state.latest_image = None
if "latest_scan_source" not in st.session_state:
    st.session_state.latest_scan_source = ""
if "latest_scan_path" not in st.session_state:
    st.session_state.latest_scan_path = ""
if "auth_session" not in st.session_state:
    st.session_state.auth_session = None


def get_profile_storage_config() -> StorageConfig:
    def pick_env_value(*names: str) -> str:
        placeholder_prefixes = ("https://your", "eyJhbGc...", "your-", "demo-")
        for name in names:
            value = os.getenv(name, "").strip()
            if not value:
                continue
            if any(value.startswith(prefix) for prefix in placeholder_prefixes):
                continue
            return value
        return ""

    supabase_url = (
        pick_env_value("SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL")
    )
    supabase_key = (
        pick_env_value(
            "SUPABASE_KEY",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "SUPABASE_ANON_KEY",
        )
    )

    if supabase_url and supabase_key:
        return StorageConfig(
            backend="Supabase",
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            supabase_table=os.getenv("SUPABASE_TABLE", "user_profiles").strip() or "user_profiles",
        )

    return StorageConfig(backend="Local JSON")


def get_auth_session() -> AuthSession | None:
    data = st.session_state.get("auth_session")
    if not isinstance(data, dict):
        return None
    if not data.get("access_token") or not data.get("user_id"):
        return None

    return AuthSession(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token", ""),
        user_id=data["user_id"],
        email=data.get("email", ""),
    )


def set_auth_session(session: AuthSession | None) -> None:
    if session is None:
        st.session_state.auth_session = None
        st.session_state.authenticated = False
        st.session_state.user_email = None
        return

    st.session_state.auth_session = {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user_id": session.user_id,
        "email": session.email,
    }
    st.session_state.authenticated = True
    st.session_state.user_email = session.email or session.user_id


def load_profile_into_session(profile: dict | None) -> None:
    st.session_state.active_profile = profile or {}


def ensure_active_profile(storage_config: StorageConfig, auth_session: AuthSession | None) -> None:
    if storage_config.backend != "Supabase" or auth_session is None:
        return
    if st.session_state.get("active_profile"):
        return

    try:
        profile = fetch_profile_from_supabase(auth_session.user_id, storage_config, auth_session)
    except Exception:
        profile = None

    load_profile_into_session(profile)


def current_profile_user_id() -> str:
    auth_session = get_auth_session()
    if auth_session is not None:
        return auth_session.user_id
    return (st.session_state.get("user_email") or "local-user").strip().lower().replace("@", "-at-").replace(".", "-")


def render_profile_builder_tab():
    st.markdown("<h2>User Profile</h2>", unsafe_allow_html=True)
    st.caption("Build a profile that the ingredient scanner can use for allergy and sensitivity checks.")

    storage_config = get_profile_storage_config()
    auth_session = get_auth_session()
    active_profile = st.session_state.get("active_profile") or {}

    if storage_config.backend == "Supabase" and auth_session is None:
        st.info("Log in first so your profile is saved to your account and reused by the ingredient scanner.")
        return

    with st.form("user-profile-form"):
        name = st.text_input("Name", value=active_profile.get("name", ""), placeholder="Jordan Lee")
        age = st.number_input("Age", min_value=0, max_value=120, value=int(active_profile.get("age", 21) or 21))
        sex_options = ["Female", "Male", "Non-binary", "Prefer not to say"]
        sex_value = active_profile.get("sex", sex_options[0])
        sex_index = sex_options.index(sex_value) if sex_value in sex_options else 0
        sex = st.selectbox("Sex", sex_options, index=sex_index)
        conditions = st.text_area(
            "Existing conditions",
            value=", ".join(active_profile.get("existing_conditions", [])),
            placeholder="Asthma, eczema",
        )
        allergies = st.text_area(
            "Allergens / sensitivities",
            value=", ".join(active_profile.get("allergies", [])),
            placeholder="Soy, wheat, peppermint",
        )
        notes = st.text_area(
            "Notes",
            value=active_profile.get("notes", ""),
            placeholder="Anything else to keep with the profile",
        )
        submitted = st.form_submit_button("Save Profile")

    if submitted:
        if not name.strip():
            st.error("Please add a name before saving the profile.")
        else:
            profile = build_profile_payload(
                name,
                int(age),
                sex,
                conditions,
                allergies,
                notes,
                user_id=current_profile_user_id(),
            )
            try:
                save_profile(profile, storage_config, auth_session=auth_session)
            except Exception as exc:
                st.error(f"Could not save profile: {exc}")
            else:
                load_profile_into_session(profile)
                st.success("Profile saved.")

    active_profile = st.session_state.get("active_profile") or {}
    if active_profile:
        allergies_display = ", ".join(active_profile.get("allergies", [])) or "None saved"
        conditions_display = ", ".join(active_profile.get("existing_conditions", [])) or "None saved"
        st.markdown(
            f"""
            <div class='card'>
                <h4 style='margin-top: 0; color: #123b6b;'>Saved Profile Snapshot</h4>
                <p><strong>Name:</strong> {html.escape(active_profile.get('name', ''))}</p>
                <p><strong>Age:</strong> {html.escape(str(active_profile.get('age', '')))}</p>
                <p><strong>Sex:</strong> {html.escape(active_profile.get('sex', ''))}</p>
                <p><strong>Conditions:</strong> {html.escape(conditions_display)}</p>
                <p><strong>Allergies:</strong> {html.escape(allergies_display)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ingredient_scanner_tab():
    st.markdown("<h2>Ingredient Scanner</h2>", unsafe_allow_html=True)
    st.caption("Upload a product label image and compare the ingredients against the saved profile.")

    storage_config = get_profile_storage_config()
    auth_session = get_auth_session()
    active_profile = st.session_state.get("active_profile") or {}
    linked_allergies = active_profile.get("allergies", [])

    if storage_config.backend == "Supabase" and auth_session is None:
        st.info("Log in first so ingredient scans stay linked to your saved profile.")
        return

    if active_profile:
        st.info(f"Linked profile: {active_profile.get('name', 'Saved user')} | Allergies: {', '.join(linked_allergies) or 'None saved'}")
    else:
        st.warning("No saved profile found yet. You can still scan, but allergy-specific flags work best after saving a profile.")

    sample_exists = DEFAULT_SAMPLE_IMAGE.exists()
    use_sample_default = sample_exists
    use_sample = st.toggle(
        "Use the sample ingredient-only image from the repo",
        value=use_sample_default,
        disabled=not sample_exists,
        key="ingredient-sample-toggle",
    )

    if not sample_exists:
        st.caption("Sample image not found in this repo, so upload mode is enabled instead.")

    uploaded_file = None
    if not use_sample:
        uploaded_file = st.file_uploader(
            "Upload ingredient label image",
            type=["png", "jpg", "jpeg"],
            key="ingredient-image-uploader",
        )

    source_label = DEFAULT_SAMPLE_IMAGE.name if use_sample and sample_exists else (uploaded_file.name if uploaded_file else "")

    if st.button("Analyze Ingredients", use_container_width=True, key="analyze-ingredients-btn"):
        if use_sample and not sample_exists:
            st.error("The sample ingredient image is missing. Please upload an image instead.")
        elif not use_sample and uploaded_file is None:
            st.error("Upload an image or switch on the sample image toggle.")
        else:
            try:
                allergies_text = ", ".join(linked_allergies)
                if use_sample and sample_exists:
                    result = analyze_ingredient_image(DEFAULT_SAMPLE_IMAGE, allergies=allergies_text)
                    display_image = Image.open(DEFAULT_SAMPLE_IMAGE).copy()
                else:
                    image_bytes = uploaded_file.getvalue()
                    result = analyze_ingredient_image(image_bytes, allergies=allergies_text)
                    display_image = Image.open(uploaded_file).copy()
                result["linked_profile"] = {
                    "id": active_profile.get("id", current_profile_user_id()),
                    "name": active_profile.get("name", ""),
                    "allergies": linked_allergies,
                }
                export_path = export_scan_result(result, source_label or "ingredient-scan")
                st.session_state.latest_scan = result
                st.session_state.latest_image = display_image
                st.session_state.latest_scan_path = str(export_path)
                st.session_state.latest_scan_source = source_label or "ingredient-scan"
                st.success("Ingredient scan complete.")
            except Exception as exc:
                st.error(f"Scan failed: {exc}")

    result = st.session_state.get("latest_scan")
    if not result:
        return

    left_col, right_col = st.columns([1, 1.1])
    with left_col:
        if st.session_state.get("latest_image") is not None:
            st.image(st.session_state.get("latest_image"), caption=st.session_state.get("latest_scan_source"))
        st.caption(f"Source: {st.session_state.get('latest_scan_source')}")
        if st.session_state.get("latest_scan_path"):
            st.caption(f"JSON export saved to: {st.session_state.get('latest_scan_path')}")

    with right_col:
        risk = result.get("risk", {})
        risk_level = risk.get("level", "Unknown")
        risk_color = risk.get("color", "#5aa9ff")
        risk_summary = risk.get("summary", "No summary available.")
        st.markdown(
            f"<div class='risk-pill' style='background:{risk_color};'>{html.escape(risk_level)} Risk</div>",
            unsafe_allow_html=True,
        )
        st.write(risk_summary)
        st.markdown("**Allergy flags**")
        if result.get("allergy_flags"):
            for flag in result["allergy_flags"]:
                st.write(f"- {flag['ingredient']}: {flag['reason']}")
        else:
            st.write("No direct allergy conflicts found.")

        st.markdown("**Sensitivity / yellow flags**")
        if result.get("yellow_flags"):
            for flag in result["yellow_flags"]:
                st.write(f"- {flag['ingredient']}: {flag['reason']}")
        else:
            st.write("No yellow-flag ingredients detected.")

    st.markdown("**Extracted ingredient list**")
    st.dataframe(result.get("ingredients", []), use_container_width=True)

    with st.expander("Raw OCR text"):
        st.text(result.get("raw_text", ""))

    json_bytes = json.dumps(result, indent=2).encode("utf-8")
    st.download_button(
        "Download scan JSON",
        data=json_bytes,
        file_name=Path(st.session_state.get("latest_scan_path", "ingredient-scan.json")).name,
        mime="application/json",
        key="download-ingredient-json",
    )


def default_metrics_list():
    return []


def get_active_analysis():
    return st.session_state.get("latest_analysis")


def format_reference_range(marker: dict) -> str:
    low = marker.get("reference_low")
    high = marker.get("reference_high")
    if low is None and high is None:
        return "Range unavailable"
    if low is None:
        return f"<{high}"
    if high is None:
        return f">{low}"
    return f"{low}-{high}"


def metric_status_for_ui(status: str) -> str:
    if status == "normal":
        return "good"
    if status == "unknown":
        return "warning"
    return "warning"


def build_metrics_list(markers: list[dict]) -> list[tuple[str, str, str, str]]:
    if not markers:
        return default_metrics_list()

    priority = [
        "White Blood Cells (WBC)",
        "Red Blood Cells (RBC)",
        "Hemoglobin",
        "Blood Glucose",
        "Blood Glucose (Fasting)",
        "Total Cholesterol",
    ]

    chosen = []
    seen = set()

    for priority_name in priority:
        for marker in markers:
            name = marker.get("name", "")
            if name == priority_name and name not in seen:
                seen.add(name)
                chosen.append(marker)
                break

    for marker in markers:
        name = marker.get("name", "")
        if name not in seen:
            chosen.append(marker)
            seen.add(name)
        if len(chosen) >= 5:
            break

    rows = []
    for marker in chosen[:5]:
        value = marker.get("value", "N/A")
        unit = marker.get("unit", "").strip()
        value_text = f"{value} {unit}".strip()
        rows.append(
            (
                marker.get("name", "Unknown Marker"),
                value_text,
                format_reference_range(marker),
                metric_status_for_ui(marker.get("status", "unknown")),
            )
        )
    return rows


def build_key_findings(markers: list[dict]) -> list[str]:
    if not markers:
        return []

    abnormal = [marker for marker in markers if marker.get("status") in {"high", "low"}]
    if not abnormal:
        return ["All extracted markers are within their listed reference ranges."]

    findings = []
    for marker in abnormal[:3]:
        direction = "higher" if marker.get("status") == "high" else "lower"
        findings.append(f"{marker.get('name', 'A marker')} is {direction} than the listed range.")
    return findings


def build_next_steps(markers: list[dict]) -> list[str]:
    if not markers:
        return []

    abnormal_names = " ".join(marker.get("name", "").lower() for marker in markers if marker.get("status") in {"high", "low"})

    if "glucose" in abnormal_names or "a1c" in abnormal_names:
        return [
            "Review blood sugar trends with your healthcare provider.",
            "Focus on food, exercise, and sleep consistency before the next lab draw.",
            "Plan a follow-up test to confirm whether the glucose change persists.",
        ]
    if abnormal_names:
        return [
            "Review the out-of-range markers with your healthcare provider.",
            "Compare these results with any prior reports to look for patterns over time.",
            "Retest on the timeline your clinician recommends.",
        ]
    return [
        "Keep up the routines that are supporting stable results.",
        "Save future reports so trends can be compared over time.",
        "Bring the results to your next routine check-in.",
    ]


def overall_status(markers: list[dict]) -> str:
    abnormal_count = sum(1 for marker in markers if marker.get("status") in {"high", "low"})
    if abnormal_count == 0:
        return "Good"
    if abnormal_count == 1:
        return "Mostly Good"
    return "Needs Review"


def clean_analysis_summary(text: str) -> str:
    if not text:
        return "Your recent blood work analysis is ready."

    compact = " ".join(text.replace("\n", " ").split())
    disclaimer_index = compact.lower().find("important:")
    if disclaimer_index > 0:
        compact = compact[:disclaimer_index].strip()
    return compact[:220] + ("..." if len(compact) > 220 else "")


def format_ai_text_as_html(text: str) -> str:
    paragraphs = []
    for block in text.split("\n\n"):
        lines = [html.escape(line.strip()) for line in block.splitlines() if line.strip()]
        if lines:
            paragraphs.append(f"<p>{'<br>'.join(lines)}</p>")
    return "".join(paragraphs) or "<p>No response available.</p>"


def fallback_chat_response(question: str) -> str:
    lowered = question.lower()

    if "glucose" in lowered:
        return (
            "Your glucose result may need a closer look if it is running above the listed reference range. "
            "That usually means it is worth reviewing food, activity, sleep, and follow-up testing with your provider."
        )
    if "normal" in lowered or "results" in lowered:
        return (
            "I can help explain whether markers appear inside or outside the listed reference ranges, "
            "but a clinician should still interpret the full report in context."
        )
    if "improve" in lowered or "health" in lowered:
        return (
            "General support for blood markers often includes steady exercise, balanced meals, sleep consistency, "
            "and following up on any abnormal values with your provider."
        )
    return (
        "I can help explain your uploaded report in general terms. "
        "If you upload a report first, I can answer with more specific context from those markers."
    )


def analyze_uploaded_report(file_bytes: bytes, filename: str) -> dict:
    services = get_backend_services()
    if services.get("error"):
        raise RuntimeError(f"Backend import failed: {services['error']}")
    if services.get("extractor_error"):
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            raise RuntimeError(
                "PDF analysis needs PyMuPDF installed in the project environment. "
                "Run: .\\myenv\\Scripts\\python.exe -m pip install PyMuPDF"
            )
        raise RuntimeError(
            f"Report extraction is unavailable right now: {services['extractor_error']}"
        )

    report = None
    extraction_mode = "backend_pipeline"

    try:
        report = services["extract_report"](file_bytes, filename)
    except Exception:
        extraction_mode = "regex_fallback"
        raw_text = services["extract_text"](file_bytes, filename)
        cleaned_text = services["clean_text"](raw_text)
        fallback_markers = services["deduplicate"](services["regex_fallback"](cleaned_text))

        usable_markers = []
        for marker in fallback_markers:
            try:
                marker["value"] = float(marker["value"])
                marker["status"] = services["compute_status"](marker)
                usable_markers.append(marker)
            except Exception:
                continue

        if not usable_markers:
            raise RuntimeError("No valid markers could be extracted from that report.")

        report = {
            "report_date": date.today().isoformat(),
            "lab_name": None,
            "patient_name": None,
            "markers": usable_markers,
            "count": len(usable_markers),
        }

    normalized_markers = services["normalize_markers"](report.get("markers", []))
    analysis_text = services["explain_report"](
        markers=normalized_markers,
        trends={},
        patterns=[],
        simple_mode=False,
    )

    try:
        suggested_questions = services["extract_questions_from_response"](analysis_text)
    except Exception:
        suggested_questions = []

    return {
        "id": str(uuid.uuid4()),
        "file_name": filename,
        "report": report,
        "markers": normalized_markers,
        "analysis_text": analysis_text,
        "summary_text": clean_analysis_summary(analysis_text),
        "questions": suggested_questions,
        "extraction_mode": extraction_mode,
        "created_at": date.today().isoformat(),
    }


def rebuild_trend_analysis() -> dict | None:
    services = get_backend_services()
    if services.get("error"):
        return None

    markers_over_time = {}
    for analysis in st.session_state.get("report_history", []):
        report_date = analysis.get("report", {}).get("report_date") or analysis.get("created_at") or date.today().isoformat()
        for marker in analysis.get("markers", []):
            try:
                value = float(marker.get("value"))
            except Exception:
                continue
            marker_name = marker.get("name", "Unknown Marker")
            markers_over_time.setdefault(marker_name, []).append({"date": report_date, "value": value})

    if not markers_over_time:
        return None

    try:
        return services["run_full_analysis"](markers_over_time)
    except Exception:
        return None


def get_ai_response(question: str) -> str:
    analysis = get_active_analysis()
    services = get_backend_services()

    if services.get("error"):
        return format_ai_text_as_html(fallback_chat_response(question))

    context_parts = []
    if analysis:
        context_parts.append(f"Current file: {analysis.get('file_name', 'uploaded report')}")
        context_parts.append(f"Analysis summary: {analysis.get('summary_text', '')}")

        marker_lines = []
        for marker in analysis.get("markers", [])[:12]:
            marker_lines.append(
                f"{marker.get('name')}: {marker.get('value')} {marker.get('unit', '')} "
                f"(ref {format_reference_range(marker)}) [{marker.get('status', 'unknown')}]"
            )
        if marker_lines:
            context_parts.append("Markers:\n" + "\n".join(marker_lines))
    else:
        context_parts.append("No report has been uploaded yet. Answer generally and encourage uploading a report.")

    history = [
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.get("chat_history", [])
        if message.get("role") in {"user", "assistant"}
    ]

    try:
        response = services["general_chat"](
            history=history[-6:],
            new_message=question,
            simple_mode=False,
            context="\n\n".join(context_parts),
        )
    except Exception:
        response = fallback_chat_response(question)

    if not response:
        response = fallback_chat_response(question)

    return format_ai_text_as_html(response)


def render_login():
    """Login page"""
    storage_config = get_profile_storage_config()

    st.markdown(
        """
        <div class="hero-card">
            <h1 class="app-title">Health Risk Score Dashboard</h1>
            <p class="app-subtitle">Sign in first to unlock your profile, ingredient scanner, and blood test tools.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    auth_container = st.container()
    with auth_container:
        st.markdown(
            """
            <div class="login-shell">
                <p class="login-title">Authentication</p>
                <p class="login-subtitle">Only signed-in users can view the dashboard.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if storage_config.backend != "Supabase":
            st.warning("Supabase credentials are not configured, so sign-in is running in local-only mode.")

        login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])

        with login_tab:
            with st.form("login-form"):
                email = st.text_input("Email", placeholder="your@email.com", key="email1")
                password = st.text_input("Password", type="password", key="pass1")
                login_submitted = st.form_submit_button("Log In")
            if login_submitted:
                if email and password:
                    if storage_config.backend == "Supabase":
                        try:
                            session = sign_in_with_supabase(email, password, storage_config)
                            profile = fetch_profile_from_supabase(session.user_id, storage_config, session)
                        except Exception as exc:
                            st.error(f"Could not log in: {exc}")
                        else:
                            set_auth_session(session)
                            load_profile_into_session(profile)
                            st.success(f"Welcome, {session.email or email}!")
                            st.rerun()
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.success(f"Welcome, {email}!")
                        st.rerun()
                else:
                    st.error("Enter email and password")

        with signup_tab:
            with st.form("signup-form"):
                new_email = st.text_input("Email", placeholder="your@email.com", key="email2")
                new_pass = st.text_input("Password", type="password", key="pass2")
                conf_pass = st.text_input("Confirm Password", type="password", key="pass3")
                signup_submitted = st.form_submit_button("Create Account")
            if signup_submitted:
                if new_email and new_pass and conf_pass:
                    if new_pass == conf_pass:
                        if storage_config.backend == "Supabase":
                            try:
                                session, message = sign_up_with_supabase(new_email, new_pass, storage_config)
                            except Exception as exc:
                                st.error(f"Could not create account: {exc}")
                            else:
                                if session is None:
                                    st.success(message)
                                else:
                                    set_auth_session(session)
                                    load_profile_into_session(None)
                                    st.success(message)
                                    st.rerun()
                        else:
                            st.session_state.authenticated = True
                            st.session_state.user_email = new_email
                            st.success(f"Welcome, {new_email}!")
                            st.rerun()
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Fill all fields")


def render_app():
    """Main app with professional design"""
    storage_config = get_profile_storage_config()
    auth_session = get_auth_session()
    ensure_active_profile(storage_config, auth_session)
    analysis = get_active_analysis()

    st.markdown(
        f"""
        <div class="hero-card">
            <h1 class="app-title">Health Risk Score Dashboard</h1>
            <p class="app-subtitle">
                {"Signed in and ready to use your profile, ingredient scanner, and blood test tools." if st.session_state.user_email else "Sign in first to unlock your profile, ingredient scanner, and blood test tools."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("<h2 style='margin: 0; color:#123b6b;'>Welcome back</h2>", unsafe_allow_html=True)
        st.caption(f"Signed in as {st.session_state.user_email}")
    with col2:
        if st.button("Logout", use_container_width=True):
            if storage_config.backend == "Supabase" and auth_session is not None:
                try:
                    sign_out_from_supabase(auth_session, storage_config)
                except Exception:
                    pass
            set_auth_session(None)
            load_profile_into_session(None)
            st.session_state.latest_scan = None
            st.session_state.latest_image = None
            st.session_state.latest_scan_path = ""
            st.session_state.latest_scan_source = ""
            st.rerun()

    st.markdown("---")
    
    profile_tab, scanner_tab, tab1, tab2, tab3, tab4 = st.tabs(
        ["User Profile", "Ingredient Scanner", "Upload Report", "Analysis", "Health Chat", "Trends"]
    )

    with profile_tab:
        render_profile_builder_tab()

    with scanner_tab:
        render_ingredient_scanner_tab()

    with tab1:
        st.markdown("<h2>Upload Your Blood Test</h2>", unsafe_allow_html=True)
        st.markdown("Upload a PDF or image of your blood report for instant AI analysis", unsafe_allow_html=True)
        st.markdown("")
        
        col_u1, col_u2 = st.columns([2, 1])
        
        with col_u1:
            file = st.file_uploader("", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
            
            if file:
                st.success(f"File uploaded: {file.name}")
                st.info(f"Size: {file.size / 1024:.1f} KB")
                
                if st.button("Analyze Now", use_container_width=True, type="primary"):
                    with st.spinner("Analyzing your blood test..."):
                        try:
                            latest_analysis = analyze_uploaded_report(file.getvalue(), file.name)
                        except Exception as exc:
                            st.session_state.analysis_error = str(exc)
                            st.error(f"Analysis failed: {exc}")
                        else:
                            st.session_state.latest_analysis = latest_analysis
                            st.session_state.analysis_error = None
                            st.session_state.report_history.append(latest_analysis)
                            st.session_state.trend_analysis = rebuild_trend_analysis()
                            analysis = latest_analysis
                            st.success("Analysis Complete!")

                latest_for_file = get_active_analysis()
                if latest_for_file and latest_for_file.get("file_name") == file.name:
                    metric_rows = build_metrics_list(latest_for_file.get("markers", []))[:3]
                    if metric_rows:
                        col_m1, col_m2, col_m3 = st.columns(3)
                        metric_columns = [col_m1, col_m2, col_m3]
                        for column, metric in zip(metric_columns, metric_rows):
                            label, value, _, status = metric
                            delta = "Normal" if status == "good" else "Review"
                            with column:
                                st.metric(label, value, delta)
            else:
                st.markdown("""
                <div style='text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #f0f4f8 0%, #f8fafb 100%); border-radius: 12px; border: 2px dashed #1a3a52;'>
                    <p style='color: #1a3a52; font-size: 1rem; margin: 0;'><strong>Drop your file here</strong></p>
                    <p style='color: #666; font-size: 0.9rem; margin: 10px 0 0 0;'>PDF, JPG, or PNG • Max 200MB</p>
                </div>
                """,
                unsafe_allow_html=True)
        
            if st.session_state.get("analysis_error"):
                st.warning(st.session_state.analysis_error)
        
        with col_u2:
            st.markdown("""
            <div class='card' style='padding: 20px;'>
                <h4 style='margin-top: 0;'>Secure Upload</h4>
                <ul style='font-size: 0.85rem; color: #666;'>
                    <li>AES-256 encrypted</li>
                    <li>Only you access</li>
                    <li>HIPAA compliant</li>
                    <li>Auto-delete option</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True)
    
    with tab2:
        analysis = get_active_analysis()
        st.markdown("<h2>Your Analysis Results</h2>", unsafe_allow_html=True)
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("<h3>Blood Metrics</h3>", unsafe_allow_html=True)
            
            metrics_list = build_metrics_list(analysis.get("markers", [])) if analysis else default_metrics_list()

            if metrics_list:
                for metric, value, normal_range, status in metrics_list:
                    status_text = "Normal" if status == "good" else "Elevated"
                    status_class = "status-good" if status == "good" else "status-warning"
                    
                    st.markdown(f"""
                    <div class='metric-box'>
                        <strong>{html.escape(metric)}</strong><br>
                        Value: <strong>{html.escape(str(value))}</strong> | Normal: {html.escape(str(normal_range))}<br>
                        <span class='{status_class}'>{status_text}</span>
                    </div>
                    """,
                    unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='card'>
                    <h4 style='color: #123b6b; margin-top: 0;'>No Blood Metrics Yet</h4>
                    <p style='color: #66768b; font-size: 0.95rem; margin-bottom: 0;'>
                    Upload and analyze a blood test report to populate this section with real marker values.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with col_a2:
            st.markdown("<h3>Health Insights</h3>", unsafe_allow_html=True)
            
            if analysis:
                findings = build_key_findings(analysis.get("markers", []))
                next_steps = build_next_steps(analysis.get("markers", []))
                status_text = overall_status(analysis.get("markers", []))
                summary_text = html.escape(analysis.get("summary_text", "Your recent blood work shows healthy results with one area to monitor."))
                findings_html = "".join(f"<li>{html.escape(item)}</li>" for item in findings) or "<li>No specific out-of-range markers were highlighted from the extracted report.</li>"
                next_steps_html = "".join(f"<li>{html.escape(item)}</li>" for item in next_steps) or "<li>Review the uploaded report with your healthcare provider for personalized interpretation.</li>"
                
                st.markdown(f"""
                <div class='card'>
                    <h4 style='color: #1a3a52; margin-top: 0;'>Overall Status: {html.escape(status_text)}</h4>
                    <p style='color: #666; font-size: 0.95rem;'>
                    {summary_text}
                    </p>
                    
                    <hr>
                    
                    <h4 style='color: #1a3a52;'>Key Findings</h4>
                    <ul style='color: #666; font-size: 0.9rem;'>
                        {findings_html}
                    </ul>
                    
                    <hr>
                    
                    <h4 style='color: #1a3a52;'>Next Steps</h4>
                    <ol style='color: #666; font-size: 0.9rem;'>
                        {next_steps_html}
                    </ol>
                </div>
                """,
                unsafe_allow_html=True)
                with st.expander("Full AI Analysis"):
                    st.write(analysis.get("analysis_text", "No analysis text available."))
            else:
                st.markdown("""
                <div class='card'>
                    <h4 style='color: #1a3a52; margin-top: 0;'>Analysis Waiting</h4>
                    <p style='color: #666; font-size: 0.95rem;'>
                    Upload and analyze a blood report to generate real AI-backed insights, follow-up questions, and marker interpretation here.
                    </p>
                </div>
                """,
                unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<h2>Health AI Assistant</h2>", unsafe_allow_html=True)
        st.markdown("Advanced AI-powered health insights based on your personal blood profile")
        st.markdown("---")
        
        chat_container = st.container()
        
        with chat_container:
            if st.session_state.chat_history:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div class='chat-message user-message'>
                            <strong>You:</strong> {html.escape(msg['content'])}
                        </div>
                        """,
                        unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='chat-message ai-message'>
                            <strong>HealthLens AI:</strong><br>{msg['display']}
                        </div>
                        """,
                        unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("<h4>Common Questions</h4>", unsafe_allow_html=True)
        col_q1, col_q2, col_q3 = st.columns(3)
        
        suggestions = [
            "What does my glucose level mean?",
            "How can I improve my health?",
            "Are my results normal?",
        ]
        
        analysis = get_active_analysis()
        if analysis and analysis.get("questions"):
            dynamic_questions = [question for question in analysis["questions"] if isinstance(question, str) and question.strip()]
            suggestions = (dynamic_questions + suggestions)[:3]
        
        suggestion_clicked = None
        with col_q1:
            if st.button(suggestions[0], use_container_width=True):
                suggestion_clicked = suggestions[0]
        with col_q2:
            if st.button(suggestions[1], use_container_width=True):
                suggestion_clicked = suggestions[1]
        with col_q3:
            if st.button(suggestions[2], use_container_width=True):
                suggestion_clicked = suggestions[2]
        
        st.markdown("")
        
        col_input1, col_input2 = st.columns([4, 1])
        
        with col_input1:
            user_input = st.text_input(
                "Ask AI Assistant anything about your health",
                placeholder="Type your health question here...",
                label_visibility="collapsed",
            )
        
        with col_input2:
            send_btn = st.button("Send", use_container_width=True, type="primary")
        
        if send_btn or suggestion_clicked:
            question = suggestion_clicked if suggestion_clicked else user_input
            
            if question:
                st.session_state.chat_history.append({"role": "user", "content": question})
                
                with st.spinner("HealthLens AI is analyzing your data..."):
                    ai_response = get_ai_response(question)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": ai_response, "display": ai_response}
                    )
                    st.rerun()
    
    with tab4:
        st.markdown("<h2>Your Health Timeline</h2>", unsafe_allow_html=True)
        
        history = st.session_state.get("report_history", [])
        trend_analysis = st.session_state.get("trend_analysis")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("<h3>Test History</h3>", unsafe_allow_html=True)
            
            if history:
                history_html_parts = []
                for index, item in enumerate(reversed(history[-3:])):
                    report = item.get("report", {})
                    markers = item.get("markers", [])[:4]
                    marker_bits = []
                    for marker in markers:
                        marker_bits.append(
                            f"{html.escape(marker.get('name', 'Marker'))}: {html.escape(str(marker.get('value', 'N/A')))}"
                        )

                    separator = "<hr style='margin: 15px 0;'>" if index < min(len(history), 3) - 1 else ""
                    history_html_parts.append(
                        f"""
                        <strong style='color: #1a3a52;'>Report - {html.escape(report.get('report_date') or item.get('created_at') or 'Unknown date')}</strong><br>
                        {' | '.join(marker_bits) if marker_bits else 'No markers extracted'}
                        {separator}
                        """
                    )
                
                st.markdown(f"""
                <div class='card'>
                    {''.join(history_html_parts)}
                </div>
                """,
                unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='card'>
                    <strong style='color: #1a3a52;'>No Test History Yet</strong><br>
                    Analyze your first blood report to start building a timeline of past results.
                </div>
                """,
                unsafe_allow_html=True)
        
        with col_t2:
            st.markdown("<h3>Trend Analysis</h3>", unsafe_allow_html=True)
            
            if trend_analysis and trend_analysis.get("per_marker"):
                trend_lines = []
                for marker_name, stats in list(trend_analysis["per_marker"].items())[:4]:
                    direction = stats.get("direction", "unknown").replace("_", " ").title()
                    trend_lines.append(
                        f"""
                        <p><strong>{html.escape(marker_name)}</strong><br>
                        <span class='status-warning'>{html.escape(direction)}</span>
                        - Change: {html.escape(str(stats.get('change_percent', 0)))}%</p>
                        <hr>
                        """
                    )
                
                patterns = trend_analysis.get("patterns", [])
                patterns_text = "<br>".join(html.escape(pattern) for pattern in patterns) if patterns else "No multi-marker pattern detected yet."
                
                st.markdown(f"""
                <div class='card'>
                    {''.join(trend_lines)}
                    <p><strong>Overall Stability</strong><br><strong style='color: #1a3a52;'>{html.escape(str(trend_analysis.get('stability_score', 'N/A')))}</strong></p>
                    <hr>
                    <p><strong>Patterns</strong><br>{patterns_text}</p>
                    <hr>
                    <p style='margin-bottom: 0;'><strong>Next Recommended Test:</strong> Keep uploading future reports to strengthen trend detection.</p>
                </div>
                """,
                unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='card'>
                    <p><strong>Trend Analysis</strong><br><span class='status-warning'>Waiting for enough real data</span></p>
                    <hr>
                    <p style='margin-bottom: 0;'><strong>Next Recommended Step:</strong> Analyze one or more blood reports to generate real marker history and trends.</p>
                </div>
                """,
                unsafe_allow_html=True)


existing_auth_session = get_auth_session()
if existing_auth_session is not None:
    set_auth_session(existing_auth_session)

if __name__ == "__main__":
    if not st.session_state.authenticated:
        render_login()
    else:
        render_app()
