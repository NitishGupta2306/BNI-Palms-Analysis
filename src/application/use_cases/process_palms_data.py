"""Use case for processing PALMS data files."""

import time
from pathlib import Path
from typing import List, Tuple

from src.application.dto.report_request import ProcessPalmsDataRequest
from src.application.dto.analysis_response import ProcessPalmsDataResponse
from src.domain.services.analysis_service import AnalysisService
from src.domain.models.member import Member
from src.domain.models.referral import Referral
from src.domain.models.one_to_one import OneToOne
from src.domain.models.tyfcb import TYFCB
from src.domain.exceptions.domain_exceptions import DataProcessingError
from src.infrastructure.data.file_handlers.file_converter import FileConverter
from src.infrastructure.config.paths import get_path_manager


class ProcessPalmsDataUseCase:
    """Use case for processing PALMS data files and preparing them for analysis."""
    
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.file_converter = FileConverter()
        self.path_manager = get_path_manager()
    
    def execute(self, request: ProcessPalmsDataRequest) -> ProcessPalmsDataResponse:
        """
        Execute the PALMS data processing use case.
        
        Args:
            request: PALMS data processing request
            
        Returns:
            Processing response with results and statistics
        """
        start_time = time.time()
        response = ProcessPalmsDataResponse(success=True)
        
        try:
            # Validate request
            request.validate()
            
            # Convert XLS files to XLSX if requested
            if request.convert_xls_files:
                converted_files = self._convert_xls_files(request.data_directory)
                response.converted_files.extend(converted_files)
                
                # Also convert member files
                member_converted = self._convert_xls_files(request.member_directory)
                response.converted_files.extend(member_converted)
            
            # Load member data
            members = self._load_members_data(request.member_directory, response)
            response.members_count = len(members)
            
            if not members:
                response.add_error("No valid members found")
                return response
            
            # Load PALMS data
            referrals, one_to_ones, tyfcbs = self._load_palms_data(
                request.data_directory, members, response
            )
            response.referrals_count = len(referrals)
            response.one_to_ones_count = len(one_to_ones)
            response.tyfcbs_count = len(tyfcbs)
            
            # Validate data quality if requested
            if request.validate_data:
                quality_report = self.analysis_service.validate_data_quality(
                    members, referrals, one_to_ones, tyfcbs
                )
                response.data_quality_report = quality_report
                
                # Add warnings for quality issues
                if quality_report['overall_quality_score'] < 90:
                    response.add_warning(
                        f"Data quality score is {quality_report['overall_quality_score']:.1f}%. "
                        "Consider reviewing the input files."
                    )
                
                if quality_report['members']['duplicates'] > 0:
                    response.add_warning(
                        f"Found {quality_report['members']['duplicates']} duplicate members"
                    )
                
                if quality_report['referrals']['self_referrals'] > 0:
                    response.add_warning(
                        f"Found {quality_report['referrals']['self_referrals']} self-referrals (filtered out)"
                    )
            
            # Get processed files list
            response.processed_files = self._get_processed_files(
                request.data_directory, request.member_directory
            )
            
        except Exception as e:
            response.add_error(f"PALMS data processing failed: {str(e)}")
        
        finally:
            response.execution_time_seconds = time.time() - start_time
        
        return response
    
    def _convert_xls_files(self, directory: Path) -> List[Path]:
        """Convert all XLS files in a directory to XLSX format."""
        try:
            converted_files = self.file_converter.batch_convert_directory(
                directory, delete_originals=True
            )
            return converted_files
            
        except Exception as e:
            raise DataProcessingError(f"Error converting XLS files in {directory}: {str(e)}")
    
    def _load_members_data(self, member_directory: Path, 
                          response: ProcessPalmsDataResponse) -> List[Member]:
        """Load member data from the member directory."""
        try:
            # Temporarily set the member directory path
            original_member_dir = self.path_manager.settings.directories.member_names
            self.path_manager.settings.directories.member_names = str(member_directory)
            
            try:
                members = self.analysis_service.load_members_data()
                return members
            finally:
                # Restore original path
                self.path_manager.settings.directories.member_names = original_member_dir
                
        except DataProcessingError as e:
            response.add_error(f"Failed to load member data: {str(e)}")
            return []
        except Exception as e:
            response.add_error(f"Unexpected error loading member data: {str(e)}")
            return []
    
    def _load_palms_data(self, data_directory: Path, members: List[Member],
                        response: ProcessPalmsDataResponse) -> Tuple[List[Referral], List[OneToOne], List[TYFCB]]:
        """Load PALMS data from the data directory."""
        try:
            # Temporarily set the Excel files directory path
            original_excel_dir = self.path_manager.settings.directories.excel_files
            self.path_manager.settings.directories.excel_files = str(data_directory)
            
            try:
                referrals, one_to_ones, tyfcbs = self.analysis_service.load_palms_data(members)
                return referrals, one_to_ones, tyfcbs
            finally:
                # Restore original path
                self.path_manager.settings.directories.excel_files = original_excel_dir
                
        except DataProcessingError as e:
            response.add_error(f"Failed to load PALMS data: {str(e)}")
            return [], [], []
        except Exception as e:
            response.add_error(f"Unexpected error loading PALMS data: {str(e)}")
            return [], [], []
    
    def _get_processed_files(self, data_directory: Path, 
                           member_directory: Path) -> List[Path]:
        """Get list of all processed files."""
        try:
            processed_files = []
            
            # Get Excel files
            if data_directory.exists():
                for ext in ['.xlsx', '.xls']:
                    processed_files.extend(data_directory.glob(f"*{ext}"))
            
            # Get member files
            if member_directory.exists():
                for ext in ['.xlsx', '.xls']:
                    processed_files.extend(member_directory.glob(f"*{ext}"))
            
            return sorted(processed_files)
            
        except Exception as e:
            raise DataProcessingError(f"Error getting processed files list: {str(e)}")
    
    def process_from_default_directories(self) -> ProcessPalmsDataResponse:
        """
        Process PALMS data from the default configured directories.
        
        Returns:
            Processing response
        """
        try:
            request = ProcessPalmsDataRequest(
                data_directory=self.path_manager.excel_files_dir,
                member_directory=self.path_manager.member_names_dir,
                convert_xls_files=True,
                validate_data=True
            )
            
            return self.execute(request)
            
        except Exception as e:
            response = ProcessPalmsDataResponse(success=False)
            response.add_error(f"Processing from default directories failed: {str(e)}")
            return response
    
    def get_processing_statistics(self, response: ProcessPalmsDataResponse) -> dict:
        """
        Get detailed processing statistics from a response.
        
        Args:
            response: Processing response
            
        Returns:
            Dictionary with detailed statistics
        """
        try:
            stats = {
                'execution_summary': {
                    'success': response.success,
                    'execution_time': response.execution_time_seconds,
                    'errors': len(response.errors),
                    'warnings': len(response.warnings)
                },
                'data_summary': {
                    'members_processed': response.members_count,
                    'referrals_processed': response.referrals_count,
                    'one_to_ones_processed': response.one_to_ones_count,
                    'files_processed': len(response.processed_files),
                    'files_converted': len(response.converted_files)
                },
                'quality_summary': response.data_quality_report or {},
                'file_details': {
                    'processed_files': [str(f) for f in response.processed_files],
                    'converted_files': [str(f) for f in response.converted_files]
                }
            }
            
            # Add quality insights
            if response.data_quality_report:
                quality = response.data_quality_report
                stats['quality_insights'] = {
                    'overall_score': quality.get('overall_quality_score', 0),
                    'data_completeness': {
                        'valid_members': quality.get('members', {}).get('valid', 0),
                        'valid_referrals': quality.get('referrals', {}).get('valid', 0),
                        'valid_one_to_ones': quality.get('one_to_ones', {}).get('valid', 0)
                    },
                    'issues_detected': {
                        'duplicate_members': quality.get('members', {}).get('duplicates', 0),
                        'incomplete_member_names': quality.get('members', {}).get('incomplete_names', 0),
                        'self_referrals': quality.get('referrals', {}).get('self_referrals', 0),
                        'self_meetings': quality.get('one_to_ones', {}).get('self_meetings', 0)
                    }
                }
            
            return stats
            
        except Exception as e:
            return {
                'error': f"Failed to generate processing statistics: {str(e)}",
                'execution_summary': {
                    'success': response.success,
                    'errors': len(response.errors),
                    'warnings': len(response.warnings)
                }
            }