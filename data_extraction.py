from openpyxl import Workbook, load_workbook
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
    ws.cell(row=1, column=1, value="Giver \ Receiver")
    for col, member in enumerate(members, start=2):
        ws.cell(row=1, column=col, value=member)

    # Write data (Y-axis: Givers)
    for row, giver in enumerate(members, start=2):
        ws.cell(row=row, column=1, value=giver)
        for col, receiver in enumerate(members, start=2):
            ws.cell(row=row, column=col, value=referral_matrix[giver][receiver])

    wb.save(output_file)
    print(f"Referral matrix exported successfully to {output_file}")

def export_OTO_matrix_to_excel(output_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "One to One Matrix"

    members = list(OTO_matrix.keys())

    # Write headers (X-axis: Receivers)
    ws.cell(row=1, column=1, value="Giver \ Receiver")
    for col, member in enumerate(members, start=2):
        ws.cell(row=1, column=col, value=member)

    # Write data (Y-axis: Givers)
    for row, giver in enumerate(members, start=2):
        ws.cell(row=row, column=1, value=giver)
        for col, receiver in enumerate(members, start=2):
            ws.cell(row=row, column=col, value=OTO_matrix[giver][receiver])

    wb.save(output_file)
    print(f"Referral matrix exported successfully to {output_file}")

# Wrapper function to process referrals and export results
def data_extraction(referral_file_path):
    process_referral_excel_data(referral_file_path)
    process_OTO_excel_data(referral_file_path)
    


