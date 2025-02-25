import os

from data_extraction import process_excel_data
from data_base_manager import create_database, insert_data_into_db, print_database_contents, delete_database

create_database()

# Processing all excel file
for files in os.listdir("Excel Files"):
    if files.endswith(".xlsx"):
        referral_data = process_excel_data(f"Excel Files/{files}")

insert_data_into_db(referral_data)

# printing current data + deleting to avoid multiple entries
print_database_contents()
delete_database()
