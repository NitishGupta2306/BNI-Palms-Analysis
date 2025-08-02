#!/usr/bin/env python3
"""
Test script to verify TYFCB detection with actual data.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.application.use_cases.generate_reports import GenerateReportsUseCase
from src.application.dto.report_request import ReportGenerationRequest

def test_tyfcb_detection():
    """Test TYFCB detection with actual data files."""
    print("🔍 Testing TYFCB Detection")
    print("=" * 40)
    
    try:
        # Initialize the use case
        use_case = GenerateReportsUseCase()
        
        print("📁 Using quick report to test with existing files...")
        
        # Generate a quick report using existing files
        response = use_case.generate_quick_report()
        
        if not response.success:
            print("❌ Report generation failed:")
            for error in response.errors:
                print(f"   • {error}")
            return False
        
        # Check the results
        report = response.report
        
        print(f"📊 Analysis Results:")
        print(f"   • Total Members: {len(report.all_members)}")
        print(f"   • Total Referrals: {len(report.referrals)}")
        print(f"   • Total One-to-Ones: {len(report.one_to_ones)}")
        print(f"   • Total TYFCBs: {len(report.tyfcbs)}")
        
        if report.tyfcbs:
            print(f"\n✅ TYFCB Detection SUCCESS!")
            print(f"   Found {len(report.tyfcbs)} TYFCB entries:")
            
            total_within = 0
            total_outside = 0
            
            for i, tyfcb in enumerate(report.tyfcbs[:5], 1):  # Show first 5
                chapter_type = "within chapter" if tyfcb.within_chapter else "outside chapter"
                giver_name = tyfcb.giver.full_name if tyfcb.giver else "Unknown"
                print(f"   {i}. {giver_name} -> {tyfcb.receiver.full_name}: ${tyfcb.amount:.2f} ({chapter_type})")
                
                if tyfcb.within_chapter:
                    total_within += tyfcb.amount
                else:
                    total_outside += tyfcb.amount
            
            if len(report.tyfcbs) > 5:
                print(f"   ... and {len(report.tyfcbs) - 5} more entries")
            
            print(f"\n💰 TYFCB Summary:")
            print(f"   • Total within chapter: ${total_within:.2f}")
            print(f"   • Total outside chapter: ${total_outside:.2f}")
            print(f"   • Grand total: ${total_within + total_outside:.2f}")
            
        else:
            print("❌ No TYFCB entries detected!")
            print("   This could mean:")
            print("   • No TYFCB data in the Excel files")
            print("   • TYFCB entries don't match expected format")
            print("   • Validation logic is still incorrect")
        
        # Check what files were generated
        print(f"\n📁 Generated Files:")
        for file_path in response.generated_files:
            print(f"   • {file_path}")
        
        # Show any processing errors
        if response.errors:
            print(f"\n⚠️ Processing Errors:")
            for error in response.errors:
                print(f"   • {error}")
        
        return len(report.tyfcbs) > 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TYFCB Detection Test")
    print("=" * 30)
    
    success = test_tyfcb_detection()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 TYFCB detection test PASSED!")
        print("TYFCB entries were successfully detected and processed.")
    else:
        print("❌ TYFCB detection test FAILED!")
        print("No TYFCB entries were detected. Check the Excel files and validation logic.")