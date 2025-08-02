from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .member import Member


@dataclass
class Referral:
    """Domain model representing a referral between BNI members."""
    
    giver: Member
    receiver: Member
    date: Optional[datetime] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate referral data after creation."""
        if self.giver == self.receiver:
            raise ValueError("A member cannot refer to themselves")
    
    def __str__(self) -> str:
        return f"Referral from {self.giver.full_name} to {self.receiver.full_name}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Referral):
            return False
        return (self.giver == other.giver and 
                self.receiver == other.receiver and 
                self.date == other.date)
    
    def __hash__(self) -> int:
        return hash((self.giver, self.receiver, self.date))