import os
from fileconversion import convert_xls_to_xlsx
from data_extraction import data_extraction, export_referral_matrix_to_excel, export_OTO_matrix_to_excel

# Processing all excel file
for files in os.listdir("Excel Files"):
    if files.endswith(".xls"):
        convert_xls_to_xlsx(f"Excel Files/{files}")

for files in os.listdir("Excel Files"):
    if files.endswith(".xlsx"):
        print(f"Processing {files}...")  # Log the file being processed
        data_extraction(f"Excel Files/{files}")

export_referral_matrix_to_excel("referral_matrix.xlsx")
export_OTO_matrix_to_excel("OTO_matrix.xlsx")