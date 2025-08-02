"""Path management utilities for the application."""

from pathlib import Path
from typing import List

from .settings import get_settings


class PathManager:
    """Manages file and directory paths for the application."""
    
    def __init__(self):
        self.settings = get_settings()
    
    @property
    def excel_files_dir(self) -> Path:
        """Get the Excel files directory path."""
        return Path(self.settings.directories.excel_files)
    
    @property
    def member_names_dir(self) -> Path:
        """Get the member names directory path."""
        return Path(self.settings.directories.member_names)
    
    @property
    def reports_dir(self) -> Path:
        """Get the reports directory path."""
        return Path(self.settings.directories.reports)
    
    @property
    def new_matrix_dir(self) -> Path:
        """Get the new matrix directory path."""
        return Path(self.settings.directories.new_matrix)
    
    @property
    def old_matrix_dir(self) -> Path:
        """Get the old matrix directory path."""
        return Path(self.settings.directories.old_matrix)
    
    def get_excel_files(self) -> List[Path]:
        """Get all Excel files from the Excel files directory."""
        excel_files = []
        if self.excel_files_dir.exists():
            for ext in self.settings.excel.supported_extensions:
                excel_files.extend(self.excel_files_dir.glob(f"*{ext}"))
        return sorted(excel_files)
    
    def get_member_files(self) -> List[Path]:
        """Get all member files from the member names directory."""
        member_files = []
        if self.member_names_dir.exists():
            for ext in self.settings.excel.supported_extensions:
                member_files.extend(self.member_names_dir.glob(f"*{ext}"))
        return sorted(member_files)
    
    def get_report_path(self, filename: str) -> Path:
        """Get the full path for a report file."""
        return self.reports_dir / filename
    
    def get_new_matrix_files(self) -> List[Path]:
        """Get all files from the new matrix directory."""
        matrix_files = []
        if self.new_matrix_dir.exists():
            for ext in self.settings.excel.supported_extensions:
                matrix_files.extend(self.new_matrix_dir.glob(f"*{ext}"))
        return sorted(matrix_files)
    
    def get_old_matrix_files(self) -> List[Path]:
        """Get all files from the old matrix directory."""
        matrix_files = []
        if self.old_matrix_dir.exists():
            for ext in self.settings.excel.supported_extensions:
                matrix_files.extend(self.old_matrix_dir.glob(f"*{ext}"))
        return sorted(matrix_files)
    
    def cleanup_directory(self, directory: Path) -> None:
        """Remove all files from a directory."""
        if directory.exists():
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_path.unlink()
    
    def cleanup_all_upload_directories(self) -> None:
        """Clean up all upload directories."""
        for directory in [
            self.excel_files_dir,
            self.member_names_dir,
            self.new_matrix_dir,
            self.old_matrix_dir
        ]:
            self.cleanup_directory(directory)


# Global path manager instance
path_manager = PathManager()


def get_path_manager() -> PathManager:
    """Get the global path manager instance."""
    return path_manager