import pandas as pd

def extract_names_from_excel(file_path):
    # Read the Excel file using column indexes (3 = Column D, 4 = Column E)
    df = pd.read_excel(file_path, usecols=[3, 4], dtype=str, header=0)  # Adjust header if needed
    
    # Drop any rows where both first and last name are empty
    df.dropna(how="all", inplace=True)

    # Concatenate first and last names with a space in between
    df["Full Name"] = df.iloc[:, 0].str.strip() + " " + df.iloc[:, 1].str.strip()
    
    # Remove empty values (in case of rows with only spaces)
    names = df["Full Name"].dropna().tolist()

    # Return as dictionary
    return names

# Example usage
file_path = "Member Names/Conti members.xlsx" 
names = extract_names_from_excel(file_path)
print(names)
