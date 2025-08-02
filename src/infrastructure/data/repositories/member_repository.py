"""Repository for managing member data."""

from pathlib import Path
from typing import List, Optional
import pandas as pd

from src.domain.models.member import Member
from src.domain.exceptions.domain_exceptions import DataProcessingError, MemberValidationError
from src.infrastructure.data.file_handlers.excel_handler import ExcelHandler
from src.infrastructure.data.file_handlers.file_converter import FileConverter
from src.infrastructure.config.paths import get_path_manager


class MemberRepository:
    """Repository for accessing and managing member data."""
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.file_converter = FileConverter()
        self.path_manager = get_path_manager()
    
    def extract_members_from_excel(self, file_path: Path) -> List[Member]:
        """
        Extract member data from an Excel file.
        
        Args:
            file_path: Path to the Excel file containing member data
            
        Returns:
            List of Member objects
        """
        try:
            # Ensure file is in xlsx format
            xlsx_path = self.file_converter.ensure_xlsx_format(file_path)
            
            # Read the Excel file
            df = self.excel_handler.read_excel_to_dataframe(
                xlsx_path,
                usecols=[0, 1],  # Read first and last names
                dtype=str,
                header=0
            )
            
            # Remove empty rows
            df.dropna(how="all", inplace=True)
            
            # Combine first and last names
            df["Full Name"] = (
                df.iloc[:, 0].str.strip() + " " + df.iloc[:, 1].str.strip()
            )
            
            # Create Member objects
            members = []
            for full_name in df["Full Name"].dropna():
                if full_name.strip():  # Skip empty names
                    try:
                        member = Member.from_full_name(full_name.strip())
                        members.append(member)
                    except Exception as e:
                        # Log the error but continue processing
                        print(f"Warning: Could not create member from name '{full_name}': {e}")
                        continue
            
            return members
            
        except Exception as e:
            raise DataProcessingError(f"Error extracting members from {file_path}: {str(e)}")
    
    def load_members_from_directory(self) -> List[Member]:
        """
        Load all members from files in the member names directory.
        
        Returns:
            List of all Member objects found in the directory
        """
        try:
            all_members = []
            member_files = self.path_manager.get_member_files()
            
            if not member_files:
                raise DataProcessingError("No member files found in the member names directory")
            
            for file_path in member_files:
                try:
                    members = self.extract_members_from_excel(file_path)
                    all_members.extend(members)
                except DataProcessingError as e:
                    print(f"Warning: Error processing member file {file_path}: {e}")
                    continue
            
            # Remove duplicates based on normalized names
            unique_members = []
            seen_names = set()
            
            for member in all_members:
                if member.normalized_name not in seen_names:
                    unique_members.append(member)
                    seen_names.add(member.normalized_name)
            
            return sorted(unique_members, key=lambda m: m.normalized_name)
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error loading members from directory: {str(e)}")
    
    def validate_member(self, member: Member) -> bool:
        """
        Validate a member object.
        
        Args:
            member: Member object to validate
            
        Returns:
            True if valid, raises exception if invalid
        """
        try:
            if not member.first_name and not member.last_name:
                raise MemberValidationError("Member must have at least a first or last name")
            
            if not member.normalized_name:
                raise MemberValidationError("Member normalized name cannot be empty")
            
            return True
            
        except Exception as e:
            if isinstance(e, MemberValidationError):
                raise
            raise MemberValidationError(f"Error validating member: {str(e)}")
    
    def find_member_by_name(self, members: List[Member], name: str) -> Optional[Member]:
        """
        Find a member by their name (flexible matching).
        
        Args:
            members: List of members to search in
            name: Name to search for
            
        Returns:
            Member object if found, None otherwise
        """
        try:
            if not name:
                return None
            
            # Normalize the search name
            normalized_search = name.replace(" ", "").lower()
            
            # Look for exact normalized name match
            for member in members:
                if member.normalized_name == normalized_search:
                    return member
            
            # If no exact match, try partial matches
            for member in members:
                if (normalized_search in member.normalized_name or 
                    member.normalized_name in normalized_search):
                    return member
            
            return None
            
        except Exception as e:
            print(f"Warning: Error finding member by name '{name}': {e}")
            return None
    
    def get_member_statistics(self, members: List[Member]) -> dict:
        """
        Get statistics about a list of members.
        
        Args:
            members: List of members
            
        Returns:
            Dictionary with member statistics
        """
        try:
            return {
                'total_members': len(members),
                'unique_first_names': len(set(m.first_name for m in members if m.first_name)),
                'unique_last_names': len(set(m.last_name for m in members if m.last_name)),
                'members_with_both_names': len([m for m in members if m.first_name and m.last_name]),
                'members_with_only_first_name': len([m for m in members if m.first_name and not m.last_name]),
                'members_with_only_last_name': len([m for m in members if not m.first_name and m.last_name])
            }
            
        except Exception as e:
            raise DataProcessingError(f"Error calculating member statistics: {str(e)}")
    
    def export_members_to_excel(self, members: List[Member], file_path: Path) -> None:
        """
        Export members to an Excel file.
        
        Args:
            members: List of members to export
            file_path: Path where to save the Excel file
        """
        try:
            data = []
            for member in members:
                data.append({
                    'First Name': member.first_name,
                    'Last Name': member.last_name,
                    'Full Name': member.full_name,
                    'Normalized Name': member.normalized_name
                })
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
        except Exception as e:
            raise DataProcessingError(f"Error exporting members to Excel: {str(e)}")