from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import streamlit as st
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from Risk_Score.risk_engine import (  # noqa: E402
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


st.set_page_config(page_title="User Profile + Risk Score", page_icon="H", layout="wide")

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
    .section-card {
        padding: 1.2rem 1.25rem;
        border-radius: 22px;
        background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
        border: 1px solid #dce7f7;
        box-shadow: 0 14px 34px rgba(33, 85, 160, 0.07);
        margin-bottom: 1rem;
    }
    .section-title {
        margin: 0;
        color: #123b6b;
        font-size: 1.35rem;
        font-weight: 700;
    }
    .section-subtitle {
        margin: 0.45rem 0 0 0;
        color: #61758b;
    }
    .chat-note {
        margin: 0;
        color: #61758b;
        font-size: 0.95rem;
    }
    .risk-pill {
        display: inline-block;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        color: white;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .soft-card {
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid #dce7f7;
        background: #ffffff;
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


def get_storage_config() -> StorageConfig:
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()

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
        st.session_state.pop("auth_session", None)
        return
    st.session_state["auth_session"] = {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user_id": session.user_id,
        "email": session.email,
    }


def load_profile_into_session(profile: dict | None) -> None:
    st.session_state["active_profile"] = profile or {}


def ensure_active_profile(storage_config: StorageConfig, auth_session: AuthSession | None) -> None:
    if auth_session is None or st.session_state.get("active_profile"):
        return

    try:
        profile = fetch_profile_from_supabase(auth_session.user_id, storage_config, auth_session)
    except Exception:
        profile = None

    load_profile_into_session(profile)


def render_auth_panel(storage_config: StorageConfig) -> AuthSession | None:
    auth_session = get_auth_session()

    if storage_config.backend != "Supabase":
        st.warning("Add Supabase credentials in .env to use authentication.")
        return None

    if auth_session is not None:
        ensure_active_profile(storage_config, auth_session)
        return auth_session

    login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])

    with login_tab:
        with st.form("login-form"):
            email = st.text_input("Email", key="login-email")
            password = st.text_input("Password", type="password", key="login-password")
            login_submitted = st.form_submit_button("Log In")
        if login_submitted:
            try:
                session = sign_in_with_supabase(email, password, storage_config)
                profile = fetch_profile_from_supabase(session.user_id, storage_config, session)
            except Exception:
                st.error("Could not log in.")
            else:
                set_auth_session(session)
                load_profile_into_session(profile)
                st.success("Logged in.")
                st.rerun()

    with signup_tab:
        with st.form("signup-form"):
            email = st.text_input("Email", key="signup-email")
            password = st.text_input("Password", type="password", key="signup-password")
            signup_submitted = st.form_submit_button("Create Account")
        if signup_submitted:
            try:
                session, message = sign_up_with_supabase(email, password, storage_config)
            except Exception:
                st.error("Could not create account.")
            else:
                if session is None:
                    st.success(message)
                else:
                    set_auth_session(session)
                    load_profile_into_session(None)
                    st.success(message)
                    st.rerun()

    return None


def render_profile_tab(storage_config: StorageConfig) -> None:
    st.subheader("Basic User Profile")
    auth_session = get_auth_session()
    active_profile = st.session_state.get("active_profile") or {}

    if auth_session is None:
        st.caption("Log in first so the saved profile is linked to the signed-in user.")
        return

    st.caption("Save one profile for the signed-in user. The ingredient scanner will use this linked profile automatically.")

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
            placeholder="Anything else the team wants to keep with the profile",
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
                user_id=auth_session.user_id,
            )
            try:
                save_profile(profile, storage_config, auth_session=auth_session)
            except Exception:
                st.error("Could not save profile.")
            else:
                load_profile_into_session(profile)
                st.success("Profile saved.")


def render_scan_tab() -> None:
    st.subheader("Ingredient Scanner + Risk Score")
    auth_session = get_auth_session()
    active_profile = st.session_state.get("active_profile") or {}

    if auth_session is None:
        st.caption("Log in and save a profile first so scans stay linked to that user.")
        return

    st.caption("Upload a product label image. The scan uses the allergies saved on the linked profile.")
    linked_allergies = active_profile.get("allergies", [])
    if linked_allergies:
        st.write(f"Linked profile allergies: {', '.join(linked_allergies)}")
    else:
        st.write("No allergies saved on the linked profile yet.")

    use_sample = st.toggle("Use the sample ingredient-only image from the repo", value=True)

    uploaded_file = None
    if not use_sample:
        uploaded_file = st.file_uploader("Upload ingredient label image", type=["png", "jpg", "jpeg"])

    source_label = DEFAULT_SAMPLE_IMAGE.name if use_sample else (uploaded_file.name if uploaded_file else "")

    if st.button("Analyze Ingredients", use_container_width=True):
        if not use_sample and uploaded_file is None:
            st.error("Upload an image or switch on the sample image toggle.")
            return

        try:
            allergies_text = ", ".join(linked_allergies)
            if use_sample:
                result = analyze_ingredient_image(DEFAULT_SAMPLE_IMAGE, allergies=allergies_text)
                display_image = Image.open(DEFAULT_SAMPLE_IMAGE)
            else:
                image_bytes = uploaded_file.getvalue()
                result = analyze_ingredient_image(image_bytes, allergies=allergies_text)
                display_image = Image.open(uploaded_file)
            result["linked_profile"] = {
                "id": active_profile.get("id", auth_session.user_id),
                "name": active_profile.get("name", ""),
                "allergies": linked_allergies,
            }
            export_path = export_scan_result(result, source_label or "ingredient-scan")
        except Exception as exc:
            st.error(f"Scan failed: {exc}")
            return

        st.session_state["latest_scan"] = result
        st.session_state["latest_scan_path"] = str(export_path)
        st.session_state["latest_scan_source"] = source_label or "ingredient-scan"
        st.session_state["latest_image"] = display_image

    result = st.session_state.get("latest_scan")
    if not result:
        return

    left_col, right_col = st.columns([1, 1.1])
    with left_col:
        st.image(st.session_state.get("latest_image"), caption=st.session_state.get("latest_scan_source"))
        st.caption(f"JSON export saved to: {st.session_state.get('latest_scan_path')}")
    with right_col:
        risk = result["risk"]
        st.markdown(
            f"<div class='risk-pill' style='background:{risk['color']};'>{risk['level']} Risk</div>",
            unsafe_allow_html=True,
        )
        st.write(risk["summary"])
        st.markdown("**Allergy flags**")
        if result["allergy_flags"]:
            for flag in result["allergy_flags"]:
                st.write(f"- {flag['ingredient']}: {flag['reason']}")
        else:
            st.write("No direct allergy conflicts found.")

        st.markdown("**Sensitivity / yellow flags**")
        if result["yellow_flags"]:
            for flag in result["yellow_flags"]:
                st.write(f"- {flag['ingredient']}: {flag['reason']}")
        else:
            st.write("No yellow-flag ingredients detected.")

    st.markdown("**Extracted ingredient list**")
    st.dataframe(result["ingredients"], use_container_width=True)

    with st.expander("Raw OCR text"):
        st.text(result["raw_text"])

    json_bytes = json.dumps(result, indent=2).encode("utf-8")
    st.download_button(
        "Download scan JSON",
        data=json_bytes,
        file_name=Path(st.session_state.get("latest_scan_path", "ingredient-scan.json")).name,
        mime="application/json",
    )


def render_blood_tab() -> None:
    st.subheader("Blood Test Analysis")
    st.write("Blood Test Analysis Placeholder")


def generate_ai_chat_reply(message: str, active_profile: dict) -> str:
    lowered = message.lower()
    allergies = active_profile.get("allergies", [])
    conditions = active_profile.get("existing_conditions", [])
    name = active_profile.get("name", "there")

    if any(word in lowered for word in ["allergy", "ingredient", "scanner"]):
        if allergies:
            return (
                f"I'd start by checking ingredients against the saved allergy list for {name}: "
                f"{', '.join(allergies)}. If you want, paste a label or ask about one ingredient at a time."
            )
        return (
            "I can help review ingredient safety, but there are no allergies saved on the profile yet. "
            "Add them in User Profile first for more specific guidance."
        )

    if any(word in lowered for word in ["blood", "test", "lab", "result"]):
        return (
            "I can help summarize blood test results and suggest follow-up questions. "
            "Share the marker names or values you want to review, and I'll help organize them."
        )

    if any(word in lowered for word in ["profile", "condition", "health"]):
        if conditions:
            return (
                f"The saved profile includes these conditions: {', '.join(conditions)}. "
                "I can tailor suggestions around those if you tell me what you're trying to decide."
            )
        return (
            "I can help think through the saved profile, symptoms, or follow-up questions. "
            "Tell me what part of the health dashboard you want help with."
        )

    return (
        "I can help with ingredient scans, saved profile details, and blood test follow-up questions. "
        "Ask me about a symptom, lab marker, ingredient, or next step."
    )


def render_ai_chat_tab() -> None:
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">AI Chatbox</p>
            <p class="section-subtitle">
                Ask questions about ingredients, saved profile details, or blood test follow-up ideas.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "ai_chat_messages" not in st.session_state:
        st.session_state["ai_chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Hi, I can help you think through ingredient flags, profile details, "
                    "or blood test questions."
                ),
            }
        ]

    for message in st.session_state["ai_chat_messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_message = st.chat_input("Ask the AI chatbox a question", key="ai-chat-input")

    if user_message:
        active_profile = st.session_state.get("active_profile") or {}
        st.session_state["ai_chat_messages"].append({"role": "user", "content": user_message})
        reply = generate_ai_chat_reply(user_message, active_profile)
        st.session_state["ai_chat_messages"].append({"role": "assistant", "content": reply})
        st.rerun()


storage_config = get_storage_config()
auth_session = get_auth_session()

if auth_session is not None:
    ensure_active_profile(storage_config, auth_session)

st.markdown(
    f"""
    <div class="hero-card">
        <h1 class="app-title">Health Risk Score Dashboard</h1>
        <p class="app-subtitle">
            {"Signed in and ready to use your profile, ingredient scanner, and blood test tools." if auth_session is not None else "Sign in first to unlock your profile, ingredient scanner, and blood test tools."}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if auth_session is None:
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
        auth_session = render_auth_panel(storage_config)

if auth_session is not None:
    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.markdown(
            f"""
            <div class="hero-card">
                <h2 style="margin:0; color:#123b6b;">Welcome back</h2>
                <p style="margin:0.5rem 0 0 0; color:#4c6783;">
                    Signed in as {auth_session.email or auth_session.user_id}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with header_right:
        if st.button("Log out", use_container_width=True):
            try:
                sign_out_from_supabase(auth_session, storage_config)
            except Exception:
                pass
            set_auth_session(None)
            load_profile_into_session(None)
            st.rerun()

    profile_tab, scanner_tab, blood_tab, chat_tab = st.tabs(
        ["User Profile", "Ingredient Scanner", "Blood Test", "AI Chatbox"]
    )

    with profile_tab:
        render_profile_tab(storage_config)

    with scanner_tab:
        render_scan_tab()

    with blood_tab:
        render_blood_tab()

    with chat_tab:
        render_ai_chat_tab()
