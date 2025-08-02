"""Reusable file uploader component for Streamlit."""

import streamlit as st
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any

from src.shared.constants.app_constants import StreamlitConfig


class FileUploaderComponent:
    """Reusable file uploader component with validation and processing."""
    
    def __init__(self, 
                 component_id: str,
                 title: str,
                 help_text: Optional[str] = None,
                 accept_multiple: bool = True,
                 max_size_mb: int = StreamlitConfig.MAX_FILE_SIZE_MB,
                 allowed_types: List[str] = None):
        """
        Initialize the file uploader component.
        
        Args:
            component_id: Unique identifier for this component
            title: Display title for the uploader
            help_text: Optional help text
            accept_multiple: Whether to accept multiple files
            max_size_mb: Maximum file size in MB
            allowed_types: List of allowed file extensions
        """
        self.component_id = component_id
        self.title = title
        self.help_text = help_text
        self.accept_multiple = accept_multiple
        self.max_size_mb = max_size_mb
        self.allowed_types = allowed_types or StreamlitConfig.ALLOWED_TYPES
        
        # Initialize session state keys
        self._init_session_state()
    
    def _init_session_state(self) -> None:
        """Initialize session state variables for this component."""
        uploader_key = f"uploader_{self.component_id}"
        files_key = f"files_{self.component_id}"
        errors_key = f"errors_{self.component_id}"
        
        if uploader_key not in st.session_state:
            st.session_state[uploader_key] = 0
        
        if files_key not in st.session_state:
            st.session_state[files_key] = []
        
        if errors_key not in st.session_state:
            st.session_state[errors_key] = []
    
    def render(self, save_directory: Path) -> Dict[str, Any]:
        """
        Render the file uploader component.
        
        Args:
            save_directory: Directory where uploaded files should be saved
            
        Returns:
            Dictionary with upload results
        """
        result = {
            'files': [],
            'errors': [],
            'success': False
        }
        
        # Create save directory if it doesn't exist
        save_directory.mkdir(parents=True, exist_ok=True)
        
        # Display file uploader
        uploader_key = f"uploader_{self.component_id}_{st.session_state[f'uploader_{self.component_id}']}"
        
        uploaded_files = st.file_uploader(
            self.title,
            type=self.allowed_types,
            accept_multiple_files=self.accept_multiple,
            help=self.help_text,
            key=uploader_key
        )
        
        # Process uploaded files
        if uploaded_files:
            if not self.accept_multiple:
                uploaded_files = [uploaded_files]
            
            for uploaded_file in uploaded_files:
                try:
                    # Validate file
                    validation_result = self._validate_file(uploaded_file)
                    if not validation_result['valid']:
                        result['errors'].extend(validation_result['errors'])
                        continue
                    
                    # Save file
                    file_path = save_directory / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    result['files'].append(file_path)
                    
                except Exception as e:
                    error_msg = f"Error processing {uploaded_file.name}: {str(e)}"
                    result['errors'].append(error_msg)
        
        # Update session state
        files_key = f"files_{self.component_id}"
        errors_key = f"errors_{self.component_id}"
        
        st.session_state[files_key] = result['files']
        st.session_state[errors_key] = result['errors']
        
        result['success'] = len(result['files']) > 0 and len(result['errors']) == 0
        
        # Display results
        self._display_results(result)
        
        return result
    
    def _validate_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Validate an uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': True,
            'errors': []
        }
        
        try:
            # Check file size
            file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
            if file_size_mb > self.max_size_mb:
                result['valid'] = False
                result['errors'].append(
                    f"File {uploaded_file.name} is too large ({file_size_mb:.1f}MB). "
                    f"Maximum size is {self.max_size_mb}MB."
                )
            
            # Check file extension
            file_extension = Path(uploaded_file.name).suffix.lower()[1:]  # Remove the dot
            if file_extension not in [ext.lower() for ext in self.allowed_types]:
                result['valid'] = False
                result['errors'].append(
                    f"File {uploaded_file.name} has unsupported format. "
                    f"Allowed formats: {', '.join(self.allowed_types)}"
                )
            
            # Check for empty file
            if len(uploaded_file.getbuffer()) == 0:
                result['valid'] = False
                result['errors'].append(f"File {uploaded_file.name} is empty.")
                
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error validating {uploaded_file.name}: {str(e)}")
        
        return result
    
    def _display_results(self, result: Dict[str, Any]) -> None:
        """Display upload results to the user."""
        if result['files']:
            st.success(f"✅ Successfully uploaded {len(result['files'])} file(s)")
            with st.expander("View uploaded files"):
                for file_path in result['files']:
                    st.write(f"📄 {file_path.name}")
        
        if result['errors']:
            st.error(f"❌ {len(result['errors'])} error(s) occurred:")
            for error in result['errors']:
                st.error(error)
    
    def clear_files(self, save_directory: Path) -> None:
        """
        Clear uploaded files and reset the component.
        
        Args:
            save_directory: Directory containing files to clear
        """
        try:
            # Clear files from directory
            if save_directory.exists():
                for file_path in save_directory.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
            
            # Reset session state
            files_key = f"files_{self.component_id}"
            errors_key = f"errors_{self.component_id}"
            uploader_key = f"uploader_{self.component_id}"
            
            st.session_state[files_key] = []
            st.session_state[errors_key] = []
            st.session_state[uploader_key] += 1  # Force re-render of uploader
            
            st.success("Files cleared successfully!")
            
        except Exception as e:
            st.error(f"Error clearing files: {str(e)}")
    
    def get_uploaded_files(self) -> List[Path]:
        """Get list of currently uploaded files."""
        files_key = f"files_{self.component_id}"
        return st.session_state.get(files_key, [])
    
    def get_errors(self) -> List[str]:
        """Get list of current errors."""
        errors_key = f"errors_{self.component_id}"
        return st.session_state.get(errors_key, [])
    
    def has_files(self) -> bool:
        """Check if any files have been uploaded."""
        return len(self.get_uploaded_files()) > 0
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.get_errors()) > 0


def create_palms_uploader(component_id: str = "palms_data") -> FileUploaderComponent:
    """Create a file uploader specifically for PALMS data files."""
    return FileUploaderComponent(
        component_id=component_id,
        title="Choose Excel slip-audit-reports",
        help_text="Upload your BNI PALMS slip audit reports in .xls or .xlsx format",
        accept_multiple=True,
        max_size_mb=50,
        allowed_types=["xls", "xlsx"]
    )


def create_members_uploader(component_id: str = "members_data") -> FileUploaderComponent:
    """Create a file uploader specifically for member data files."""
    return FileUploaderComponent(
        component_id=component_id,
        title="Choose Excel with member names",
        help_text="Upload your member list in .xls or .xlsx format",
        accept_multiple=False,
        max_size_mb=10,
        allowed_types=["xls", "xlsx"]
    )


def create_matrix_uploader(component_id: str, title: str) -> FileUploaderComponent:
    """Create a file uploader specifically for matrix files."""
    return FileUploaderComponent(
        component_id=component_id,
        title=title,
        help_text="Upload matrix file in .xls or .xlsx format",
        accept_multiple=False,
        max_size_mb=20,
        allowed_types=["xls", "xlsx"]
    )