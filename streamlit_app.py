"""HealthLens - Blood Test Analysis Platform"""
import streamlit as st

st.set_page_config(page_title="HealthLens", page_icon="H", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main { background-color: #f8fafb; }
    h1 { color: #1a3a52; }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None


def render_login():
    """Login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <h1 style='font-size: 3rem; color: #1a3a52; margin: 0;'>HealthLens</h1>
            <p style='color: #2d5a7b; font-size: 1.1rem;'>Blood Test Analysis Platform</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            st.subheader("Sign In")
            email = st.text_input("Email", placeholder="your@email.com", key="email1")
            password = st.text_input("Password", type="password", key="pass1")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Sign In", use_container_width=True, type="primary"):
                    if email and password:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.success(f"Welcome, {email}!")
                        st.rerun()
                    else:
                        st.error("Enter email and password")
            with col_b:
                if st.button("Google", use_container_width=True):
                    st.session_state.authenticated = True
                    st.session_state.user_email = "user@gmail.com"
                    st.success("Signed in with Google")
                    st.rerun()
        
        with tab2:
            st.subheader("Create Account")
            new_email = st.text_input("Email", placeholder="your@email.com", key="email2")
            new_pass = st.text_input("Password", type="password", key="pass2")
            conf_pass = st.text_input("Confirm Password", type="password", key="pass3")
            
            if st.button("Sign Up", use_container_width=True, type="primary"):
                if new_email and new_pass and conf_pass:
                    if new_pass == conf_pass:
                        st.session_state.authenticated = True
                        st.session_state.user_email = new_email
                        st.success(f"Welcome, {new_email}!")
                        st.rerun()
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Fill all fields")


def render_app():
    """Main app"""
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("HealthLens")
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.caption(f"Logged in: {st.session_state.user_email}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Upload", "Analysis", "Chat", "Trends"])
    
    with tab1:
        st.subheader("Upload Report")
        file = st.file_uploader("Upload blood test (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])
        if file:
            st.success(f"File: {file.name}")
            if st.button("Analyze"):
                with st.spinner("Analyzing..."):
                    st.success("Complete!")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("WBC", "7.2", "Normal")
                    with col_m2:
                        st.metric("RBC", "4.5", "Normal")
                    with col_m3:
                        st.metric("Hemoglobin", "14.0", "Normal")
    
    with tab2:
        st.subheader("Analysis Results")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""**Blood Metrics**
- WBC: 7.2 (4.5-11.0)
- RBC: 4.5 (4.5-5.9)
- Hemoglobin: 14.0 (12-17.5)
- Glucose: 110 (70-100)
- Cholesterol: 185 (<200)""")
        with col_r:
            st.markdown("""**AI Insights**
**Status:** Good

**Findings:**
- All counts normal
- Glucose slightly elevated
- Lipid profile healthy

**Recommendations:**
1. Monitor glucose
2. Increase activity
3. Follow-up in 3 months""")
    
    with tab3:
        st.subheader("Health Assistant")
        q = st.text_area("Ask a health question", placeholder="What does elevated glucose mean?", height=80)
        if st.button("Get Answer"):
            if q:
                with st.spinner("Thinking..."):
                    st.success("AI Response:")
                    st.markdown("""Your glucose (110 mg/dL) is slightly elevated. Consider:
- Reduce sugar intake
- Add 30 min daily activity
- Monitor regularly
- See doctor if persists""")
            else:
                st.warning("Ask a question")
    
    with tab4:
        st.subheader("Health Trends")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("""**Test History**
1. Apr 16: WBC 7.2, Glucose 110
2. Mar 15: WBC 7.0, Glucose 105
3. Feb 10: WBC 6.8, Glucose 98""")
        with col_h2:
            st.markdown("""**Trend Analysis**
WBC: Stable
Glucose: Increasing
Overall: Good
Next Test: May 2024""")


if __name__ == "__main__":
    if not st.session_state.authenticated:
        render_login()
    else:
        render_app()
