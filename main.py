import os
from fileconversion import convert_xls_to_xlsx
from data_extraction import data_extraction, final_referral_data_to_excel, final_OTO_data_to_excel, final_combination_data_to_excel

import sys

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

