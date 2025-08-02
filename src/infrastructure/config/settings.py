"""Application configuration management."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class DirectoryConfig:
    """Configuration for application directories."""
    
    excel_files: str = "Excel Files"
    member_names: str = "Member Names"
    reports: str = "Reports"
    new_matrix: str = "New Matrix"
    old_matrix: str = "Old Matrix"
    
    def ensure_directories_exist(self) -> None:
        """Create directories if they don't exist."""
        for directory in [
            self.excel_files,
            self.member_names,
            self.reports,
            self.new_matrix,
            self.old_matrix
        ]:
            Path(directory).mkdir(exist_ok=True)


@dataclass
class ExcelConfig:
    """Configuration for Excel file processing."""
    
    supported_extensions: List[str] = None
    max_file_size_mb: int = 50
    encoding: str = "utf-8"
    
    def __post_init__(self):
        if self.supported_extensions is None:
            self.supported_extensions = [".xls", ".xlsx"]


@dataclass
class MatrixConfig:
    """Configuration for matrix generation and styling."""
    
    # Cell styling
    zero_highlight_color: str = "FFFF00"  # Yellow
    border_style: str = "thin"
    text_alignment: str = "center"
    header_text_rotation: int = 90
    header_bold: bool = True
    
    # Column width settings
    name_column_width: int = 35
    data_column_width_buffer: int = 2
    max_column_width: int = 15


@dataclass
class ApplicationSettings:
    """Main application settings."""
    
    # Application metadata
    app_name: str = "BNI Palms Analysis"
    version: str = "2.0.0"
    description: str = "BNI PALMS data analysis and reporting tool"
    
    # Configuration objects
    directories: DirectoryConfig = None
    excel: ExcelConfig = None
    matrix: MatrixConfig = None
    
    # Debug settings
    debug_mode: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Initialize configuration objects with defaults."""
        if self.directories is None:
            self.directories = DirectoryConfig()
        if self.excel is None:
            self.excel = ExcelConfig()
        if self.matrix is None:
            self.matrix = MatrixConfig()
        
        # Override with environment variables if present
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        self.debug_mode = os.getenv("BNI_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("BNI_LOG_LEVEL", self.log_level)
        
        # Directory overrides
        self.directories.excel_files = os.getenv("BNI_EXCEL_DIR", self.directories.excel_files)
        self.directories.member_names = os.getenv("BNI_MEMBERS_DIR", self.directories.member_names)
        self.directories.reports = os.getenv("BNI_REPORTS_DIR", self.directories.reports)
    
    def initialize(self) -> None:
        """Initialize the application with this configuration."""
        self.directories.ensure_directories_exist()


# Global settings instance
settings = ApplicationSettings()


def get_settings() -> ApplicationSettings:
    """Get the global application settings."""
    return settings


def configure_app(custom_settings: Optional[ApplicationSettings] = None) -> None:
    """Configure the application with custom settings."""
    global settings
    if custom_settings:
        settings = custom_settings
    settings.initialize()