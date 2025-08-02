#!/usr/bin/env python3
"""
Legacy main.py entry point for BNI PALMS Analysis.

This file maintains backward compatibility while using the new architecture.
For the new CLI interface, use: python -m src.presentation.cli.main
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.application.use_cases.generate_reports import GenerateReportsUseCase
from src.infrastructure.config.settings import configure_app


def main():
    """Main entry point using the new architecture."""
    print("🔧 BNI PALMS Analysis - Legacy Mode")
    print("=" * 40)
    
    try:
        # Initialize the application
        configure_app()
        
        # Use the new architecture to generate reports
        use_case = GenerateReportsUseCase()
        
        print("📊 Generating reports from uploaded files...")
        response = use_case.generate_quick_report()
        
        if response.success:
            print("✅ Reports generated successfully!")
            print("📄 Generated files:")
            for file_path in response.generated_files:
                print(f"   • {file_path.name}")
            
            if response.execution_time_seconds:
                print(f"⏱️  Processing time: {response.execution_time_seconds:.2f} seconds")
        else:
            print("❌ Report generation failed!")
            for error in response.errors:
                print(f"   • {error}")
        
        # Display warnings
        for warning in response.warnings:
            print(f"⚠️  {warning}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 For more features, use the Streamlit web interface:")
        print("   streamlit run streamlit_app.py")
        sys.exit(1)


if __name__ == "__main__":
    main()

