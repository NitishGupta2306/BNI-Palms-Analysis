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