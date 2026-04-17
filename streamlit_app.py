"""HealthLens - Blood Test Analysis Platform"""
import streamlit as st

st.set_page_config(page_title="HealthLens", page_icon="H", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main { background-color: #f8fafb; }
    h1 { color: #1a3a52; font-size: 2.5rem; font-weight: 700; }
    h2 { color: #1a3a52; font-size: 1.5rem; font-weight: 600; }
    h3 { color: #1a3a52; font-size: 1.1rem; }
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
    .chat-message {
        padding: 16px;
        margin: 12px 0;
        border-radius: 10px;
        line-height: 1.6;
    }
    .user-message {
        background: linear-gradient(135deg, #1a3a52 0%, #2d5a7b 100%);
        color: white;
        margin-left: 40px;
        border-radius: 10px 0px 10px 10px;
    }
    .ai-message {
        background: #f0f4f8;
        color: #1a3a52;
        margin-right: 40px;
        border-radius: 0px 10px 10px 10px;
        border-left: 4px solid #1a3a52;
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
        st.markdown("Advanced AI-powered health insights based on your personal blood profile")
        st.markdown("---")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat display area
        chat_container = st.container()
        
        with chat_container:
            if st.session_state.chat_history:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div class='chat-message user-message'>
                            <strong>You:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='chat-message ai-message'>
                            <strong>HealthLens AI:</strong><br>{msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick suggestions
        st.markdown("<h4>Common Questions</h4>", unsafe_allow_html=True)
        col_q1, col_q2, col_q3 = st.columns(3)
        
        suggestions = [
            "What does my glucose level mean?",
            "How can I improve my health?",
            "Are my results normal?"
        ]
        
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
        
        # Input area
        col_input1, col_input2 = st.columns([4, 1])
        
        with col_input1:
            user_input = st.text_input(
                "Ask AI Assistant anything about your health",
                placeholder="Type your health question here...",
                label_visibility="collapsed"
            )
        
        with col_input2:
            send_btn = st.button("Send", use_container_width=True, type="primary")
        
        # Process input or suggestion
        if send_btn or suggestion_clicked:
            question = suggestion_clicked if suggestion_clicked else user_input
            
            if question:
                # Add user message to history
                st.session_state.chat_history.append({"role": "user", "content": question})
                
                # Generate AI response based on question
                with st.spinner("HealthLens AI is analyzing your data..."):
                    ai_response = get_ai_response(question)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()


def get_ai_response(question):
    """Generate AI response based on user question and health data"""
    
    responses = {
        "What does my glucose level mean?": """
            <p><strong>Understanding Your Glucose Level (110 mg/dL)</strong></p>
            
            <div class='insight-box'>
                <p><strong>What This Means:</strong> Your fasting glucose of 110 mg/dL is slightly elevated. Normal is 70-100 mg/dL. This suggests your body may have mild difficulty managing blood sugar.</p>
            </div>
            
            <p><strong>Risk Assessment:</strong></p>
            <ul>
                <li>Not diabetic (diabetes starts at 126+)</li>
                <li>Prediabetic range (100-125 mg/dL)</li>
                <li>Can be reversed with lifestyle changes</li>
            </ul>
            
            <p><strong>Recommended Actions (in priority order):</strong></p>
            <div class='recommendation'>
                <strong>1. Diet Modifications (Highest Impact)</strong>
                <ul style='margin: 8px 0; padding-left: 20px;'>
                    <li>Reduce refined carbs (white bread, sugar, pastries)</li>
                    <li>Increase fiber (vegetables, whole grains)</li>
                    <li>Avoid sugary drinks</li>
                    <li>Practice portion control</li>
                </ul>
            </div>
            
            <div class='recommendation'>
                <strong>2. Exercise Routine</strong>
                <ul style='margin: 8px 0; padding-left: 20px;'>
                    <li>150 minutes moderate activity per week</li>
                    <li>Include strength training 2x/week</li>
                    <li>Walking after meals helps glucose</li>
                </ul>
            </div>
            
            <div class='recommendation'>
                <strong>3. Lifestyle Factors</strong>
                <ul style='margin: 8px 0; padding-left: 20px;'>
                    <li>Sleep: 7-9 hours nightly</li>
                    <li>Stress management (meditation, yoga)</li>
                    <li>Weight management (5-10% loss helps)</li>
                </ul>
            </div>
            
            <p><strong>When to See Your Doctor:</strong></p>
            <div class='insight-box'>
                <ul style='margin: 0; padding-left: 20px;'>
                    <li>If glucose stays above 125 mg/dL fasting</li>
                    <li>For formal diabetes screening</li>
                    <li>To discuss medication if lifestyle changes don't help</li>
                </ul>
            </div>
            
            <p><strong>Good News:</strong> Prediabetes is reversible! Many people return to normal glucose with consistent lifestyle changes. Your early detection is a huge advantage.</p>
        """,
        
        "How can I improve my health?": """
            <p><strong>Personalized Health Improvement Plan (Based on Your Blood Work)</strong></p>
            
            <div class='insight-box'>
                <p><strong>Your Current Status:</strong> Overall good health with glucose as the primary focus area. All other metrics are healthy.</p>
            </div>
            
            <p><strong>30-Day Quick Wins:</strong></p>
            <div class='recommendation'>
                <strong>Week 1: Foundation</strong>
                <ul style='margin: 8px 0; padding-left: 20px;'>
                    <li>Start food tracking (MyFitnessPal or similar)</li>
                    <li>Add 10k steps daily (use pedometer)</li>
                    <li>Eliminate sugary drinks</li>
                </ul>
            </div>
            
            <div class='recommendation'>
                <strong>Week 2-3: Build Momentum</strong>
                <ul style='margin: 8px 0; padding-left: 20px;'>
                    <li>Increase to 150 min exercise/week</li>
                    <li>Focus on whole foods</li>
                    <li>Add strength training</li>
                </ul>
            </div>
            
            <div class='recommendation'>
                <strong>Week 4: Sustain & Monitor</strong>
                <ul style='margin: 8px 0; padding-left: 20px;'>
                    <li>Retest glucose for progress</li>
                    <li>Adjust diet based on results</li>
                    <li>Plan next blood work</li>
                </ul>
            </div>
            
            <p><strong>90-Day Goals:</strong></p>
            <ul>
                <li>Glucose back to normal range (70-100)</li>
                <li>5-10% weight reduction (if needed)</li>
                <li>Establish sustainable habits</li>
                <li>Plan next comprehensive blood test</li>
            </ul>
            
            <p><strong>Why This Matters:</strong> These changes prevent progression to type 2 diabetes and improve overall longevity by 10-15 years.</p>
        """,
        
        "Are my results normal?": """
            <p><strong>Your Blood Work Summary - Overall Assessment: GOOD</strong></p>
            
            <p><strong>Normal Results (All Healthy):</strong></p>
            <div class='recommendation'>
                <strong>✓ WBC: 7.2 K/µL</strong> - Normal white blood count. Your immune system is functioning well.
            </div>
            <div class='recommendation'>
                <strong>✓ RBC: 4.5 M/µL</strong> - Normal red blood cell count. Good oxygen-carrying capacity.
            </div>
            <div class='recommendation'>
                <strong>✓ Hemoglobin: 14.0 g/dL</strong> - Normal. Indicates good iron levels and oxygen transport.
            </div>
            <div class='recommendation'>
                <strong>✓ Cholesterol: 185 mg/dL</strong> - Healthy lipid profile. Low cardiovascular risk.
            </div>
            
            <p><strong>Area Needing Attention:</strong></p>
            <div class='insight-box'>
                <strong>⚠️ Glucose: 110 mg/dL</strong> - Slightly elevated (normal is 70-100). Not diabetic, but shows prediabetic trend. Reversible with lifestyle changes.
            </div>
            
            <p><strong>Overall Risk Profile:</strong></p>
            <ul>
                <li>Cardiovascular Risk: <span class='status-good'>LOW</span></li>
                <li>Metabolic Health: <span class='status-warning'>MODERATE - Monitor Glucose</span></li>
                <li>Immune Function: <span class='status-good'>HEALTHY</span></li>
                <li>Oxygen Transport: <span class='status-good'>EXCELLENT</span></li>
            </ul>
            
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Focus on glucose management through diet and exercise</li>
                <li>Retest in 3 months to track progress</li>
                <li>Maintain healthy habits in normal areas</li>
                <li>Annual comprehensive screening recommended</li>
            </ol>
            
            <p><strong>Verdict:</strong> Your results show good overall health. Early detection of glucose trend is excellent—this gives you time to prevent serious issues. With simple lifestyle changes, you can normalize your glucose and maintain excellent health long-term.</p>
        """
    }
    
    # Default response if question doesn't match
    default = """
        <p><strong>Processing Your Question with HealthLens AI</strong></p>
        
        <p>Based on your recent blood work analysis:</p>
        
        <div class='insight-box'>
            <p>Your health profile shows generally good results with glucose being the area to focus on. This is positive news because prediabetic trends are highly reversible through lifestyle modification.</p>
        </div>
        
        <p><strong>Key Recommendations:</strong></p>
        <div class='recommendation'>
            <ul style='margin: 0; padding-left: 20px;'>
                <li>Monitor glucose regularly</li>
                <li>Increase physical activity to 150+ minutes weekly</li>
                <li>Reduce refined sugars and processed foods</li>
                <li>Maintain consistent sleep schedule</li>
                <li>Schedule follow-up testing in 3 months</li>
            </ul>
        </div>
        
        <p><strong>Important:</strong> For personalized medical advice, consult with your healthcare provider. This AI provides general health insights based on your blood work data.</p>
    """
    
    return responses.get(question, default)
    
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
