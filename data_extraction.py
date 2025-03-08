from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
import pandas as pd

# Extract names from an Excel file
def extract_names_from_excel(file_path):
    df = pd.read_excel(file_path, usecols=[3, 4], dtype=str, header=0)  # Read first and last names
    df.dropna(how="all", inplace=True)  # Drop empty rows
    df["Full Name"] = df.iloc[:, 0].str.strip() + " " + df.iloc[:, 1].str.strip()
    return df["Full Name"].dropna().tolist()  # Return list of full names

# Load member names once
member_names = extract_names_from_excel("Member Names/Conti members.xlsx")

# Persistent referral matrix (dictionary of dictionaries)
referral_matrix = {giver: {receiver: 0 for receiver in member_names} for giver in member_names}
OTO_matrix = {giver: {receiver: 0 for receiver in member_names} for giver in member_names}

# Function to process Excel data and update the referral matrix
def process_referral_excel_data(file_path):
    book = load_workbook(file_path)
    sheet = book.active

    column_slip_type = sheet["C"]
    column_giver_name = sheet["A"]
    column_reciever_name = sheet["B"]

    for cell_slip_type, cell_giver_name, cell_reciever_name in zip(column_slip_type, column_giver_name, column_reciever_name):
        if (cell_reciever_name.value in member_names and
            cell_giver_name.value in member_names and
            cell_slip_type.value == "Referral"):

            giver = cell_giver_name.value
            receiver = cell_reciever_name.value
            referral_matrix[giver][receiver] += 1  # Increment count instead of resetting

    return referral_matrix  # Return updated matrix

# Function to process Excel data and update the OTO matrix
def process_OTO_excel_data(file_path):
    book = load_workbook(file_path)
    sheet = book.active

    column_slip_type = sheet["C"]
    column_giver_name = sheet["A"]
    column_reciever_name = sheet["B"]

    for cell_slip_type, cell_giver_name, cell_reciever_name in zip(column_slip_type, column_giver_name, column_reciever_name):
        if (cell_reciever_name.value in member_names and
            cell_giver_name.value in member_names and
            cell_slip_type.value == "One to One"):

            giver = cell_giver_name.value
            receiver = cell_reciever_name.value
            OTO_matrix[giver][receiver] += 1  # Increment count instead of resetting

    return OTO_matrix  # Return updated matrix

# Function to export the matrix to an Excel file
def export_referral_matrix_to_excel(output_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "Referral Matrix"

    members = list(referral_matrix.keys())

    # Write headers (X-axis: Receivers)
    ws.cell(row=1, column=1, value="Giver \ Receiver").font = Font(bold=True)
    for col, member in enumerate(members, start=2):
        ws.cell(row=1, column=col, value=member).font = Font(bold=True)

    # Define styles
    zero_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    border_style = Border(left=Side(style="thin"), right=Side(style="thin"),
                          top=Side(style="thin"), bottom=Side(style="thin"))
    center_align = Alignment(horizontal="center", vertical="center")

    # Write and processes data (Y-axis: Givers)
    for row, giver in enumerate(members, start=2):
        ws.cell(row=row, column=1, value=giver).font = Font(bold=True)

        row_values = []
        unique_referrals = 0
        for col, receiver in enumerate(members, start=2):
            value_row = referral_matrix[giver][receiver]
            cell = ws.cell(row=row, column=col, value=value_row)
            cell.alignment = center_align
            cell.border = border_style  # Apply borders
            if value_row == 0:
                cell.fill = zero_fill  # Highlight zero values
            elif value_row > 0:
                unique_referrals += 1
            
            row_values.append(value_row)
                    
        # Adding columns for "Total Referrals Given" and "Unique Referrals Given."
        ws.cell(row=1, column=len(members) + 2, value="Total Referrals Given: ").font = Font(bold=True)
        ws.cell(row=1, column=len(members) + 3, value= f"Unique Referals Given: (Total Members = {len(members)})").font = Font(bold=True)

        # Adding calculated values to the new cells.
        avg_cell_given = ws.cell(row=row, column=len(members) + 2, value = sum(row_values))
        unique_cell_given = ws.cell(row = row, column = len(members) + 3, value = unique_referrals)

        # Styling all new cells:
        avg_cell_given.font = Font(bold=True)
        avg_cell_given.alignment = center_align
        avg_cell_given.border = border_style

        unique_cell_given.font = Font(bold=True)
        unique_cell_given.alignment = center_align
        unique_cell_given.border = border_style

    # calculating recieved data
    for col, reciever in enumerate(members, start=2):
        col_values = []
        unique_referrals = 0
        for row, giver in enumerate(members, start=2):
            value_col = referral_matrix[giver][reciever]
            if value_col > 0:
                unique_referrals += 1
            col_values.append(value_col)
        
        # Adding rows for "Total Referrals Recieved" and "Unique Referrals Recieved."
        ws.cell(row=len(members) + 2, column=1, value="Total Referrals Recieved: ").font = Font(bold=True)
        ws.cell(row=len(members) + 3, column=1, value= f"Unique Referals Recieved: (Total Members = {len(members)})").font = Font(bold=True)
        
        # Adding calculated values to the new cells:
        avg_cell_recieved = ws.cell(row=len(members) + 2, column=col, value = sum(col_values))
        unique_cell_recieved = ws.cell(row = len(members) + 3, column =col, value = unique_referrals)

        # Styling all new cells:
        avg_cell_recieved.font = Font(bold=True)
        avg_cell_recieved.alignment = center_align
        avg_cell_recieved.border = border_style

        unique_cell_recieved.font = Font(bold=True)
        unique_cell_recieved.alignment = center_align
        unique_cell_recieved.border = border_style



    # Auto-adjust column widths
    for cell in range(1, len(members) + 5):  # +3 to include "Row Average"
        ws.column_dimensions[ws.cell(row=1, column=cell).column_letter].auto_size = True
       # ws.row_dimensions[ws.cell(row=cell, column=1).row_letter].auto_size = True

    wb.save(output_file)
    print(f"Referral matrix exported successfully to {output_file}")

def export_OTO_matrix_to_excel(output_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "One to One Matrix"

    members = list(OTO_matrix.keys())

    # Write headers (X-axis: Receivers)
    ws.cell(row=1, column=1, value="Giver \ Receiver").font = Font(bold=True)
    for col, member in enumerate(members, start=2):
        ws.cell(row=1, column=col, value=member).font = Font(bold=True)

    # Define styles
    zero_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    border_style = Border(left=Side(style="thin"), right=Side(style="thin"),
                          top=Side(style="thin"), bottom=Side(style="thin"))
    center_align = Alignment(horizontal="center", vertical="center")

    # Write data (Y-axis: Givers)
    for row, giver in enumerate(members, start=2):
        ws.cell(row=row, column=1, value=giver).font = Font(bold=True)

        row_values = []
        unique_values = 0
        for col, receiver in enumerate(members, start=2):
            value = OTO_matrix[giver][receiver]
            cell = ws.cell(row=row, column=col, value=OTO_matrix[giver][receiver])
            cell.alignment = center_align
            cell.border = border_style  # Apply borders
            if value == 0:
                cell.fill = zero_fill  # Highlight zero values
            elif value > 0:
                unique_values += 1
            
            row_values.append(value)
        
        # Add a column for "Total OTO"
        ws.cell(row = 1, column = len(members) + 2, value = "Total OTO: ").font = Font(bold=True)

        # Add a column for "Unique OTO"
        ws.cell(row=1, column=len(members) + 3, value= f"Unique OTO: (Total Members = {len(members)})").font = Font(bold=True)

        # Compute row average and write it in the last column
        avg_cell = ws.cell(row=row, column=len(members) + 2, value = sum(row_values))
        unique_cell = ws.cell(row = row, column = len(members) + 3, value = unique_values)

        avg_cell.font = Font(bold=True)
        avg_cell.alignment = center_align
        avg_cell.border = border_style

        unique_cell.font = Font(bold=True)
        unique_cell.alignment = center_align
        unique_cell.border = border_style

    # Auto-adjust column widths
    for col in range(1, len(members) + 2):
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].auto_size = True

    wb.save(output_file)
    print(f"OTO matrix exported successfully to {output_file}")


# Wrapper function to process referrals and export results
def data_extraction(referral_file_path):
    process_referral_excel_data(referral_file_path)
    process_OTO_excel_data(referral_file_path)
    


