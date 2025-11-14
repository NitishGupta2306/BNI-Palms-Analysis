#!/usr/bin/env python3
"""
BNI PALMS Analysis - Streamlit Web Application

Modern web interface for BNI chapter analysis using the new clean architecture.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the new page modules
from src.presentation.streamlit.pages.introduction_page import render_introduction_page
from src.presentation.streamlit.pages.reports_page import render_reports_page
from src.presentation.streamlit.pages.comparison_page import render_comparison_page
from src.infrastructure.config.settings import get_settings

# Configure Streamlit page
st.set_page_config(
    page_title="BNI PALMS Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display deprecation warning banner
st.markdown("""
<div style='background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
            border-left: 6px solid #c92a2a;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0 30px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
    <h2 style='color: white; margin-top: 0; margin-bottom: 10px; font-size: 24px;'>
        ⚠️ Application Deprecation Notice
    </h2>
    <p style='color: white; font-size: 16px; line-height: 1.6; margin-bottom: 15px;'>
        <strong>This application is being deprecated and will be shut down on November 28, 2025.</strong>
    </p>
    <p style='color: white; font-size: 15px; line-height: 1.6; margin-bottom: 0;'>
        If you would like access to the current software, please contact us at:
        <a href='https://www.ortus-solutions.com'
           target='_blank'
           style='color: #fff3bf; font-weight: bold; text-decoration: underline;'>
            Ortus Solutions
        </a>
    </p>
</div>
""", unsafe_allow_html=True)

# Page definitions using new architecture
intro_page = st.Page(
    render_introduction_page,
    title="Introduction",
    icon=":material/waving_hand:",
    default=True,
)

report_page = st.Page(
    render_reports_page,
    title="PALMS Analysis", 
    icon=":material/partner_exchange:",
)

comparison_page = st.Page(
    render_comparison_page,
    title="Matrix Comparison",
    icon=":material/compare:",
)

# Navigation setup
pg = st.navigation(
    {
        "📋 Info": [intro_page],
        "📊 Analysis": [report_page, comparison_page],
    }
)

# Add footer with version info
settings = get_settings()
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='text-align: center; color: #666666; font-size: 12px;'>
    {settings.app_name}<br>
    Version {settings.version}
</div>
""", unsafe_allow_html=True)

# Run the application
pg.run()