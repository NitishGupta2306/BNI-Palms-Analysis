"""Use case for generating BNI analysis reports."""

import time
from pathlib import Path
from typing import List

from src.application.dto.report_request import ReportGenerationRequest
from src.application.dto.analysis_response import ReportGenerationResponse
from src.domain.services.analysis_service import AnalysisService
from src.domain.exceptions.domain_exceptions import DataProcessingError, ExportError
from src.infrastructure.config.paths import get_path_manager
from src.shared.constants.app_constants import FileNames
from src.shared.utils.export_utils import ExportService


class GenerateReportsUseCase:
    """Use case for generating all BNI analysis reports."""
    
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.export_service = ExportService()
        self.path_manager = get_path_manager()
    
    def execute(self, request: ReportGenerationRequest) -> ReportGenerationResponse:
        """
        Execute the report generation use case.
        
        Args:
            request: Report generation request
            
        Returns:
            Report generation response
        """
        start_time = time.time()
        response = ReportGenerationResponse(success=True)
        
        try:
            # Validate request
            request.validate()
            
            # Generate complete analysis
            report = self.analysis_service.generate_complete_analysis()
            response.report = report
            
            # Set output directory
            output_dir = request.output_directory or self.path_manager.reports_dir
            
            # Generate requested reports
            if request.include_referral_matrix:
                try:
                    file_path = self._export_referral_matrix(report, output_dir)
                    response.add_generated_file(file_path)
                except Exception as e:
                    response.add_error(f"Failed to generate referral matrix: {str(e)}")
            
            if request.include_oto_matrix:
                try:
                    file_path = self._export_oto_matrix(report, output_dir)
                    response.add_generated_file(file_path)
                except Exception as e:
                    response.add_error(f"Failed to generate OTO matrix: {str(e)}")
            
            if request.include_combination_matrix:
                try:
                    file_path = self._export_combination_matrix(report, output_dir)
                    response.add_generated_file(file_path)
                except Exception as e:
                    response.add_error(f"Failed to generate combination matrix: {str(e)}")
            
            # Always generate TYFCB data if TYFCB entries exist
            print(f"Debug: Found {len(report.tyfcbs)} TYFCB entries in report")
            if report.tyfcbs:
                try:
                    print(f"Debug: Generating TYFCB data file...")
                    file_path = self._export_tyfcb_data(report, output_dir)
                    response.add_generated_file(file_path)
                    print(f"Debug: TYFCB data file generated successfully: {file_path}")
                except Exception as e:
                    print(f"Debug: TYFCB export failed: {str(e)}")
                    response.add_error(f"Failed to generate TYFCB data: {str(e)}")
            else:
                print("Debug: No TYFCB entries found, skipping TYFCB data generation")
            
            # Add metadata
            response.metadata = {
                'total_members': len(report.all_members),
                'total_referrals': report.metadata.get('total_referrals', 0),
                'total_one_to_ones': report.metadata.get('total_one_to_ones', 0),
                'total_tyfcbs': report.metadata.get('total_tyfcbs', 0),
                'total_tyfcb_amount': report.metadata.get('total_tyfcb_amount', 0),
                'files_generated': len(response.generated_files),
                'output_directory': str(output_dir)
            }
            
        except Exception as e:
            response.add_error(f"Report generation failed: {str(e)}")
        
        finally:
            response.execution_time_seconds = time.time() - start_time
        
        return response
    
    def _export_referral_matrix(self, report, output_dir: Path) -> Path:
        """Export the referral matrix to Excel."""
        try:
            file_path = output_dir / FileNames.REFERRAL_MATRIX
            self.export_service.export_referral_matrix(
                report.referral_matrix,
                file_path
            )
            return file_path
            
        except Exception as e:
            raise ExportError(f"Failed to export referral matrix: {str(e)}")
    
    def _export_oto_matrix(self, report, output_dir: Path) -> Path:
        """Export the one-to-one matrix to Excel."""
        try:
            file_path = output_dir / FileNames.OTO_MATRIX
            self.export_service.export_oto_matrix(
                report.one_to_one_matrix,
                file_path
            )
            return file_path
            
        except Exception as e:
            raise ExportError(f"Failed to export OTO matrix: {str(e)}")
    
    def _export_combination_matrix(self, report, output_dir: Path) -> Path:
        """Export the combination matrix to Excel."""
        try:
            file_path = output_dir / FileNames.COMBINATION_MATRIX
            self.export_service.export_combination_matrix(
                report.combination_matrix,
                file_path
            )
            return file_path
            
        except Exception as e:
            raise ExportError(f"Failed to export combination matrix: {str(e)}")
    
    def _export_tyfcb_data(self, report, output_dir: Path) -> Path:
        """Export the TYFCB data to Excel."""
        try:
            file_path = output_dir / FileNames.TYFCB_DATA
            self.export_service.export_tyfcb_data(
                report.all_members,
                report.tyfcbs,
                file_path
            )
            return file_path
            
        except Exception as e:
            raise ExportError(f"Failed to export TYFCB data: {str(e)}")
    
    def generate_quick_report(self) -> ReportGenerationResponse:
        """
        Generate a quick report using default settings and existing files.
        
        Returns:
            Report generation response
        """
        try:
            # Get files from default directories
            excel_files = self.path_manager.get_excel_files()
            member_files = self.path_manager.get_member_files()
            
            if not excel_files:
                response = ReportGenerationResponse(success=False)
                response.add_error("No Excel files found in the Excel files directory")
                return response
            
            if not member_files:
                response = ReportGenerationResponse(success=False)
                response.add_error("No member files found in the member names directory")
                return response
            
            # Create request with default settings
            request = ReportGenerationRequest(
                excel_files=excel_files,
                member_files=member_files,
                include_referral_matrix=True,
                include_oto_matrix=True,
                include_combination_matrix=True
            )
            
            return self.execute(request)
            
        except Exception as e:
            response = ReportGenerationResponse(success=False)
            response.add_error(f"Quick report generation failed: {str(e)}")
            return response
    
    def validate_input_files(self, excel_files: List[Path], 
                           member_files: List[Path]) -> List[str]:
        """
        Validate input files before processing.
        
        Args:
            excel_files: List of Excel files to validate
            member_files: List of member files to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        try:
            # Check if files exist and are readable
            for file_path in excel_files + member_files:
                if not file_path.exists():
                    errors.append(f"File not found: {file_path}")
                elif not file_path.is_file():
                    errors.append(f"Path is not a file: {file_path}")
                elif file_path.suffix.lower() not in ['.xls', '.xlsx']:
                    errors.append(f"Unsupported file format: {file_path}")
            
            # Validate PALMS files format
            for excel_file in excel_files:
                if excel_file.exists():
                    if not self.analysis_service.palms_repository.validate_palms_file_format(excel_file):
                        errors.append(f"Invalid PALMS file format: {excel_file}")
            
            return errors
            
        except Exception as e:
            errors.append(f"File validation error: {str(e)}")
            return errors