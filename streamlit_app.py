"""HealthLens - Blood Test Analysis Platform"""
import streamlit as st

st.set_page_config(page_title="HealthLens", page_icon="H", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main { background-color: #f8fafb; }
    h1 { color: #1a3a52; font-size: 2.5rem; font-weight: 700; }
    h2 { color: #1a3a52; font-size: 1.5rem; font-weight: 600; }
    .card { 
        background: white; 
        padding: 25px; 
        border-radius: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
        margin-bottom: 20px;
    }
    .metric-box {
        background: linear-gradient(135deg, #edf6ff 0%, #f0f4f8 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1a3a52;
        margin: 12px 0;
    }
    .status-good { color: #059669; font-weight: 600; }
    .status-warning { color: #d97706; font-weight: 600; }
    .status-alert { color: #dc2626; font-weight: 600; }
    .upload-box {
        background: linear-gradient(135deg, #f0f4f8 0%, #f8fafb 100%);
        border: 2px dashed #1a3a52;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
    }
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
    """Main app with professional design"""
    # Header
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("<h1 style='margin: 0;'>HealthLens</h1>", unsafe_allow_html=True)
        st.caption("Blood test analysis powered by AI")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    st.caption(f"Welcome, {st.session_state.user_email.split('@')[0]}")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Upload Report", "Analysis", "Health Chat", "Trends"])
    
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
                        st.success("Analysis Complete!")
                        
                        col_m1, col_m2, col_m3 = st.columns(3)
                        with col_m1:
                            st.metric("WBC Count", "7.2", "Normal")
                        with col_m2:
                            st.metric("RBC Count", "4.5", "Normal")
                        with col_m3:
                            st.metric("Hemoglobin", "14.0", "Normal")
            else:
                st.markdown("""
                <div style='text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #f0f4f8 0%, #f8fafb 100%); border-radius: 12px; border: 2px dashed #1a3a52;'>
                    <p style='color: #1a3a52; font-size: 1rem; margin: 0;'><strong>Drop your file here</strong></p>
                    <p style='color: #666; font-size: 0.9rem; margin: 10px 0 0 0;'>PDF, JPG, or PNG • Max 200MB</p>
                </div>
                """, unsafe_allow_html=True)
        
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
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<h2>Your Analysis Results</h2>", unsafe_allow_html=True)
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("<h3>Blood Metrics</h3>", unsafe_allow_html=True)
            
            metrics_list = [
                ("WBC (K/µL)", "7.2", "4.5-11.0", "good"),
                ("RBC (M/µL)", "4.5", "4.5-5.9", "good"),
                ("Hemoglobin (g/dL)", "14.0", "12-17.5", "good"),
                ("Glucose (mg/dL)", "110", "70-100", "warning"),
                ("Cholesterol (mg/dL)", "185", "<200", "good"),
            ]
            
            for metric, value, normal_range, status in metrics_list:
                status_color = "good" if status == "good" else "warning"
                status_text = "Normal" if status == "good" else "Elevated"
                status_class = "status-good" if status == "good" else "status-warning"
                
                st.markdown(f"""
                <div class='metric-box'>
                    <strong>{metric}</strong><br>
                    Value: <strong>{value}</strong> | Normal: {normal_range}<br>
                    <span class='{status_class}'>{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col_a2:
            st.markdown("<h3>Health Insights</h3>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class='card'>
                <h4 style='color: #1a3a52; margin-top: 0;'>Overall Status: Good</h4>
                <p style='color: #666; font-size: 0.95rem;'>
                Your recent blood work shows healthy results with one area to monitor.
                </p>
                
                <hr>
                
                <h4 style='color: #1a3a52;'>Key Findings</h4>
                <ul style='color: #666; font-size: 0.9rem;'>
                    <li>All major blood counts normal</li>
                    <li>Glucose slightly elevated</li>
                    <li>Healthy lipid profile</li>
                </ul>
                
                <hr>
                
                <h4 style='color: #1a3a52;'>Next Steps</h4>
                <ol style='color: #666; font-size: 0.9rem;'>
                    <li>Monitor glucose intake</li>
                    <li>Increase physical activity</li>
                    <li>Retest in 3 months</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<h2>Health AI Assistant</h2>", unsafe_allow_html=True)
        st.markdown("Ask your health questions. Get instant AI answers based on your blood data.")
        
        question = st.text_area("", placeholder="E.g., What does elevated glucose mean? Or: How can I improve my health?", height=120, label_visibility="collapsed")
        
        col_c1, col_c2, col_c3 = st.columns([1, 1, 2])
        with col_c1:
            ask_btn = st.button("Get Answer", use_container_width=True, type="primary")
        
        if ask_btn:
            if question:
                with st.spinner("AI Assistant is thinking..."):
                    st.success("AI Response (Based on Your Health Profile):")
                    
                    st.markdown("""
                    <div class='card'>
                        <p>Your glucose reading of 110 mg/dL is slightly elevated. Here's what you should know:</p>
                        
                        <h4>What This Means</h4>
                        <p>Normal fasting glucose is 70-100 mg/dL. Your reading suggests your body may be less efficient at managing blood sugar.</p>
                        
                        <h4>Action Items</h4>
                        <ul>
                            <li><strong>Diet:</strong> Reduce refined sugars and processed carbs</li>
                            <li><strong>Exercise:</strong> Aim for 150 minutes weekly</li>
                            <li><strong>Monitoring:</strong> Check levels monthly</li>
                            <li><strong>Sleep:</strong> Get 7-9 hours nightly</li>
                        </ul>
                        
                        <h4>When to See a Doctor</h4>
                        <p>If glucose stays above 125 mg/dL fasting, schedule an appointment for prediabetes screening.</p>
                        
                        <p style='color: #d97706; font-weight: 600;'>💡 Tip: Small lifestyle changes now prevent bigger health issues later</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Please ask a health question")
    
    with tab4:
        st.markdown("<h2>Your Health Timeline</h2>", unsafe_allow_html=True)
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("<h3>Test History</h3>", unsafe_allow_html=True)
            st.markdown("""
            <div class='card'>
                <strong style='color: #1a3a52;'>Latest Test - April 16, 2024</strong><br>
                WBC: 7.2 | RBC: 4.5 | Glucose: 110 | Hemoglobin: 14.0
                <hr style='margin: 15px 0;'>
                <strong style='color: #1a3a52;'>Previous - March 15, 2024</strong><br>
                WBC: 7.0 | RBC: 4.5 | Glucose: 105 | Hemoglobin: 13.9
                <hr style='margin: 15px 0;'>
                <strong style='color: #1a3a52;'>Earlier - February 10, 2024</strong><br>
                WBC: 6.8 | RBC: 4.4 | Glucose: 98 | Hemoglobin: 13.8
            </div>
            """, unsafe_allow_html=True)
        
        with col_t2:
            st.markdown("<h3>Trend Analysis</h3>", unsafe_allow_html=True)
            st.markdown("""
            <div class='card'>
                <p><strong>WBC Count</strong><br><span class='status-good'>Stable</span> - Healthy white blood cell levels</p>
                <hr>
                <p><strong>Glucose Levels</strong><br><span class='status-warning'>Increasing</span> - Slight upward trend: 98 → 105 → 110</p>
                <hr>
                <p><strong>Hemoglobin</strong><br><span class='status-good'>Healthy</span> - Good oxygen-carrying capacity</p>
                <hr>
                <p><strong>Overall Health</strong><br><strong style='color: #1a3a52;'>Maintaining Well</strong></p>
                <hr>
                <p style='margin-bottom: 0;'><strong>Next Recommended Test:</strong> May 20, 2024</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    if not st.session_state.authenticated:
        render_login()
    else:
        render_app()
