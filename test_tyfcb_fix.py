#!/usr/bin/env python3
"""
Test script to verify TYFCB extraction fix.

This script creates a sample Excel file with TYFCB data to test the extraction.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from src.shared.constants.app_constants import SlipType
from src.infrastructure.data.repositories.palms_repository import PalmsRepository
from src.domain.models.member import Member

def create_test_excel_file():
    """Create a test Excel file with various slip type formats."""
    
    test_data = [
        ["Giver Name", "Receiver Name", "Slip Type", "Date", "Amount", "Details", "Notes"],
        ["John Doe", "Jane Smith", "TYFCB", "2024-01-01", "100.00", "", "Within chapter"],
        ["Jane Smith", "Bob Johnson", "TYFCB ", "2024-01-02", "250.50", "Outside chapter", "With trailing space"],
        ["Bob Johnson", "Alice Brown", "tyfcb", "2024-01-03", "75.25", "", "Lowercase"],
        ["Alice Brown", "John Doe", "TY FCB", "2024-01-04", "300.00", "", "With space"],
        ["John Doe", "Jane Smith", "Referral", "2024-01-05", "", "", "Normal referral"],
        ["Jane Smith", "Bob Johnson", "One to One", "2024-01-06", "", "", "OTO meeting"],
        ["Bob Johnson", "Alice Brown", "THANK YOU FCB", "2024-01-07", "500.00", "Big deal", "Full text"],
        ["Alice Brown", "John Doe", "TYFCB", "2024-01-08", "0", "", "Zero amount - should be skipped"],
        ["John Doe", "Jane Smith", "TYFCB", "2024-01-09", "", "", "Empty amount - should be skipped"],
    ]
    
    df = pd.DataFrame(test_data[1:], columns=test_data[0])
    
    test_file_path = Path("test_tyfcb_data.xlsx")
    df.to_excel(test_file_path, index=False)
    
    print(f"Created test Excel file: {test_file_path}")
    return test_file_path

def create_test_members():
    """Create test member objects."""
    return [
        Member("John", "Doe"),
        Member("Jane", "Smith"),
        Member("Bob", "Johnson"),
        Member("Alice", "Brown")
    ]

def test_tyfcb_extraction():
    """Test TYFCB extraction with the improved code."""
    
    # Create test files
    test_file = create_test_excel_file()
    members = create_test_members()
    
    try:
        # Test the extraction
        repository = PalmsRepository()
        referrals, one_to_ones, tyfcbs = repository.extract_palms_data_from_file(test_file, members)
        
        print("\n" + "="*60)
        print("TYFCB EXTRACTION TEST RESULTS")
        print("="*60)
        
        print(f"\nReferrals found: {len(referrals)}")
        for ref in referrals:
            print(f"  - {ref.giver.name} -> {ref.receiver.name}")
        
        print(f"\nOne-to-Ones found: {len(one_to_ones)}")
        for oto in one_to_ones:
            print(f"  - {oto.member1.name} <-> {oto.member2.name}")
        
        print(f"\nTYFCBs found: {len(tyfcbs)}")
        for tyfcb in tyfcbs:
            print(f"  - {tyfcb.giver.name} -> {tyfcb.receiver.name}: ${tyfcb.amount:.2f} (within_chapter: {tyfcb.within_chapter})")
        
        print(f"\nExpected TYFCB count: 6 (excluding zero/empty amounts)")
        print(f"Actual TYFCB count: {len(tyfcbs)}")
        
        if len(tyfcbs) == 6:
            print("✅ SUCCESS: All expected TYFCBs were extracted!")
        else:
            print("❌ ISSUE: Expected 6 TYFCBs but found " + str(len(tyfcbs)))
        
    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            print(f"\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    test_tyfcb_extraction()