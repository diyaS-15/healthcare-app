"""Healthcare App - Streamlit Entry Point for Cloud Deployment"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import and run the main Streamlit app
from blood_report_ai.Frontend.UserProfile import *
