"""Introduction page for the BNI Palms Analysis application."""

import streamlit as st

from src.infrastructure.config.settings import get_settings


def render_introduction_page():
    """Render the introduction page."""
    settings = get_settings()
    
    # Page title
    st.title(f"📊 {settings.app_name}")
    st.markdown(f"*Version {settings.version}*")
    
    # Introduction section
    st.markdown("""
    ### 👋 Welcome to BNI Palms Analysis
    
    This application helps BNI chapters analyze their PALMS (Palms Audit and Logging Management System) data 
    to gain insights into referrals, one-to-one meetings, and overall member engagement patterns.
    """)
    
    # Features overview
    st.markdown("""
    ### ✨ Key Features
    
    - **📈 Referral Analysis**: Track and analyze referral patterns between members
    - **🤝 One-to-One Tracking**: Monitor one-to-one meeting activities
    - **🔄 Combination Matrix**: Understand the relationship between referrals and meetings
    - **📊 Matrix Comparison**: Compare performance over different time periods
    - **📋 Automated Reports**: Generate comprehensive Excel reports
    - **🎯 Performance Insights**: Get actionable insights for chapter improvement
    """)
    
    # How it works
    st.markdown("""
    ### 🔧 How It Works
    
    1. **📤 Upload Your Data**: Upload BNI PALMS slip audit reports and member lists
    2. **⚡ Automatic Processing**: The system processes your data and validates quality
    3. **📊 Generate Reports**: Create detailed matrices showing member interactions
    4. **📈 Analyze Trends**: Compare current performance with historical data
    5. **💡 Get Insights**: Receive actionable recommendations for chapter growth
    """)
    
    # Getting started
    st.markdown("""
    ### 🚀 Getting Started
    
    #### Step 1: Prepare Your Data
    Download the following files from BNI Connect:
    
    **Slip Audit Reports:**
    1. Go to [BNI Connect Global](https://bniconnectglobal.com/)
    2. Navigate to **Operations → Chapter → Meeting Management**
    3. Select **View PALMS Summary**
    4. Choose your date range and click on completed meetings
    5. Download **Slip Audit Report** (Export without Headers)
    
    **Member Details:**
    1. Go to **Reports → Chapter → Summary PALMS Report**
    2. Enter current date and click "Go"
    3. Download the member details (Export without Headers)
    
    #### Step 2: Use the Application
    - Visit the **"PALMS Analysis"** page to generate your reports
    - Visit the **"Matrix Comparison"** page to compare different time periods
    """)
    
    # Report types explanation
    st.markdown("""
    ### 📄 Report Types
    
    **Referral Matrix (`referral_matrix.xlsx`)**
    - Shows referrals given and received between all members
    - Includes totals and unique referral counts
    - Yellow highlighting indicates zero referrals
    
    **One-to-One Matrix (`OTO_matrix.xlsx`)**
    - Displays one-to-one meetings between members
    - Symmetric matrix (meetings count for both participants)
    - Summary statistics for networking activity
    
    **Combination Matrix (`combination_matrix.xlsx`)**
    - Combines referral and one-to-one data
    - Values: 0=Neither, 1=OTO only, 2=Referral only, 3=Both
    - Identifies relationship patterns between members
    
    **Comparison Matrix (`combination_matrix_comparison.xlsx`)**
    - Compares current and historical performance
    - Shows growth/decline indicators
    - Provides change analysis with visual indicators
    """)
    
    # Tips and best practices
    st.markdown("""
    ### 💡 Tips for Best Results
    
    - **Consistent Data**: Ensure member names are consistent across all files
    - **Complete Records**: Upload all slip audit reports for the analysis period
    - **Regular Analysis**: Compare data regularly to track improvement trends
    - **Data Quality**: Review any validation warnings to ensure accurate results
    - **File Formats**: Both .xls and .xlsx formats are supported
    """)
    
    # Support section
    st.markdown("""
    ### 🆘 Need Help?
    
    If you encounter any issues or have questions:
    
    - Check the validation messages for data quality issues
    - Ensure your files are in the correct format (.xls or .xlsx)
    - Verify that member names match exactly between files
    - Make sure slip audit reports contain the expected columns (Giver, Receiver, Slip Type)
    
    For technical support or feature requests, please contact your system administrator.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666666; font-size: 12px;'>
        {settings.app_name} v{settings.version} | 
        Built for BNI Chapter Analysis | 
        Powered by Streamlit
    </div>
    """, unsafe_allow_html=True)