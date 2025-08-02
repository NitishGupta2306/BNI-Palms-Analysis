"""Command-line interface for BNI PALMS analysis."""

import sys
import argparse
from pathlib import Path

# Add src to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.application.use_cases.generate_reports import GenerateReportsUseCase
from src.application.use_cases.process_palms_data import ProcessPalmsDataUseCase
from src.application.use_cases.compare_matrices import CompareMatricesUseCase
from src.application.dto.report_request import ReportGenerationRequest, ProcessPalmsDataRequest, MatrixComparisonRequest
from src.infrastructure.config.settings import configure_app, get_settings
from src.infrastructure.config.paths import get_path_manager


def main():
    """Main CLI entry point."""
    # Initialize application
    configure_app()
    settings = get_settings()
    
    print(f"🔧 {settings.app_name} v{settings.version}")
    print("=" * 50)
    
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'generate':
            handle_generate_command(args)
        elif args.command == 'process':
            handle_process_command(args)
        elif args.command == 'compare':
            handle_compare_command(args)
        elif args.command == 'clean':
            handle_clean_command(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def create_argument_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="BNI PALMS Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate                    # Generate reports from uploaded files
  %(prog)s process --validate          # Process and validate PALMS data
  %(prog)s compare new.xlsx old.xlsx   # Compare two matrices
  %(prog)s clean --all                 # Clean all directories
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate reports command
    generate_parser = subparsers.add_parser('generate', help='Generate analysis reports')
    generate_parser.add_argument('--no-referral', action='store_true', 
                                help='Skip referral matrix generation')
    generate_parser.add_argument('--no-oto', action='store_true',
                                help='Skip one-to-one matrix generation')  
    generate_parser.add_argument('--no-combination', action='store_true',
                                help='Skip combination matrix generation')
    generate_parser.add_argument('--output-dir', type=Path,
                                help='Output directory for reports')
    
    # Process data command
    process_parser = subparsers.add_parser('process', help='Process PALMS data')
    process_parser.add_argument('--no-convert', action='store_true',
                               help='Skip XLS to XLSX conversion')
    process_parser.add_argument('--validate', action='store_true',
                               help='Validate data quality')
    process_parser.add_argument('--data-dir', type=Path,
                               help='Directory containing PALMS data files')
    process_parser.add_argument('--member-dir', type=Path,
                               help='Directory containing member files')
    
    # Compare matrices command
    compare_parser = subparsers.add_parser('compare', help='Compare two matrices')
    compare_parser.add_argument('new_matrix', type=Path, help='Path to new matrix file')
    compare_parser.add_argument('old_matrix', type=Path, help='Path to old matrix file')
    compare_parser.add_argument('--output', type=Path, help='Output file path')
    compare_parser.add_argument('--insights', action='store_true',
                               help='Generate detailed insights')
    
    # Clean directories command
    clean_parser = subparsers.add_parser('clean', help='Clean directories')
    clean_parser.add_argument('--all', action='store_true', help='Clean all directories')
    clean_parser.add_argument('--reports', action='store_true', help='Clean reports directory')
    clean_parser.add_argument('--uploads', action='store_true', help='Clean upload directories')
    
    return parser


def handle_generate_command(args):
    """Handle the generate reports command."""
    print("📊 Generating analysis reports...")
    
    path_manager = get_path_manager()
    use_case = GenerateReportsUseCase()
    
    # Get files from directories
    excel_files = path_manager.get_excel_files()
    member_files = path_manager.get_member_files()
    
    if not excel_files:
        print("❌ No Excel files found in the Excel files directory")
        print(f"   Please upload files to: {path_manager.excel_files_dir}")
        return
    
    if not member_files:
        print("❌ No member files found in the member names directory")
        print(f"   Please upload files to: {path_manager.member_names_dir}")
        return
    
    # Create request
    request = ReportGenerationRequest(
        excel_files=excel_files,
        member_files=member_files,
        output_directory=args.output_dir,
        include_referral_matrix=not args.no_referral,
        include_oto_matrix=not args.no_oto,
        include_combination_matrix=not args.no_combination
    )
    
    print(f"📁 Found {len(excel_files)} PALMS files and {len(member_files)} member files")
    
    # Execute request
    response = use_case.execute(request)
    
    # Display results
    if response.success:
        print("✅ Reports generated successfully!")
        print(f"📊 Generated {len(response.generated_files)} report files:")
        for file_path in response.generated_files:
            print(f"   • {file_path}")
        
        if response.execution_time_seconds:
            print(f"⏱️  Processing time: {response.execution_time_seconds:.2f} seconds")
    else:
        print("❌ Report generation failed!")
        for error in response.errors:
            print(f"   • {error}")
    
    # Display warnings
    for warning in response.warnings:
        print(f"⚠️  {warning}")


def handle_process_command(args):
    """Handle the process data command."""
    print("🔄 Processing PALMS data...")
    
    path_manager = get_path_manager()
    use_case = ProcessPalmsDataUseCase()
    
    # Determine directories
    data_dir = args.data_dir or path_manager.excel_files_dir
    member_dir = args.member_dir or path_manager.member_names_dir
    
    # Create request
    request = ProcessPalmsDataRequest(
        data_directory=data_dir,
        member_directory=member_dir,
        convert_xls_files=not args.no_convert,
        validate_data=args.validate
    )
    
    # Execute request
    response = use_case.execute(request)
    
    # Display results
    if response.success:
        print("✅ Data processing completed successfully!")
        print(f"👥 Members loaded: {response.members_count}")
        print(f"📈 Referrals found: {response.referrals_count}")
        print(f"🤝 One-to-ones found: {response.one_to_ones_count}")
        
        if response.converted_files:
            print(f"🔄 Files converted: {len(response.converted_files)}")
        
        if response.data_quality_report:
            quality = response.data_quality_report
            print(f"📊 Data quality score: {quality.get('overall_quality_score', 0):.1f}%")
        
        if response.execution_time_seconds:
            print(f"⏱️  Processing time: {response.execution_time_seconds:.2f} seconds")
    else:
        print("❌ Data processing failed!")
        for error in response.errors:
            print(f"   • {error}")
    
    # Display warnings
    for warning in response.warnings:
        print(f"⚠️  {warning}")


def handle_compare_command(args):
    """Handle the compare matrices command."""
    print("🔄 Comparing matrices...")
    
    use_case = CompareMatricesUseCase()
    
    # Validate input files
    if not args.new_matrix.exists():
        print(f"❌ New matrix file not found: {args.new_matrix}")
        return
    
    if not args.old_matrix.exists():
        print(f"❌ Old matrix file not found: {args.old_matrix}")
        return
    
    # Create request
    request = MatrixComparisonRequest(
        new_matrix_file=args.new_matrix,
        old_matrix_file=args.old_matrix,
        output_file=args.output
    )
    
    print(f"📊 Comparing {args.new_matrix.name} with {args.old_matrix.name}")
    
    # Execute request
    response = use_case.execute(request)
    
    # Display results
    if response.success:
        print("✅ Matrix comparison completed successfully!")
        if response.comparison_file:
            print(f"📄 Comparison file: {response.comparison_file}")
        
        if response.insights and args.insights:
            insights = response.insights
            print("\n📈 Comparison Insights:")
            print(f"   • Total members: {insights.get('total_members', 0)}")
            print(f"   • Improved: {insights.get('improved_members', 0)}")
            print(f"   • Declined: {insights.get('declined_members', 0)}")
            print(f"   • Unchanged: {insights.get('unchanged_members', 0)}")
        
        if response.execution_time_seconds:
            print(f"⏱️  Processing time: {response.execution_time_seconds:.2f} seconds")
    else:
        print("❌ Matrix comparison failed!")
        for error in response.errors:
            print(f"   • {error}")
    
    # Display warnings
    for warning in response.warnings:
        print(f"⚠️  {warning}")


def handle_clean_command(args):
    """Handle the clean directories command."""
    path_manager = get_path_manager()
    
    if args.all:
        print("🗑️ Cleaning all directories...")
        path_manager.cleanup_all_upload_directories()
        path_manager.cleanup_directory(path_manager.reports_dir)
        print("✅ All directories cleaned!")
    
    elif args.reports:
        print("🗑️ Cleaning reports directory...")
        path_manager.cleanup_directory(path_manager.reports_dir)
        print("✅ Reports directory cleaned!")
    
    elif args.uploads:
        print("🗑️ Cleaning upload directories...")
        path_manager.cleanup_all_upload_directories()
        print("✅ Upload directories cleaned!")
    
    else:
        print("❌ Please specify what to clean (--all, --reports, or --uploads)")


if __name__ == "__main__":
    main()