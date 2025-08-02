"""Service for handling matrix comparisons and trend analysis."""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from pathlib import Path

from src.domain.models.member import Member
from src.domain.models.analysis_result import AnalysisMatrix, MatrixType, ComparisonResult
from src.domain.exceptions.domain_exceptions import DataProcessingError
from src.infrastructure.data.file_handlers.excel_handler import ExcelHandler
from src.shared.constants.app_constants import MatrixHeaders


class ComparisonService:
    """Service for comparing matrices and analyzing trends."""
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
    
    def load_matrix_from_excel(self, file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Tuple[int, int]]]:
        """
        Load a matrix from an Excel file and find header locations.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Tuple of (dataframe, header_locations)
        """
        try:
            # Read the Excel file without headers
            df = self.excel_handler.read_excel_to_dataframe(file_path, header=None)
            
            # Find header locations
            header_locations = self._find_header_locations(df)
            
            if not header_locations:
                raise DataProcessingError(f"Required headers not found in {file_path}")
            
            return df, header_locations
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error loading matrix from Excel: {str(e)}")
    
    def _find_header_locations(self, df: pd.DataFrame) -> Dict[str, Tuple[int, int]]:
        """
        Find the locations of required headers in a dataframe.
        
        Args:
            df: DataFrame to search
            
        Returns:
            Dictionary mapping header names to (row, col) positions
        """
        try:
            required_headers = [
                MatrixHeaders.NEITHER,
                MatrixHeaders.OTO_ONLY,
                MatrixHeaders.REFERRAL_ONLY,
                MatrixHeaders.OTO_AND_REFERRAL
            ]
            
            header_locations = {}
            
            # Search through the dataframe for each header
            for row_idx in range(len(df)):
                for col_idx in range(len(df.columns)):
                    cell_value = df.iloc[row_idx, col_idx]
                    if pd.notna(cell_value) and str(cell_value) in required_headers:
                        header_locations[str(cell_value)] = (row_idx, col_idx)
            
            # Return only if all headers are found
            return header_locations if len(header_locations) == 4 else {}
            
        except Exception as e:
            raise DataProcessingError(f"Error finding header locations: {str(e)}")
    
    def add_current_referral_column(self, df: pd.DataFrame, 
                                  header_locations: Dict[str, Tuple[int, int]]) -> pd.DataFrame:
        """
        Add a 'Current Referral' column that sums 'Referral only' + 'OTO and Referral'.
        
        Args:
            df: Source dataframe
            header_locations: Dictionary with header positions
            
        Returns:
            DataFrame with added column
        """
        try:
            df_copy = df.copy()
            
            # Get header positions
            referral_only_row, referral_only_col = header_locations[MatrixHeaders.REFERRAL_ONLY]
            oto_and_referral_row, oto_and_referral_col = header_locations[MatrixHeaders.OTO_AND_REFERRAL]
            
            # Position for new column (after OTO and Referral)
            new_col_position = oto_and_referral_col + 1
            
            # Ensure dataframe has enough columns
            while new_col_position >= len(df_copy.columns):
                df_copy[len(df_copy.columns)] = None
            
            # Add header
            df_copy.iloc[referral_only_row, new_col_position] = MatrixHeaders.CURRENT_REFERRAL
            
            # Calculate values for each row
            for row_idx in range(referral_only_row + 1, len(df_copy)):
                referral_only_value = df_copy.iloc[row_idx, referral_only_col]
                oto_and_referral_value = df_copy.iloc[row_idx, oto_and_referral_col]
                
                # Handle NaN values
                referral_only_value = 0 if pd.isna(referral_only_value) else referral_only_value
                oto_and_referral_value = 0 if pd.isna(oto_and_referral_value) else oto_and_referral_value
                
                # Calculate sum
                current_referral = referral_only_value + oto_and_referral_value
                df_copy.iloc[row_idx, new_col_position] = current_referral
            
            return df_copy
            
        except Exception as e:
            raise DataProcessingError(f"Error adding current referral column: {str(e)}")
    
    def add_comparison_columns(self, new_df: pd.DataFrame, old_df: pd.DataFrame,
                             new_headers: Dict[str, Tuple[int, int]], 
                             old_headers: Dict[str, Tuple[int, int]]) -> pd.DataFrame:
        """
        Add comparison columns (Last Referral, Change in Referrals, etc.) to the new matrix.
        
        Args:
            new_df: New matrix dataframe
            old_df: Old matrix dataframe
            new_headers: Header locations in new matrix
            old_headers: Header locations in old matrix
            
        Returns:
            DataFrame with comparison columns added
        """
        try:
            result_df = new_df.copy()
            
            # Add Current Referral column to both matrices if not already present
            result_df = self.add_current_referral_column(result_df, new_headers)
            old_df_with_current = self.add_current_referral_column(old_df, old_headers)
            
            # Get positions
            new_oto_referral_row, new_oto_referral_col = new_headers[MatrixHeaders.OTO_AND_REFERRAL]
            old_oto_referral_row, old_oto_referral_col = old_headers[MatrixHeaders.OTO_AND_REFERRAL]
            old_neither_row, old_neither_col = old_headers[MatrixHeaders.NEITHER]
            
            current_referral_col = new_oto_referral_col + 1
            last_referral_col = current_referral_col + 1
            change_referral_col = last_referral_col + 1
            last_neither_col = change_referral_col + 1
            change_neither_col = last_neither_col + 1
            
            # Ensure enough columns
            while change_neither_col >= len(result_df.columns):
                result_df[len(result_df.columns)] = None
            
            # Add headers
            result_df.iloc[new_oto_referral_row, last_referral_col] = MatrixHeaders.LAST_REFERRAL
            result_df.iloc[new_oto_referral_row, change_referral_col] = MatrixHeaders.CHANGE_IN_REFERRALS
            result_df.iloc[new_oto_referral_row, last_neither_col] = MatrixHeaders.LAST_NEITHER
            result_df.iloc[new_oto_referral_row, change_neither_col] = MatrixHeaders.CHANGE_IN_NEITHER
            
            # Create lookup dictionaries for old matrix values
            old_referral_lookup = self._create_member_value_lookup(
                old_df_with_current, old_oto_referral_row, old_oto_referral_col + 1
            )
            old_neither_lookup = self._create_member_value_lookup(
                old_df, old_neither_row, old_neither_col
            )
            
            # Fill comparison columns
            for row_idx in range(new_oto_referral_row + 1, len(result_df)):
                member_name = result_df.iloc[row_idx, 0]
                if pd.notna(member_name):
                    normalized_name = str(member_name).strip().lower()
                    
                    # Get current values
                    current_referral = result_df.iloc[row_idx, current_referral_col]
                    current_neither = result_df.iloc[row_idx, new_headers[MatrixHeaders.NEITHER][1]]
                    
                    # Convert to numeric, defaulting to 0 for any non-numeric values
                    try:
                        current_referral = 0 if pd.isna(current_referral) else float(current_referral)
                    except (ValueError, TypeError):
                        current_referral = 0
                    
                    try:
                        current_neither = 0 if pd.isna(current_neither) else float(current_neither)
                    except (ValueError, TypeError):
                        current_neither = 0
                    
                    # Get last values and ensure they're numeric
                    last_referral = old_referral_lookup.get(normalized_name, 0)
                    last_neither = old_neither_lookup.get(normalized_name, 0)
                    
                    try:
                        last_referral = float(last_referral) if last_referral is not None else 0
                    except (ValueError, TypeError):
                        last_referral = 0
                    
                    try:
                        last_neither = float(last_neither) if last_neither is not None else 0
                    except (ValueError, TypeError):
                        last_neither = 0
                    
                    # Fill last values
                    result_df.iloc[row_idx, last_referral_col] = last_referral
                    result_df.iloc[row_idx, last_neither_col] = last_neither
                    
                    # Calculate and fill changes
                    referral_change = current_referral - last_referral
                    neither_change = current_neither - last_neither
                    
                    result_df.iloc[row_idx, change_referral_col] = self._format_change_value(referral_change)
                    result_df.iloc[row_idx, change_neither_col] = self._format_change_value(neither_change)
            
            return result_df
            
        except Exception as e:
            raise DataProcessingError(f"Error adding comparison columns: {str(e)}")
    
    def _create_member_value_lookup(self, df: pd.DataFrame, start_row: int, 
                                  value_col: int) -> Dict[str, Any]:
        """
        Create a lookup dictionary mapping member names to their values.
        
        Args:
            df: Source dataframe
            start_row: Row to start reading from (after headers)
            value_col: Column containing the values
            
        Returns:
            Dictionary mapping normalized names to values
        """
        try:
            lookup = {}
            
            for row_idx in range(start_row + 1, len(df)):
                member_name = df.iloc[row_idx, 0]  # Assuming names are in column 0
                if pd.notna(member_name):
                    value = df.iloc[row_idx, value_col]
                    # Convert to numeric, defaulting to 0 for any non-numeric values
                    if pd.isna(value):
                        value = 0
                    else:
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0
                    normalized_name = str(member_name).strip().lower()
                    lookup[normalized_name] = value
            
            return lookup
            
        except Exception as e:
            raise DataProcessingError(f"Error creating member value lookup: {str(e)}")
    
    def _format_change_value(self, change: float) -> str:
        """
        Format a change value with appropriate indicators.
        
        Args:
            change: The change value
            
        Returns:
            Formatted string with change indicators
        """
        try:
            if change > 0:
                return f"+{change} ↗️"
            elif change < 0:
                return f"{change} ↘️"
            else:
                return f"{change} ➡️"
                
        except Exception:
            return "0 ➡️"
    
    def generate_comparison_report(self, new_matrix_path: Path, 
                                 old_matrix_path: Path) -> pd.DataFrame:
        """
        Generate a complete comparison report between two matrices.
        
        Args:
            new_matrix_path: Path to the new matrix file
            old_matrix_path: Path to the old matrix file
            
        Returns:
            DataFrame with complete comparison data
        """
        try:
            # Load both matrices
            new_df, new_headers = self.load_matrix_from_excel(new_matrix_path)
            old_df, old_headers = self.load_matrix_from_excel(old_matrix_path)
            
            # Generate comparison
            comparison_df = self.add_comparison_columns(new_df, old_df, new_headers, old_headers)
            
            return comparison_df
            
        except Exception as e:
            if isinstance(e, DataProcessingError):
                raise
            raise DataProcessingError(f"Error generating comparison report: {str(e)}")
    
    def export_comparison_to_excel(self, comparison_df: pd.DataFrame, 
                                 output_path: Path) -> None:
        """
        Export a comparison dataframe to Excel with proper formatting.
        
        Args:
            comparison_df: DataFrame with comparison data
            output_path: Path where to save the Excel file
        """
        try:
            # Create workbook
            workbook = self.excel_handler.create_styled_workbook()
            worksheet = workbook.active
            worksheet.title = "Combination Matrix Comparison"
            
            # Write data to worksheet
            for row_idx, row_data in enumerate(comparison_df.values, start=1):
                for col_idx, value in enumerate(row_data, start=1):
                    worksheet.cell(row=row_idx, column=col_idx, value=value)
            
            # Apply styling
            data_range = {
                'max_row': len(comparison_df),
                'max_col': len(comparison_df.columns)
            }
            
            self.excel_handler.apply_matrix_styling(worksheet, data_range, highlight_zeros=True)
            self.excel_handler.auto_adjust_column_widths(worksheet)
            
            # Save workbook
            self.excel_handler.save_workbook(workbook, output_path)
            
        except Exception as e:
            raise DataProcessingError(f"Error exporting comparison to Excel: {str(e)}")
    
    def get_comparison_insights(self, comparison_df: pd.DataFrame,
                              headers: Dict[str, Tuple[int, int]]) -> Dict[str, Any]:
        """
        Generate insights from a comparison matrix.
        
        Args:
            comparison_df: DataFrame with comparison data
            headers: Header locations
            
        Returns:
            Dictionary with comparison insights
        """
        try:
            insights = {
                'total_members': 0,
                'improved_members': 0,
                'declined_members': 0,
                'unchanged_members': 0,
                'biggest_improvements': [],
                'biggest_declines': [],
                'summary_stats': {}
            }
            
            # Find change columns
            header_row = headers[MatrixHeaders.OTO_AND_REFERRAL][0]
            
            # Count members and analyze changes
            member_changes = []
            
            for row_idx in range(header_row + 1, len(comparison_df)):
                member_name = comparison_df.iloc[row_idx, 0]
                if pd.notna(member_name):
                    insights['total_members'] += 1
                    
                    # Extract change values (assuming specific column positions)
                    # This would need to be adjusted based on actual column positions
                    change_col = None
                    for col_idx in range(len(comparison_df.columns)):
                        header_val = comparison_df.iloc[header_row, col_idx]
                        if pd.notna(header_val) and MatrixHeaders.CHANGE_IN_REFERRALS in str(header_val):
                            change_col = col_idx
                            break
                    
                    if change_col is not None:
                        change_str = comparison_df.iloc[row_idx, change_col]
                        if pd.notna(change_str):
                            # Parse change value
                            change_val = self._parse_change_value(str(change_str))
                            member_changes.append((str(member_name), change_val))
                            
                            if change_val > 0:
                                insights['improved_members'] += 1
                            elif change_val < 0:
                                insights['declined_members'] += 1
                            else:
                                insights['unchanged_members'] += 1
            
            # Get top improvements and declines
            member_changes.sort(key=lambda x: x[1], reverse=True)
            insights['biggest_improvements'] = member_changes[:5]
            insights['biggest_declines'] = member_changes[-5:]
            
            # Calculate summary statistics
            if member_changes:
                changes = [change for _, change in member_changes]
                insights['summary_stats'] = {
                    'average_change': sum(changes) / len(changes),
                    'total_change': sum(changes),
                    'improvement_rate': insights['improved_members'] / insights['total_members'],
                    'decline_rate': insights['declined_members'] / insights['total_members']
                }
            
            return insights
            
        except Exception as e:
            raise DataProcessingError(f"Error generating comparison insights: {str(e)}")
    
    def _parse_change_value(self, change_str: str) -> float:
        """
        Parse a change value from a formatted string.
        
        Args:
            change_str: Formatted change string (e.g., "+5 ↗️", "-2 ↘️")
            
        Returns:
            Numeric change value
        """
        try:
            # Remove emoji and extra characters, extract numeric value
            import re
            match = re.search(r'([+-]?\d+\.?\d*)', change_str)
            return float(match.group(1)) if match else 0.0
            
        except:
            return 0.0