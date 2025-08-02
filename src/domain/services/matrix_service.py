"""Service for generating and managing analysis matrices."""

from typing import List, Dict, Set
from collections import defaultdict

from src.domain.models.member import Member
from src.domain.models.referral import Referral
from src.domain.models.one_to_one import OneToOne
from src.domain.models.analysis_result import (
    AnalysisMatrix, MatrixType, MemberStatistics, ComparisonResult
)
from src.domain.exceptions.domain_exceptions import MatrixGenerationError
from src.shared.constants.app_constants import CombinationValues


class MatrixService:
    """Service responsible for generating analysis matrices."""
    
    def generate_referral_matrix(self, members: List[Member], 
                               referrals: List[Referral]) -> AnalysisMatrix:
        """
        Generate a referral matrix from members and referrals data.
        
        Args:
            members: List of all members
            referrals: List of all referrals
            
        Returns:
            AnalysisMatrix with referral data
        """
        try:
            # Initialize matrix with zeros
            matrix_data = {
                giver: {receiver: 0 for receiver in members} 
                for giver in members
            }
            
            # Count referrals
            for referral in referrals:
                if referral.giver in matrix_data and referral.receiver in matrix_data[referral.giver]:
                    matrix_data[referral.giver][referral.receiver] += 1
            
            # Calculate member statistics
            member_stats = {}
            for member in members:
                stats = MemberStatistics(member=member)
                
                # Calculate referrals given
                stats.total_referrals_given = sum(matrix_data[member].values())
                stats.unique_referrals_given = sum(1 for count in matrix_data[member].values() if count > 0)
                
                # Calculate referrals received
                stats.total_referrals_received = sum(
                    matrix_data[other_member][member] for other_member in members
                )
                stats.unique_referrals_received = sum(
                    1 for other_member in members if matrix_data[other_member][member] > 0
                )
                
                member_stats[member] = stats
            
            return AnalysisMatrix(
                matrix_type=MatrixType.REFERRAL,
                data=matrix_data,
                member_statistics=member_stats,
                total_members=len(members)
            )
            
        except Exception as e:
            raise MatrixGenerationError(f"Error generating referral matrix: {str(e)}")
    
    def generate_one_to_one_matrix(self, members: List[Member], 
                                 one_to_ones: List[OneToOne]) -> AnalysisMatrix:
        """
        Generate a one-to-one matrix from members and one-to-one data.
        
        Args:
            members: List of all members
            one_to_ones: List of all one-to-one meetings
            
        Returns:
            AnalysisMatrix with one-to-one data
        """
        try:
            # Initialize matrix with zeros
            matrix_data = {
                member1: {member2: 0 for member2 in members} 
                for member1 in members
            }
            
            # Count one-to-one meetings (symmetric)
            for oto in one_to_ones:
                if (oto.member1 in matrix_data and oto.member2 in matrix_data and
                    oto.member2 in matrix_data[oto.member1] and oto.member1 in matrix_data[oto.member2]):
                    matrix_data[oto.member1][oto.member2] += 1
                    matrix_data[oto.member2][oto.member1] += 1
            
            # Calculate member statistics
            member_stats = {}
            for member in members:
                stats = MemberStatistics(member=member)
                
                # Calculate one-to-ones
                stats.total_one_to_ones = sum(matrix_data[member].values())
                stats.unique_one_to_ones = sum(1 for count in matrix_data[member].values() if count > 0)
                
                member_stats[member] = stats
            
            return AnalysisMatrix(
                matrix_type=MatrixType.ONE_TO_ONE,
                data=matrix_data,
                member_statistics=member_stats,
                total_members=len(members)
            )
            
        except Exception as e:
            raise MatrixGenerationError(f"Error generating one-to-one matrix: {str(e)}")
    
    def generate_combination_matrix(self, referral_matrix: AnalysisMatrix, 
                                  one_to_one_matrix: AnalysisMatrix) -> AnalysisMatrix:
        """
        Generate a combination matrix from referral and one-to-one matrices.
        
        Args:
            referral_matrix: The referral analysis matrix
            one_to_one_matrix: The one-to-one analysis matrix
            
        Returns:
            AnalysisMatrix with combination data
        """
        try:
            members = referral_matrix.get_all_members()
            
            # Initialize matrix with zeros
            matrix_data = {
                giver: {receiver: 0 for receiver in members} 
                for giver in members
            }
            
            # Generate combination values
            for giver in members:
                for receiver in members:
                    referral_count = referral_matrix.get_cell_value(giver, receiver)
                    oto_count = one_to_one_matrix.get_cell_value(giver, receiver)
                    
                    if referral_count > 0 and oto_count > 0:
                        matrix_data[giver][receiver] = CombinationValues.BOTH
                    elif referral_count > 0:
                        matrix_data[giver][receiver] = CombinationValues.REFERRAL_ONLY
                    elif oto_count > 0:
                        matrix_data[giver][receiver] = CombinationValues.OTO_ONLY
                    else:
                        matrix_data[giver][receiver] = CombinationValues.NEITHER
            
            # Calculate member statistics
            member_stats = {}
            for member in members:
                stats = MemberStatistics(member=member)
                
                # Count combination types
                row_data = matrix_data[member]
                stats.neither_count = sum(1 for value in row_data.values() if value == CombinationValues.NEITHER)
                stats.oto_only_count = sum(1 for value in row_data.values() if value == CombinationValues.OTO_ONLY)
                stats.referral_only_count = sum(1 for value in row_data.values() if value == CombinationValues.REFERRAL_ONLY)
                stats.both_count = sum(1 for value in row_data.values() if value == CombinationValues.BOTH)
                
                member_stats[member] = stats
            
            return AnalysisMatrix(
                matrix_type=MatrixType.COMBINATION,
                data=matrix_data,
                member_statistics=member_stats,
                total_members=len(members)
            )
            
        except Exception as e:
            raise MatrixGenerationError(f"Error generating combination matrix: {str(e)}")
    
    def compare_matrices(self, new_matrix: AnalysisMatrix, 
                        old_matrix: AnalysisMatrix) -> ComparisonResult:
        """
        Compare two matrices to identify changes.
        
        Args:
            new_matrix: The newer matrix
            old_matrix: The older matrix to compare against
            
        Returns:
            ComparisonResult with change analysis
        """
        try:
            comparison = ComparisonResult(
                new_matrix=new_matrix,
                old_matrix=old_matrix
            )
            
            comparison.calculate_changes()
            
            return comparison
            
        except Exception as e:
            raise MatrixGenerationError(f"Error comparing matrices: {str(e)}")
    
    def get_matrix_summary(self, matrix: AnalysisMatrix) -> Dict:
        """
        Get a summary of matrix statistics.
        
        Args:
            matrix: The matrix to summarize
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            summary = {
                'matrix_type': matrix.matrix_type.value,
                'total_members': matrix.total_members,
                'total_interactions': 0,
                'active_members': 0,  # Members with at least one interaction
                'top_performers': [],  # Top 5 most active members
            }
            
            # Calculate totals based on matrix type
            member_totals = []
            
            for member, stats in matrix.member_statistics.items():
                if matrix.matrix_type == MatrixType.REFERRAL:
                    total = stats.total_referrals_given
                elif matrix.matrix_type == MatrixType.ONE_TO_ONE:
                    total = stats.total_one_to_ones
                else:  # COMBINATION
                    total = stats.total_interactions
                
                summary['total_interactions'] += total
                
                if total > 0:
                    summary['active_members'] += 1
                    member_totals.append((member, total))
            
            # Get top performers
            member_totals.sort(key=lambda x: x[1], reverse=True)
            summary['top_performers'] = [
                {'member': member.full_name, 'total': total}
                for member, total in member_totals[:5]
            ]
            
            return summary
            
        except Exception as e:
            raise MatrixGenerationError(f"Error generating matrix summary: {str(e)}")
    
    def validate_matrix_consistency(self, referral_matrix: AnalysisMatrix,
                                  one_to_one_matrix: AnalysisMatrix,
                                  combination_matrix: AnalysisMatrix) -> bool:
        """
        Validate that all matrices have consistent member data.
        
        Args:
            referral_matrix: Referral matrix
            one_to_one_matrix: One-to-one matrix
            combination_matrix: Combination matrix
            
        Returns:
            True if all matrices are consistent
        """
        try:
            ref_members = set(referral_matrix.get_all_members())
            oto_members = set(one_to_one_matrix.get_all_members())
            combo_members = set(combination_matrix.get_all_members())
            
            # All matrices should have the same members
            return ref_members == oto_members == combo_members
            
        except Exception as e:
            raise MatrixGenerationError(f"Error validating matrix consistency: {str(e)}")