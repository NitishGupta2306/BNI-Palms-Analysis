import os
import pandas as pd
from fileconversion import convert_xls_to_xlsx
from data_extraction import data_extraction, final_referral_data_to_excel, final_OTO_data_to_excel, final_combination_data_to_excel

# Processing all excel file
for files in os.listdir("Excel Files"):
    if files.endswith(".xls"):
        convert_xls_to_xlsx(f"Excel Files/{files}")

for files in os.listdir("Excel Files"):
    if files.endswith(".xlsx"):
        data_extraction(f"Excel Files/{files}")


final_referral_data_to_excel("referral_matrix.xlsx")
final_OTO_data_to_excel("OTO_matrix.xlsx")
final_combination_data_to_excel("combination_matrix.xlsx")


'''
Technically works, but doesnt keep the formatting of the previous files.


file_names = {
    "referral_matrix": "referral_matrix.xlsx",
    "oto_matrix": "OTO_matrix.xlsx",
    "combination_matrix": "combination_matrix.xlsx"
}

# Create a new Excel file with multiple sheets
output_file = "Palms-Analysis.xlsx"

with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    for sheet_name, file_name in file_names.items():
        df = pd.read_excel(file_name)  # Read each Excel file
        df.to_excel(writer, sheet_name=sheet_name, index=False)  # Write to the new file

print(f"Successfully created '{output_file}' with sheets: {', '.join(file_names.keys())}")

'''

