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
    .hero-card {
        padding: 1.25rem 1.5rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #f5fbff 0%, #eef8f2 100%);
        border: 1px solid #d0e4dd;
        margin-bottom: 1rem;
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
        border: 1px solid #e4e7ec;
        background: #ffffff;
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


def render_auth_panel(storage_config: StorageConfig) -> AuthSession | None:
    auth_session = get_auth_session()

    if storage_config.backend != "Supabase":
        st.warning("Add Supabase credentials in .env to use authentication.")
        return None

    st.subheader("Authentication")

    if auth_session is not None:
        left_col, right_col = st.columns([3, 1])
        with left_col:
            st.caption(f"Signed in as {auth_session.email or auth_session.user_id}")
        with right_col:
            if st.button("Log out", use_container_width=True):
                try:
                    sign_out_from_supabase(auth_session, storage_config)
                except Exception:
                    pass
                set_auth_session(None)
                load_profile_into_session(None)
                st.rerun()

        if not st.session_state.get("active_profile"):
            try:
                profile = fetch_profile_from_supabase(auth_session.user_id, storage_config, auth_session)
            except Exception:
                profile = None
            load_profile_into_session(profile)
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


storage_config = get_storage_config()
render_auth_panel(storage_config)

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown(
        """
        <div class="hero-card">
            <h1 style="margin:0; color:#123524;">Health Risk Score Dashboard</h1>
            <p style="margin:0.5rem 0 0 0; color:#344054;">
                Basic user profile + ingredient scanner for your team project, with room to plug in the AI chatbot later.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_right:
    st.write("")
    if st.button("AI chatbot", use_container_width=True):
        st.write("AI chatbot placeholder")

profile_tab, scanner_tab, blood_tab = st.tabs(["User Profile", "Ingredient Scanner", "Blood Test"])

with profile_tab:
    render_profile_tab(storage_config)

with scanner_tab:
    render_scan_tab()

with blood_tab:
    render_blood_tab()
