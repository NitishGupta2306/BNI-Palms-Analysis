import pandas as pd

# Extract names from an Excel file
def extract_names_from_excel(file_path):

    if file_path:
        df = pd.read_excel(file_path, usecols=[0, 1], dtype=str, header=0)  # Read first and last names
        df.dropna(how="all", inplace=True)  # Drop empty rows
        df["Full Name"] = df.iloc[:, 0].str.strip() + " " + df.iloc[:, 1].str.strip()
        return df["Full Name"].dropna().tolist()  # Return list of full names
    else:
        print("Could not find file path")
        print(file_path)