#!/usr/bin/env python3
"""
Test script to verify TYFCB slip type normalization is working correctly.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.infrastructure.data.repositories.palms_repository import PalmsRepository
from src.shared.constants.app_constants import SlipType

def test_tyfcb_normalization():
    """Test the TYFCB slip type normalization."""
    print("🧪 Testing TYFCB Slip Type Normalization")
    print("=" * 50)
    
    repo = PalmsRepository()
    
    # Test cases for TYFCB variations
    test_cases = [
        "TYFCB",           # Exact match
        "tyfcb",           # Lowercase
        "Tyfcb",           # Mixed case
        "TYFCB ",          # With trailing space
        " TYFCB",          # With leading space
        " TYFCB ",         # With both spaces
        "TY FCB",          # With space in middle
        "TY-FCB",          # With hyphen
        "THANK YOU FCB",   # Full variation
        "THANK YOU FOR CLOSE BUSINESS",  # Very full variation
    ]
    
    print(f"Expected normalized value: {repr(SlipType.TYFCB.value)}")
    print()
    
    success_count = 0
    for test_case in test_cases:
        result = repo._normalize_slip_type(test_case)
        is_success = result == SlipType.TYFCB.value
        success_count += is_success
        
        status = "✅" if is_success else "❌"
        print(f"{status} {repr(test_case):30} -> {repr(result)}")
    
    print()
    print(f"📊 Results: {success_count}/{len(test_cases)} test cases passed")
    
    if success_count == len(test_cases):
        print("🎉 All TYFCB normalization tests passed!")
        return True
    else:
        print("⚠️  Some TYFCB normalization tests failed!")
        return False

def test_other_slip_types():
    """Test that other slip types still work correctly."""
    print("\n🧪 Testing Other Slip Types")
    print("=" * 50)
    
    repo = PalmsRepository()
    
    test_cases = [
        # Referral variations
        ("Referral", SlipType.REFERRAL.value),
        ("referral", SlipType.REFERRAL.value),
        ("REFERRAL", SlipType.REFERRAL.value),
        ("REF", SlipType.REFERRAL.value),
        
        # One-to-One variations
        ("One to One", SlipType.ONE_TO_ONE.value),
        ("one to one", SlipType.ONE_TO_ONE.value),
        ("ONE TO ONE", SlipType.ONE_TO_ONE.value),
        ("One-to-One", SlipType.ONE_TO_ONE.value),
        ("1-to-1", SlipType.ONE_TO_ONE.value),
        ("OTO", SlipType.ONE_TO_ONE.value),
        
        # Invalid cases
        ("Invalid Type", None),
        ("", None),
        ("   ", None),
    ]
    
    success_count = 0
    for test_input, expected in test_cases:
        result = repo._normalize_slip_type(test_input)
        is_success = result == expected
        success_count += is_success
        
        status = "✅" if is_success else "❌"
        print(f"{status} {repr(test_input):20} -> {repr(result):20} (expected: {repr(expected)})")
    
    print()
    print(f"📊 Results: {success_count}/{len(test_cases)} test cases passed")
    
    if success_count == len(test_cases):
        print("🎉 All other slip type tests passed!")
        return True
    else:
        print("⚠️  Some other slip type tests failed!")
        return False

if __name__ == "__main__":
    print("🔧 TYFCB Slip Type Normalization Test Suite")
    print("=" * 60)
    
    # Run tests
    tyfcb_success = test_tyfcb_normalization()
    other_success = test_other_slip_types()
    
    print("\n" + "=" * 60)
    if tyfcb_success and other_success:
        print("🎉 ALL TESTS PASSED! TYFCB normalization is working correctly.")
        print("\nYour TYFCB data should now be extracted properly.")
        print("Try running your Streamlit app again to see TYFCB data.")
    else:
        print("❌ SOME TESTS FAILED! There may be issues with slip type normalization.")
        print("\nPlease check the implementation in palms_repository.py")