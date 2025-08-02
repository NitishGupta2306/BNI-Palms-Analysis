"""Service for generating and managing TYFCB analysis."""

from typing import List, Dict
from collections import defaultdict
from dataclasses import dataclass

from src.domain.models.member import Member
from src.domain.models.tyfcb import TYFCB
from src.domain.exceptions.domain_exceptions import DataProcessingError


@dataclass
class TYFCBStatistics:
    """Statistics for a member's TYFCB activity."""
    
    member: Member
    total_given_within_chapter: float = 0.0
    total_given_outside_chapter: float = 0.0
    total_received_within_chapter: float = 0.0
    total_received_outside_chapter: float = 0.0
    count_given_within_chapter: int = 0
    count_given_outside_chapter: int = 0
    count_received_within_chapter: int = 0
    count_received_outside_chapter: int = 0
    
    @property
    def total_given(self) -> float:
        """Total TYFCB amount given by this member."""
        return self.total_given_within_chapter + self.total_given_outside_chapter
    
    @property
    def total_received(self) -> float:
        """Total TYFCB amount received by this member."""
        return self.total_received_within_chapter + self.total_received_outside_chapter
    
    @property
    def total_count_given(self) -> int:
        """Total number of TYFCB entries given by this member."""
        return self.count_given_within_chapter + self.count_given_outside_chapter
    
    @property
    def total_count_received(self) -> int:
        """Total number of TYFCB entries received by this member."""
        return self.count_received_within_chapter + self.count_received_outside_chapter


@dataclass
class TYFCBSummary:
    """Summary of all TYFCB activity."""
    
    total_amount_within_chapter: float = 0.0
    total_amount_outside_chapter: float = 0.0
    total_count_within_chapter: int = 0
    total_count_outside_chapter: int = 0
    member_statistics: Dict[Member, TYFCBStatistics] = None
    
    def __post_init__(self):
        if self.member_statistics is None:
            self.member_statistics = {}
    
    @property
    def total_amount(self) -> float:
        """Total TYFCB amount across all members."""
        return self.total_amount_within_chapter + self.total_amount_outside_chapter
    
    @property
    def total_count(self) -> int:
        """Total number of TYFCB entries."""
        return self.total_count_within_chapter + self.total_count_outside_chapter
    
    @property
    def within_chapter_percentage(self) -> float:
        """Percentage of TYFCB amount that was within chapter."""
        if self.total_amount == 0:
            return 0.0
        return (self.total_amount_within_chapter / self.total_amount) * 100


class TYFCBService:
    """Service responsible for TYFCB analysis and statistics."""
    
    def calculate_member_statistics(self, members: List[Member], tyfcbs: List[TYFCB]) -> Dict[Member, TYFCBStatistics]:
        """
        Calculate TYFCB statistics for each member.
        
        Args:
            members: List of all members
            tyfcbs: List of all TYFCB entries
            
        Returns:
            Dictionary mapping members to their TYFCB statistics
        """
        try:
            # Initialize statistics for all members
            member_stats = {member: TYFCBStatistics(member=member) for member in members}
            
            # Process each TYFCB entry
            for tyfcb in tyfcbs:
                # Update giver statistics (only if giver is specified)
                if tyfcb.giver and tyfcb.giver in member_stats:
                    stats = member_stats[tyfcb.giver]
                    if tyfcb.within_chapter:
                        stats.total_given_within_chapter += tyfcb.amount
                        stats.count_given_within_chapter += 1
                    else:
                        stats.total_given_outside_chapter += tyfcb.amount
                        stats.count_given_outside_chapter += 1
                
                # Update receiver statistics (primary focus for TYFCB)
                if tyfcb.receiver in member_stats:
                    stats = member_stats[tyfcb.receiver]
                    if tyfcb.within_chapter:
                        stats.total_received_within_chapter += tyfcb.amount
                        stats.count_received_within_chapter += 1
                    else:
                        stats.total_received_outside_chapter += tyfcb.amount
                        stats.count_received_outside_chapter += 1
            
            return member_stats
            
        except Exception as e:
            raise DataProcessingError(f"Error calculating TYFCB member statistics: {str(e)}")
    
    def generate_tyfcb_summary(self, members: List[Member], tyfcbs: List[TYFCB]) -> TYFCBSummary:
        """
        Generate a complete TYFCB summary.
        
        Args:
            members: List of all members
            tyfcbs: List of all TYFCB entries
            
        Returns:
            TYFCBSummary with complete statistics
        """
        try:
            # Calculate member statistics
            member_statistics = self.calculate_member_statistics(members, tyfcbs)
            
            # Calculate totals
            summary = TYFCBSummary(member_statistics=member_statistics)
            
            for tyfcb in tyfcbs:
                if tyfcb.within_chapter:
                    summary.total_amount_within_chapter += tyfcb.amount
                    summary.total_count_within_chapter += 1
                else:
                    summary.total_amount_outside_chapter += tyfcb.amount
                    summary.total_count_outside_chapter += 1
            
            return summary
            
        except Exception as e:
            raise DataProcessingError(f"Error generating TYFCB summary: {str(e)}")
    
    def get_top_performers(self, member_statistics: Dict[Member, TYFCBStatistics], 
                          by_given: bool = True, top_n: int = 5) -> List[tuple]:
        """
        Get top performing members by TYFCB given or received.
        
        Args:
            member_statistics: Dictionary of member statistics
            by_given: If True, rank by amount given; if False, rank by amount received
            top_n: Number of top performers to return
            
        Returns:
            List of (member, amount) tuples sorted by performance
        """
        try:
            performers = []
            
            for member, stats in member_statistics.items():
                amount = stats.total_given if by_given else stats.total_received
                if amount > 0:
                    performers.append((member, amount))
            
            # Sort by amount (descending)
            performers.sort(key=lambda x: x[1], reverse=True)
            
            return performers[:top_n]
            
        except Exception as e:
            raise DataProcessingError(f"Error getting top TYFCB performers: {str(e)}")
    
    def create_tyfcb_matrix_data(self, members: List[Member], tyfcbs: List[TYFCB]) -> Dict[Member, Dict[Member, Dict[str, float]]]:
        """
        Create matrix data for TYFCB amounts between members.
        
        Args:
            members: List of all members
            tyfcbs: List of all TYFCB entries
            
        Returns:
            Nested dictionary: giver -> receiver -> {within_chapter: amount, outside_chapter: amount}
        """
        try:
            # Initialize matrix with zeros
            matrix_data = {
                giver: {
                    receiver: {"within_chapter": 0.0, "outside_chapter": 0.0}
                    for receiver in members
                } 
                for giver in members
            }
            
            # Populate matrix with TYFCB data (only when giver is specified)
            for tyfcb in tyfcbs:
                if tyfcb.giver and tyfcb.giver in matrix_data and tyfcb.receiver in matrix_data[tyfcb.giver]:
                    cell = matrix_data[tyfcb.giver][tyfcb.receiver]
                    if tyfcb.within_chapter:
                        cell["within_chapter"] += tyfcb.amount
                    else:
                        cell["outside_chapter"] += tyfcb.amount
            
            return matrix_data
            
        except Exception as e:
            raise DataProcessingError(f"Error creating TYFCB matrix data: {str(e)}")