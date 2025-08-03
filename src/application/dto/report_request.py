"""Data Transfer Objects for report requests and responses."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class ReportGenerationRequest:
    """Request object for generating reports."""
    
    excel_files: List[Path]
    member_files: List[Path]
    output_directory: Optional[Path] = None
    include_referral_matrix: bool = True
    include_oto_matrix: bool = True
    include_combination_matrix: bool = True
    include_comprehensive_member_report: bool = False
    
    def validate(self) -> bool:
        """Validate the request."""
        if not self.excel_files:
            raise ValueError("At least one Excel file is required")
        if not self.member_files:
            raise ValueError("At least one member file is required")
        
        # Check if files exist
        for file_path in self.excel_files + self.member_files:
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")
        
        return True


@dataclass
class MatrixComparisonRequest:
    """Request object for matrix comparison."""
    
    new_matrix_file: Path
    old_matrix_file: Path
    output_file: Optional[Path] = None
    
    def validate(self) -> bool:
        """Validate the request."""
        if not self.new_matrix_file.exists():
            raise ValueError(f"New matrix file not found: {self.new_matrix_file}")
        if not self.old_matrix_file.exists():
            raise ValueError(f"Old matrix file not found: {self.old_matrix_file}")
        
        return True


@dataclass
class ProcessPalmsDataRequest:
    """Request object for processing PALMS data."""
    
    data_directory: Path
    member_directory: Path
    convert_xls_files: bool = True
    validate_data: bool = True
    
    def validate(self) -> bool:
        """Validate the request."""
        if not self.data_directory.exists():
            raise ValueError(f"Data directory not found: {self.data_directory}")
        if not self.member_directory.exists():
            raise ValueError(f"Member directory not found: {self.member_directory}")
        
        return True