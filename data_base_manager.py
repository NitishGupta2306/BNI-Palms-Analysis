import sqlite3
import os

# Function to create the SQLite database and table
def create_database():
    conn = sqlite3.connect('referrals.db')
    cursor = conn.cursor()

    # Create the table (if it doesn't exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            receiver_name TEXT,
            slip_type TEXT,
            insider_ref INTEGER,
            outside_ref INTEGER
        )
    ''')

    # Commit and close
    conn.commit()
    conn.close()

# Function to insert data into the SQLite database
def insert_data_into_db(data):
    conn = sqlite3.connect('referrals.db')
    cursor = conn.cursor()

    # Insert data into the referrals table
    cursor.executemany('''
        INSERT INTO referrals (receiver_name, slip_type, insider_ref, outside_ref)
        VALUES (?, ?, ?,?)
    ''', data)

    # Commit and close
    conn.commit()
    conn.close()

def print_database_contents():
    conn = sqlite3.connect('referrals.db')
    cursor = conn.cursor()

    # Query all rows from the referrals table sorted by receiver_name
    cursor.execute("SELECT * FROM referrals ORDER BY receiver_name ASC")
    rows = cursor.fetchall()

    # Print headers
    print(f"{'Receiver Name':<30}   {'Slip Type':<10}   {'Insider Ref':<12}     {'Outside Ref':<12}")
    print("-" * 60)

    # Print each row in a readable format
    for row in rows:
        receiver_name, slip_type, insider_ref, outside_ref = row  # Fixed unpacking issue
        print(f" {receiver_name:<26} {slip_type:<10} {insider_ref:<12} {outside_ref:<12}")

    # Close the connection
    conn.close()

def delete_database():
    try:
        os.remove('referrals.db')  # Delete the database file
    except FileNotFoundError:
        print("Database file not found.")
    except Exception as e:
        print(f"An error occurred while deleting the database: {e}")