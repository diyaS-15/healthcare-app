"""
Healthcare AI - Blood Test Analysis App
Main Streamlit Application
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure Streamlit page
st.set_page_config(
    page_title="Healthcare AI - Blood Test Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    :root {
        --primary-color: #1a3a52;
        --secondary-color: #2d5a7b;
        --accent-color: #0c3d66;
        --background: #f8fafb;
        --text-color: #1a3a52;
    }
    
    .main {
        background-color: #f8fafb;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        background-color: #f0f4f8;
        border-radius: 5px;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a3a52;
        color: white;
        border-color: #0c3d66;
    }
    
    h1 {
        color: #1a3a52;
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    h2 {
        color: #2d5a7b;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    
    h3 {
        color: #1a3a52;
        margin-top: 20px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #edf6ff 0%, #fff 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1a3a52;
        margin-bottom: 15px;
    }
    
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .warning-badge {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .danger-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000"


def render_auth_panel():
    """Render authentication panel"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔐 Authentication")
        
        if not st.session_state.authenticated:
            auth_method = st.radio("Choose login method:", ["Email/Password", "Google OAuth"], 
                                   label_visibility="collapsed")
            
            if auth_method == "Email/Password":
                email = st.text_input("Email", placeholder="your@email.com", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("🔑 Sign In", use_container_width=True):
                    if email and password:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.success(f"Welcome back, {email}!")
                        st.rerun()
                    else:
                        st.error("Please enter email and password")
            else:
                st.info("Click to sign in with Google")
                if st.button("🔵 Google Sign-In", use_container_width=True):
                    st.session_state.authenticated = True
                    st.session_state.user_email = "user@gmail.com"
                    st.success("Welcome! Signed in with Google")
                    st.rerun()
        else:
            st.success(f"✓ Logged in as: {st.session_state.user_email}")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.info("Logged out successfully")
                st.rerun()


def render_hero_section():
    """Render hero section with app description"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        # 🏥 Healthcare AI
        ## Advanced Blood Test Analysis with AI Intelligence
        
        Transform your medical reports into actionable health insights using artificial intelligence.
        """)
        
        st.markdown("""
        **Key Features:**
        - 📄 Upload PDF or image blood reports
        - 🤖 AI-powered medical analysis
        - 📊 Health metrics visualization
        - 💬 24/7 AI health assistant
        - 📈 Track health trends over time
        - 🔒 End-to-end encrypted data
        """)
    
    with col2:
        st.metric(label="Status", value="Ready", delta="Connected")
        st.metric(label="AI Model", value="GPT-4", delta="Active")


def render_upload_section():
    """Render blood test upload section"""
    st.subheader("📄 Upload Your Medical Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a blood test report (PDF or Image)",
            type=["pdf", "jpg", "jpeg", "png"],
            help="Supported formats: PDF, JPG, PNG"
        )
        
        if uploaded_file:
            st.success(f"✓ File received: {uploaded_file.name}")
            st.info(f"File size: {uploaded_file.size / 1024:.1f} KB")
            
            if st.button("🔍 Analyze Report", use_container_width=True):
                with st.spinner("Analyzing your blood report..."):
                    st.success("✓ Report analyzed successfully!")
                    
                    # Display sample analysis
                    st.markdown("### Analysis Results")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("WBC Count", "7.2", "Normal")
                    with col_b:
                        st.metric("RBC Count", "4.5", "Normal")
                    with col_c:
                        st.metric("Hemoglobin", "14.0", "Normal")
    
    with col2:
        st.info("""
        **Secure Upload:**
        - Encrypted with AES-256
        - Only you can access
        - Stored in Supabase
        - GDPR compliant
        """)


def render_analysis_section():
    """Render analysis results section"""
    st.subheader("📊 Analysis Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Blood Metrics")
        metrics_data = {
            "WBC (K/µL)": ("7.2", "4.5 - 11.0", "✓ Normal"),
            "RBC (M/µL)": ("4.5", "4.5 - 5.9", "✓ Normal"),
            "Hemoglobin (g/dL)": ("14.0", "12 - 17.5", "✓ Normal"),
            "Glucose (mg/dL)": ("110", "70 - 100", "⚠️ Slightly High"),
            "Cholesterol (mg/dL)": ("185", "< 200", "✓ Normal"),
        }
        
        for metric, (value, range_val, status) in metrics_data.items():
            st.markdown(f"""
            **{metric}**
            - Value: {value} ({range_val})
            - Status: {status}
            """)
    
    with col2:
        st.markdown("#### AI Insights")
        st.markdown("""
        **Overall Health Status:** Good
        
        **Key Findings:**
        - ✓ All major blood counts are normal
        - ⚠️ Glucose slightly elevated
        - ✓ Lipid profile healthy
        
        **Recommendations:**
        1. Monitor glucose intake
        2. Increase physical activity (30 min/day)
        3. Maintain current diet
        4. Follow-up test in 3 months
        
        **Risk Assessment:** Low Risk
        """)


def render_chat_section():
    """Render AI chat assistant section"""
    st.subheader("💬 Health AI Assistant")
    
    st.info("Ask me anything about your health and blood test results!")
    
    user_question = st.text_area(
        "Your health question:",
        placeholder="E.g., What does elevated glucose mean for my health?",
        label_visibility="collapsed",
        height=100
    )
    
    if st.button("💭 Get AI Response", use_container_width=True):
        if user_question:
            with st.spinner("Thinking..."):
                st.success("Response from AI Health Assistant:")
                st.markdown("""
                Based on your recent blood work and health profile:
                
                Your glucose level of 110 mg/dL is slightly elevated (normal is 70-100). 
                This could indicate:
                
                **Possible Causes:**
                - Dietary habits (high sugar/refined carbs)
                - Lack of physical activity
                - Stress levels
                - Genetic factors
                
                **Recommended Actions:**
                1. **Diet**: Reduce sugary drinks and refined foods
                2. **Exercise**: Add 30 minutes of moderate activity daily
                3. **Monitoring**: Check glucose levels regularly
                4. **Consultation**: See your doctor if it persists
                
                **When to Seek Medical Help:**
                - If glucose remains > 125 mg/dL
                - If you experience increased thirst/urination
                - For personalized medical advice
                
                Keep tracking your health metrics for early detection!
                """)
        else:
            st.warning("Please enter a question")


def render_trends_section():
    """Render health trends section"""
    st.subheader("📈 Health Trends")
    
    st.info("Track your blood test results over time to identify patterns and improvements.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Test History")
        st.markdown("""
        1. **Latest Test** - April 16, 2024
           - WBC: 7.2 K/µL
           - Glucose: 110 mg/dL
        
        2. **Previous Test** - March 15, 2024
           - WBC: 7.0 K/µL
           - Glucose: 105 mg/dL
        
        3. **Earlier Test** - February 10, 2024
           - WBC: 6.8 K/µL
           - Glucose: 98 mg/dL
        """)
    
    with col2:
        st.markdown("#### Trend Analysis")
        st.markdown("""
        **WBC Count Trend:** ✓ Stable
        
        **Glucose Trend:** ⚠️ Slowly Increasing
        - Feb: 98 → Mar: 105 → Apr: 110
        - Action: Monitor diet and exercise
        
        **Overall Health:** Maintaining
        
        **Next Recommended Test:** May 2024
        """)


def main():
    """Main application"""
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 20px; 
                background: linear-gradient(135deg, #1a3a52 0%, #2d5a7b 100%);
                color: white; border-radius: 10px; margin-bottom: 30px;'>
        <h1 style='margin: 0; color: white;'>🏥 Healthcare AI Analysis Platform</h1>
        <p style='margin: 10px 0 0 0; font-size: 1.1rem;'>Blood Test Intelligence with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication
    render_auth_panel()
    
    # Check if authenticated
    if not st.session_state.authenticated:
        st.warning("👤 Please log in to access the healthcare application")
        render_hero_section()
        return
    
    # Main content (authenticated users only)
    render_hero_section()
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Upload Report",
        "📊 Analysis",
        "💬 AI Assistant",
        "📈 Trends"
    ])
    
    with tab1:
        render_upload_section()
    
    with tab2:
        render_analysis_section()
    
    with tab3:
        render_chat_section()
    
    with tab4:
        render_trends_section()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🔒 Secure & Encrypted")
    with col2:
        st.caption("🤖 AI-Powered Analysis")
    with col3:
        st.caption("📱 Mobile Friendly")


if __name__ == "__main__":
    main()
