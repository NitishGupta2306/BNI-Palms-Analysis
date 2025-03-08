import xml.etree.ElementTree as ET
import pandas as pd
import os

def convert_xls_to_xlsx(file_path):
    """
    Converts an XML-based .xls (Excel 2003 XML format) to a proper .xlsx file.
    Saves the converted file in the same folder as the original.
    Deletes the original .xls file upon successful conversion.
    """
    if not file_path.lower().endswith(".xls"):
        raise ValueError("The provided file must have a .xls extension")

    # Parse XML
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError:
        raise ValueError("Invalid XML format. Ensure this is an Excel 2003 XML file.")

    # Define XML namespaces
    namespaces = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}

    # Find all rows in the worksheet
    rows = root.findall(".//ss:Table/ss:Row", namespaces)

    # Extract data from each row
    data = []
    for row in rows:
        row_data = []
        for cell in row.findall(".//ss:Data", namespaces):
            row_data.append(cell.text if cell.text else "")  # Get cell value
        data.append(row_data)

    # Convert to Pandas DataFrame
    df = pd.DataFrame(data)

    # Get the folder where the original file is stored
    folder_path = os.path.dirname(file_path)

    # Generate output filename (same folder as original)
    output_file = os.path.join(folder_path, os.path.splitext(os.path.basename(file_path))[0] + ".xlsx")

    # Save as .xlsx
    df.to_excel(output_file, index=False, header=False, engine="openpyxl")

    # Delete original .xls file
    os.remove(file_path)

    print(f"Conversion successful! Saved as '{output_file}' and deleted '{file_path}'.")
