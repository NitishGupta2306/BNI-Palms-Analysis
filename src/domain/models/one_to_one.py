from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .member import Member


@dataclass
class OneToOne:
    """Domain model representing a one-to-one meeting between BNI members."""
    
    member1: Member
    member2: Member
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate one-to-one data after creation."""
        if self.member1 == self.member2:
            raise ValueError("A member cannot have a one-to-one with themselves")
        
        # Normalize the order to ensure consistency (alphabetical by normalized name)
        if self.member1.normalized_name > self.member2.normalized_name:
            self.member1, self.member2 = self.member2, self.member1
    
    @property
    def participants(self) -> tuple[Member, Member]:
        """Get the participants in the one-to-one meeting."""
        return (self.member1, self.member2)
    
    def involves_member(self, member: Member) -> bool:
        """Check if a specific member is involved in this one-to-one."""
        return member == self.member1 or member == self.member2
    
    def get_other_member(self, member: Member) -> Optional[Member]:
        """Get the other member in the one-to-one meeting."""
        if member == self.member1:
            return self.member2
        elif member == self.member2:
            return self.member1
        return None
    
    def __str__(self) -> str:
        return f"One-to-One between {self.member1.full_name} and {self.member2.full_name}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, OneToOne):
            return False
        return (self.member1 == other.member1 and 
                self.member2 == other.member2 and 
                self.date == other.date)
    
    def __hash__(self) -> int:
        return hash((self.member1, self.member2, self.date))