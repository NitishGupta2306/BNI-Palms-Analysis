from dataclasses import dataclass
from typing import Optional


@dataclass
class Member:
    """Domain model representing a BNI member."""
    
    first_name: str
    last_name: str
    normalized_name: Optional[str] = None
    
    def __post_init__(self):
        """Initialize calculated fields after object creation."""
        if self.normalized_name is None:
            self.normalized_name = f"{self.first_name}{self.last_name}".replace(" ", "").lower()
    
    @property
    def full_name(self) -> str:
        """Get the member's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @classmethod
    def from_full_name(cls, full_name: str) -> 'Member':
        """Create a Member from a full name string."""
        parts = full_name.strip().split(' ', 1)
        first_name = parts[0] if len(parts) > 0 else ""
        last_name = parts[1] if len(parts) > 1 else ""
        return cls(first_name=first_name, last_name=last_name)
    
    def __str__(self) -> str:
        return self.full_name
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Member):
            return False
        return self.normalized_name == other.normalized_name
    
    def __hash__(self) -> int:
        return hash(self.normalized_name)