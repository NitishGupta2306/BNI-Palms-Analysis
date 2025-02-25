import os
from export_sql_excel import extract_excel
from data_extraction import process_excel_data, empty_referral_list
from data_base_manager import create_database, insert_data_into_db, print_database_contents, delete_database

DB_NAME = "referrals.db"
TABLE_NAME = "referrals"

create_database()

# Processing all excel file
for files in os.listdir("Excel Files"):
    if files.endswith(".xlsx"):
        referral_data = process_excel_data(f"Excel Files/{files}")

# adding data to db
insert_data_into_db(referral_data)
empty_referral_list()

# printing current data + deleting to avoid multiple entries
print_database_contents()
extract_excel(DB_NAME, TABLE_NAME)

delete_database()
