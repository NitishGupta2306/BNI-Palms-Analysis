"""Repository for managing PALMS data from Excel files."""

from pathlib import Path
from typing import List, Tuple, Optional
import pandas as pd
from openpyxl import load_workbook

from src.domain.models.member import Member
from src.domain.models.referral import Referral
from src.domain.models.one_to_one import OneToOne
from src.domain.models.tyfcb import TYFCB
from src.domain.exceptions.domain_exceptions import DataProcessingError
from src.shared.constants.app_constants import SlipType, ExcelColumns
from src.infrastructure.data.file_handlers.excel_handler import ExcelHandler
from src.infrastructure.data.file_handlers.file_converter import FileConverter
from src.infrastructure.config.paths import get_path_manager


class PalmsRepository:
    """Repository for accessing PALMS data from Excel files."""
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.file_converter = FileConverter()
        self.path_manager = get_path_manager()
    
    def extract_palms_data_from_file(self, file_path: Path, 
                                   members: List[Member]) -> Tuple[List[Referral], List[OneToOne], List[TYFCB]]:
        """
        Extract referrals, one-to-one, and TYFCB data from a PALMS Excel file.
        
        Args:
            file_path: Path to the PALMS Excel file
            members: List of valid members to match against
            
        Returns:
            Tuple of (referrals, one_to_ones, tyfcbs)
        """
        try:
            # Ensure file is in xlsx format
            xlsx_path = self.file_converter.ensure_xlsx_format(file_path)
            
            # Load the workbook using openpyxl for better control
            workbook = self.excel_handler.read_excel_with_openpyxl(xlsx_path)
            sheet = workbook.active
            
            referrals = []
            one_to_ones = []
            tyfcbs = []
            
            # Create a lookup dictionary for members
            member_lookup = {member.normalized_name: member for member in members}
            
            # Process each row in the sheet
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                try:
                    # Skip header row or empty rows
                    if row_idx == 1 or not any(row):
                        continue
                    
                    # Extract data from columns
                    giver_name = row[ExcelColumns.GIVER_NAME.value] if len(row) > ExcelColumns.GIVER_NAME.value else None
                    receiver_name = row[ExcelColumns.RECEIVER_NAME.value] if len(row) > ExcelColumns.RECEIVER_NAME.value else None
                    slip_type = row[ExcelColumns.SLIP_TYPE.value] if len(row) > ExcelColumns.SLIP_TYPE.value else None
                    
                    if not all([giver_name, receiver_name, slip_type]):
                        continue
                    
                    # Normalize names and find members
                    giver = self._find_member_by_name(str(giver_name), member_lookup)
                    receiver = self._find_member_by_name(str(receiver_name), member_lookup)
                    
                    if not giver or not receiver:
                        continue  # Skip if we can't find both members
                    
                    # Process based on slip type
                    if slip_type == SlipType.REFERRAL.value:
                        referral = Referral(giver=giver, receiver=receiver)
                        referrals.append(referral)
                        
                    elif slip_type == SlipType.ONE_TO_ONE.value:
                        one_to_one = OneToOne(member1=giver, member2=receiver)
                        one_to_ones.append(one_to_one)
                
                except Exception as e:
                    # Log the error but continue processing other rows
                    print(f"Warning: Error processing row {row_idx} in {file_path}: {e}")
                    continue
            
            return referrals, one_to_ones
            
        except Exception as e:
            raise DataProcessingError(f"Error extracting PALMS data from {file_path}: {str(e)}")
    
    def load_all_palms_data(self, members: List[Member]) -> Tuple[List[Referral], List[OneToOne]]:
        """
        Load all PALMS data from the Excel files directory.
        
        Args:
            members: List of valid members to match against
            
        Returns:
            Tuple of (all_referrals, all_one_to_ones)
        """
        try:
            all_referrals = []
            all_one_to_ones = []
            
            excel_files = self.path_manager.get_excel_files()
            
            if not excel_files:
                raise DataProcessingError("No Excel files found in the Excel files directory")
            
            for file_path in excel_files:
                try:
                    referrals, one_to_ones = self.extract_palms_data_from_file(file_path, members)
                    all_referrals.extend(referrals)
                    all_one_to_ones.extend(one_to_ones)
                    
                except DataProcessingError as e:
                    print(f"Warning: Error processing PALMS file {file_path}: {e}")
                    continue
            
            return all_referrals, all_one_to_ones
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error loading all PALMS data: {str(e)}")
    
    def _find_member_by_name(self, name: str, member_lookup: dict) -> Optional[Member]:
        """
        Find a member by name using the lookup dictionary.
        
        Args:
            name: Name to search for
            member_lookup: Dictionary mapping normalized names to Member objects
            
        Returns:
            Member object if found, None otherwise
        """
        try:
            if not name:
                return None
            
            # Normalize the name
            normalized_name = name.replace(" ", "").lower()
            
            # Direct lookup
            return member_lookup.get(normalized_name)
            
        except Exception:
            return None
    
    def get_palms_data_statistics(self, referrals: List[Referral], 
                                one_to_ones: List[OneToOne]) -> dict:
        """
        Get statistics about PALMS data.
        
        Args:
            referrals: List of referrals
            one_to_ones: List of one-to-one meetings
            
        Returns:
            Dictionary with statistics
        """
        try:
            # Get unique members involved
            referral_members = set()
            for referral in referrals:
                referral_members.add(referral.giver)
                referral_members.add(referral.receiver)
            
            oto_members = set()
            for oto in one_to_ones:
                oto_members.add(oto.member1)
                oto_members.add(oto.member2)
            
            return {
                'total_referrals': len(referrals),
                'total_one_to_ones': len(one_to_ones),
                'unique_referral_members': len(referral_members),
                'unique_oto_members': len(oto_members),
                'all_active_members': len(referral_members.union(oto_members)),
                'referral_givers': len(set(r.giver for r in referrals)),
                'referral_receivers': len(set(r.receiver for r in referrals)),
                'unique_referral_pairs': len(set((r.giver, r.receiver) for r in referrals)),
                'unique_oto_pairs': len(set((oto.member1, oto.member2) for oto in one_to_ones))
            }
            
        except Exception as e:
            raise DataProcessingError(f"Error calculating PALMS statistics: {str(e)}")
    
    def filter_referrals_by_member(self, referrals: List[Referral], 
                                 member: Member) -> Tuple[List[Referral], List[Referral]]:
        """
        Filter referrals by a specific member.
        
        Args:
            referrals: List of all referrals
            member: Member to filter by
            
        Returns:
            Tuple of (referrals_given, referrals_received)
        """
        try:
            referrals_given = [r for r in referrals if r.giver == member]
            referrals_received = [r for r in referrals if r.receiver == member]
            
            return referrals_given, referrals_received
            
        except Exception as e:
            raise DataProcessingError(f"Error filtering referrals by member: {str(e)}")
    
    def filter_one_to_ones_by_member(self, one_to_ones: List[OneToOne], 
                                   member: Member) -> List[OneToOne]:
        """
        Filter one-to-one meetings by a specific member.
        
        Args:
            one_to_ones: List of all one-to-one meetings
            member: Member to filter by
            
        Returns:
            List of one-to-one meetings involving the member
        """
        try:
            return [oto for oto in one_to_ones if oto.involves_member(member)]
            
        except Exception as e:
            raise DataProcessingError(f"Error filtering one-to-ones by member: {str(e)}")
    
    def validate_palms_file_format(self, file_path: Path) -> bool:
        """
        Validate that a file has the expected PALMS format.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file appears to be in PALMS format
        """
        try:
            # First check if it's a valid Excel file
            if not self.excel_handler.validate_excel_file(file_path):
                print(f"Debug: Excel validation failed for {file_path}")
                return False
            
            # Convert to xlsx if needed for better compatibility
            try:
                xlsx_path = self.file_converter.ensure_xlsx_format(file_path, delete_original=False)
                
                # Read first few rows to check structure
                df = self.excel_handler.read_excel_to_dataframe(xlsx_path, nrows=10)
                
                # Basic validation: check if we have data and at least 2 columns
                if df.empty:
                    print(f"Debug: File {file_path} is empty")
                    return False
                
                if df.shape[1] < 2:
                    print(f"Debug: File {file_path} has less than 2 columns")
                    return False
                
                # More flexible validation - just check if file can be read
                # PALMS files should have some data in the first few rows
                non_empty_rows = df.dropna(how='all')
                if len(non_empty_rows) == 0:
                    print(f"Debug: File {file_path} has no data rows")
                    return False
                
                print(f"Debug: File {file_path} passed validation")
                return True
                
            except Exception as e:
                print(f"Debug: Error during conversion/validation for {file_path}: {e}")
                return False
            
        except Exception as e:
            print(f"Debug: General validation error for {file_path}: {e}")
            return False