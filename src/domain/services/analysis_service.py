"""Core business logic service for BNI PALMS analysis."""

from typing import List, Tuple, Optional

from src.domain.models.member import Member
from src.domain.models.referral import Referral
from src.domain.models.one_to_one import OneToOne
from src.domain.models.analysis_result import AnalysisReport, AnalysisMatrix, ComparisonResult
from src.domain.exceptions.domain_exceptions import DataProcessingError
from src.domain.services.matrix_service import MatrixService
from src.infrastructure.data.repositories.member_repository import MemberRepository
from src.infrastructure.data.repositories.palms_repository import PalmsRepository


class AnalysisService:
    """Core service for BNI PALMS analysis operations."""
    
    def __init__(self):
        self.matrix_service = MatrixService()
        self.member_repository = MemberRepository()
        self.palms_repository = PalmsRepository()
    
    def load_members_data(self) -> List[Member]:
        """
        Load all member data from the configured directory.
        
        Returns:
            List of Member objects
        """
        try:
            members = self.member_repository.load_members_from_directory()
            
            if not members:
                raise DataProcessingError("No members found. Please ensure member files are uploaded.")
            
            # Validate all members
            for member in members:
                self.member_repository.validate_member(member)
            
            return members
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error loading members data: {str(e)}")
    
    def load_palms_data(self, members: List[Member]) -> Tuple[List[Referral], List[OneToOne]]:
        """
        Load all PALMS data from the configured directory.
        
        Args:
            members: List of valid members to match against
            
        Returns:
            Tuple of (referrals, one_to_ones)
        """
        try:
            referrals, one_to_ones = self.palms_repository.load_all_palms_data(members)
            
            return referrals, one_to_ones
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error loading PALMS data: {str(e)}")
    
    def generate_complete_analysis(self, members: Optional[List[Member]] = None,
                                 referrals: Optional[List[Referral]] = None,
                                 one_to_ones: Optional[List[OneToOne]] = None) -> AnalysisReport:
        """
        Generate a complete analysis report with all matrices.
        
        Args:
            members: Optional list of members (will load if not provided)
            referrals: Optional list of referrals (will load if not provided)
            one_to_ones: Optional list of one-to-ones (will load if not provided)
            
        Returns:
            Complete AnalysisReport
        """
        try:
            # Load data if not provided
            if members is None:
                members = self.load_members_data()
            
            if referrals is None or one_to_ones is None:
                loaded_referrals, loaded_one_to_ones = self.load_palms_data(members)
                if referrals is None:
                    referrals = loaded_referrals
                if one_to_ones is None:
                    one_to_ones = loaded_one_to_ones
            
            # Generate matrices
            referral_matrix = self.matrix_service.generate_referral_matrix(members, referrals)
            one_to_one_matrix = self.matrix_service.generate_one_to_one_matrix(members, one_to_ones)
            combination_matrix = self.matrix_service.generate_combination_matrix(
                referral_matrix, one_to_one_matrix
            )
            
            # Validate consistency
            if not self.matrix_service.validate_matrix_consistency(
                referral_matrix, one_to_one_matrix, combination_matrix
            ):
                raise DataProcessingError("Generated matrices have inconsistent member data")
            
            # Create analysis report
            report = AnalysisReport(
                referral_matrix=referral_matrix,
                one_to_one_matrix=one_to_one_matrix,
                combination_matrix=combination_matrix,
                metadata={
                    'total_members': len(members),
                    'total_referrals': len(referrals),
                    'total_one_to_ones': len(one_to_ones),
                    'palms_stats': self.palms_repository.get_palms_data_statistics(referrals, one_to_ones),
                    'member_stats': self.member_repository.get_member_statistics(members)
                }
            )
            
            return report
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error generating complete analysis: {str(e)}")
    
    def compare_combination_matrices(self, new_matrix: AnalysisMatrix, 
                                   old_matrix: AnalysisMatrix) -> ComparisonResult:
        """
        Compare two combination matrices to identify changes.
        
        Args:
            new_matrix: The newer combination matrix
            old_matrix: The older combination matrix
            
        Returns:
            ComparisonResult with change analysis
        """
        try:
            return self.matrix_service.compare_matrices(new_matrix, old_matrix)
            
        except Exception as e:
            raise DataProcessingError(f"Error comparing combination matrices: {str(e)}")
    
    def get_member_performance_analysis(self, report: AnalysisReport, 
                                      member: Member) -> dict:
        """
        Get detailed performance analysis for a specific member.
        
        Args:
            report: Complete analysis report
            member: Member to analyze
            
        Returns:
            Dictionary with detailed member analysis
        """
        try:
            # Get statistics from each matrix
            ref_stats = report.referral_matrix.member_statistics.get(member)
            oto_stats = report.one_to_one_matrix.member_statistics.get(member)
            combo_stats = report.combination_matrix.member_statistics.get(member)
            
            if not all([ref_stats, oto_stats, combo_stats]):
                raise DataProcessingError(f"Member {member.full_name} not found in analysis")
            
            analysis = {
                'member_name': member.full_name,
                'referrals': {
                    'given': ref_stats.total_referrals_given,
                    'received': ref_stats.total_referrals_received,
                    'unique_given': ref_stats.unique_referrals_given,
                    'unique_received': ref_stats.unique_referrals_received,
                },
                'one_to_ones': {
                    'total': oto_stats.total_one_to_ones,
                    'unique': oto_stats.unique_one_to_ones,
                },
                'combinations': {
                    'neither': combo_stats.neither_count,
                    'oto_only': combo_stats.oto_only_count,
                    'referral_only': combo_stats.referral_only_count,
                    'both': combo_stats.both_count,
                    'total_interactions': combo_stats.total_interactions,
                },
                'performance_metrics': {
                    'referral_efficiency': (
                        ref_stats.unique_referrals_given / len(report.all_members)
                        if report.all_members else 0
                    ),
                    'networking_score': (
                        (oto_stats.unique_one_to_ones + ref_stats.unique_referrals_given) / 
                        (len(report.all_members) * 2) if report.all_members else 0
                    ),
                    'engagement_ratio': (
                        combo_stats.total_interactions / len(report.all_members)
                        if report.all_members else 0
                    ),
                }
            }
            
            return analysis
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error analyzing member performance: {str(e)}")
    
    def get_chapter_overview(self, report: AnalysisReport) -> dict:
        """
        Get a high-level overview of the chapter's performance.
        
        Args:
            report: Complete analysis report
            
        Returns:
            Dictionary with chapter overview
        """
        try:
            # Get summaries from each matrix
            ref_summary = self.matrix_service.get_matrix_summary(report.referral_matrix)
            oto_summary = self.matrix_service.get_matrix_summary(report.one_to_one_matrix)
            combo_summary = self.matrix_service.get_matrix_summary(report.combination_matrix)
            
            # Calculate chapter-wide metrics
            total_members = len(report.all_members)
            active_referral_members = ref_summary['active_members']
            active_oto_members = oto_summary['active_members']
            
            overview = {
                'chapter_size': total_members,
                'referrals': {
                    'total': ref_summary['total_interactions'],
                    'active_members': active_referral_members,
                    'participation_rate': active_referral_members / total_members if total_members > 0 else 0,
                    'average_per_member': ref_summary['total_interactions'] / total_members if total_members > 0 else 0,
                    'top_givers': ref_summary['top_performers']
                },
                'one_to_ones': {
                    'total': oto_summary['total_interactions'],
                    'active_members': active_oto_members,
                    'participation_rate': active_oto_members / total_members if total_members > 0 else 0,
                    'average_per_member': oto_summary['total_interactions'] / total_members if total_members > 0 else 0,
                    'top_networkers': oto_summary['top_performers']
                },
                'engagement': {
                    'total_active_members': len(set(
                        [m for m, s in report.referral_matrix.member_statistics.items() 
                         if s.total_referrals_given > 0] +
                        [m for m, s in report.one_to_one_matrix.member_statistics.items() 
                         if s.total_one_to_ones > 0]
                    )),
                    'overall_participation': None,  # Will calculate below
                    'top_overall_performers': combo_summary['top_performers']
                },
                'metadata': report.metadata
            }
            
            # Calculate overall participation rate
            overview['engagement']['overall_participation'] = (
                overview['engagement']['total_active_members'] / total_members 
                if total_members > 0 else 0
            )
            
            return overview
            
        except Exception as e:
            raise DataProcessingError(f"Error generating chapter overview: {str(e)}")
    
    def validate_data_quality(self, members: List[Member], 
                            referrals: List[Referral], 
                            one_to_ones: List[OneToOne]) -> dict:
        """
        Validate the quality of loaded data.
        
        Args:
            members: List of members
            referrals: List of referrals
            one_to_ones: List of one-to-ones
            
        Returns:
            Dictionary with data quality metrics
        """
        try:
            # Check for duplicate members
            normalized_names = [m.normalized_name for m in members]
            duplicate_members = len(normalized_names) - len(set(normalized_names))
            
            # Check for self-referrals (should be 0 due to domain model validation)
            self_referrals = sum(1 for r in referrals if r.giver == r.receiver)
            
            # Check for self one-to-ones (should be 0 due to domain model validation)
            self_otos = sum(1 for oto in one_to_ones if oto.member1 == oto.member2)
            
            # Check for members with incomplete names
            incomplete_names = sum(1 for m in members if not m.first_name or not m.last_name)
            
            quality_report = {
                'members': {
                    'total': len(members),
                    'duplicates': duplicate_members,
                    'incomplete_names': incomplete_names,
                    'valid': len(members) - duplicate_members - incomplete_names
                },
                'referrals': {
                    'total': len(referrals),
                    'self_referrals': self_referrals,
                    'valid': len(referrals) - self_referrals
                },
                'one_to_ones': {
                    'total': len(one_to_ones),
                    'self_meetings': self_otos,
                    'valid': len(one_to_ones) - self_otos
                },
                'overall_quality_score': 0  # Will calculate below
            }
            
            # Calculate overall quality score (0-100)
            total_records = len(members) + len(referrals) + len(one_to_ones)
            total_issues = duplicate_members + incomplete_names + self_referrals + self_otos
            
            if total_records > 0:
                quality_report['overall_quality_score'] = (
                    (total_records - total_issues) / total_records * 100
                )
            
            return quality_report
            
        except Exception as e:
            raise DataProcessingError(f"Error validating data quality: {str(e)}")