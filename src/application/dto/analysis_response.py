"""Data Transfer Objects for analysis responses."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.domain.models.analysis_result import AnalysisReport


@dataclass
class ReportGenerationResponse:
    """Response object for report generation."""
    
    success: bool
    report: Optional[AnalysisReport] = None
    generated_files: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_seconds: Optional[float] = None
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def add_generated_file(self, file_path: Path) -> None:
        """Add a generated file to the response."""
        self.generated_files.append(file_path)


@dataclass
class MatrixComparisonResponse:
    """Response object for matrix comparison."""
    
    success: bool
    comparison_file: Optional[Path] = None
    insights: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_seconds: Optional[float] = None
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


@dataclass
class ProcessPalmsDataResponse:
    """Response object for PALMS data processing."""
    
    success: bool
    members_count: int = 0
    referrals_count: int = 0
    one_to_ones_count: int = 0
    tyfcbs_count: int = 0
    processed_files: List[Path] = field(default_factory=list)
    converted_files: List[Path] = field(default_factory=list)
    data_quality_report: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_seconds: Optional[float] = None
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def add_processed_file(self, file_path: Path) -> None:
        """Add a processed file to the response."""
        self.processed_files.append(file_path)
    
    def add_converted_file(self, file_path: Path) -> None:
        """Add a converted file to the response."""
        self.converted_files.append(file_path)


@dataclass
class AnalysisInsightsResponse:
    """Response object for analysis insights."""
    
    success: bool
    chapter_overview: Optional[Dict[str, Any]] = None
    member_performance: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation."""
        self.recommendations.append(recommendation)