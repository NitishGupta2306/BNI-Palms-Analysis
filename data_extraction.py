import sqlite3
import os
from openpyxl import load_workbook

referral_list = []

def empty_referral_list():
    global referral_list  
    referral_list.clear()

def print_referral_list():
    print(referral_list)
# Function to process the Excel data and return the filtered list
def process_excel_data(file_path):
    book = load_workbook(file_path)
    sheet = book.active

    # Identify columns in the Excel sheet
    column_slip_type = sheet["D"]
    column_reciever_name = sheet["B"]
    column_insider_ref = sheet["J"]

    curr_ref_type = True  # Default reference type value
    is_name_inlist = False

    # Loop through the rows and filter the data
    for cell_slip_type, cell_reciever_name, cell_insider_ref in zip(column_slip_type, column_reciever_name, column_insider_ref):
        if cell_slip_type.value == "Referral":
            # checking current referral type
            if cell_insider_ref.value == "":
                curr_ref_type = True
            else:
                curr_ref_type = False
            
            # checking if the reciever already in list.
            for list in referral_list:
                if cell_reciever_name.value in list:
                    is_name_inlist = True
                    if curr_ref_type:
                        # incrementing number of inside referrals.
                        list[2] += 1
                    else:
                        # incrementing number of outside referrals.
                        list[3] += 1
                    break

            if curr_ref_type == True and is_name_inlist == False:
                referral_list.append([cell_reciever_name.value, cell_slip_type.value, 1, 0])
            elif curr_ref_type == False and is_name_inlist == False:
                referral_list.append([cell_reciever_name.value, cell_slip_type.value, 0, 1])

            is_name_inlist = False

    return referral_list




