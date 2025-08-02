#!/usr/bin/env python3
"""
Test script to verify TYFCB export functionality.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.domain.models.member import Member
from src.domain.models.tyfcb import TYFCB
from src.shared.utils.export_utils import ExportService

def test_tyfcb_export():
    """Test TYFCB export functionality."""
    print("🧪 Testing TYFCB Export")
    print("=" * 40)
    
    try:
        # Create test data
        member1 = Member(first_name="John", last_name="Doe")
        member2 = Member(first_name="Jane", last_name="Smith")
        member3 = Member(first_name="Bob", last_name="Johnson")
        
        members = [member1, member2, member3]
        
        tyfcbs = [
            TYFCB(giver=member1, receiver=member2, amount=1000.0, within_chapter=True),
            TYFCB(giver=member2, receiver=member3, amount=2500.0, within_chapter=False),
            TYFCB(giver=member3, receiver=member1, amount=750.0, within_chapter=True),
        ]
        
        print(f"✅ Created test data: {len(members)} members, {len(tyfcbs)} TYFCB entries")
        
        # Test export
        export_service = ExportService()
        test_file = Path("test_tyfcb_export.xlsx")
        
        print(f"📊 Exporting to: {test_file}")
        export_service.export_tyfcb_data(members, tyfcbs, test_file)
        
        if test_file.exists():
            file_size = test_file.stat().st_size
            print(f"✅ Export successful! File created: {test_file} ({file_size} bytes)")
            
            # Clean up
            test_file.unlink()
            print("🗑️ Test file cleaned up")
            
            return True
        else:
            print("❌ Export failed - file not created")
            return False
            
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 TYFCB Export Test")
    print("=" * 30)
    
    success = test_tyfcb_export()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 TYFCB export test PASSED!")
        print("The export functionality is working correctly.")
    else:
        print("❌ TYFCB export test FAILED!")
        print("There may be an issue with the export functionality.")