from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .member import Member


@dataclass
class TYFCB:
    """Domain model representing a TYFCB (Thank You For Closed Business) between BNI members."""
    
    giver: Member
    receiver: Member
    amount: float
    within_chapter: bool = True
    date: Optional[datetime] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate TYFCB data after creation."""
        if self.giver == self.receiver:
            raise ValueError("A member cannot give TYFCB to themselves")
        if self.amount < 0:
            raise ValueError("TYFCB amount cannot be negative")
    
    def __str__(self) -> str:
        chapter_type = "within chapter" if self.within_chapter else "outside chapter"
        return f"TYFCB from {self.giver.full_name} to {self.receiver.full_name}: ${self.amount:.2f} ({chapter_type})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TYFCB):
            return False
        return (self.giver == other.giver and 
                self.receiver == other.receiver and 
                self.amount == other.amount and
                self.within_chapter == other.within_chapter and
                self.date == other.date)
    
    def __hash__(self) -> int:
        return hash((self.giver, self.receiver, self.amount, self.within_chapter, self.date))