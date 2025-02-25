from data_extraction import process_excel_data
from data_base_manager import create_database, insert_data_into_db, print_database_contents, delete_database

create_database()

# Processing excel file and inserting into database
referral_data = process_excel_data("Excel Files/TestFile.xlsx")
insert_data_into_db(referral_data)

# printing current data + deleting to avoid multiple entries
print_database_contents()
delete_database()
