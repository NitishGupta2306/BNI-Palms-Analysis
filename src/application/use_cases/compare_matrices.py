"""Use case for comparing matrices and generating comparison reports."""

import time
from pathlib import Path
from typing import Optional, List

from src.application.dto.report_request import MatrixComparisonRequest
from src.application.dto.analysis_response import MatrixComparisonResponse
from src.domain.services.comparison_service import ComparisonService
from src.domain.exceptions.domain_exceptions import DataProcessingError
from src.infrastructure.config.paths import get_path_manager
from src.shared.constants.app_constants import FileNames


class CompareMatricesUseCase:
    """Use case for comparing matrices and analyzing changes over time."""
    
    def __init__(self):
        self.comparison_service = ComparisonService()
        self.path_manager = get_path_manager()
    
    def execute(self, request: MatrixComparisonRequest) -> MatrixComparisonResponse:
        """
        Execute the matrix comparison use case.
        
        Args:
            request: Matrix comparison request
            
        Returns:
            Comparison response with results and insights
        """
        start_time = time.time()
        response = MatrixComparisonResponse(success=True)
        
        try:
            # Validate request
            request.validate()
            
            # Generate comparison report
            comparison_df = self.comparison_service.generate_comparison_report(
                request.new_matrix_file,
                request.old_matrix_file
            )
            
            # Determine output file path
            output_file = request.output_file or self._get_default_output_path()
            
            # Export comparison to Excel
            self.comparison_service.export_comparison_to_excel(
                comparison_df,
                output_file
            )
            response.comparison_file = output_file
            
            # Load matrices to get headers for insights
            new_df, new_headers = self.comparison_service.load_matrix_from_excel(
                request.new_matrix_file
            )
            
            # Generate insights
            if new_headers:
                insights = self.comparison_service.get_comparison_insights(
                    comparison_df, new_headers
                )
                response.insights = insights
            else:
                response.add_warning("Headers not found - insights may be limited")
            
        except Exception as e:
            response.add_error(f"Matrix comparison failed: {str(e)}")
        
        finally:
            response.execution_time_seconds = time.time() - start_time
        
        return response
    
    def compare_from_directories(self) -> MatrixComparisonResponse:
        """
        Compare matrices from the new and old matrix directories.
        
        Returns:
            Comparison response
        """
        try:
            # Get files from the directories
            new_matrix_files = self.path_manager.get_new_matrix_files()
            old_matrix_files = self.path_manager.get_old_matrix_files()
            
            if not new_matrix_files:
                response = MatrixComparisonResponse(success=False)
                response.add_error("No files found in new matrix directory")
                return response
            
            if not old_matrix_files:
                response = MatrixComparisonResponse(success=False)
                response.add_error("No files found in old matrix directory")
                return response
            
            # Use the first file from each directory
            new_matrix_file = new_matrix_files[0]
            old_matrix_file = old_matrix_files[0]
            
            # Create and execute request
            request = MatrixComparisonRequest(
                new_matrix_file=new_matrix_file,
                old_matrix_file=old_matrix_file
            )
            
            return self.execute(request)
            
        except Exception as e:
            response = MatrixComparisonResponse(success=False)
            response.add_error(f"Directory comparison failed: {str(e)}")
            return response
    
    def compare_specific_files(self, new_file_path: Path, 
                             old_file_path: Path,
                             output_file_path: Optional[Path] = None) -> MatrixComparisonResponse:
        """
        Compare two specific matrix files.
        
        Args:
            new_file_path: Path to the new matrix file
            old_file_path: Path to the old matrix file
            output_file_path: Optional output file path
            
        Returns:
            Comparison response
        """
        try:
            request = MatrixComparisonRequest(
                new_matrix_file=new_file_path,
                old_matrix_file=old_file_path,
                output_file=output_file_path
            )
            
            return self.execute(request)
            
        except Exception as e:
            response = MatrixComparisonResponse(success=False)
            response.add_error(f"File comparison failed: {str(e)}")
            return response
    
    def _get_default_output_path(self) -> Path:
        """Get the default output path for comparison files."""
        return self.path_manager.get_report_path(FileNames.COMBINATION_COMPARISON)
    
    def generate_comparison_insights_report(self, response: MatrixComparisonResponse) -> dict:
        """
        Generate a detailed insights report from a comparison response.
        
        Args:
            response: Comparison response
            
        Returns:
            Dictionary with detailed insights report
        """
        try:
            if not response.success or not response.insights:
                return {
                    'error': 'Comparison was not successful or insights not available',
                    'success': response.success,
                    'errors': response.errors
                }
            
            insights = response.insights
            
            # Generate detailed report
            report = {
                'executive_summary': self._generate_executive_summary(insights),
                'member_performance': self._analyze_member_performance(insights),
                'trend_analysis': self._analyze_trends(insights),
                'recommendations': self._generate_recommendations(insights),
                'raw_insights': insights
            }
            
            return report
            
        except Exception as e:
            return {
                'error': f"Failed to generate insights report: {str(e)}",
                'success': False
            }
    
    def _generate_executive_summary(self, insights: dict) -> dict:
        """Generate executive summary from insights."""
        try:
            summary = {
                'total_members_analyzed': insights.get('total_members', 0),
                'overall_performance': 'Unknown',
                'key_metrics': {}
            }
            
            # Determine overall performance
            improved = insights.get('improved_members', 0)
            declined = insights.get('declined_members', 0)
            total = insights.get('total_members', 0)
            
            if total > 0:
                improvement_rate = improved / total
                decline_rate = declined / total
                
                if improvement_rate > decline_rate:
                    summary['overall_performance'] = 'Improving'
                elif decline_rate > improvement_rate:
                    summary['overall_performance'] = 'Declining'
                else:
                    summary['overall_performance'] = 'Stable'
                
                summary['key_metrics'] = {
                    'improvement_rate': f"{improvement_rate:.1%}",
                    'decline_rate': f"{decline_rate:.1%}",
                    'stability_rate': f"{(total - improved - declined) / total:.1%}"
                }
            
            return summary
            
        except Exception as e:
            return {'error': f"Failed to generate executive summary: {str(e)}"}
    
    def _analyze_member_performance(self, insights: dict) -> dict:
        """Analyze member performance from insights."""
        try:
            performance = {
                'top_performers': [],
                'needs_attention': [],
                'consistent_performers': []
            }
            
            # Get top improvements and declines
            improvements = insights.get('biggest_improvements', [])
            declines = insights.get('biggest_declines', [])
            
            # Top performers (biggest improvements)
            performance['top_performers'] = [
                {
                    'member': member,
                    'improvement': change,
                    'category': 'High Growth'
                }
                for member, change in improvements[:3] if change > 0
            ]
            
            # Members needing attention (biggest declines)
            performance['needs_attention'] = [
                {
                    'member': member,
                    'decline': abs(change),
                    'category': 'Needs Support'
                }
                for member, change in declines[:3] if change < 0
            ]
            
            # Consistent performers (no change)
            unchanged = insights.get('unchanged_members', 0)
            total = insights.get('total_members', 0)
            
            if total > 0:
                performance['consistency_rate'] = f"{unchanged / total:.1%}"
            
            return performance
            
        except Exception as e:
            return {'error': f"Failed to analyze member performance: {str(e)}"}
    
    def _analyze_trends(self, insights: dict) -> dict:
        """Analyze trends from insights."""
        try:
            trends = {
                'overall_direction': 'Unknown',
                'engagement_trend': 'Unknown',
                'participation_change': {}
            }
            
            # Determine overall direction
            summary_stats = insights.get('summary_stats', {})
            avg_change = summary_stats.get('average_change', 0)
            total_change = summary_stats.get('total_change', 0)
            
            if avg_change > 0:
                trends['overall_direction'] = 'Positive Growth'
            elif avg_change < 0:
                trends['overall_direction'] = 'Declining Activity'
            else:
                trends['overall_direction'] = 'Stable Performance'
            
            trends['metrics'] = {
                'average_change_per_member': avg_change,
                'total_chapter_change': total_change,
                'improvement_rate': summary_stats.get('improvement_rate', 0),
                'decline_rate': summary_stats.get('decline_rate', 0)
            }
            
            return trends
            
        except Exception as e:
            return {'error': f"Failed to analyze trends: {str(e)}"}
    
    def _generate_recommendations(self, insights: dict) -> List[str]:
        """Generate recommendations based on insights."""
        try:
            recommendations = []
            
            # Analyze improvement and decline rates
            summary_stats = insights.get('summary_stats', {})
            improvement_rate = summary_stats.get('improvement_rate', 0)
            decline_rate = summary_stats.get('decline_rate', 0)
            
            if decline_rate > 0.3:  # More than 30% declining
                recommendations.append(
                    "High decline rate detected. Consider implementing additional member "
                    "engagement initiatives and one-to-one coaching sessions."
                )
            
            if improvement_rate < 0.2:  # Less than 20% improving
                recommendations.append(
                    "Low improvement rate. Consider recognizing and rewarding active members "
                    "to encourage better participation."
                )
            
            # Analyze biggest declines
            declines = insights.get('biggest_declines', [])
            if len(declines) >= 3 and all(change < -5 for _, change in declines[:3]):
                recommendations.append(
                    "Several members show significant decline in activity. Consider "
                    "personalized outreach and support programs."
                )
            
            # Analyze improvements
            improvements = insights.get('biggest_improvements', [])
            if len(improvements) >= 3 and all(change > 5 for _, change in improvements[:3]):
                recommendations.append(
                    "Excellent growth from top performers! Consider having them mentor "
                    "other members or share their best practices."
                )
            
            # General recommendations
            unchanged = insights.get('unchanged_members', 0)
            total = insights.get('total_members', 0)
            
            if total > 0 and unchanged / total > 0.5:
                recommendations.append(
                    "Many members show no change in activity. Consider implementing "
                    "new engagement strategies or training programs."
                )
            
            if not recommendations:
                recommendations.append(
                    "Overall performance is stable. Continue current strategies and "
                    "monitor for emerging trends."
                )
            
            return recommendations
            
        except Exception as e:
            return [f"Failed to generate recommendations: {str(e)}"]