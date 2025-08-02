from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .member import Member


class MatrixType(Enum):
    """Types of matrices that can be generated."""
    REFERRAL = "referral"
    ONE_TO_ONE = "one_to_one"
    COMBINATION = "combination"


@dataclass
class MatrixCell:
    """Represents a single cell in an analysis matrix."""
    
    row_member: Member
    column_member: Member
    value: int
    matrix_type: MatrixType
    
    def __str__(self) -> str:
        return f"{self.row_member.full_name} -> {self.column_member.full_name}: {self.value}"


@dataclass
class MemberStatistics:
    """Statistics for a single member across different matrix types."""
    
    member: Member
    total_referrals_given: int = 0
    total_referrals_received: int = 0
    unique_referrals_given: int = 0
    unique_referrals_received: int = 0
    total_one_to_ones: int = 0
    unique_one_to_ones: int = 0
    
    # Combination matrix statistics
    neither_count: int = 0
    oto_only_count: int = 0
    referral_only_count: int = 0
    both_count: int = 0
    
    @property
    def total_interactions(self) -> int:
        """Total number of meaningful interactions (not 'neither')."""
        return self.oto_only_count + self.referral_only_count + self.both_count


@dataclass
class AnalysisMatrix:
    """Represents a complete analysis matrix with metadata."""
    
    matrix_type: MatrixType
    data: Dict[Member, Dict[Member, int]] = field(default_factory=dict)
    member_statistics: Dict[Member, MemberStatistics] = field(default_factory=dict)
    total_members: int = 0
    
    def get_cell_value(self, row_member: Member, column_member: Member) -> int:
        """Get the value at a specific matrix position."""
        return self.data.get(row_member, {}).get(column_member, 0)
    
    def set_cell_value(self, row_member: Member, column_member: Member, value: int) -> None:
        """Set the value at a specific matrix position."""
        if row_member not in self.data:
            self.data[row_member] = {}
        self.data[row_member][column_member] = value
    
    def get_all_members(self) -> List[Member]:
        """Get all members involved in this matrix."""
        members = set()
        for row_member, row_data in self.data.items():
            members.add(row_member)
            members.update(row_data.keys())
        return sorted(list(members), key=lambda m: m.normalized_name)


@dataclass
class ComparisonResult:
    """Result of comparing two matrices over time."""
    
    new_matrix: AnalysisMatrix
    old_matrix: Optional[AnalysisMatrix]
    member_changes: Dict[Member, Dict[str, Any]] = field(default_factory=dict)
    
    def calculate_changes(self) -> None:
        """Calculate changes between old and new matrices."""
        if not self.old_matrix:
            return
            
        for member in self.new_matrix.get_all_members():
            new_stats = self.new_matrix.member_statistics.get(member)
            old_stats = self.old_matrix.member_statistics.get(member)
            
            if new_stats and old_stats:
                changes = {
                    'referral_change': new_stats.total_referrals_given - old_stats.total_referrals_given,
                    'referral_received_change': new_stats.total_referrals_received - old_stats.total_referrals_received,
                    'oto_change': new_stats.total_one_to_ones - old_stats.total_one_to_ones,
                    'neither_change': new_stats.neither_count - old_stats.neither_count,
                }
                self.member_changes[member] = changes


@dataclass
class AnalysisReport:
    """Complete analysis report containing all matrices and statistics."""
    
    referral_matrix: AnalysisMatrix
    one_to_one_matrix: AnalysisMatrix
    combination_matrix: AnalysisMatrix
    comparison_result: Optional[ComparisonResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def all_members(self) -> List[Member]:
        """Get all unique members across all matrices."""
        members = set()
        members.update(self.referral_matrix.get_all_members())
        members.update(self.one_to_one_matrix.get_all_members())
        members.update(self.combination_matrix.get_all_members())
        return sorted(list(members), key=lambda m: m.normalized_name)