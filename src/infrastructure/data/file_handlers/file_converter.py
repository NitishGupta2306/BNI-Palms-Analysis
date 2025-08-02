"""File conversion utilities."""

import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from typing import Optional

from src.domain.exceptions.domain_exceptions import FileProcessingError


class FileConverter:
    """Handles file format conversions."""
    
    def convert_xls_to_xlsx(self, file_path: Path, delete_original: bool = True) -> Path:
        """
        Convert an XML-based .xls (Excel 2003 XML format) to a proper .xlsx file.
        
        Args:
            file_path: Path to the .xls file
            delete_original: Whether to delete the original file after conversion
            
        Returns:
            Path to the converted .xlsx file
        """
        try:
            if not file_path.exists():
                raise FileProcessingError(f"File not found: {file_path}")
            
            if not file_path.name.lower().endswith(".xls"):
                raise FileProcessingError("The provided file must have a .xls extension")
            
            # Parse XML
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
            except ET.ParseError:
                raise FileProcessingError("Invalid XML format. Ensure this is an Excel 2003 XML file.")
            
            # Define XML namespaces
            namespaces = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}
            
            # Find all rows in the worksheet
            rows = root.findall(".//ss:Table/ss:Row", namespaces)
            
            # Extract data from each row
            data = []
            for row in rows:
                row_data = []
                for cell in row.findall(".//ss:Data", namespaces):
                    row_data.append(cell.text if cell.text else "")
                data.append(row_data)
            
            # Convert to Pandas DataFrame
            df = pd.DataFrame(data)
            
            # Generate output filename (same folder as original)
            output_file = file_path.with_suffix('.xlsx')
            
            # Save as .xlsx
            df.to_excel(output_file, index=False, header=False, engine="openpyxl")
            
            # Delete original .xls file if requested
            if delete_original:
                file_path.unlink()
            
            return output_file
            
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error converting XLS to XLSX: {str(e)}")
    
    def ensure_xlsx_format(self, file_path: Path, delete_original: bool = False) -> Path:
        """
        Ensure a file is in .xlsx format, converting if necessary.
        
        Args:
            file_path: Path to the file
            delete_original: Whether to delete the original file after conversion
            
        Returns:
            Path to the .xlsx file (original or converted)
        """
        try:
            if file_path.suffix.lower() == '.xlsx':
                return file_path
            elif file_path.suffix.lower() == '.xls':
                # Try to convert using pandas first (simpler approach)
                try:
                    output_file = file_path.with_suffix('.xlsx')
                    
                    # Read the .xls file with appropriate engine
                    try:
                        df = pd.read_excel(file_path, engine='xlrd')
                    except:
                        # If xlrd fails, try openpyxl
                        df = pd.read_excel(file_path, engine='openpyxl')
                    
                    # Save as .xlsx
                    df.to_excel(output_file, index=False, engine='openpyxl')
                    
                    # Delete original if requested
                    if delete_original:
                        file_path.unlink()
                    
                    return output_file
                    
                except Exception:
                    # Fall back to XML-based conversion
                    return self.convert_xls_to_xlsx(file_path, delete_original)
            else:
                raise FileProcessingError(f"Unsupported file format: {file_path.suffix}")
                
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error ensuring XLSX format: {str(e)}")
    
    def batch_convert_directory(self, directory_path: Path, 
                               delete_originals: bool = True) -> list[Path]:
        """
        Convert all .xls files in a directory to .xlsx format.
        
        Args:
            directory_path: Path to the directory containing files
            delete_originals: Whether to delete original files after conversion
            
        Returns:
            List of paths to converted files
        """
        try:
            if not directory_path.exists() or not directory_path.is_dir():
                raise FileProcessingError(f"Directory not found: {directory_path}")
            
            converted_files = []
            
            # Find all .xls files in the directory
            xls_files = list(directory_path.glob("*.xls"))
            
            for xls_file in xls_files:
                try:
                    converted_file = self.convert_xls_to_xlsx(xls_file, delete_originals)
                    converted_files.append(converted_file)
                except FileProcessingError as e:
                    # Log the error but continue with other files
                    print(f"Warning: Could not convert {xls_file}: {e}")
                    continue
            
            return converted_files
            
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error batch converting directory: {str(e)}")
    
    def get_file_format_info(self, file_path: Path) -> dict:
        """
        Get information about a file's format.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file format information
        """
        try:
            if not file_path.exists():
                raise FileProcessingError(f"File not found: {file_path}")
            
            extension = file_path.suffix.lower()
            file_size = file_path.stat().st_size
            
            info = {
                'file_name': file_path.name,
                'extension': extension,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'is_excel': extension in ['.xls', '.xlsx'],
                'needs_conversion': extension == '.xls'
            }
            
            return info
            
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error getting file format info: {str(e)}")