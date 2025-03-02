import os
from member_names import extract_names_from_excel
from fileconversion import convert_xls_to_xlsx
from export_sql_excel import extract_excel
from data_extraction import process_oto_excel_data, process_referral_excel_data, empty_list
from data_base_manager import create_database, insert_data_into_referraldb, insert_data_into_otodb, print_database_contents, delete_database

create_database()

# Processing all excel file
for files in os.listdir("Excel Files"):
    if files.endswith(".xls"):
        convert_xls_to_xlsx(f"Excel Files/{files}")

for files in os.listdir("Excel Files"):
    if files.endswith(".xlsx"):
        referral_data = process_referral_excel_data(f"Excel Files/{files}", extract_names_from_excel("Member Names/Conti members.xlsx"))
        #oto_data = process_oto_excel_data(f"Excel Files/{files}")

# adding data to db
insert_data_into_referraldb(referral_data)
#insert_data_into_otodb(oto_data)
empty_list()

# printing current data + deleting to avoid multiple entries
# print_database_contents()
extract_excel()

delete_database()
