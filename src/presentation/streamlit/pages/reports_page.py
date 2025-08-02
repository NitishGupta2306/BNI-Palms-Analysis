"""Reports page for generating BNI analysis reports."""

import streamlit as st
from typing import Optional

from src.application.use_cases.generate_reports import GenerateReportsUseCase
from src.application.use_cases.process_palms_data import ProcessPalmsDataUseCase
from src.application.dto.report_request import ReportGenerationRequest, ProcessPalmsDataRequest
from src.presentation.streamlit.components.file_uploader import create_palms_uploader, create_members_uploader
from src.presentation.streamlit.utils.streamlit_helpers import (
    display_report_generation_results, create_progress_tracker, 
    display_file_validation_results, create_data_quality_display,
    safe_streamlit_operation
)
from src.infrastructure.config.paths import get_path_manager
from src.infrastructure.config.settings import configure_app


def render_reports_page():
    """Render the main reports generation page."""
    # Initialize application
    configure_app()
    
    # Initialize use cases
    generate_reports_use_case = GenerateReportsUseCase()
    process_data_use_case = ProcessPalmsDataUseCase()
    path_manager = get_path_manager()
    
    st.title("📊 BNI PALMS Analysis")
    
    # Instructions
    st.markdown("""
    ### 📋 Instructions
    
    1. **Upload Excel slip-audit-reports** (multiple files supported)
    2. **Upload member names file** (single Excel file with first and last names)
    3. **Click "Generate Reports"** to create your analysis matrices
    4. **Download the generated reports** when processing is complete
    
    **Note:** Files must be in .xls or .xlsx format
    """)
    
    # Progress tracker
    steps = ["Upload Files", "Validate Data", "Process Data", "Generate Reports", "Download Results"]
    current_step = _determine_current_step()
    create_progress_tracker(steps, current_step)
    
    # File upload section
    st.markdown("---")
    st.header("📤 Step 1: Upload Your Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("PALMS Data Files")
        palms_uploader = create_palms_uploader("palms_reports")
        palms_result = palms_uploader.render(path_manager.excel_files_dir)
    
    with col2:
        st.subheader("Member Names File")
        members_uploader = create_members_uploader("members_list")
        members_result = members_result = members_uploader.render(path_manager.member_names_dir)
    
    # File validation
    if palms_uploader.has_files() and members_uploader.has_files():
        st.markdown("---")
        st.header("✅ Step 2: Validate Files")
        
        # Validate files
        all_files = palms_uploader.get_uploaded_files() + members_uploader.get_uploaded_files()
        validation_errors = safe_streamlit_operation(
            lambda: generate_reports_use_case.validate_input_files(
                palms_uploader.get_uploaded_files(),
                members_uploader.get_uploaded_files()
            ),
            "File validation failed"
        )
        
        validation_passed = display_file_validation_results(all_files, validation_errors or [])
        
        # Report generation section
        if validation_passed:
            st.markdown("---")
            st.header("⚙️ Step 3: Generate Reports")
            
            # Report options
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Report Options")
                include_referral = st.checkbox("Generate Referral Matrix", value=True)
                include_oto = st.checkbox("Generate One-to-One Matrix", value=True)
                include_combination = st.checkbox("Generate Combination Matrix", value=True)
            
            with col2:
                st.subheader("Advanced Options")
                validate_data_quality = st.checkbox("Validate Data Quality", value=True)
                show_processing_details = st.checkbox("Show Processing Details", value=False)
            
            # Generate reports button
            if st.button("🚀 Generate Reports", type="primary", use_container_width=True):
                _generate_reports(
                    generate_reports_use_case,
                    process_data_use_case,
                    path_manager,
                    include_referral,
                    include_oto,
                    include_combination,
                    validate_data_quality,
                    show_processing_details
                )
    
    # Clear files section
    st.markdown("---")
    st.header("🗑️ File Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear PALMS Files", help="Remove all uploaded PALMS data files"):
            palms_uploader.clear_files(path_manager.excel_files_dir)
            st.rerun()
    
    with col2:
        if st.button("Clear Member Files", help="Remove all uploaded member files"):
            members_uploader.clear_files(path_manager.member_names_dir)
            st.rerun()
    
    with col3:
        if st.button("Clear All Files", help="Remove all uploaded files and generated reports"):
            _clear_all_files(path_manager, palms_uploader, members_uploader)
            st.rerun()


def _determine_current_step() -> int:
    """Determine the current step in the process."""
    path_manager = get_path_manager()
    
    # Check if files are uploaded
    palms_files = path_manager.get_excel_files()
    member_files = path_manager.get_member_files()
    
    if not palms_files or not member_files:
        return 0  # Upload Files
    
    # Files uploaded - assume at validation step
    return 1


def _generate_reports(generate_reports_use_case: GenerateReportsUseCase,
                     process_data_use_case: ProcessPalmsDataUseCase,
                     path_manager,
                     include_referral: bool,
                     include_oto: bool,  
                     include_combination: bool,
                     validate_data_quality: bool,
                     show_processing_details: bool):
    """Generate reports with progress tracking."""
    
    progress_placeholder = st.empty()
    details_placeholder = st.empty()
    
    try:
        # Step 1: Process data
        with progress_placeholder.container():
            st.info("🔄 Processing PALMS data...")
        
        if validate_data_quality:
            # Process and validate data first
            process_request = ProcessPalmsDataRequest(
                data_directory=path_manager.excel_files_dir,
                member_directory=path_manager.member_names_dir,
                convert_xls_files=True,
                validate_data=True
            )
            
            process_response = process_data_use_case.execute(process_request)
            
            if show_processing_details:
                with details_placeholder.container():
                    st.write("### 📊 Data Processing Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Members Loaded", process_response.members_count)
                    with col2:
                        st.metric("Referrals Found", process_response.referrals_count)
                    with col3:
                        st.metric("One-to-Ones Found", process_response.one_to_ones_count)
                    
                    if process_response.data_quality_report:
                        create_data_quality_display(process_response.data_quality_report)
                    
                    if process_response.warnings:
                        st.warning("⚠️ **Data Quality Warnings:**")
                        for warning in process_response.warnings:
                            st.warning(f"• {warning}")
                    
                    if process_response.errors:
                        st.error("❌ **Processing Errors:**")
                        for error in process_response.errors:
                            st.error(f"• {error}")
                        return
        
        # Step 2: Generate reports
        with progress_placeholder.container():
            st.info("📊 Generating analysis reports...")
        
        # Get file lists
        excel_files = path_manager.get_excel_files()
        member_files = path_manager.get_member_files()
        
        # Create report generation request
        request = ReportGenerationRequest(
            excel_files=excel_files,
            member_files=member_files,
            output_directory=path_manager.reports_dir,
            include_referral_matrix=include_referral,
            include_oto_matrix=include_oto,
            include_combination_matrix=include_combination
        )
        
        # Generate reports
        response = generate_reports_use_case.execute(request)
        
        # Clear progress and show results
        progress_placeholder.empty()
        
        # Display results
        display_report_generation_results(response)
        
        # Clean up uploaded files if successful
        if response.success:
            _cleanup_uploaded_files(path_manager)
            st.success("✨ Upload files have been cleaned up automatically.")
    
    except Exception as e:
        progress_placeholder.empty()
        st.error(f"❌ An unexpected error occurred: {str(e)}")


def _clear_all_files(path_manager, palms_uploader, members_uploader):
    """Clear all files and reset the application state."""
    try:
        # Clear uploaded files
        palms_uploader.clear_files(path_manager.excel_files_dir)
        members_uploader.clear_files(path_manager.member_names_dir)
        
        # Clear generated reports
        path_manager.cleanup_directory(path_manager.reports_dir)
        
        st.success("🗑️ All files cleared successfully!")
        
    except Exception as e:
        st.error(f"Error clearing files: {str(e)}")


def _cleanup_uploaded_files(path_manager):
    """Clean up uploaded files after successful report generation."""
    try:
        path_manager.cleanup_directory(path_manager.excel_files_dir)
        path_manager.cleanup_directory(path_manager.member_names_dir)
    except Exception as e:
        st.warning(f"Could not clean up uploaded files: {str(e)}")