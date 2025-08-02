"""Utility functions for Streamlit interface."""

import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from io import BytesIO

from src.domain.models.analysis_result import AnalysisReport
from src.application.dto.analysis_response import ReportGenerationResponse, MatrixComparisonResponse


def display_error_messages(errors: List[str], title: str = "Errors") -> None:
    """Display error messages in Streamlit."""
    if errors:
        st.error(f"**{title}:**")
        for error in errors:
            st.error(f"• {error}")


def display_warning_messages(warnings: List[str], title: str = "Warnings") -> None:
    """Display warning messages in Streamlit."""
    if warnings:
        st.warning(f"**{title}:**")
        for warning in warnings:
            st.warning(f"• {warning}")


def display_success_messages(messages: List[str], title: str = "Success") -> None:
    """Display success messages in Streamlit."""
    if messages:
        st.success(f"**{title}:**")
        for message in messages:
            st.success(f"• {message}")


def create_download_button(file_path: Path, label: str = None, 
                         mime_type: str = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") -> None:
    """Create a download button for a file."""
    if not file_path.exists():
        st.error(f"File not found: {file_path}")
        return
    
    label = label or f"Download {file_path.name}"
    
    try:
        with open(file_path, "rb") as f:
            st.download_button(
                label=label,
                data=f.read(),
                file_name=file_path.name,
                mime=mime_type
            )
    except Exception as e:
        st.error(f"Error creating download button: {str(e)}")


def display_report_generation_results(response: ReportGenerationResponse) -> None:
    """Display the results of report generation."""
    if response.success:
        st.success("✅ Reports generated successfully!")
        
        # Display metadata
        if response.metadata:
            st.info("**Report Summary:**")
            metadata = response.metadata
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Members", metadata.get('total_members', 0))
            with col2:
                st.metric("Total Referrals", metadata.get('total_referrals', 0))
            with col3:
                st.metric("Total One-to-Ones", metadata.get('total_one_to_ones', 0))
        
        # Display generated files
        if response.generated_files:
            st.write("**📊 Download Your Reports:**")
            for file_path in response.generated_files:
                create_download_button(file_path, f"📄 Download {file_path.name}")
        
        # Display execution time
        if response.execution_time_seconds:
            st.info(f"⏱️ Processing completed in {response.execution_time_seconds:.2f} seconds")
    
    else:
        st.error("❌ Report generation failed!")
    
    # Display warnings and errors
    display_warning_messages(response.warnings)
    display_error_messages(response.errors)


def display_matrix_comparison_results(response: MatrixComparisonResponse) -> None:
    """Display the results of matrix comparison."""
    if response.success:
        st.success("✅ Matrix comparison completed successfully!")
        
        # Download button for comparison file
        if response.comparison_file:
            create_download_button(
                response.comparison_file, 
                "📊 Download Comparison Matrix"
            )
        
        # Display insights
        if response.insights:
            display_comparison_insights(response.insights)
        
        # Display execution time
        if response.execution_time_seconds:
            st.info(f"⏱️ Comparison completed in {response.execution_time_seconds:.2f} seconds")
    
    else:
        st.error("❌ Matrix comparison failed!")
    
    # Display warnings and errors
    display_warning_messages(response.warnings)
    display_error_messages(response.errors)


def display_comparison_insights(insights: Dict[str, Any]) -> None:
    """Display matrix comparison insights."""
    st.write("## 📈 Comparison Insights")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Members", insights.get('total_members', 0))
    with col2:
        st.metric("Improved", insights.get('improved_members', 0))
    with col3:
        st.metric("Declined", insights.get('declined_members', 0))
    with col4:
        st.metric("Unchanged", insights.get('unchanged_members', 0))
    
    # Top performers and declines
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🚀 Top Improvements")
        improvements = insights.get('biggest_improvements', [])[:5]
        if improvements:
            for member, change in improvements:
                if change > 0:
                    st.success(f"**{member}**: +{change} ↗️")
        else:
            st.write("No significant improvements detected.")
    
    with col2:
        st.write("### ⚠️ Needs Attention")
        declines = insights.get('biggest_declines', [])[-5:]  # Last 5 (biggest declines)
        if declines:
            for member, change in declines:
                if change < 0:
                    st.error(f"**{member}**: {change} ↘️")
        else:
            st.write("No significant declines detected.")
    
    # Summary statistics
    summary_stats = insights.get('summary_stats', {})
    if summary_stats:
        st.write("### 📊 Summary Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Change", f"{summary_stats.get('average_change', 0):.1f}")
            st.metric("Improvement Rate", f"{summary_stats.get('improvement_rate', 0):.1%}")
        
        with col2:
            st.metric("Total Change", summary_stats.get('total_change', 0))
            st.metric("Decline Rate", f"{summary_stats.get('decline_rate', 0):.1%}")


def create_progress_tracker(steps: List[str], current_step: int = 0) -> None:
    """Create a progress tracker for multi-step processes."""
    st.write("### Progress")
    
    progress_html = "<div style='display: flex; align-items: center; margin: 10px 0;'>"
    
    for i, step in enumerate(steps):
        if i < current_step:
            # Completed step
            progress_html += f"""
            <div style='display: flex; align-items: center; margin-right: 20px;'>
                <div style='background-color: #00ff00; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                    ✓
                </div>
                <span style='color: #00ff00;'>{step}</span>
            </div>
            """
        elif i == current_step:
            # Current step
            progress_html += f"""
            <div style='display: flex; align-items: center; margin-right: 20px;'>
                <div style='background-color: #0066cc; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                    {i + 1}
                </div>
                <span style='color: #0066cc; font-weight: bold;'>{step}</span>
            </div>
            """
        else:
            # Pending step
            progress_html += f"""
            <div style='display: flex; align-items: center; margin-right: 20px;'>
                <div style='background-color: #cccccc; color: #666666; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                    {i + 1}
                </div>
                <span style='color: #666666;'>{step}</span>
            </div>
            """
        
        # Add arrow between steps (except for the last step)
        if i < len(steps) - 1:
            progress_html += "<span style='margin-right: 20px; color: #cccccc;'>→</span>"
    
    progress_html += "</div>"
    st.markdown(progress_html, unsafe_allow_html=True)


def display_file_validation_results(files: List[Path], errors: List[str]) -> bool:
    """
    Display file validation results and return whether validation passed.
    
    Args:
        files: List of files to validate
        errors: List of validation errors
        
    Returns:
        True if validation passed, False otherwise
    """
    if errors:
        st.error("**File Validation Errors:**")
        for error in errors:
            st.error(f"• {error}")
        return False
    
    if files:
        st.success(f"✅ All {len(files)} files validated successfully!")
        with st.expander("View validated files"):
            for file_path in files:
                st.write(f"📄 {file_path.name}")
        return True
    
    st.warning("No files to validate.")
    return False


def create_data_quality_display(quality_report: Dict[str, Any]) -> None:
    """Display data quality report."""
    if not quality_report:
        return
    
    st.write("### 📊 Data Quality Report")
    
    # Overall quality score
    overall_score = quality_report.get('overall_quality_score', 0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Color code the quality score
        if overall_score >= 90:
            color = "green"
        elif overall_score >= 70:
            color = "orange"
        else:
            color = "red"
        
        st.markdown(
            f"<h3 style='text-align: center; color: {color};'>Quality Score: {overall_score:.1f}%</h3>",
            unsafe_allow_html=True
        )
    
    # Detailed breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Members**")
        members = quality_report.get('members', {})
        st.metric("Total", members.get('total', 0))
        st.metric("Valid", members.get('valid', 0))
        if members.get('duplicates', 0) > 0:
            st.error(f"Duplicates: {members['duplicates']}")
        if members.get('incomplete_names', 0) > 0:
            st.warning(f"Incomplete: {members['incomplete_names']}")
    
    with col2:
        st.write("**Referrals**")
        referrals = quality_report.get('referrals', {})
        st.metric("Total", referrals.get('total', 0))
        st.metric("Valid", referrals.get('valid', 0))
        if referrals.get('self_referrals', 0) > 0:
            st.error(f"Self-referrals: {referrals['self_referrals']}")
    
    with col3:
        st.write("**One-to-Ones**")
        one_to_ones = quality_report.get('one_to_ones', {})
        st.metric("Total", one_to_ones.get('total', 0))
        st.metric("Valid", one_to_ones.get('valid', 0))
        if one_to_ones.get('self_meetings', 0) > 0:
            st.error(f"Self-meetings: {one_to_ones['self_meetings']}")


def create_analysis_overview(report: AnalysisReport) -> None:
    """Create an overview display for analysis report."""
    st.write("### 📈 Analysis Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Members", len(report.all_members))
    
    with col2:
        total_referrals = report.metadata.get('total_referrals', 0)
        st.metric("Total Referrals", total_referrals)
    
    with col3:
        total_otos = report.metadata.get('total_one_to_ones', 0)
        st.metric("Total One-to-Ones", total_otos)
    
    with col4:
        # Calculate active members (those with any activity)
        active_members = len([
            m for m in report.all_members
            if (report.referral_matrix.member_statistics.get(m, {}).total_referrals_given > 0 or
                report.one_to_one_matrix.member_statistics.get(m, {}).total_one_to_ones > 0)
        ])
        st.metric("Active Members", active_members)


def safe_streamlit_operation(operation, error_message: str = "An error occurred"):
    """
    Safely execute a Streamlit operation with error handling.
    
    Args:
        operation: Function to execute
        error_message: Message to display on error
        
    Returns:
        Result of operation or None if error occurred
    """
    try:
        return operation()
    except Exception as e:
        st.error(f"{error_message}: {str(e)}")
        return None