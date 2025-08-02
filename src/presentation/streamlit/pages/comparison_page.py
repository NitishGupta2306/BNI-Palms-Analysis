"""Matrix comparison page for comparing performance over time."""

import streamlit as st
from typing import Optional

from src.application.use_cases.compare_matrices import CompareMatricesUseCase
from src.application.dto.report_request import MatrixComparisonRequest
from src.presentation.streamlit.components.file_uploader import create_matrix_uploader
from src.presentation.streamlit.utils.streamlit_helpers import (
    display_matrix_comparison_results, create_progress_tracker, 
    display_file_validation_results, safe_streamlit_operation
)
from src.infrastructure.config.paths import get_path_manager
from src.infrastructure.config.settings import configure_app


def render_comparison_page():
    """Render the matrix comparison page."""
    # Initialize application
    configure_app()
    
    # Initialize use case
    compare_matrices_use_case = CompareMatricesUseCase()
    path_manager = get_path_manager()
    
    st.title("🔄 Combination Matrix Comparison")
    
    # Introduction
    st.markdown("""
    ### 📈 Compare Performance Over Time
    
    This tool helps you compare two combination matrices to identify trends, improvements, 
    and areas that need attention in your BNI chapter's performance.
    
    **What you'll get:**
    - 📊 Enhanced matrix with comparison columns
    - 📈 Growth/decline indicators for each member
    - 💡 Insights about chapter performance trends
    - 🎯 Recommendations for improvement
    """)
    
    # Progress tracker
    steps = ["Upload Matrices", "Validate Files", "Compare Data", "Generate Insights", "Download Results"]
    current_step = _determine_current_step()
    create_progress_tracker(steps, current_step)
    
    # File upload section
    st.markdown("---")
    st.header("📤 Step 1: Upload Your Matrix Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 New Matrix")
        st.markdown("*Upload your most recent combination matrix*")
        new_matrix_uploader = create_matrix_uploader("new_matrix", "Choose new combination matrix file")
        new_matrix_result = new_matrix_uploader.render(path_manager.new_matrix_dir)
    
    with col2:
        st.subheader("📋 Old Matrix")
        st.markdown("*Upload the previous combination matrix for comparison*")
        old_matrix_uploader = create_matrix_uploader("old_matrix", "Choose old combination matrix file")
        old_matrix_result = old_matrix_uploader.render(path_manager.old_matrix_dir)
    
    # File validation and comparison
    if new_matrix_uploader.has_files() and old_matrix_uploader.has_files():
        st.markdown("---")
        st.header("✅ Step 2: Validate Matrix Files")
        
        new_files = new_matrix_uploader.get_uploaded_files()
        old_files = old_matrix_uploader.get_uploaded_files()
        
        # Validate file formats
        validation_errors = _validate_matrix_files(new_files + old_files)
        validation_passed = display_file_validation_results(new_files + old_files, validation_errors)
        
        if validation_passed:
            # Preview matrix information
            _display_matrix_preview(new_files[0], old_files[0], compare_matrices_use_case)
            
            st.markdown("---")
            st.header("⚙️ Step 3: Comparison Options")
            
            # Comparison options
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Output Options")
                generate_insights = st.checkbox("Generate Detailed Insights", value=True, 
                                              help="Include trend analysis and recommendations")
                include_recommendations = st.checkbox("Include Recommendations", value=True,
                                                    help="Get actionable recommendations for improvement")
            
            with col2:
                st.subheader("Advanced Options")
                show_processing_details = st.checkbox("Show Processing Details", value=False,
                                                    help="Display detailed processing information")
                custom_output_name = st.text_input("Custom Output Filename (optional)", 
                                                 placeholder="combination_matrix_comparison.xlsx")
            
            # Compare matrices button
            if st.button("🔄 Compare Matrices", type="primary", use_container_width=True):
                _perform_comparison(
                    compare_matrices_use_case,
                    new_files[0],
                    old_files[0],
                    path_manager,
                    generate_insights,
                    include_recommendations,
                    show_processing_details,
                    custom_output_name
                )
    
    # Help section
    st.markdown("---")
    st.header("❓ How to Use This Tool")
    
    with st.expander("📖 Step-by-Step Guide"):
        st.markdown("""
        ### Getting Your Matrix Files
        
        1. **Generate combination matrices** for two different time periods using the Reports page
        2. **Download both matrices** to your computer
        3. **Upload the newer matrix** as "New Matrix"
        4. **Upload the older matrix** as "Old Matrix"
        
        ### Understanding the Results
        
        **Comparison Matrix Columns:**
        - **Current Referral**: Sum of "Referral only" + "OTO and Referral" from new matrix
        - **Last Referral**: Current Referral value from the old matrix
        - **Change in Referrals**: Difference with growth/decline indicators (↗️ ↘️ ➡️)
        - **Last Neither**: "Neither" value from the old matrix
        - **Change in Neither**: Change in "Neither" count (↘️ is good, ↗️ needs attention)
        
        **Growth Indicators:**
        - ↗️ **Positive change** (improvement)
        - ↘️ **Negative change** (decline) 
        - ➡️ **No change** (stable)
        """)
    
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        - **Use consistent time periods** (e.g., monthly or quarterly comparisons)
        - **Ensure member names match** between the two matrices
        - **Compare similar data ranges** for accurate trend analysis
        - **Review the insights** to identify actionable improvement opportunities
        - **Share results** with chapter leadership for strategic planning
        """)
    
    # File management section
    st.markdown("---")
    st.header("🗑️ File Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear New Matrix", help="Remove uploaded new matrix file"):
            new_matrix_uploader.clear_files(path_manager.new_matrix_dir)
            st.rerun()
    
    with col2:
        if st.button("Clear Old Matrix", help="Remove uploaded old matrix file"):
            old_matrix_uploader.clear_files(path_manager.old_matrix_dir)
            st.rerun()
    
    with col3:
        if st.button("Clear All Files", help="Remove all uploaded matrix files"):
            new_matrix_uploader.clear_files(path_manager.new_matrix_dir)
            old_matrix_uploader.clear_files(path_manager.old_matrix_dir)
            st.success("All matrix files cleared!")
            st.rerun()


def _determine_current_step() -> int:
    """Determine the current step in the comparison process."""
    path_manager = get_path_manager()
    
    new_files = path_manager.get_new_matrix_files()
    old_files = path_manager.get_old_matrix_files()
    
    if not new_files or not old_files:
        return 0  # Upload Matrices
    
    return 1  # Validate Files


def _validate_matrix_files(files: list) -> list:
    """Validate matrix files for comparison."""
    errors = []
    
    for file_path in files:
        try:
            if not file_path.exists():
                errors.append(f"File not found: {file_path}")
                continue
            
            if file_path.suffix.lower() not in ['.xls', '.xlsx']:
                errors.append(f"Unsupported file format: {file_path}")
                continue
            
            # Basic file validation
            if file_path.stat().st_size == 0:
                errors.append(f"File is empty: {file_path}")
                continue
                
        except Exception as e:
            errors.append(f"Error validating {file_path}: {str(e)}")
    
    return errors


def _display_matrix_preview(new_file, old_file, compare_use_case):
    """Display a preview of the matrix files."""
    st.subheader("📋 Matrix File Preview")
    
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**New Matrix Info:**")
            new_df, new_headers = compare_use_case.comparison_service.load_matrix_from_excel(new_file)
            st.write(f"• File: {new_file.name}")
            st.write(f"• Size: {new_df.shape[0]} rows × {new_df.shape[1]} columns")
            st.write(f"• Headers found: {'✅' if new_headers else '❌'}")
            
            if new_headers:
                st.write("• Required headers detected:")
                for header in new_headers.keys():
                    st.write(f"  - {header}")
        
        with col2:
            st.write("**Old Matrix Info:**")
            old_df, old_headers = compare_use_case.comparison_service.load_matrix_from_excel(old_file)
            st.write(f"• File: {old_file.name}")
            st.write(f"• Size: {old_df.shape[0]} rows × {old_df.shape[1]} columns")
            st.write(f"• Headers found: {'✅' if old_headers else '❌'}")
            
            if old_headers:
                st.write("• Required headers detected:")
                for header in old_headers.keys():
                    st.write(f"  - {header}")
        
        # Compatibility check
        if new_headers and old_headers:
            st.success("✅ Both matrices have compatible formats for comparison!")
        else:
            st.warning("⚠️ Matrix files may not have the expected format. Comparison may fail.")
            
    except Exception as e:
        st.error(f"Error previewing matrix files: {str(e)}")


def _perform_comparison(compare_use_case: CompareMatricesUseCase,
                       new_file, old_file, path_manager,
                       generate_insights: bool,
                       include_recommendations: bool,
                       show_processing_details: bool,
                       custom_output_name: str):
    """Perform the matrix comparison with progress tracking."""
    
    progress_placeholder = st.empty()
    details_placeholder = st.empty()
    
    try:
        # Step 1: Load and validate matrices
        with progress_placeholder.container():
            st.info("📊 Loading and validating matrix files...")
        
        # Determine output file name
        output_file = None
        if custom_output_name:
            if not custom_output_name.endswith('.xlsx'):
                custom_output_name += '.xlsx'
            output_file = path_manager.get_report_path(custom_output_name)
        
        # Step 2: Perform comparison
        with progress_placeholder.container():
            st.info("🔄 Comparing matrices and calculating changes...")
        
        # Create comparison request
        request = MatrixComparisonRequest(
            new_matrix_file=new_file,
            old_matrix_file=old_file,
            output_file=output_file
        )
        
        # Execute comparison
        response = compare_use_case.execute(request)
        
        # Clear progress indicator
        progress_placeholder.empty()
        
        # Show processing details if requested
        if show_processing_details and response.success:
            with details_placeholder.container():
                st.write("### 🔧 Processing Details")
                
                if response.insights:
                    insights = response.insights
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Members Analyzed", insights.get('total_members', 0))
                    with col2:
                        st.metric("Processing Time", f"{response.execution_time_seconds:.2f}s")
                    with col3:
                        st.metric("Data Quality", "✅ Good" if not response.warnings else "⚠️ Issues")
        
        # Display results
        display_matrix_comparison_results(response)
        
        # Generate detailed insights report if requested
        if response.success and generate_insights and response.insights:
            _display_detailed_insights(response, include_recommendations, compare_use_case)
        
        # Clean up uploaded files if successful
        if response.success:
            path_manager.cleanup_directory(path_manager.new_matrix_dir)
            path_manager.cleanup_directory(path_manager.old_matrix_dir)
            st.info("🗑️ Uploaded matrix files have been cleaned up automatically.")
            
    except Exception as e:
        progress_placeholder.empty()
        st.error(f"❌ Comparison failed: {str(e)}")


def _display_detailed_insights(response, include_recommendations: bool, compare_use_case):
    """Display detailed insights from the comparison."""
    st.markdown("---")
    st.header("🔍 Detailed Analysis")
    
    try:
        # Generate insights report
        insights_report = compare_use_case.generate_comparison_insights_report(response)
        
        if 'error' in insights_report:
            st.error(f"Could not generate detailed insights: {insights_report['error']}")
            return
        
        # Executive Summary
        if 'executive_summary' in insights_report:
            summary = insights_report['executive_summary']
            st.subheader("📋 Executive Summary")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Members Analyzed", summary.get('total_members_analyzed', 0))
                st.metric("Overall Performance", summary.get('overall_performance', 'Unknown'))
            
            with col2:
                if 'key_metrics' in summary:
                    metrics = summary['key_metrics']
                    for metric, value in metrics.items():
                        st.metric(metric.replace('_', ' ').title(), value)
        
        # Member Performance Analysis
        if 'member_performance' in insights_report:
            performance = insights_report['member_performance']
            st.subheader("👥 Member Performance Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🌟 Top Performers**")
                top_performers = performance.get('top_performers', [])
                if top_performers:
                    for performer in top_performers:
                        st.success(f"**{performer['member']}**: +{performer['improvement']} ({performer['category']})")
                else:
                    st.write("No significant improvements detected.")
            
            with col2:
                st.write("**⚠️ Needs Attention**")
                needs_attention = performance.get('needs_attention', [])
                if needs_attention:
                    for member in needs_attention:
                        st.error(f"**{member['member']}**: -{member['decline']} ({member['category']})")
                else:
                    st.write("No significant declines detected.")
        
        # Trend Analysis
        if 'trend_analysis' in insights_report:
            trends = insights_report['trend_analysis']
            st.subheader("📈 Trend Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Overall Direction", trends.get('overall_direction', 'Unknown'))
                st.metric("Engagement Trend", trends.get('engagement_trend', 'Unknown'))
            
            with col2:
                if 'metrics' in trends:
                    trend_metrics = trends['metrics']
                    for metric, value in trend_metrics.items():
                        if isinstance(value, (int, float)):
                            st.metric(metric.replace('_', ' ').title(), f"{value:.2f}")
                        else:
                            st.metric(metric.replace('_', ' ').title(), value)
        
        # Recommendations
        if include_recommendations and 'recommendations' in insights_report:
            recommendations = insights_report['recommendations']
            st.subheader("💡 Recommendations")
            
            if recommendations:
                for i, recommendation in enumerate(recommendations, 1):
                    st.info(f"**{i}.** {recommendation}")
            else:
                st.write("No specific recommendations generated.")
                
    except Exception as e:
        st.error(f"Error displaying detailed insights: {str(e)}")